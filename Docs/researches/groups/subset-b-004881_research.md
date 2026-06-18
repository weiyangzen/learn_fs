# Research: subset-b-004881

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.c

## Purpose
Shared mac80211-facing core for the Realtek `rtlwifi` family. It exports the global `rtl_ops` operation table and implements device start/stop, TX dispatch, interface lifetime, channel/bandwidth configuration, RX filter programming, station tracking, QoS, beacon updates, BSS association state, TSF helpers, AMPDU callbacks, scan transitions, hardware key programming, WoWLAN suspend/resume, RF-kill polling, power-sequence command parsing, command-packet TX, LED defaults, Bluetooth coexistence fallback, and DIG initialization.

## Important APIs, Types, And Functions
The central object is `const struct ieee80211_ops rtl_ops`. Important callbacks include `rtl_op_start()`, `rtl_op_stop()`, `rtl_op_tx()`, `rtl_op_add_interface()`, `rtl_op_remove_interface()`, `rtl_op_config()`, `rtl_op_configure_filter()`, `rtl_op_bss_info_changed()`, `rtl_op_set_key()`, `rtl_op_ampdu_action()`, `rtl_op_sw_scan_start()`, and `rtl_op_sw_scan_complete()`. Exported helpers include `rtl_fw_cb()`, `rtl_wowlan_fw_cb()`, `rtl_addr_delay()`, `rtl_rfreg_delay()`, `rtl_hal_pwrseqcmdparsing()`, `rtl_cmd_send_packet()`, `rtl_init_sw_leds()`, `rtl_btc_status_false()`, and `rtl_dm_diginit()`.

## Control Flow
mac80211 starts the adapter through `rtl_op_start()`, which serializes on `conf_mutex`, calls the bus `adapter_start`, then starts watchdog work. TX checks HAL/RF/interface state, optionally inserts into the PCI early-mode wait queue, otherwise calls the bus `adapter_tx`. Interface add accepts one active vif, sets P2P/AP/IBSS/mesh/station mode state, programs network type, MAC address, basic rates, beacon registers, and retry limits. `rtl_op_config()` reacts to idle, PS, and channel changes by entering IPS, waking the NIC, scheduling SW LPS work, calculating 20/40/80 MHz primary/secondary channel state, then calling chip ops for channel access and bandwidth. BSS changes reset security on association, update BSSID/basic rates/HT parameters, notify firmware join state, and leave LPS plus disable P2P PS on disassociation.

## State And Persistence
Persistent runtime state is mainly in `rtl_priv`, `rtl_mac`, `rtl_hal`, `rtl_ps_ctl`, and `rtl_sec`: current vif, opmode, BSSID, link state, P2P role, beacon enable, bandwidth flags, retry limits, association counters, efuse/firmware buffers, encryption algorithms, key buffers, and DIG thresholds. Most hardware state is volatile and replayed through chip-specific `cfg->ops` after start, channel changes, key changes, and association.

## Dependencies And Integration Points
Depends on mac80211/cfg80211, `wifi.h` core structures, `base.h` helpers, CAM security helpers, `ps.c`, `pwrseqcmd.h`, bus `rtl_intf_ops`, chip-specific `rtl_hal_ops`, firmware loading, Bluetooth coexistence callbacks, and PCI command TX for `rtl_cmd_send_packet()`.

## Risks
The single-vif assumption is enforced by rejecting a second vif. Association, key, LPS/IPS, scan, and channel changes are tightly ordered around `conf_mutex`; races can cause stale BSSID, power-save state, or CAM entries. `rtl_op_set_key()` has many special cases for WEP, group keys, IBSS/mesh software crypto, MFP management frames, and missing pairwise stations. WoWLAN mask translation shifts OS Ethernet patterns into hardware 802.11/LLC offsets and is easy to break. `rtl_hal_pwrseqcmdparsing()` loops until `PWR_CMD_END`, so malformed command arrays can hang or timeout.

## Test Signals
Useful signals are successful probe/register/start, one station/AP/IBSS/mesh/P2P vif, association/disassociation, channel changes across 20/40/80 MHz, SW/FW LPS transitions, idle IPS, scan start/complete under traffic, key install/remove for WEP/TKIP/CCMP/group/pairwise, AMPDU start/stop, beacon enable/update, WoWLAN pattern wake, RF-kill state changes, and clean logs from chip `cfg->ops` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.h

## Purpose
Public declarations for the shared `rtlwifi` core. It exposes the mac80211 operation table, firmware callbacks, RF register delay helper, command-packet TX, LED initialization, DIG initialization, beacon work callback, and common dynamic mechanism thresholds used by chip-specific drivers.

