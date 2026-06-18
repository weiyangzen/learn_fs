# subset-b-004911 research

Grouped research for Realtek `rtw88` RTL8822B bus glue and RTL8822C chip implementation/header files. Each section is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.h

## Purpose

`rtw8822b_table.h` is a small declaration header for RTL8822B PHY/MAC/RF initialization and regulatory power-limit tables. It does not contain table data itself; it exposes `extern const struct rtw_table` objects generated/defined in the matching RTL8822B table implementation so `rtw8822b.c` and chip-spec setup can bind the right initialization tables into `struct rtw_chip_info` and RFE definitions.

## Important APIs and Types

- Include guard `__RTW8822B_TABLE_H__` prevents duplicate declarations.
- Declares MAC, AGC, BB, BB power-by-rate, RF path A/B, and transmit power limit tables:
  - `rtw8822b_mac_tbl`, `rtw8822b_agc_tbl`, `rtw8822b_bb_tbl`
  - `rtw8822b_bb_pg_type2_tbl`, `rtw8822b_bb_pg_type3_tbl`, `rtw8822b_bb_pg_type5_tbl`
  - `rtw8822b_rf_a_tbl`, `rtw8822b_rf_b_tbl`
  - `rtw8822b_txpwr_lmt_type0_tbl`, `rtw8822b_txpwr_lmt_type2_tbl`, `rtw8822b_txpwr_lmt_type5_tbl`
- Depends on `struct rtw_table` being declared before inclusion, normally through chip or PHY headers in the surrounding `rtw88` driver.

## Control Flow and Integration

There is no executable control flow in this header. Its role is link-time integration: other RTL8822B code includes it and assigns table addresses to chip/RFE descriptors. During device bring-up, the core `rtw_phy_load_tables()` path consumes the selected `struct rtw_table` entries and calls their parse callbacks to write register sequences into MAC/BB/RF hardware blocks.

## State and Persistence

The declarations reference immutable, static table data. Persistent behavior comes from the hardware state programmed from those tables, not from this header. The declared transmit-power limit tables are especially important because they feed regulatory/rate/channel power decisions after efuse and RFE selection.

## Dependencies

This header depends on the rtw88 table abstraction and matching table definitions. It is coupled to RTL8822B chip data in `rtw8822b.c`, RFE macros in `main.h`, and table parser helpers in `phy.c`/table declaration macros.

## Risks

- Missing or mismatched table symbols cause link failures for RTL8822B modules.
- Picking the wrong power-limit or BB power-group table for an RFE type can produce incorrect transmit power, regulatory failures, or poor RF performance.
- Because the header only declares `struct rtw_table`, include order must provide the type definition; using it in a new compilation unit without proper rtw88 headers will fail.

## Test Signals

- Build coverage for RTL8822B variants should catch unresolved externs.
- Runtime signals are indirect: successful PHY table loading, correct channel/rate TX power, and absence of RF initialization errors in `RTW_DBG_PHY`/`RTW_DBG_RFK` logs.
- Regulatory and RF regression testing should exercise all RFE table types referenced here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822be.c

## Purpose

`rtw8822be.c` is the PCIe module binding for Realtek RTL8822BE devices. It contains no chip logic itself; it identifies PCI device ID `10ec:b822`, attaches `rtw8822b_hw_spec` through `driver_data`, and delegates probe/remove/shutdown/error handling to the shared `rtw88` PCI transport layer.

## Important APIs and Types

- `rtw_8822be_id_table[]`: `struct pci_device_id` table with `PCI_DEVICE(PCI_VENDOR_ID_REALTEK, 0xB822)` and `.driver_data = (kernel_ulong_t)&rtw8822b_hw_spec`.
- `MODULE_DEVICE_TABLE(pci, rtw_8822be_id_table)`: exports modalias information for autoloading.
- `rtw_8822be_driver`: `struct pci_driver` using:
  - `.probe = rtw_pci_probe`
  - `.remove = rtw_pci_remove`
  - `.driver.pm = &rtw_pm_ops`
  - `.shutdown = rtw_pci_shutdown`
  - `.err_handler = &rtw_pci_err_handler`
