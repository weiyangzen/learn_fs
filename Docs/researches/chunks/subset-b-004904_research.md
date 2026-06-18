# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c lines 1-10249

## Scope

This chunk covers the opening 10,249 lines of `rtw8814a_table.c`, the generated/static hardware table source for the Realtek RTL8814A support in the `rtw88` wireless driver. The file includes `main.h`, `phy.h`, and `rtw8814a_table.h`, then defines table data and exports it through `struct rtw_table` instances produced by the `RTW_DECL_TABLE_*` macros.

Within this chunk, the complete covered sections are:

- `rtw8814a_mac[]` and `rtw8814a_mac_tbl` at lines 9-155.
- `rtw8814a_agc[]` and `rtw8814a_agc_tbl` at lines 157-3248.
- `rtw8814a_bb[]` and `rtw8814a_bb_tbl` at lines 3250-5442.
- `rtw8814a_bb_pg[]`, `rtw8814a_bb_pg_type0[]`, `type2[]`, `type3[]`, `type4[]`, `type5[]`, `type7[]`, and `type8[]`, each exported as a BB power-group table at lines 5444-6538.
- All of `rtw8814a_rf_a[]` and its `rtw8814a_rf_a_tbl` declaration at lines 6540-8589.
- The beginning and most of `rtw8814a_rf_b[]` from line 8591 through the chunk end at line 10249. The path-B table and its `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_b, B)` declaration continue outside this chunk.

The chunk is almost entirely static data. It has no local executable functions, no heap allocation, no locks, and no persistent storage writes. Runtime behavior comes from the shared `rtw_table` parser callbacks and the chip/RFE selection code in the surrounding driver.

## Purpose

The tables encode RTL8814A bring-up and calibration defaults for MAC, AGC, baseband, per-rate transmit power offsets, and RF radio register programming. During PHY initialization, `rtw_phy_load_tables()` loads the chip-level tables from `rtw8814a_hw_spec`: MAC first, then BB, AGC, optional RFE-specific AGC BTG, RFK init, and one RF table per active RF path. Separately, `rtw_phy_init_tx_power()` and related setup paths consume the RFE-selected `phy_pg_tbl` and `txpwr_lmt_tbl`; in this chunk, the BB power-by-rate tables are the relevant RFE-specific inputs.

For RTL8814A, `rtw8814a.c` wires these objects into `rtw8814a_hw_spec`:

- `.mac_tbl = &rtw8814a_mac_tbl`
- `.agc_tbl = &rtw8814a_agc_tbl`
- `.bb_tbl = &rtw8814a_bb_tbl`
- `.rf_tbl = { &rtw8814a_rf_a_tbl, &rtw8814a_rf_b_tbl, &rtw8814a_rf_c_tbl, &rtw8814a_rf_d_tbl }`
- `.rfe_defs` chooses between `rtw8814a_bb_pg_type0_tbl`/`rtw8814a_txpwr_lmt_type0_tbl`/`rtw8814a_rtw_pwrtrk_type0_tbl` for RFE 0 and `rtw8814a_bb_pg_tbl`/`rtw8814a_txpwr_lmt_type1_tbl`/`rtw8814a_rtw_pwrtrk_tbl` for RFE 1.

The data is therefore not optional documentation: incorrect entries directly change MMIO/RF writes, power tables, receive gain behavior, rate power offsets, and regulatory power calculations.

## Important APIs, Types, and Tables

`struct rtw_table` is the common wrapper. It stores `.data`, `.size`, `.parse`, `.do_cfg`, and `.rf_path`; `rtw_load_table()` simply calls `tbl->parse(rtwdev, tbl)`.

`RTW_DECL_TABLE_PHY_COND(name, cfg)` wraps `u32` address/data/condition arrays for MAC, AGC, and BB tables. It uses `rtw_parse_tbl_phy_cond` as the parser and one of the following callbacks:

- `rtw_phy_cfg_mac`: writes an 8-bit MAC register via `rtw_write8`.
- `rtw_phy_cfg_agc`: writes a 32-bit AGC register via `rtw_write32`.
- `rtw_phy_cfg_bb`: writes a 32-bit BB register via `rtw_write32`, with special pseudo-addresses `0xfe`, `0xfd`, `0xfc`, `0xfb`, `0xfa`, and `0xf9` interpreted as sleeps/delays.

`RTW_DECL_TABLE_RF_RADIO(name, path)` is the RF variant. It wraps the same conditional table format, sets `.do_cfg = rtw_phy_cfg_rf`, and pins `.rf_path` to `RF_PATH_A` or another path. `rtw_phy_cfg_rf` writes through `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` and treats RF pseudo-addresses `0xffe` and `0xfe` as delays.

`RTW_DECL_TABLE_BB_PG(name)` wraps arrays of `struct rtw_phy_pg_cfg_pair` with fields `band`, `rf_path`, `tx_num`, `addr`, `bitmask`, and `data`. `rtw_parse_tbl_bb_pg` feeds each entry to `rtw_phy_store_tx_power_by_rate`, filling `hal->tx_pwr_by_rate_offset_2g` or `hal->tx_pwr_by_rate_offset_5g`.

The chunk contains 824 conditional/branch marker lines in the `u32` tables and 1,056 `struct rtw_phy_pg_cfg_pair` initializer lines across the BB power-group variants. The RF tables also include delay markers, including three `0xFFE` entries in the complete path-A table and multiple `0xFE`/`0xfe` pseudo-delay markers across the chunk.

## Control Flow

At runtime, table consumption is linear and parser-driven:

1. `rtw_phy_load_tables()` loads the chip's MAC, BB, and AGC tables, then each RF path table up to `rtwdev->hal.rf_path_num`.
2. For `rtw8814a_mac_tbl`, `rtw_parse_tbl_phy_cond` iterates pairs from `rtw8814a_mac[]` and calls `rtw_phy_cfg_mac` for matched entries.
3. For `rtw8814a_agc_tbl`, the same conditional parser calls `rtw_phy_cfg_agc`.
4. For `rtw8814a_bb_tbl`, the parser calls `rtw_phy_cfg_bb`, so pseudo-address delay entries are honored while normal entries are written to BB registers.
5. For `rtw8814a_rf_a_tbl` and the subsequent RF path tables, the parser calls `rtw_phy_cfg_rf` with the table's embedded RF path.
6. RFE-specific power-by-rate setup calls `rtw_load_table()` on one of the `rtw8814a_bb_pg*` tables. `rtw_parse_tbl_bb_pg` does not write hardware immediately; it populates transmit-power offset arrays in `struct rtw_hal`.

The conditional `u32` table format uses encoded positive/negative branch tiles. `rtw_parse_tbl_phy_cond` keeps `is_matched` and `is_skipped` state, interprets `BRANCH_IF`, `BRANCH_ELIF`, `BRANCH_ELSE`, and `BRANCH_ENDIF`, and only calls the `do_cfg` callback when the current branch matches the runtime condition. The runtime condition is built from chip/package/interface/RFE state populated from efuse and HCI information. For RTL8814A, non-8812A/8821A chips require exact `cond.rfe == drv_cond.rfe` matches.

## Data Sections in This Chunk

`rtw8814a_mac[]` is a compact MAC register initialization sequence. It contains byte-oriented writes for control/status, queue/timing, GPIO/MAC configuration, and other low-level MAC setup addresses. Because the declaration uses `rtw_phy_cfg_mac`, only the low byte of each data word is written.

`rtw8814a_agc[]` is a large AGC table. It repeatedly writes AGC register `0x81c` with dense gain-table values and ends by toggling DIG-related registers including `0xc50`, `0xe50`, `0x1850`, and `0x1a50`. The repeated conditional blocks select different values for RFE/interface/package cases.

