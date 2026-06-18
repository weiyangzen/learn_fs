# Research: subset-b-004938

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.h

## Purpose
This header is the table export contract for the RTL8851B RTW89 chip support. It does not define data itself; it exposes board/chip parameter tables produced by companion table sources to the 8851B core and bus-specific modules.

## Important APIs, Types, and Data
- Includes `core.h` for RTW89 table and RFE types.
- Exports `rtw89_8851b_phy_bb_table`, `rtw89_8851b_phy_bb_gain_table`, `rtw89_8851b_phy_radioa_table`, and `rtw89_8851b_phy_nctl_table` as `struct rtw89_phy_table` instances used during PHY/RF initialization.
- Exports `rtw89_8851b_trk_cfg` as `struct rtw89_txpwr_track_cfg` for thermal/TSSI tracking compensation.
- Exports `rtw89_8851b_dflt_parms` and `rtw89_8851b_rfe_parms_conf[]` for radio front-end parameter selection.

## Control Flow and Integration
The header has no runtime control flow. Its declarations are consumed by 8851B chip metadata, most likely in `rtw8851b.c` and bus wrappers such as PCI/USB modules. Initialization code passes these table addresses into generic RTW89 parser helpers, which then write BB, RF, gain, NCTL, power-tracking, and RFE values to hardware.

## State and Persistence
No state is stored here. The declared objects are `const`, so persistence is compile-time data in the kernel module image. Runtime state is created by consumers after parsing tables into hardware registers and `rtw89_dev` fields.

## Dependencies
This file depends on `core.h` for the `rtw89_phy_table`, `rtw89_txpwr_track_cfg`, `rtw89_rfe_parms`, and `rtw89_rfe_parms_conf` type definitions. It also depends on matching definitions in table implementation files; missing or renamed definitions would produce link failures for any 8851B module that references them.

## Risks
- The header is only declarations, so the main risk is drift between declarations and generated/handwritten table definitions.
- RFE and calibration tables are hardware-sensitive; incorrect table definitions behind these declarations can cause bring-up failures, poor RF performance, or regulatory power issues even though this header compiles cleanly.
- Because declarations are shared across bus variants, changing exported names has broad build impact.

## Test Signals
- Build/link coverage for RTL8851B modules verifies symbol availability.
- Device probe logs and RTW89 debug categories for table parsing, RFK, TSSI, and TX power verify that consumers can load and apply the tables.
- Hardware smoke tests should include association, scan, TX power, and thermal tracking on known 8851B RFE variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851be.c

## Purpose
This file is the PCIe bus glue for the Realtek RTL8851BE 802.11ax chipset. It binds the generic RTW89 PCI framework to the 8851B chip description, declares the PCI device ID, and registers a Linux `pci_driver`.

