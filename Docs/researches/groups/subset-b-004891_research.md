# subset-b-004891 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/reg.h

## Purpose
`reg.h` is the RTL8192SE register map and bit-mask contract used by the 8192SE PCI wireless driver. It names MAC, DMA, interrupt, security CAM, firmware, EFUSE, baseband, OFDM/CCK, RF, and TX power-control addresses so implementation files can use symbolic offsets rather than literals.

## APIs, Types, And Constants
The file exports macros only. Important groups include system/command registers (`REG_SYS_ISO_CTRL`, `CMDR`, `RCR`, `MSR`), queue/FIFO registers (`RQPN`, `TXPKTBUF_PGBNDY`, `TP_POLL`), interrupt masks (`IMR_*`, `INTA_MASK`), CAM/security registers and algorithms, descriptor/control bits, baseband blocks (`RFPGA*`, `RCCK*`, `ROFDM*`), TX gain registers (`RTXAGC_*`), RF register numbers (`RF_CHNLBW`, `RF_RX_AGC_HP`), and masks such as `BRFSI_RFENV`, `B3WIRE_*`, `BTX_AGCRATECCK`.

## Control Flow, State, And Persistence
There is no executable control flow or owned state. The persistence surface is hardware state: every macro corresponds to a register write/read performed by `hw.c`, `phy.c`, `rf.c`, `dm.c`, and `trx.c`. Wrong values persist in device registers until reset or reprogramming.

## Dependencies And Integration Points
The header is included across the rtl8192se subdriver and consumed through rtlwifi core I/O helpers (`rtl_read_*`, `rtl_write_*`, `rtl_set_bbreg`, RF accessors). It is also coupled to PHY table contents in `table.c`.

## Risks And Test Signals
Risks are silent hardware regressions from wrong offsets, mask width errors, or register alias confusion. Signals are compile coverage, successful probe/firmware load, interrupt delivery, RX/TX traffic, RF calibration, channel/bandwidth switching, encryption CAM operation, and suspend/resume on real RTL8192SE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.c

## Purpose
`rf.c` programs the RTL8192SE RF6052 radio path, bandwidth, and CCK/OFDM transmit power. It turns EFUSE calibration data, regulatory mode, channel width, antenna differences, and dynamic high-power state into baseband/RF register writes.

## APIs, Types, And Functions
Public entry points are `rtl92s_phy_rf6052_config`, `rtl92s_phy_rf6052_set_bandwidth`, `rtl92s_phy_rf6052_set_ccktxpower`, and `rtl92s_phy_rf6052_set_ofdmtxpower`. Internal helpers compute OFDM/MCS power bases, clamp antenna A/B deltas, apply regulatory policy, and write the six OFDM TX power registers.

## Control Flow, State, And Persistence
Power programming starts with per-channel EFUSE power levels and `rtlphy->current_chan_bw`, then adjusts for legacy/HT20 differences and regulatory mode 0-3. Dynamic TX high-power levels can override writes to low fixed values. RF config iterates each available RF path, enables the 3-wire RF environment, calls PHY RF table programming, then restores RFENV control. Register writes persist until later channel, bandwidth, power, or reset operations.

## Dependencies And Integration Points
The file depends on `reg.h`, `def.h`, `phy.h`, `dm.h`, EFUSE fields, `rtl_set_bbreg`, `rtl_set_rfreg`, and `rtl92s_phy_config_rf`. It is called from PHY channel/bandwidth setup and dynamic management.

## Risks And Test Signals
Key risks are out-of-range power, regulatory violations, A/B path underflow/overflow, and failed RF path initialization. Test signals are successful association, expected RSSI/EVM, channel-width transitions, tx power changes under near-field dynamic power, and no RF init errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.h

## Purpose
`rf.h` is the RTL8192SE RF6052 interface header. It exposes the RF power limit and the RF programming functions used by PHY and hardware setup code.

## APIs, Types, And Functions
The header defines `RF6052_MAX_TX_PWR` as `0x3f`, the maximum TX power index enforced by `rf.c`. It declares bandwidth programming, RF configuration, CCK TX power programming, and OFDM TX power programming APIs: `rtl92s_phy_rf6052_set_bandwidth`, `rtl92s_phy_rf6052_config`, `rtl92s_phy_rf6052_set_ccktxpower`, and `rtl92s_phy_rf6052_set_ofdmtxpower`.

