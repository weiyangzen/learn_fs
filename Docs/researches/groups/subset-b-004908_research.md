# Research: subset-b-004908

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c

## Purpose

This file is the generated/static PHY table payload for the Realtek RTW8821C chip in the `rtw88` wireless driver. It contains no executable control-flow functions of its own beyond table declaration macros; its job is to package MAC, AGC, BB, RF, per-rate power-group, and transmit-power-limit register data as `struct rtw_table` objects consumed by the common PHY loader.

The tables are used by `rtw8821c.c` through `rtw8821c_hw_spec`, where `.mac_tbl`, `.agc_tbl`, `.bb_tbl`, and `.rf_tbl` point at the exported table objects declared here. During `rtw8821c_phy_set_param()`, the chip powers up BB/RF domains, clears `REG_RXPSEL` reset state, calls `rtw_phy_load_tables(rtwdev)`, restores RX path selection, then continues with crystal-cap programming, `rtw_phy_init()`, power tracking, and beamforming setup. This makes the register payload here part of device bring-up rather than runtime policy.

## Important APIs, Types, and Data

- `rtw8821c_mac[]`: address/value MAC initialization pairs. The payload starts with low MAC/system registers such as `0x010`, `0x025`, queue and timing ranges around `0x420`-`0x70b`, and is declared with `RTW_DECL_TABLE_PHY_COND(rtw8821c_mac, rtw_phy_cfg_mac)`.
- `rtw8821c_agc[]`: AGC programming stream declared with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_agc)`. It contains conditional markers such as `0x80001004`, `0x90001005`, and many writes to `0x81c`, which is the AGC table load register pattern used by the Realtek table interpreter.
- `rtw8821c_agc_btg_type2[]`: alternate AGC payload for BTG/RFE type 2 layouts, also wired to `rtw_phy_cfg_agc`. Its presence matches `rtw8821c` efuse/RFE handling where BTG-capable RFE options need different gain behavior.
- `rtw8821c_bb[]`: baseband initialization stream declared with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_bb)`, including BB register writes and conditional table blocks.
- `rtw8821c_bb_pg_type0[]`: `struct rtw_phy_pg_cfg_pair` array for path/rate-group power-index programming. It is declared through `RTW_DECL_TABLE_BB_PG`.
- `rtw8821c_rf_a[]`: RF radio table for path A only, declared through `RTW_DECL_TABLE_RF_RADIO(rtw8821c_rf_a, A)`. This reflects 8821C being a single-stream chip in the associated `rtw8821c_hw_spec` (`.rf_tbl = {&rtw8821c_rf_a_tbl}`).
- `rtw8821c_txpwr_lmt_type0[]`: `struct rtw_txpwr_lmt_cfg_pair` rows declared through `RTW_DECL_TABLE_TXPWR_LMT`. Rows encode regulatory domain/rate/bandwidth/channel-group/path constraints and cap values, with `63` appearing as the common sentinel-like maximum/disabled cap value used by the table format.

The file depends on `main.h` for common driver types, `phy.h` for table macros and parser functions, and `rtw8821c_table.h` for the extern declarations that expose the generated `struct rtw_table` objects.

## Control Flow and Integration

There is no direct function call flow inside this file. The table declaration macros create named table descriptors that the driver core invokes indirectly:

1. Bus-specific modules (`rtw8821ce.c`, `rtw8821cs.c`, `rtw8821cu.c`) match a PCI/SDIO/USB device and pass `&rtw8821c_hw_spec` as driver data.
2. The common bus probe builds an `rtw_dev` whose `chip` field points to `rtw8821c_hw_spec`.
3. The common power-on sequence eventually calls `rtw8821c_ops.phy_set_param`.
4. `rtw8821c_phy_set_param()` enables BB/RF domains and calls `rtw_phy_load_tables(rtwdev)`.
5. `rtw_phy_load_tables()` follows the chip info table pointers and applies these payloads via parser callbacks such as `rtw_phy_cfg_mac`, `rtw_phy_cfg_agc`, `rtw_phy_cfg_bb`, RF radio loaders, BB power-group loaders, and transmit-power-limit loaders.

The conditional numeric records embedded in the `u32` arrays are interpreted by the PHY table engine. They are not ordinary register/value pairs exclusively; values such as `0x80001005`, `0x90000400`, `0xA0000000`, and `0xB0000000` are condition/control tokens that select chip cut, package, platform, interface, or RFE variants before applying subsequent writes.

## State and Persistence Behavior

The arrays are `static const` and persist only as read-only kernel module data. They do not hold mutable runtime state and do not allocate memory. Runtime state is created by side effects when the PHY loader writes hardware registers and RF registers. Those side effects last until hardware reset, suspend/power-off, or a later channel/RF reconfiguration rewrites overlapping registers.

Because this file is data-only, persistence risks are primarily around stale or incorrect hardware payload values. A wrong AGC/BB/RF row can survive across the active power session and manifest as poor sensitivity, broken RF path selection, bad TX power, regulatory noncompliance, or BT coexistence issues.

