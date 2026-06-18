# subset-b-004907 Research

This grouped report covers the rtw88 Realtek 8814A, 8821A, and 8821C files listed for subset B. Each source file has its own source-tree-aligned section bounded by the reconciliation markers used to split this grouped document into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.h

## Purpose

`rtw8814a_table.h` is the declaration surface for the RTL8814A static hardware tables consumed by the rtw88 chip profile in `rtw8814a.c`. It does not implement logic; it names the MAC, AGC, BB, RF, transmit-power-limit, power-tracking, and power-sequence data objects that are defined in the matching table source and selected through `struct rtw_chip_info`.

## Important APIs, Types, And Data

The header exports `struct rtw_table` instances for common initialization tables (`rtw8814a_mac_tbl`, `rtw8814a_agc_tbl`, `rtw8814a_bb_tbl`), multiple RFE-specific BB power-group tables (`rtw8814a_bb_pg_tbl` and type0/type2/type3/type4/type5/type7/type8 variants), four RF path tables (`rtw8814a_rf_a_tbl` through `rtw8814a_rf_d_tbl`), and multiple regulatory/RFE-specific transmit-power-limit tables. It also exports `struct rtw_pwr_track_tbl` instances for the default and typed power-tracking curves plus `card_disable_flow_8814a[]` and `card_enable_flow_8814a[]`.

## Control Flow

There is no runtime control flow in this file. The important flow is link-time and initialization-time wiring: `rtw8814a.c` includes this header, builds an RFE definition table from these symbols, and passes the selected tables to shared PHY setup helpers through `rtw_chip_info`.

## State And Persistence Behavior

The declared objects are immutable calibration/configuration data. When consumed by PHY and power-sequence loaders, they cause persistent hardware register writes until reset, power transition, channel change, or another table/application path overwrites those registers.

## Dependencies And Integration Points

The declarations require prior visibility of `struct rtw_table`, `struct rtw_pwr_track_tbl`, and `struct rtw_pwr_seq_cmd`, supplied by common rtw88 headers in including translation units. Integration is with `rtw_phy_load_tables()`, RFE selection, transmit-power limit calculation, thermal power tracking, and chip power-on/off sequence parsing.

## Risks And Test Signals

The main risk is declaration/data skew: missing definitions or wrong table-to-RFE mapping will fail link or silently program inappropriate RF values. Build tests should catch unresolved symbols. Hardware smoke tests should confirm probe, firmware load, RF path initialization across four paths, RFE option selection, regulatory power limits, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814ae.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814ae.c

## Purpose

`rtw8814ae.c` is the PCIe bus binding for RTL8814AE devices. It binds Realtek PCI device ID `0x8813` to the common RTL8814A chip description and delegates all operational work to the rtw88 PCI core.

## Important APIs, Types, And Functions

The file defines `rtw_8814ae_id_table[]`, where the single concrete `PCI_DEVICE(PCI_VENDOR_ID_REALTEK, 0x8813)` entry stores `&rtw8814a_hw_spec` in `driver_data`. It registers the table with `MODULE_DEVICE_TABLE(pci, ...)`. The `struct pci_driver rtw_8814ae_driver` uses `KBUILD_MODNAME` as its name and points `.probe`, `.remove`, `.shutdown`, and `.driver.pm` at shared rtw88 PCI functions: `rtw_pci_probe`, `rtw_pci_remove`, `rtw_pci_shutdown`, and `rtw_pm_ops`. `module_pci_driver()` supplies the module init/exit boilerplate.

## Control Flow

On PCI enumeration, the kernel matches device ID `0x8813`, loads this module, and calls `rtw_pci_probe()`. The common probe path retrieves `driver_data`, interprets it as the chip specification, allocates the rtw88 device, initializes PCI resources, then drives the chip callbacks from `rtw8814a_hw_spec`. Removal, shutdown, and system power transitions go through the common PCI layer.

## State And Persistence Behavior