## Control Flow, State, And Persistence
The header owns no state. Its prototypes form the call contract for code that changes persistent hardware RF and baseband state. Callers pass `struct ieee80211_hw`, channel/bandwidth values, and power-level arrays that are interpreted against `rtl_priv`, `rtl_phy`, and EFUSE state inside the implementation.

## Dependencies And Integration Points
It depends on rtlwifi/kernel type visibility from including translation units. The functions integrate with `phy.c`, `hw.c`, dynamic management, and the register definitions in `reg.h`.

## Risks And Test Signals
Risks are interface drift between declarations and `rf.c`, wrong max-power assumptions in callers, or missing include coverage. Test signals are clean builds with `CONFIG_RTL8192SE`, RF init success, and expected TX power/rate behavior across channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/sw.c

## Purpose
`sw.c` is the RTL8192SE PCI module binding file. It initializes software variables, requests firmware, declares HAL operations/configuration, maps rtlwifi generic register IDs to RTL8192SE-specific offsets, registers PCI IDs, and exposes module parameters.

## APIs, Types, And Functions
Key functions are `rtl92s_init_sw_vars`, `rtl92s_deinit_sw_vars`, firmware callback `rtl92se_fw_cb`, ASPM setup `rtl92s_init_aspm_vars`, and descriptor readiness helper `rtl92se_is_tx_desc_closed`. Static structures include `rtl8192se_hal_ops`, `rtl92se_mod_params`, `rtl92se_hal_cfg`, PCI ID table, PM ops, and `pci_driver`.

## Control Flow, State, And Persistence
Probe through rtlwifi PCI core calls `init_sw_vars`, which initializes DM flags, receive/interrupt masks, retry limits, power-save settings, ASPM constants, firmware buffer allocation, and async `request_firmware_nowait`. The callback validates size, copies firmware into `rtlhal.pfirmware`, releases the firmware object, and completes `firmware_loading_complete`. Deinit frees the firmware buffer. Module parameters persist for the module lifetime and shape power saving, ASPM, debug, and crypto behavior.

## Dependencies And Integration Points
This file integrates rtl8192se-specific implementations with rtlwifi core, mac80211, PCI probe/remove, PM suspend/resume, firmware loading, LED, PHY, DM, HW, and TRX layers.

## Risks And Test Signals
Risks include firmware load races, memory leaks, wrong IRQ/RCR masks, bad generic map entries, and descriptor ownership mistakes. Signals are module probe, firmware completion, successful TX/RX, suspend/resume, module unload without leaks, and module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.c

## Purpose
`table.c` contains RTL8192SE static hardware programming tables: baseband initialization, RF path setup, MAC defaults, per-rate power-group offsets, antenna-mode conversion tables, and AGC values.

## APIs, Types, And Data
It defines the arrays declared by `table.h`: `rtl8192sephy_reg_2t2rarray`, `rtl8192sephy_changeto_1t1rarray`, `rtl8192sephy_changeto_1t2rarray`, `rtl8192sephy_reg_array_pg`, `rtl8192seradioa_1t_array`, `rtl8192seradiob_array`, `rtl8192seradiob_gm_array`, `rtl8192semac_2t_array`, and `rtl8192seagctab_array`.

## Control Flow, State, And Persistence
There is no executable control flow. PHY/RF/MAC configuration code walks these arrays and writes address/value or address/mask/value triples into hardware registers. The programmed values persist in MAC, BB, AGC, and RF hardware state until reconfigured or reset.

## Dependencies And Integration Points
The table depends on `table.h` length constants and on register meanings from `reg.h`. It is consumed by PHY configuration routines such as baseband table loading, RF path setup, power-group programming, and antenna topology changes.

## Risks And Test Signals
Risks are length mismatches, malformed triplets, wrong table order, chip-cut mismatch, and values that conflict with later dynamic management. Signals are successful PHY init, RF calibration, expected sensitivity, stable throughput, correct 1T1R/1T2R operation, and no out-of-bounds table iteration under kernel sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.h