## Important APIs, Types, And Functions
`RTL_SUPPORTED_FILTERS` declares accepted mac80211 filter bits. DIG constants define RSSI/false-alarm thresholds, IGI bounds, AP-specific IGI limits, and backoff bounds. `enum cck_packet_detection_threshold`, `enum dm_dig_ext_port_alg_e`, and `enum dm_dig_connect_e` encode dynamic initial gain and CCK packet-detection state. Declared entry points include `rtl_ops`, `rtl_fw_cb()`, `rtl_wowlan_fw_cb()`, `rtl_rfreg_delay()`, `rtl_cmd_send_packet()`, `rtl_btc_status_false()`, and `rtl_dm_diginit()`.

## Control Flow
This header is included by shared and chip-specific sources that bind into the same driver family. `rtl_ops` is consumed during `ieee80211_alloc_hw()`/registration, firmware callbacks are passed to the kernel firmware loader, and delay/DIG helpers are called by PHY/RF configuration paths.

## State And Persistence
No storage is defined here. It standardizes constants that initialize or constrain state in `struct dig_t`, `struct rtl_mac`, and mac80211 filter handling.

## Dependencies And Integration Points
Requires mac80211 types, Realtek `radio_path`, firmware loading types, and `work_struct`. It integrates the common core with chip-specific PHY, RF, LED, firmware, and beacon code.

## Risks
Changing filter masks changes the behavior mac80211 is allowed to request. DIG threshold changes can alter receive sensitivity and false-alarm behavior across all rtlwifi chips using this core. Enum values are persisted in driver state machines, so reordering would be risky.

## Test Signals
Build coverage across all rtlwifi PCI/USB/SDIO variants, successful mac80211 registration, expected RX filter behavior, and stable DIG behavior under low/high RSSI and false-alarm scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.c

## Purpose
Optional debug implementation for `CONFIG_RTLWIFI_DEBUG`. It provides filtered trace printing, hex dumps, a top-level `rtlwifi` debugfs directory, per-device debugfs directories named by MAC address, read-only MAC/BB/RF/CAM/BT coexistence dumps, and write-only hooks for direct register, H2C, and RF-register writes.

## Important APIs, Types, And Functions
`_rtl_dbg_print()` and `_rtl_dbg_print_data()` implement `rtl_dbg`, `RTPRINT`, and `RT_PRINT_DATA`. `struct rtl_debugfs_priv` binds each debugfs file to `rtlpriv`, a read callback, write callback, and data selector. Dump callbacks include `rtl_debug_get_mac_page()`, `rtl_debug_get_bb_page()`, `rtl_debug_get_reg_rf()`, `rtl_debug_get_cam_register()`, and `rtl_debug_get_btcoex()`. Public debugfs lifecycle APIs are `rtl_debug_add_one()`, `rtl_debug_remove_one()`, `rtl_debugfs_add_topdir()`, and `rtl_debugfs_remove_topdir()`.

## Control Flow
When debug is enabled, probe creates a per-device directory and populates register pages. Read paths call `single_open()` then the selected callback reads MMIO, BB, RF, CAM, or BT-coex information. Write paths copy a short user buffer, parse hex fields with `sscanf`, then call `rtl_write_*`, `fill_h2c_cmd`, or `rtl_set_rfreg()`.

## State And Persistence
The only global state is `debugfs_topdir`. Per-file state is static `rtl_debugfs_priv` objects whose `rtlpriv` pointer is filled during `rtl_debug_add_one()`. The files expose live hardware state; writes mutate device registers immediately and are not persisted across reset.

## Dependencies And Integration Points
Depends on debugfs, seq_file, register accessors, CAM constants, chip `maps`, `fill_h2c_cmd`, RF helpers, and BT coexistence ops. Probe/disconnect in `pci.c` call add/remove.

## Risks
Write debugfs files can corrupt hardware state or firmware communication with minimal validation. Static debugfs private objects have their `rtlpriv` pointer overwritten per device, so multi-device behavior can be fragile. CAM and RF dumps poll live hardware and may race with normal driver operations.

## Test Signals
With `CONFIG_RTLWIFI_DEBUG`, verify `/sys/kernel/debug/rtlwifi/<mac>/` appears and disappears, register pages read without faults, BT coexistence dump is guarded by status, write_reg/write_h2c/write_rfreg reject malformed input, and disconnect removes all debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.h

## Purpose
Defines rtlwifi debug levels, component masks, legacy print flag groups, debug-print macros, and debugfs lifecycle declarations. It compiles debug calls either to real functions or empty inline stubs depending on `CONFIG_RTLWIFI_DEBUG`.