This file keeps no runtime state beyond static registration data. Persistent side effects are kernel driver registration and module alias generation. Hardware state is owned by the shared PCI core and the RTL8814A chip operations reached through `rtw8814a_hw_spec`.

## Dependencies And Integration Points

The file depends on Linux PCI/module infrastructure, `pci.h` for rtw88 PCI entry points, and `rtw8814a.h` for the chip-info symbol. It integrates with modalias autoloading, PCI power management, and the rtw88 core's bus-independent chip setup.

## Risks And Test Signals

Incorrect `driver_data` would bind the device to the wrong chip profile; an incorrect ID table would prevent autoload or bind unrelated devices. Test signals are module build, `modinfo` PCI aliases, probe on `10ec:8813`, suspend/resume, shutdown, and clean remove without leaving PCI resources or IRQs active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814ae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814au.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814au.c

## Purpose

`rtw8814au.c` is the USB bus binding for RTL8814AU-family adapters. It declares the supported USB VID/PID list and routes matching devices into the generic rtw88 USB probe path with the RTL8814A hardware specification.

## Important APIs, Types, And Functions

The key data object is `rtw_8814au_id_table[]`, a `struct usb_device_id` array using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for Realtek and partner devices. Each entry stores `&rtw8814a_hw_spec` in `.driver_info`. The module exports the table through `MODULE_DEVICE_TABLE(usb, ...)`. `struct usb_driver rtw_8814au_driver` supplies `.probe = rtw_usb_probe` and `.disconnect = rtw_usb_disconnect`, and `module_usb_driver()` registers it.

## Control Flow

When a matching USB interface appears, the USB core invokes `rtw_usb_probe()`. The shared rtw88 USB layer reads `driver_info`, attaches the RTL8814A chip profile, sets up endpoints and aggregation policy, and then executes common chip initialization. Disconnect unwinds through `rtw_usb_disconnect()`.

## State And Persistence Behavior

The file has only static device-match and driver-registration state. Device runtime state, URBs, endpoint queues, firmware state, and hardware registers live in the rtw88 USB and chip layers. The USB IDs determine which devices persistently autoload this module via generated modaliases.

## Dependencies And Integration Points

Dependencies are Linux USB/module APIs, `main.h`, `usb.h`, and `rtw8814a.h`. Integration points are USB modalias matching, common rtw88 USB transport setup, RTL8814A register/table initialization, firmware loading, and disconnect cleanup.

## Risks And Test Signals

The class/subclass/protocol wildcard style can bind vendor-specific wireless interfaces broadly for listed VID/PID pairs, so ID accuracy matters. Test signals include `modinfo` USB aliases, probe on each listed Realtek/vendor adapter, endpoint detection for two/three/four bulk-out variants, firmware download, traffic under USB suspend/resume, and disconnect during active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814au.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.c

## Purpose

`rtw8821a.c` implements the RTL8821A/RTL8811A chip profile for rtw88. It supplies chip operations, IQK calibration, RX PHY status handling, LED control, transmit descriptor checksum handling, Bluetooth coexistence hooks, page/RQPN tables, RFE definitions, coexistence tables, and the exported `rtw8821a_hw_spec` consumed by USB and other bus glue.

## Important APIs, Types, And Functions

`rtw8821a_ops` is the central callback table. It reuses many 88xxA common helpers (`rtw88xxa_power_on`, `rtw88xxa_read_efuse`, `rtw88xxa_set_channel`, `rtw88xxa_set_tx_power_index`, `rtw88xxa_false_alarm_statistics`, `rtw88xxa_phy_cck_pd_set`) and provides local implementations for power-off, PHY status, calibration, power tracking, LED control, TX descriptor checksum, and coexistence setup.