- `module_pci_driver(rtw_8822be_driver)`: provides module init/exit registration.

## Control Flow and Integration

When the PCI core matches the device ID, `rtw_pci_probe()` receives the `pci_dev` and ID entry. The shared PCI probe path extracts `driver_data`, obtains the RTL8822B chip descriptor, maps PCI resources, allocates and initializes `struct rtw_dev`, loads firmware/tables, and registers with mac80211. Removal and shutdown reverse that work through common PCI callbacks. PCIe Advanced Error Reporting or reset handling flows through `rtw_pci_err_handler`.

## State and Persistence

This file owns only static module registration state. Device state is allocated by the common PCI probe path and chip-specific RTL8822B operations. Suspend/resume behavior is delegated to `rtw_pm_ops`; this module only wires the PM operations into the driver object.

## Dependencies

It depends on Linux PCI/module APIs plus rtw88 headers `pci.h` and `rtw8822b.h`. The real operational dependency is `rtw8822b_hw_spec`, which supplies all chip operations, firmware names, register tables, efuse layout, and capability flags.

## Risks

- Any incorrect PCI ID or `driver_data` pointer would bind the wrong hardware specification or fail autoloading.
- Because this file is deliberately thin, changes to shared PCI callbacks affect RTL8822BE behavior broadly.
- Error recovery depends on `rtw_pci_err_handler`; devices may behave poorly after bus reset if chip state cannot be rebuilt from the shared path.

## Test Signals

- Kernel module build and `modinfo` should expose the PCI alias for `10ec:b822`.
- On hardware, `lspci -nnk` should show this driver bound, and probe logs should enter the common `rtw88_pci` path.
- Suspend/resume, shutdown, and PCI error injection tests validate that this binding supplies the common callbacks correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822be.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bs.c

## Purpose

`rtw8822bs.c` is the SDIO module binding for RTL8822BS. It matches the Realtek SDIO vendor/device ID, points the shared SDIO transport at `rtw8822b_hw_spec`, and registers a `struct sdio_driver` with standard rtw88 SDIO callbacks.

## Important APIs and Types

- `rtw_8822bs_id_table[]`: `struct sdio_device_id` table matching `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8822BS`.
- `MODULE_DEVICE_TABLE(sdio, rtw_8822bs_id_table)`: exposes SDIO modalias information.
- `rtw_8822bs_driver`: `struct sdio_driver` with:
  - `.probe = rtw_sdio_probe`
  - `.remove = rtw_sdio_remove`
  - `.shutdown = rtw_sdio_shutdown`
  - `.drv.pm = &rtw_sdio_pm_ops`
  - `.id_table = rtw_8822bs_id_table`
- `module_sdio_driver(rtw_8822bs_driver)` supplies module registration boilerplate.

## Control Flow and Integration

The MMC/SDIO core calls `rtw_sdio_probe()` when the function ID matches. The generic rtw88 SDIO path reads `.driver_data`, initializes the bus-specific I/O layer, then uses RTL8822B chip operations for firmware loading, efuse parsing, PHY/MAC setup, and mac80211 registration. Removal and shutdown are delegated to the same SDIO infrastructure.

## State and Persistence

This file contains only static ID and driver registration state. Runtime device state lives in the SDIO core function object, rtw88 transport structures, and RTL8822B chip/DM state. Power-management persistence is handled by `rtw_sdio_pm_ops`.

## Dependencies

It depends on Linux MMC/SDIO IDs, `main.h`, `sdio.h`, and `rtw8822b.h`. It is tightly coupled to the shared SDIO transport and to the correctness of the `rtw8822b_hw_spec` pointer stored in `.driver_data`.

## Risks

- Bad device ID coverage prevents autoload or matching for RTL8822BS modules.
- SDIO power sequencing and wake behavior are completely delegated; regressions in the shared transport will surface here without local mitigation.
- SDIO I/O can be sensitive to host-controller quirks; this binding has no quirk table of its own.

