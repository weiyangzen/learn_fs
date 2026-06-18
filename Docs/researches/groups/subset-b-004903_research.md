# subset-b-004903 research

This grouped report covers the Realtek rtw88 source files assigned to subset-b-004903. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.c

## Purpose
`rtw8723x.c` implements shared RTL8723x/RTL8703B family support for the rtw88 driver. It exports `rtw8723x_common`, a table of register addresses and function pointers consumed by chip-specific 8723x variants. The file centralizes 2.4 GHz 802.11n behavior that is common across HCI variants: EFUSE parsing, MAC setup, LCK/IQK support, transmit-power programming, false-alarm statistics, thermal crystal-cap adjustment, TX descriptor checksums, and Bluetooth coexistence initialization.

## Important APIs, types, and functions
- `rtw8723x_common`: exported shared contract containing IQK backup register lists, LTE coexistence and RF SIPI addresses, DIG register descriptors, priority queue register addresses, and callbacks.
- `__rtw8723x_read_efuse()`: casts the logical EFUSE map to `struct rtw8723x_efuse`, copies board/RF/thermal/regulatory fields into `rtwdev->efuse`, selects the MAC-address location by HCI type, and repairs invalid all-`0xff` values.
- `__rtw8723x_lck()`: performs LC calibration by pausing traffic or clearing context type, setting `BIT_LCK` in `RF_CFGCH`, polling completion, restoring RF state, and unpausing traffic.
- `__rtw8723x_mac_init()` and `__rtw8723x_mac_postinit()`: program TX control, RX filter maps, RCR, interrupt migration, second CCA behavior, and firmware/hardware TXQ report enablement.
- `__rtw8723x_set_tx_power_index()` plus `rtw8723x_set_tx_power_index_by_rate()`: iterate RF paths and rate sections through `hal->tx_pwr_tbl` and write TXAGC register fields from `rtw8723x_txagc`.
- `__rtw8723x_false_alarm_statistics()`: snapshots, stores, and resets CCK/OFDM false-alarm, CCA, and CRC counters into `rtwdev->dm_info`.
- `__rtw8723x_iqk_backup_regs()`, `__rtw8723x_iqk_restore_regs()`, and `__rtw8723x_iqk_similarity_cmp()`: shared IQ calibration state handling and multi-round result reconciliation.
- `__rtw8723x_pwrtrack_get_limit_ofdm()` and `__rtw8723x_pwrtrack_set_xtal()`: map current TX rate to OFDM power-track limits and adjust crystal cap based on thermal delta tables.
- `__rtw8723x_fill_txdesc_checksum()`: calculates the Realtek 16-word XOR checksum over the first 32 bytes of a TX descriptor.

## Control flow and state behavior
EFUSE read starts with optional debug dumping, then populates persistent in-memory driver state in `rtwdev->efuse`. HCI type controls which packed EFUSE union member supplies the MAC address; unsupported HCI types return `-EOPNOTSUPP`. Invalid EFUSE values are normalized in place: TX power defaults are copied when the first bytes are all `0xff`, invalid Bluetooth antenna settings are forced to shared antenna/path A, invalid board options clear the regulatory derivation, and invalid crystal cap becomes `0x20`.

MAC initialization is direct register programming and returns success unconditionally. TX power programming depends on current HAL state (`rf_path_num`, `tx_pwr_tbl`) and is rerunnable after channel/rate recalculation. False alarm collection briefly holds hardware counters, reads CCK/OFDM and CRC counters into `dm_info`, then toggles reset bits so future dynamic-mechanism passes see fresh counts.

IQK helpers persist pre-calibration register values in `struct rtw8723x_iqk_backup_regs`, including ADDA/MAC/BB registers, IGI values, LTE coexistence grant/path state, and BTG selection. Similarity comparison treats IQ result pairs as Q10.8 values, compares two calibration rounds with `MAX_TOLERANCE`, and may synthesize a hybrid result round when only some path pairs match. Power tracking stores state in `dm_info` and writes corrected crystal-cap bits to `REG_AFE_CTRL3`; it does not persist state outside hardware and runtime structures.

## Dependencies and integration points
This file depends heavily on rtw88 core helpers from `main.h`, `debug.h`, `phy.h`, `reg.h`, and `tx.h`: `rtw_read*`, `rtw_write*`, RF accessors, `rtw_hci_type()`, `rtw_rate_section`, `rtw_rate_size`, `rtw_get_rfe_def()`, debug categories, and `fill_txdesc_checksum_common`-adjacent descriptor definitions. Exported `rtw8723x_common` is the integration surface for 8723x chip modules; inline wrappers in `rtw8723x.h` dispatch to these function pointers. Bluetooth coexistence integrates through PTA/GPIO, beacon/TBTT, and BT statistic registers. EFUSE integration feeds regulatory, board, antenna, thermal, and power-index subsystems.