The IQK path is the most substantial local logic. `rtw8821a_do_iqk()` backs up MAC/BB/AFE/RF registers, calls common MAC preparation, runs `rtw8821a_iqk()`, and restores state. `rtw8821a_iqk()` performs three calibration attempts, configures path-A LOK, TX IQK, optional VDF handling for 80 MHz, RX IQK, averages successful results through `rtw88xxa_iqk_finish()`, and writes final TX/RX imbalance values. `rtw8821a_pwr_track()` uses a trigger/read two-phase thermal-meter sequence and calls `rtw88xxa_phy_pwrtrack()` with `rtw8821a_do_iqk` as the recalibration callback.

`rtw8821a_hw_spec` declares firmware `rtw88/rtw8821a_fw.bin`, descriptor sizes, efuse sizes, FIFO sizes, 2.4/5 GHz support, VHT/HT support, USB aggregation settings, power sequences, table pointers from `rtw8821a_table.c`, coexistence parameters, and debug register domains.

## Control Flow

Bus modules pass `rtw8821a_hw_spec` to rtw88 probe. Common bring-up powers the chip, reads efuse with the 88xxA parser, loads MAC/AGC/BB/RF tables, applies RFE power tables, downloads firmware, and invokes chip ops as needed. RX processing calls `rtw8821a_query_phy_status()`, which delegates to `rtw88xxa_query_phy_status()` with the local CCK LNA/VGA power calculator. Periodic dynamic management calls `rtw8821a_pwr_track()`; the first pass triggers RF thermal measurement and the next pass reads/adjusts.

## State And Persistence Behavior

Runtime state lives in shared `struct rtw_dev`, especially `rtwdev->hal`, `rtwdev->efuse`, `rtwdev->dm_info`, and `rtwdev->coex`. This file persistently writes RF/BB/MAC registers during IQK, coexistence antenna switching, LED updates, and power tracking. IQK carefully backs up and restores selected registers, but the final calibration coefficients are intentionally left in hardware. `rtw8821a_coex_cfg_wl_tx_power()` updates only `coex_dm->cur_wl_pwr_lvl` for non-shared antenna cases; receive-gain and grant-debug hooks are no-ops.

## Dependencies And Integration Points

The file depends on rtw88 core headers (`main.h`, `coex.h`, `phy.h`, `reg.h`, `tx.h`), 88xxA shared routines, and static tables declared in `rtw8821a_table.h`. It integrates with USB binding through `rtw8821au.c`, firmware loading through `MODULE_FIRMWARE`, mac80211 LED class support, the rtw88 coexistence engine, and common transmit descriptor checksum code.

## Risks And Edge Cases

The IQK implementation contains explicit overrides where readiness and TX failure reads are forced to success after comments about original bitwise-not checks looking like typos. That can mask hardware calibration failures and should be validated against real devices. The calibration path is register-heavy, single-path, and bandwidth/RFE dependent. Empty hooks (`cfg_ldo25`, coex grant debug/fix, RX gain) may be intentional but are coverage gaps. Coexistence tables were copied from 8821C with a documented TDMA byte change to avoid A2DP/PAN confusion, so Bluetooth audio behavior is a key regression area.

## Test Signals

Useful signals include probe with `rtw8821a_fw.bin`, efuse parsing through common 88xxA code, MAC/BB/RF table load, CCK and OFDM RSSI correctness, channel changes across 2.4/5 GHz and 20/40/80 MHz, IQK debug logs and final coefficients, thermal tracking trigger/read alternation, LED on/off polarity, USB TX descriptor checksums, Bluetooth coexistence antenna phases, A2DP stability, suspend/resume power-off through `enter_lps_flow_8821a`, and operation under shared and non-shared antenna efuse settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.h

## Purpose

`rtw8821a.h` is the minimal public chip-profile header for RTL8821A/RTL8811A support. It exposes the `rtw8821a_hw_spec` symbol so bus-specific modules can bind devices to the chip implementation in `rtw8821a.c`.

## Important APIs, Types, And Functions

The single API is `extern const struct rtw_chip_info rtw8821a_hw_spec;`. That object contains operation callbacks, firmware name, descriptor and FIFO sizing, PHY table pointers, RFE definitions, coexistence parameters, and power-sequence pointers.