## Test Signals

- Build/modalias output should include the Realtek RTL8822BS SDIO ID.
- Hardware boot logs should show `rtw_sdio_probe()` selecting `rtw8822b_hw_spec`.
- Suspend/resume, card removal, and shutdown tests are the primary behavior signals for this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bu.c

## Purpose

`rtw8822bu.c` is the USB module binding for RTL8822BU and many rebadged USB adapters using the same RTL8822B hardware. It maintains the USB VID/PID match table, associates every entry with `rtw8822b_hw_spec`, and registers a `usb_driver` that delegates probe/disconnect to the shared rtw88 USB transport.

## Important APIs and Types

- `rtw_8822bu_id_table[]`: `struct usb_device_id` table using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for vendor-specific Realtek-style interfaces.
- Each table entry sets `.driver_info = (kernel_ulong_t)&rtw8822b_hw_spec`.
- The table covers Realtek default IDs and adapters from Edimax, ASUS, D-Link, Linksys, TP-Link, Netgear, Hawking, LiteOn, TRENDnet, ELECOM, Mercusys, and Buffalo.
- `rtw8822bu_probe()` is a thin wrapper around `rtw_usb_probe(intf, id)`.
- `rtw_8822bu_driver` registers `.probe = rtw8822bu_probe` and `.disconnect = rtw_usb_disconnect`.
- `MODULE_DEVICE_TABLE(usb, rtw_8822bu_id_table)` and `module_usb_driver()` provide autoload and registration.

## Control Flow and Integration

USB core interface matching selects an ID entry, then `rtw8822bu_probe()` calls `rtw_usb_probe()`. The generic rtw88 USB path uses `id->driver_info` to obtain RTL8822B chip capabilities, creates the device, configures USB aggregation and endpoints, loads firmware/tables, and registers with mac80211. Disconnect calls the shared cleanup path.

## State and Persistence

The file owns a static device-ID allowlist. Runtime state is allocated by the USB transport and chip code. No suspend/resume callbacks are explicitly wired here; USB PM behavior depends on the shared `rtw_usb` layer and driver-core defaults. The static ID table is effectively persistent kernel configuration for which retail adapters bind to this module.

## Dependencies

It depends on Linux USB/module APIs and rtw88 headers `main.h`, `usb.h`, and `rtw8822b.h`. The common USB path contains transport behavior such as endpoint setup, TX/RX aggregation, and chip-specific USB quirks keyed from `rtw8822b_hw_spec`.

## Risks

- The match table is broad and uses vendor-specific interface class masks. Adding IDs without confirming the chipset can bind unrelated devices.
- Missing IDs result in supported adapters not autoloading even though the core chip support exists.
- Probe is only a wrapper, so transport regressions or chip-spec mistakes are surfaced as device bring-up failures in all matched adapters.
- Lack of local PM callbacks means runtime suspend/wake behavior should be verified in the shared USB layer.

## Test Signals

- `modinfo` should expose all intended USB aliases.
- Hotplugging each known VID/PID should call `rtw_usb_probe()` with `rtw8822b_hw_spec`.
- Functional tests should cover association, throughput, disconnect/reconnect, module unload, and autosuspend/runtime PM for representative USB2 and USB3 adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.c

## Purpose

`rtw8822c.c` is the main RTL8822C chip implementation for the rtw88 mac80211 driver. It provides chip operations, efuse parsing, PHY/MAC initialization, channel and antenna control, RF calibration, dynamic tracking, coexistence hooks, beamforming hooks, power sequences, power-tracking tables, and the exported `rtw8822c_hw_spec` consumed by PCI/USB/SDIO bus modules.

## Important APIs and Types