## Important APIs, Types, and Data
- `rtw8851b_pci_info` is a `struct rtw89_pci_info` describing AX-generation PCI behavior: descriptor truncation modes, RXBD mode, multi-tag mode, burst sizes, DMA idle/active intervals, DMA stop/busy registers, interrupt callbacks, RPP format size, DMA channel mask, and BD RAM table.
- `rtw89_8851be_info` is a `struct rtw89_driver_info` that points `.chip` to `rtw8851b_chip_info` and attaches the PCI info under `.bus.pci`.
- `rtw89_8851be_id_table` matches Realtek vendor ID with device ID `0xb851` and stores a pointer to `rtw89_8851be_info` in `driver_data`.
- `rtw89_8851be_driver` wires Linux PCI callbacks to generic RTW89 PCI entry points: `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

## Control Flow
At module load, `module_pci_driver()` registers `rtw89_8851be_driver`. When the PCI core matches device `10ec:b851`, `rtw89_pci_probe` receives the ID table entry, extracts `rtw89_8851be_info`, and initializes the common RTW89 device using `rtw8851b_chip_info` plus the PCI transport parameters in `rtw8851b_pci_info`. Removal, power management, and PCI error recovery are delegated to shared RTW89 PCI/core routines.

## State and Persistence
This wrapper stores only immutable module metadata and static config structures. Runtime state is allocated by the generic PCI probe path and RTW89 core. Persistent behavior includes PCI device binding through `MODULE_DEVICE_TABLE(pci, ...)`, which allows module auto-loading by modalias.

## Dependencies and Integration Points
- Linux PCI and module subsystems: `<linux/pci.h>`, `<linux/module.h>`.
- RTW89 PCI framework in `pci.h`, register definitions in `reg.h`, and chip-level RTL8851B metadata in `rtw8851b.h`.
- Shared PCI helper callbacks provide DMA setup, LTR, descriptor address filling, RPP parsing, interrupt mask programming, and interrupt recognition.
- Integrates with kernel PM through `rtw89_pm_ops` and PCI AER/error handling through `rtw89_pci_err_handler`.

## Risks
- Incorrect DMA channel masks, burst sizes, stop/busy registers, or tag settings can cause hangs, missed interrupts, or descriptor corruption.
- The ID table only binds `0xb851`; additional subsystem-specific IDs would not probe unless covered by this generic ID.
- `ssid_quirks = NULL` means no board-specific PCI quirks are applied here.

## Test Signals
- Kernel build with `CONFIG_RTW89_8851BE` or equivalent confirms API compatibility.
- `modinfo` should expose the PCI alias for `10ec:b851`.
- Runtime probe should create an RTW89 wireless PHY without DMA timeout, interrupt, or firmware download errors.
- Suspend/resume and PCI error-recovery tests exercise the `.driver.pm` and `.err_handler` paths delegated by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851be.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851bu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851bu.c

## Purpose
This file is the USB bus glue for RTL8851BU-family Realtek 802.11ax adapters. It binds the generic RTW89 USB transport to the 8851B chip descriptor and declares USB IDs for Realtek and several retail adapters.

## Important APIs, Types, and Data
- `rtw8851b_usb_info` is a `struct rtw89_usb_info` containing register addresses for USB host request, WLAN, HCI enable, USB3 NPI config, and endpoint registers.
- The same structure sets `rx_agg_alignment = 8` and maps RTW89 DMA queues to bulk-out endpoint IDs: ACH0/1/2/3 to endpoints 3/4/5/6, management/high/H2C queues to endpoints 0/1/2.
- `rtw89_8851bu_info` points `.chip` to `rtw8851b_chip_info` and attaches the USB info under `.bus.usb`.
- `rtw_8851bu_id_table` matches Realtek IDs `0x0bda:0xb831` and `0x0bda:0xb851`, plus D-Link AX9U rev. A1, TP-Link Archer TX10UB Nano, and Edimax EW-7611UXB IDs using vendor-specific interface class/subclass/protocol `0xff`.
- `rtw_8851bu_driver` delegates `.probe` and `.disconnect` to `rtw89_usb_probe` and `rtw89_usb_disconnect`.

## Control Flow
`module_usb_driver()` registers the USB driver. When a matching interface appears, the USB core calls `rtw89_usb_probe`; that generic routine receives `rtw89_8851bu_info` through `driver_info`, then initializes RTW89 core state with 8851B chip operations and the USB endpoint/register map. Disconnect is handled by the common USB teardown routine.

## State and Persistence
This file has no mutable driver state. Persistent binding comes from `MODULE_DEVICE_TABLE(usb, ...)`, which enables modalias-based auto-loading. Runtime transport queues, URBs, firmware state, and hardware state are maintained by RTW89 USB/core layers.

## Dependencies and Integration Points
- Linux USB and module subsystems: `<linux/usb.h>`, `<linux/module.h>`.
- RTL8851B chip metadata in `rtw8851b.h`, register definitions in `reg.h`, and generic RTW89 USB helpers in `usb.h`.
- The endpoint map is an integration contract with USB descriptors and firmware/HCI queue routing.

## Risks
- Bulk endpoint mapping is hardware-contract data; a wrong queue-to-endpoint ID can break TX, management frames, or H2C commands.
- Device IDs use vendor-specific interface matching. Composite devices with unexpected interface descriptors could fail to bind.
- USB-specific power management is not declared here; behavior depends on generic RTW89 USB support.

## Test Signals
- Kernel build confirms `struct rtw89_usb_info` and generic USB callbacks match this wrapper.
- `modinfo` should list USB aliases for the declared adapters.
- Runtime tests should verify firmware download, scan, association, data TX/RX, disconnect cleanup, and operation through USB2/USB3 ports where applicable.
- Queue-specific traffic, especially management/H2C and multiple AC queues, is a useful endpoint-map validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851bu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.c

## Purpose
This file is the main RTL8852A chip implementation for the RTW89 driver. It defines chip-level capabilities, power sequences, HCI queue and DLE layouts for PCIe/USB, EFUSE/PHYCAP parsing, channel programming, BB reset and PMAC helpers, TX power setup, Bluetooth coexistence hooks, PPDU reporting, DIG/EDCCA/IMR register maps, and the exported `rtw8852a_chip_info`.

## Important APIs, Types, and Data
- Firmware identity is defined by `RTW8852A_FW_BASENAME`, `RTW8852A_FW_FORMAT_MAX`, `RTW8852A_MODULE_FIRMWARE`, and `MODULE_FIRMWARE`.
- HCI resource tables include `rtw8852a_hfc_param_ini_pcie`, `rtw8852a_hfc_param_ini_usb`, `rtw8852a_dle_mem_pcie`, and `rtw8852a_dle_mem_usb`.
- Power sequencing is encoded in `rtw8852a_pwron`, `rtw8852a_pwroff`, and the pointer arrays `pwr_on_seq_8852a` and `pwr_off_seq_8852a`.
- Register maps cover H2C/C2H registers, WoW wake reason registers, page registers, DCFO/NHM/IMR/RRSR/RFKILL/DIG/EDCCA settings.
- `rtw8852a_read_efuse()` parses country code, MAC address by HCI type, RFE type, XTAL cap, and TSSI EFUSE offsets into `rtwdev->efuse` and `rtwdev->tssi`.
- `rtw8852a_read_phycap()` parses TSSI trim, thermal trim, and PA-bias trim from PHY capability data into `rtwdev->tssi` and `rtwdev->pwr_trim`.
- Channel operations are provided by `rtw8852a_set_channel()`, `rtw8852a_set_channel_mac()`, `rtw8852a_set_channel_bb()`, `rtw8852a_ctrl_ch()`, and `rtw8852a_ctrl_bw()`.
- RFK integration callbacks call into `rtw8852a_rfk.c`: `rtw8852a_rfk_init()`, `rtw8852a_rfk_channel()`, `rtw8852a_rfk_band_changed()`, `rtw8852a_rfk_scan()`, and `rtw8852a_rfk_track()`.
- Exported PMAC/test helpers include `rtw8852a_bb_set_plcp_tx()`, `rtw8852a_bb_set_pmac_tx()`, `rtw8852a_bb_set_pmac_pkt_tx()`, `rtw8852a_bb_set_power()`, `rtw8852a_bb_cfg_tx_path()`, and `rtw8852a_bb_tx_mode_switch()`.
- Coexistence hooks include RFE derivation, WL priority masks, TX power control, BT RSSI conversion, BT counter refresh, WL standby, and WL RX gain adjustment.
- `rtw8852a_chip_ops` binds all chip callbacks into the RTW89 core, and `rtw8852a_chip_info` exports the full chip descriptor with capabilities and table pointers.

## Control Flow
Probe code in bus-specific modules supplies `rtw8852a_chip_info` to the RTW89 core. The core uses `.ops` to power the chip, parse EFUSE and PHY capability maps, initialize BB/RF, configure channels, run RF calibration, set TX power, parse RX status, and coordinate coexistence.

Channel changes have a staged flow. `rtw8852a_set_channel_help(..., enter=true)` stops scheduled TX, disables PPDU status, DFS, TSSI continuous tracking, and ADC, then disables BB reset. `rtw8852a_set_channel()` programs MAC bandwidth/subcarrier/rate-check state and BB/RF channel and bandwidth registers, handles CCK/SCO/band-edge/TXFIR settings, spur elimination, RXCCA, primary channel index, and BB reset. `rtw8852a_set_channel_help(..., enter=false)` restores PPDU status, ADC, DFS, TSSI, BB reset, and scheduled TX.

RF calibration is orchestrated by chip callbacks. Initial RFK runs RCK, DACK, and RX DCK. Per-channel RFK notifies coexistence, runs RX DCK, IQK, TSSI, and DPK, with BT time preservation around TSSI/DPK, then clears the coexistence RFK notification. Band-change and scan callbacks update TSSI behavior, while periodic tracking runs DPK and TSSI tracking.

TX power setup calls generic RTW89 PHY limit/by-rate/offset/RU helpers and initializes MAC TX power unit registers. The PMAC helpers program packet/continuous test TX by writing PLCP and PMAC registers, selecting TX path, setting BB power, and toggling PMAC TX enables.

Coexistence flow derives antenna topology from RFE type, initializes PTA, priority masks, RF grant debug, TRX mask tables, break table, and BT counters. Runtime coexistence callbacks adjust WL priority, forced TX power, BT RSSI normalization, BT counter snapshots, S1 standby, non-BTG pre-AGC, and path-B LNA2 behavior.

## State and Persistence
This file persists immutable chip description data in `rtw8852a_chip_info`. Runtime state is stored in shared `rtw89_dev` substructures:
- `rtwdev->efuse` receives country code, MAC address, RFE type, and XTAL cap.
- `rtwdev->tssi` receives EFUSE TSSI offsets, trim data, thermal values, base thermal, extra offset, and tracking flags.
- `rtwdev->pwr_trim` receives PHY capability thermal and PA-bias trim values and presence flags.
- `rtwdev->fem` is derived from `efuse.rfe_type` to mark external PA/LNA combinations.
- `rtwdev->btc` stores coexistence antenna type, BTG position, module metadata, counters, and WL LNA2 state.
Most hardware persistence is register state established by table parsers and direct register/RF writes.

## Dependencies and Integration Points
- Includes RTW89 core modules: `coex.h`, `fw.h`, `mac.h`, `phy.h`, `reg.h`, `txrx.h`, `rtw8852a.h`, `rtw8852a_rfk.h`, and `rtw8852a_table.h`.
- Relies on table objects such as `rtw89_8852a_phy_bb_table`, radio tables, NCTL table, default RFE parameters, and tracking configuration.
- Calls many generic RTW89 helpers for MAC power/queue control, TX power, firmware H2C, RX descriptor parsing, RF register access, BTC notifications, and PHY table parsing.
- Exports `rtw8852a_chip_info` for bus modules such as PCI/USB wrappers.

## Risks
- Channel and bandwidth logic writes many direct RF/BB registers; ordering mistakes can cause deaf receive, invalid CCK behavior, spurs, or broken DBCC path selection.
- EFUSE and PHY capability parsing uses fixed offsets and HCI-specific MAC address layouts; map layout drift can produce wrong identity, trims, or front-end behavior.
- Coexistence antenna derivation from `rfe_type` is heuristic; wrong RFE data can select shared versus dedicated antenna behavior incorrectly.
- RFK callback ordering is performance-sensitive and coordinated with BT notifications; missing notifications can hurt Bluetooth coexistence.
- Several capability flags are hard-coded in `rtw8852a_chip_info`; incorrect feature flags can expose unsupported kernel/mac80211 behavior.

## Test Signals
- Build/link confirms all chip ops and table symbols match the RTW89 core.
- Firmware load should request `rtw89/rtw8852a_fw` with supported format max 1.
- Probe logs should show successful EFUSE, PHYCAP, BB/RF table parsing, DLE/HFC setup, and power sequence completion.
- Channel-switch tests across 2.4 GHz and 5 GHz, 20/40/80 MHz, and DBCC/non-DBCC modes exercise MAC/BB/RF channel code.
- RFK debug logs for RCK/DACK/RX DCK/IQK/TSSI/DPK, association throughput, thermal tracking, scan behavior, and BT coexistence traffic are important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.h

## Purpose
This header declares RTL8852A-specific public types, EFUSE layouts, PMAC test structures, the exported chip descriptor, and BB/PMAC helper functions used across the RTW89 8852A implementation and RF calibration code.

## Important APIs, Types, and Data
- `RF_PATH_NUM_8852A` defines two RF paths.
- `enum rtw8852a_pmac_mode` enumerates PMAC modes: no test, packet TX, packet RX, and continuous TX.
- `struct rtw8852au_efuse` and `struct rtw8852ae_efuse` model USB and PCIe MAC-address placement in the EFUSE union.
- `struct rtw8852a_tssi_offset` stores CCK, 2 GHz MCS, and 5 GHz one-stream TSSI offsets.
- `struct rtw8852a_efuse` is a packed hardware EFUSE map containing TSSI offsets, channel plan, XTAL, IQK/LCK flag, regulatory/customer/RFE fields, thermal values, power indexes, and a USB/PCIe-specific MAC-address union.
- `struct rtw8852a_bb_pmac_info` describes PMAC TX enable, CCK flag, mode, packet count, period, TX time, and duty cycle.
- Declares `rtw8852a_chip_info` and BB helper functions for PLCP, PMAC packet TX, BB power, TX path, and TX mode switching.

## Control Flow and Integration
The header has no runtime control flow. Its EFUSE structures are used by `rtw8852a_read_efuse()` to cast the logical EFUSE map and copy fields into RTW89 runtime state. The PMAC structures and helpers are used by TSSI calibration in `rtw8852a_rfk.c` to generate controlled TX packets and by any manufacturing/test paths that need direct PMAC control. The exported chip descriptor is consumed by bus-specific probe modules.

## State and Persistence
The packed EFUSE structs describe persistent device-programmed data, not driver-owned mutable state. `rtw8852a_bb_pmac_info` is transient stack/config state for PMAC operations. `rtw8852a_chip_info` is immutable module-level metadata exported by `rtw8852a.c`.

## Dependencies
Includes `core.h` for RTW89 device, channel, PHY index, and TSSI constants. The packed layout depends on Linux integer and `ETH_ALEN` definitions reachable through core includes.

## Risks
- `struct rtw8852a_efuse` is a hardware ABI. Any offset, packing, or bitfield change can corrupt EFUSE interpretation.
- C bitfield ordering is compiler/ABI-sensitive; kernel conventions make this acceptable in-tree, but fields should not be casually reorganized.
- PMAC helper declarations are shared with RFK code; signature drift between header and implementation breaks build or calibration.

## Test Signals
- Compile coverage validates declarations against `rtw8852a.c` and `rtw8852a_rfk.c`.
- EFUSE parsing can be validated through debug output for MAC address, country code, RFE type, thermal, TSSI, and trim values.
- TSSI calibration smoke tests exercise PMAC helper declarations through `_tssi_pre_tx()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.c