## Control Flow

There is no executable flow. USB glue includes this header and stores `&rtw8821a_hw_spec` in USB match-table `driver_info`; common probe later recovers the pointer and drives the full rtw88 chip setup from it.

## State And Persistence Behavior

The header stores no state. It defines a compile-time contract around an immutable chip-info object whose callbacks and table pointers cause hardware state changes when invoked by rtw88 core paths.

## Dependencies And Integration Points

The including file must already have `struct rtw_chip_info` visible through rtw88 core headers. Integration is primarily with `rtw8821au.c` and any other future bus binding that supports RTL8821A-compatible devices.

## Risks And Test Signals

The risk is symbol or type visibility mismatch: missing `rtw8821a.c` in the build, a stale declaration, or an include-order issue breaks module compilation or linking. Test signals are allmodconfig/module builds and successful bus module probe using the exported chip-info pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.c

## Purpose

`rtw8821a_table.c` contains the static register, calibration, power-sequence, transmit-power-limit, and thermal power-tracking data for RTL8821A/RTL8811A. It is data-heavy by design: the rtw88 core interprets these arrays through table-declaration macros and applies them during chip initialization, power transitions, channel/RFE setup, and dynamic power tracking.

## Important APIs, Types, And Data

The file defines raw MAC, AGC, BB, and RF-A arrays and converts them into exported `struct rtw_table` objects with `RTW_DECL_TABLE_PHY_COND`, `RTW_DECL_TABLE_BB_PG`, `RTW_DECL_TABLE_RF_RADIO`, and `RTW_DECL_TABLE_TXPWR_LMT`. `rtw8821a_bb_pg[]` supplies baseband power-by-rate/group data. `rtw8821a_txpwr_lmt[]` is a large regulatory/channel/bandwidth/rate-section limit table.

The power-sequence data is split into transition arrays: `trans_carddis_to_cardemu_8821a`, `trans_cardemu_to_act_8821a`, `trans_act_to_lps_8821a`, `trans_act_to_cardemu_8821a`, and `trans_cardemu_to_carddis_8821a`. Public flow arrays `card_enable_flow_8821a[]`, `enter_lps_flow_8821a[]`, and `card_disable_flow_8821a[]` compose those transitions for the chip profile. The file also defines per-band/per-path power-tracking curves and exports `rtw8821a_rtw_pwr_track_tbl`.

## Control Flow

The file has no procedural C control flow beyond static initializers. Runtime control comes from common rtw88 loaders: PHY initialization walks the `struct rtw_table` objects and writes register/value pairs, including conditional markers embedded in the raw arrays; power management walks `struct rtw_pwr_seq_cmd` arrays until `RTW_PWR_CMD_END`; power tracking indexes the thermal delta tables through `struct rtw_pwr_track_tbl`.

## State And Persistence Behavior

All objects are constant except for their hardware side effects when applied. Table application writes MAC, BB, AGC, and RF registers that persist until later reconfiguration or reset. Power-sequence arrays manipulate MAC, USB, PCI, and SDIO-visible registers according to interface masks. Power-tracking tables do not store state but shape updates to `dm_info` and TX power/swing registers in the chip code.

## Dependencies And Integration Points

The file depends on `main.h`, `phy.h`, and `rtw8821a_table.h` for common structures and table macros. `rtw8821a.c` references all exported symbols through `rtw8821a_hw_spec` and RFE definitions. The power sequences integrate with common rtw88 power-sequence parsing, while power-limit data integrates with regulatory and per-rate TX power code.

## Risks And Edge Cases

Most failures are silent RF behavior problems rather than compile errors. A wrong conditional marker can apply values for the wrong package, interface, band, or channel group. Power-sequence errors can leave the card stuck during enable, LPS entry, or disable. Transmit-power-limit entries use sentinel-looking values such as `63`, so validation should distinguish "maximum/no limit" semantics from literal power indices.

## Test Signals

