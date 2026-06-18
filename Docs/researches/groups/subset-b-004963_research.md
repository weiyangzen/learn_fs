# Research: subset-b-004963

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.h

## Purpose
This header is the external table contract for the RTL8852C rtw89 chip support. It does not define data; it declares the BB, gain, radio, NCTL, TSSI, tracking, and default RFE parameter objects consumed by the 8852C chip descriptor and PHY initialization paths elsewhere in the driver.

## Important APIs, Types, and Data
- Includes `core.h` for `struct rtw89_phy_table`, `struct rtw89_phy_tssi_dbw_table`, `struct rtw89_txpwr_track_cfg`, and `struct rtw89_rfe_parms`.
- Declares `rtw89_8852c_phy_bb_table`, `rtw89_8852c_phy_bb_gain_table`, `rtw89_8852c_phy_radioa_table`, `rtw89_8852c_phy_radiob_table`, and `rtw89_8852c_phy_nctl_table`.
- Declares `rtw89_8852c_tssi_dbw_table`, `rtw89_8852c_trk_cfg`, and `rtw89_8852c_dflt_parms`.

## Control Flow and Integration
There is no executable control flow. The header is included by 8852C implementation files to bind generated/static register programming tables into the chip-info initialization pipeline. Consumers use the declared objects to load PHY/RF tables, configure TSSI behavior, and select default RFE parameters during probe or hardware setup.

## State and Persistence
The file owns no mutable state. The declared objects are expected to be immutable `const` definitions in matching table source files and become part of the module image.

## Dependencies
The declarations depend on rtw89 core table structures and on matching definitions being linked into the same driver build. The source path indicates Linux kernel driver code under Realtek rtw89, not Ceph-specific logic despite the repository prefix.

## Risks
- Missing or mismatched table definitions will fail link or cause chip descriptor setup to reference unavailable data.
- Table content errors in the defining C files can cause hardware misprogramming, but this header has no validation layer.
- Because these are extern declarations, build configuration must keep producer and consumer files in sync.

## Test Signals
- Compile/link coverage is the primary signal: all externs must resolve.
- Runtime bring-up should show successful 8852C PHY/RF table load, no register-table parse warnings, valid TSSI tracking, and normal association/throughput on both RF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ce.c

## Purpose
This file is the PCIe bus binding for the RTL8852CE 802.11ax device. It connects the generic rtw89 PCI framework to `rtw8852c_chip_info`, supplies AX-generation PCI DMA/interrupt/register layout data, registers the Realtek PCI ID `0xc852`, and carries DMI quirks for specific Dell systems.

## Important APIs, Types, and Data
- `rtw8852c_bd_idx_addr_low_power` maps low-power TX/RX buffer descriptor index handshakes to `R_AX_DRV_FW_HSK_*` registers.
- `rtw8852c_pci_info` is the core bus descriptor. It selects `rtw89_pci_gen_ax`, `rtw89_pci_isr_ax`, AX HAXI registers, DMA stop/busy registers, RPWM/CPWM addresses, RPP format size, `rtw89_pci_ch_dma_addr_set_v1`, `rtw89_bd_ram_table_dual`, and v1 interrupt/LTR/TX-address helpers.
- `rtw8852c_pci_quirks` matches Dell Vostro 16 5640 and Inspiron 16 5640 DMI strings and applies `RTW89_QUIRK_PCI_BER`.
- `rtw89_8852ce_info` points the bus layer at `rtw8852c_chip_info`, the PCI info, and the DMI quirk table.
- `rtw89_8852ce_id_table` binds vendor `PCI_VENDOR_ID_REALTEK` and device `0xc852`.
- `rtw89_8852ce_driver` uses `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops`, and `rtw89_pci_err_handler`.

## Control Flow
At module load, `module_pci_driver()` registers the PCI driver. During device discovery, the PCI core matches the ID table and passes `rtw89_8852ce_info` through `driver_data` to the common rtw89 PCI probe path. Probe then uses the chip info for MAC/PHY behavior and `rtw8852c_pci_info` for PCI DMA rings, interrupts, power-management registers, and descriptor parsing. Remove, runtime/system PM, and PCI error recovery are delegated to common rtw89 handlers.

## State and Persistence
All state in this file is static const configuration or kernel driver registration metadata. Runtime state is allocated and owned by the common rtw89 core and PCI layers. DMI quirk results persist for the lifetime of the probed device through the driver info/quirk path.

## Dependencies and Integration Points
The file depends on Linux PCI/module/DMI matching, rtw89 `pci.h`, `reg.h`, and `rtw8852c.h`. It integrates with common PCI DMA channel configuration, interrupt recognition, low-power HCI handshakes, PM ops, and PCI Advanced Error Reporting recovery.