## Dependencies and Integration Points

- `rtw8821c.c`: consumes the generated table symbols through `rtw8821c_hw_spec`.
- `phy.h` and PHY loader code: define the table declaration macros, conditional parser format, register write helpers, and BB/RF/TX power table application routines.
- `rtw8821c_table.h`: public header for these table symbols.
- Bus glue (`rtw8821ce.c`, `rtw8821cs.c`, `rtw8821cu.c`): indirectly consumes this file by passing `rtw8821c_hw_spec` to common probe paths.
- Firmware and calibration flows: run after table load and assume these base hardware defaults are valid.

## Risks

- The file is large, generated-looking, and numeric. Review cannot infer semantic correctness from C type checking; hardware validation is required.
- Conditional table tokens must match the parser contract. A malformed token can skip rows, write rows to the wrong variant, or leave hardware partially initialized.
- `rtw8821c_agc_btg_type2_tbl` is declared but not directly referenced in the inspected `rtw8821c_hw_spec` fields. It may be selected indirectly by RFE definitions or table-loader logic; if that linkage is absent or broken, BTG type 2 devices could use the wrong gain table.
- TX power limit rows are regulatory-sensitive. Errors can cause underpowered links or illegal transmit power for a region/bandwidth/rate combination.
- RF table only covers path A. That is expected for 8821C, but any future attempt to use the file for a dual-path variant would be structurally wrong.
- Since register writes happen during bring-up before normal traffic, failures can appear as probe timeouts, silent association failures, or low throughput rather than obvious kernel errors.

## Test Signals

- Build coverage should ensure all macro-generated symbols match the externs in `rtw8821c_table.h` and the chip spec references in `rtw8821c.c`.
- Probe tests for PCI, SDIO, and USB 8821C devices should confirm `rtw_phy_load_tables()` succeeds and the firmware reaches normal operation.
- RF smoke tests should cover 2.4 GHz, 5 GHz, channel 14 if supported by regulatory configuration, and HT/VHT rates.
- RFE/BT coexistence testing should include devices whose efuse selects BTG-related RFE options to verify the alternate AGC payload is selected correctly.
- Regulatory and power tests should compare per-rate/channel TX power against expected efuse and regulatory caps.
- Suspend/resume and power-cycle tests should confirm the static tables are reapplied cleanly and no register programming order dependency is exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h

## Purpose

This header exposes the RTW8821C PHY table descriptors produced by `rtw8821c_table.c`. It is the narrow compile-time contract between the generated/static hardware data file and the executable chip implementation in `rtw8821c.c`.

## Important APIs and Types

The header declares seven `extern const struct rtw_table` symbols:

- `rtw8821c_mac_tbl`
- `rtw8821c_agc_tbl`
- `rtw8821c_agc_btg_type2_tbl`
- `rtw8821c_bb_tbl`
- `rtw8821c_bb_pg_type0_tbl`
- `rtw8821c_rf_a_tbl`
- `rtw8821c_txpwr_lmt_type0_tbl`

The only type used directly is `struct rtw_table`, supplied by the surrounding `rtw88` headers included by C files before or alongside this header. The include guard is `__RTW8821C_TABLE_H__`.

## Control Flow and Integration

This header has no runtime control flow. Its declarations allow `rtw8821c.c` to assign table pointers inside `rtw8821c_hw_spec`, while `rtw8821c_table.c` provides the definitions through `RTW_DECL_TABLE_*` macros. The common PHY loader later consumes those pointers from the chip info structure.

The exported symbols form part of this sequence:

1. `rtw8821c_table.c` defines static arrays and macro-generated `struct rtw_table` descriptors.
2. This header declares the descriptors.
3. `rtw8821c.c` includes the header and places selected descriptors in `rtw8821c_hw_spec`.
4. Bus glue drivers pass `rtw8821c_hw_spec` to common probe routines.
5. `rtw_phy_load_tables()` applies the referenced table descriptors during chip initialization.

## State and Persistence Behavior

The header declares immutable table descriptors only. It does not define mutable state, allocate resources, register devices, or persist data. The persistent effect of these declarations is ABI-like within the driver module: symbol names must remain synchronized with the table definitions and chip spec fields.

## Dependencies and Integration Points

- Definition provider: `rtw8821c_table.c`.
- Primary consumer: `rtw8821c.c`.
- Indirect consumers: PCI/SDIO/USB 8821C bus modules and common PHY loader code.
- Shared type provider: `struct rtw_table` from the `rtw88` PHY/table infrastructure.

## Risks

- If an extern declaration is removed or renamed without matching changes in `rtw8821c_table.c` and `rtw8821c.c`, the driver fails to link.
- If a table is declared here but not wired into `rtw8821c_hw_spec` or RFE selection logic, it can become dead data and hide missing hardware variant support.
- The header does not include the type definition itself, so include ordering must keep `struct rtw_table` visible where required. This matches local style but is a coupling to surrounding includes.

## Test Signals

