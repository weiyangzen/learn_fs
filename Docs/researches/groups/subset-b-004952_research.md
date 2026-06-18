# Research Report: subset-b-004952

This grouped report covers the requested Realtek RTW89 8852B/8852BT table, bus glue, chip definition, and RF calibration files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.h

Purpose: Declares the externally defined RTL8852B PHY, RF, NCTL, transmit-power tracking, and default RFE parameter tables used by the common 8852B chip implementation. It is a small contract header between `rtw8852b_table.c` and chip setup code in `rtw8852b.c`.

Important APIs and types: The exports are `rtw89_8852b_phy_bb_table`, `rtw89_8852b_phy_bb_gain_table`, `rtw89_8852b_phy_radioa_table`, `rtw89_8852b_phy_radiob_table`, `rtw89_8852b_phy_nctl_table`, `rtw89_8852b_trk_cfg`, and `rtw89_8852b_dflt_parms`. All are declared as `const` table objects using core RTW89 types.

Control flow: The header has no executable logic. Control flow is indirect: chip registration points table pointers at these symbols, and the RTW89 PHY/table parser later walks them during device initialization and calibration.

State and persistence: The header declares immutable static configuration. The values become persistent hardware state only after parser code writes them into BB/RF/NCTL registers or firmware-visible power tracking structures.

Dependencies and integration points: Includes `core.h` for `struct rtw89_phy_table`, `struct rtw89_txpwr_track_cfg`, and `struct rtw89_rfe_parms`. It is consumed by `rtw8852b.c`; the definitions live in `rtw8852b_table.c`.

Risks: Symbol names are build-time ABI within the module. A missing declaration/definition pair breaks link, while a mismatched table pointer can silently program the wrong register group. Because the table data is hardware-sensitive, review must include the defining `.c` file and chip-info consumers.

Test signals: Compile/link coverage for `CONFIG_RTW89_8852B`, successful table parsing during probe, and RF/BB bring-up on PCI/USB 8852B devices validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852be.c

Purpose: Registers the PCIe RTL8852BE driver and supplies bus-specific PCI HCI parameters for the generic RTW89 PCI probe path. It binds Realtek PCI device ids `0xb852` and `0xb85b` to the common `rtw8852b_chip_info`.

Important APIs and types: `rtw8852b_pci_info` configures AX-generation PCI DMA descriptors, tag mode, burst sizes, low-power beacon control, DMA stop/busy registers, interrupt hooks, LTR handling, DMA channel masks, and RPP parsing. `rtw89_8852be_info` packages the chip pointer and PCI bus info. The `pci_device_id` table, `pci_driver`, and `module_pci_driver()` macro form the module entry.

Control flow: PCI core matches the id table, calls `rtw89_pci_probe`, and passes `rtw89_8852be_info` through `driver_data`. The shared PCI layer then uses `rtw8852b_pci_info` for ring setup, interrupts, power management, and DMA address programming. Remove, PM, and PCI error recovery are delegated to RTW89 generic callbacks.

State and persistence: The file itself stores only const descriptors. Runtime state lives in PCI core objects and the allocated `rtw89_dev`; PCI configuration values persist in hardware registers after the generic PCI layer writes them.

Dependencies and integration points: Depends on Linux PCI/module APIs plus local `pci.h`, `reg.h`, and `rtw8852b.h`. It integrates with `rtw8852b.c` chip operations and the shared RTW89 PCI HCI implementation.

Risks: Incorrect register fields or DMA masks can prevent RX/TX rings from operating or break low-power transitions. The BE module has no SSID quirks, so platform-specific quirks must be added deliberately. Device-id overlap with USB ids is harmless because the bus match layer is different, but the driver data must always point at PCI bus info.

Test signals: Build `rtw89_8852be`, verify modalias/module autoload for `10ec:b852` and `10ec:b85b`, probe/remove, suspend/resume, PCI AER recovery, interrupt handling, DMA ring traffic, and RX/TX throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852be.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.c