- Exported symbol: `const struct rtw_chip_info rtw8822c_hw_spec`.
- Chip ops table `rtw8822c_ops` implements callbacks such as `.phy_set_param`, `.read_efuse`, `.query_phy_status`, `.set_channel`, `.mac_init`, `.dump_fw_crash`, `.set_tx_power_index`, `.set_antenna`, `.false_alarm_statistics`, `.phy_calibration`, `.dpk_track`, `.pwr_track`, `.adaptivity`, `.cfo_track`, `.config_bfee`, coexistence hooks, LED control, and TX descriptor checksum filling.
- Efuse parsers split MAC-address extraction by HCI type: `rtw8822ce_efuse_parsing()`, `rtw8822cu_efuse_parsing()`, `rtw8822cs_efuse_parsing()`, with common extraction in `rtw8822c_read_efuse()`.
- Calibration families:
  - DACK: `rtw8822c_rf_dac_cal()` and helpers for ADC/DAC IQ sampling, vector backup/restore, and DCK backup.
  - TXGAPK: `rtw8822c_do_gapk()`, `rtw8822c_txgapk()`, gain-table backup/read/offset/write helpers.
  - IQK/LCK: firmware IQK via `rtw8822c_do_iqk()` and synthesizer lock calibration via `rtw8822c_do_lck()`.
  - DPK: `rtw8822c_do_dpk()`, `rtw8822c_dpk_calibrate()`, reload, coefficient capture/write, gain/loss search, thermal tracking, and `rtw8822c_parse_tbl_dpk()`.
- Dynamic behavior includes CFO tracking, CCK packet-detection threshold adjustment, EDCCA adaptivity, false-alarm statistics, power tracking, path diversity/RSSI updates, and BT coexistence GNT/RFE configuration.

## Control Flow

Device bring-up starts through a bus driver using `rtw8822c_hw_spec`. The core rtw88 flow calls `.read_efuse` to decode logical efuse data into `rtwdev->efuse`, then `.mac_init` writes MAC timing, queue, EDCA, beacon, RX filter, retry, TSF, interrupt migration, and low-power registers. `.phy_set_param` powers BB/RF domains, disables low-rate DPD, applies pre/post header-file settings around `rtw_phy_load_tables()`, writes the efuse crystal cap, configures TX/RX paths, initializes PHY state, records CCK gain-index bounds, runs RF init, initializes power tracking, and initializes beamforming PHY state.

Channel changes flow through `rtw8822c_set_channel()`: BB settings are updated for 2 GHz or 5 GHz filter/AGC/SCO/DFIR/bandwidth cases, common MAC channel settings are applied by `rtw_set_channel_mac()`, RF path A/B `RF_CFGCH` is rewritten by `rtw8822c_set_channel_rf()`, and IGI is toggled to refresh gain state.

RX descriptor processing calls `query_phy_status()`, dispatching page 0 for CCK-like status and page 1 for OFDM/HT/VHT status. These functions populate `struct rtw_rx_pkt_stat`, update RSSI/SNR/EVM/CFO fields in `rtwdev->dm_info`, feed path-diversity sums, and call `rtw_phy_parsing_cfo()`.

Periodic PHY work calls the registered chip ops for false alarm counting, CCK PD, CFO tracking, DPK tracking, EDCCA adaptivity, and power tracking. The first `rtw8822c_pwr_track()` invocation triggers RF thermal measurement; the next reads averaged thermal values, optionally runs LCK, computes swing-table deltas, and writes per-path power-index offsets.

RF calibration is explicitly staged. `rtw8822c_phy_calibration()` disables RFK power save, runs TXGAPK, firmware IQK, and DPK, then re-enables RFK power save. DPK first tries channel-based reload; otherwise it saves BB/RF registers, pauses TX, applies MAC/BB/AFE DPK tables, calibrates both paths, writes coefficients, restores RF/BB state, and refreshes RXBB DC calibration.

## State and Persistence

The driver persists chip state in `rtwdev->efuse`, `rtwdev->hal`, `rtwdev->dm_info`, `rtwdev->dm_path_div`, and `rtwdev->coex`. Important cached state includes efuse-derived crystal cap, RFE, country/channel plan, thermal meters, power-track type, TX power indexes, DACK vectors/DCK backups, TXGAPK gain tables and offsets, DPK coefficients/result bits/TXAGC/thermal deltas, CFO accumulators, CCK PD levels, false-alarm counters, and coexistence current gain/power settings.

