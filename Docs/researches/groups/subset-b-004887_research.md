# Research: subset-b-004887

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.c

## Purpose
Implements the RTL8192DE PCIe PHY layer: BB/MAC/RF table loading, BB register access, RF-path configuration, bandwidth changes, band/channel switching, IQK and LCK calibration, RF power-state transitions, and dual-MAC/dual-PHY coordination. This is the main hardware-tuning file for the 8192DE variant and is wired into the driver's `rtl_hal_ops` from `sw.c`.

## Important APIs, Types, And Functions
The exported entry points are `rtl92d_phy_query_bb_reg()`, `rtl92d_phy_set_bb_reg()`, `rtl92d_phy_mac_config()`, `rtl92d_phy_bb_config()`, `rtl92d_phy_rf_config()`, `rtl92d_phy_config_rf_with_headerfile()`, `rtl92d_phy_set_bw_mode()`, `rtl92d_phy_sw_chnl()`, `rtl92d_phy_set_rf_power_state()`, `rtl92d_phy_set_poweron()`, `rtl92d_phy_check_poweroff()`, `rtl92d_phy_lc_calibrate()`, `rtl92d_update_bbrf_configuration()`, `rtl92d_phy_iq_calibrate()`, and `rtl92d_phy_reload_iqk_setting()`. Internal helpers cover static RF parameter tables for C-cut 2.4G/5G paths, IMR reload, RF SYN channel programming, IQK path-A/path-B trial execution, IQK similarity selection, IQK matrix programming, LCK curve-index generation, and stepwise channel command execution.

## Control Flow
Initialization starts with `rtl92d_phy_bb_config()`, which initializes common register definitions, enables BB/RF clocks and reset bits, then calls `_rtl92d_phy_bb_config()` to load PHY register tables, optional power-index PG data, and AGC tables from `table.c`. `rtl92d_phy_rf_config()` delegates RF6052 setup to `rf.c`, while `rtl92d_phy_mac_config()` writes the MAC table and adjusts aggregation limits for single-PHY versus multi-PHY operation.

Channel changes enter `rtl92d_phy_sw_chnl()`. It waits for LCK to finish, switches wireless band when a single-PHY/both-band device crosses channel 14, validates band/channel consistency, then executes pre, RF-dependent, and post command arrays. The RF command writes `RF_CHNLBW`, reloads IMR, applies channel-specific RF SYN settings, and reloads IQK matrix data. Bandwidth changes enter `rtl92d_phy_set_bw_mode()`, update MAC bandwidth registers, CCK/OFDM sideband state, BB RF mode bits, and RF6052 bandwidth.

Calibration is multi-stage. `rtl92d_phy_iq_calibrate()` performs up to three IQK trials, compares results with `_rtl92d_phy_simularity_compare()`, stores the winning matrix per channel, and writes TX/RX IQ imbalance registers. LCK waits for scan quiescence, pauses TX, puts RF paths in standby, captures curve-count data, calculates 2G/5G curve indexes, restores queues and RF modes, then reloads the channel-specific LCK setting.

## State And Persistence
State is stored mostly in `rtlpriv->phy`, `rtlpriv->rtlhal`, `rtlpriv->efuse`, and `rtlpriv->psc`. Important persistent fields include `current_channel`, `current_chan_bw`, `rfreg_chnlval[]`, `reg_rf3c[]`, `iqk_matrix[]`, IQK backup registers, `need_iqk`, `lck_inprogress`, `sw_chnl_inprogress`, `set_bwmode_inprogress`, `rfpwr_state`, MAC/PHY mode, interface index, current band type, internal-PA flags, and dual-MAC DBI flags. The static `curveindex_2g[]` and `curveindex_5g[]` arrays cache LCK-derived channel synthesizer values after calibration.

## Dependencies And Integration Points
Depends on common rtlwifi PCI, power-save, register, RF, DM, and PHY helpers plus the 8192DE table arrays. It integrates with mac80211 through the `rtl_hal_ops` callbacks in `sw.c`, with RF6052 setup in `rf.c`, with firmware/hardware mode state from `hw.c`, and with global dual-MAC locks from `sw.h`. The DBI read/write paths are critical when one MAC programs the other PHY/radio in dual-MAC dual-PHY mode.

## Risks
This file is timing and ordering sensitive. Incorrect DBI direction, band/channel mismatch, wrong 2G/5G path selection, or stale `during_mac*init_*` flags can program the wrong PHY. IQK and LCK save/restore paths touch many BB/MAC/RF registers and can leave TX paused, RF disabled, or imbalance matrices corrupted if interrupted or partially failed. `rtl92d_phy_reload_iqk_setting()` contains a disabled redo branch (`if (0 && ...)`), so missing per-channel IQK data may silently fall back to previously stored/default values. RF sleep waits for PCI TX queues but has bounded retry behavior, so pending packets and power transitions can race under stress.