## Purpose
This file implements RTL8852A RF calibration for RTW89. It covers RCK, DACK, IQK, RX DCK, DPK, TSSI setup/tracking, and scan-related TSSI handling. It is invoked by `rtw8852a.c` chip callbacks during hardware initialization, channel changes, periodic tracking, and scan transitions.

## Important APIs, Types, and Data
- Public functions declared in `rtw8852a_rfk.h`: `rtw8852a_rck`, `rtw8852a_dack`, `rtw8852a_iqk`, `rtw8852a_rx_dck`, `rtw8852a_dpk`, `rtw8852a_dpk_track`, `rtw8852a_tssi`, `rtw8852a_tssi_scan`, `rtw8852a_tssi_track`, and `rtw8852a_wifi_scan_notify`.
- `_kpath()` maps DBCC and PHY index to RF path mask (`RF_A`, `RF_B`, or `RF_AB`).
- Backup/restore helpers save BB and RF registers around calibration sequences.
- DACK helpers calibrate ADC/DAC DC offsets, save MSBK/BIAS/DADCK/ADDCK values into `rtwdev->dack`, and reload them into path-specific registers.
- IQK helpers execute LOK, TXK, RXK, narrowband/wideband calibration, coefficient reads, and result recording into `rtwdev->iqk`.
- RX DCK helpers run AFE/RFC RX DC calibration while pausing TSSI when required.
- DPK helpers implement KIP setup, loopback RXIQK, AGC search, gain-loss/PAS checks, result fill, reload/bypass logic, and thermal tracking with results in `rtwdev->dpk`.
- TSSI helpers program RF/BB TSSI tables, EFUSE-derived DE offsets, thermal meter tables, slope/gap/PAK settings, high-power tracking decisions, PMAC pre-TX, and scan average/default TXAGC behavior.