Purpose: Defines the RTL8852BT chip profile used by the 8852BT PCI variant. It supplies HFC/DLE memory layouts, register maps, interrupt masks, RF kill wiring, DIG/EDCCA controls, coexistence parameters, power sequencing, RFK hook ordering, chip operations, firmware metadata, and the exported `rtw8852bt_chip_info`.

Important APIs and functions: Public output is `rtw8852bt_chip_info`. Key private functions include `rtw8852bt_pwr_on_func()`, `rtw8852bt_pwr_off_func()`, `rtw8852bt_bb_reset()`, `rtw8852bt_set_channel()`, `rtw8852bt_set_channel_help()`, `rtw8852bt_rfk_init()`, `rtw8852bt_rfk_channel()`, `rtw8852bt_rfk_band_changed()`, `rtw8852bt_rfk_scan()`, `rtw8852bt_rfk_track()`, `rtw8852bt_btc_set_rfe()`, and `rtw8852bt_btc_set_wl_txpwr_ctrl()`.

Control flow: Probe reaches this file through `rtw8852bt_chip_info`. Power-on toggles SYS power, platform enable, XTAL SI, isolation, and DMAC/CMAC function bits, with polling around readiness. Channel changes use common 8852Bx MAC/BB helpers plus `rtw8852bt_set_channel_rf()` from the RFK file. Channel-help entry stops scheduler TX, disables PPDU status, pauses TSSI, disables ADC, and asserts BB reset; exit reverses that sequence. RFK initialization clears TSSI state, resets MCC state, initializes DPK, then runs RCK, DACK, and RX DCK. Per-channel RFK gathers MCC channel info, notifies coexistence, runs RX DCK, IQK, TSSI, and DPK with BT time preservation, then sends firmware MCC notification.

State and persistence: Most data is immutable chip configuration. Runtime state is mutated through `rtwdev`: `is_tssi_mode`, `rfk_mcc`, DPK/TSSI/IQK substructures, BTC module info, efuse-derived RFE data, scheduler stop state, and hardware registers. Power and chip-info settings persist in hardware until reset or power off.

Dependencies and integration points: Uses common RTW89 core, firmware, MAC, PHY, register, coexistence, and `rtw8852b_common` helpers. `rtw8852bte.c` points PCI devices at this chip info. The Makefile links this file with `rtw8852bt_rfk.c` and `rtw8852bt_rfk_table.c`.

Risks: Power sequencing is timing and register-order sensitive; failed XTAL SI writes or readiness polls abort probe. `rtw8852bt_rfk_channel()` runs several long RF calibrations and must keep scheduler/BT coexistence state balanced. Chip-info fields define many shared limits such as efuse sizes, DMA masks, queue quotas, NSS, channel contexts, and firmware format; wrong values can break core assumptions beyond this file.

Test signals: Module build/link, firmware request for `rtw89/rtw8852bt_fw`, PCI probe through BTE, power on/off, channel switch across 2G/5G and 20/40/80 MHz, MCC start/stop, WoWLAN stub exposure under PM, RFK debug logs, BTC notifications, and DPK/TSSI tracking during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.h

Purpose: Provides the minimal public chip header for RTL8852BT. It publishes path-count constants and the external `rtw8852bt_chip_info` symbol for bus modules and shared code.

Important APIs and types: Defines `RF_PATH_NUM_8852BT` and `BB_PATH_NUM_8852BT` as two-path devices, and declares `extern const struct rtw89_chip_info rtw8852bt_chip_info`.

Control flow: No executable control flow exists. The declared chip info is consumed by bus registration code such as `rtw8852bte.c`; path-count constants size loops and arrays in RFK code.

State and persistence: No mutable state. Constants determine compile-time and runtime iteration bounds for RF path A/B and BB path handling.

Dependencies and integration points: Includes `core.h` for `struct rtw89_chip_info`. Used by `rtw8852bt.c`, `rtw8852bt_rfk.c`, and `rtw8852bte.c`.

Risks: Path-count constants are assumed by calibration code and state arrays. Changing them without auditing `rtwdev->dpk`, `tssi`, `iqk`, DBCC path selection, and RF register offset logic would introduce out-of-bounds or skipped-path bugs.