## Test Signals
Useful signals are successful probe and firmware bring-up on RTL8192DE, 2.4G and 5G association, channel changes across channel 14, 20/40 MHz transitions, dual-MAC dual-PHY startup order, suspend/resume and IPS/LPS RF state transitions, and stable throughput after IQK/LCK. Kernel logs should show no `WARN_ONCE` for band/channel mismatch, no power-off timeout, no RF switch timeout, and no repeated IQK/LCK failures. RF register readback, RSSI stability, EVM/throughput, and scan results are practical hardware validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.h

## Purpose
Declares the RTL8192DE PHY interface and constants used by the PCIe PHY implementation. It exposes the BB/RF configuration, channel, bandwidth, RF power, power-on/off, IQK, LCK, and BB/RF update functions consumed by `sw.c`, `rf.c`, `hw.c`, and common rtl8192d code.

## Important APIs, Types, And Functions
The header defines channel-switch command capacities (`MAX_PRECMD_CNT`, `MAX_RFDEPENDCMD_CNT`, `MAX_POSTCMD_CNT`), RF sleep wait limits, IQK register counts, EEPROM/efuse offset constants, and `enum swchnlcmd_id` plus `struct swchnlcmd`. Exported prototypes cover BB register access, MAC/BB/RF configuration, RF table loading, bandwidth setting, software channel switch, RF power-state setting, power-on/check-poweroff, LCK, BBRF update, IQK, and IQK reload.

## Control Flow
The header does not execute control flow directly, but it defines the command IDs used by `phy.c` to build pre/RF/post channel-switch command arrays. `rtl92d_phy_sw_chnl()` consumes `struct swchnlcmd` entries to run TX power updates, port writes, and RF writes in ordered stages.

## State And Persistence
No state is allocated in this header. The constants shape persistent arrays and bounded loops in `phy.c`, especially channel-switch command arrays and IQK backup matrix dimensions. The EEPROM offset macros document efuse layout positions used by companion parsing/configuration code.

## Dependencies And Integration Points
Requires declarations for `struct ieee80211_hw`, `enum nl80211_channel_type`, `enum radio_path`, `enum rf_content`, and `enum rf_pwrstate` from rtlwifi/mac80211 headers included by users. It is included by 8192DE `phy.c`, `rf.c`, `sw.c`, and likely hardware initialization code to expose PHY operations.

## Risks
There is a prototype typo, `rtl92c_phy_config_rf_with_feaderfile`, that does not match the implemented `rtl92d_phy_config_rf_with_headerfile()` and appears unused here. Command array limits are fixed; adding new channel-switch commands without respecting these sizes would fail command insertion. Header constants encode chip-specific magic numbers, so sharing them across variants would be risky.

## Test Signals
Build coverage is the main signal: all translation units including this header should compile without missing enum or prototype conflicts. Runtime channel-switch tests indirectly validate the `swchnlcmd` structure and limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.c

## Purpose
Implements RTL8192DE RF6052 radio setup and helper routines for temporarily enabling or powering down the other PHY/radio in dual-MAC dual-PHY configurations. It is the RF table-loading bridge between `phy.c`, static RF arrays in `table.c`, and the dual-MAC DBI access model.

## Important APIs, Types, And Functions
`rtl92d_phy_enable_anotherphy()` checks whether the peer MAC is powered and, if needed, enables BB/RF power through DBI writes. `rtl92d_phy_powerdown_anotherphy()` powers the peer radio path down when the peer MAC is not active. `rtl92d_phy_rf6052_config()` selects one or two RF paths, handles single-PHY versus dual-MAC dual-PHY startup, configures RF environment bits, loads `radioa_txt` or `radiob_txt` through `rtl92d_phy_config_rf_with_headerfile()`, restores RF environment state, and powers down temporarily enabled radios.

## Control Flow
RF configuration first derives `num_total_rfpath` from `rtlphy->rf_type`. In dual-MAC dual-PHY mode it may require MAC0 on 2.4G to pre-load Radio B via PHY1, or MAC1 on 5G to pre-load Radio A via PHY0. If the peer MAC is already on, it assumes both radio tables are loaded and returns success. For each selected RF path, it saves RFENV bits, enables RF serial interface environment, sets address/data length fields, loads the appropriate RF table, then restores RFENV. Temporary peer PHY access is unwound by `rtl92d_phy_powerdown_anotherphy()`.

## State And Persistence
The file mutates `rtlhal->during_mac0init_radiob`, `rtlhal->during_mac1init_radioa`, and `rtlphy->num_total_rfpath`. Those flags alter BB register access in `phy.c` so reads/writes go through DBI to the peer PHY while RF tables are loaded. Actual persistent radio state lives in hardware RF registers populated from table arrays.

## Dependencies And Integration Points
Depends on rtlwifi register I/O, DBI helpers from 8192DE hardware code, common PHY/RF definitions, RF content identifiers from `phy.h`, DM and hardware headers, and the RF register tables in `table.c`. It is called through `rtl92d_phy_rf_config()` in `phy.c` during hardware initialization.