## Purpose
`table.h` declares the RTL8192SE hardware table arrays and their expected element counts. It is the compile-time contract between static table data and PHY/RF table loaders.

## APIs, Types, And Constants
The header defines array-length macros for PHY, RF, MAC, and AGC tables and declares each table as `extern u32[]`. Some arrays are register/value pairs, while antenna-conversion and power-group arrays use triplets interpreted by PHY code.

## Control Flow, State, And Persistence
The file has no runtime control flow or local state. Its constants determine how many `u32` entries loader loops consume. The resulting side effects are persistent hardware register programming by the files that include this header.

## Dependencies And Integration Points
It depends on `<linux/types.h>` for `u32`. It integrates `table.c` with RTL8192SE PHY setup and RF initialization code. `reg.h` provides the symbolic meanings of most addresses embedded in the arrays.

## Risks And Test Signals
The main risk is a length/data mismatch causing skipped writes or out-of-bounds reads during hardware init. Other risks include stale declarations after table edits. Signals are clean builds, successful table load, stable RF initialization, and absence of memory/debug warnings during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.c

## Purpose
`trx.c` translates between mac80211 packets/status and RTL8192SE PCI DMA descriptors. It fills TX and command descriptors, parses RX descriptors and PHY status, exposes descriptor get/set helpers, and triggers hardware queue polling.

## APIs, Types, And Functions
Public functions are `rtl92se_tx_fill_desc`, `rtl92se_tx_fill_cmddesc`, `rtl92se_rx_query_desc`, `rtl92se_set_desc`, `rtl92se_get_desc`, and `rtl92se_tx_polling`. Internal helpers map skb queues to firmware queues and convert CCK/OFDM PHY status into `rtl_stats` and `ieee80211_rx_status` signal fields.

## Control Flow, State, And Persistence
TX fill maps the skb for DMA, computes rate/protection/security/bandwidth/fragment fields, writes descriptor words, and leaves ownership to later core code. Command descriptors set ownership directly for firmware download and H2C packets. RX query extracts length, errors, decryption, rate, AMPDU, timestamp, bandwidth, and PHY metrics, with special handling for robust management frames. Descriptor ownership and buffer addresses are persistent ring state shared with hardware.

## Dependencies And Integration Points
The file depends on rtlwifi PCI/core helpers, descriptor bit accessors from `def.h`, rates from `reg.h`/`def.h`, mac80211 frame helpers, DMA mapping APIs, and stats/PHY processing helpers.

## Risks And Test Signals
Risks include DMA mapping leaks, wrong queue selection, endian/bitfield errors, false decrypted flags, RX signal miscalculation, and descriptor ownership races. Signals are traffic under all AC queues, EAPOL success, AMPDU operation, hardware crypto, firmware command delivery, and RX status correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.h

## Purpose
`trx.h` exposes the RTL8192SE transmit/receive descriptor operations used by the rtlwifi PCI core and the HAL ops table in `sw.c`.

## APIs, Types, And Functions
The header declares TX data descriptor fill, TX command descriptor fill, RX descriptor query, generic descriptor set/get, and TX polling functions. Parameters connect mac80211 (`ieee80211_hw`, `ieee80211_hdr`, `ieee80211_tx_info`, `ieee80211_sta`, `ieee80211_rx_status`), rtlwifi (`rtl_stats`, `rtl_tcb_desc`), skb data, and raw descriptor buffers.

## Control Flow, State, And Persistence
The header has no state. It defines the function-level contract for manipulating PCI descriptor rings, DMA buffer addresses, ownership bits, RX status extraction, and hardware queue polling.

## Dependencies And Integration Points
It is included by `sw.c` for HAL registration and by TX/RX paths in the rtlwifi PCI core. It depends on surrounding includes for mac80211, skb, and rtlwifi types.

## Risks And Test Signals
Risks are prototype drift, incorrect caller assumptions about descriptor ownership, and mismatches between command/data descriptor handling. Signals are clean builds, successful HAL ops binding, TX queue progress, RX delivery, firmware command submission, and no WARN_ONCE paths for unsupported descriptor names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/Makefile

## Purpose
The `rtl8723ae/Makefile` defines the kernel object composition for the Realtek RTL8723AE PCI wireless subdriver.