## Important APIs, Types, And Functions
Debug levels are `DBG_WARNING`, `DBG_DMESG`, `DBG_LOUD`, and `DBG_TRACE`. Component masks include `COMP_FW`, `COMP_INIT`, `COMP_RECV`, `COMP_SEND`, `COMP_POWER`, `COMP_EFUSE`, `COMP_REGD`, `COMP_BT_COEXIST`, and `COMP_TX_REPORT`. `enum dbgp_flag_e` defines older `RTPRINT` domains. Public macros are `rtl_dbg()`, `RTPRINT()`, and `RT_PRINT_DATA()`.

## Control Flow
When debug is enabled, macros call `_rtl_dbg_print()` or `_rtl_dbg_print_data()` with component and level filtering. When disabled, the same call sites compile to no-op inline functions, preserving type checking for printf arguments.

## State And Persistence
No state is owned here. Filtering uses `rtlpriv->cfg->mod_params->debug_mask` and `debug_level` in `debug.c`.

## Dependencies And Integration Points
Used throughout rtlwifi shared and chip-specific code. The component mask taxonomy is the contract between call sites, module parameters, and debug output.

## Risks
Mask overlap is intentional in one case (`COMP_EASY_CONCURRENT` reuses `COMP_USB`), so consumers must not assume every bit is unique. Build coverage is needed for both debug-enabled and debug-disabled paths because function-like macros change definitions.

## Test Signals
Compile with and without `CONFIG_RTLWIFI_DEBUG`, verify debug module parameters filter expected components/levels, and confirm disabled builds do not emit debugfs symbols or runtime logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.c

## Purpose
Implements Realtek efuse access and firmware-memory write helpers. It reads the physical efuse byte stream, reconstructs logical maps, maintains init/modify shadow maps, checks and commits shadow updates, powers efuse circuitry on/off, parses EEPROM identity fields into `rtl_efuse`, and writes firmware pages/blocks to MCU download memory.

## Important APIs, Types, And Functions
Public efuse APIs include `efuse_initialize()`, `efuse_read_1byte()`, `efuse_write_1byte()`, `read_efuse_byte()`, `read_efuse()`, `efuse_shadow_read()`, `efuse_shadow_write()`, `efuse_shadow_update_chk()`, `efuse_shadow_update()`, `rtl_efuse_shadow_map_update()`, `efuse_power_switch()`, `efuse_one_byte_read()`, `rtl_get_hwinfo()`, and `rtl_efuse_ops_init()`. Internal packet programming uses `efuse_pg_packet_read()`, `efuse_pg_packet_write()`, `enable_efuse_data_write()`, and `efuse_get_current_size()`.

## Control Flow
Probe initializes `rtlpriv->efuse.efuse_ops`, chip code reads EEPROM info, and `rtl_get_hwinfo()` loads the logical map. Physical reads walk efuse packet headers, including extended headers, reconstructing four two-byte words per section. Shadow writes update only `EFUSE_MODIFY_MAP`; `efuse_shadow_update()` capacity-checks changed words, powers the efuse in write mode, writes section packets, powers down, then refreshes the init and modify maps. Firmware writes select a page in `REG_MCUFWDL` and write by byte for PCI or chunked transfers for USB.

## State And Persistence
Physical efuse is one-time-programmable persistent device state. Runtime state includes `efuse_map[EFUSE_INIT_MAP]`, `efuse_map[EFUSE_MODIFY_MAP]`, used byte count, used percentage, autoload flag, vendor/device/subsystem IDs, MAC address, channel plan, EEPROM version, and OEM ID. Hardware registers hold transient efuse access and power state.

## Dependencies And Integration Points
Depends on `rtl_priv` register maps, chip-specific map sizes/protect lengths, PCI private device for `rtl_get_hwinfo()`, USB/PCI interface distinction for firmware writes, and hardware vars `HW_VAR_EFUSE_BYTES`/`HW_VAR_EFUSE_USAGE`.

## Risks
Efuse programming is irreversible and capacity-limited. Retry logic and `repeat_times` behavior are subtle, and `efuse_pg_packet_write()` returns true even after some result failures. Several paths use fixed `EFUSE_MAX_SIZE` and section count assumptions. Shadow writes lack offset bounds checks. Power sequencing differs by chip family and write/read mode.

## Test Signals
Validate efuse map read on valid and autoload-failed devices, correct MAC/VID/DID/channel-plan extraction, used-byte accounting, shadow update capacity rejection near OOB protection, successful readback after programmed words, no writes when only shadow read occurs, and firmware block/page writes on PCI and USB paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.h

## Purpose
Header for efuse layout, packet programming state, logical item identifiers, voltage constants, SDIO-oriented efuse private data, and public efuse/firmware helper declarations.