`rtw8814a_bb[]` programs baseband registers across the main BB register range and per-path BB blocks, including addresses in the `0x800` range, CCK/OFDM path areas, and path-specific blocks around `0xcxx`, `0Exx`, `0x18xx`, and `0x1Axx`. It includes pseudo-delay handling through the BB parser and conditional branches for RFE variants. The table ends by programming many path-D style `0x1b80` entries.

The BB power-group tables encode per-band, per-RF-path, per-TX-chain power-by-rate offsets. The repeated address sets show the four RF paths:

- path A around `0x0c20` through `0x0ce8`
- path B around `0x0e20` through `0x0ee8`
- path C around `0x1820` through `0x18e8`
- path D around `0x1a20` through `0x1ae8`

Each RFE type changes the data nibbles while preserving the same broad address layout. Type 0 is lower-power than the default in many places; type 3, type 4, type 5, type 7, and type 8 carry distinct per-path/per-band offsets. In the currently visible `rtw8814a.c`, only the default table and type0 table are selected by `rtw8814a_rfe_defs`, but the header exports the other variants for possible future or out-of-tree RFE mapping.

`rtw8814a_rf_a[]` is a complete RF path-A radio table. It starts with common RF setup registers such as `0x018`, `0x040`, `0x058`, `0x07f`, and `0x0b0`-`0x0bf`; then conditionally programs many calibration/gain/lut-style RF registers. Heavily repeated addresses include `0x034`, `0x035`, `0x036`, `0x03b`, `0x03c`, `0x0ef`, and `0x018`. It ends by switching `0x018`, executing three `0xFFE` delay markers, and restoring `0x018` values before declaring `rtw8814a_rf_a_tbl` for `RF_PATH_A`.

`rtw8814a_rf_b[]` begins at line 8591. The visible part initializes path B with common registers, then conditionally programs analogous RF gain/calibration tables. The chunk ends before this static array closes, so the path-B declaration macro and any tail entries are outside this research item.

## State and Persistence Behavior

All arrays in this chunk are `static const` and live in the driver image as read-only data. The exported `const struct rtw_table` wrappers are also immutable. The tables do not persist data to disk, firmware NVRAM, or efuse.

Runtime side effects are hardware and in-memory driver state:

- MAC/AGC/BB/RF tables write device registers and RF registers during initialization.
- BB PG tables update `rtwdev->hal.tx_pwr_by_rate_offset_2g` and `rtwdev->hal.tx_pwr_by_rate_offset_5g`.
- RF delay pseudo-addresses affect initialization timing.
- Conditional branches select or skip writes based on efuse/RFE/interface state.

Once loaded, the hardware register state persists until reset, power transition, suspend/resume reinitialization, or another driver path overwrites the same registers.

## Dependencies and Integration Points

This chunk depends on shared `rtw88` infrastructure:

- `main.h` for `struct rtw_table`, `struct rtw_chip_info`, `struct rtw_rfe_def`, `struct rtw_dev`, `struct rtw_hal`, RF path enums, and `rtw_load_table`.
- `phy.h` for `struct rtw_phy_pg_cfg_pair`, parser declarations, register mask constants, and `RTW_DECL_TABLE_*` macros.
- `phy.c` for `rtw_parse_tbl_phy_cond`, `rtw_parse_tbl_bb_pg`, `rtw_phy_cfg_mac`, `rtw_phy_cfg_agc`, `rtw_phy_cfg_bb`, and `rtw_phy_cfg_rf`.
- `rtw8814a_table.h` for extern declarations consumed by `rtw8814a.c`.
- `rtw8814a.c` for chip specification wiring, efuse-derived RFE selection, RF path count, and RFE definitions.

The tables also indirectly depend on the register definitions and low-level write helpers used by parser callbacks: `rtw_write8`, `rtw_write32`, `rtw_write_rf`, `rtw_phy_store_tx_power_by_rate`, and timing primitives such as `msleep`, `mdelay`, `usleep_range`, and `udelay`.

## Risks and Maintenance Hazards