Some state is used to avoid expensive recalibration. DACK restores backed-up MSBK/DCK values if present. DPK reloads coefficients when the current channel matches `dpk_info->dpk_ch`. TXGAPK reads all gain tables once unless the capability flag disables it. WoWLAN firmware support is conditionally advertised under `CONFIG_PM`.

## Dependencies and Integration Points

This file sits at the center of rtw88 chip integration. It depends on `main.h`, `coex.h`, `fw.h`, `tx.h`, `rx.h`, `phy.h`, `mac.h`, `reg.h`, `debug.h`, `util.h`, `bf.h`, `efuse.h`, and generated `rtw8822c_table.h` data. It calls generic helpers such as `rtw_power_on/off`, `rtw_phy_load_tables`, `rtw_phy_init`, `rtw_phy_set_edcca_th`, `rtw_phy_pwrtrack_*`, `rtw_fw_do_iqk`, `rtw_fw_inform_rfk_status`, `rtw_dump_fw`, `rtw_dump_reg`, `rtw_bf_*`, `rtw_coex_*`, and register/RF accessors.

Bus modules for RTL8822CE/CS/CU refer to `rtw8822c_hw_spec`. Core rtw88 code uses chip ID `RTW_CHIP_TYPE_8822C` for several transport quirks, and firmware code consumes DPK state for reserved pages. The exported firmware names are `rtw88/rtw8822c_fw.bin` and, with PM enabled, `rtw88/rtw8822c_wow_fw.bin`.

## Risks

- Register programming is dense and hardware-order sensitive; missing backup/restore or failed polling can leave RF paths, TX pause, CCA, or 3-wire state misconfigured.
- Several loops use hardware readiness polling with warnings rather than hard failures, so degraded RF performance can occur without probe failure.
- Efuse parsing is HCI-dependent; wrong HCI type or struct layout mismatch yields bad MAC address, RFE, thermal, or regulatory state.
- Calibration caches in `dm_info` must match channel/path/band assumptions. Reusing stale DPK/DACK/TXGAPK data can hurt EVM, power, or throughput.
- Coexistence code mutates RF path B and grant/ignore registers based on `share_ant`, `kt_ver`, 5 GHz state, and freerun state; incorrect inputs can break WiFi/BT coexistence.
- Some path loops use `<= rtwdev->hal.rf_path_num` in PHY status processing, which should be reviewed against array sizing expectations for two-path devices.
- The chip spec advertises capabilities and firmware names; incorrect flags affect mac80211 features, WoWLAN, beamforming, LDPC/STBC, aggregation, scan IE sizing, and transport buffer allocation.

## Test Signals

- Build tests should ensure `rtw8822c_hw_spec` exports and all table symbols from `rtw8822c_table.c` resolve.
- Probe logs should show successful efuse parsing, firmware load, MAC init, PHY table load, RF init, and mac80211 registration.
- RFK debug logs should be watched for DACK restore/calibration failures, IQK timeout, DPK stuck/fail messages, TXGAPK pause failures, and BT RFK handshake timeouts.
- Runtime validation should cover 2.4 GHz/5 GHz channels, 20/40/80/5/10 MHz widths where supported, antenna path changes, throughput, RSSI/EVM/SNR reporting, EDCCA behavior, CFO convergence, thermal power tracking, suspend/WoWLAN, and WiFi/BT coexistence.
- Firmware crash dump paths can be validated by checking `rtw8822c_dump_fw_crash()` dumps REG/DMEM/IMEM/EMEM/ROM segments in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.h

## Purpose

`rtw8822c.h` declares the RTL8822C chip-private efuse layouts, DPK enums, DPK table parser API, exported chip spec, PHY-status extraction macros, and a large set of chip-specific MAC/BB/RF register constants used by `rtw8822c.c` and table macros. It is the local hardware contract for RTL8822C-specific code.