## Important APIs, Types, And Functions
Defines `EFUSE_IC_ID_OFFSET`, `EFUSE_MAX_WORD_UNIT`, `EFUSE_INIT_MAP`, `EFUSE_MODIFY_MAP`, `PG_STATE_*`, and `EFUSE_REPEAT_THRESHOLD_`. `struct efuse_map` describes logical byte spans; `struct pgpkt_struct` describes one programmable section packet; `enum efuse_data_item` names logical data items; `struct efuse_priv` stores ID, LDO, clock, CIS, MAC, channel plan, and TX power fields. Declarations cover physical byte access, shadow map access/update, power switching, hardware info extraction, firmware writes, and ops initialization.

## Control Flow
Consumers include shared efuse code, chip-specific EEPROM readers, and firmware download logic. Headers standardize how logical efuse sections are represented before `efuse.c` reads, updates, or programs them.

## State And Persistence
The header describes persistent efuse fields and transient shadow maps but owns no storage. Its state-machine constants are used during packet read/write traversal.

## Dependencies And Integration Points
Requires mac80211 `ieee80211_hw` and rtlwifi `rtl_priv`. It bridges common efuse code with chip-specific map offsets and interface-specific firmware loading.

## Risks
The misspelled `EFUSE_ERROE_HANDLE` is part of the local API surface. Fixed section/word assumptions must match the physical efuse encoding used by supported chips. Firmware write declarations are shared by PCI and USB behavior.

## Test Signals
Build all users, verify logical map reads by 1/2/4 byte type, shadow update flows, efuse power switching, and firmware page writes using chip-specific map constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/efuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.c

## Purpose
PCI bus implementation for rtlwifi. It provides module metadata, MMIO access setup, PCI probe/disconnect, DMA ring allocation/free/reset, TX/RX descriptor handling, interrupt demultiplexing, beacon tasklets, ASPM and CLKREQ power policy, MSI/legacy IRQ selection, suspend/resume hooks, and the exported `rtl_pci_ops` interface used by the shared core.

## Important APIs, Types, And Functions
Public entry points are `rtl_pci_probe()`, `rtl_pci_disconnect()`, `rtl_pci_suspend()`, `rtl_pci_resume()`, `rtl_pci_reset_trx_ring()`, and `const struct rtl_intf_ops rtl_pci_ops`. Key internals include `_rtl_mac_to_hwqueue()`, `_rtl_pci_update_default_setting()`, `rtl_pci_enable_aspm()`, `rtl_pci_disable_aspm()`, `_rtl_pci_init_tx_ring()`, `_rtl_pci_init_rx_ring()`, `_rtl_pci_interrupt()`, `_rtl_pci_rx_interrupt()`, `_rtl_pci_tx_isr()`, `_rtl_pci_prepare_bcn_tasklet()`, `rtl_pci_tx()`, `rtl_pci_flush()`, `rtl_pci_start()`, `rtl_pci_stop()`, and `_rtl_pci_find_adapter()`.

## Control Flow
Probe enables PCI, selects DMA mask, allocates `ieee80211_hw`, maps BAR MMIO, identifies the Realtek hardware type, installs IO handlers, reads efuse, initializes chip software, core mac80211 state, PCI rings, registers hardware, adds debugfs/rfkill, and requests IRQ. Start resets rings, initializes BT coexistence, calls chip `hw_init`, enables interrupts, initializes RX config, and marks HAL started. TX maps mac80211 queues to hardware rings, fills descriptors, queues SKBs, stops mac80211 queues when descriptors run low, and polls hardware. Interrupt handling disables interrupts, reads chip ISR vectors, services beacon/TX/RX/FW/HSISR events, schedules tasklets, then reenables interrupts. Disconnect reverses registration, IRQ/MSI, rings, core state, chip vars, MMIO, and PCI device enablement.

## State And Persistence
`struct rtl_pci` stores `pdev`, IRQ state, TX/RX rings, descriptor counts, RX buffer size, IRQ masks, ASPM constants, retry limits, MSI state, and unload/init flags. Rings persist DMA coherent descriptors and queued SKBs while the device is active. ASPM policy is derived from module/chip constants and bridge/vendor quirks.

## Dependencies And Integration Points
Depends on Linux PCI/DMA/interrupt APIs, mac80211, shared rtlwifi core/base/ps/efuse/debug/rfkill helpers, chip `cfg->ops` descriptor methods, BT coexistence, and hardware-specific register maps.

## Risks
DMA descriptor lifetime and ownership bits are high risk. New TRX flow and old descriptor flow have different index and descriptor semantics. IRQ handler runs with interrupts disabled under `irq_th_lock`; long RX/TX work can affect latency. Probe error labels must free exactly initialized resources. ASPM quirks can cause link instability or AER storms. `rtl_pci_tx()` returns `skb->len` on descriptor pressure instead of consuming the SKB, so callers must preserve behavior.