## Risks and edge cases
- EFUSE structure offsets are hardware ABI: wrong packing or HCI selection would corrupt MAC address, regulatory, or power data.
- TX power defaults only validate a small byte range; partially corrupted EFUSE tables can still pass as valid.
- Calibration routines pause traffic and directly manipulate RF/BB registers; missing restore paths or timeout behavior can leave degraded RF state.
- `__rtw8723x_set_tx_power_index()` only covers CCK/OFDM/HT 1-stream sections, matching 802.11n 8723x capabilities; adding variants with more streams would need updates.
- False-alarm reset ordering is hardware-sensitive and may affect dynamic gain decisions if registers change across silicon revisions.
- The file relies on debug-gated dumping for observability; many hardware failures only emit warnings, not hard failures.

## Test signals
Useful test signals include successful probe with valid MAC address for PCIe/USB/SDIO variants, EFUSE debug output showing repaired invalid values, stable association throughput after `mac_init`/`mac_postinit`, correct TXAGC register writes per rate section, LCK timeout warnings absent during calibration, `dm_info` false-alarm counters changing and resetting across watchdog cycles, thermal power tracking adjusting `REG_AFE_CTRL3`, and TX descriptor checksum acceptance by firmware/hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.h

## Purpose
`rtw8723x.h` defines the shared ABI and hardware constants for RTL8723x common support. It exposes packed EFUSE layouts for PCIe, USB, and SDIO variants; IQK enums and backup state; the `rtw8723x_common` dispatch structure; register and bit definitions used by 8723x calibration/statistics/channel code; and inline wrappers that let chip-specific code call common operations without exporting every helper symbol.

## Important APIs, types, and definitions
- `enum rtw8723x_path`, `enum rtw8723x_iqk_round`, and `enum rtw8723x_iqk_result`: define path and IQK result indexing for S1/S0 TX/RX X/Y values and hybrid calibration rounds.
- `struct rtw8723xe_efuse`, `struct rtw8723xu_efuse`, `struct rtw8723xs_efuse`, and `struct rtw8723x_efuse`: packed logical EFUSE layouts with common 8723x fields plus HCI-specific tail layouts.
- `struct rtw8723x_iqk_backup_regs`: runtime backup container for ADDA, MAC, BB, LTE coexistence, BTG, and IGI state across IQ calibration.
- `struct rtw8723x_common`: exported common-data and callback table consumed through inline wrappers such as `rtw8723x_lck()`, `rtw8723x_read_efuse()`, `rtw8723x_false_alarm_statistics()`, and `rtw8723x_fill_txdesc_checksum()`.
- Register constants from MAC, BB, RF, CCK, OFDM, IQK, LTE coexistence, and false-alarm domains, such as `REG_LTECOEX_CTRL`, `REG_CCK_FA_RST_11N`, `REG_OFDM_FA_TYPE*`, `REG_FPGA0_IQK_11N`, and `REG_IQK_RES_*`.
- Inline math helpers `iqkxy_to_s32()` and `iqk_mult()` for Q10.8 IQK values.
- Inline IQK helpers for BTG/path control, LTE grant backup/config/restore, and ADDA mass programming.

## Control flow and state behavior
The header intentionally uses inline dispatchers to route calls through the singleton `rtw8723x_common`. This keeps chip-specific modules small while centralizing function implementations in `rtw8723x.c`. IQK helper inlines mutate hardware state immediately: they backup BTG/LTE grant values into caller-provided backup storage, write path-control or LTE grant registers for calibration, restore backed-up values afterward, and can set all common ADDA registers to a single value.

EFUSE structs are pure layout state and must match the logical EFUSE map offsets. IQK result enums encode array layout assumptions used by calibration code: pairs of X/Y values are adjacent, and `IQK_SX_NR` is derived from `IQK_NR / PATH_NR`. `iqkxy_to_s32()` sign-extends 10-bit values, and `iqk_mult()` multiplies Q10.8 terms while optionally returning the extra fractional bit used by register programming.

## Dependencies and integration points
The header includes `main.h`, `debug.h`, `phy.h`, and `reg.h`, so it is coupled to core rtw88 device state, debug helpers, PHY types, bit macros, and common register definitions. It depends on `rtw8723x_common` being defined and exported by `rtw8723x.c`. The inline wrappers are used by 8723x chip-specific implementation files to integrate with rtw88 chip ops without duplicating common logic. Register constants are also shared with any variant-specific channel or calibration code.