- Kernel build/link tests are the primary signal because the header is a symbol contract.
- Static search should verify every declaration has exactly one definition and every expected table pointer in `rtw8821c_hw_spec` resolves to the intended symbol.
- Device probe tests indirectly validate the declarations by exercising table load through the chip info structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c

## Purpose

This file is the PCI bus binding module for Realtek RTW8821CE devices. It does not implement chip behavior itself; it matches PCI device IDs, passes `&rtw8821c_hw_spec` to the shared `rtw88` PCI probe path, and registers a `struct pci_driver` with standard remove, power-management, shutdown, and PCI error-recovery hooks.

## Important APIs, Types, and Functions

- `rtw_8821ce_id_table[]`: PCI ID table with Realtek vendor ID and device IDs `0xB821` and `0xC821`. Each entry stores `(kernel_ulong_t)&rtw8821c_hw_spec` in `.driver_data`.
- `MODULE_DEVICE_TABLE(pci, rtw_8821ce_id_table)`: exports aliases so module autoload can bind matching PCI hardware.
- `rtw_8821ce_driver`: `struct pci_driver` with `.name = KBUILD_MODNAME`, `.id_table = rtw_8821ce_id_table`, `.probe = rtw_pci_probe`, `.remove = rtw_pci_remove`, `.driver.pm = &rtw_pm_ops`, `.shutdown = rtw_pci_shutdown`, and `.err_handler = &rtw_pci_err_handler`.
- `module_pci_driver(rtw_8821ce_driver)`: emits module init/exit registration boilerplate.

## Control Flow

At module load, `module_pci_driver` registers the driver with the PCI core. When a matching Realtek PCI function appears, the PCI core calls `rtw_pci_probe`. The common PCI probe reads the matched ID's `driver_data` and uses the `rtw8821c_hw_spec` chip description to allocate/configure the shared `rtw_dev`, firmware, MAC/PHY tables, efuse parsing, and mac80211 integration. Removal and shutdown are delegated to the shared PCI helpers.

PCI Advanced Error Reporting or similar recovery paths enter through `rtw_pci_err_handler`, so this small file also integrates 8821CE devices into common PCI error handling.

## State and Persistence Behavior

This file owns only static module registration data. Runtime device state is allocated and managed by the common PCI and core `rtw88` layers. Persistent effects are kernel driver binding and module alias metadata. Power-management state is not stored here; suspend/resume behavior is controlled by `rtw_pm_ops` and shared chip operations.

## Dependencies and Integration Points

- Linux PCI and module frameworks: `<linux/pci.h>`, `<linux/module.h>`, `struct pci_driver`, module alias generation.
- `pci.h`: common `rtw88` PCI probe/remove/shutdown/error handlers.
- `rtw8821c.h`: declares `rtw8821c_hw_spec`.
- `rtw8821c.c` and `rtw8821c_table.c`: provide chip operations and tables selected by this bus binding.
- mac80211/cfg80211 integration occurs in shared core code after probe.

## Risks

- Incorrect or missing PCI IDs prevent module autoload or leave supported devices unbound.
- A wrong `.driver_data` pointer would bind hardware to the wrong chip description and break efuse parsing, register tables, and firmware selection.
- Because all real behavior is delegated, this file relies on shared PCI code correctly interpreting `driver_data` and handling runtime PM/error recovery for 8821CE.
- The file has no per-ID quirks; if one PCI ID requires a different RFE, firmware, or power-management workaround, it must be represented elsewhere.

## Test Signals

- `modinfo` should show PCI aliases for `10ec:b821` and `10ec:c821`.
- Boot/probe on both IDs should call `rtw_pci_probe` and load `rtw88/rtw8821c_fw.bin`.
- Suspend/resume, shutdown, and PCI error recovery tests validate the delegated hooks.
- Build tests catch signature drift in common PCI helpers or `rtw8821c_hw_spec`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c

## Purpose

This file is the SDIO bus binding module for Realtek RTW8821CS devices. It maps the SDIO vendor/device ID to `rtw8821c_hw_spec` and registers the shared `rtw88` SDIO probe, remove, shutdown, and power-management callbacks.

## Important APIs, Types, and Functions

- `rtw_8821cs_id_table[]`: SDIO ID table containing `SDIO_VENDOR_ID_REALTEK` and `SDIO_DEVICE_ID_REALTEK_RTW8821CS`, with `.driver_data = (kernel_ulong_t)&rtw8821c_hw_spec`.
- `MODULE_DEVICE_TABLE(sdio, rtw_8821cs_id_table)`: emits SDIO module aliases for autoload.
- `rtw_8821cs_driver`: `struct sdio_driver` with `.probe = rtw_sdio_probe`, `.remove = rtw_sdio_remove`, `.shutdown = rtw_sdio_shutdown`, `.id_table = rtw_8821cs_id_table`, and `.drv.pm = &rtw_sdio_pm_ops`.
- `module_sdio_driver(rtw_8821cs_driver)`: standard module registration wrapper.

## Control Flow