## Risks
- Register-field mismatches in `rtw8852c_pci_info` can break DMA start/stop, interrupt masking, or low-power transitions.
- The Dell DMI quirk is highly specific; SKU or product-name drift can leave affected systems without BER handling.
- `check_rx_tag = false` and `rx_ring_eq_is_full = false` are behavioral assumptions that must match 8852C PCI hardware semantics.

## Test Signals
- Kernel module builds and exposes `MODULE_DEVICE_TABLE(pci, ...)`.
- `lspci -nn` device `10ec:c852` binds to `rtw89_8852ce`; probe completes without HAXI/DMA busy timeout.
- Suspend/resume, PCI error recovery, RX/TX DMA, and Dell quirked systems should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852cu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852cu.c

## Purpose
This file is the USB bus binding for RTL8852CU devices. It supplies USB register addresses, endpoint/channel mapping, USB IDs from several vendors, and a `usb_driver` that delegates probe/disconnect to the common rtw89 USB layer while reusing `rtw8852c_chip_info`.

## Important APIs, Types, and Data
- `rtw8852c_usb_info` provides USB HCI register addresses, `rx_agg_alignment = 8`, and `bulkout_id` mappings from rtw89 DMA queues to USB bulk endpoints.
- `rtw89_8852cu_info` selects `rtw8852c_chip_info` with `.bus.usb = &rtw8852c_usb_info`.
- `rtw_8852cu_id_table` matches multiple USB vendor/product IDs, including Realtek `0x0bda:c832`, `0x0bda:c85a`, and `0x0bda:c85d`.
- `rtw_8852cu_driver` uses `rtw89_usb_probe` and `rtw89_usb_disconnect`.