## Risks
The dual-MAC path is fragile because control flags redirect later BB register operations. A failure before flags are cleared could make subsequent register access target the wrong PHY. The "peer MAC already on" shortcut assumes the radio tables have already been loaded, which depends on startup ordering. Error handling returns the current status but does not perform elaborate restoration beyond the normal environment restore/powerdown paths.

## Test Signals
Test single-MAC single-PHY, dual-MAC dual-PHY MAC0-first, and MAC1-first initialization. Hardware logs should show successful Radio A/B table loading, no "Radio[%d] Fail!!" messages, correct RF path count, and valid RF register readback after initialization. Dual-MAC tests should verify one interface does not break the other's radio state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.h

## Purpose
Declares the small RTL8192DE RF helper interface used by PHY and hardware initialization code.

## Important APIs, Types, And Functions
Exports `rtl92d_phy_rf6052_config()` for RF table programming, `rtl92d_phy_enable_anotherphy()` for temporary peer-PHY enablement, and `rtl92d_phy_powerdown_anotherphy()` for restoring the peer-PHY power state.

## Control Flow
The header has no executable flow. Its prototypes support the flow where `phy.c` calls RF6052 configuration and the RF/channel code temporarily enables the other PHY before DBI-based operations.

## State And Persistence
No state is owned here. The declared functions mutate `rtl_hal` flags and hardware RF power/register state in their implementations.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` and bool definitions from included users. It is consumed by `phy.c` and `rf.c` and complements `phy.h`.

## Risks
The API exposes low-level dual-PHY power controls without ownership annotations; callers must pair temporary enablement and powerdown correctly.

## Test Signals
Compilation and successful RF initialization are the primary signals. Dual-MAC bring-up exercises all three declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.c

## Purpose
Provides the RTL8192DE PCI module wiring. It initializes software variables, declares module parameters and firmware, maps chip registers and rates into the rtlwifi abstraction, installs the `rtl_hal_ops` callback table, declares PCI IDs, and registers/unregisters the PCI driver.

## Important APIs, Types, And Functions
`rtl92d_init_aspm_vars()` configures PCI ASPM policy constants. `rtl92d_init_sw_vars()` initializes DM defaults, current channel, dual-MAC buffer behavior, TX/RX configuration masks, IRQ masks, power-save settings, early mode, per-TID wait queues, firmware buffer allocation, and asynchronous firmware request. `rtl92d_deinit_sw_vars()` frees firmware memory and purges wait queues. `rtl8192de_hal_ops` is the central integration object for PCI probe, MAC/PHY/RF operations, TX/RX descriptor handling, security, channel/bandwidth, watchdog, LED, and calibration. `rtl92de_hal_cfg` maps abstract rtlwifi indices to RTL8192DE register/rate constants. Module init/exit register the `pci_driver`.

## Control Flow
On module load, `rtl92de_module_init()` registers `rtl92de_driver`. `rtl_pci_probe()` receives matching device IDs and uses `rtl92de_hal_cfg`, which points back to the callbacks in this file. Software initialization sets default operating state, allocates a firmware buffer, and starts `request_firmware_nowait()` for `rtlwifi/rtl8192defw.bin`. Later core flows call the configured operations for hardware initialization, interrupt control, networking mode changes, descriptor fill/query, channel switching, RF power, and calibration. Module exit unregisters the PCI driver.

## State And Persistence
Persistent driver state initialized here includes DM flags, `current_channel`, dual-MAC `disable_amsdu_8k`, PCI RX buffer size, `transmit_config`, `receive_config`, IRQ masks, power-save knobs, firmware buffer pointer/size, `fwctrl_psmode`, early-mode flag, and per-TID skb queues. The file also defines global spinlocks `globalmutex_power`, `globalmutex_for_fwdownload`, and `globalmutex_for_power_and_efuse` used by dual-MAC power and firmware/efuse code.

## Dependencies And Integration Points
Depends on the rtlwifi core, PCI glue, rtl8192d common modules, and local PHY/DM/HW/TRX/LED implementations. It integrates with Linux PCI and module infrastructure, request_firmware, mac80211 through rtlwifi, and kernel PM via `SIMPLE_DEV_PM_OPS`.

## Risks
Asynchronous firmware loading requires the allocated firmware buffer to survive until callback completion and deinit. The `rtl_hal_cfg` callback table is dense; incorrect function assignment can cause failures far from probe. Module parameters directly alter power-save, crypto, ASPM, and debug behavior. Dual-MAC state relies on global spinlocks declared here, making cross-file ordering and lock use important.

## Test Signals
Build the module, verify PCI IDs bind to RTL8192DE hardware, confirm firmware request and callback success, and exercise module unload/reload for firmware buffer and queue cleanup. Runtime signals include interrupts, TX/RX, scan/association, suspend/resume, ASPM behavior, debug module parameters, and dual-MAC operation without lock warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.h

## Purpose
Declares shared RTL8192DE global spinlocks for dual-MAC power, firmware download, and power/efuse coordination.

## Important APIs, Types, And Functions
Exports `globalmutex_power`, `globalmutex_for_fwdownload`, and `globalmutex_for_power_and_efuse` as `spinlock_t` objects. Their definitions are in `sw.c`.

## Control Flow
The header has no executable flow. Callers include it to serialize critical low-level register operations across MAC instances.

## State And Persistence
The locks themselves are persistent module globals. They protect shared hardware state such as MAC power-on/off markers and other dual-MAC register operations.

## Dependencies And Integration Points
Requires Linux spinlock declarations via included users. `phy.c` uses `globalmutex_power` around dual-MAC power-on/off checks. Other RTL8192DE files may use the firmware and efuse locks.

## Risks
Global locks create cross-device coupling for devices handled by the same module. Any caller must use IRQ-safe locking consistently and avoid long register polling while holding the lock.

## Test Signals
Lockdep under dual-MAC bring-up, concurrent interface power transitions, firmware download, and efuse access is the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.c

## Purpose
Provides static RTL8192DE register programming tables used by PHY, RF, MAC, power-index, and AGC configuration code. The file is data-only and encodes chip-vendor initialization values for 2T operation, internal/external PA variants, 2.4G/5G AGC tables, and MAC register defaults.

## Important APIs, Types, And Functions
The exported arrays are `rtl8192de_phy_reg_2tarray`, `rtl8192de_phy_reg_array_pg`, `rtl8192de_radioa_2tarray`, `rtl8192de_radiob_2tarray`, `rtl8192de_radioa_2t_int_paarray`, `rtl8192de_radiob_2t_int_paarray`, `rtl8192de_mac_2tarray`, `rtl8192de_agctab_array`, `rtl8192de_agctab_5garray`, and `rtl8192de_agctab_2garray`. Each is declared with a matching length macro in `table.h`.

## Control Flow
There is no executable control flow. Consumers iterate these arrays as address/value pairs or, for `rtl8192de_phy_reg_array_pg`, address/mask/data triples. `phy.c` applies PHY and AGC tables via `rtl_set_bbreg()`, applies power-group data via `rtl92d_store_pwrindex_diffrate_offset()`, applies RF arrays via `rtl_rfreg_delay()`, and applies MAC defaults via byte writes.

## State And Persistence
The arrays are persistent module data. They do not change at runtime. Their values become persistent hardware state only after initialization writes them to device registers. Internal-PA efuse flags choose the internal-PA RF arrays for each path.

## Dependencies And Integration Points
Included by `phy.c` through `table.h`. The array layout and length macros must match consumer iteration steps exactly. Register names and semantics come from rtl8192d common headers, but this file stores raw numeric addresses and values.

## Risks
The main risk is data integrity. A wrong length macro, odd number of address/value entries, bad register value, or accidental edit can break hardware initialization without compiler errors. The large raw tables are hard to review and mostly validated only on real hardware. Internal-PA and band-specific table selection must match efuse parsing and current band state.

## Test Signals
Successful BB/RF/MAC initialization is the primary test. Hardware probe, RF register readback, scan sensitivity, 2.4G/5G association, TX power by rate, and AGC behavior validate the tables. Static checks can verify array sizes match length macros and address/value or address/mask/value grouping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.h

## Purpose
Declares the RTL8192DE static configuration arrays and their expected lengths for use by PHY and RF initialization code.

## Important APIs, Types, And Functions
Defines length macros for PHY, power-group, Radio A/B, internal-PA Radio A/B, MAC, full AGC, 5G AGC, and 2G AGC tables. Declares extern `u32` arrays matching those lengths.

## Control Flow
No control flow is implemented. The macros control iteration bounds in `phy.c` and therefore determine how many raw register table entries are applied.

## State And Persistence
No mutable state is owned here. The declarations point to immutable module-level data in `table.c`.

## Dependencies And Integration Points
Included by `table.c` and `phy.c`. It depends on `u32` being available from the including compilation unit. It forms the contract between table data and configuration loops.

## Risks
Any mismatch between length macros and actual arrays can cause truncated initialization or out-of-bounds reads. Because the tables use raw `u32` values, the header provides no type-level distinction between pair and triple table layouts.

## Test Signals
Compiler array-size checks catch some mismatches. Runtime PHY/RF initialization, especially PG power-index loading and AGC table selection, validates the declared lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.c

## Purpose
Implements RTL8192DE PCIe TX descriptor construction, command/beacon descriptor construction, TX descriptor ownership checks, and TX polling doorbells. It translates mac80211 skb/tx-info state and rtlwifi rate-control metadata into the 8192DE hardware descriptor format.

## Important APIs, Types, And Functions
`rtl92de_tx_fill_desc()` is the main data-frame descriptor builder. `_rtl92de_map_hwqueue_to_fwqueue()` maps beacons, management frames, and data priorities to firmware queue selectors. `_rtl92de_insert_emcontent()` fills the 8-byte early-mode aggregation header. `rtl92de_tx_fill_cmddesc()` builds command/beacon descriptors. `rtl92de_is_tx_desc_closed()` checks the hardware OWN bit for the current ring descriptor. `rtl92de_tx_polling()` writes `REG_PCIE_CTRL_REG` to notify hardware of queued TX work.

## Control Flow
Data TX starts by deriving frame type, sequence number, bandwidth, TCB descriptor fields, and optional early-mode skb headroom. The function DMA maps the skb, clears descriptor content, sets first-segment fields when appropriate, clamps CCK rates on 5G, enables short GI/preamble, AMPDU aggregation, RTS/CTS flags, BW/subcarrier selection, packet size, AMPDU density, encryption type, queue selector, fallback limits, rate-control policy, RDG, buffer size/address, rate ID/MAC ID, QoS, firmware-LPS hardware sequence fields, and fragmentation markers.

Command/beacon TX maps the skb, clears a descriptor, chooses 6M on 5G or 1M otherwise, uses the beacon queue selector, sets buffer address/size, enables driver rate, applies firmware-LPS sequence handling for non-QoS frames, writes a memory barrier, and sets OWN. Polling uses a special beacon bit for `BEACON_QUEUE`, otherwise shifts bit 0 by hardware queue.

## State And Persistence
The file mutates descriptors and DMA mappings owned by the PCI TX rings. It reads `rtlhal->earlymode_enable`, `rtlhal->current_bandtype`, `rtlpriv->dm.useramask`, `rtl_ps_ctl->fwctrl_lps`, `mac->bw_40`, `mac->cur_40_prime_sc`, `mac->rdg_en`, station HT bandwidth/density, and `rtl_tcb_desc` rate-control metadata. Persistent hardware-visible state is the filled descriptor plus DMA address.

## Dependencies And Integration Points
Depends on rtlwifi PCI ring structures, common TX descriptor bitfield macros from `trx_common.h`, mac80211 skb/tx-info/station structures, DMA mapping APIs, PHY band state, LED header inclusion, and rtlwifi rate-control helpers. The operation is installed as `.fill_tx_desc`, `.fill_tx_cmddesc`, `.is_tx_desc_closed`, and `.tx_polling` in `sw.c`.

## Risks
DMA mapping failure returns without filling a usable descriptor, so callers must tolerate dropped TX. The function pushes early-mode bytes into the skb and sets descriptor packet offset; incorrect headroom assumptions or packet-size accounting can corrupt TX. Descriptor bitfields are hardware-specific, and 5G CCK clamping, AMPDU limits, encryption mapping, and useramask MACID/rate-id selection must match firmware expectations. `rtl92de_is_tx_desc_closed()` ignores its `index` argument and uses `ring->idx`, which is intentional only if callers query the current descriptor.

## Test Signals
Exercise data, management, beacon, QoS, nullfunc/control, encrypted WEP/TKIP/CCMP, AMPDU, early-mode, 20/40 MHz, 2.4G/5G, and firmware-LPS TX paths. Signals include clean DMA mapping, correct descriptor OWN transitions, no TX hangs, valid rate/MACID selection, successful beacon transmission, and no hardware queue stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.h

## Purpose
Defines the RTL8192DE TX/RX descriptor sizes, the packed TX descriptor layout, descriptor-clear helper, and TX descriptor operation prototypes.

## Important APIs, Types, And Functions
Defines `TX_DESC_SIZE`, `TX_DESC_AGGR_SUBFRAME_SIZE`, `RX_DESC_SIZE`, `TX_DESC_NEXT_DESC_OFFSET`, `USB_HWDESC_HEADER_LEN`, and `CRCLENGTH`. `clear_pci_tx_desc_content()` zeroes descriptor content only up to `TX_DESC_NEXT_DESC_OFFSET`, preserving link fields beyond that offset. `struct tx_desc_92d` models the hardware descriptor bitfields. Prototypes expose data descriptor fill, command descriptor fill, descriptor-closed check, and TX polling.

## Control Flow
The inline clear helper is used before descriptor fill. It bounds zeroing to the smaller of the requested size and the next-descriptor-address offset so ring linkage fields are not destroyed.

## State And Persistence
The packed descriptor structure is hardware-visible state once written into a PCI TX ring. The header itself owns no mutable state.

## Dependencies And Integration Points
Used by `trx.c` and the rtlwifi PCI layer. The descriptor layout must match Realtek hardware and common descriptor macro expectations. It depends on Linux types, endian annotations, and mac80211/rtlwifi structures from including files.

## Risks
C bitfields are sensitive to compiler layout, though this follows the driver family convention. Clearing only part of the descriptor is correct for linked rings but dangerous if reused outside that context. The constant `USB_HWDESC_HEADER_LEN` is used here for PCI descriptor offsets due shared Realtek naming.

## Test Signals
Compile-time packing and runtime TX success validate the layout. Descriptor dumps, OWN transitions, DMA address preservation, and absence of ring corruption validate `clear_pci_tx_desc_content()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/Makefile