## Important APIs and Types

- HCI-specific efuse sub-layouts:
  - `struct rtw8822ce_efuse` for PCIe fields, MAC address, PCI IDs, capabilities, LTR/OBFF, class code, and L1 substate support bits.
  - `struct rtw8822cu_efuse` for USB VID/PID and MAC address offset.
  - `struct rtw8822cs_efuse` for SDIO MAC address offset.
- `struct rtw8822c_efuse` is the common logical efuse map. It includes RTL ID, USB mode, four-path TX power indexes, channel plan, crystal cap, IQK/LCK byte, board/RFE/BT options, country code, path thermal values, RX gain gaps, and a union of PCIe/USB/SDIO layouts.
- `enum rtw8822c_dpk_agc_phase` and `enum rtw8822c_dpk_one_shot_action` name DPK state-machine phases and one-shot hardware actions.
- `void rtw8822c_parse_tbl_dpk(struct rtw_dev *rtwdev, const struct rtw_table *tbl)` is exported within the driver for DPK table parsing.
- `extern const struct rtw_chip_info rtw8822c_hw_spec` lets bus modules bind to the chip implementation.
- `RTW_DECL_TABLE_DPK(name)` declares a `struct rtw_table` using `rtw8822c_parse_tbl_dpk`.
- PHY status macros decode page 0/page 1 RX reports with `le32_get_bits()`.
- Register and bit definitions cover EDCCA, XCAP/CFO thresholds, TX/RX path mapping, CCK/OFDM filters, DACK, DPK, TXGAPK, RF registers, and physical efuse power/thermal trim offsets.

## Control Flow and Integration

This header has no executable control flow except macro expansion. It directly shapes `rtw8822c.c` behavior: efuse parsing casts the logical map to `struct rtw8822c_efuse`, RX status parsing uses the page macros, DPK table declarations in `rtw8822c_table.c` use `RTW_DECL_TABLE_DPK`, and calibration/channel/power functions use the register constants throughout. Bus modules include this header to reach `rtw8822c_hw_spec`.

## State and Persistence

The packed efuse structs define persistent one-time-programmed device data layout. Values read through these structs populate runtime `rtwdev->efuse` fields such as MAC address, RFE option, crystal cap, channel plan, country code, thermal meter, BT setting, regulatory domain, and TX power index table. Register constants define volatile hardware state, while DPK/DACK-related constants bound runtime cached arrays in `rtwdev->dm_info`.

## Dependencies

It depends on byte-order helpers from `<asm/byteorder.h>`, kernel bit macros, `ETH_ALEN`, and rtw88 types such as `struct rtw_txpwr_idx`, `struct rtw_dev`, `struct rtw_table`, and `struct rtw_chip_info` supplied by surrounding includes. The macros assume little-endian PHY status layout and unaligned casts to `__le32 *` matching firmware/hardware RX report format.

## Risks

- Packed efuse offsets are hardware ABI. Any padding, field order, or bitfield change can corrupt MAC address, power, PCI capability, or thermal parsing.
- PHY status macros cast raw byte pointers to `__le32 *`; callers must pass correctly aligned/valid hardware report buffers.
- Register constants are reused across calibration flows; incorrect masks can silently program unrelated bits.
- `RTW_DECL_TABLE_DPK` divides table size by triplets in the parser; table data must be exact address/mask/data triples.
- DPK and DACK constants such as path counts and backup lengths must stay consistent with `main.h` state arrays and hardware path count.

## Test Signals

- Compile coverage verifies that all constants and declarations match implementation usage.
- Efuse parsing tests on PCIe/USB/SDIO hardware should confirm correct MAC address, RFE, thermal, crystal cap, and TX power indexes.
- RX monitor/debug paths should validate decoded RSSI, channel, SNR, EVM, CFO, and bandwidth from page 0/page 1 PHY reports.
- Calibration debug logs and RF performance tests are the main signal that DPK/DACK/TXGAPK register definitions and table parser contracts remain correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c.h -->