Signals include successful table load during probe, no unresolved exported table symbols, channel bring-up on 2.4 GHz and 5 GHz, regulatory TX power within expected limits, stable thermal compensation, correct LPS entry through `enter_lps_flow_8821a`, clean card disable/reenable, and RF behavior across USB and any future SDIO/PCI use because the power sequences include interface-specific commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.h

## Purpose

`rtw8821a_table.h` declares the RTL8821A static data objects defined in `rtw8821a_table.c`. It is the table contract consumed by `rtw8821a.c`.

## Important APIs, Types, And Data

The header exports `rtw8821a_mac_tbl`, `rtw8821a_agc_tbl`, `rtw8821a_bb_tbl`, `rtw8821a_bb_pg_tbl`, `rtw8821a_rf_a_tbl`, and `rtw8821a_txpwr_lmt_tbl` as `struct rtw_table` objects. It also exports `card_enable_flow_8821a[]`, `enter_lps_flow_8821a[]`, and `card_disable_flow_8821a[]` as power-sequence flow arrays, plus `rtw8821a_rtw_pwr_track_tbl` for thermal compensation.

## Control Flow

There is no runtime code. The declarations allow the chip profile to select these data objects during probe, PHY setup, power management, and power tracking.

## State And Persistence Behavior

The header itself stores no mutable state. The declared constant objects become hardware state only when common rtw88 routines apply their register writes or power commands.

## Dependencies And Integration Points

Including translation units must have `struct rtw_table`, `struct rtw_pwr_seq_cmd`, and `struct rtw_pwr_track_tbl` available. The header integrates `rtw8821a.c` with its table source, the PHY table loader, the power-sequence parser, and the dynamic power-tracking path.

## Risks And Test Signals

Declaration/definition drift can break linking or cause incomplete chip setup. Build coverage should verify symbols resolve. Hardware tests should check that all declared tables are referenced by `rtw8821a_hw_spec`, that LPS and disable flows run, and that thermal tracking can access the exported power-track table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821a_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821au.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821au.c

## Purpose

`rtw8821au.c` is the USB device binding for RTL8821AU/RTL8811AU adapters. It maps a broad set of Realtek and vendor-branded USB IDs to the RTL8821A chip specification and delegates probing/disconnect to the shared rtw88 USB layer.

## Important APIs, Types, And Functions

`rtw_8821au_id_table[]` contains Realtek IDs (`0x0811`, `0x0820`, `0x0821`, `0x8822`, `0x0823`, `0xa811`) and partner devices from Buffalo, I-O DATA, ELECOM, Netgear, Hawking, D-Link, Planex, TRENDnet, TP-Link, Obihai, and Edimax. Each entry uses `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` and stores `&rtw8821a_hw_spec` in `.driver_info`. `rtw_8821au_driver` uses `rtw_usb_probe` and `rtw_usb_disconnect`; `module_usb_driver()` performs registration.

## Control Flow

USB enumeration matches an entry, autoloads the module via the generated alias, and calls the common rtw88 USB probe. The shared probe builds transport state, reads the chip-info pointer from `driver_info`, and initializes the RTL8821A chip. Disconnect tears down USB queues and common rtw88 state.

## State And Persistence Behavior

The file has no per-device mutable state. The static ID table determines persistent module alias behavior. Hardware, firmware, URB, and queue state belong to rtw88 USB/core and to `rtw8821a.c`.

## Dependencies And Integration Points

Dependencies are Linux USB/module headers, `main.h`, `usb.h`, and `rtw8821a.h`. Integration is with USB interface matching, rtw88 transport setup, firmware loading for `rtw88/rtw8821a_fw.bin`, and the chip operation/table paths in `rtw8821a.c`.

## Risks And Test Signals

The listed vendor devices all bind to the same chip profile, so unsupported board quirks or different RF front ends would appear as probe success but poor RF behavior. Tests should verify module aliases, probe on representative vendor IDs, endpoint mapping and aggregation, firmware load, traffic on 2.4/5 GHz, Bluetooth coexistence where present, suspend/resume, and removal during active I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821au.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.c