## Purpose
Defines the Kbuild object composition for the RTL8192DU USB driver module.

## Important APIs, Types, And Functions
The `rtl8192du-objs` list includes `dm.o`, `fw.o`, `hw.o`, `led.o`, `phy.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. `obj-$(CONFIG_RTL8192DU) += rtl8192du.o` builds the aggregate object when the kernel configuration enables this driver.

## Control Flow
No runtime flow exists. Kbuild compiles the listed objects and links them into `rtl8192du.o`, then includes that object according to `CONFIG_RTL8192DU`.

## State And Persistence
No runtime state is stored. The file persists the module composition contract.

## Dependencies And Integration Points
Integrates with Linux Kbuild and the surrounding rtlwifi Makefiles/Kconfig. The object list must match the source files and exported symbols used by the DU driver.

## Risks
Omitting an object causes link failures or missing callback implementations. Including stale objects can pull in unused or conflicting symbols. The DU driver uses shared rtl8192d common files outside this directory, so Kbuild dependency ordering must remain compatible with the parent build.

## Test Signals
`CONFIG_RTL8192DU=m` or built-in kernel builds should compile and link `rtl8192du.o` without undefined symbols. Module load on matching USB hardware validates that all required objects were linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.c

## Purpose
Implements RTL8192DU dynamic-management initialization and watchdog behavior. It initializes DIG/rate-adaptive/EDCA/thermal tracking state, periodically reports RSSI to firmware or registers, runs common false-alarm/RSSI/DIG/EDCA/thermal logic, and applies a USB-specific 1R CCA power-saving heuristic on 5G single-PHY devices.

## Important APIs, Types, And Functions
`rtl92du_dm_init()` initializes driver-owned dynamic management. `rtl92du_dm_watchdog()` is the periodic runtime callback. Private helpers are `rtl92du_dm_init_1r_cca()`, `rtl92du_dm_1r_cca()`, and `rtl92du_dm_pwdb_monitor()`. The 1R CCA logic uses `dm_pstable->pre_ccastate`, `cur_ccasate`, RSSI/PWDB thresholds 35 and 30, and BB register `ROFDM0_TRXPATHENABLE`.

## Control Flow
Initialization sets `dm_type`, calls common DIG init with initial gain `0x20`, sets DIG gain bounds, initializes EDCA turbo, initializes 1R CCA state, initializes rate-adaptive mask, and initializes TX power tracking. Watchdog exits early when RF is not on, firmware power-save/race guards indicate unsafe I/O, or RF change is in progress. Otherwise it reports PWDB, updates false-alarm counters, minimum RSSI, DIG, thermal TX power tracking, EDCA turbo, and finally runs 1R CCA.

## State And Persistence
Persistent state lives in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->dm_pstable`, and common DM fields such as undecorated PWDB/RSSI and `useramask`. The 1R CCA state is intended to be hysteretic through previous/current CCA fields, though this implementation changes `cur_ccasate` and does not visibly update `pre_ccastate` in the local function.