## APIs, Types, And Data
It builds `rtl8723ae.o` from `dm.o`, `fw.o`, `hal_btc.o`, `hal_bt_coexist.o`, `hw.o`, `led.o`, `phy.o`, `pwrseq.o`, `rf.o`, `sw.o`, `table.o`, and `trx.o`. The final object is linked when `CONFIG_RTL8723AE` is enabled.

## Control Flow, State, And Persistence
There is no runtime control flow. Build-time composition determines which code participates in the module and therefore which init paths, firmware commands, Bluetooth coexistence logic, and descriptor handlers are present at runtime.

## Dependencies And Integration Points
It integrates with the kernel Kbuild system and the parent rtlwifi driver directory. The object list must remain aligned with source-file symbols referenced by `sw.c` HAL ops and by cross-file includes.

## Risks And Test Signals
Risks include missing objects causing link errors, stale object names after file renames, or feature code compiled out unintentionally. Signals are successful kernel/module builds for `CONFIG_RTL8723AE=m/y`, no unresolved symbols, and a module containing the expected firmware, DM, BT coexistence, PHY/RF, HW, LED, table, and TRX logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/btc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/btc.h

## Purpose
`btc.h` provides a small RTL8723AE Bluetooth coexistence support definition shared by coexistence implementation files.

## APIs, Types, And Data
It includes rtlwifi base definitions and `hal_bt_coexist.h`, then defines `struct bt_coexist_c2h_info` with `no_parse_c2h` and `has_c2h` flags. These flags describe firmware-to-host coexistence event availability/parsing state.

## Control Flow, State, And Persistence
The header has no executable flow. The struct is transient driver state for C2H event handling; it reflects firmware notifications rather than persistent storage. Hardware/FW state changes are performed by the coexistence implementation through H2C commands and register writes.

## Dependencies And Integration Points
It is included by `hal_btc.h`, tying low-level C2H bookkeeping to the larger BT coexistence state-machine and policy definitions. It depends on rtlwifi/mac80211 type visibility through `../wifi.h`.

## Risks And Test Signals
Risks are minimal but include stale fields if C2H parsing changes, or circular include assumptions. Signals are clean builds, BT info C2H processing, coexistence periodical callbacks, and no lost BT status updates during Wi-Fi/BT activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/btc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/def.h

## Purpose
`def.h` contains RTL8723AE chip identity macros, RF/power enums, descriptor queue/rate constants, PHY status layout, and H2C command description types.

## APIs, Types, And Constants
Important macros extract chip version fields (`GET_CVID_*`, `IS_8723_SERIES`, cut/vendor/RF type tests), define queue selectors (`QSLT_*`), and enumerate RTL8723E descriptor rates from CCK through MCS32. Enums cover RF operation, RF power state, power-save mode and policy, PCI interface selection, queue selection, and rates. Structs describe CCK PHY status and generic H2C command metadata.

## Control Flow, State, And Persistence
There is no runtime flow. Constants steer later control flow in firmware commands, RF setup, TRX descriptor packing, and chip-cut conditional logic. Incorrect definitions become persistent hardware behavior through register/descriptor programming.

## Dependencies And Integration Points
The header is used across RTL8723AE DM, FW, PHY, RF, HW, and TRX code. It integrates with mac80211 queueing/rate concepts, firmware H2C command paths, and chip version values from hardware/EFUSE reads.

## Risks And Test Signals
Risks include wrong chip-cut detection, rate-code mismatch, queue selector mistakes, or PHY status layout drift. Signals are correct probe classification, association at legacy and HT rates, queue QoS behavior, firmware command construction, and RX signal parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.c

## Purpose
`dm.c` implements RTL8723AE dynamic management: DIG initial gain, false-alarm accounting, CCK packet-detection thresholds, dynamic TX power, EDCA turbo, RF/baseband power saving, rate-adaptive mask refresh, and BT coexistence watchdog entry.