## Risks and edge cases
- EFUSE structs are packed hardware ABI. Any field movement changes parsing for real devices.
- The inline wrappers assume every function pointer in `rtw8723x_common` is initialized; a missing callback becomes a null call.
- `PATH_NR`, `IQK_NR`, and `IQK_SX_NR` are tightly coupled to S1/S0 result ordering. Adding paths or result dimensions requires coordinated updates.
- Inline hardware mutation helpers provide no locking; callers must ensure they run in appropriate calibration/device-state contexts.
- Several register constants are local duplicates of hardware knowledge. Silicon revisions with different offsets require careful validation.

## Test signals
Build coverage should catch missing struct/type declarations and uninitialized exported symbols. Runtime signals include successful EFUSE parsing for each HCI layout, IQK backup/restore preserving BTG and LTE grant state, calibration debug logs using expected S1/S0 indexes, and no null callback faults when chip variants call the inline dispatchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.c

## Purpose
`rtw8812a.c` registers RTL8812A chip support for rtw88. It supplies the chip ops table, exported `rtw8812a_hw_spec`, RX PHY status parsing, LC/IQ calibration, power tracking, LED handling, queue/page configuration, coexistence parameters, and links to the static initialization tables in `rtw8812a_table.c`. The implementation targets a 2x2 dual-band 802.11ac device, especially the USB 8812AU path, while reusing generic 88xxA helpers where possible.

## Important APIs, types, and functions
- `rtw8812a_hw_spec`: exported `struct rtw_chip_info` describing firmware name, descriptor sizes, EFUSE sizes, FIFO sizes, band/features, power sequences, table pointers, RFE definitions, coexistence parameters, and chip ops.
- `rtw8812a_ops`: `struct rtw_chip_ops` implementation using many `rtw88xxa_*` helpers, plus local `query_phy_status`, `phy_calibration`, `pwr_track`, LED, checksum, and no-op coexistence callbacks.
- `rtw8812a_query_phy_status()`: delegates generic 88xxA PHY status parsing with a local CCK RX power converter, then applies 8812A-specific CCK RSSI correction when high-power CCK is not enabled.
- `rtw8812a_do_lck()`: pauses TX if not in continuous TX, triggers RF LCK, waits up to five 10 ms polls, restores RF state, and unpauses TX.
- `rtw8812a_do_iqk()` and `rtw8812a_iqk()`: backup MAC/BB/AFE/RF state, run two-path TX and RX IQK retry loops, average successful samples through `rtw88xxa_iqk_finish()`, fill TX/RX IQ compensation registers, then restore state.
- `rtw8812a_phy_calibration()`: runs IQK and loads low-band or high-band AGC differential tables based on current channel.
- `rtw8812a_pwr_track()`: implements a two-stage thermal-meter trigger/read cycle and calls `rtw88xxa_phy_pwrtrack()` with local LCK/IQK callbacks.
- `rtw8812a_led_set()` and `rtw8812a_fill_txdesc_checksum()`: hardware LED GPIO update and 16-word TX descriptor checksum.
- Static tables `page_table_8812a`, `rqpn_table_8812a`, `prioq_addrs_8812a`, `rtw8812a_dig`, `rtw8812a_rfe_defs`, RSSI thresholds, and coexistence RF parameters.

## Control flow and state behavior
Power-off is delegated to `rtw88xxa_power_off()` with `enter_lps_flow_8812a`. During RX, PHY status handling updates `pkt_stat` and dynamic mechanism state through the generic parser; local CCK logic adjusts RSSI percentage for low-rate packets depending on high-power mode.

IQK is the largest state transition. `rtw8812a_do_iqk()` saves MAC/BB registers, selected AFE registers, RF registers on paths A/B, and two page-C1 RFECTL registers. It configures MAC for calibration, calls `rtw8812a_iqk()`, restores RF and AFE state, restores RFECTL, and finally restores MAC/BB. Inside `rtw8812a_iqk()`, the driver powers AFE blocks, disables hardware 3-wire, sets DAC/ADC sampling, configures RF mode-table entries, then loops for TX and RX calibration. Each loop triggers one-shot calibration, waits up to 20 ms, collects up to ten samples, and stops when enough averaged samples pass or retry limits are reached. Failed paths are filled with neutral IQC values (`0x200`, `0`) so hardware has a defined compensation state.

Power tracking persists trigger state in `dm_info->pwr_trk_triggered`. On the first watchdog pass it starts the RF thermal meter, and on the second it reads/uses thermal data through the common 88xxA power tracking flow, potentially invoking LCK and IQK. Chip registration state is static and exported through `rtw8812a_hw_spec`; no on-disk persistence exists.