## Dependencies And Integration Points
Depends on common rtl8192d DM and firmware helpers, BB register access, rtlwifi core state, and mac80211 opmode. It is called from DU hardware init and the DU operation table in the driver.

## Risks
The watchdog must not race RF-off or power-save transitions; the early guards are important. The local `fw_current_inpsmode` and `fwps_awake` variables are fixed constants, so firmware power-save suppression is effectively disabled here. The 1R CCA state may repeatedly write or never advance if `pre_ccastate` is not updated by common code elsewhere. RSSI report behavior differs depending on `useramask`.

## Test Signals
Association in station mode should produce H2C RSSI reports or register writes. Watch false-alarm counters, DIG behavior, EDCA turbo changes, thermal TX power tracking, and 1R/2R CCA transitions on 5G single-PHY hardware under strong and weak signal levels. RF-off and suspend paths should show no unsafe DM I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.h

## Purpose
Declares the RTL8192DU dynamic-management entry points.

## Important APIs, Types, And Functions
Exports `rtl92du_dm_init()` for setup and `rtl92du_dm_watchdog()` for periodic runtime maintenance.

## Control Flow
No executable flow. The DU driver calls initialization after hardware bring-up and watchdog through its operation table.

## State And Persistence
No state is owned here. The implementation initializes and updates `rtlpriv` DM structures.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` from including headers. Used by `dm.c`, `hw.c`, and DU module operation wiring.

## Risks
Small header, low direct risk. The only risk is drift between callback prototypes and the operation table users.

## Test Signals
Build success and watchdog invocation on a running DU interface validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.c

## Purpose
Downloads and starts RTL8192DU firmware using shared rtl8192d firmware helpers. It parses the Realtek firmware header, skips it when present, resets running RAM firmware when needed, writes the firmware image, waits for readiness, and performs firmware initialization.

## Important APIs, Types, And Functions
The single exported function is `rtl92du_download_fw()`. It uses `GET_FIRMWARE_HDR_VERSION()`, `GET_FIRMWARE_HDR_SUB_VER()`, `GET_FIRMWARE_HDR_SIGNATURE()`, `IS_FW_HEADER_EXIST()`, `rtl92d_is_fw_downloaded()`, `rtl92d_firmware_selfreset()`, `rtl92d_enable_fw_download()`, `rtl92d_write_fw()`, `rtl92d_fw_free_to_go()`, and `rtl92d_fw_init()`.

## Control Flow
The function first rejects missing firmware storage. It records firmware version and subversion from the header, advances past the 32-byte header if present, and skips direct download if firmware is already loaded. If the MCU firmware download register indicates RAM code is running, it triggers firmware self-reset and clears `REG_MCUFWDL`. It then enables firmware download mode, writes the body, disables download mode, waits for firmware to be free-to-go, logs failure if not ready, and finally calls firmware init regardless of whether the image was newly downloaded.

## State And Persistence
Updates `rtlhal->fw_version` and `rtlhal->fw_subversion`; reads `rtlhal->pfirmware`, `fwsize`, `max_fw_size`, and chip version. Persistent firmware state lives in the device MCU after successful download/init. `REG_MCUFWDL` tracks download/readiness status.

## Dependencies And Integration Points
Called by `rtl92du_hw_init()` in `hw.c`. Depends on firmware memory prepared by software init, rtl8192d common firmware routines, and register constants. The exact firmware name and request path are handled in DU `sw.c`, not this file.

## Risks
The function returns failure when firmware storage is missing, and hardware init treats some firmware errors specially. Header parsing assumes at least a valid header-sized buffer when macros inspect it. If `rtl92d_fw_free_to_go()` fails, the code still calls `rtl92d_fw_init()`, so callers must interpret the returned error carefully. Resetting running RAM code is timing sensitive.

## Test Signals
Firmware logs should show version, subversion, and signature, optional header shift, successful free-to-go, and successful firmware init. Reinitialization after suspend/reset should exercise the self-reset and already-downloaded paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.h

## Purpose
Declares the RTL8192DU firmware download entry point.

## Important APIs, Types, And Functions
Exports `rtl92du_download_fw(struct ieee80211_hw *hw)`, returning 0 on success or an error-style nonzero value from the firmware helpers.

## Control Flow
No executable flow. `hw.c` calls this during hardware initialization after MAC/LLT setup and before PHY/RF configuration.

## State And Persistence
No state is owned here. The implementation updates firmware version fields and device MCU state.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` from including headers. Used by DU hardware init and the firmware implementation.