## APIs, Types, And Functions
Public functions include `rtl8723e_dm_init`, `rtl8723e_dm_watchdog`, `rtl8723e_dm_write_dig`, `rtl8723e_dm_check_txpower_tracking`, `rtl8723e_dm_init_rate_adaptive_mask`, `rtl8723e_dm_rf_saving`, and `rtl8723e_dm_bt_coexist`. Internal helpers compute minimum RSSI, read/reset false alarm counters, adjust gain by RSSI/FA, update CCK thresholds, EDCA values, RF save/normal register sets, and rate masks.

## Control Flow, State, And Persistence
`rtl8723e_dm_init` seeds driver-managed DM tables. `rtl8723e_dm_watchdog` runs while RF is on, firmware is awake, and no RF change is active, under `rf_ps_lock`. It updates DIG, counters, power saving, TX power, rate masks, BT coexistence, and EDCA. State lives in `rtlpriv->dm`, `dm_digtable`, `dm_pstable`, `ra`, `falsealm_cnt`, `btcoexist`, and static cached BB registers. Writes persist in BB/MAC/RF registers.

## Dependencies And Integration Points
It depends on rtlwifi core, PCI, PHY, firmware, common RTL8723 DM helpers, BT coexistence, mac80211 link state, stats counters, and hardware register definitions.

## Risks And Test Signals
Risks are unstable gain loops, stale static state across devices, missed lock boundaries, bad EDCA overrides, incorrect near-field TX power, and BT coexistence interference. Signals include stable throughput, roaming/scan behavior, false alarm trends, rate-mask updates, low-power transitions, and concurrent Wi-Fi/BT performance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.h

## Purpose
`dm.h` defines RTL8723AE dynamic-management thresholds, enums, helper macros, and public DM entry points.

## APIs, Types, And Constants
It defines DIG disable flags, OFDM/CCK table sizes, bandwidth switch thresholds, false-alarm thresholds, rate-adaptive states, TX high-power levels, DM ownership modes, near-field TX-power thresholds, and BT RSSI state masks. `struct swat_t` tracks software antenna-switch attempts. Enums describe DIG operations, 1R CCA, RF save/normal state, and software antenna choices. `GET_UNDECORATED_AVERAGE_RSSI` abstracts station vs adhoc RSSI source.

## Control Flow, State, And Persistence
The header has no runtime flow but its constants govern watchdog state transitions in `dm.c` and coexistence decisions. Public functions initialize and periodically update hardware state; those updates persist in BB/RF/MAC registers.

## Dependencies And Integration Points
It is included by RTL8723AE DM and BT coexistence code and depends on rtlwifi/mac80211 structures through surrounding includes. It shares state meanings with common RTL8723 DM helpers and `rtlpriv->dm`.

## Risks And Test Signals
Risks include threshold changes causing oscillation, mismatch with `dm.c` expectations, and RSSI macro misuse. Signals are clean builds, stable DIG values, appropriate TX power reduction near APs, correct rate-adaptive transitions, and no regressions in low-power RF saving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.c

## Purpose
`fw.c` implements RTL8723AE host-to-firmware command delivery and firmware-assisted power-save helpers, including reserved-page packet download and P2P power-save offload.

## APIs, Types, And Functions
Public functions are `rtl8723e_fill_h2c_cmd`, `rtl8723e_set_fw_pwrmode_cmd`, `rtl8723e_set_fw_rsvdpagepkt`, `rtl8723e_set_fw_joinbss_report_cmd`, and `rtl8723e_set_p2p_ps_offload_cmd`. Internals include mailbox-read checking, locked H2C box filling, CTWindow command setup, and a static 768-byte reserved-page template for beacon, PS-Poll, null data, and probe response pages.

## Control Flow, State, And Persistence
H2C command fill waits for exclusive `h2c_lock` ownership, selects the next firmware mailbox, polls until firmware has read it, writes normal/extended mailbox bytes for 1-5 byte commands, then advances the mailbox index. Reserved-page setup patches MAC/BSSID/AID fields, sends the template through `rtl_cmd_send_packet`, and tells firmware page locations. P2P offload writes NoA/CTWindow registers and sends a packed offload byte.

## Dependencies And Integration Points
The file depends on rtlwifi core/PCI, firmware common definitions, mac80211 P2P state, `rtl_cmd_send_packet`, register accessors, and H2C IDs. BT coexistence also uses the H2C helper heavily.