## Control Flow
The USB core matches an interface using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)`. The `driver_info` pointer supplies the rtw89 driver info to the common USB probe path. That path configures endpoints, aggregation, HCI registers, and chip-level operations from `rtw8852c_chip_info`. Disconnect is fully delegated to common USB teardown.

## State and Persistence
The file owns only static immutable registration tables. Runtime URB, endpoint, firmware, and device state is allocated by the rtw89 USB/core layers. The ID table persists in module metadata through `MODULE_DEVICE_TABLE(usb, ...)`.

## Dependencies and Integration Points
Depends on Linux USB/module APIs and rtw89 `usb.h`, `reg.h`, and `rtw8852c.h`. Integration hinges on correct DMA queue to endpoint mapping for data, management, high-priority, and H2C command traffic.

## Risks
- Incorrect `bulkout_id` mapping can silently route traffic to the wrong endpoint or break queue QoS.
- Vendor-specific IDs with class `0xff` rely on devices exposing the expected Realtek vendor interface.
- USB aggregation alignment must match firmware/device expectations or RX parsing can fail.

## Test Signals
- `modinfo` contains the USB aliases and devices bind on insertion.
- Probe should enumerate endpoints, download firmware, and pass TX/RX traffic on all mapped queues.
- Hot unplug/replug, suspend/resume, high-throughput RX aggregation, and H2C command delivery are key runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852cu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.c

## Purpose
This is the core RTL8922A Wi-Fi 7 chip implementation. It defines firmware identity, hardware flow-control/DLE/IMR/page/register tables, power-on/off sequences, efuse and phycap parsing, channel/MLO programming, RF calibration orchestration, TX power setup, Bluetooth coexistence hooks, RX report conversion, chip operations, exported chip info, and the 8922AE-VS variant.

## Important APIs, Types, and Data
- Firmware constants: `RTW8922A_FW_BASENAME`, `RTW8922A_FW_FORMAT_MAX`, and `MODULE_FIRMWARE`.
- Bus/memory tables: `rtw8922a_hfc_param_ini_pcie`, `rtw8922a_dle_mem_pcie`, H2C/C2H register arrays, WoW wake registers, page registers, DMAC/CMAC IMR tables, RRSR, rfkill, DIG, EDCCA, and efuse block layout.
- Power: `rtw8922a_pwr_on_func()` and `rtw8922a_pwr_off_func()` directly sequence BE sys power, HCI IO, ADIE pads, XTAL SI writes, DMAC/CMAC enables, and rtwdev flag bits.
- Efuse/phycap: `rtw8922a_read_efuse()`, RF/HCI block readers, TSSI and gain parsing, MAC address fallback to random when zero, thermal/PA/PAD bias trim parsing, and `rtw8922a_power_trim()`.
- Channel and PHY: `rtw8922a_set_channel_mac()`, `rtw8922a_ctrl_ch()`, `rtw8922a_ctrl_bw()`, CCK coefficient setup, RX gain programming, spur/NBI/CSI hooks, BBMCU pre/post init, MLO control, reset helpers, and `rtw8922a_set_channel_help()`.
- RFK: `rtw8922a_rfk_init()`, late init, channel calibration sequence, band-change TSSI scan calibration, and RFK notifications to BTC.
- TX power: by-rate/offset/limit/RU limit, triangular shaping, antenna/SAR differential handling, TSSI K/reference programming.
- BTC/coex: RFE detection, PTA/TRX mask initialization, BT RSSI conversion, WL TX power control, standby LUT programming, monitor registers, and RF parameter tables.
- Exported integration: `rtw8922a_chip_ops`, `rtw8922a_chip_info`, and `rtw8922ae_vs_variant`.

## Control Flow
Probe reaches this file through a bus wrapper such as `rtw8922ae.c`, which passes `rtw8922a_chip_info` to rtw89 core. The core calls chip ops through a lifecycle: power on, firmware load, BB pre/post init, efuse/phycap read, power trim, RFK init, channel setup, TX power setup, and runtime operations. Channel changes run through `set_channel_help(enter=true)`, which performs DBCC/MLO pre-work, hal reset, scheduler stop, PPDU disable, DFS/TSSI/ADC gating, and BB reset. `set_channel()` then updates MAC subcarrier/rate checks, BB frequency/bandwidth/gain/CCK/spur state, and RF channel registers. `set_channel_help(enter=false)` restores BB/RF MLO state, re-enables PPDU/ADC/DFS/TSSI, and resumes scheduling.

## State and Persistence
The file mutates persistent runtime state in `rtwdev`: flags for DMAC/CMAC enablement, `efuse` fields, `tssi`, `efuse_gain`, `pwr_trim`, `bb_gain`, `rfk_mcc`, `is_tssi_mode`, `btc` module/coexistence status, and HAL chip cut/thermal state. Persistent hardware state is programmed into MAC/BB/RF registers and survives until reset, power-off, or later channel/MLO changes. Immutable chip capabilities live in `rtw8922a_chip_info`.

## Dependencies and Integration Points
This implementation is tightly integrated with rtw89 core, MAC, PHY, firmware H2C/C2H, efuse, SAR, channel context, BTC, and Linux mac80211 RX status paths. It depends on firmware-provided parameters for default RFE/PHY data (`dflt_parms = NULL`, `rfe_parms_conf = NULL`), BE generation descriptors, and common helpers such as `rtw89_phy_set_txpwr_*`, `rtw89_btc_ntfy_wl_rfk()`, `rtw89_core_query_rxdesc_v2`, and BE firmware H2C table functions.

## Risks
- Power sequencing is register- and cut-version-sensitive; a failed poll or XTAL write aborts probe or power transition.
- Efuse gain conversion treats all-0xff/all-0x00 as invalid; bad maps can leave gain compensation disabled or wrong.
- MLO/DBCC register sequences have many mode-specific constants and are a high-risk area for single-link versus dual-link regressions.
- `rtw8922a_spur_freq()` currently returns zero, so NBI/CSI spur mitigation is effectively disabled for this chip.
- Several hooks are empty or firmware-offloaded (`rfk_scan`, `rfk_track`, WL RX gain), so test expectations must reflect missing local action.
- BTC RFE assumptions depend on efuse `rfe_type`; type zero is treated as an error path.

## Test Signals
- Build/link exports `rtw8922a_chip_info` and `rtw8922ae_vs_variant`; firmware request should target `rtw89/rtw8922a_fw`.
- Probe logs should show successful power-on, efuse parse, BB init, RFK, and no HCI/XTAL poll timeout.
- Channel switch tests should cover 2.4/5/6 GHz, 20/40/80/160 MHz, DBCC/MLO modes, SAR-by-antenna, and CCK channel 14.
- Runtime signals include valid RX RSSI/chains/frequency in mac80211 status, stable suspend/WoW behavior, BTC coexistence under BT traffic, and no RFK timeout during channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.h

## Purpose
This header defines the public RTL8922A chip-local data layout used by the implementation and bus wrappers. It exposes RF/BB path counts, packed efuse structures, and extern declarations for the chip info and PCI VS variant.

## Important APIs, Types, and Data
- `RF_PATH_NUM_8922A` and `BB_PATH_NUM_8922A` are both 2.
- `struct rtw8922a_tssi_offset` stores 2 GHz CCK/MCS, 5 GHz one-stream TSSI, and bandwidth-difference fields.
- `struct rtw8922a_rx_gain` and `struct rtw8922a_rx_gain_6g` model 2/5/6 GHz gain offsets.
- `struct rtw8922a_efuse` is a packed map of country code, TSSI offsets per path, channel plan, XTAL calibration, board/RFE information, thermals, gain offsets, and 6 GHz TSSI/gain data.
- Exports `rtw8922a_chip_info` and `rtw8922ae_vs_variant`.

## Control Flow and Integration
The header has no control flow. `rtw8922a.c` casts RF efuse log-map bytes to `struct rtw8922a_efuse` and reads fields from exact offsets. `rtw8922ae.c` references the exported chip info and variant when registering PCI IDs.

## State and Persistence
The structures describe persistent calibration data stored in device efuse. The header itself owns no runtime state. The `__packed` attributes are important because hardware efuse byte offsets must match the C layout exactly.

## Dependencies
Depends on `core.h` for shared rtw89 constants, gain/TSSI group sizes, and chip descriptor types.

## Risks
- Any field-size or order change breaks efuse offset interpretation.
- Reserved padding encodes the hardware layout; removing or resizing it can corrupt reads of later fields.
- The 8922A map lacks some second-offset gain structures that 8922D adds, so code must not assume the layouts are interchangeable.

## Test Signals
- Compile-time use by `rtw8922a.c` and `rtw8922ae.c`.
- Runtime efuse parse should produce plausible country, RFE, XTAL, thermal, TSSI, and gain values on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.c

## Purpose
This file implements RTL8922A RF calibration support outside the main chip file. It handles TSSI continuous tracking gating, RF channel register programming, synthesizer power selection for DBCC/MLO modes, calibration table reload selection, and RFK hardware/channel pre/post hooks.

## Important APIs, Types, and Functions
- `rtw8922a_tssi_cont_en_phyidx()` enables/disables continuous TSSI per PHY, mapping PHY0/PHY1 to RF A/B in `MLO_1_PLUS_1_1RF` and both paths otherwise.
- `rtw8922a_set_channel_rf()` wraps `rtw8922a_ctl_band_ch_bw()` to update RF `RR_CFGCH`/`RR_CFGCH_V1` for active kpaths and apply CAV-specific LUT writes.
- `_rf_syn_pow` encodes `RF_SYN_ON_OFF`, `RF_SYN_OFF_ON`, `RF_SYN_ALLON`, and `RF_SYN_ALLOFF`.
- `rtw8922a_set_syn01_cav()` and `_cbv()` program cut-specific synthesizer power bits.
- `rtw8922a_chlk_reload_sel_tbl_v0/v1()` maintain RFK MCC channel descriptors, with v1 selected when firmware advertises `RFK_PRE_NOTIFY_MCC_V1`.
- `rtw8922a_rfk_hw_init()`, `rtw8922a_pre_set_channel_rf()`, and `rtw8922a_post_set_channel_rf()` are called by chip ops around RFK and channel changes.

## Control Flow
Channel changes call pre-set RF logic when DBCC is active, temporarily selecting the appropriate synthesizer power state for the PHY being changed. RF channel programming reads current RF18 values, validates against `INV_RF_DATA`, merges channel/band/bandwidth bits from `rtw89_chip_chan_to_rf18_val()`, writes both RF channel registers, and delays for hardware settling. Post-set calls `rtw8922a_rfk_mlo_ctrl()`, which chooses synthesizer state from `mlo_dbcc_mode` and reloads calibration table selections for the management channels.

## State and Persistence
The file updates RF hardware registers and persistent driver RFK state in `rtwdev->rfk_mcc`. Table indices, channel, band, bandwidth, and RF18 values are retained for reuse across MCC/MLO channel reloads.

## Dependencies and Integration Points
It depends on `chan.h`, `mac.h`, `phy.h`, `reg.h`, `rtw8922a.h`, and rtw89 RFK helpers such as `rtw89_phy_get_kpath()`, `rtw89_phy_get_syn_sel()`, `rtw89_rfk_chan_lookup()`, and `rtw89_mgnt_chan_get()`. The main chip file wires these functions through `rtw8922a_chip_ops`.

## Risks
- Invalid RF reads abort programming; repeated `INV_RF_DATA` indicates lower-level RF access or power sequencing failure.
- Calibration table selection is limited to index <= 2; mode or firmware changes that need more entries require code changes.
- CAV/CBV synthesizer programming differs; wrong cut detection can power the wrong RF synthesizer.
- Shared-table v1 logic stores common channel arrays with per-path `table_idx`, so indexing mistakes can cross-contaminate paths.

## Test Signals
- RFK debug logs should show expected SYN config and no invalid RF18 warnings.
- DBCC/MLO channel switch tests should verify both PHYs retain calibrated RF state.
- Firmware feature toggling for `RFK_PRE_NOTIFY_MCC_V1` should be covered if both firmware generations are supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.h

## Purpose
This header exposes the RTL8922A RFK helper surface used by the main chip implementation. It declares TSSI tracking control, RF channel setup, hardware RFK init, and channel pre/post RF hooks.

## Important APIs
- `rtw8922a_tssi_cont_en_phyidx(struct rtw89_dev *rtwdev, bool en, u8 phy_idx)`
- `rtw8922a_set_channel_rf(struct rtw89_dev *rtwdev, const struct rtw89_chan *chan, enum rtw89_phy_idx phy_idx)`
- `rtw8922a_rfk_hw_init(struct rtw89_dev *rtwdev)`
- `rtw8922a_pre_set_channel_rf(struct rtw89_dev *rtwdev, enum rtw89_phy_idx phy_idx)`
- `rtw8922a_post_set_channel_rf(struct rtw89_dev *rtwdev, enum rtw89_phy_idx phy_idx)`

## Control Flow and Integration
No code executes here. `rtw8922a.c` includes this header and assigns the functions into chip ops or calls them from channel helper sequences. The header decouples RFK-specific register programming from the larger chip implementation.

## State and Persistence
No state is owned in the header. Implementations mutate RF registers and `rtwdev` RFK/TSSI state.

## Dependencies
Depends on `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, and PHY index definitions.