## Test Signals
Probe/remove for every PCI ID, MSI fallback to legacy IRQ, DMA32/DMA64 selection, start/stop cycles, heavy TX/RX with queue stop/wake, RX C2H command enqueue, beacon interrupt refresh, early-mode aggregation wait queue, suspend/resume, ASPM enable/disable under IPS/LPS, and DMA/debug/lockdep checks during disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.h

## Purpose
Defines PCI constants, device IDs, queue IDs, descriptor layouts, ring structures, PCI private state, MMIO accessors, and public PCI driver operations for rtlwifi.

## Important APIs, Types, And Functions
Queue constants map hardware TX/RX queues such as `BK_QUEUE`, `BE_QUEUE`, `VI_QUEUE`, `VO_QUEUE`, `BEACON_QUEUE`, `TXCMD_QUEUE`, `MGNT_QUEUE`, `HIGH_QUEUE`, and `H2C_QUEUE`. Device IDs cover RTL8192SE/CE/DE, RTL8188EE, RTL8723AE/BE, RTL8192EE, RTL8821/12AE, and RTL8822BE. Descriptor structs include `rtl_tx_buffer_desc`, `rtl_tx_desc`, `rtl_rx_buffer_desc`, `rtl_rx_desc`, and `rtl_tx_cmd_desc`. `rtl8192_tx_ring`, `rtl8192_rx_ring`, `rtl_pci`, `mp_adapter`, and `rtl_pci_priv` hold bus state.

## Control Flow
`RTL_PCI_DEVICE()` builds PCI ID-table entries pointing to chip configs. `rtl_pci_probe()` and `rtl_pci_disconnect()` own PCI lifecycle, while `rtl_pci_ops` is called by `core.c` for adapter start/stop/TX/flush/ring reset/wait-queue insertion/ASPM.

## State And Persistence
The header lays out active PCI state: DMA addresses, descriptor arrays, SKB queues, RX buffers, indices, IRQ masks, ASPM capabilities, bridge identity, retry limits, MSI flags, and BT/LED private state.

## Dependencies And Integration Points
Depends on Linux PCI, rtlwifi `rtl_priv`, `bt_coexist_info`, LED control, and common queue/acm definitions. Inline MMIO helpers bind `rtlpriv->io.pci_mem_start` to read/write callbacks.

## Risks
Descriptor structs are packed hardware ABI. Queue numbering is shared with descriptor fill and interrupt maps. `calc_fifo_space()` assumes ring pointer arithmetic with one reserved slot. Any private-state layout change affects `ieee80211_alloc_hw()` private allocation in probe.

## Test Signals
Compile all PCI chip drivers, verify MMIO read/write callbacks, descriptor alignment, queue selection, ring reset, ASPM toggles, and `rtl_pcipriv()`/`rtl_pcidev()` casts under probe/disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.c

## Purpose
Power-save control for rtlwifi. It implements NIC enable/disable for power transitions, inactive power save (IPS), firmware-controlled leisure power save (FW LPS), software LPS driven by beacon TIM parsing, RF state serialization, delayed work callbacks, and P2P Notice of Absence/offload handling.

## Important APIs, Types, And Functions
Public APIs include `rtl_ps_enable_nic()`, `rtl_ps_disable_nic()`, `rtl_ips_nic_off()`, `rtl_ips_nic_on()`, `rtl_ips_nic_off_wq_callback()`, `rtl_lps_enter()`, `rtl_lps_leave()`, `rtl_lps_set_psmode()`, `rtl_swlps_beacon()`, `rtl_swlps_rf_awake()`, `rtl_swlps_rf_sleep()`, `rtl_swlps_wq_callback()`, `rtl_swlps_rfon_wq_callback()`, `rtl_p2p_ps_cmd()`, `rtl_p2p_info()`, and `rtl_lps_change_work_callback()`.

## Control Flow
IPS schedules delayed NIC-off work when mac80211 marks the device idle. The worker refuses IPS for non-station, P2P, linked, stopped, scanning, or key-setting states, notifies BT coexistence, sets `inactive_pwrstate`, and calls `_rtl_ps_inactive_ps()` to change RF state and optionally ASPM. LPS enter/leave either runs immediately or schedules `lps_change_work`; FW LPS sends `HW_VAR_FW_LPS_ACTION` and P2P power commands, while SW LPS parses beacon TIMs, sleeps after multicast-free beacons, and wakes before DTIM. P2P helpers parse beacon/probe/action vendor IEs for NoA and CTWindow data, then send `HW_VAR_H2C_FW_P2P_PS_OFFLOAD`.