## Purpose

`rtw8821c.c` implements the RTL8821C chip profile for rtw88. It handles HCI-specific efuse parsing, MAC/PHY initialization, channel and bandwidth programming, RX PHY status parsing, TX power index programming, false-alarm collection, firmware-driven IQK, Bluetooth coexistence, thermal power tracking, beamformee support, LED control, power sequences, interface PHY parameters, queue/page configuration, RFE definitions, and the exported `rtw8821c_hw_spec`.

## Important APIs, Types, And Functions

`rtw8821c_ops` is the operation table used by the common core. Local callbacks include `rtw8821c_phy_set_param()`, `rtw8821c_read_efuse()`, `query_phy_status()`, `rtw8821c_set_channel()`, `rtw8821c_mac_init()`, `rtw8821c_set_tx_power_index()`, `rtw8821c_false_alarm_statistics()`, `rtw8821c_phy_calibration()`, `rtw8821c_phy_cck_pd_set()`, `rtw8821c_pwr_track()`, beamforming callbacks, LED control, and coexistence callbacks.

`rtw8821c_read_efuse()` casts the logical map to `struct rtw8821c_efuse`, copies board/RFE/thermal/country/TX power fields, derives `hal->rfe_btg`, applies a power-table quirk for RFE options 2 and 4, and selects MAC address parsing by HCI type (PCIe, USB, or SDIO). `rtw8821c_set_channel()` coordinates BB, BB swing, MAC, RF register 0x18, RF front-end switching, and RX DFIR setup. `rtw8821c_do_iqk()` asks firmware to run IQK, polls RF register `RF_DTXLOK` for sentinel `0xabcde`, clears it, and logs reload/fail-mask state from `REG_IQKFAILMSK`.

`rtw8821c_hw_spec` declares firmware `rtw88/rtw8821c_fw.bin`, WCPU 3081, descriptor sizes, efuse sizes, FIFO/page layout, power flows, interface PHY parameters, table pointers, RFE definitions, beamforming limits, LPS support, coexistence tables, and debug register domains.

## Control Flow

Probe reaches this file through bus modules such as PCIe/USB/SDIO bindings that use `rtw8821c_hw_spec`. Bring-up powers the chip with generic rtw88 power helpers, parses efuse, runs `rtw8821c_mac_init()`, and then `rtw8821c_phy_set_param()`. PHY setup enables BB/RF domains, resets BB, loads tables, applies crystal-cap settings, records baseline channel parameters, initializes dynamic PHY state and power tracking, and initializes beamforming PHY registers.

RX processing selects PHY status page 0 for CCK or page 1 for OFDM/HT/VHT style reports. Dynamic management samples false alarms, adjusts CCK packet-detection thresholds, and uses two-phase thermal-meter tracking. Channel changes first program BB band/bandwidth and regulatory SRRC CCK filter behavior, then MAC channel state, RF channel/bandwidth bits, RF front-end switch state, and RX digital filters.

## State And Persistence Behavior

Persistent runtime state is stored in shared objects: efuse data, `hal->pkg_type`, `hal->rfe_btg`, cached `hal->ch_param[]`, `dm_info` power tracking and CCK PD state, coexistence RFE state, and beamforming state. The file writes many MAC/BB/RF registers that remain active until later reconfiguration. A function-local static `do_iqk_cnt` counts firmware IQK runs globally for the module, not per device.

## Dependencies And Integration Points

The implementation depends on `main.h`, `coex.h`, `fw.h`, `tx.h`, `rx.h`, `phy.h`, `mac.h`, `reg.h`, `debug.h`, `bf.h`, `regd.h`, `rtw8821c.h`, and `rtw8821c_table.h`. It integrates with firmware IQK commands, regulatory SRRC handling, beamforming helpers, LTE coexistence registers, common TX descriptor checksum code, rtw88 power-sequence parsing, and Bluetooth coexistence decision tables.