## Control Flow
Initialization from `rtw8852a_rfk_init()` in the chip file runs RCK on both paths, then DACK and RX DCK. Per-channel RFK from `rtw8852a_rfk_channel()` runs RX DCK, IQK, TSSI, and DPK in sequence with coexistence notifications around the overall operation and BT time preservation around longer TSSI/DPK stages.

Each public calibration function stops scheduled TX where needed, waits for the selected RF paths to leave TX mode using `_wait_rx_mode()`, sends BTC RFK start/stop notifications, runs the internal calibration routine, and resumes TX.

DACK flow uses `_afe_init()`, ADDCK reset/trigger/backup/reload, DACK S0/S1 trigger/poll/backup/reload, and updates `dack_done`, timeout flags, and count. IQK flow initializes IQK state once, captures channel/bandwidth info, backs up BB/RF registers, sets MAC/BB calibration tables, presets coefficient selection, runs LOK/TXK/RXK per path, restores KIP/AFE/BB/RF state, and records fail bits. RX DCK flow iterates selected paths, optionally pauses TSSI, toggles RF DCK registers, waits, and restores path state.

DPK flow checks whether external PA FEM configuration should bypass DPK. Otherwise it optionally reloads a previous channel result, backs up state, pauses TSSI, configures BB/AFE/KIP, runs RF setup, RX DCK, AGC/sync/gain-loss loops, fills DPD coefficients and power-scale factors, enables or disables DPK per path, restores state, and later adjusts PWSF in `_dpk_track()` based on thermal delta and TSSI offsets.