## State And Persistence
`rtl_ps_ctl` stores RF power state, RF-off reasons, `rfchange_inprogress`, inactive/LPS settings, FW/SW PS flags, DTIM state, multicast buffering, `state_inap`, and `p2p_ps_info`. Runtime state is volatile and tied to association, scan, and RF transitions.

## Dependencies And Integration Points
Uses chip `cfg->ops` for `hw_init`, `hw_disable`, interrupts, RF power state, channel/bandwidth, and H2C hardware vars. It interacts with PCI ring reset/ASPM, watchdog/deferred work, BT coexistence, mac80211 PS flags, beacon parser helpers, and TX completion state.

## Risks
RF state changes are serialized but contain wait loops and multiple locks; deadlocks or long delays are possible. IPS/LPS must not run during scans, key programming, P2P operations, or early association handshakes. SW LPS sleep timing subtracts 40 ms from beacon-derived intervals and can underflow if assumptions change. P2P IE parsing uses vendor-element offsets and length checks that must remain exact.

## Test Signals
Exercise idle/unidle IPS, FW LPS enter/leave, SW LPS beacon/TIM handling, nullfunc PM transitions, busy-traffic wakeups, scans while linked, P2P GO/client NoA/CTWindow updates, BT coexistence notifications, ASPM toggles, and lockdep around RF/LPS/IPS locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.h

## Purpose
Declares rtlwifi power-save entry points shared by core, PCI, RX, and chip-specific code.

## Important APIs, Types, And Functions
`MAX_SW_LPS_SLEEP_INTV` caps software LPS sleep to five beacon intervals. Declarations cover NIC enable/disable, IPS off/on/work callback, LPS enter/leave/mode setting, SW LPS beacon/work/RF callbacks, P2P power-save command and information parsing, and LPS change work.

## Control Flow
The core calls IPS/LPS functions from mac80211 config and BSS transitions. PCI TX/RX completion paths call LPS leave under traffic. RX paths feed beacons/action frames to SW LPS and P2P parsing.

## State And Persistence
No storage is defined here; functions mutate `rtlpriv->psc`, work items, RF state, and firmware power-save variables.

## Dependencies And Integration Points
Requires `ieee80211_hw`, `work_struct`, chip ops, and bus interface ops. It is the API boundary between power policy and bus/core paths.

## Risks
Callers must pass the correct `may_block` value for contexts that cannot sleep. Work callbacks assume they are embedded in `struct rtl_works`.

## Test Signals
Build coverage for all declarations, LPS enter/leave from blocking and nonblocking contexts, delayed IPS/SW LPS work, and P2P PS command emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pwrseqcmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pwrseqcmd.h

## Purpose
Defines the compact power-sequence command format used by Realtek chips and declares the parser implemented in `core.c`.

## Important APIs, Types, And Functions
Command IDs are `PWR_CMD_READ`, `PWR_CMD_WRITE`, `PWR_CMD_POLLING`, `PWR_CMD_DELAY`, and `PWR_CMD_END`. Base selectors include MAC, USB, PCIE, and SDIO. Masks select interface, fabrication vendor, and chip cut. `struct wlan_pwr_cfg` packs register offset, cut mask, fab mask, interface mask, base, command, mask, and value. Getter macros expose each packed field. `rtl_hal_pwrseqcmdparsing()` applies an array of commands.

## Control Flow
Chip-specific power arrays are filtered by cut/fab/interface. Matching commands read, write masked bytes, poll until masked value matches, delay in us/ms, or terminate at END.

## State And Persistence
No state is stored in the header. Commands mutate hardware registers through `rtl_read_byte()`/`rtl_write_byte()` when parsed.

## Dependencies And Integration Points
Includes `wifi.h` for `rtl_priv` and bit helpers. Used by power-on/off and radio state sequences in chip-specific code.

## Risks
The command array must be correctly terminated. Bitfield packing is compiler ABI sensitive but local to kernel C usage. Polling has a fixed max loop in the parser, so incorrect masks or values can cause slow failure.

## Test Signals
Run chip power-on/off sequences for PCI/USB/SDIO masks, verify register writes and polling success, and cover each delay unit plus malformed/no-match command arrays in review or instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/pwrseqcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.c

## Purpose
Registers a lightweight rtlwifi mac80211 rate-control algorithm named `rtl_rc`. Firmware controls actual rates, while this file seeds mac80211-visible rate series, handles special low-rate traffic, sets HT/VHT flags, and triggers TX BA aggregation sessions from TX status.

## Important APIs, Types, And Functions
`rtl_rate_control_register()` and `rtl_rate_control_unregister()` expose lifecycle. `rtl_rate_ops` binds `rtl_get_rate()`, `rtl_tx_status()`, allocation/free callbacks, and empty update/init callbacks. `_rtl_rc_get_highest_rix()` chooses a maximum legacy/MCS/VHT rate index from band, wireless mode, station capabilities, bandwidth, and RF chain count. `_rtl_rc_rate_set_series()` fills one `ieee80211_tx_rate`. `_rtl_tx_aggr_check()` decides when to start BA for a TID.