At module initialization, the SDIO driver is registered. The MMC/SDIO core matches Realtek RTW8821CS functions against `rtw_8821cs_id_table`, then calls `rtw_sdio_probe`. The shared SDIO probe consumes the chip spec from `driver_data` and initializes the common `rtw88` stack for 8821C: efuse parsing, firmware load, table application, queues, interrupts, and mac80211 registration.

On device removal or system shutdown, control goes to the shared SDIO helpers. Suspend/resume hooks are provided through `rtw_sdio_pm_ops` in the embedded `.drv` field.

## State and Persistence Behavior

The file stores only static ID and driver structures. It does not keep per-device runtime state. Runtime state lives in the SDIO function/device objects and common `rtw_dev` allocation created by `rtw_sdio_probe`. Persistent effects are module alias metadata and registration with the SDIO core.

## Dependencies and Integration Points

- Linux MMC/SDIO framework: `<linux/mmc/sdio_func.h>`, `<linux/mmc/sdio_ids.h>`, `struct sdio_driver`.
- `sdio.h`: shared `rtw88` SDIO bus implementation.
- `main.h` and `rtw8821c.h`: core types and chip spec declaration.
- `rtw8821c.c` and `rtw8821c_table.c`: chip behavior, firmware name, table pointers, and efuse parser used after probe.

## Risks

- Missing or incorrect SDIO ID prevents automatic binding on embedded/mobile platforms.
- Wrong chip-spec driver data would misconfigure firmware, efuse parsing, and hardware table loading.
- SDIO power sequencing and host quirks are delegated entirely to shared code; this binding has no local quirk table for boards that require special handling.
- Device-tree or ACPI integration issues may appear outside this file even when the SDIO ID is correct.

## Test Signals

- `modinfo` should expose an SDIO alias for the Realtek RTW8821CS device ID.
- Probe testing on an SDIO 8821CS board should reach `rtw_sdio_probe`, load the 8821C firmware, and register a wireless PHY.
- Runtime PM and system suspend/resume are important because SDIO devices are often power-gated by platform firmware.
- Basic association/throughput tests across 2.4 GHz and 5 GHz confirm the common 8821C chip path works through the SDIO transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c

## Purpose

This file is the USB bus binding module for RTW8821CU-family USB adapters. It declares the supported USB vendor/product/interface matches, forwards matching interfaces to the shared `rtw88` USB probe path, and registers disconnect handling.

## Important APIs, Types, and Functions

- `rtw_8821cu_id_table[]`: USB match table using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for vendor-specific interfaces. Most entries use `RTW_USB_VENDOR_ID_REALTEK`; additional third-party entries include D-Link (`0x2001:0x331d`), Edimax (`0x7392:0xc811`, `0x7392:0xd811`), and Mercusys (`0x2c4e:0x0105`). All entries set `.driver_info = (kernel_ulong_t)&rtw8821c_hw_spec`.
- `MODULE_DEVICE_TABLE(usb, rtw_8821cu_id_table)`: exports USB aliases for autoload.
- `rtw_8821cu_probe()`: thin wrapper that calls `rtw_usb_probe(intf, id)`.
- `rtw_8821cu_driver`: `struct usb_driver` with `.probe = rtw_8821cu_probe`, `.disconnect = rtw_usb_disconnect`, and `.id_table = rtw_8821cu_id_table`.
- `module_usb_driver(rtw_8821cu_driver)`: standard USB driver registration wrapper.

## Control Flow

When the module loads, it registers with the USB core. A matching vendor-specific USB interface triggers `rtw_8821cu_probe`, which delegates directly to `rtw_usb_probe`. The common USB probe reads `id->driver_info`, selects `rtw8821c_hw_spec`, creates the `rtw_dev`, configures USB transport resources, loads firmware, parses efuse, applies tables, and registers mac80211 state. Disconnect events go to `rtw_usb_disconnect`.

The local probe wrapper exists mostly to satisfy the expected USB probe signature and keep the ID table associated with the shared USB implementation.

## State and Persistence Behavior

The file contains static USB ID and driver metadata. It does not maintain runtime state or persistent configuration. Per-device state is owned by USB core structures and the common `rtw88` USB layer after probe. The module's persistent user-visible effect is the USB modalias list, which controls autoloading for many branded adapters.

## Dependencies and Integration Points

- Linux USB and module frameworks: `<linux/usb.h>`, `<linux/module.h>`.
- `usb.h`: shared `rtw88` USB probe/disconnect implementation and `RTW_USB_VENDOR_ID_REALTEK`.
- `main.h` and `rtw8821c.h`: common driver types and the 8821C chip spec.
- `rtw8821c.c` and `rtw8821c_table.c`: executable chip behavior and hardware table payloads used after probe.

## Risks

- USB ID coverage is product-facing. Missing IDs mean otherwise compatible adapters do not bind; incorrect IDs could bind an incompatible Realtek part to the 8821C chip spec.
- Vendor-specific interface matching (`0xff/0xff/0xff`) is broad at the interface class level, so product/vendor IDs must be precise.
- No local suspend/resume hooks are provided in this `struct usb_driver`; any runtime or system PM support depends on shared USB-layer registration and kernel USB defaults.
- The wrapper does not inspect interface altsettings or endpoints; endpoint validation must be done by `rtw_usb_probe`.