TSSI flow disables TSSI, programs RF and BB TSSI tables per path and band, writes thermal-meter and EFUSE-derived CCK/MCS DE values, enables TSSI, decides high-power tracking, and runs a short PMAC packet TX to capture default TXAGC offsets. Scan notifications temporarily alter TSSI averaging and save/restore default TXAGC offsets.

## State and Persistence
Calibration results persist in `rtw89_dev`:
- `rtwdev->dack` stores ADDCK, DADCK, BIAS, MSBK arrays, timeout flags, `dack_done`, and `dack_cnt`.
- `rtwdev->iqk` stores initialization flags, channel/bandwidth/path metadata, LOK/TX/RX fail flags, coefficient backups, IQK table indexes, fail count, and diagnostic enable flags.
- `rtwdev->dpk` stores current backup index per path, per-path/channel DPK records including band/channel/bandwidth, thermal-at-DPK, TXAGC, PWSF, gain scaling, path_ok, and tracking correlation/DC values.
- `rtwdev->tssi` stores EFUSE/trim data read by `rtw8852a.c`, base thermal, default TXAGC offset, extra thermal offset, and tracking-check flags.
- `rtwdev->is_tssi_mode[]` gates thermal reads, RX DCK pause/resume, DPK pause/resume, and TSSI tracking.