## Dependencies and integration points
The file depends on `main.h`, `coex.h`, `phy.h`, `reg.h`, `rtw88xxa.h`, `rtw8812a_table.h`, and `tx.h`. It reuses `rtw88xxa_power_on/off`, EFUSE reading, channel setting, RF access, TX power index programming, false alarm statistics, CCK PD, generic IQK backup helpers, and generic power tracking. It integrates static tables from `rtw8812a_table.c` through `rtw_chip_info`: MAC/BB/AGC/RF init tables, PHY power-gain tables, TX power limit tables, power sequences, and power-track tables. USB module binding in `rtw8812au.c` passes this `rtw_chip_info` via `driver_info`.

## Risks and edge cases
- Several chip ops are `NULL` or no-op (`phy_set_param`, MAC init/postinit, LDO25, coexistence callbacks), so correctness depends on generic 88xxA initialization being sufficient for all supported devices.
- IQK has many hard-coded RF/BB values, retry limits, and RFE-specific branches. A failed restore or wrong RFE option can leave poor EVM/RSSI/throughput.
- CCK RSSI correction is heuristic and depends on `hal.cck_high_power`; wrong classification changes signal reporting and dynamic gain decisions.
- `rtw8812a_phy_calibration()` loads AGC diff tables only for channels 36-64 and >=100 after IQK; mid/edge channels rely on default AGC.
- `rtw8812a_pwr_track()` assumes a two-call cadence. Missed watchdog cycles or RF read failures could leave `pwr_trk_triggered` stale.
- Coexistence metadata exists, but callback bodies are empty and `coex_para_ver` is zero, indicating limited/no active BT coexistence tuning.

## Test signals
Relevant signals include successful USB probe using `rtw8812a_hw_spec`, firmware request for `rtw88/rtw8812a_fw.bin`, stable RX RSSI for CCK and OFDM packets, IQK debug logs showing TX/RX path A/B completion without repeated timeouts, channel-specific AGC diff table load on low/high 5 GHz channels, power tracking toggling thermal meter trigger and updating power without warnings, LED state changes on activity, and absence of TX descriptor checksum errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.h

## Purpose
`rtw8812a.h` is the small public header for RTL8812A chip support. It declares the exported `rtw8812a_hw_spec` object so bus-specific modules, notably the USB binding, can associate device IDs with the 8812A chip description.

## Important APIs and types
- Include guard `__RTW8812A_H__`.
- `extern const struct rtw_chip_info rtw8812a_hw_spec;`: the only API in this header. The type is supplied by rtw88 core headers included by users before or alongside this header.

## Control flow and state behavior
The header has no executable control flow and owns no mutable state. Its role is link-time integration: consumers reference `rtw8812a_hw_spec`, which is defined and exported in `rtw8812a.c`.

## Dependencies and integration points
`rtw8812au.c` includes this header and stores `&rtw8812a_hw_spec` in each USB ID table entry's `driver_info`. The rtw88 USB probe path later retrieves that pointer to initialize the correct chip. Any other bus variant could use the same declaration to bind the 8812A chip ops and static tables.

## Risks and edge cases
- The header intentionally does not include `main.h`; including code must have visibility for `struct rtw_chip_info` where needed.
- If `rtw8812a_hw_spec` is not exported or the object file is omitted from the build, bus-specific modules will fail to link.

## Test signals
Build/link success for `rtw8812au` is the primary signal. Runtime confirmation is USB probe selecting `RTW_CHIP_TYPE_8812A` through the `driver_info` pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.c

## Purpose
`rtw8812a_table.c` contains static hardware programming data for RTL8812A. It exports typed rtw88 tables for MAC, AGC, BB, PHY power-gain, RF path A/B, TX power limits, power transition sequences, and thermal power tracking. The file is almost entirely declarative data consumed by `rtw8812a.c` through `rtw_chip_info` and by generic rtw88 table loaders.