## Test Signals

- `modinfo` should list all USB aliases in the table, including branded D-Link, Edimax, and Mercusys IDs.
- Hotplug tests for representative Realtek and third-party IDs should trigger `rtw_usb_probe` and load `rtw88/rtw8821c_fw.bin`.
- Disconnect/replug stress should validate `rtw_usb_disconnect` cleanup.
- Traffic tests over USB 2 and USB 3 hosts should confirm endpoint setup, aggregation, and firmware operation through the shared USB transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.c

## Purpose

This file is the main RTW8822B chip implementation for the `rtw88` driver. It provides efuse parsing, MAC/PHY/RF initialization, channel and antenna programming, RX PHY status parsing, TX power index programming, power tracking, IQ calibration, Bluetooth coexistence hooks, beamforming hooks, EDCCA adaptivity, LED control, power-sequence tables, interface PHY parameter tables, coexistence policy tables, and the exported `rtw8822b_hw_spec` consumed by PCI/USB/SDIO bus modules.

Unlike the small bus binding files, this file is the central behavior and hardware contract for all 8822B transports. It connects the common `rtw88` core to chip-specific register addresses, firmware name `rtw88/rtw8822b_fw.bin`, table symbols from `rtw8822b_table.c`, efuse map layout from `rtw8822b.h`, and coexistence/power tracking policy data.

## Important APIs, Types, and Functions

- Efuse parsing:
  - `rtw8822b_read_efuse()` maps the logical efuse buffer to `struct rtw8822b_efuse`, copies RF/RFE/crystal/channel/country/thermal/TX power fields into `rtwdev->efuse`, copies four TX power index tables, and dispatches MAC address parsing by HCI type.
  - `rtw8822be_efuse_parsing()`, `rtw8822bu_efuse_parsing()`, and `rtw8822bs_efuse_parsing()` select the bus-specific MAC address location in the efuse union.
- PHY bring-up:
  - `rtw8822b_phy_set_param()` enables BB/RF domains, clears RX path reset, calls `rtw_phy_load_tables()`, applies crystal cap, restores RX path reset, configures TX/RX paths, calls `rtw_phy_init()`, initializes RFE, power tracking, and beamforming.
  - `rtw8822b_phy_rfe_init()` programs top mux and RFE input/output selections.
  - `rtw8822b_phy_bf_init()` delegates to `rtw_bf_phy_init()` and programs grouping bitmap register `0x1C94`.
- MAC initialization:
  - `rtw8822b_mac_init()` writes protocol, EDCA, beacon, WMAC RX filter, packet size, TCR, and VHT SIG-B CRC-check settings.
- Channel/RF/RFE setup:
  - `rtw8822b_set_channel()` coordinates BB, MAC, RF, RX DFIR, IGI toggle, CCA, and RFE switching.
  - `rtw8822b_set_channel_bb()` handles 2 GHz/5 GHz BB settings, CCK enable/disable, RX CCA mask, clock tracking, ADC clock, primary channel index, and 5/10/20/40/80 MHz bandwidth programming.
  - `rtw8822b_set_channel_rf()` programs RF register `0x18` for band/channel/bandwidth and RF register `RF_MALSEL` using low/middle/high 5 GHz band lookup tables.
  - `rtw8822b_set_channel_cca()` selects CCA thresholds from `struct cca_ccut` tables based on RFE type, band, RX path count, channel width, cut version, and efuse RFE option.
  - `rtw8822b_set_channel_rfe_efem()` and `rtw8822b_set_channel_rfe_ifem()` program RFE selection/inversion/TRSW for external/internal FEM layouts.
  - `rtw8822b_config_trx_mode()` programs BB path selection, TX/RX path registers, MRC/ANTWT controls, RF mode table contents, and reapplies CCA/RFE settings.
- RX status:
  - `query_phy_status()` dispatches PHY status page 0 or page 1.
  - `query_phy_status_page0()` handles CCK/single-antenna status, deriving RX power, RSSI, bandwidth, signal power, and dynamic-management RSSI.
  - `query_phy_status_page1()` handles OFDM/HT/VHT two-path status, derives bandwidth from RXSC/RF mode, stores RX power/RSSI/EVM/SNR/CFO into `pkt_stat` and `dm_info`.
- TX power and antenna:
  - `rtw8822b_set_tx_power_index()` writes per-rate TX AGC indexes to path-specific TXAGC register windows at `0x1d00` and `0x1d80`.
  - `rtw8822b_set_antenna()` validates `BB_PATH_A`, `BB_PATH_B`, or `BB_PATH_AB`, updates `hal->antenna_tx/rx`, and reconfigures hardware if powered on.