The highest risk is silent hardware misconfiguration. Most entries are opaque vendor-provided register values; a single wrong address, value, condition tile, or table order can degrade RF performance, break association, violate transmit-power expectations, or leave one RF path unusable.

Conditional encoding is fragile. The parser consumes the `u32` arrays as pairs through `union phy_table_tile`; branch markers such as `0x800000..`, `0x900000..`, `0xA0000000`, and `0xB0000000` are not ordinary writes. Inserting or deleting one word instead of an address/data pair would desynchronize the whole table and turn data into branch state or vice versa.

RFE matching is exact for RTL8814A. If efuse parsing in `rtw8814a_read_rfe_type()` or RFE definitions in `rtw8814a_rfe_defs[]` do not match the encoded table conditions, expected writes can be skipped. This is especially important for USB versus PCIe handling and for boards where RFE option bit 7 is remapped to option 0 or 1.

The BB power-by-rate tables affect both PHY behavior and later regulatory power calculations. Wrong `band`, `rf_path`, `tx_num`, `addr`, `bitmask`, or packed `data` fields can corrupt `hal->tx_pwr_by_rate_offset_*` arrays without an immediate register-write failure.

RF path table boundaries matter. This chunk includes all of path A and only part of path B; any review or merge must reconcile the later chunk before making whole-file claims about path B/C/D or transmit-power-limit and power-tracking sections.

Delay sentinel values are semantically significant. In RF tables, `0xffe` and `0xfe` are delays; in BB tables, `0xfe` through `0xf9` are delays. Treating them as normal register addresses, changing case-insensitive values incorrectly, or removing duplicate delay entries can create timing-sensitive bring-up failures.

The table variants exported but not currently selected by `rtw8814a_rfe_defs[]` are a drift risk. They compile and remain available through the header, but if no in-tree RFE mapping references them, regressions may be detected only by external board support or future mapping changes.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build with `W=1` or equivalent kernel warning levels to catch malformed initializers, missing externs, type mismatches, and array declaration errors.
- Boot or load the `rtw88_8814a` path on RTL8814A hardware and confirm `rtw_phy_load_tables()` completes without warnings, stalls, or RF write failures.
- Enable `RTW_DBG_PHY`, `RTW_DBG_EFUSE`, and `RTW_DBG_REGD` where practical to confirm the expected RFE option, RF path count, table loading order, and absence of unsupported-RFE errors.
- Verify both RFE 0 and RFE 1 paths if hardware or emulation can expose them, because this chunk provides both selected BB PG table families.
- Exercise 2.4 GHz and 5 GHz association, scan, RX sensitivity, and TX throughput across active antenna configurations. AGC/BB/RF table regressions often surface as poor RSSI, failed calibration, low MCS, or path-specific throughput loss.
- Inspect `hal->tx_pwr_by_rate_offset_2g` and `hal->tx_pwr_by_rate_offset_5g` after `rtw_parse_tbl_bb_pg` to confirm populated offsets for all expected RF paths and rate sections.
- For RF path-A changes, compare RF register traces around high-frequency repeated registers (`0x034`, `0x035`, `0x036`, `0x03b`, `0x03c`, `0x0ef`, `0x018`) against known-good traces. For path-B work, defer final judgement until the continuation chunk is reviewed.

## Chunk Notes for Merge Lane

This is a partial oversized-file chunk report, not the final per-file research document. The merge lane should combine it with later chunks for `rtw8814a_table.c` to cover the tail of `rtw8814a_rf_b[]`, RF paths C and D, transmit-power-limit tables, power-tracking swing tables, and power-sequence command arrays.

For whole-file synthesis, preserve that this first chunk establishes the shared table macro model, the initialization load path, and the RFE-specific BB power-by-rate selection. Later chunks should add the remaining exported objects from `rtw8814a_table.h`, especially `rtw8814a_txpwr_lmt*`, `rtw8814a_rtw_pwrtrk*`, `card_enable_flow_8814a`, and `card_disable_flow_8814a`.
