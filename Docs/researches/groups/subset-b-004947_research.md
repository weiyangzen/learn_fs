# Research Report: subset-b-004947

This grouped report covers the requested Realtek RTW89 8852A bus/table declarations and RTW8852B chip, common PHY/MAC, and RF calibration sources. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.h

Purpose: This header is the table declaration boundary for the RTL8852A variant of the RTW89 driver. It exposes immutable PHY/RF/NCTL configuration tables, transmit-power tracking configuration, and default RFE parameters to the 8852A chip implementation while keeping the table definitions in separate generated or vendor-derived table translation units.

Important APIs, types, and data: The exported symbols are `rtw89_8852a_phy_bb_table`, `rtw89_8852a_phy_radioa_table`, `rtw89_8852a_phy_radiob_table`, `rtw89_8852a_phy_nctl_table`, `rtw89_8852a_trk_cfg`, and `rtw89_8852a_dflt_parms`. The types come from `core.h`: `struct rtw89_phy_table` for baseband/radio/NCTL register sequences, `struct rtw89_txpwr_track_cfg` for thermal power tracking swing tables, and `struct rtw89_rfe_parms` for front-end parameter defaults.

Control flow: There is no executable flow in this file. Runtime behavior is indirect: the 8852A chip info points at these symbols, and common PHY setup code later parses the `rtw89_phy_table` descriptors to program BB, RF path A/B, and NCTL registers. The tracking and RFE structures are read by TX power and RF front-end logic when selecting temperature compensation and regulatory/front-end limits.

State and persistence: The declarations refer to const data. The header creates no driver state, but parsing the declared tables persists hardware register state until reset, power transition, channel reconfiguration, or a later table overrides it. Any consumer assumes the table objects have static lifetime.

Dependencies and integration points: Depends only on `core.h` and the matching 8852A table C files. It is normally consumed by `rtw8852a.c` and bus glue such as `rtw8852ae.c`/`rtw8852au.c` through the 8852A chip info. It also sits in the broader RTW89 table-parser contract shared with `phy.c`.

Risks: This is a small ABI header, so the main risk is declaration/definition drift. A missing or renamed table breaks the module link; a semantically wrong table with the same type compiles but can misprogram RF paths, baseband, NCTL, or TX power tracking. The dual-radio declarations must remain path-specific because later chip info distinguishes radio A and radio B tables.

Test signals: Build and module link validate symbol names and types. Runtime validation comes from successful RTL8852A probe on PCIe and USB variants, firmware load, PHY table parsing without register-write errors, 2.4 GHz and 5 GHz association, channel changes, thermal/TX power tracking debug output, and absence of RF/BB initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ae.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ae.c

Purpose: This file is the PCIe bus glue module for RTL8852AE. It binds Realtek PCI device IDs to the generic RTW89 PCI probe/remove paths and supplies the 8852A-specific PCI host-controller configuration used by the common bus layer.