## Control Flow
For each TX, `rtl_get_rate()` chooses rate 0 for special/non-data frames and otherwise fills up to four descending attempts. TX status ignores non-data, special, multicast, and broadcast frames, then starts a BA session for HT QoS data when the TID aggregation state is stopped and scanning/early-link guards allow it.

## State And Persistence
Per-station allocation creates `struct rtl_rate_priv` and stores it in `rtlpriv->rate_priv`. Aggregation state lives in `rtl_sta_info.tids[tid].agg.agg_state`. Rate decisions read `rtl_hal`, `rtl_phy`, `rtl_mac`, and station `wireless_mode`.

## Dependencies And Integration Points
Depends on mac80211 rate-control API, station private data from `core.c`, RF type helpers, special-data detection in `base.h`, and aggregation callbacks in the shared driver.

## Risks
Firmware controls true rate selection, so mac80211-visible rates can be approximate. VHT paths dereference `sta` after wireless-mode checks; callers should ensure VHT data frames have station context. BA session start is heuristic and tied to traffic, scan, and early association counters.

## Test Signals
Register/unregister module path, TX rates for B/G/A/N/AC on 2.4/5 GHz and 1T/2T+ RF, special DHCP/EAPOL/management low-rate behavior, HT/VHT flags, and BA start on sustained QoS unicast data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.h

## Purpose
Header for rtlwifi rate-control constants, per-rate-control private state, and registration functions.

## Important APIs, Types, And Functions
Defines maximum rate indexes for B, G, A, N MCS7/MCS15, and AC MCS7/MCS8/MCS9. `struct rtl_rate_priv` currently stores `ht_cap`. Public APIs are `rtl_rate_control_register()` and `rtl_rate_control_unregister()`.

## Control Flow
Module init/exit paths call register/unregister so mac80211 can select the `rtl_rc` algorithm. `rc.c` uses the constants when building rate series.

## State And Persistence
The header defines a small per-station rate-private structure but no global state. Runtime instances are allocated by `rtl_rate_alloc_sta()`.

## Dependencies And Integration Points
Integrated with mac80211 rate-control registration and station private state.

## Risks
Constants must match mac80211 legacy and MCS index semantics. Extending `rtl_rate_priv` requires matching allocation/free users.

## Test Signals
Build and module lifecycle coverage plus expected max rate index selection in B/G/A/N/AC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.c

## Purpose
Implements rtlwifi regulatory-domain setup and notifier handling. It maps efuse channel plans to Realtek country-code enums, selects static custom regulatory domains, applies radar/passive-scan/beaconing flags, stores alpha2, and updates channel flags on regulatory notifications.

## Important APIs, Types, And Functions
Public APIs are `rtl_regd_init()` and `rtl_reg_notifier()`. Internals include country table `all_countries`, static `ieee80211_regdomain` definitions for 2.4 GHz/5 GHz combinations, `_rtl_is_radar_freq()`, `_rtl_reg_apply_beaconing_flags()`, `_rtl_reg_apply_active_scan_flags()`, `_rtl_reg_apply_radar_flags()`, `_rtl_regdomain_select()`, `_rtl_regd_init_wiphy()`, `_rtl_regd_find_country()`, and `channel_plan_to_country_code()`.

## Control Flow
Initialization converts `rtlpriv->efuse.channel_plan` into a country code, falls back to world-wide 13 on invalid values, fills `rtlpriv->regd.alpha2`, installs the notifier, sets `REGULATORY_CUSTOM_REG`, applies the selected static regdomain to the wiphy, and applies radar/world flags. Later notifier calls always reapply DFS radar flags and, for country IE events, relax beaconing/active-scan flags where the regulatory rule allows it.

## State And Persistence
Persistent runtime state is `rtlpriv->regd.country_code` and `alpha2`, derived from efuse. Channel flags live in wiphy band/channel structures and change over time with regulatory events and beacon hints.

## Dependencies And Integration Points
Depends on cfg80211 regulatory APIs, wiphy bands, efuse channel plan populated during probe, debug logging, and mac80211 channel flags.

## Risks
Static domains are broad approximations of Realtek channel plans. `channel_plan_to_country_code()` only maps a small set of plan values. Radar rules are hard-coded for 5260-5700 MHz. Active scan on channels 12/13 is selectively relaxed, so incorrect initiator handling can violate local restrictions.