## Risks And Edge Cases

Efuse parsing is HCI-layout dependent; using the wrong HCI type returns `-ENOTSUPP` or extracts the wrong MAC address. `phy_para_table_8821c` sets `.n_usb3_para = ARRAY_SIZE(usb2_param_8821c)`, which is currently harmless only because both arrays have one element. Firmware IQK can wait up to 300 * 20 ms before logging completion status. Coexistence antenna switching has several RFE option branches and cached switch-status suppression, so stale RFE metadata can prevent needed register changes. The file is dense with register constants and magic values, making channel/RFE regressions likely to show up as poor RF performance rather than obvious errors.

## Test Signals

Test probe on PCIe, USB, and SDIO variants; verify efuse MAC extraction for each layout; load `rtw8821c_fw.bin`; exercise 2.4 GHz, 5 GHz, 20/40/80/10/5 MHz bandwidths; validate SRRC channel 13/14 behavior; inspect RX RSSI and bandwidth reports for PHY status pages 0 and 1; run firmware IQK and observe sentinel/fail-mask logs; force thermal deltas for power tracking; test CCK PD level changes; verify beamformee SU/MU configuration; exercise coexistence with multiple RFE options; and confirm clean power-on/off sequence execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.h

## Purpose

`rtw8821c.h` defines the RTL8821C chip-private contract used by `rtw8821c.c`: efuse map layouts, the exported chip-info symbol, mirrored baseband write helper, MAC/PHY timing constants, PHY status extraction macros, register offsets, coexistence control pins, and RF register 0x18 bit definitions.

## Important APIs, Types, And Constants

The efuse structures model HCI-specific logical efuse tails: `struct rtw8821ce_efuse` for PCIe, `struct rtw8821cu_efuse` for USB, and `struct rtw8821cs_efuse` for SDIO. `struct rtw8821c_efuse` wraps common fields such as RTL ID, TX power index table, channel plan, crystal cap, thermal meter, PA/LNA type, RF options, country code, and a union of HCI-specific tails.

`_rtw_write32s_mask()` writes the same mask/data to a baseband path register and its mirrored `+0x200` peer; `rtw_write32s_mask()` wraps it with a build-time address-range assertion for `0xC00` to `0xCFF`. PHY status macros decode little-endian page 0 and page 1 reports for PWDB, LNA/VGA, RF mode, RX subchannel, EVM, CFO, and SNR fields. The many `WLAN_*`, `REG_*`, `BIT_*`, `BTG_*`, `WLG_*`, `PTA_CTRL_PIN`, `DPDT_CTRL_PIN`, and `RF18_*` constants are consumed by MAC init, channel switching, false-alarm logic, and coexistence.

## Control Flow

The header has no standalone runtime flow. Its inline helper performs immediate paired register writes when called. Its macros control how `rtw8821c.c` parses receive descriptors and programs register fields during initialization, channel changes, and coexistence switching.

## State And Persistence Behavior

Packed efuse structures describe persistent hardware-programmed data read from efuse into driver state. Constants and macros do not store state, but incorrect values directly alter persistent hardware register programming. The mirrored write helper affects both RF/baseband path register banks.

## Dependencies And Integration Points

The header depends on kernel byteorder helpers, bit macros, and rtw88 core register-access helpers. It is tightly integrated with `rtw8821c.c`; bus modules use only the `rtw8821c_hw_spec` declaration from this header or equivalent chip header paths.

## Risks And Test Signals

Packed bitfields and HCI-specific efuse offsets are fragile across compiler, endian, or layout changes; the file uses `__packed` and little-endian helpers to reduce that risk. PHY status macros cast byte pointers to `__le32 *`, so buffer alignment and report length assumptions matter. Test signals include compile-time `BUILD_BUG_ON` coverage for mirrored writes, efuse parse validation against known dumps for PCIe/USB/SDIO, RX PHY status decoding for both pages, and channel-switch register verification for RF18 band/channel/bandwidth fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c.h -->