Important APIs, types, and data: `rtw8852a_pci_info` is the key data object. It fills `struct rtw89_pci_info` with AX-generation PCI definitions, BD truncation/tag/burst modes, DMA idle/active intervals, RPP format size, register addresses and bit masks for HCI enable, BD modes, DMA stop/busy checks, RPWM/CPWM/MIT registers, DMA address setup, BD RAM table, interrupt callbacks, LTR setup, TX address filling, and RPP parsing. `rtw89_8852ae_info` is a `struct rtw89_driver_info` pointing at `rtw8852a_chip_info` and `rtw8852a_pci_info`. The PCI ID table matches vendor `PCI_VENDOR_ID_REALTEK` with device IDs `0x8852` and `0xa85a`, then stores `rtw89_8852ae_info` in `driver_data`. `rtw89_8852ae_driver` registers `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

Control flow: Module loading registers the `pci_driver` through `module_pci_driver()`. When the PCI core matches one of the IDs, `rtw89_pci_probe()` receives the driver info, allocates/initializes the RTW89 device, loads `rtw8852a_chip_info`, and configures PCI rings, DMA, interrupts, power management, and firmware around the static `rtw8852a_pci_info` parameters. Removal and PCI error recovery are delegated to common RTW89 PCI callbacks.

State and persistence: This file owns no mutable state beyond kernel driver registration. Persistent runtime state is held by the PCI core, `struct pci_dev`, and RTW89 device allocation performed by the common probe. The static config remains read-only and shared across devices.

Dependencies and integration points: Includes Linux module and PCI headers plus RTW89 `pci.h`, `reg.h`, and `rtw8852a.h`. It integrates with the Linux PCI bus, module autoloading through `MODULE_DEVICE_TABLE(pci, ...)`, RTW89 PCI DMA/interrupt helpers, RTW89 PM ops, and the RTL8852A chip info exported by the chip-specific implementation.

Risks: The static PCI register map and DMA/HCI parameters must match RTL8852AE hardware. Incorrect stop/busy registers, BD mode bits, tag settings, or interrupt callbacks can cause failed probe, stuck DMA, interrupt storms, suspend/resume failures, or packet loss. Device ID additions must use the right chip info; because `driver_data` is a raw pointer cast to `kernel_ulong_t`, a wrong pointer type would fail at runtime rather than through strong typing.

Test signals: Compile/link checks include `rtw8852a_chip_info` availability and PCI helper prototypes. Runtime signals are PCI modalias autoload, successful probe for IDs `10ec:8852` and `10ec:a85a`, firmware load, ring setup, TX/RX traffic, interrupt delivery, suspend/resume, PCI AER recovery paths, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852au.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852au.c

Purpose: This file is the USB bus glue module for RTL8852AU adapters. It maps known USB VID/PID/interface matches to the common RTW89 USB driver and supplies the 8852A-specific USB register map, endpoint alignment, and bulk-out DMA queue mapping.

Important APIs, types, and data: `rtw8852a_usb_info` fills `struct rtw89_usb_info` with USB HCI register addresses, endpoint registers, RX aggregation alignment of 8 bytes, and `bulkout_id` assignments for AC queues, management/high queues, and H2C firmware commands. `rtw89_8852au_info` points at `rtw8852a_chip_info` and the USB info. `rtw_8852au_id_table` contains vendor/product matches from Buffalo, Elecom, ASUS, Realtek, D-Link, TP-Link, and others using vendor-specific interface class/subclass/protocol values. `rtw_8852au_driver` registers `rtw89_usb_probe` and `rtw89_usb_disconnect`.

Control flow: Module insertion registers a Linux `usb_driver`. On a matching interface, the USB core calls `rtw89_usb_probe()`, which consumes `driver_info`, creates the RTW89 device, configures USB endpoints/aggregation/HCI registers from `rtw8852a_usb_info`, and then enters common chip initialization using `rtw8852a_chip_info`. Disconnect tears down URBs, queues, and the common RTW89 device through `rtw89_usb_disconnect()`.

State and persistence: The file has static const configuration and no local mutable state. Runtime persistence is in USB core device/interface state, URB/queue state allocated by common RTW89 USB code, firmware state on the adapter, and chip state programmed by common initialization. The endpoint mapping effectively persists for the device lifetime.

Dependencies and integration points: Includes Linux module and USB headers, `rtw8852a.h`, `reg.h`, and `usb.h`. Integrates with USB modalias autoloading through `MODULE_DEVICE_TABLE(usb, ...)`, the common RTW89 USB transport, H2C/C2H firmware paths, and the 8852A chip-info layer shared with PCIe.

Risks: Bulk-out queue mapping is hardware and firmware contract data. Wrong endpoint IDs can route traffic to the wrong pipe or stall TX/H2C commands. Missing or overly broad USB IDs can either fail to bind supported adapters or claim incompatible ones. USB suspend/resume is not wired locally in this snippet, so behavior depends on generic RTW89 USB support and kernel USB PM defaults.

Test signals: Build validates USB helper prototypes and chip-info linkage. Runtime signals include modalias autoload for listed VID/PIDs, successful probe and firmware download, correct endpoint discovery, RX aggregation alignment without malformed frames, H2C command completion, TX on all mapped queues, disconnect cleanup without URB leaks, and association/traffic on 2.4 GHz and 5 GHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852au.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.c

Purpose: This is the RTL8852B chip-description and chip-ops implementation for RTW89. It ties hardware constants, firmware naming, queue/memory quotas, efuse/PHY/RF tables, power sequencing, channel/RFK orchestration, Bluetooth coexistence parameters, TX power control hooks, WoWLAN capabilities, and MAC/PHY operation callbacks into one exported `rtw8852b_chip_info`.

Important APIs, types, and data: The exported symbol is `rtw8852b_chip_info`. Its `ops` member points at `rtw8852b_chip_ops`, which wires chip callbacks such as `rtw8852b_pwr_on_func`, `rtw8852b_pwr_off_func`, `rtw8852b_bb_reset`, `rtw8852b_set_channel`, `rtw8852b_set_channel_help`, `rtw8852b_rfk_init`, `rtw8852b_rfk_channel`, `rtw8852b_rfk_band_changed`, `rtw8852b_rfk_scan`, `rtw8852b_rfk_track`, `rtw8852b_btc_set_rfe`, and `rtw8852b_btc_set_wl_txpwr_ctrl`. Most PHY/MAC helpers are delegated through the 8852B-common function table wrappers such as `rtw8852bx_set_channel_bb()`, `rtw8852bx_read_efuse()`, `rtw8852bx_set_txpwr()`, and coexistence helpers. Static configuration includes PCIe/USB HFC quotas, DLE memory layouts, H2C/C2H registers, page registers, IMR registers, DIG/EDCCA/rfkill register maps, RRSR config, Bluetooth RF parameters, monitor registers, and RSSI thresholds.

Control flow: During probe the bus driver provides this chip info to common RTW89 initialization. Power-on runs a strict register sequence: SPS analog/digital adjustments, system-power polling, AFE LDO enable, WLON/MAC enable, platform toggles, XTAL SI transitions, isolation release, optional efuse-dependent voltage adjustments, and DMAC/CMAC function enables. Power-off reverses XTAL/RF/MAC state, waits for `APFM_OFFMAC`, and then selects PCIe or USB low-power behavior. Channel changes call MAC, BB, and RF setters in order. `set_channel_help` brackets channel changes by stopping scheduler TX, disabling PPDU status/TSSI continuous tracking/ADC, asserting BB reset, then restoring them afterward. RFK initialization resets TSSI mode and MCC RFK state, then performs DPK init, RCK, DACK, and RX DCK. Per-channel RFK does MCC channel indexing, notifies BTC, performs RX DCK, IQK, TSSI, DPK with BT time reservations, then notifies firmware about MCC RF state.

State and persistence: The chip info and tables are immutable. Runtime state is mutated in `rtwdev`: efuse values affect power voltage/RFE handling, `is_tssi_mode[]` tracks whether TSSI tracking is active per RF path, `rfk_mcc` stores multi-channel calibration indexes, and `btc` module info stores antenna type, BTG position, and coexistence metadata. Hardware register writes persist across later channel operations until reset or explicit restore. The DPK/TSSI/IQK state itself is maintained in structures filled by `rtw8852b_rfk.c`.

Dependencies and integration points: Includes core RTW89 modules for coexistence, firmware H2C, MAC, PHY, registers, TX/RX, 8852B-common helpers, RFK functions, and 8852B table objects. It exports chip info for bus-specific modules. It integrates with firmware loading through `MODULE_FIRMWARE(RTW8852B_MODULE_FIRMWARE)`, Linux PM WoWLAN stubs, RTW89 channel-context callbacks, BTC notifications/policies, common security/CAM/BA/beacon H2C paths, and generic RTW89 MAC/PHY definitions.

Risks: Power sequencing is timing-sensitive and bus-specific; missed polling errors or wrong XTAL SI masks can fail probe or leave RF partially powered. Queue quota and DLE/HFC tables differ for PCIe and USB; wrong values can starve queues or break firmware download. The channel helper always uses MAC/PHY 0 in several calls, so DBCC/MCC interactions depend on surrounding RTW89 assumptions. Coexistence RFE derivation infers antenna count from `rfe_type` parity, making efuse correctness important. `rtw8852b_btc_set_wl_txpwr_ctrl()` decodes packed bitfields from a firmware/coex word, so layout or sentinel drift can apply unintended TX power limits.

Test signals: Compile and module link validate exported table/chip symbols and callback signatures. Runtime signals include successful RTL8852B firmware request for `rtw89/rtw8852b_fw*`, PCIe and USB probe paths that use this chip info, power on/off and suspend/resume, channel changes across 2.4/5 GHz and 20/40/80 MHz, RFK logs for RCK/DACK/RX DCK/IQK/TSSI/DPK, BTC coexistence behavior with shared and dedicated antenna RFE types, WoWLAN magic/disconnect wake, RF kill GPIO behavior, and sustained TX/RX without DMA or MAC IMR errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.h

Purpose: This header is the minimal public chip-info declaration for RTL8852B. It gives bus modules and sibling code the RF/BB path counts and the exported `rtw8852b_chip_info` object.

Important APIs, types, and data: Defines `RF_PATH_NUM_8852B` and `BB_PATH_NUM_8852B` as 2, and declares `extern const struct rtw89_chip_info rtw8852b_chip_info`. `struct rtw89_chip_info` comes from `core.h` and is the main RTW89 per-chip capability and operation descriptor.

Control flow: No executable flow. Consumers include this header to pass `rtw8852b_chip_info` to bus probe glue and to size path-indexed loops or arrays for 8852B-specific code.

State and persistence: No local state. The declared chip-info object is immutable; all mutable state lives in `struct rtw89_dev` and hardware registers after consumers use the chip info.

Dependencies and integration points: Depends on `core.h`. It is paired with `rtw8852b.c`, which defines and exports `rtw8852b_chip_info`, and with RFK/common sources that share the two-path constants.

Risks: The path-count constants are deceptively small but foundational. If they diverge from the actual chip, loops over RF/TSSI/DPK/IQK state can skip a path or write nonexistent hardware. Renaming the chip-info declaration without updating bus glue breaks linking.

Test signals: Build coverage catches declaration mismatches. Runtime validation is indirect through any RTL8852B probe using the chip info, plus RF path A/B calibration, TSSI, DPK, and TX/RX chain reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.c

Purpose: This file implements the shared RTL8852B/RTL8852BT support layer behind the `rtw8852bx_info` indirection table. It covers efuse and PHY-cap parsing, thermal/PA-bias/power trim, channel MAC/BB programming, bandwidth and ADC setup, baseband resets, TX power setup, PMAC/TSSI helper primitives, RX path control, PPDU/RSSI translation, Bluetooth coexistence register programming, and BB/RF enable/disable.

Important APIs, types, and data: The exported `rtw8852bx_info` table binds many internal `__rtw8852bx_*` functions to inline wrappers declared in `rtw8852b_common.h`. Important structures are `struct rtw8852bx_efuse`, `struct rtw8852bx_tssi_offset`, `struct rtw89_tssi_info`, `struct rtw89_phy_efuse_gain`, `struct rtw89_power_trim_info`, `struct rtw8852bx_bb_tssi_bak`, and `struct rtw8852bx_bb_pmac_info`. Key routines parse efuse TSSI/gain/MAC address/RFE/XTAL data, parse PHY-cap power-cal/TSSI trim/thermal trim/PA-bias/gain compensation, program channel and bandwidth (`__rtw8852bx_set_channel_mac`, `__rtw8852bx_set_channel_bb`, `rtw8852bx_ctrl_ch`, `rtw8852bx_ctrl_bw`), configure TX power (`__rtw8852bx_set_txpwr`, `__rtw8852bx_init_txpwr_unit`, UL TB offset), control PMAC packet TX and path selection, backup/restore TSSI-sensitive BB state, initialize BTC/PTA, and convert RX reports.

Control flow: Common probe calls efuse and PHY-cap readers, which populate `rtwdev->efuse`, `rtwdev->tssi`, `rtwdev->efuse_gain`, and `rtwdev->pwr_trim`. Power trim later writes RF thermal and PA-bias fields only when programmed values are present. Channel changes first program MAC bandwidth/subcarrier/rate-check fields, then BB channel, SCO, CCK, gain compensation, bandwidth, BT-share, channel index, 5 MHz masks, monitor-mode packet-pop behavior, and a BB reset. TX power setup proceeds by by-rate, offset, CCK/OFDM shaping, limit, RU limit, then path-differential reference power based on antenna gain and SAR. PMAC/TSSI helpers configure synthetic packet TX, TX path, RX path, and restore state around calibration. BTC init programs PTA mode, priority masks, RF grant debug, TRX mask LUTs, break tables, BT counters, and marks coexistence init done.

State and persistence: This file is stateful through `rtwdev`. Efuse parsing persists country code, MAC address, RFE type, XTAL cap, TSSI offsets, thermal values, and RX gain offsets. PHY-cap parsing persists power calibration validity, trim tables, and gain compensation validity. BB setup snapshots RPL/RSSI bases into `efuse_gain`. BTC functions update `btc->cx.wl.status.map.init_ok` and `btc->dm.wl_lna2`. Hardware writes persist channel, gain, TX power, ADC, RF mode, PMAC, and coexistence state until later reconfiguration. Backup/restore helpers hold caller-provided stack copies of BB/TSSI state.

Dependencies and integration points: Includes RTW89 coexistence, debug, MAC, PHY, register, SAR, and utility layers plus its own header. It is consumed by `rtw8852b.c`, `rtw8852bt.c` style chip files, and RFK/TSSI calibration code through inline wrappers. It integrates with Linux/mac80211 RX status reporting, RTW89 regulatory/SAR queries, PHY table loaded defaults, firmware/BTC policy layers, and chip IDs `RTL8852B` and `RTL8852BT`.

Risks: The code is dominated by register masks and chip-specific constants, so semantic mistakes often compile cleanly. Channel-to-SCO and channel-to-gain-comp mappings must match supported bands. Efuse layout differs for PCIe and USB MAC address locations; using the wrong union member gives invalid addresses. `rtw8852bt_adc_cfg()` only applies to RTL8852BT, while RTL8852B uses simpler ADC settings; chip-ID branching must stay correct. TX power reference math combines SAR, antenna gain, RF codeword clamping, and TSSI offsets, so unit mistakes can create regulatory or performance issues. BTC routines manipulate RF LUTs and shared path gains; wrong values can regress Wi-Fi/BT coexistence.

Test signals: Build verifies the function-table shape and wrapper declarations. Runtime signals include efuse MAC/RFE/XTAL parsing for PCIe and USB devices, PHY-cap trim debug output, successful channel switch on 2.4/5 GHz with 20/40/80 MHz widths, correct CCK enable only on 2.4 GHz, TX power limit and SAR behavior, PMAC packet TX during TSSI alignment, RX chain/signal reporting in `ieee80211_rx_status`, monitor-mode packet-pop behavior, BTC init and priority masks, BT RSSI compensation, and BB/RF enable/disable during power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.h

Purpose: This header defines the shared 8852B-family interface used by concrete chip files and RFK code. It provides the packed efuse layout, PMAC/TSSI helper structures, the `rtw8852bx_info` function-pointer dispatch table, and static inline wrappers that call the current common implementation.

Important APIs, types, and data: It defines `RF_PATH_NUM_8852BX` and `BB_PATH_NUM_8852BX` as 2, `enum rtw8852bx_pmac_mode`, packed efuse structs `rtw8852bx_u_efuse`, `rtw8852bx_e_efuse`, `rtw8852bx_tssi_offset`, and `rtw8852bx_efuse`, PMAC info `rtw8852bx_bb_pmac_info`, TSSI backup `rtw8852bx_bb_tssi_bak`, and the central `struct rtw8852bx_info`. The function table includes MAC BB/RF enable, BB reset/setup/path control, PMAC TX, TSSI backup/restore, TX mode switch, channel MAC/BB programming, BTG/NBTG coexistence control, PPDU/RSSI handling, efuse/PHY-cap parsing, power trim, TX power configuration, thermal reads, ADC config, and BTC operations. Inline wrappers expose each operation with `rtw8852bx_*` names.

Control flow: The header itself has no branches other than inline forwarding. It shapes runtime dispatch: callers invoke a typed inline helper, which dereferences `rtw8852bx_info.<operation>` and calls the implementation installed by `rtw8852b_common.c`. This keeps concrete chip code concise while allowing the common implementation to be exported as one table.

State and persistence: The packed efuse structs describe persistent device-programmed data read from logical efuse/PHY-cap maps. The PMAC and TSSI backup structures hold transient state during calibration. The function table is immutable once linked. Inline wrappers do not store state, but the target functions mutate `struct rtw89_dev` and hardware registers.

Dependencies and integration points: Depends on `core.h`, including RTW89 core types, RF paths, channel structures, RX PPDU/status structures, and efuse block enums. It is included by 8852B chip, common, and RFK code. Its ABI must match `rtw8852b_common.c` exactly and is used by bus/chip code through `rtw8852b.c`.

Risks: Packed efuse layout is high risk because offsets and bitfields must match the device map; accidental padding or field movement corrupts MAC address, TSSI, RFE, country, gain, and thermal parsing. The function-pointer table has no null checks in wrappers, so every used slot must be initialized before use. Since many wrappers return void and write hardware, wrong dispatch wiring can create silent RF behavior changes. The header uses 8852BX naming for shared B/BT behavior, so new variants need clear compatibility review before reuse.

Test signals: Build catches function-pointer signature drift and missing `rtw8852bx_info`. Runtime validation includes efuse parsing for USB and PCIe layouts, common channel/TX power/BT coexistence flows through every wrapper used by `rtw8852b.c`, TSSI alignment backup/restore correctness, PMAC TX calibration, and static analysis or pahole-style checks for packed efuse offsets if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.c

Purpose: This is the RTL8852B RF calibration implementation. It performs RCK, DACK, RX DCK, IQK, DPK, TSSI setup/alignment/tracking, RF channel/bandwidth programming, MCC RFK channel bookkeeping, and channel-context RFK callbacks. It is the most stateful chip-specific RF file in this group.

Important APIs, types, and data: Public entry points are `rtw8852b_rck`, `rtw8852b_dack`, `rtw8852b_iqk`, `rtw8852b_rx_dck`, `rtw8852b_dpk_init`, `rtw8852b_dpk`, `rtw8852b_dpk_track`, `rtw8852b_tssi`, `rtw8852b_tssi_scan`, `rtw8852b_wifi_scan_notify`, `rtw8852b_set_channel_rf`, `rtw8852b_mcc_get_ch_info`, and `rtw8852b_rfk_chanctx_cb`. Internal state is organized around `struct rtw89_dack_info`, `struct rtw89_iqk_info`, `struct rtw89_dpk_info`, `struct rtw89_tssi_info`, `struct rtw89_rfk_mcc_info_data`, and `struct rtw89_chan`. The file uses RFK tables from `rtw8852b_rfk_table.h`, PHY/TX power tracking tables from `rtw8852b_table.h`, and common 8852BX BB helpers for PMAC/TSSI backup, TX path, RX path, and synthetic TX.

Control flow: Initial RFK from `rtw8852b.c` calls DPK init, RCK, DACK, and RX DCK. RCK loops paths and triggers RF RC calibration with timeout polling. DACK initializes AFE/DRCK, performs ADDCK and DACK for both paths, backs up calibration values into `rtwdev->dack`, and marks `dack_done`. RX DCK stops scheduler TX, waits for RX mode, toggles TSSI tracking if needed, runs DCK per path, then restores TX. IQK stops scheduler TX, initializes IQK state once, selects RF path by DBCC/PHY, backs up BB/RF registers, applies MAC/BB settings, presets KIP/CFIR table index, runs LOK/TXK/RXK with one-shot NCTL commands and retry logic, restores IQK coefficients and registers, and notifies BTC at start/stop. DPK optionally bypasses for external PA, otherwise selects/reloads DPK table slots, backs up KIP/RF/BB state, pauses TSSI, sets AFE/KIP/RF, runs sync/gain AGC/MDPK, fills result tables, enables or bypasses DPK per path, then restores everything. TSSI disables current tracking, programs RF/system/DCK/thermal/DAC/slope/alignment tables per path, optionally runs hardware TX alignment under stopped scheduler TX, enables tracking, and writes efuse/trim DE values. Channel RF programming writes RF channel/bandwidth for both DAV and non-DAV registers and validates LCK on path A.

State and persistence: This file writes both persistent hardware state and driver caches. `rtwdev->dack` stores ADDCK/MSBK/BIAS/DADCK data plus timeout flags and counters. `rtwdev->iqk` stores per-path band/bw/channel, MCC table indexes, LOK/IQK failures, coefficient backups, narrowband coefficient values, and counters. `rtwdev->dpk` stores enable/reload flags, current backup index per path, per-index band/channel/bw, TXAGC, PWSF, thermal-at-DPK, gain state, correlation/DC readings, and path validity. `rtwdev->tssi` stores efuse offsets, trim tables, alignment-done flags, alignment values by band and channel index, and accumulated alignment time. Register backups are stack-local and restored after calibration. Hardware RF/BB/TSSI/DPD coefficient state persists until later channel changes, scans, MCC transitions, resets, or tracking updates modify it.

Dependencies and integration points: Includes channel, coexistence, debug, MAC, PHY, register, 8852B chip/common/RFK/table headers. It integrates with RTW89 scheduler TX stop/resume, BTC RFK notifications and BT time preservation, channel-context/MCC callbacks, management channel lookup, RFK channel lookup helpers, NCTL polling, PHY register/RF accessors, PMAC synthetic TX, TSSI tracking, DPK thermal tracking via EWMA thermal stats, and chip ops installed in `rtw8852b.c`.

Risks: Calibration sequences are timing and order sensitive, with many `read_poll_timeout_atomic()` waits and small delays. A timeout may only set a debug flag while later code continues, so runtime RF degradation can be subtler than probe failure. DBCC/MCC path selection must match active PHY/channel context or calibration may be written to the wrong path/table. DPK reload uses band/channel matching but not bandwidth in the reload check, which is a point to review when changing backup semantics. TSSI alignment uses PMAC hardware TX and cached per-channel alignment; failures to restore BB/TSSI state would affect normal traffic. RF channel setting on path A includes LCK recovery while other writes are direct, so lock failures may be path-asymmetric. External PA bypass logic disables DPK by band based on FEM flags, making board data accuracy important.

Test signals: Build verifies the RFK table declarations and exported prototypes. Runtime validation requires RFK debug logs for RCK/DACK/RX DCK/IQK/DPK/TSSI, no NCTL or DPK one-shot timeouts, valid DACK backup dumps, association and throughput across 2.4/5 GHz, 20/40/80 MHz channel switches, DBCC and MCC channel-context start/stop, scan start/end TSSI behavior, DPK tracking over thermal changes, external-PA boards showing DPK bypass, BT coexistence notifications around RFK, and stable TX power/EVM/RSSI after repeated channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.h

Purpose: This header declares the public RTL8852B RF calibration entry points implemented in `rtw8852b_rfk.c`. It is the contract used by `rtw8852b.c` chip ops and channel-context callbacks to invoke RFK phases without exposing internal calibration helpers.

Important APIs and types: It includes `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, `enum rtw89_phy_idx`, and `enum rtw89_chanctx_idx`. Declared functions cover RCK, DACK, IQK, RX DCK, DPK initialization/calibration/tracking, TSSI setup and scan handling, scan notifications, RF channel setting, MCC channel info capture, and RFK channel-context state callbacks.