## Important APIs, tables, and macros
- `rtw8812a_mac_tbl`: generated from `rtw8812a_mac[]` with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_mac)` for MAC register initialization.
- `rtw8812a_agc_tbl`, `rtw8812a_agc_diff_lb_tbl`, `rtw8812a_agc_diff_hb_tbl`: AGC table programming and 5 GHz low/high-band differential updates loaded during calibration.
- `rtw8812a_bb_tbl`: BB register initialization table.
- `rtw8812a_bb_pg_tbl` and `rtw8812a_bb_pg_rfe3_tbl`: PHY power-gain tables declared with `RTW_DECL_TABLE_BB_PG`, with a separate table for RFE type 3.
- `rtw8812a_rf_a_tbl` and `rtw8812a_rf_b_tbl`: RF radio path tables declared with `RTW_DECL_TABLE_RF_RADIO`.
- `rtw8812a_txpwr_lmt_tbl`: regulatory/channel/rate TX power limits declared with `RTW_DECL_TABLE_TXPWR_LMT`.
- `card_enable_flow_8812a`, `enter_lps_flow_8812a`, and `card_disable_flow_8812a`: exported arrays of `struct rtw_pwr_seq_cmd` sequence pointers.
- `rtw8812a_rtw_pwr_track_tbl` and `rtw8812a_rtw_pwr_track_rfe3_tbl`: exported thermal tracking lookup tables for default and RFE3 boards.

## Control flow and state behavior
The data tables are loaded by external control flow. MAC/AGC/BB/RF arrays use rtw88 table encodings that include raw address/value pairs and conditional selector words, allowing the generic table loader to apply entries only for matching conditions. Power sequence arrays are interpreted by the rtw88 power-sequence engine: card-disabled to card-emulation, card-emulation to active, active to low-power state, active to card-emulation, and card-emulation to card-disabled. Commands include register writes, polling, and delays with interface masks for PCI and USB-specific steps.

Power tracking tables map thermal deltas to swing/power adjustments for 2.4 GHz, 5 GHz path A/B, positive/negative temperature direction, CCK/OFDM, and RFE3-specific behavior. These tables are immutable and referenced through `struct rtw_pwr_track_tbl`; runtime state lives in `rtwdev->dm_info` and PHY code, not in this file.

## Dependencies and integration points
The file includes `main.h`, `phy.h`, and `rtw8812a_table.h`. It depends on table declaration macros from rtw88 PHY code and power-sequence definitions from core rtw88 headers. `rtw8812a.c` points `rtw_chip_info` fields to the exported tables: `mac_tbl`, `agc_tbl`, `bb_tbl`, `rf_tbl`, RFE definitions' `phy_pg_tbl`/`txpwr_lmt_tbl`/`pwr_track_tbl`, and power on/off sequences. `rtw8812a_phy_calibration()` directly loads `rtw8812a_agc_diff_lb_tbl` or `rtw8812a_agc_diff_hb_tbl` based on channel.

## Risks and edge cases
- Tables encode vendor hardware knowledge as constants. Errors typically appear as failed bring-up, low sensitivity, poor TX power, or regulatory violations rather than compile failures.
- Conditional table markers are opaque; malformed condition ordering can skip or over-apply register writes.
- Power sequence commands are interface-mask-sensitive. A USB/PCI mask mistake can break suspend/resume or power-on sequencing.
- RFE3 has distinct BB power-gain and power-track tables; incorrect `rfe_option` parsing in EFUSE sends hardware through the wrong table set.
- TX power limit tables must stay aligned with regulatory code expectations and channel/rate indexes.

## Test signals
Test signals include successful `rtw_load_table()` calls during power-on/PHY init, reliable card enable/disable and LPS entry/exit on both USB and PCI masks where applicable, expected AGC diff table load by channel, correct RFE3 power-gain selection, no table parser warnings, stable thermal power tracking across positive and negative temperature deltas, and regulatory TX power values matching the `rtw8812a_txpwr_lmt_tbl` limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.h

## Purpose
`rtw8812a_table.h` declares the static RTL8812A hardware data exported by `rtw8812a_table.c`. It is the table interface used by `rtw8812a.c` to populate `rtw_chip_info` and to run channel-specific AGC updates.

## Important APIs and declarations
- Table declarations for `rtw8812a_mac_tbl`, `rtw8812a_agc_tbl`, `rtw8812a_agc_diff_lb_tbl`, `rtw8812a_agc_diff_hb_tbl`, `rtw8812a_bb_tbl`, `rtw8812a_bb_pg_tbl`, `rtw8812a_bb_pg_rfe3_tbl`, `rtw8812a_rf_a_tbl`, `rtw8812a_rf_b_tbl`, and `rtw8812a_txpwr_lmt_tbl`.
- Power sequence flow declarations: `card_enable_flow_8812a`, `enter_lps_flow_8812a`, and `card_disable_flow_8812a`.
- Power tracking table declarations: `rtw8812a_rtw_pwr_track_tbl` and `rtw8812a_rtw_pwr_track_rfe3_tbl`.

## Control flow and state behavior
The header has no executable flow. It exposes immutable table objects whose interpretation is handled by rtw88 core table loaders, power sequence engines, and power tracking code. Runtime mutable state is held by the caller (`rtw_dev`, `rtw_hal`, `rtw_dm_info`) and hardware registers after the tables are applied.

## Dependencies and integration points
The declarations depend on rtw88 core types `struct rtw_table`, `struct rtw_pwr_seq_cmd`, and `struct rtw_pwr_track_tbl`. `rtw8812a.c` includes this header for chip registration and calibration, and the table implementation includes it to verify matching extern declarations.

## Risks and edge cases
- Missing or mismatched extern declarations cause link or type errors when `rtw8812a.c` references table objects.
- Because the header exposes both default and RFE3 tables, callers must choose the table matching EFUSE-derived RFE definitions.
- The power sequence pointer arrays are null-terminated; consumers rely on that convention from the implementation.

## Test signals
Build/link coverage is the primary signal. Runtime table-use signals include `rtw8812a_hw_spec` referencing all expected table objects, channel calibration being able to load low/high-band AGC diff tables, and power on/off flows resolving their declared sequence arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812au.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812au.c

## Purpose
`rtw8812au.c` is the USB bus binding for RTL8812AU-class devices. It declares USB vendor/product IDs that should bind to the rtw88 8812A chip implementation, registers a `usb_driver`, and points all matching devices at `rtw8812a_hw_spec` through `driver_info`.

## Important APIs and data
- `rtw_8812au_id_table[]`: `struct usb_device_id` array using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for Realtek and many OEM product IDs. Each entry stores `(kernel_ulong_t)&rtw8812a_hw_spec`.
- `MODULE_DEVICE_TABLE(usb, rtw_8812au_id_table)`: exports modalias information for module autoloading.
- `rtw_8812au_driver`: `struct usb_driver` with `.name = KBUILD_MODNAME`, `.id_table`, `.probe = rtw_usb_probe`, and `.disconnect = rtw_usb_disconnect`.
- `module_usb_driver(rtw_8812au_driver)`: creates module init/exit registration boilerplate.

## Control flow and state behavior
There is no device-control logic in this file. The kernel USB core matches a connected interface against `rtw_8812au_id_table`, module autoloading can occur via the generated device table, and the generic rtw88 USB probe receives the matched ID. Probe then uses the `driver_info` pointer to initialize the device with `rtw8812a_hw_spec`. Disconnect is delegated to the generic rtw88 USB disconnect path. Runtime state is owned by the USB core and rtw88 core, not this file.

## Dependencies and integration points
The file includes Linux USB/module headers, rtw88 `main.h`, `usb.h`, and `rtw8812a.h`. It integrates the bus-neutral chip implementation in `rtw8812a.c` with USB transport helpers `rtw_usb_probe()` and `rtw_usb_disconnect()`. The ID table includes Realtek product IDs (`0x8812`, `0x881a`, `0x881b`, `0x881c`) and OEM IDs from NEC, Buffalo, I-O DATA, Belkin, ZyXEL, Logitec, Abocom, Netgear, ASUS, Sitecom, Hawking, WD, Linksys, Amped Wireless, EnGenius, D-Link, Planex, TRENDnet, TP-Link, Tenda, and Edimax.

## Risks and edge cases
- The broad vendor-specific interface match (`0xff/0xff/0xff`) is appropriate for Realtek USB Wi-Fi devices but can bind incorrectly if an OEM product ID is reused for a non-8812A interface.
- A missing product ID prevents autoload/probe for that adapter even though the chip support exists.
- All entries point to the same `rtw8812a_hw_spec`; devices with board-specific quirks must be handled through EFUSE/RFE data or additional matching logic elsewhere.
- Probe/disconnect behavior depends entirely on generic USB code and the chip spec being linked into the module.

## Test signals
Test signals include `modinfo` showing the listed USB aliases, hotplug autoload for supported adapters, `rtw_usb_probe()` receiving `rtw8812a_hw_spec`, firmware request for `rtw88/rtw8812a_fw.bin`, successful disconnect without leaks or crashes, and no unintended binding reports for adjacent Realtek USB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812au.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.c

## Purpose
`rtw8814a.c` implements RTL8814A chip support for rtw88. It exports `rtw8814a_hw_spec` and provides chip ops for EFUSE parsing, PHY and MAC initialization, channel/bandwidth switching, RF path setup, RX PHY status parsing, transmit-power programming, false-alarm statistics, IQ calibration, thermal power tracking, CCK packet detection, LED control, descriptor checksum handling, and limited coexistence hooks. The chip is a dual-band 802.11ac part with up to 3 spatial streams selected from four RF paths.

## Important APIs, types, and functions
- `rtw8814a_hw_spec`: exported `struct rtw_chip_info` describing firmware `rtw88/rtw8814a_fw.bin`, 3081 WLAN CPU, EFUSE/FIFO sizes, HT/VHT support, LDPC, LPS support, RF base/SIPI addresses, table pointers, RFE definitions, and coexistence parameters.
- `rtw8814a_ops`: chip ops table linking rtw88 core to local power/PHY/MAC/RF/dynamic-mechanism callbacks.
- `rtw8814a_read_efuse()`: parses `struct rtw8814a_efuse`, derives USB mode switch, RFE option, board/regulatory/thermal/swing fields, amplifier type, RF type, hardware capabilities, TX power table, and HCI-specific MAC address.
- `rtw8814a_phy_set_param()` and `rtw8814a_mac_init()`: bring up BB/RF and MAC domains, load tables, set crystal cap, RF paths, CCK/RX antenna behavior, queue/NAV/EDCA/filter settings, USB3/PCIe-specific workarounds, and power tracking initial state.
- `rtw8814a_set_channel()`, `rtw8814a_switch_band()`, `rtw8814a_switch_channel()`, and `rtw8814a_set_bw_mode()`: coordinate band changes, RFE pinmux, AGC/ADC/BW/RF channel programming, CCK filter coefficients, ADC clock workaround, and spur/NBI/CSI calibration.
- `rtw8814a_query_phy_status()`: parses Jaguar PHY reports for CCK and OFDM/VHT packets, updating RSSI, per-path power, SNR, EVM, bandwidth, signal power, and CFO state.
- `rtw8814a_do_iqk()` and helpers: backup MAC/BB/RF state, configure AFE/MAC for calibration, perform LOK/TXK/RXK one-shot flows for paths A-D, reset NCTL, and restore hardware state.
- `rtw8814a_pwr_track()` and helpers: trigger/read RF thermal meter, update per-path OFDM swing/TXAGC offsets, and rerun IQK when needed.
- `rtw8814a_false_alarm_statistics()`, `rtw8814a_set_tx_power_index()`, `rtw8814a_phy_cck_pd_set()`, `rtw8814a_set_ampdu_factor()`, `rtw8814a_led_set()`, and `rtw8814a_fill_txdesc_checksum()`.

## Control flow and state behavior
EFUSE parsing is the first major state population step. It copies logical-map fields into `rtwdev->efuse`, derives RFE defaults when the high bit indicates autoselection, maps RFE option to external/internal PA/LNA flags, sets `hal->rf_type`, `hal->rf_path_num`, `hal->rf_phy_num`, antenna masks, and hardware capability NSS. USB devices running below SuperSpeed are forced to 2T2R despite EFUSE 3T/4T indicators.

PHY setup powers the relevant interface BB/RF domain, enables all four RF paths, loads BB and AGC tables, writes crystal cap, configures CCK/TRX paths, loads RF tables per active path, initializes generic PHY state and power tracking, then applies RFE GPIO setup and USB cleanup. MAC setup enables MAC TX/RX/security/32K calibration, loads the MAC table, sets interrupt masks, rate response, retry limits, RX filters, aggregation, SIFS, EDCA, beacon/NAV timing, and per-interface workarounds. USB SuperSpeed disables U1/U2 and pre-TX command behavior to avoid spurs/H2C failures; PCIe toggles GPIO/RF power and antenna selection.

Channel control derives old/new band from `REG_CCK_CHECK` and channel number. Band switches temporarily gate BB reset, configure 2.4/5 GHz RFE pinmux and CCK/RX path settings, update BB swing and power-track defaults, set ADC/AGC bandwidth values, then re-enable BB. Channel switching writes clock-tracking and RF channel/band fields per path and selects AGC table area. Bandwidth mode sets MAC RF mode, subchannel fields, ADC/AGC/RF bandwidth, runs the A-cut ADC clock workaround when needed, and applies spur/NBI/CSI masks for specific 2.4 GHz and 5 GHz channel/bandwidth/RFE combinations.

IQK backs up selected MAC, BB, and RF registers, changes AFE/MAC into calibration mode, triggers LOK for each path, then TX and RX one-shot calibration for paths A-D with polling and up to four retries. TX/RX results are applied through IQC registers when successful; failed TX/RX disables corresponding IQK application bits. Power tracking uses a two-pass thermal trigger state in `dm_info->pwr_trk_triggered`, EWMA thermal averages, per-path `delta_power_index`, and the regulatory TX power index to split compensation between TXAGC and BB swing. False-alarm counters and CCK PD levels feed dynamic mechanism state.

## Dependencies and integration points
The file depends on Linux USB definitions and rtw88 headers: `main.h`, `coex.h`, `tx.h`, `phy.h`, `rtw8814a.h`, `rtw8814a_table.h`, `rtw88xxa.h`, `reg.h`, `debug.h`, `efuse.h`, `regd.h`, and `usb.h`. It integrates with table data from `rtw8814a_table.c`, generic rtw88 power and RF accessors, regulatory power lookup `rtw_regd_get()`/`rtw_phy_get_tx_power_index()`, USB private state via `rtw_get_usb_priv()`, coexistence state through `rtwdev->coex`, LED classdev callbacks, and dynamic mechanism fields in `rtwdev->dm_info`.

## Risks and edge cases
- EFUSE-derived RF type intentionally differs by USB speed; wrong speed detection can expose unsupported NSS/path combinations.
- Channel and spur workarounds are highly specific. Missing one channel/bandwidth/RFE case can cause sensitivity loss or spurious interference.
- The A-cut ADC clock workaround pauses TX and waits for MAC idle with a bounded loop. If hardware remains active, it proceeds after the limit and may still disturb traffic.
- IQK touches paths A-D even when effective RF type may be 2T2R/3T3R; restore correctness and path masks are critical.
- `rtw8814a_set_tx_power_index()` skips HT/VHT sections while scanning, so scan-time behavior differs from connected operation.
- `rtw8814a_false_alarm_statistics()` only counts CCK when CCK is enabled in `REG_RXPSEL`; wrong CCK gate detection skews dynamic gain.
- Coexistence callbacks are mostly no-op, with only antenna-switch behavior forcing LTE mux path clear. BT coexistence quality may be limited.
- `rtw8814a_set_ampdu_factor()` caps AMPDU to 256K to avoid low TX speed with some 11n APs; changing it can regress interoperability.

## Test signals
Strong signals include successful EFUSE parsing for USB and PCIe layouts, correct NSS/antenna selection on USB2 versus USB3 devices, firmware request for `rtw88/rtw8814a_fw.bin`, table loads during PHY/MAC init, stable channel switches across 2.4 GHz/5 GHz and 20/40/80 MHz widths, absence of spur-related throughput drops on channels 54/58/118/122/151/153/155 and 2.4 GHz channels 4-8/14, IQK logs without repeated path timeouts, thermal tracking changing TXAGC/swing without overflow warnings, false-alarm counters resetting each watchdog pass, and LED/TX descriptor checksum behavior matching hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.h

## Purpose
`rtw8814a.h` defines the RTL8814A logical EFUSE layouts and declares the exported `rtw8814a_hw_spec` chip descriptor. It provides the packed structures used by `rtw8814a_read_efuse()` to interpret USB and PCIe logical EFUSE maps.

## Important APIs and types
- `struct rtw8814au_efuse`: USB-specific tail containing VID, PID, reserved bytes, and MAC address at logical offset `0xd8`.
- `struct rtw8814ae_efuse`: PCIe-specific tail containing MAC address at `0xd0` plus vendor/device/subsystem IDs.
- `struct rtw8814a_efuse`: full 512-byte logical EFUSE view with RTL ID, USB mode, four-path TX power index table, channel plan, crystal cap, thermal meter, IQK/LCK, PA/LNA/RF board fields, BT setting, customer/version fields, 2G/5G BB swing settings, antenna/RFE option, country code, and HCI-specific union.
- `static_assert(sizeof(struct rtw8814a_efuse) == 512)`: build-time guard for the logical EFUSE ABI.
- `extern const struct rtw_chip_info rtw8814a_hw_spec;`: exported chip description defined in `rtw8814a.c`.

## Control flow and state behavior
The header has no executable flow. Its packed structs define how a raw logical EFUSE byte map is cast and read. The union lets parsing code select USB or PCIe tail fields by HCI type. The size assertion protects against accidental padding or layout drift, which would otherwise corrupt later EFUSE offsets.

## Dependencies and integration points
The structs rely on core kernel/rtw88 types and constants such as `u8`, `__le16`, `ETH_ALEN`, and `struct rtw_txpwr_idx`, made visible by including contexts in implementation files. `rtw8814a.c` includes this header for EFUSE parsing and chip spec export. Bus-specific modules can include it to reference `rtw8814a_hw_spec`.

## Risks and edge cases
- Packed field offsets are hardware ABI. Any change to reserved lengths or field order breaks EFUSE parsing.
- The header declares only USB and PCIe tail layouts; SDIO is treated as unsupported in the implementation.
- The main EFUSE struct contains `res5[0x122]` to force total size. Future fields within that region require careful offset-preserving edits.
- Like `rtw8812a.h`, it declares `struct rtw_chip_info` without including `main.h`, so include ordering matters for consumers.

## Test signals
Build success with the `static_assert` intact is the first signal. Runtime signals include `rtw8814a_read_efuse()` extracting the expected MAC address for USB and PCIe devices, correct VID/PID/DID debugging when added, valid channel plan/country/thermal/swing fields, and unsupported HCI types returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a.h -->