- Calibration and dynamic management:
  - `rtw8822b_false_alarm_statistics()` reads CCK/OFDM/HT/VHT counters into `dm_info` and toggles reset bits for the next sampling period.
  - `rtw8822b_do_iqk()` asks firmware to run IQK, polls RF path A `RF_DTXLOK` for completion marker `0xabcde`, clears it, reads fail/reload status, and logs diagnostics.
  - `rtw8822b_pwr_track()` alternates thermal measurement trigger and application of power tracking. `rtw8822b_phy_pwrtrack()` averages thermal state, updates per-path delta power indexes, and triggers IQK when needed.
  - `rtw8822b_txagc_swing_offset()` and `rtw8822b_pwrtrack_set_pwr()` split thermal compensation between TXAGC offset and OFDM swing table programming.
- Bluetooth coexistence:
  - `rtw8822b_coex_cfg_init()`, `rtw8822b_coex_cfg_ant_switch()`, `rtw8822b_coex_cfg_rfe_type()`, `rtw8822b_coex_cfg_wl_tx_power()`, and `rtw8822b_coex_cfg_wl_rx_gain()` are chip-specific callbacks referenced by `rtw8822b_ops`.
  - Coexistence table arrays include shared/non-shared antenna decision tables, TDMA parameters, RSSI steps, RF parameters, 5 GHz AFH maps, and hardware-register dump definitions.
- Other hooks:
  - `rtw8822b_adaptivity_init()` and `rtw8822b_adaptivity()` program EDCCA thresholds and source/decision behavior.
  - `rtw8822b_led_set()` maps LED brightness to `REG_LED_CFG` software-control bits.
  - `rtw8822b_fill_txdesc_checksum()` calculates the first 32 bytes/16 words of TX descriptor checksum.
  - `rtw8822b_bf_config_bfee()` routes SU/MU beamformee enable/disable to common beamforming helpers.
- Exported chip spec:
  - `rtw8822b_ops`: `struct rtw_chip_ops` vtable for common core callbacks.
  - `rtw8822b_hw_spec`: exported `struct rtw_chip_info` with descriptor sizes, efuse sizes, FIFO sizes, firmware name, supported bands/features, table pointers, RFE definitions, coexistence configuration, EDCCA thresholds, and FIFO addresses.

## Control Flow

The primary lifecycle flow is:

1. A bus module such as `rtw8822be.c`, `rtw8822bu.c`, or `rtw8822bs.c` matches hardware and passes `&rtw8822b_hw_spec` to the common bus probe.
2. Common probe allocates `rtw_dev`, loads firmware named by `.fw_name`, reads efuse, and calls `.read_efuse = rtw8822b_read_efuse`.
3. Power-on uses `.pwr_on_seq = card_enable_flow_8822b`, which chains `trans_carddis_to_cardemu_8822b` then `trans_cardemu_to_act_8822b`.
4. PHY setup calls `rtw8822b_phy_set_param()`, which powers BB/RF, loads hardware tables, configures crystal and paths, initializes common PHY, RFE, thermal tracking, and beamforming.
5. MAC setup calls `rtw8822b_mac_init()` to establish aggregation, EDCA, beacon, RX filter, and WMAC defaults.
6. Channel changes call `rtw8822b_set_channel()`, which applies BB/MAC/RF/DFIR/IGI/CCA/RFE changes in a fixed order.
7. RX interrupt/NAPI processing supplies PHY status blobs to `.query_phy_status`, which updates packet stats and dynamic-management state used by rate/power/adaptivity logic.
8. Periodic dynamic-management work invokes false alarm statistics, adaptivity, power tracking, and possibly IQK.
9. Coexistence state machines call the coex callbacks and table data through the chip ops/spec.
10. Power-off uses `.pwr_off_seq = card_disable_flow_8822b`, chaining `trans_act_to_cardemu_8822b` and `trans_cardemu_to_carddis_8822b`.

## State and Persistence Behavior

The file mutates several core runtime state areas:

- `rtwdev->efuse`: populated from logical efuse fields, including RFE option, board option, crystal cap, country code, thermal meter, BT setting, regulatory domain bits, and TX power index tables.
- `rtwdev->hal`: antenna path choices, current channel/bandwidth, RF path count/type, cut version, and other chip-level runtime fields are read or updated by channel/antenna logic.
- `rtwdev->dm_info`: dynamic management state for default OFDM swing index, thermal moving averages, delta power indexes, RSSI/SNR/CFO/EVM, false alarm counters, EDCCA mode/thresholds, power-tracking trigger state, and current TX/RX rate.
- `rtwdev->coex`: coexistence current switch status, RFE module type, antenna switch flags, current WL power level, and RX low-gain state.
- Hardware registers and RF registers: almost every function writes persistent device state that remains until later reconfiguration, reset, suspend, or power-off.

Static arrays, power sequences, coexistence tables, power tracking tables, and chip info are read-only module data. IQK uses a static `do_iqk_cnt` counter for logging across invocations.

## Dependencies and Integration Points