## Risks
- Prototype drift from `rtw8922a_rfk.c` breaks build.
- The surface is small but timing-sensitive: callers assume pre/post hooks can be used around scheduler/BB reset channel transitions.

## Test Signals
- Compile coverage confirms prototypes match definitions.
- Runtime channel-switch and RFK tests exercise every declared function indirectly through `rtw8922a_chip_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922ae.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922ae.c

## Purpose
This file is the PCIe bus binding for RTL8922AE and RTL8922AE-VS Wi-Fi 7 devices. It connects Linux PCI enumeration to `rtw8922a_chip_info`, supplies BE-generation PCI parameters, applies an SSID thermal-protection quirk, and selects the VS variant for device `0x892B`.

## Important APIs, Types, and Data
- `rtw8922a_pci_ssid_quirks` applies `RTW89_QUIRK_THERMAL_PROT_120C` to a Dell-specific Realtek subsystem ID.
- `rtw8922a_pci_info` selects `rtw89_pci_gen_be`, `rtw89_pci_isr_be`, BE HAXI registers, v2 interrupt/LTR helpers, BE DMA address setup, RX tag checking, no RXBD FS, and equal-full ring behavior.
- `rtw89_8922ae_info` uses base `rtw8922a_chip_info`.
- `rtw89_8922ae_vs_info` adds `rtw8922ae_vs_variant`.
- PCI IDs: Realtek `0x8922` for base AE and `0x892B` for VS.
- Driver uses `rtw89_pci_probe`, `rtw89_pci_remove`, `rtw89_pm_ops_be`, and `rtw89_pci_err_handler`.

## Control Flow
`module_pci_driver()` registers the PCI driver. PCI ID matching selects base or VS driver info via `driver_data`; common rtw89 PCI probe uses that info to allocate the device, load 8922A chip ops, configure PCI DMA/interrupt behavior, and apply variant constraints. Removal, PM, and error recovery remain common-code responsibilities.

## State and Persistence
Static const tables provide registration and bus configuration. Runtime state is held by rtw89 core/PCI. Variant choice persists for the lifetime of the device and changes firmware/MCS behavior through `rtw8922ae_vs_variant`.

## Dependencies and Integration Points
Depends on Linux PCI/module support, `pci.h`, `reg.h`, and `rtw8922a.h`. It integrates with BE PCI HCI ops, BE PM ops, PCI error recovery, and SSID quirk handling.

## Risks
- BE PCI register selection differs from AX parts; using the wrong ISR or DMA busy masks causes probe or interrupt failures.
- VS devices require the variant to disable MCS 12/13 and enforce minimum firmware; incorrect ID mapping can expose unsupported rates.
- Thermal-protection quirk coverage depends on exact subsystem ID match.

## Test Signals
- PCI aliases bind `10ec:8922` and `10ec:892b`.
- Base and VS devices should request correct firmware, complete BE PCI probe, and pass suspend/resume and AER tests.
- VS devices should report no MCS 12/13 support and satisfy firmware minimum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922ae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.c

## Purpose
This is the core RTL8922D Wi-Fi 7 chip implementation. It is structurally similar to 8922A but updated for BE4/PHY v1/v3 paths, new efuse gain layout, firmware TX compensation elements, LCK tracking, 8922D/8922DS firmware selection, PCI DMA masks, and the 8922DE-VS variant.

## Important APIs, Types, and Data
- Firmware constants: `RTW8922D_FW_BASENAME`, `RTW8922DS_FW_BASENAME`, both with format max 0.
- Bus/memory/register tables: 8922D HFC/DLE PCI quotas, H2C/C2H registers, page regs, WoW regs, DMAC/CMAC IMR tables, RRSR, rfkill, DIG, EDCCA, efuse blocks, and `rtw8922d_nctl_post_defs_tbl`.
- Power: `rtw8922d_pwr_on_func()` and `rtw8922d_pwr_off_func()` implement BE power sequencing with CID-specific cases for `RTL8922D_CID7025` and `RTL8922D_CID7090`.
- Efuse/phycap: `rtw8922d_read_efuse()` parses HCI MAC addresses, RF RFE/XTAL/country/BT settings, TSSI, primary and secondary gain offsets, VCO/thermal/PA/PAD trims.
- Gain/channel: channel-aware gain interpolation/selection for 2/5/6 GHz, CCK/OFDM calculated efuse gain, BE4 channel/bandwidth programming, spur mitigation for AID7060 at 6400 MHz, and `calc_rx_gain_normal` support.
- MLO/channel helper: `rtw8922d_ctrl_mlo()`, pre/post channel BB/RF hooks, DACK reset, TSSI gating, scheduler stop/resume, and EMLSR/BB wrapper register programming.
- RFK: late init, channel RFK sequence including TXGAPK, TXIQK, IQK, TSSI, CIM3K, DPK, RXDCK, scan TSSI disable/enable, and LCK tracking.
- TX power: by-rate/offset/limit/RU, reference and differential path programming, SAR by path, and firmware-provided digital power compensation.
- BTC/coex: v9 RF parameter tables, BT RSSI conversion, firmware-offloaded RFE/init/counter/standby/RX gain hooks, and WL TX power control.
- Exported integration: `rtw8922d_chip_ops`, `rtw8922d_chip_info`, `rtw8922de_vs_fw_def`, and `rtw8922de_vs_variant`.

## Control Flow
Bus wrappers such as `rtw8922de.c` pass `rtw8922d_chip_info` and optionally `rtw8922de_vs_variant` to rtw89 probe. The common core calls chip ops for power, efuse, phycap, BB init, RFK, channel setup, TX power, and RX reporting. Channel changes use `rtw8922d_set_channel_help()` to enter a protected state: DBCC pre-sequencing, RF pre-hook, scheduler stop, PPDU disable, DACK reset, TSSI tracking disable, and BB reset. The actual channel setup updates MAC subcarrier and rate checks, BE4 BB frequency/bandwidth/gain/spur state, and RF registers. Exit restores MLO, RFK table state, TSSI, BB reset, PPDU status, and scheduler state.

## State and Persistence
The file mutates `rtwdev->flags`, `efuse`, `tssi`, `efuse_gain` including `offset2`, `pwr_trim`, `rfk_mcc`, `lck`, `is_tssi_mode`, BTC data, and HAL CID/AID/CV dependent behavior. Hardware state is persisted in MAC/BB/RF registers until reset or reconfiguration. The exported chip info is immutable module data and advertises capability limits, firmware requirements, efuse sizes, security CAM sizes, DMA masks, power-save modes, and default quirks.

## Dependencies and Integration Points
Depends on rtw89 core, MAC BE/BE v1, PHY BE v1/v3 helpers, firmware element parsing, efuse, SAR, BTC, channel context, and Linux mac80211 status conversion. Digital power compensation depends on the firmware `tx_comp` element size matching the expected 5-dimensional table. RX descriptor handling uses v3 core query/fill helpers.

## Risks
- `rtw8922d_set_digital_pwr_comp()` dereferences firmware TX compensation metadata after size validation but assumes `tx_comp` is present; firmware element coverage is critical.
- Gain offset selection uses many channel boundary cases and secondary efuse offsets; off-by-one channel ranges can bias RSSI/TSSI by band edge.
- CID/AID-specific paths affect power, spur mitigation, and AWGN detection; unsupported silicon IDs may miss required workarounds.
- `rtw8922d_btc_set_rfe()` and related BTC initialization are firmware-offloaded stubs, so firmware regressions have fewer driver-side guardrails.
- LCK tracking triggers recalibration on thermal delta >= 16; incorrect thermal reads can cause missed or excessive calibration.

## Test Signals
- Build exports `rtw8922d_chip_info` and `rtw8922de_vs_variant`; firmware requests should include `rtw89/rtw8922d_fw` and VS `rtw89/rtw8922ds_fw`.
- Probe should validate firmware elements, parse efuse/phycap, and complete power/BB/RFK initialization on supported CIDs/AIDs.
- Channel/MLO testing should cover 2.4/5/6 GHz, 20/40/80/160 MHz, single-link, DBCC, EMLSR/MLO modes, scan transitions, and AID7060 spur mitigation.
- Runtime signals include stable RX RSSI/frequency reporting, SAR behavior per antenna, BTC coexistence with firmware-offloaded policy, LCK under thermal change, WoW/suspend, and PCI recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.h

## Purpose
This header defines RTL8922D path counts, packed efuse structures, and extern declarations for the base chip info and VS variant. It is the layout contract used by `rtw8922d.c` when parsing RF efuse bytes and by PCI bus glue when selecting chip descriptors.

## Important APIs, Types, and Data
- `RF_PATH_NUM_8922D` and `BB_PATH_NUM_8922D` are both 2.
- `struct rtw8922d_tssi_offset` and `struct rtw8922d_tssi_offset_6g` separate common 2/5 GHz and 6 GHz TSSI layouts.
- `struct rtw8922d_rx_gain` and `struct rtw8922d_rx_gain_6g` define 2/5/6 GHz gain offsets.
- `struct rtw8922d_efuse` extends 8922A-style layout with BT settings, secondary 2/5 GHz gain sets, path-specific 6 GHz TSSI structs, extra secondary 6 GHz gains, and additional reserved padding.
- Exports `rtw8922d_chip_info` and `rtw8922de_vs_variant`.

## Control Flow and Integration
The header has no executable code. `rtw8922d.c` casts the RF efuse log map to `struct rtw8922d_efuse` and copies fields into rtw89 runtime structures. `rtw8922de.c` consumes the exported descriptors for PCI ID registration.

## State and Persistence
The structures model persistent efuse calibration/state written on hardware. The file itself has no mutable state. The `__packed` annotations preserve byte-accurate hardware layout.

## Dependencies
Depends on `core.h` for shared rtw89 types and group-count constants.

## Risks
- Layout drift will corrupt efuse parsing and can break MAC address, RFE, TSSI, gain, thermal, and BT setting extraction.
- Secondary gain fields are important for channel-dependent compensation; treating this like the 8922A layout loses calibration fidelity.
- Reserved bytes should not be repurposed without matching hardware documentation.

## Test Signals
- Compile coverage from `rtw8922d.c` and `rtw8922de.c`.
- Runtime efuse dumps should produce plausible primary/secondary gains, BT settings, RFE type, XTAL, thermals, and 6 GHz calibration fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.c

## Purpose
This file implements RTL8922D RFK helper logic. It handles a small NCTL post table, TSSI continuous tracking control, RF channel programming, synthesizer/MLO RF state, calibration table reload, RFK hardware setup, pre/post channel RF hooks, and LCK thermal tracking.

## Important APIs, Types, and Functions
- `rtw8922d_nctl_post_defs` plus `RTW89_DECLARE_RFK_TBL()` exports `rtw8922d_nctl_post_defs_tbl`.
- `rtw8922d_tssi_cont_en_phyidx()` gates continuous TSSI tracking per PHY/path using BE4 indexed PHY writes.
- `rtw8922d_set_channel_rf()` writes RF `RR_CFGCH` and `RR_CFGCH_V1` with RSV/MOD sequencing and a 400 us settling delay.
- `_rf_syn_pow`, `rtw8922d_get_syn_pow()`, and `rtw8922d_set_syn01()` select RF synthesizer power based on `mlo_dbcc_mode`.
- `rtw8922d_chlk_reload_sel_tbl()` and `rtw8922d_chlk_reload()` update RFK MCC descriptors and RF/BB table selection for both paths.
- `rtw8922d_rfk_hw_init()` applies X4K settings.
- `rtw8922d_pre_set_channel_rf()` and `rtw8922d_post_set_channel_rf()` coordinate RF state around channel changes.
- `_get_thermal()`, `_lck_keep_thermal()`, `_lck()`, and `rtw8922d_lck_track()` implement thermal-threshold-triggered LCK.

## Control Flow
Hardware init applies X4K RF settings. Channel changes call pre-set when DBCC is enabled to select SYN power for the changing PHY, then the main chip code writes channel state, then post-set calls `rtw8922d_rfk_mlo_ctrl()` to restore mode-appropriate SYN power and reload calibration table selection. LCK tracking periodically reads thermal per RF path; when the delta from stored `lck->thermal[]` reaches `RTW8922D_LCK_TH` (16), `_lck()` triggers calibration on active paths and refreshes the baseline.

## State and Persistence
The file mutates RF/BB registers, `rtwdev->rfk_mcc.data`, and `rtwdev->lck.thermal[]`. These values persist across channel changes and tracking cycles until reset or RFK reinitialization.

## Dependencies and Integration Points
Depends on `chan.h`, `debug.h`, `phy.h`, `reg.h`, `rtw8922d.h`, and rtw89 RFK channel lookup, management-channel, RF read/write, and indexed PHY write helpers. `rtw8922d.c` wires the exported functions into chip ops and RFK tracking.

## Risks
- `mlo_linking` in `rtw8922d_chlk_ktbl_sel()` is hardcoded false, so any future linking-specific behavior is currently inactive.
- LCK relies on thermal reads being stable; noisy thermal values can cause excessive LCK or missed recalibration.
- RF channel writes use the selected synthesizer path only; wrong `rtw89_phy_get_syn_sel()` results can tune the wrong path.
- Table selection supports only indices <= 2; more RFK channel slots require updates.

## Test Signals
- RFK debug logs should show expected SYN config, LCK thermal readings, and no out-of-limit table warnings.
- DBCC/MLO channel switch tests should validate correct RF path tuning and calibration reuse.
- Thermal-stress tests should verify LCK fires when expected and does not destabilize RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.h

## Purpose
This header exposes RTL8922D RFK helper functions and the NCTL post RFK table to the main 8922D chip implementation.

## Important APIs
- `extern const struct rtw89_rfk_tbl rtw8922d_nctl_post_defs_tbl`
- `rtw8922d_tssi_cont_en_phyidx()`
- `rtw8922d_set_channel_rf()`
- `rtw8922d_rfk_hw_init()`
- `rtw8922d_rfk_mlo_ctrl()`
- `rtw8922d_pre_set_channel_rf()`
- `rtw8922d_post_set_channel_rf()`
- `rtw8922d_lck_track()`

## Control Flow and Integration
No code runs in the header. `rtw8922d.c` includes it to connect RFK helper implementations to chip ops and the chip info NCTL post table. The declarations form the boundary between general chip lifecycle code and RF-specific calibration code.

## State and Persistence
No state is owned here. Implementations mutate RF registers, RFK MCC data, TSSI state, and LCK thermal baselines.

## Dependencies
Depends on `core.h` for rtw89 device, channel, PHY index, and RFK table types.

## Risks
- Prototype mismatch breaks build.
- Callers rely on the declared pre/post channel hooks and LCK tracking semantics; changing signatures or behavior requires synchronized chip-op updates.

## Test Signals
- Compile/link coverage for `rtw8922d.c` and `rtw8922d_rfk.c`.
- Runtime RFK/channel/LCK tests exercise all declared functions indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922de.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922de.c

## Purpose
This file is the PCIe bus binding for RTL8922DE and RTL8922DE-VS Wi-Fi 7 devices. It supplies BE-generation PCI v1 parameters, maps Realtek device IDs to base or VS chip variants, and registers the PCI driver against common rtw89 probe/remove/PM/error handlers.

## Important APIs, Types, and Data
- `rtw8922d_pci_info` selects `rtw89_pci_gen_be`, `rtw89_pci_isr_be_v1`, BE HAXI registers, group BD addressing, RPP format v1, BE v1 DMA address setup, v3 interrupt helpers, v1 DMA busy/stop masks, and a TX DMA channel mask that excludes alternating ACH/high queues.
- `rtw89_8922de_vs_info` uses `rtw8922d_chip_info` with `rtw8922de_vs_variant`.
- `rtw89_8922de_info` uses base `rtw8922d_chip_info`.
- PCI IDs: `0x892D` and `0x882D` select VS, while `0x895D` selects base.
- Driver uses `rtw89_pm_ops_be` and `rtw89_pci_err_handler`.

## Control Flow
The PCI core matches one of the device IDs and passes the selected `rtw89_driver_info` pointer through `driver_data`. Common PCI probe then initializes PCI DMA/interrupt behavior from `rtw8922d_pci_info` and chip behavior from the base or VS chip descriptor. Removal, PM, and PCI error recovery are delegated to shared rtw89 code.

## State and Persistence
The file contains static const bus configuration and registration metadata only. Runtime device state is owned by the common rtw89 core/PCI layers. Variant selection persists for the device lifetime and can override firmware and capability behavior.

## Dependencies and Integration Points
Depends on Linux PCI/module APIs, rtw89 `pci.h`, `reg.h`, and `rtw8922d.h`. It integrates with BE PCI v1/v3 interrupt plumbing, DMA channel selection, PM, and AER recovery.

## Risks
- `group_bd_addr = true`, `rpp_fmt_size = sizeof(struct rtw89_pci_rpp_fmt_v1)`, and v3 interrupt helpers must match the 8922D PCI hardware revision.
- Device-ID to variant mapping affects firmware basename and MCS support; wrong mapping can request incompatible firmware or advertise unsupported rates.
- TX DMA channel mask must align with queue topology in `rtw8922d_chip_info`.

## Test Signals
- PCI aliases should bind `10ec:892d`, `10ec:882d`, and `10ec:895d`.
- Base and VS devices should complete probe, firmware load, DMA ring init, interrupt handling, suspend/resume, and PCI error recovery.
- VS devices should request the 8922DS firmware override and enforce variant capability limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922de.c -->