## Risks And Test Signals
Risks include mailbox races/timeouts, firmware-not-ready commands, static reserved-page corruption, skb allocation failure, and P2P NoA timing mistakes. Signals are firmware command completion, LPS/IPS behavior, reserved-page download success, P2P Notice-of-Absence operation, and BT coexistence H2C delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.h

## Purpose
`fw.h` defines RTL8723AE firmware image bounds, firmware-header detection, H2C command byte setters, and public firmware command APIs.

## APIs, Types, And Constants
It defines firmware size/start/end/page constants, polling delay, `IS_FW_HEADER_EXIST`, and `pagenum_128`. H2C setters encode power mode, smart PS, beacon pass time, join-BSS status, and reserved-page locations. Public declarations cover generic H2C fill, firmware power mode, reserved pages, join-BSS report, and P2P PS offload.

## Control Flow, State, And Persistence
The header has no control flow. Its macros directly write command bytes into caller-provided buffers, so they shape firmware-visible state. The declared functions in `fw.c` persist settings in firmware mailboxes, reserved packet pages, and P2P hardware registers.

## Dependencies And Integration Points
It integrates `fw.c`, DM/power-save paths, join status notifications, P2P handling, and BT coexistence H2C command submission. It depends on firmware IDs and shared RTL8723 common firmware definitions included by implementation files.

## Risks And Test Signals
Risks are command layout drift, wrong firmware size assumptions, and unsafe macro use with undersized buffers. Signals include clean builds, successful firmware readiness, power-save entry/exit, join report handling, reserved-page H2C acknowledgements, and P2P PS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.c

## Purpose
`hal_bt_coexist.c` provides shared RTL8723AE Wi-Fi/Bluetooth coexistence helpers: Wi-Fi state classification, RSSI hysteresis, AGC/backoff controls, FW balance commands, all-off wrappers, and state-change checks.

## APIs, Types, And Functions
Public functions include `_rtl8723_dm_bt_check_wifi_state`, RSSI state helpers, `rtl8723e_dm_bt_get_rx_ss`, `rtl8723e_dm_bt_balance`, AGC table and BB backoff controls, all-off wrappers, AP aggregation rejection stub, coexistence state-change check, and Wi-Fi uplink detection.

## Control Flow, State, And Persistence
Wi-Fi state updates set bits in `rtlpriv->btcoexist.cstate` for idle/uplink/downlink, legacy/HT20/HT40, RSSI level, and BT3.0 operation. RSSI helpers use hysteresis against prior BT RSSI states. Mechanism functions write AGC table/RF registers, BB backoff registers, and H2C command `0xc` for time balance. All-off wrappers avoid duplicate work using `fw/sw/hw_coexist_all_off` flags. State persists in `rtlpriv->btcoexist`, baseband/RF registers, and firmware coexistence settings.

## Dependencies And Integration Points
It depends on `dm.h`, `fw.h`, `phy.h`, `reg.h`, `hal_btc.h`, rtlwifi PCI/core state, RSSI metrics, and H2C command submission. `hal_btc.c` calls these helpers to apply profile policies.

## Risks And Test Signals
Risks include stale state bits, hysteresis bugs, duplicate or missing all-off transitions, register value regressions, and an empty aggregation-rejection stub. Signals are BT coexistence debug state transitions, stable Wi-Fi RSSI/throughput with BT traffic, and correct all-off behavior before low power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.h

## Purpose
`hal_bt_coexist.h` defines RTL8723AE coexistence register addresses, state bitmaps, RSSI states, profile/mechanism IDs, BT info bits, and helper prototypes.

## APIs, Types, And Constants
Key constants include high/low priority BT counter registers, RSSI thresholds/tolerance, Wi-Fi/BT/profile state bits, BT counter levels, AGC/backoff/FW NAV toggles, coexistence mechanism IDs, debug profile IDs, and BT info byte bits for FTP/A2DP/HID/SCO/ACL/inquiry/connection. Function declarations expose all shared helper and all-off operations.

## Control Flow, State, And Persistence
The header has no flow. Its bit definitions are the state language stored in `rtlpriv->btcoexist.cstate` and `cstate_h`; its mechanism IDs classify the selected profile action. Helper prototypes lead to persistent H2C, MAC, BB, and RF changes in implementation files.