## Risks
Low direct risk. Prototype drift would break the hardware initialization path.

## Test Signals
Build success plus successful firmware download in `rtl92du_hw_init()` validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.c

## Purpose
Implements RTL8192DU USB hardware initialization, register get/set callbacks, network-mode and BSSID filtering, beacon/TSF handling, power-off/card-disable sequences, and chip-version reporting. This is the central USB hardware lifecycle file for the DU variant.

## Important APIs, Types, And Functions
Public callbacks include `rtl92du_get_hw_reg()`, `rtl92du_set_hw_reg()`, `rtl92du_hw_init()`, `rtl92du_card_disable()`, `rtl92du_enable_interrupt()`, `rtl92du_disable_interrupt()`, `rtl92du_set_network_type()`, `rtl92du_set_check_bssid()`, `rtl92du_set_beacon_related_registers()`, `rtl92du_set_beacon_interval()`, `rtl92du_update_interrupt_mask()`, `rtl92du_read_chip_version()`, and `rtl92du_linked_set_reg()`. Private helpers cover beacon-control shadowing, queue reserved pages, TX buffer boundary, LLT table setup, USB endpoint queue priority mapping, WMAC/adaptive/EDCA/retry/operation/beacon/AMPDU initialization, MAC power-on, media status, and adapter power-off.