Test signals: Compile coverage for all 8852BT objects and runtime RFK logs showing both RF paths validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.c

Purpose: Implements RTL8852BT RF calibration and RF channel programming. It covers RCK, RX DCK, DACK/ADDCK, IQK, DPK, TSSI setup/alignment/tracking, scan notifications, MCC channel bookkeeping, and RF channel/bandwidth writes.

Important APIs and functions: Public exports are `rtw8852bt_rck()`, `rtw8852bt_dack()`, `rtw8852bt_iqk()`, `rtw8852bt_rx_dck()`, `rtw8852bt_dpk_init()`, `rtw8852bt_dpk()`, `rtw8852bt_dpk_track()`, `rtw8852bt_tssi()`, `rtw8852bt_tssi_scan()`, `rtw8852bt_wifi_scan_notify()`, `rtw8852bt_set_channel_rf()`, `rtw8852bt_mcc_get_ch_info()`, and `rtw8852bt_rfk_chanctx_cb()`. Major internal groups include backup/reload helpers, `_kpath()`, `_iqk_*`, `_dpk_*`, `_tssi_*`, and RF channel helpers `_ctrl_ch()`, `_ctrl_bw()`, and `_rxbb_bw()`.

Control flow: Public calibration entry points notify BTC, stop scheduler TX when needed, wait for RX mode, back up BB/RF/KIP registers, force calibration clocks/AFE state, trigger NCTL one-shot commands, poll status registers, store results, restore registers, and resume TX. IQK runs per active path selected by DBCC, performs LOK/TX/RX calibrations, and restores CFIR state. DPK may reload an existing channel/path backup, otherwise runs KIP preset, TXAGC/RXAGC, sync/gain-loss AGC, MDPK, result fill, and DPD enable. TSSI disables DPK/TSSI, parses RFK tables, loads thermal/efuse derived DE values, optionally performs hardware-TX alignment, then re-enables tracking. Channel setting writes RF channel and bandwidth in both DAV and non-DAV RF register banks and checks S0 lock.

State and persistence: Mutates `rtwdev->dack`, `rtwdev->iqk`, `rtwdev->dpk`, `rtwdev->tssi`, `rtwdev->rfk_mcc`, `rtwdev->is_tssi_mode`, and thermal EWMA-derived tracking. Calibration results persist in driver backup arrays and in hardware DPD/TSSI/IQK/DACK registers until channel change, MCC callback, reset, or recalibration.

Dependencies and integration points: Depends on RTW89 channel management, BTC coexistence notifications, debug logging, firmware notifications, MAC scheduler controls, PHY/RF register accessors, `rtw8852b_common` helpers, and RFK tables from `rtw8852bt_rfk_table.c`. Called by chip ops in `rtw8852bt.c`.

Risks: This file is high risk because it is timing-sensitive, register-order-sensitive, and mostly hardware stateful. Poll timeouts often only log and continue, so degraded calibration can produce poor RF performance without probe failure. Some loops always process both paths in DPK/TSSI even when DBCC path selection is narrower. Signed arithmetic for DPK gain offsets and TSSI thermal deltas needs care. Backup/restore balance is critical when early exits happen.

Test signals: RFK debug logs for RCK/DACK/RX_DCK/IQK/DPK/TSSI, channel switches on all supported bands and widths, DBCC/MCC start-stop, scan start/end, external PA bypass cases, thermal drift with DPK tracking, BT coexistence during RFK, and register dumps after timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.h

Purpose: Declares the public RF calibration and RF channel-control API implemented by `rtw8852bt_rfk.c` for use by `rtw8852bt.c` chip operations.

Important APIs and types: Declares entry points for one-shot/initial calibration (`rtw8852bt_rck`, `rtw8852bt_dack`, `rtw8852bt_iqk`, `rtw8852bt_rx_dck`, `rtw8852bt_dpk_init`, `rtw8852bt_dpk`), periodic tracking (`rtw8852bt_dpk_track`), TSSI operation (`rtw8852bt_tssi`, `rtw8852bt_tssi_scan`, `rtw8852bt_wifi_scan_notify`), channel programming (`rtw8852bt_set_channel_rf`), MCC channel bookkeeping (`rtw8852bt_mcc_get_ch_info`), and channel-context callback handling (`rtw8852bt_rfk_chanctx_cb`).

