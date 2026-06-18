# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004904`: lines 1-10249, `Docs/researches/chunks/subset-b-004904_research.md`
- `subset-b-004905`: lines 10250-20492, `Docs/researches/chunks/subset-b-004905_research.md`
- `subset-b-004906`: lines 20493-23930, `Docs/researches/chunks/subset-b-004906_research.md`

## Chunk Research

### subset-b-004904: lines 1-10249

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

### subset-b-004905: lines 10250-20492

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c lines 10250-20492

## Scope

This chunk covers a data-heavy section of the Realtek rtw88 RTL8814A hardware tables. The range starts inside the tail of `rtw8814a_rf_b[]`, completes RF path B registration, contains all of `rtw8814a_rf_c[]`, all of `rtw8814a_rf_d[]`, and then defines the generic and several board/package-specific transmit-power limit tables through the beginning of `rtw8814a_txpwr_lmt_type7[]`.

The exact in-scope declarations are:

- Tail of `rtw8814a_rf_b[]`, ending with `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_b, B)` at line 10548.
- Full `rtw8814a_rf_c[]` plus `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_c, C)`, lines 10550-12551.
- Full `rtw8814a_rf_d[]` plus `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_d, D)`, lines 12553-14583.
- Full `rtw8814a_txpwr_lmt[]`, `rtw8814a_txpwr_lmt_type0[]`, `rtw8814a_txpwr_lmt_type1[]`, `rtw8814a_txpwr_lmt_type2[]`, `rtw8814a_txpwr_lmt_type3[]`, and `rtw8814a_txpwr_lmt_type5[]`, each with 972 `struct rtw_txpwr_lmt_cfg_pair` entries and a corresponding `RTW_DECL_TABLE_TXPWR_LMT(...)` wrapper.
- The first 45 entries of `rtw8814a_txpwr_lmt_type7[]`, from line 20447 through the chunk boundary at line 20492. The type7 table is incomplete in this chunk and must be reconciled with the following chunk.

This file is not executable filesystem logic despite the repository path. It is Linux wireless PHY/RF calibration and regulatory data for the RTL8814A 4-stream Wi-Fi chipset.

## Purpose

The RF arrays provide register programming sequences for the RTL8814A radio paths. They are consumed during PHY table loading to bring each active RF path into a calibrated state. Because RTL8814A supports four RF paths, the chip descriptor exposes one table per path: A, B, C, and D. This chunk owns the end of path B and the complete path C/D table bodies.

The transmit-power limit arrays encode regulatory and board-specific caps by regulatory domain, band, channel width, rate section, and channel. These limits are stored into `rtwdev->hal.tx_pwr_limit_2g` and `rtwdev->hal.tx_pwr_limit_5g`; later TX-power calculations use them to clamp per-rate power indices before programming hardware.

The section is therefore critical to:

- RF path C/D bring-up and calibration for 4x4 RTL8814A devices.
- RF path B completion at the beginning of this chunk.
- Per-regulatory-domain TX power caps for RFE/package variants.
- Runtime power-limit fallback and cross-reference behavior in the shared rtw88 PHY layer.

## Important APIs, Types, and Tables

The RF table declarations use plain `static const u32` arrays. The table stream alternates normal address/data pairs with conditional branch markers such as `0x800000..`, `0x900000..`, `0xA0000000`, and `0xB0000000`. These are interpreted by `rtw_parse_tbl_phy_cond()`, which views the data as `union phy_table_tile` entries and applies branch/condition handling before calling the table's `do_cfg` callback.

`RTW_DECL_TABLE_RF_RADIO(name, path)` wraps an RF array into a public `const struct rtw_table name_tbl` with:

- `.parse = rtw_parse_tbl_phy_cond`
- `.do_cfg = rtw_phy_cfg_rf`
- `.rf_path = RF_PATH_A/B/C/D`

`rtw_phy_cfg_rf()` writes each matched RF entry with `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` and applies a short delay after normal writes. Special pseudo-addresses `0xffe` and `0xfe` are delay tokens rather than RF registers.

The transmit-power limit tables use:

```c
struct rtw_txpwr_lmt_cfg_pair {
	u8 regd;
	u8 band;
	u8 bw;
	u8 rs;
	u8 ch;
	s8 txpwr_lmt;
};
```