## Test Signals
Probe devices with channel plans 0x20/0x21/0x22/0x25/0x32/0x41/0x7f and invalid values, verify selected alpha2/regdomain, channel 12/13 passive-scan behavior, DFS flags on 5 GHz radar channels, and notifier effects for user/core/driver/country-IE requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.h

## Purpose
Declares regulatory data structures, country-code enum values, compatibility aliases for channel flags, and rtlwifi regulatory initialization/notifier APIs.

## Important APIs, Types, And Functions
`struct country_code_to_enum_rd` maps Realtek country codes to ISO alpha2 strings. `enum country_code_type_t` includes FCC, IC, ETSI, Spain, France, MKK variants, Israel, TELEC, MIC, global/world-wide plans, and 5 GHz-all world-wide. APIs are `rtl_regd_init()` and `rtl_reg_notifier()`.

## Control Flow
Chip/core initialization calls `rtl_regd_init()` after efuse channel plan is known. cfg80211 calls `rtl_reg_notifier()` when regulatory requests arrive.

## State And Persistence
No storage is declared here. Enum values are stored in `rtlpriv->regd.country_code` and influence wiphy channel flags.

## Dependencies And Integration Points
Requires cfg80211/mac80211 `wiphy` and `regulatory_request` types. The aliases map old `NO_IBSS` and passive-scan naming to `IEEE80211_CHAN_NO_IR`.

## Risks
Enum values are coupled to the country table and regdomain selection switch. Adding new channel plans requires updates in both header and implementation.

## Test Signals
Build against current kernel channel flag names, initialize all enum values that have switch coverage, and verify notifier callback wiring on registered wiphys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/Makefile

## Purpose
Kernel build fragment for the RTL8188EE rtlwifi subdriver. It defines the object list that links into `rtl8188ee.o` and gates the module on `CONFIG_RTL8188EE`.

## Important APIs, Types, And Functions
`rtl8188ee-objs` includes `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `pwrseq.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8188EE) += rtl8188ee.o` attaches the composite object to Kbuild.

## Control Flow
When the kernel config enables RTL8188EE, Kbuild compiles the listed chip-specific objects and links them with the shared rtlwifi core infrastructure.

## State And Persistence
No runtime state. The object list defines which chip-specific implementation units are present.

## Dependencies And Integration Points
Integrates with the parent rtlwifi Makefile/Kconfig, shared `core.c`, `pci.c`, `efuse.c`, `ps.c`, `rc.c`, and the Linux kernel module build system.

## Risks
Missing objects cause unresolved symbols or incomplete chip behavior. Object ordering is mostly link-order only, but all listed files must remain synchronized with RTL8188EE declarations.

## Test Signals
Build with `CONFIG_RTL8188EE=m` and `=y`, ensure `rtl8188ee.o` links, loads, and binds to the RTL8188EE PCI ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/def.h

## Purpose
RTL8188EE/related Realtek definition header for chip-version bits, loopback/RF/power/interface enums, TX descriptor queue selectors, descriptor rate IDs, CCK PHY status layout, and H2C command metadata.

## Important APIs, Types, And Functions
Macros define prime channel offsets, RX queue IDs, C2H header length, chip bonding identifier extraction, chip/version bit fields, masks, and helper predicates such as `IS_81XXC()`, `IS_8723_SERIES()`, `IS_92D()`, `IS_NORMAL_CHIP()`, `IS_1T1R()`, `IS_2T2R()`, and `IS_CHIP_VENDOR_UMC()`. Enums include `version_8188e`, `rtl819x_loopback_e`, `rf_optype`, `rf_power_state`, `power_save_mode`, `power_polocy_config`, `interface_select_pci`, `rtl_desc_qsel`, and `rtl_desc92c_rate`. Structs include `phy_sts_cck_8192s_t` and `h2c_cmd_8192c`.

## Control Flow
Chip-specific hardware, PHY, RF, TX/RX, and firmware files include this header to decode chip version, select RF/power paths, classify descriptor queues, and map rates into descriptor fields.

## State And Persistence
No storage is declared. The definitions interpret hardware version words, descriptor fields, received PHY status, and H2C command buffers.

## Dependencies And Integration Points
Depends on kernel bit macros and is consumed by the RTL8188EE object set in the Makefile. Its constants align with shared rtlwifi queue/rate/power abstractions.

## Risks
The header name guard says `__RTL92C_DEF_H__`, showing heritage from related chips; changes can affect multiple assumptions in RTL8188EE code. Bit masks and descriptor rate IDs are hardware ABI and must not drift. `RF_TYPE_1T1R` is expressed as an inverted mask, so careless boolean use is risky.

## Test Signals
Compile RTL8188EE objects, verify chip-version detection, RF path/rate descriptor encoding, queue selector use in TX descriptors, CCK PHY status parsing, and H2C command construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/def.h -->