## Control Flow
`rtl92du_hw_init()` locks `mutex_for_hw_init`, resets IQK results, initializes MAC power and coexistence, builds the LLT table, downloads firmware, configures MAC tables, assigns reserved pages based on USB output endpoints and MAC/PHY mode, initializes queue priority and buffer boundaries, configures RX/TX DMA, RCR, adaptive control, EDCA, retry, operation mode, beacon parameters, AMPDU limits, LED hardware blinking, early mode, BB/RF tables, BBRF configuration, security CAM, IQK/LCK/PA bias, and DM. It then sets beacon control shadow state and performs final dual-PHY/scheduler tweaks.

`rtl92du_set_hw_reg()` handles DU-specific AC parameters, ACM control, RCR, join-BSS firmware report with beacon-control sequencing, TSF correction, and keep-alive no-op, delegating unknown variables to common rtl8192d code. Network type changes flow through `_rtl92du_set_media_status()`, which stops/resumes TX beacon, adjusts beacon subfunctions, writes MSR mode bits, controls LED, and sets beacon configuration.

Power-off starts in `rtl92du_card_disable()`: mark no link, set media status unspecified, pause TX, clear CR, disable RF, reset BB/MAC as allowed by MAC/PHY mode, call `rtl92du_phy_check_poweroff()`, then `_rtl92du_poweroff_adapter()` resets firmware/MCU, GPIO, LEDs, analog sequence, and power-control locking.