- Common `rtw88` core headers: `main.h`, `fw.h`, `tx.h`, `rx.h`, `phy.h`, `mac.h`, `reg.h`, `debug.h`, `bf.h`, `regd.h`, and `coex.h`.
- Table payloads: `rtw8822b_table.h` symbols wired into `rtw8822b_hw_spec`.
- Firmware: `MODULE_FIRMWARE("rtw88/rtw8822b_fw.bin")`; IQK also uses `rtw_fw_do_iqk()`.
- Bus modules: PCI/USB/SDIO 8822B wrappers bind device IDs to `rtw8822b_hw_spec`.
- Linux LED class: `struct led_classdev` callback uses `container_of` to recover `rtw_dev`.
- mac80211 rate/band definitions: chip spec advertises HT/VHT, LDPC, AMPDU density, max scan IE length, and beamforming capacities.
- Regulatory layer: power tracking calls `rtw_regd_get()` and TX power table lookup uses regulatory/channel/bandwidth inputs.

## Risks

- RFE option handling is sparse. `rtw8822b_rfe_info[]` and `rtw8822b_rfe_defs[]` define entries for options 2, 3, and 5. `rtw8822b_set_channel()` and `rtw8822b_config_trx_mode()` only check that the option is within array bounds; a zero-filled in-bounds unsupported option would leave `rtw_set_channel_rfe` NULL and can crash if reached. Correct efuse/RFE validation elsewhere is therefore critical.
- `query_phy_status_page1()` loops with `path <= rtwdev->hal.rf_path_num`; most path loops in this file use `< rf_path_num`. If arrays are sized exactly to the path count, this is a bounds risk and should be covered by review or tests.
- `phy_para_table_8822b.n_usb3_para` is assigned `ARRAY_SIZE(usb2_param_8822b)` rather than `ARRAY_SIZE(usb3_param_8822b)`. The current arrays both have one entry, so behavior is unchanged today, but this is fragile if USB3 parameters grow.
- Channel programming has multiple hardware-specific tables and special cases (`channel == 144`, 5/10 MHz modes, RFE option 2/3 BW80 handling). Regressions can be band- or bandwidth-specific.
- IQK polling waits up to 300 * 20 ms and only logs diagnostics after firmware-driven calibration. Firmware or RF failures can add long delays.
- TX power and EDCCA/adaptivity code affects regulatory behavior. Bad thresholds or power indexes can cause noncompliance, poor range, or over-conservative channel access.
- Bluetooth coexistence code has many cached "current" states that skip redundant writes. If cache state desynchronizes from hardware after reset or firmware events, coexistence behavior may be wrong until reinitialized.
- Power sequence arrays are transport-specific and cut-specific. Incorrect mask/address/value tuples can break only one bus or one chip cut, making broad test coverage necessary.

## Test Signals

- Build and modpost should confirm `rtw8822b_hw_spec` exports and all table symbols resolve.
- Probe tests should cover PCI, USB, and SDIO 8822B modules, confirming efuse MAC address selection for each HCI type.
- Channel tests should cover 2.4 GHz, 5 GHz low/mid/high bands, channel 144, 20/40/80 MHz, and 5/10 MHz monitor or special modes if supported.
- RFE coverage should include efuse options 2, 3, and 5, plus negative validation for unsupported in-range options.
- RX status tests should validate CCK page 0 and OFDM/HT/VHT page 1 parsing, including path count bounds and RSSI/SNR/EVM/CFO updates.
- Thermal/power tracking tests should exercise trigger/apply alternation, swing-index bounds, TXAGC offset clamping, and IQK threshold behavior.
- Bluetooth coexistence tests should cover shared and non-shared antenna configurations, antenna switch control modes, WL TX power reduction, WL RX low-gain toggling, and 5 GHz AFH mapping.
- Suspend/resume and reset recovery should verify power sequences, cached coex states, and table reloading restore hardware deterministically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.h

## Purpose

This header defines the RTW8822B chip-specific public contract needed by `rtw8822b.c` and its bus binding modules. It contains the efuse layout structures for USB/PCIe/SDIO variants, helper macros for mirrored BB register writes and PHY status decoding, register address constants used by the chip implementation, EDCCA constants, and the exported `rtw8822b_hw_spec` declaration.

## Important APIs, Types, and Macros