`RTW_DECL_TABLE_TXPWR_LMT(name)` wraps each array as a `struct rtw_table` parsed by `rtw_parse_tbl_txpwr_lmt()`. That parser iterates entries, calls `rtw_phy_set_tx_power_limit()`, fills missing regulatory domains from an alternate or worldwide domain, then cross-references HT/VHT 5 GHz limits where one side is absent.

Important in-scope RF tables:

- `rtw8814a_rf_b_tbl`: completed at the start of this range, mapped to RF path B.
- `rtw8814a_rf_c_tbl`: full RF path C sequence, roughly matching path B but with path-specific differences in registers such as `0x03b`, `0x034`, and later gain/power values.
- `rtw8814a_rf_d_tbl`: full RF path D sequence, similar to path C but with path-D-specific values and repeated conditional channel/RFE sections.

Important in-scope TX-power limit tables:

- `rtw8814a_txpwr_lmt_tbl`: generic/default limits.
- `rtw8814a_txpwr_lmt_type0_tbl`
- `rtw8814a_txpwr_lmt_type1_tbl`
- `rtw8814a_txpwr_lmt_type2_tbl`
- `rtw8814a_txpwr_lmt_type3_tbl`
- `rtw8814a_txpwr_lmt_type5_tbl`
- Partial `rtw8814a_txpwr_lmt_type7[]`, not yet declared as a table in this chunk.

`rtw8814a_table.h` exports these table objects so `rtw8814a.c` can reference them through chip and RFE descriptors.

## Control Flow

RF table loading is driven by `rtw_phy_load_tables()`. The function loads MAC, BB, AGC, optional RFE AGC/BTG, optional RFK, and then iterates `rf_path` from zero to `rtwdev->hal.rf_path_num - 1`. For each active path it selects `chip->rf_tbl[rf_path]` and calls `rtw_load_table()`. In `rtw8814a_hw_spec`, `chip->rf_tbl` is `{&rtw8814a_rf_a_tbl, &rtw8814a_rf_b_tbl, &rtw8814a_rf_c_tbl, &rtw8814a_rf_d_tbl}`, so this chunk supplies the complete path C/D stream and the registered path B table object.

During parsing, `rtw_parse_tbl_phy_cond()` walks two `u32` words at a time as either a condition tile or a register/data pair. Positive and negative condition markers update `is_matched` and `is_skipped`, implementing if/elif/else/endif-like selection. Only matched address/data pairs reach `rtw_phy_cfg_rf()`. The RF tables in this range use many conditional blocks around channel/package/RFE selectors; the repeated `0x800000..`, `0x900000..`, `0xA0000000`, and `0xB0000000` markers are part of this mini-language rather than direct hardware writes.

TX-power limit loading is selected through the RFE definition. In the current `rtw8814a_rfe_defs[]`, RFE option 0 uses `rtw8814a_txpwr_lmt_type0_tbl`, and RFE option 1 uses `rtw8814a_txpwr_lmt_type1_tbl`. The other exported tables in this chunk are still ABI-visible through the table header and may be used by future/alternate RFE mappings, downstream changes, or reconciliation with adjacent chunks.

`rtw_parse_tbl_txpwr_lmt()` records which regulatory domains were present, then stores each tuple into the HAL power-limit arrays. For 2 GHz it writes `hal->tx_pwr_limit_2g[regd][bw][rs][channel_index]`; for 5 GHz it writes `hal->tx_pwr_limit_5g[...]`. The worldwide domain is tightened with the minimum of existing worldwide and newly parsed values. Missing domains are copied from configured alternatives when available or from worldwide as a fallback. Finally, HT and VHT 5 GHz rate-section limits are cross-filled where one of a matching HT/VHT pair is still at the max-power sentinel.

## State and Persistence

The RF arrays are `static const` data and do not hold mutable state. Their effects persist in hardware RF registers after table load until a reset, power cycle, RF reconfiguration, calibration, or later table load overwrites them. Because these are path-specific tables, a wrong path binding would persist incorrect radio state on the corresponding RF chain.

The TX-power limit arrays are also immutable. Runtime state is created when `rtw_parse_tbl_txpwr_lmt()` stores their values in `struct rtw_hal`. Those HAL arrays persist for subsequent TX-power calculations and are reused across channel/rate updates. The parser also mutates worldwide and missing-domain entries based on the parsed table content, so the final runtime limits are not simply a direct copy of the array.