Control flow: No logic executes here. The prototypes define the call boundary used by the chip ops table and channel-context listener in `rtw8852bt.c`.

State and persistence: No direct state. The function signatures expose which operations need `phy_idx`, `chanctx_idx`, or a concrete `struct rtw89_chan`, making channel-context state part of the API contract.

Dependencies and integration points: Includes `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, and enum types. Integrated by `rtw8852bt.c`; implemented by `rtw8852bt_rfk.c`.

Risks: Signature drift breaks chip-op wiring at compile time. More subtle risk is semantic: callers must stop/resume traffic and notify coexistence in the expected layer. Moving that responsibility across this header boundary requires auditing both caller and implementation.

Test signals: Build coverage and runtime execution of chip RFK hooks during init, channel change, scan, MCC, and periodic tracking validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.c

Purpose: Defines the RTL8852BT RFK register tables consumed by TSSI setup in `rtw8852bt_rfk.c`. The data programs system TSSI registers, per-path/per-band settings, TX power control, HE TB power, TSSI DCK, DAC gain, slope calibration, and alignment defaults.

Important APIs and types: Uses arrays of `struct rtw89_reg5_def` populated by `RTW89_DECL_RFK_WM()` and exported as `struct rtw89_rfk_tbl` objects through `RTW89_DECLARE_RFK_TBL()`. Exported table symbols include `rtw8852bt_tssi_sys_defs_tbl`, per-path 2G/5G system tables, init TX power tables, HE TB tables, DCK tables, DAC gain tables, 2G/5G slope tables, per-subband alignment defaults, and final slope enable tables.

Control flow: No executable branch logic exists apart from static initialization macros. Runtime selection is done by `rtw89_rfk_parser()` and `rtw89_rfk_parser_by_cond()` in the RFK implementation, which choose tables by RF path, band, and channel subband.

State and persistence: The file is immutable data. Once parsed, register writes persist in TSSI hardware blocks and influence power tracking until changed by scan/channel recalibration, reset, or another RFK pass.

Dependencies and integration points: Includes `rtw8852bt_rfk_table.h`, which includes `phy.h` for parser/table types. Closely coupled to `_tssi_set_sys()`, `_tssi_ini_txpwr_ctrl_bb()`, `_tssi_set_dck()`, `_tssi_set_dac_gain_tbl()`, `_tssi_slope_cal_org()`, `_tssi_alignment_default()`, and `_tssi_set_tssi_slope()`.

Risks: Table values are vendor/hardware data with little compiler validation. Path A/B tables are mostly offset variants; accidental cross-path register addresses or wrong masks would produce asymmetric RF behavior. Channel subband alignment tables have explicit 2G, 5G low/mid/high coverage and rely on caller channel classification.

Test signals: TSSI setup logs, register dumps after `rtw8852bt_tssi()` and `rtw8852bt_tssi_scan()`, path A/B transmit power tracking, 2G and 5G subband channel switches, HE TB power behavior, and comparison against vendor reference tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.h

Purpose: Declares all RFK TSSI table symbols provided by `rtw8852bt_rfk_table.c` for use by the 8852BT RFK implementation.

Important APIs and types: Exports `const struct rtw89_rfk_tbl` declarations for common TSSI system defaults, path A/B 2G/5G system defaults, init TX power, HE TB TX power, DCK, DAC gain, 2G/5G slope, per-path alignment defaults for 2G and three 5G ranges, and slope finalization tables.

Control flow: No executable logic. The header enables conditional parser calls in `rtw8852bt_rfk.c` to select the correct table based on path, band, and channel range.

State and persistence: No mutable state. It exposes immutable table data whose parsed results become hardware state.

Dependencies and integration points: Includes `phy.h` for `struct rtw89_rfk_tbl`. Used only by RFK table definition and RFK calibration implementation.

Risks: Declaration list must stay synchronized with the `.c` file and TSSI helper call sites. Removing or renaming a table breaks builds; swapping path or band semantics can build cleanly but misprogram RF power tracking.

Test signals: Compile/link coverage, table parser coverage during TSSI operations, and channel sweeps that hit every declared alignment table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bte.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bte.c

Purpose: Registers the PCIe 8852BE-VT/8852BT-facing module and binds Realtek PCI device `0xb520` to `rtw8852bt_chip_info` with PCI HCI parameters.

Important APIs and types: `rtw8852bt_pci_ssid_quirks` adds an HP subsystem quirk enabling `RTW89_QUIRK_THERMAL_PROT_110C`. `rtw8852bt_pci_info` mirrors AX PCI settings for descriptor truncation, DMA bursts, tags, interrupt operations, DMA stop/busy registers, and channel masks. `rtw89_8852bte_info`, the PCI id table, and `rtw89_8852bte_driver` wire the generic RTW89 PCI probe/remove/PM/AER callbacks.

Control flow: PCI match on `10ec:b520` passes `rtw89_8852bte_info` to `rtw89_pci_probe`. The shared PCI layer uses `rtw8852bt_pci_info` for HCI initialization and the core uses `rtw8852bt_chip_info` for chip operations, RFK, firmware, and limits.

State and persistence: The file holds immutable descriptors. Runtime state exists in PCI/core allocations and in hardware registers programmed by the generic PCI layer. SSID quirks become persistent driver behavior flags for matching systems.

Dependencies and integration points: Depends on Linux PCI/module APIs and local `pci.h`, `reg.h`, and `rtw8852bt.h`. Integrates with `rtw8852bt.c` and the shared RTW89 PCI transport.

Risks: Because the PCI setup is similar to 8852BE, drift between common AX PCI expectations and this descriptor can cause HCI issues. Quirk matching must be exact to avoid missing thermal protection on affected HP systems or applying it too broadly.

Test signals: Build `rtw89_8852bte`, modalias autoload for `10ec:b520`, HP SSID quirk detection, probe/remove, suspend/resume, AER recovery, DMA/interrupt traffic, and thermal-protection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bu.c

Purpose: Registers the USB RTL8852BU driver and supplies USB HCI register/endpoint parameters for the common RTW89 USB probe path. It binds multiple Realtek and OEM USB ids to the common `rtw8852b_chip_info`.

Important APIs and types: `rtw8852b_usb_info` defines USB HCI register addresses, RX aggregation alignment, and bulk-out endpoint ids for AC queues, management/high queues, and H2C. `rtw89_8852bu_info` packages the chip pointer and USB bus info. `rtw_8852bu_id_table` lists Realtek, Zyxel, ASUS, MSI, D-Link, TP-Link, and other vendor ids using vendor-specific class/interface matching. `rtw_8852bu_driver` delegates probe/disconnect to shared RTW89 USB callbacks.

Control flow: USB core matches an id table entry, calls `rtw89_usb_probe`, and passes `rtw89_8852bu_info` via `driver_info`. The generic USB layer uses the register map and bulkout endpoint mapping to configure transport, H2C, RX aggregation, and queues. Disconnect is fully delegated.

State and persistence: This file stores immutable bus descriptors. Runtime USB endpoints, URBs, aggregation settings, and core device state are allocated by shared USB/core code. Hardware register writes persist until disconnect/reset.

Dependencies and integration points: Includes Linux USB/module APIs plus local `rtw8852b.h`, `reg.h`, and `usb.h`. It integrates with shared 8852B chip operations rather than the 8852BT variant.

Risks: Endpoint mapping must match firmware and USB descriptors; a wrong bulkout id can route traffic to the wrong queue. The broad vendor-specific interface match is appropriate for Realtek-style devices but id additions must avoid unrelated devices with the same vendor/product. RX aggregation alignment affects buffer parsing.

Test signals: Build `rtw89_8852bu`, modalias/autoload for all listed ids, probe on USB2 and USB3, H2C command delivery, queue traffic on all ACs, RX aggregation parsing with 8-byte alignment, disconnect under traffic, and suspend/resume if supported by the shared USB layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bu.c -->