Most operations also leave calibrated coefficients in BB/RF registers. The DPK reload path can reuse stored per-channel DPK entries instead of recalibrating if reload is enabled and channel matches, although the public `rtw8852a_dpk()` currently sets reload disabled before `_dpk()`.

## Dependencies and Integration Points
- Includes `coex.h`, `debug.h`, `mac.h`, `phy.h`, `reg.h`, `rtw8852a.h`, `rtw8852a_rfk.h`, `rtw8852a_rfk_table.h`, and `rtw8852a_table.h`.
- Heavy use of generated RFK table parsers such as `rtw89_rfk_parser()` and `rtw89_rfk_parser_by_cond()`.
- Uses RTW89 MAC helpers to stop/resume scheduled TX and PHY/RF helpers to read/write registers.
- Uses BTC notifications (`rtw89_btc_ntfy_wl_rfk`, `rtw89_btc_phymap`, `rtw89_btc_path_phymap`) so Bluetooth coexistence can reserve or account for calibration time.
- TSSI uses PMAC helpers from `rtw8852a.c` and TX power limit helpers from generic PHY code.

## Risks
- Calibration code is register-order-sensitive; missing restore paths can leave MAC/BB/RF in calibration mode and break normal traffic.
- Timeout handling mostly records debug flags and continues, so hardware failures can degrade RF performance without failing probe.
- DBCC path selection and path-specific offsets are easy to regress because many registers are computed as `base + (path << 8)` or `base + (path << 13)`.
- TSSI and DPK interact through `is_tssi_mode`, default TXAGC offsets, and extra thermal offsets; incorrect scan or tracking transitions can skew transmit power.
- EFUSE-derived TSSI/trim values from `rtw8852a.c` are trusted here; invalid values can propagate into DE tables and power tracking.