The tables interact with persistent device identity and board state:

- `rtwdev->efuse.rfe_option` selects the RFE definition and therefore the power-limit table.
- `rtwdev->hal.rf_path_num` determines whether paths C and D are loaded.
- `rtwdev->chip->max_power_index` clamps parsed power limits. For RTL8814A this is `0x3f`.
- `rtwdev->chip->is_pwr_by_rate_dec = true` affects nearby power-by-rate parsing, but the limit tables in this chunk already store signed integer limits directly.

## Dependencies and Integration Points

This chunk depends on `main.h`, `phy.h`, and `rtw8814a_table.h`. The key shared declarations are `struct rtw_table`, `struct rtw_txpwr_lmt_cfg_pair`, `RTW_DECL_TABLE_RF_RADIO`, and `RTW_DECL_TABLE_TXPWR_LMT`.

Integration points include:

- `rtw8814a_hw_spec` in `rtw8814a.c`, which installs the RF table pointers and RFE definitions into the chip descriptor.
- `rtw_phy_load_tables()` in `phy.c`, which loads RF tables for active paths.
- `rtw_phy_cfg_rf()` in `phy.c`, which turns RF table entries into `rtw_write_rf()` operations using the table's path.
- `rtw_parse_tbl_txpwr_lmt()` in `phy.c`, which turns power-limit tuples into HAL arrays and performs regulatory-domain fallback.
- `rtw_phy_get_tx_power_index()` and related TX-power paths later in `phy.c`, which consume the parsed limit arrays when deriving final transmit power.
- Regulatory domain helpers such as `rtw_regd_has_alt()`, because missing domains in these tables can be copied from alternate domains.

The RF register writes ultimately depend on lower rtw88 register access, RF path base addresses in `rtw8814a_hw_spec`, and the device's hardware/firmware state at PHY bring-up time.

## Risks

The RF arrays are fragile calibration data. Small changes to an address/data pair, conditional marker, or ordering can alter synthesizer, gain, tracking, path enable, or channel-specific calibration behavior. The path C and D arrays are similar but not identical; blindly copying values between them risks breaking one RF chain while leaving the others apparently functional.

The chunk boundary is a risk. The source range starts inside `rtw8814a_rf_b[]` and ends inside `rtw8814a_txpwr_lmt_type7[]`. A final file-level report must merge adjacent chunks before drawing conclusions about complete path B contents or type7 power-limit behavior.

The conditional table encoding is not self-validating. `rtw_parse_tbl_phy_cond()` depends on paired words and specific bitfield encodings in `union phy_table_tile`. If a data pair accidentally matches a condition pattern, or if a condition marker is malformed, the parser can skip or apply a large block unexpectedly.

The TX-power limit data is regulatory-sensitive. Incorrect values can underpower the device, reduce throughput, or exceed regional conducted-power limits. The values are clamped to `max_power_index`, but that only bounds magnitude; it does not prove the regulatory mapping is correct.

The current RFE map references only type0 and type1 for RTL8814A, but this file exports more type-specific tables. Unused-looking tables should not be removed without checking vendor variants and downstream RFE mappings.

Power-limit fallback can hide missing table coverage. If a regulatory domain is absent, the parser copies an alternate or worldwide table. That keeps runtime arrays populated but can make domain-specific omissions less obvious unless debug logs are reviewed.

## Test and Validation Signals

Useful validation for this chunk is mostly hardware- and integration-based:

- Probe an RTL8814A device with four RF paths and confirm `rtw_phy_load_tables()` loads RF paths A-D without RF write failures.
- Use debug logging around table loading to confirm path C uses `rtw8814a_rf_c_tbl` and path D uses `rtw8814a_rf_d_tbl`, with the expected `.rf_path` values.
- Exercise both supported `efuse.rfe_option` values in `rtw8814a_rfe_defs[]` and confirm RFE 0 selects `rtw8814a_txpwr_lmt_type0_tbl` while RFE 1 selects `rtw8814a_txpwr_lmt_type1_tbl`.
- Watch for `wrong txpwr_lmt` warnings from `rtw_phy_set_tx_power_limit()`. Such warnings would indicate invalid `regd`, `band`, `bw`, `rs`, or channel values in one of these arrays.
- Check `RTW_DBG_REGD` output for regulatory domains filled from alternatives or worldwide; unexpected fallback may indicate missing table coverage.
- Validate conducted TX power on 2.4 GHz channels 1-14 and 5 GHz channels 36-165 across CCK, OFDM, HT, and VHT sections, with both 20 MHz and 40 MHz widths covered by these tables.
- Run throughput/RSSI checks with 1x1 through 4x4 path configurations to catch RF path C/D calibration mistakes that would not appear on lower-chain devices.
- Build-test the file to verify all table wrappers declared in this chunk match the extern declarations in `rtw8814a_table.h`.
- During merge/reconciliation, verify the next chunk completes `rtw8814a_txpwr_lmt_type7[]` and supplies its `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` wrapper.

### subset-b-004906: lines 20493-23930

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c lines 20493-23930

## Scope

This chunk covers the last 3,438 lines of `rtw8814a_table.c`. The range starts in the middle of the `rtw8814a_txpwr_lmt_type7[]` transmit-power-limit table, continues through the full `rtw8814a_txpwr_lmt_type8[]` table and its `RTW_DECL_TABLE_TXPWR_LMT()` wrapper, then defines RTL8814A thermal power-tracking tables for the default board type and board types 0, 2, 5, 7, and 8. It ends with the RTL8814A card power-on and power-off command sequences exported as `card_enable_flow_8814a[]` and `card_disable_flow_8814a[]`.

Because the range starts inside a data table, earlier chunks are needed for the beginning of `rtw8814a_txpwr_lmt_type7[]` and for the file-level context around MAC, AGC, BB, RF, baseband power-group, and earlier transmit-power-limit tables. This chunk still includes all code-visible declarations from `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` to the end of the file.

## Purpose

This file is a generated-style hardware data source for the Realtek `rtw88` RTL8814A driver. In this chunk, the data has three runtime roles:

- It completes board-specific transmit power limits for the type 7 and type 8 RFE configurations. Each row is a `struct rtw_txpwr_lmt_cfg_pair` describing regulatory domain, band, channel width, rate section, channel, and limit.
- It provides thermal power-tracking swing-index lookup tables. The driver selects these by RFE definition, current band/channel, transmit rate family, RF path A/B/C/D, temperature direction, and thermal delta from efuse calibration.
- It defines card enable and disable power state flows as `struct rtw_pwr_seq_cmd` arrays. The MAC power sequence parser executes these arrays during device bring-up and shutdown.

The chunk is pure data plus macro-generated `struct rtw_table` exports. There are no local functions with branches or loops here; control flow is in consumers such as `rtw_parse_tbl_txpwr_lmt()`, `rtw_phy_config_swing_table()`, and `rtw_pwr_seq_parser()`.

## Important APIs, Types, and Data

Transmit power limit data uses `struct rtw_txpwr_lmt_cfg_pair` from `phy.h`:

- `regd`: regulatory domain index.
- `band`: 2.4 GHz versus 5 GHz table group.
- `bw`: channel-width bucket.
- `rs`: rate-section bucket.
- `ch`: channel number or channel-group key.
- `txpwr_lmt`: signed 8-bit transmit power limit value; in these tables `63` appears as a sentinel/high cap in many unsupported or unconstrained combinations.

`RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` and `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type8)` produce exported `struct rtw_table` objects named `rtw8814a_txpwr_lmt_type7_tbl` and `rtw8814a_txpwr_lmt_type8_tbl`. Those objects set `.data` to the raw array, `.size` to `ARRAY_SIZE()`, and `.parse` to `rtw_parse_tbl_txpwr_lmt`.

Power tracking data is organized around `struct rtw_pwr_track_tbl` from `main.h`. `RTW_PWR_TRK_TBL_SZ` is 30, and each lookup table maps a clamped thermal delta to a positive or negative swing index. For 5 GHz, `RTW_PWR_TRK_5G_NUM` is 3, so each path/direction has three sub-bands selected by the current channel group. For 2.4 GHz, there are separate OFDM and CCK tables per RF path:

- 5 GHz path tables use path suffixes `5ga`, `5gb`, `5gc`, and `5gd` for RF paths A, B, C, and D, with `_n` and `_p` variants for negative and positive temperature compensation.
- 2.4 GHz OFDM tables use `2ga`, `2gb`, `2gc`, and `2gd`, again split into `_n` and `_p`.
- 2.4 GHz CCK tables use `2g_cck_a`, `2g_cck_b`, `2g_cck_c`, and `2g_cck_d`, split into `_n` and `_p`.
- Exported aggregate structs in this chunk are `rtw8814a_rtw_pwrtrk_tbl`, `rtw8814a_rtw_pwrtrk_type0_tbl`, `rtw8814a_rtw_pwrtrk_type2_tbl`, `rtw8814a_rtw_pwrtrk_type5_tbl`, `rtw8814a_rtw_pwrtrk_type7_tbl`, and `rtw8814a_rtw_pwrtrk_type8_tbl`.

Power sequence data uses `struct rtw_pwr_seq_cmd` from `main.h`:

- `offset`: MAC or bus-local register offset, or delay duration for delay commands.
- `cut_mask`: hardware cut mask; all commands in this chunk use `RTW_PWR_CUT_ALL_MSK`.
- `intf_mask`: interface selector such as `RTW_PWR_INTF_ALL_MSK`, `RTW_PWR_INTF_USB_MSK`, or `RTW_PWR_INTF_PCI_MSK`.
- `base`: register base; this chunk uses `RTW_PWR_ADDR_MAC` for actual writes/polls and `0` on end markers.
- `cmd`: `RTW_PWR_CMD_WRITE`, `RTW_PWR_CMD_POLLING`, `RTW_PWR_CMD_DELAY`, or `RTW_PWR_CMD_END`.
- `mask` and `value`: bit mask and desired value for write/poll commands, or delay unit for delay commands.

The internal sequence arrays are `init_power_on_8814a[]`, `trans_carddis_to_cardemu_8814a[]`, `trans_cardemu_to_act_8814a[]`, `trans_act_to_cardemu_8814a[]`, and `trans_cardemu_to_carddis_8814a[]`. The exported flow arrays are pointer lists terminated by `NULL`.

## Control Flow

Transmit power limit control flow is indirect. `rtw8814a.c` maps each supported RFE option to a `struct rtw_rfe_def` containing a power-limit table pointer. For RTL8814A, RFE option 0 uses `rtw8814a_txpwr_lmt_type0_tbl`, while RFE option 1 uses `rtw8814a_txpwr_lmt_type1_tbl`; the type 7 and type 8 tables in this chunk are exported for board configurations declared in the table header and for possible reuse by downstream or future RFE mappings. When a selected table is loaded, `rtw_parse_tbl_txpwr_lmt()` walks every `rtw_txpwr_lmt_cfg_pair`, calls `rtw_phy_set_tx_power_limit()` with the six row fields, records which regulatory domains were present, and fills missing domains from an alternative domain or worldwide defaults.

Power tracking flow starts from the selected `rtw_rfe_def->pwr_track_tbl`. `rtw_phy_config_swing_table()` inspects `rtwdev->hal.current_channel` and `rtwdev->dm_info.tx_rate`. On 2.4 GHz CCK rates it points each RF path at the CCK tables; on 2.4 GHz non-CCK rates it points at the OFDM tables; on 5 GHz it selects one of the three 5 GHz sub-band table sets. Later, `rtw_phy_pwrtrack_get_delta()` clamps the temperature delta to `RTW_PWR_TRK_TBL_SZ - 1`, and `rtw_phy_pwrtrack_get_pwridx()` indexes the selected positive or negative table for the effective transmit power adjustment.

Power sequence control flow is executed by `rtw_pwr_seq_parser()`. The chip info for RTL8814A assigns `.pwr_on_seq = card_enable_flow_8814a` and `.pwr_off_seq = card_disable_flow_8814a`. The parser determines the active HCI interface mask from PCIE/USB/SDIO, derives a cut mask from the chip cut version, iterates each sub-sequence until a `NULL` pointer, and then iterates commands until `RTW_PWR_CMD_END`. Commands whose interface or cut mask does not match are skipped. Write commands read-modify-write an 8-bit register, polling commands wait until `(reg & mask) == value`, and delay commands call `udelay()` or `mdelay()`.

The enable flow is:

- `init_power_on_8814a[]`: for USB, set BIT(1) at MAC offset `0x10c2`, then end.
- `trans_carddis_to_cardemu_8814a[]`: move card-disable to card-emulation by setting/clearing bits at offsets `0x0012`, `0x0015`, `0x0023`, `0x0046`, `0x0062`, and interface-specific PCI registers including `0x0005`, `0x0301`, and `0x0071`.
- `trans_cardemu_to_act_8814a[]`: clear suspend-related bits, poll offset `0x0006` BIT(1), program `0x00f0`, `0x0081`, set BIT(0) at `0x0005`, then poll BIT(0) clear at `0x0005`.

The disable flow is:

- `trans_act_to_cardemu_8814a[]`: write several active-state MAC registers (`0x0c00`, `0x0e00`, `0x1002`, `0x001f`, `0x0007`, `0x0005`) with a one-microsecond delay and additional USB-specific low-power bits at `0x0008`, `0x0066`, `0x0041`, `0x0042`, and `0x004e`, then poll BIT(1) clear at `0x0005`.
- `trans_cardemu_to_carddis_8814a[]`: transition from card-emulation to card-disable by programming offsets `0x0003`, `0x0080`, `0x0081`, `0x0045`, `0x0046`, `0x0047`, `0x0015`, `0x0012`, `0x0023`, `0x0008`, `0x0007`, `0x001f`, `0x0020`, `0x0021`, `0x0076`, `0x0091`, `0x0070`, and `0x0005`.

## State and Persistence

All transmit power limit tables are compile-time `static const` data, except for the macro-emitted `const struct rtw_table` wrappers. Once parsed, their values populate mutable arrays in `struct rtw_hal`, including 2.4 GHz and 5 GHz per-regulatory-domain/channel-width/rate-section/channel power limits. Those cached limits persist in the driver until reinitialized by chip bring-up or another table load.

All power tracking leaf arrays are `static const u8` data. The exported `struct rtw_pwr_track_tbl` objects hold pointers into those arrays and have no mutable local state. Runtime state lives in `rtwdev`: efuse thermal calibration values, EWMA thermal averages, current channel, current TX rate, selected RFE definition, and the `struct rtw_swing_table` pointers configured from these constants. The lookup tables are therefore persistent calibration policy, while actual thermal tracking state changes dynamically with temperature sampling.

The power sequence arrays are immutable command scripts. Their effects persist in hardware registers and device power state, not in this file. The parser skips commands by interface mask, so a PCIe device and a USB device execute different subsets of the same sequences. Polling commands can block bring-up/shutdown until hardware reaches the expected state or the parser returns `-EBUSY`.

## Dependencies and Integration Points

This chunk depends on declarations from `main.h`, `phy.h`, and `rtw8814a_table.h`. `BIT()`, `ARRAY_SIZE()`, `RTW_PWR_*` masks, `RTW_PWR_TRK_*` constants, `struct rtw_table`, `struct rtw_pwr_track_tbl`, `struct rtw_pwr_seq_cmd`, and `struct rtw_txpwr_lmt_cfg_pair` are all defined outside this file.

The table header exports the type 7 and type 8 transmit-power-limit table wrappers, all six power-tracking aggregate tables, and the card enable/disable flow arrays. `rtw8814a.c` integrates the exported enable/disable flows into `rtw8814a_hw_spec` and maps RFE definitions to selected baseband power-group, transmit-power-limit, and power-tracking tables. In the visible consumer code, only RFE options 0 and 1 are wired for RTL8814A, but this table file exports a wider set of board-type data.

`phy.c` consumes the transmit-power-limit wrappers through `rtw_load_table()` and `rtw_parse_tbl_txpwr_lmt()`. It consumes power-tracking tables through `rtw_phy_config_swing_table()` and `rtw_phy_pwrtrack_get_pwridx()`.

`mac.c` consumes power sequence arrays through `rtw_pwr_seq_parser()`, which is called from MAC power-on/power-off paths using `chip->pwr_on_seq` and `chip->pwr_off_seq`. That parser performs hardware register writes and polling through the rtw88 register accessors.

Hardware integration is direct and sensitive: the power sequences touch RTL8814A MAC power-control registers, USB-specific power bits, and PCIe-specific registers. The power-limit and power-tracking tables control RF transmit power behavior across regulatory domains, channel groups, bandwidths, rate sections, RF paths, and board layouts.