- `RCR_VHT_ACK`: receive configuration bit for VHT ACK handling.
- `struct rtw8822bu_efuse`: USB-specific logical efuse tail layout, including USB optional function, serial/vendor/device strings, VID/PID bytes, MAC address at offset `0x107`, and package type.
- `struct rtw8822be_efuse`: PCIe-specific logical efuse tail layout, including MAC address at offset `0xd0`, PCI IDs, PM/LTR/MSI/link fields, OBFF fields, class code, and L1 substate support bitfields.
- `struct rtw8822bs_efuse`: SDIO-specific logical efuse tail layout with MAC address at offset `0x11a`.
- `struct rtw8822b_efuse`: common logical efuse map with RTL ID, USB mode, four RF-path TX power index tables, channel plan, crystal and thermal calibration, PA/LNA/RFE/BT/country fields, and a union of bus-specific tails.
- `_rtw_write32s_mask()`: inline helper that writes the same masked value to `addr` and `addr + 0x200`, matching the mirrored layout of BB register ranges `0xC00-0xCFF` and `0xE00-0xEFF`.
- `rtw_write32s_mask(...)`: wrapper macro with `BUILD_BUG_ON` range checking for compile-time constant addresses in `0xC00-0xCFF`.
- PHY status macros:
  - `GET_PHY_STAT_P0_PWDB`
  - `GET_PHY_STAT_P1_PWDB_A/B`
  - `GET_PHY_STAT_P1_RF_MODE`
  - `GET_PHY_STAT_P1_L_RXSC`
  - `GET_PHY_STAT_P1_HT_RXSC`
  - `GET_PHY_STAT_P1_RXEVM_A/B`
  - `GET_PHY_STAT_P1_CFO_TAIL_A/B`
  - `GET_PHY_STAT_P1_RXSNR_A/B`
- EDCCA constants: `RTW8822B_EDCCA_MAX`, `RTW8822B_EDCCA_SRC_DEF`.
- Register constants: chip-specific BB/RF/MAC register offsets such as `REG_HTSTFWT`, `REG_RXCCAMSK`, `REG_L1WT`, `REG_EDCCA_*`, `REG_CDDTXP`, `REG_ACBB*`, `REG_TXDFIR`, `REG_TRSW`, `REG_RFESEL*`, `REG_RFECTL`, `REG_RFEINV`, `REG_ANTWT`, and `REG_IQKFAILMSK`.
- `extern const struct rtw_chip_info rtw8822b_hw_spec`: chip descriptor exported by `rtw8822b.c` and used by 8822B bus modules.

All efuse structures are `__packed`, which is required because the code casts the logical efuse byte map directly to `struct rtw8822b_efuse`.

## Control Flow and Integration

The header itself has no standalone runtime flow, but its definitions are active in several flows:

1. Efuse read flow casts the logical efuse buffer to `struct rtw8822b_efuse`, then reads common fields and a bus-specific union member according to `rtw_hci_type(rtwdev)`.
2. Channel and antenna configuration use `rtw_write32s_mask()` to program mirrored path-A/path-B BB register windows with one call.
3. RX processing passes raw PHY status bytes to macros here so `rtw8822b.c` can extract RSSI, bandwidth, EVM, CFO, and SNR fields.
4. EDCCA/adaptivity and channel setup use the register constants here to avoid raw addresses in some of the implementation.
5. PCI/USB/SDIO binding files include this header, or a bus-specific wrapper includes it, to reference `rtw8822b_hw_spec`.

## State and Persistence Behavior

The header defines layout and constants rather than owning runtime state. Its packed structures describe persistent efuse contents programmed on the device. The inline write helper mutates hardware registers when called, but it does not store software state. PHY status macros are read-only extraction helpers over RX descriptor/status memory supplied by the hardware.

Because efuse layouts are cast directly from bytes, field offsets are effectively persistent ABI with the hardware/firmware format. Any structure layout change has immediate runtime consequences.

## Dependencies and Integration Points

- `<asm/byteorder.h>` and `le32_get_bits()` are used for little-endian PHY status extraction.
- Common driver types such as `struct rtw_dev`, `struct rtw_txpwr_idx`, and `struct rtw_chip_info` are expected from including C files and shared headers.
- `rtw8822b.c` is the main consumer of efuse structures, register constants, PHY status macros, and mirrored-write helper.
- 8822B bus modules consume `rtw8822b_hw_spec` to bind matching hardware.

## Risks

- Packed bitfields in `struct rtw8822be_efuse` are compiler-layout-sensitive even though this is common kernel style for hardware maps. The surrounding `__packed` and byte-sized fields reduce but do not eliminate maintenance risk.
- Direct casts from `u8 *log_map` to `struct rtw8822b_efuse *` require the logical map size and offsets to match exactly.
- PHY status macros cast `u8 *` to `__le32 *`; callers must provide sufficiently sized and suitably accessible status buffers. On strict-alignment architectures, this pattern relies on kernel/architecture support for the access pattern used here.
- `rtw_write32s_mask()` only enforces the address range at compile time for constant addresses. Non-constant misuse may not get the intended `BUILD_BUG_ON` protection.
- Register constants are shared hardware knowledge. A wrong address or mask silently misprograms hardware rather than causing a C-level failure.

## Test Signals

- Build tests catch missing type visibility, broken macro syntax, and unresolved `rtw8822b_hw_spec`.
- Efuse parsing tests or hardware probe logs should confirm MAC addresses are read correctly for PCIe, USB, and SDIO variants.
- RX status tests should validate each macro against known hardware status bytes for page 0 and page 1.
- Channel/RFE tests indirectly validate mirrored-write helper behavior because path-A/path-B register windows must remain synchronized.
- Static layout checks would be useful for efuse offsets if available, especially around bus-specific MAC address fields and PCIe bitfields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b.h -->