Control flow: The header has no executable code. It enables the higher-level chip file to install RFK functions into `rtw89_chip_ops` and the channel-context listener. At runtime those call sites enter `rtw8852b_rfk.c` for initial calibration, per-channel calibration, scan TSSI updates, periodic DPK tracking, and MCC start/stop handling.

State and persistence: No state is stored in the header. The declared functions mutate `struct rtw89_dev` RFK/TSSI/DPK/IQK/DACK state and hardware registers when called.

Dependencies and integration points: Paired with `rtw8852b_rfk.c` and included by `rtw8852b.c`. It also depends on common RTW89 channel and PHY index types from `core.h`. Function signatures must remain synchronized with chip ops and channel-context listener expectations.

Risks: Declaration drift breaks builds or silently discourages use of the intended RFK lifecycle if callers switch to incomplete alternatives. Since all routines accept `struct rtw89_dev *` and enum indexes, invalid phy/channel-context arguments are only checked in deeper helper logic, so call-site discipline matters. Adding new RFK phases should preserve BTC notification, scheduler pause, and state-restore conventions used by the implementation.

Test signals: Compile/link catches missing definitions. Runtime coverage comes from chip probe initial RFK, channel RFK, scan start/end, DPK tracking, RF channel changes, and MCC channel-context callbacks. Debug output from the implementation is the main confirmation that calls reached the expected phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_rfk.h -->