## Dependencies And Integration Points
It includes `../wifi.h` and is shared by `btc.h`, `hal_btc.h`, `hal_bt_coexist.c`, `hal_btc.c`, and DM code. It bridges firmware BT info parsing and hardware coexistence programming.

## Risks And Test Signals
Risks are bit collisions, wrong profile classification, threshold tuning regressions, and prototype drift. Signals are clean builds, coherent debug bitmaps, BT profile detection, correct AGC/PTA/TDMA policy selection, and Wi-Fi/BT coexistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.c

## Purpose
`hal_btc.c` is the RTL8723AE Bluetooth coexistence policy engine. It queries firmware BT info, monitors BT hardware counters, classifies BT profiles, builds `btdm_8723` coexistence policies, and applies them through firmware commands, PTA tables, BB/RF settings, and software rate/AGC tweaks.

## APIs, Types, And Functions
Public functions include `rtl8723e_dm_bt_turn_off_bt_coexist_before_enter_lps`, media-status notification, all-off implementations, `rtl8723e_dm_bt_set_bt_dm`, `rtl8723e_dm_bt_coexist_8723`, and `rtl_8723e_c2h_command_handle`. Internal helpers set H2C commands (`0x11`, `0x14`, `0x15`, `0x21`-`0x26`, `0x29`, `0x33`, `0x38`, `0x3a`), PTA table registers, RF LPF, DAC swing, retry index, WLAN_ACT timing, and profile-specific PS-TDMA bytes.

## Control Flow, State, And Persistence
The watchdog path queries BT information, reads high/low priority counters, detects BT enable/disable, chooses 2-antenna logic, handles inquiry/page windows, then selects common, HID/SCO/eSCO, or FTP/A2DP policy. `rtl8723e_dm_bt_set_bt_dm` skips unchanged policies, handles hold-for-BT-operation, applies all-off or ordered mechanism changes, delays for DAC swing, and updates BT power. State lives in static `hal_coex_8723` plus `rtlpriv->btcoexist`; writes persist in firmware and hardware.

## Dependencies And Integration Points
It depends on `hal_btc.h`, `hal_bt_coexist.h`, `fw.h`, `phy.h`, `reg.h`, rtlwifi/mac80211 state, common PHY helpers, C2H registers, and optional `btc_ops->btc_periodical`.

## Risks And Test Signals
Risks include static global multi-device leakage, C2H length/ownership errors, policy oscillation, ordering bugs between TDMA/HID/PS-TDMA, unimplemented 1-antenna path, and poor BT/Wi-Fi fairness. Signals are BT info C2H parsing, counter changes, profile-specific debug actions, LPS all-off, and throughput/latency under A2DP, HID, SCO, PAN/FTP, inquiry, and idle scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.h

## Purpose
`hal_btc.h` defines RTL8723AE Bluetooth coexistence policy constants, enums, C2H event metadata, and public policy-engine entry points.

## APIs, Types, And Constants
It defines BT TX/RX counter thresholds and levels, queue/power/coex toggles, TDMA/PTA/rate-adaptive/RF-corner modes, C2H close markers, BT traffic/profile/spec/state enums, `struct c2h_evt_hdr`, and C2H event IDs including `C2H_V0_BT_INFO`. It declares all-off routines, main coexistence execution, policy application, C2H handling, media notification, and LPS pre-entry coexistence shutdown.

## Control Flow, State, And Persistence
The header has no flow but encodes the state vocabulary for `hal_btc.c`. Thresholds classify BT counter totals; event IDs control C2H dispatch; TDMA/PTA constants become H2C command bits. Resulting policies persist in firmware mailboxes, PTA registers, and RF/BB state.

## Dependencies And Integration Points
It includes `../wifi.h`, `btc.h`, and `hal_bt_coexist.h`. It is used by DM, firmware/coexistence code, and C2H handling to coordinate Wi-Fi link state with BT profile/counter information.

## Risks And Test Signals
Risks include threshold changes that alter policy selection, mismatched C2H IDs, enum value drift, and prototype mismatches. Signals are clean builds, correct C2H BT info dispatch, expected counter-level classification, media-status H2C commands, and stable coexistence profile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.h -->