## Risks

- The transmit power limit rows are dense numeric data with no per-row names. A swapped field, missing row, or incorrect sentinel value can silently produce wrong regulatory limits or fallback behavior.
- `63` appears frequently as a cap/sentinel-like value in the power-limit tables. Consumers treat it as a normal `s8` table value, so interpretation relies on surrounding rtw88 power-limit logic and chip maximum power index.
- This chunk starts inside `rtw8814a_txpwr_lmt_type7[]`. File-level review must merge with the previous chunk to validate that type 7 has a complete initializer and consistent row coverage.
- Type 7 and type 8 board tables differ materially. Accidentally mapping an RFE option to the wrong table would alter both regulatory power limits and thermal compensation behavior for a board variant.
- Power tracking arrays must have exactly `RTW_PWR_TRK_TBL_SZ` entries and 5 GHz arrays must have exactly `RTW_PWR_TRK_5G_NUM` rows. The compiler catches many size mismatches because dimensions are explicit, but semantically wrong values or path ordering errors still compile.
- The path naming is reversed relative to common A-to-D listing in some places: aggregate struct fields map RF path A to `5ga`/`2ga`, B to `5gb`/`2gb`, C to `5gc`/`2gc`, and D to `5gd`/`2gd`. A generator or manual edit that changes suffixes can miscalibrate one or more chains.
- Power sequence register ordering is hardware-critical. Reordering writes, changing delays, or changing poll masks can leave the device stuck in card-emulation, fail bring-up, or fail low-power shutdown.
- Interface masks must remain precise. USB-only commands in `init_power_on_8814a[]` and `trans_act_to_cardemu_8814a[]`, and PCI-only commands in `trans_carddis_to_cardemu_8814a[]`, should not be broadened without hardware evidence.
- Poll failures in `rtw_pwr_seq_parser()` surface as `-EBUSY`; repeated failures would likely appear as probe, resume, or shutdown failures rather than compile-time errors.
- There are no comments in the table data explaining source provenance, units, or board-type differences. Regression review requires comparing against vendor tables, measured RF behavior, or known-good upstream data.

## Test and Validation Signals

Useful static validation:

- Build the driver with this table file enabled and treat missing symbols or initializer-size warnings as hard failures.
- Confirm `rtw8814a_table.h` declarations match exported symbols: `rtw8814a_txpwr_lmt_type7_tbl`, `rtw8814a_txpwr_lmt_type8_tbl`, the six `rtw8814a_rtw_pwrtrk*` aggregate tables, and both card flow arrays.
- Check that every `struct rtw_pwr_track_tbl` field required by `rtw_phy_config_swing_table()` is non-NULL for all exported board types.
- Check each `RTW_PWR_TRK_TBL_SZ` table has 30 values and each 5 GHz table has three rows.
- Compare type 7 and type 8 transmit-power-limit row counts and row coverage against the generated manifest or vendor source.

Useful runtime and hardware validation:

- Probe RTL8814A over supported PCIe and USB paths and verify `card_enable_flow_8814a[]` completes without power-polling errors.
- Exercise suspend/resume, module unload/reload, and device removal to verify `card_disable_flow_8814a[]` reaches card-disable state and does not leave the device wedged for the next probe.
- Enable rtw88 regulatory/debug logging and verify `rtw_parse_tbl_txpwr_lmt()` does not report unexpected missing regulatory domains for a selected RFE table.
- Test 2.4 GHz CCK, 2.4 GHz OFDM, and 5 GHz low/mid/high channel groups so `rtw_phy_config_swing_table()` selects every major table family.
- Heat/cool the device or emulate thermal deltas where possible and verify `rtw_phy_pwrtrack_get_delta()` and `rtw_phy_pwrtrack_get_pwridx()` stay within bounds and do not log "power track table overflow", "swing table not configured", or "invalid swing table index".
- Measure conducted or radiated transmit power across board/RFE variants, RF paths A-D, bandwidths, rates, and representative channels to catch wrong path mapping or incorrect board-type table selection.
- Validate regulatory behavior for channels where the tables use high-cap values, especially 5 GHz channel groups around 149, 153, 157, 161, and 165 where many rows in this chunk differ from lower-band rows.