## Test Signals
- RFK debug logs should show RCK, DACK, IQK, RX DCK, DPK, and TSSI start/finish messages without repeated timeout reports.
- Association and throughput across 2.4 GHz/5 GHz and 20/40/80 MHz validate IQK/TSSI/DPK programming.
- Thermal drift tests should show DPK/TSSI tracking updating PWSF and offsets without power instability.
- Scan tests should exercise `rtw8852a_wifi_scan_notify()` and verify TSSI average/default TXAGC restoration after scan end.
- Bluetooth coexistence tests during RFK should verify BTC notifications prevent severe BT/Wi-Fi disruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.h

## Purpose
This header declares the RTL8852A RF calibration interface used by the main chip file. It separates RFK implementation details in `rtw8852a_rfk.c` from chip operation wiring in `rtw8852a.c`.

## Important APIs, Types, and Data
- Declares one-shot/init calibration entry points: `rtw8852a_rck()`, `rtw8852a_dack()`, `rtw8852a_iqk()`, `rtw8852a_rx_dck()`, `rtw8852a_dpk()`, and `rtw8852a_tssi()`.
- Declares periodic or contextual calibration helpers: `rtw8852a_dpk_track()`, `rtw8852a_tssi_scan()`, `rtw8852a_tssi_track()`, and `rtw8852a_wifi_scan_notify()`.
- Function signatures consistently pass `struct rtw89_dev *`, PHY index, channel context index, and sometimes channel pointer or scan-start boolean.

## Control Flow and Integration
`rtw8852a.c` uses these declarations in chip callbacks:
- RFK init calls RCK, DACK, and RX DCK.
- Channel RFK calls RX DCK, IQK, TSSI, and DPK.
- Band changes call TSSI scan refresh.
- Scan notifications call Wi-Fi scan TSSI handling.
- Periodic tracking calls DPK and TSSI tracking.
The header itself has no control flow.

## State and Persistence
No state is declared in the header. Implementations mutate `rtw89_dev` calibration substructures and hardware registers. The API shape makes channel-context and PHY selection explicit for multi-channel/DBCC-aware calibration.

## Dependencies
Includes `core.h` for `struct rtw89_dev`, `enum rtw89_phy_idx`, `enum rtw89_chanctx_idx`, and `struct rtw89_chan`.

## Risks
- These prototypes are a narrow contract between chip operations and RFK internals; signature changes require coordinated updates in `rtw8852a.c`.
- Missing declarations for newly added RFK functions would push callers toward local externs or reduce compile coverage.
- The API exposes calibration at a coarse level, so ordering guarantees live in callers and implementation rather than the header.

## Test Signals
- Build coverage validates all declared functions against `rtw8852a_rfk.c`.
- Runtime RFK logs from chip callbacks confirm the declared entry points are reached during init, channel change, scan, and tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_rfk.h -->