## State And Persistence
Maintains `rtlusb->reg_bcn_ctrl_val` as a software shadow of `REG_BCN_CTRL`; updates `mac->rx_conf`, link/opmode state, `rtlhal->last_hmeboxnum`, `rtlpriv->psc.fw_current_inpsmode`, `rtlphy->rf_mode`, `rfreg_chnlval[]`, and `ppsc->rfpwr_state`. Hardware-persistent state includes LLT entries, TX page boundaries, queue maps, RCR, MSR, EDCA, beacon timing, firmware, BB/RF registers, CAM security, and power-off markers.

## Dependencies And Integration Points
Depends on rtlwifi USB glue, CAM/security helpers, common rtl8192d firmware, hardware, PHY, and DM helpers, local DU PHY/RF/TRX/DM/FW headers, mac80211 interface types, and USB endpoint topology (`out_ep_nums`, `out_queue_sel`). It is used by DU software operation wiring and interacts heavily with firmware H2C commands.

## Risks
Initialization ordering is critical: LLT, firmware, MAC tables, queue pages, BB/RF, security, and calibration have hardware dependencies. Firmware download failure handling is subtle: hardware init can continue or fail depending on the error and register `0x1c5`. Beacon control is shadowed in software, so direct writes outside `_rtl92du_set_bcn_ctrl_reg()` can desynchronize state. Interrupt functions are no-ops for USB, so callers must not expect PCI-style masks. Power-off resets MCU/MAC/GPIO/LEDs and dual-MAC power markers; wrong interface-index handling can affect the peer MAC.

## Test Signals
Probe with one, two, and three USB OUT endpoint configurations; firmware download; LLT initialization; station/AP/adhoc mode changes; BSSID filtering; join-BSS report; TSF correction; beacon interval programming; 2.4G/5G BB/RF init; IQK/LCK; security CAM use; and card disable/unplug/suspend. Useful logs include "Init MAC failed", "Init LLT failed", firmware readiness, and no hangs during MCU reset or power off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.h

## Purpose
Declares the RTL8192DU hardware lifecycle and register-control API used by the DU driver operation table and adjacent files.

## Important APIs, Types, And Functions
Exports callbacks for getting/setting hardware variables, chip-version readout, hardware init, card disable, interrupt enable/disable, network type selection, BSSID filtering, beacon register programming, beacon interval setting, interrupt-mask update, and linked-state register updates.

## Control Flow
The header has no executable flow. The declared functions are called by rtlwifi core callbacks during probe/init, mac80211 state changes, beacon updates, link transitions, and shutdown.

## State And Persistence
No state is owned here. Implementations update `rtl_priv`, `rtl_usb`, MAC/PHY/PSC state, and hardware registers.

## Dependencies And Integration Points
Requires `struct ieee80211_hw`, `enum nl80211_iftype`, bool, and integer types from including headers. It is included by `hw.c` and DU module wiring.

## Risks
Because these declarations form the HAL contract for DU, prototype drift or missing declarations would break callback assignment. No-op interrupt functions may be surprising to callers that expect mask programming.

## Test Signals
Build success and callback invocation across init, network mode, beacon, and shutdown paths validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.c

## Purpose
Provides the RTL8192DU LED-control callback as a deliberate no-op because LED behavior is handled by hardware.

## Important APIs, Types, And Functions
The only function is `rtl92du_led_control(struct ieee80211_hw *hw, enum led_ctl_mode ledaction)`.

## Control Flow
No runtime action is taken for any LED action. Calls from network mode changes, RF power changes, or rtlwifi core LED paths simply return.

## State And Persistence
No software LED state is mutated. Hardware LED registers are initialized in `hw.c` for hardware-controlled blinking and power-off behavior.

## Dependencies And Integration Points
Included in the DU object list and exposed through `led.h`. It satisfies the rtlwifi HAL LED callback expected by common code.

## Risks
If a platform expects software LED control, link/power LED actions will not be reflected beyond hardware defaults. This is intentional for DU but should be documented in operation behavior.

## Test Signals
Calls to the LED callback should not crash or alter registers. Hardware LEDs should follow the register configuration established by `rtl92du_hw_init()` and `_rtl92du_poweroff_adapter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.h

## Purpose
Declares the RTL8192DU LED-control callback.

## Important APIs, Types, And Functions
Exports `rtl92du_led_control(struct ieee80211_hw *hw, enum led_ctl_mode ledaction)`.

## Control Flow
No executable flow. The implementation is a no-op and is installed to satisfy the rtlwifi LED operation contract.

## State And Persistence
No state is owned here. The implementation leaves LED state to hardware.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` and `enum led_ctl_mode` from including rtlwifi headers. Used by DU module wiring and `led.c`.

## Risks
Low direct risk. Consumers should not assume the function changes visible LED state.

## Test Signals
Build success and harmless callback invocation during link and power transitions validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/led.h -->
