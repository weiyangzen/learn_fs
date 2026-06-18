# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004912`: lines 1-11729, `Docs/researches/chunks/subset-b-004912_research.md`
- `subset-b-004913`: lines 11730-21777, `Docs/researches/chunks/subset-b-004913_research.md`
- `subset-b-004914`: lines 21778-33742, `Docs/researches/chunks/subset-b-004914_research.md`
- `subset-b-004915`: lines 33743-43411, `Docs/researches/chunks/subset-b-004915_research.md`
- `subset-b-004916`: lines 43412-46105, `Docs/researches/chunks/subset-b-004916_research.md`

## Chunk Research

### subset-b-004912: lines 1-11729

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 1-11729

## Scope

This chunk covers the first 11,729 lines of the Realtek `rtw88` RTL8822C table source. The covered range contains:

- Includes for `main.h`, `phy.h`, `rtw8822c.h`, and `rtw8822c_table.h`.
- The empty `rtw8822c_mac[]` table and its `rtw8822c_mac_tbl` descriptor.
- The full `rtw8822c_agc[]` gain table and descriptor.
- The full `rtw8822c_bb[]` baseband table and descriptor.
- The full `rtw8822c_bb_pg_type0[]` power-by-rate group table and descriptor.
- The beginning of `rtw8822c_rf_a[]`, from its first RF register writes through line 11,729. RF path A continues beyond this chunk and is declared as `rtw8822c_rf_a_tbl` only later in the file.

The file is almost entirely generated hardware-programming data. The only C constructs in this range are static table definitions and table-declaration macros; there are no local functions or dynamic algorithms in this source chunk.

## Purpose

The purpose of this chunk is to provide the RTL8822C PHY initialization payload consumed by the common `rtw88` table loader. The tables encode register-address/data pairs and conditional table opcodes that program MAC, baseband, AGC, transmit power-by-rate offsets, and RF path A defaults for a concrete RTL8822C hardware condition.

The table data is attached to `struct rtw_table` descriptors by macros in `phy.h`:

- `RTW_DECL_TABLE_PHY_COND(rtw8822c_mac, rtw_phy_cfg_mac)` creates a descriptor whose parser is `rtw_parse_tbl_phy_cond()` and whose write callback is `rtw_phy_cfg_mac()`.
- `RTW_DECL_TABLE_PHY_COND(rtw8822c_agc, rtw_phy_cfg_agc)` creates a conditional table whose matched entries are written with 32-bit AGC register writes.
- `RTW_DECL_TABLE_PHY_COND(rtw8822c_bb, rtw_phy_cfg_bb)` creates a conditional baseband table whose matched entries are written as 32-bit BB writes, with special delay pseudo-addresses.
- `RTW_DECL_TABLE_BB_PG(rtw8822c_bb_pg_type0)` creates a power-by-rate parser table instead of a direct register-write table.

In the 8822C chip descriptor, `rtw8822c_hw_spec` points `.mac_tbl`, `.agc_tbl`, and `.bb_tbl` at these descriptors. It also maps RF tables in reverse path order as `{ &rtw8822c_rf_b_tbl, &rtw8822c_rf_a_tbl }`, so the RF table data in this chunk is ultimately loaded through the common RF table loop once the full file has provided the RF path A descriptor.

## Important APIs, Types, and Table Shapes

`struct rtw_table` in `main.h` is the integration contract. It stores a data pointer, an element count, a parser callback, an optional write callback, and an RF path. `rtw_load_table()` simply calls `tbl->parse(rtwdev, tbl)`.

The `u32` PHY tables are interpreted by `rtw_parse_tbl_phy_cond()` as an array of `union phy_table_tile`. Each tile is two 32-bit words:

- As `struct phy_cfg_pair`, the words are `{ addr, data }` and are sent to the table's `do_cfg` callback when the current condition block is matched.
- As `{ struct rtw_phy_cond cond; struct rtw_phy_cond2 cond2; }`, the same two words can encode positive and negative conditional branch markers.

`struct rtw_phy_cond` bitfields encode RFE option, interface type, package, platform, cut version, branch kind, and whether the tile is a positive or negative condition marker. `rtw_phy_setup_phy_cond()` fills the active condition from `hal->cut_version`, `efuse->rfe_option`, package defaults, and HCI type (`PCIE`, `USB`, or `SDIO`). `check_positive()` compares a table condition against that active runtime condition.

`struct rtw_phy_pg_cfg_pair` is used by `rtw8822c_bb_pg_type0[]`. Each entry carries `band`, `rf_path`, `tx_num`, `addr`, `bitmask`, and `data`. `rtw_parse_tbl_bb_pg()` does not write these entries directly to hardware; it decodes the packed register data into per-rate power offsets and stores them in `hal->tx_pwr_by_rate_offset_2g` or `hal->tx_pwr_by_rate_offset_5g`.

## Covered Tables

`rtw8822c_mac[]` is empty in this chip table. It still has a descriptor, so the generic loader can call `rtw_load_table(chip->mac_tbl)` without special-casing 8822C. Because `ARRAY_SIZE(rtw8822c_mac)` is zero, `rtw_parse_tbl_phy_cond()` sees no tiles and performs no writes.

`rtw8822c_agc[]` spans lines 15-1856. It is dominated by writes to AGC-table selection/programming registers such as `0x1D90`, with conditional blocks for many RFE/interface/cut cases. The first repeated pattern programs index-like values through `0x1D90` across conditions including `0x83000000`, `0x90000015`, `0x90000016`, `0xA0000000`, and `0xB0000000`. Later entries use `0x1D94`, `0x1D70`, `0x1E84`, and several baseband addresses. At runtime, matched entries are passed to `rtw_phy_cfg_agc()`, which issues `rtw_write32(rtwdev, addr, data)`.

`rtw8822c_bb[]` spans lines 1860-3301. This table programs the baseband register set before the AGC and RF tables finish initialization. It includes conditional blocks and direct writes to baseband addresses such as `0x1830`, `0x4130`, `0x1884`, `0x4184`, `0x1C94`, `0x1C98`, `0x1D70`, `0x1D90`, `0x1D94`, `0x1E84`, `0x1EE8`, and `0xC0C`. Matched entries call `rtw_phy_cfg_bb()`, which writes 32-bit values except for pseudo-addresses `0xfe`, `0xfd`, `0xfc`, `0xfb`, `0xfa`, and `0xf9`, which encode required sleeps or delays.

`rtw8822c_bb_pg_type0[]` spans lines 3305-3352. It defines power-by-rate offsets for type-0 RFE data over 2.4 GHz and 5 GHz bands, RF paths 0 and 1, and one- or two-transmit-stream cases. The register addresses are mainly `0x0c20`-`0x0c4c` for path A and `0x0e20`-`0x0e4c` for path B, with full `0xffffffff` bitmasks and packed offset words such as `0x484c5054`, `0x54585858`, and `0x383c4044`. These values seed HAL transmit-power offset arrays rather than immediate hardware state.

`rtw8822c_rf_a[]` begins at line 3356 and continues past this chunk. The covered portion starts with unconditional RF writes to registers such as `0x000`, `0x018`, `0x093`, and `0x0DE`, then many conditional sections for RF registers including `0x08E`, `0x085`, `0x0EE`, `0x0EF`, `0x033`, `0x03E`, and `0x03F`. The heavy repetition of `0x033`, `0x03E`, and `0x03F` indicates indirect RF-table programming: `0x033` selects an internal RF table index, while following `0x03E`/`0x03F` writes provide values for those selected slots. The chunk ends mid-array after a `0x94000016` conditional branch and before the `rtw8822c_rf_a[]` closing brace and declaration macro.

## Control Flow

The runtime load path starts in `rtw8822c_phy_set_param()` in `rtw8822c.c`. After powering on BB/RF domains and running pre-initialization, it calls `rtw_phy_load_tables(rtwdev)`.

`rtw_phy_load_tables()` performs the common sequence:

1. Resolve the board/RFE definition with `rtw_get_rfe_def()`.
2. Load `chip->mac_tbl`.
3. Load `chip->bb_tbl`.
4. Load `chip->agc_tbl`.
5. Optionally load an RFE-specific `agc_btg_tbl`.
6. Load RF calibration initialization with `rtw_load_rfk_table()`.
7. Iterate `rf_path < rtwdev->hal.rf_path_num` and load `chip->rf_tbl[rf_path]`.

For the `u32` tables in this chunk, `rtw_parse_tbl_phy_cond()` walks two words at a time. Positive condition tiles remember the candidate condition, negative condition tiles evaluate it, `ELSE` and `ENDIF` update the parser state, and ordinary address/data tiles are written only when the current branch is matched. This means the table itself carries the board/cut/interface branching, while the driver code only supplies the current `hal->phy_cond`.

For `rtw8822c_bb_pg_type0[]`, the parser is different. `rtw_parse_tbl_bb_pg()` walks typed `struct rtw_phy_pg_cfg_pair` entries and calls `rtw_phy_store_tx_power_by_rate()`, which decodes packed per-rate offsets and stores them into `struct rtw_hal`. No conditional branch opcodes are involved in this specific table.

## State and Persistence Behavior

The static arrays in this file are immutable kernel data. The persistent effects are hardware and HAL state established during initialization.

The MAC table in this chunk has no state effect because it is empty. The BB and AGC tables program device registers that persist until reset, power cycling, suspend/resume reinitialization, or later driver calibration code overwrites them. The RF path A entries program RF registers through `rtw_write_rf()` when the RF table is loaded; those settings are path-specific and affect analog/RF operation, gain behavior, channel/radio setup, and calibration baselines.

The power-group table persists in software HAL arrays. Its values feed later transmit-power calculations and are combined with regulatory limits, SAR limits, thermal tracking, channel, bandwidth, rate section, and RF path decisions. Incorrect values here may not show up as a direct register-write failure, but they can later produce wrong transmit-power indexes.

The conditional table state is transient inside the parser: `is_matched`, `is_skipped`, `pos_cond`, and `pos_cond2` are reset for each table load. The active condition stored in `hal->phy_cond` and `hal->phy_cond2` is set outside this file and reused across all conditional tables.

## Dependencies and Integration Points

This chunk depends on:

- `main.h` for `struct rtw_table`, `struct rtw_chip_info`, `struct rtw_phy_cond`, `struct rtw_phy_cond2`, RF path enums, and HAL state.
- `phy.h` for table declaration macros and parser/write callback declarations.
- `phy.c` for `rtw_parse_tbl_phy_cond()`, `rtw_parse_tbl_bb_pg()`, `rtw_phy_cfg_mac()`, `rtw_phy_cfg_agc()`, `rtw_phy_cfg_bb()`, and `rtw_phy_cfg_rf()`.
- `rtw8822c_table.h` for extern declarations consumed by the chip descriptor and 8822C-specific code.
- `rtw8822c.c` for `rtw8822c_hw_spec`, `rtw8822c_phy_set_param()`, RF/DPK calibration flow, and the final table wiring.

Important integration points are 8822C probe/initialization, resume paths that re-run PHY setup, RF calibration setup, RFE option handling from efuse, and transmit-power setup. The data also has regulatory integration indirectly through power-by-rate storage: the values from `rtw8822c_bb_pg_type0[]` are later constrained by power-limit tables and regulatory logic before final transmit power is applied.

## Risks

- The `u32` conditional tables rely on exact two-word alignment. Adding or deleting one word corrupts all following condition and register-pair interpretation.
- Conditional marker values such as `0x83000000`, `0x90000015`, `0xA0000000`, and `0xB0000000` are not ordinary register addresses even though they live in the same array. Misclassifying them as writes would program nonsensical addresses; misencoding them would select the wrong branch for a cut, interface, package, or RFE option.
- The BB write callback treats several small addresses as delay opcodes. Accidentally changing a delay pseudo-address to a normal address, or vice versa, can break hardware timing during initialization.
- RF path A is split across chunk boundaries for this research item. Any final merged research must join this document with later chunks before drawing conclusions about the full `rtw8822c_rf_a[]` table or its declaration macro.
- The RF path table order in `rtw8822c_hw_spec` is `{ B, A }`, while this chunk contains path A data. Reviewers should not assume source order and chip table order match.
- Power-by-rate data is packed and decoded later. Wrong `band`, `rf_path`, `tx_num`, address, bitmask, or packed offset data can create subtle rate/path/channel-specific transmit-power errors rather than immediate initialization failures.
- The file is generated-style hardware data with little semantic naming. Copy/paste drift across repeated lane/path/RFE blocks is difficult to detect by code review alone.

## Test Signals

Useful validation signals include:

- Build coverage for `rtw88`, proving the array initializers, declaration macros, and extern declarations remain consistent.
- Boot/probe logs for RTL8822C devices showing successful PHY table load, no unsupported RFE errors, no table parser warnings, and no RF write failures.
- Runtime association tests on PCIe/USB/SDIO RTL8822C variants and on boards with different efuse RFE options, since conditional branches are selected from interface type and RFE data.
- RF sanity tests: scan sensitivity, association stability, throughput on 2.4 GHz and 5 GHz, path diversity/2x2 operation, and behavior after suspend/resume.
- Transmit-power validation against regulatory expectations, including per-rate and per-channel power-index checks, because `rtw8822c_bb_pg_type0[]` seeds the software power-by-rate offsets.
- Calibration and thermal tracking traces around RFK/DPK/LCK/IQK flows, since this chunk's BB/AGC/RF defaults establish the baseline that later calibration code adjusts.

### subset-b-004913: lines 11730-21777

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 11730-21777

## Scope

This chunk covers a middle section of the Realtek RTL8822C hardware table file. It starts inside the large `static const u32 rtw8822c_rf_a[]` radio table and continues through the first portion of `static const u32 rtw8822c_rf_b[]`. The line range is entirely table-driven PHY/RF initialization data: it contains no C functions, but it is executable configuration data consumed by the shared rtw88 PHY table parser.

Within the requested range, `rtw8822c_rf_a[]` runs from the chunk start through line 21352 and is exported at line 21354 by `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_a, A)`. `rtw8822c_rf_b[]` begins at line 21356 and the requested range ends while still inside that RF-B table, at an RF conditional block that programs RF register `0x0ef`, selector register `0x033`, and data register `0x03f`.

## Purpose

The data programs RTL8822C RF-path radio defaults for board/interface/RFE variants. It supplies per-condition RF register writes for synthesizer, gain, tracking, calibration, and internal table selector state. The table is part of the radio bring-up sequence used when the driver loads PHY tables for an RTL8822C device.

The chunk is dominated by repeated conditional blocks keyed by packed condition words such as `0x8f000000`, `0x9f000001`, `0x91000001`, `0x93000015`, `0x95000016`, `0xA0000000`, and `0xB0000000`. These encode if/elif/else/endif control for cut, package, interface, platform, and RFE option matching. When a condition matches the current hardware, the following register/value pairs are sent to the configured RF path.

The most visible RF programming pattern in this range is indirect RF table access through registers:

- `0x033`, used as an index/selector in many blocks.
- `0x03e`, used as a mask/control companion in portions of the RF-A table.
- `0x03f`, used as the data/value payload for the selected entry.
- `0x0ed`, `0x0ee`, and `0x0ef`, used to select or gate internal RF banks/pages before `0x033`/`0x03f` writes.
- `0x0fe`, used as a delay pseudo-register in the RF table parser.

## Important APIs, Types, and Data

The directly relevant data objects in this file are:

- `rtw8822c_rf_a[]`: a large `u32` array declared earlier at line 3356 and closed in this chunk at line 21352. This chunk contains a substantial middle and tail portion of that path-A radio initialization stream.
- `rtw8822c_rf_a_tbl`: the exported `struct rtw_table` generated by `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_a, A)`. The macro sets `.parse = rtw_parse_tbl_phy_cond`, `.do_cfg = rtw_phy_cfg_rf`, and `.rf_path = RF_PATH_A`.
- `rtw8822c_rf_b[]`: a second `u32` array beginning at line 21356. The requested chunk includes only its initial section, not the whole RF-B table.

The shared table machinery is defined outside this file:

- `struct rtw_table` in `main.h` carries a data pointer, element count, parser callback, configuration callback, and RF path.
- `RTW_DECL_TABLE_RF_RADIO()` in `phy.h` wraps an RF array as a conditional PHY table using `rtw_phy_cfg_rf`.
- `struct rtw_phy_cond` and `struct rtw_phy_cond2` in `main.h` overlay packed `u32` condition words. On little-endian builds, the first word carries RFE, interface, package, platform, cut, branch, negative-condition, and positive-condition bits.
- `union phy_table_tile` and `struct phy_cfg_pair` in `phy.c` make each two-word table tile either a conditional control record or an address/data pair.
- `rtw_parse_tbl_phy_cond()` walks the table, tracks active if/elif/else/endif state, calls `check_positive()` against `rtwdev->hal.phy_cond`, and applies matching address/data pairs.
- `rtw_phy_cfg_rf()` handles RF table entries: `0xffe` sleeps 50 ms, `0xfe` sleeps about 100 us, and all other addresses are written through `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` followed by a 1 us delay.

The RTL8822C chip registration in `rtw8822c.c` is an important integration point. `rtw8822c_hw_spec.rf_tbl` is `{&rtw8822c_rf_b_tbl, &rtw8822c_rf_a_tbl}`, so runtime RF path index 0 loads the table named RF-B and runtime RF path index 1 loads the table named RF-A. The macro-generated table still carries the RF path enum from its declaration, so this unusual ordering is intentional driver data and should not be normalized casually.

## Control Flow

The chunk executes only when the driver loads PHY tables for an RTL8822C device. The higher-level flow is:

1. Device setup identifies RTL8822C and fills `rtwdev->chip = &rtw8822c_hw_spec`.
2. `rtw_phy_setup_phy_cond()` computes `hal->phy_cond` from hardware cut, package type, HCI type, platform, and efuse RFE option.
3. `rtw_phy_load_tables()` loads the MAC, BB, AGC, optional AGC-BTG, RFK-init table, and then iterates `rf_path` from `0` to `rtwdev->hal.rf_path_num - 1`.
4. For each enabled RF path, it selects `chip->rf_tbl[rf_path]` and calls `rtw_load_table()`.
5. `rtw_parse_tbl_phy_cond()` interprets two `u32` values at a time. Conditional records update match state; normal records are passed to `rtw_phy_cfg_rf()`.
6. `rtw_phy_cfg_rf()` writes the selected RF path register or performs a table-encoded delay.

Inside this chunk, control flow is data encoded. The repeated sequence is: positive condition tile, negative condition tile, one or more RF writes, then a branch or endif marker. In the raw table this appears as four-value condition records such as `0x95000003, 0x00000000, 0x40000000, 0x00000000`, followed by register/data pairs. The first word encodes a positive condition. The `0x40000000` word encodes the negative half used by the parser to decide whether the pending positive condition is active.

The table also contains unconditional blocks between condition ranges. In RF-A, the tail writes RF `0x092` twice, inserts four `0x0fe` delay records, rewrites `0x092`, and then programs RF `0x08f`, `0x088`, `0x019`, and several `0x0ef`/`0x033`/`0x03e`/`0x03f` masked internal entries before closing the table. RF-B then starts with common writes to `0x000`, `0x018`, and `0x093`, selects page `0x0ef = 0x00080000`, sets selector `0x033 = 1`, and begins its own conditional set of `0x03f` writes.

## State and Persistence

The chunk persists state in hardware RF registers, not in normal C objects. Once parsed, matching entries program the RTL8822C RF path selected by the table. These values remain active until later RF reconfiguration, channel changes, calibration routines, power transitions, or another table load overwrites them.

There is no heap allocation, file I/O, firmware buffer mutation, or explicit driver-side persistence in this chunk. The only software state involved is parser state (`is_matched`, `is_skipped`, pending positive condition fields) and the precomputed `hal->phy_cond`/`hal->phy_cond2` used to decide which conditional blocks apply.

The RF tables are compiled into the driver image as `static const u32` arrays. Their externally visible form is the macro-generated `const struct rtw_table` objects declared in `rtw8822c_table.h` and referenced by `rtw8822c_hw_spec`.

## Dependencies and Integration Points

This chunk depends on the rtw88 table parser and RF access layer:

- `rtw_write_rf()` and the chip-specific RF address information in `rtw8822c_hw_spec` provide the actual RF register transport.
- `rtw_phy_cfg_rf()` supplies the per-entry RF write and delay semantics.
- `rtw_parse_tbl_phy_cond()` supplies condition interpretation and decides whether a raw table pair is a branch marker or a real RF write.
- `rtw_phy_setup_phy_cond()` ties table branches to efuse and bus state, especially `efuse->rfe_option` and the HCI type (`PCIE`, `USB`, or `SDIO`).
- `rtw_phy_load_tables()` integrates these RF tables into the broader PHY initialization order after MAC/BB/AGC and RFK-init table loads.
- `rtw8822c_table.h` exposes `rtw8822c_rf_a_tbl` and `rtw8822c_rf_b_tbl` to `rtw8822c.c`.

The chunk is also coupled to Realtek vendor table encoding. Magic values such as `0x8f000000`, `0x95000016`, `0xA0000000`, and `0xB0000000` are not ordinary RF registers when parsed as condition tiles. Conversely, values such as `0x033` and `0x03f` are ordinary RF register writes when the parser is in matched state. Correct interpretation requires the two-word tile alignment preserved by `struct rtw_table.size` and `tbl->size / 2` parsing.

## Risks

- Table alignment is critical. Adding or removing a single `u32` would desynchronize the two-word tile parser, turning condition words into RF writes or RF writes into bogus conditions.
- The RF-A/RF-B naming and chip-spec ordering are easy to misread. `rtw8822c_hw_spec.rf_tbl` loads `{RF-B, RF-A}` by path index, while the table macros encode explicit `RF_PATH_B` and `RF_PATH_A`. Refactors that "fix" the order without hardware validation could swap radio-path initialization.
- Conditional words are opaque. Many blocks differ only by cut/package/RFE/interface condition and small RF data changes. A copy/paste error in one condition can silently apply the wrong front-end or package tuning.
- The parser has no per-write failure propagation here. `rtw_phy_cfg_rf()` calls the RF write helper and then delays, but table loading itself does not return a status for this chunk. Bad RF transport or unsupported RF state may surface later as calibration, association, throughput, or regulatory power symptoms.
- RF register sequences include internal page/bank selectors (`0x0ed`, `0x0ee`, `0x0ef`) followed by indexed writes through `0x033`/`0x03f`. Missing a page reset such as `0x0ef, 0x00000000` can leave later writes targeting the wrong internal RF bank.
- Delay pseudo-registers are data-dependent. RF-A uses `0x0fe` delay entries near the table tail. Removing or reordering them can violate hardware settling requirements that are not expressed in code.
- The chunk is generated/vendor-style data with little semantic naming. Static review cannot prove the numeric values are correct; validation needs real RTL8822C hardware variants.

## Test and Validation Signals

Useful validation is hardware/integration oriented:

- Boot RTL8822C devices across PCIe/USB/SDIO variants and verify `rtw_phy_load_tables()` completes without RF access warnings.
- Exercise boards with different efuse RFE options, especially RFE option 5 because the 8822C RFE table has a distinct type-5 power-limit definition elsewhere in the same table file.
- Confirm both RF paths are active on 2x2 devices and that path ordering matches expected RSSI/TX behavior despite the `{rf_b, rf_a}` table order in `rtw8822c_hw_spec`.
- Test 2.4 GHz and 5 GHz association, throughput, channel switching, and power-save transitions after cold boot and resume, because these table values set the baseline RF state reused by later channel/calibration code.
- Watch PHY/RF debug output around table loading and calibration for write failures, unexpected RF path masks, IQK/LCK/DPK anomalies, or poor EVM/sensitivity.
- Compare RF register dumps after table load against a known-good RTL8822C baseline for the same cut/package/RFE/interface tuple.
- Run suspend/resume and module reload loops to catch state that only fails when RF tables are replayed after prior radio state.

### subset-b-004914: lines 21778-33742

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 21778-33742

## Scope

This chunk covers a large middle section of the Realtek `rtw88` 8822C PHY table file. The range is entirely inside the static `u32 rtw8822c_rf_b[]` array, which starts at line 21356 and is exported later as `rtw8822c_rf_b_tbl` by `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)`. The next top-level table is `rtw8822c_txpwr_lmt_type0[]` at line 39824, so this chunk is not standalone code; it is a slice of the path-B RF register programming script.

The assigned lines begin after a conditional block header at line 21774 and continue through another repeated conditional section ending in the next chunk. The data is a sequence of two-word address/data pairs interpreted as either RF register writes or PHY conditional-table control words. Within this range, the dominant write pattern selects RF register `0x033` and writes coefficient values through RF register `0x03f`; later sections also use RF register `0x03e`, RF register `0x030`, RF register `0x063`, and bank/select register `0x0ef`. The visible conditional markers include many `0x8f000000`, `0x9f000001`, `0x91...`, `0x92...`, `0x93...`, `0x94...`, `0x95...`, `0xA0000000`, and `0xB0000000` words.

## Purpose

The purpose of this chunk is to provide chip-specific RF path B initialization values for RTL8822C devices. During PHY bring-up the driver walks this table and applies the matching rows to the second RF chain. These values initialize radio-internal lookup/bank entries used by path-B analog/RF behavior. The repeated `0x033`/`0x03f` sequences look like index/data programming for RF-internal tables: `0x033` selects an index or subentry and `0x03f` supplies the value. The repeated groups for cut/package/RFE-like condition keys allow different board or silicon variants to receive different RF values without procedural code.

This is hardware bring-up data rather than an algorithm. Its correctness controls RF path B behavior after `rtw_phy_load_tables()` runs, affecting dual-chain receive/transmit behavior, calibration baselines, and later dynamic PHY mechanisms that assume the RF path has already been initialized.

## Important APIs, Types, and Data

The central data item is:

- `static const u32 rtw8822c_rf_b[]`: a flat array of 32-bit words representing address/data pairs plus conditional-table markers.
- `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)`: wraps the array in a `const struct rtw_table` with `.parse = rtw_parse_tbl_phy_cond`, `.do_cfg = rtw_phy_cfg_rf`, and `.rf_path = RF_PATH_B`.

Important shared types and helpers:

- `struct rtw_table` carries the table data pointer, word count, parse callback, configuration callback, and RF path selector.
- `struct rtw_phy_cond` and `struct rtw_phy_cond2` overlay conditional control words. Their fields encode RFE option, interface, package, platform, cut, branch type, and positive/negative condition markers.
- `union phy_table_tile` overlays each two-word tile as either a condition pair or a normal `{addr, data}` configuration pair.
- `rtw_parse_tbl_phy_cond()` interprets the mixed stream, evaluates branch markers, and emits only matching configuration pairs.
- `rtw_phy_cfg_rf()` writes a matching pair with `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` and delays one microsecond after ordinary RF writes. It treats RF pseudo-addresses `0xffe` and `0xfe` as delay commands, although this chunk mainly contains real RF-register pairs and condition markers.

Notable data patterns in this chunk:

- The most common pairs are `0x033` followed by an index-like value, then `0x03f` followed by the corresponding payload.
- Early visible rows program low index ranges such as `0x00000004` through `0x0000001f` with values like `0x000773e8`, `0x000ff3a0`, `0x00000380`, and related variants.
- Later visible rows program higher index ranges such as `0x00000200` through `0x0000028a`, with two families of payloads: a ramp-like set ending around `0x00000cf7`, and a small-value set such as `0x00000005`, `0x00000008`, `0x0000000b`, through `0x00000077`.
- The condition markers repeat across many branch keys, indicating that the same register-programming pattern is specialized by platform/RFE/cut/package combinations rather than being one unconditional sequence.

## Control Flow

The runtime path starts in normal device initialization:

1. Chip setup calls `rtw_phy_setup_phy_cond(rtwdev, hal->pkg_type)`, which builds `hal->phy_cond` from cut version, package, platform, interface type, and `efuse->rfe_option`.
2. `rtw_phy_load_tables()` loads MAC, BB, AGC, optional BTG AGC, RFK init, and then loops over `chip->rf_tbl[rf_path]` for each RF path.
3. In `rtw8822c_hw_spec`, `.rf_tbl = { &rtw8822c_rf_b_tbl, &rtw8822c_rf_a_tbl }`, so the first configured RF slot uses this path-B table and the table wrapper forces `RF_PATH_B`.
4. `rtw_load_table()` calls the table parser. For this table, `rtw_parse_tbl_phy_cond()` walks two `u32` words at a time.
5. Positive conditional markers remember a candidate condition and branch kind. Negative markers cause `check_positive()` to compare that condition with `hal->phy_cond`; `BRANCH_IF`, `BRANCH_ELIF`, `BRANCH_ELSE`, and `BRANCH_ENDIF` semantics decide whether following pairs are active.
6. When the current branch is matched and the tile is a normal pair, `rtw_phy_cfg_rf()` writes the RF register on path B.

There are no local loops or functions in this chunk. All control flow is encoded by the condition words and executed by the generic `rtw88` table loader.

## State and Persistence

The array itself is read-only static kernel data. It does not store runtime state.

The table writes persistent state into the RTL8822C RF path-B register file. These writes remain active until a later RF table load, RF calibration sequence, channel reconfiguration, power-cycle, reset, or explicit RF register update changes the same hardware locations. Because the table uses full `RFREG_MASK` writes, each emitted pair replaces the whole target RF register field as understood by `rtw_write_rf()`.

Branch selection state is transient during parsing (`is_matched`, `is_skipped`, `pos_cond`, and `pos_cond2` inside `rtw_parse_tbl_phy_cond()`), while the hardware-selection inputs persist in `rtwdev->hal.phy_cond` and `rtwdev->hal.phy_cond2`.

## Dependencies and Integration Points

This chunk depends on the broader `rtw88` table infrastructure:

- `phy.h` macros generate the exported `rtw8822c_rf_b_tbl` object and bind it to `rtw_parse_tbl_phy_cond()` plus `rtw_phy_cfg_rf()`.
- `main.h` defines `struct rtw_table`, `struct rtw_phy_cond`, branch encodings, interface encodings, and the inline `rtw_load_table()`.
- `phy.c` supplies the conditional parser and RF configuration callback.
- `rtw8822c.c` wires the table into `rtw8822c_hw_spec.rf_tbl`, alongside RF base/SIPI addresses and the rest of the 8822C chip descriptor.
- Efuse and HAL state provide `rfe_option`, package type, cut version, and HCI interface, which decide which conditional subblocks in this data are applied.

The table integrates with later PHY behavior indirectly. Dynamic mechanisms, DPK/RFK calibration, transmit power programming, path diversity, RSSI handling, and channel changes assume this RF path was initialized with the correct variant-specific base values.

## Risks

- Table alignment is critical. The parser consumes the array as two-word tiles. Adding, deleting, or moving a single `u32` can reinterpret all later data as the wrong address/data or condition pairs.
- Condition markers are opaque and easy to corrupt. Values such as `0x93000015` or `0xA0000000` are not ordinary RF addresses; changing them alters which boards or chip cuts receive following RF writes.
- Path mapping is non-obvious. `rtw8822c_hw_spec.rf_tbl` lists path-B before path-A, while `RTW_DECL_TABLE_RF_RADIO()` fixes this table to `RF_PATH_B`. A mistaken reorder or wrapper path would program the wrong RF chain.
- RF register writes are full-mask writes. Incorrect constants can overwrite undocumented RF state and cause weak sensitivity, transmit impairment, calibration failure, or regulatory power issues.
- There are few software sanity checks. Most bad values will surface only as hardware behavior: failed association, poor RSSI, unstable throughput, failed RF calibration, or path-specific performance asymmetry.
- The chunk boundaries split a single generated hardware table. A final per-file report should reconcile this slice with the preceding and following portions of `rtw8822c_rf_b[]` before drawing conclusions about complete RF path-B initialization.

## Test and Validation Signals

Useful validation is mostly hardware-based:

- Boot/probe an RTL8822C device with PHY debug enabled and confirm `rtw_phy_load_tables()` completes without RF write failures or later calibration warnings.
- Test devices with different RFE options, package/cut values, and host interfaces if available, because this chunk is dominated by conditional branches.
- Compare RF path A and path B performance after initialization: receive sensitivity, RSSI balance, transmit EVM/power, and dual-chain MIMO throughput should not show path-B-only degradation.
- Exercise 2.4 GHz and 5 GHz channels, including channel changes and suspend/resume, to ensure later channel programming and RFK/DPK flows can safely build on these base RF values.
- Watch for kernel logs from `RTW_DBG_PHY`, RFK/DPK status, association failures, and low-throughput symptoms; these are practical signals for malformed RF table data.
- Static validation should check that the `rtw8822c_rf_b[]` word count remains even, condition branches remain paired with their negative/end markers, and the generated `rtw8822c_rf_b_tbl` still uses `rtw_phy_cfg_rf` with `RF_PATH_B`.

### subset-b-004915: lines 33743-43411

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 33743-43411

## Scope

This chunk covers a large static-data region in the Realtek `rtw88` RTL8822C table file. It begins in the late portion of the `rtw8822c_rf_b[]` radio-path-B programming script, includes the end of that array and its `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)` wrapper, then contains the complete `rtw8822c_txpwr_lmt_type0[]` table and the first large portion of `rtw8822c_txpwr_lmt_type5[]`.

The range is not algorithmic C code. It is vendor-derived PHY/RF configuration data consumed by generic `rtw88` table parsers. The beginning is mid-array and the ending is mid-array, so the complete RF-B script and complete type-5 power-limit table require adjacent chunks during merge.

## Purpose

The RF-B portion supplies conditional RF register writes for RTL8822C radio path B. The values are interpreted as address/data pairs plus condition opcodes by `rtw_parse_tbl_phy_cond()`, then applied through `rtw_phy_cfg_rf()`. In this chunk the RF script repeatedly programs RF registers such as `0x033`, `0x03f`, `0x051`, `0x052`, `0x092`, `0x08f`, `0x088`, `0x019`, and `0x0ef`, with conditional branch markers such as `0x8f000000`, `0x9f000001`, `0x91...`, `0x92...`, `0x93...`, `0x94...`, `0x95...`, `0xa0000000`, and `0xb0000000`. These encode hardware-package, interface, board, and RFE-dependent RF initialization branches.

The power-limit portions provide regulatory and board-variant transmit-power ceilings. Each `struct rtw_txpwr_lmt_cfg_pair` row is `{ regd, band, bw, rs, ch, txpwr_lmt }`, where `regd` indexes `RTW_REGD_*`, `band` selects 2.4 GHz or 5 GHz PHY band, `bw` uses `RTW_CHANNEL_WIDTH_*`, `rs` uses rate sections such as CCK, OFDM, HT, and VHT, `ch` is the channel or 5 GHz center-channel bucket, and `txpwr_lmt` is a signed power-index limit. Many rows use `127`, which matches the initialized maximum-power sentinel and effectively means no table-specific tightening after clamping.

`rtw8822c_txpwr_lmt_type0[]` is the default RTL8822C RFE power-limit profile used by RFE definitions 0, 1, 2, 3, 4, and 6. `rtw8822c_txpwr_lmt_type5[]` is the alternate profile used by RFE definition 5; this chunk covers its 2.4 GHz and early 5 GHz entries but stops before the array is complete.

## Important APIs, Types, and Data

Important data and wrappers in this range:

- `rtw8822c_rf_b[]`: `u32` conditional PHY/RF table for radio path B. This chunk contains the latter part of the array and its closing declaration.
- `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)`: creates `rtw8822c_rf_b_tbl` with `.parse = rtw_parse_tbl_phy_cond`, `.do_cfg = rtw_phy_cfg_rf`, and `.rf_path = RF_PATH_B`.
- `rtw8822c_txpwr_lmt_type0[]`: complete `struct rtw_txpwr_lmt_cfg_pair` table covering multiple regulatory domains, both bands, 20/40/80 MHz-style width indices, CCK/OFDM/HT/VHT sections, and 2.4/5 GHz channels.
- `RTW_DECL_TABLE_TXPWR_LMT(rtw8822c_txpwr_lmt_type0)`: creates `rtw8822c_txpwr_lmt_type0_tbl` with `.parse = rtw_parse_tbl_txpwr_lmt`.
- `rtw8822c_txpwr_lmt_type5[]`: alternate RFE-5 power-limit table. The chunk starts the array but does not include its wrapper or final entries.

The key shared types are `struct rtw_table`, `struct rtw_txpwr_lmt_cfg_pair`, and the PHY table pair/condition union used by `rtw_parse_tbl_phy_cond()`. The table declarations are exposed through `rtw8822c_table.h` and selected by `rtw8822c.c`.

## Control Flow

RF table load flow:

1. RTL8822C chip setup stores RF table pointers in `rtw8822c_hw_spec.rf_tbl`.
2. Generic PHY bring-up calls `rtw_load_table(rtwdev, tbl)`.
3. `rtw_parse_tbl_phy_cond()` walks the `u32` RF table as condition/config tiles, evaluates positive and negative condition markers, and calls the table's `do_cfg` only for matched branches.
4. For `rtw8822c_rf_b_tbl`, `rtw_phy_cfg_rf()` writes matched address/data pairs to RF path B with `rtw_write_rf()`. It treats `0xffe` and `0xfe` as delay pseudo-registers.

Power-limit table load flow:

1. `rtw8822c_rfe_defs[]` chooses an RFE definition from efuse/RFE state. Entries 0, 1, 2, 3, 4, and 6 use type 0; entry 5 uses type 5.
2. Main initialization loads the selected `rfe_def->txpwr_lmt_tbl`.
3. `rtw_parse_tbl_txpwr_lmt()` iterates every tuple, records which regulatory domains were configured, and calls `rtw_phy_set_tx_power_limit()`.
4. `rtw_phy_set_tx_power_limit()` clamps the signed limit to the chip maximum, maps the channel to a 2G/5G channel index, stores it in `hal->tx_pwr_limit_2g` or `hal->tx_pwr_limit_5g`, and keeps the world-wide domain as the minimum of configured limits.
5. After parsing, missing regulatory domains are filled from an alternative domain or from `RTW_REGD_WW`; 5 GHz HT/VHT gaps are cross-referenced.
6. Later transmit-power index calculation calls `rtw_phy_get_tx_power_limit()` and combines the chosen limit with efuse base power, per-rate offset, remnant tracking, and SAR before writing TXAGC.

## State and Persistence

The arrays in this chunk are `static const`; they do not mutate at runtime. Their effects persist in two places:

- RF-B register writes persist in hardware until another RF table load, channel switch, calibration routine, power transition, or reset rewrites those RF registers.
- Parsed power limits persist in `struct rtw_hal` arrays `tx_pwr_limit_2g` and `tx_pwr_limit_5g`. These arrays are initialized to the chip maximum, then tightened by loaded table rows and used for later per-rate/per-channel transmit-power decisions.

The selected power-limit profile is board/RFE state dependent. RFE option 5 gets a different type-5 regulatory matrix than the default type-0 matrix, so efuse parsing and RFE definition selection are part of the persistent behavior even though this file only contains constants.

## Dependencies and Integration Points

This chunk depends on the `rtw88` PHY table framework in `phy.h`, `main.h`, and `phy.c`:

- `RTW_DECL_TABLE_RF_RADIO` and `RTW_DECL_TABLE_TXPWR_LMT` wrap raw arrays as `struct rtw_table` descriptors.
- `rtw_load_table()` dispatches through the descriptor parser.
- `rtw_parse_tbl_phy_cond()` interprets condition markers embedded in RF scripts.
- `rtw_phy_cfg_rf()` writes RF registers for the configured path.
- `rtw_parse_tbl_txpwr_lmt()` and `rtw_phy_set_tx_power_limit()` translate table tuples into the HAL transmit-power-limit matrices.

The chunk integrates with RTL8822C chip setup in `rtw8822c.c`: `rtw8822c_hw_spec.rf_tbl` references `rtw8822c_rf_b_tbl`, and `rtw8822c_rfe_defs[]` chooses `rtw8822c_txpwr_lmt_type0_tbl` or `rtw8822c_txpwr_lmt_type5_tbl`. It also integrates with regulatory-domain handling, efuse/RFE option discovery, channel/bandwidth selection, rate-section mapping, SAR handling, and TX power programming.

## Risks

- The RF script is opaque and sequencing-sensitive. The conditional markers, delays, and register writes must remain paired exactly as generated; deleting or moving one value can desynchronize the parser and write incorrect RF registers.
- The chunk begins in the middle of `rtw8822c_rf_b[]`, so any local-only review can miss the condition state that led into line 33743. Merge-stage research should describe the full RF-B script using adjacent chunks.
- Power-limit tuple field order is positional. Swapping `band`, `bw`, `rs`, `ch`, or `txpwr_lmt` compiles cleanly but silently corrupts regulatory behavior.
- Regulatory risk is high. These limits feed final TX power decisions; incorrect values can underpower links, violate regional limits, or interact badly with SAR reductions and efuse power offsets.
- `127` entries depend on chip maximum clamping and initialization semantics. Treating them as literal restrictive limits or changing `max_power_index` behavior would alter many rows at once.
- Type 5 is incomplete in this chunk. Final conclusions about RFE-5 limits must include lines after 43411 through the table wrapper.
- There are no semantic checks that every meaningful combination is present. The parser only warns on invalid indexes, then fills missing regulatory domains from alternatives or `WW`; missing rows can therefore become broad fallback behavior.

## Test and Validation Signals

Useful validation is mostly hardware and driver-integration oriented:

- Build tests should catch table syntax, missing wrappers, or broken extern declarations in `rtw8822c_table.h`.
- Probe/init logs on RTL8822C hardware should show successful RF table loading with no PHY/RF table parser warnings or RF access failures.
- RFE-option coverage should test default RFE options and RFE option 5 to confirm the selected `txpwr_lmt_type0` or `txpwr_lmt_type5` table is loaded.
- Regulatory-domain tests should exercise FCC, MKK, ETSI, IC, KCC, ACMA, Chile, Mexico, CN, Qatar, UK, and WW fallback paths, watching for `"wrong txpwr_lmt"` and `"txpwr regd ... does not be configured"` debug messages.
- Channel/rate tests should verify 2.4 GHz channels 1-14 and 5 GHz channel groups across 20/40/80 MHz operation, CCK/OFDM/HT/VHT sections, and both RF paths where applicable.
- Conducted-power or calibrated radiated-power measurements should compare final TXAGC-derived output against expected regulatory caps for type 0 and type 5 boards.
- Regression tests should include channel changes and suspend/resume because RF register state from the RF-B script and parsed HAL power matrices must survive normal initialization flows and be refreshed after reset-like transitions.

### subset-b-004916: lines 43412-46105

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 43412-46105

## Scope

This chunk is the final portion of `rtw8822c_table.c`. It finishes the `rtw8822c_txpwr_lmt_type5` table and then declares the 8822C DPK/DPD calibration register tables:

- `rtw8822c_txpwr_lmt_type5[]`, completed in this chunk and exported as `rtw8822c_txpwr_lmt_type5_tbl`.
- `rtw8822c_dpk_afe_no_dpk[]`, exported as `rtw8822c_dpk_afe_no_dpk_tbl`.
- `rtw8822c_dpk_afe_is_dpk[]`, exported as `rtw8822c_dpk_afe_is_dpk_tbl`.
- `rtw8822c_dpk_mac_bb[]`, exported as `rtw8822c_dpk_mac_bb_tbl`.
- `rtw8822c_array_mp_cal_init[]`, exported as `rtw8822c_array_mp_cal_init_tbl`.

The file ends at line 46105 after `RTW_DECL_TABLE_PHY_COND(rtw8822c_array_mp_cal_init, rtw_phy_cfg_bb)`.

## Purpose

The visible TX power-limit rows provide board/RFE-specific regulatory cap data for RTL8822C RFE option 5. Each row is a `struct rtw_txpwr_lmt_cfg_pair` tuple of regulatory domain, band, bandwidth, rate section, channel or channel group, and maximum power index. The values include ordinary caps and sentinel-looking `127` entries that preserve the driver's maximum power-index ceiling and effectively indicate unconstrained or placeholder limits for specific combinations.

The DPK tables are hardware register scripts for digital pre-distortion calibration. They configure AFE state before and after DPK, pause or isolate MAC/BB transmit state, program DPD/DPK SRAM windows, and seed the RFK initialization table used during PHY setup. The chunk is table-only code; runtime behavior comes from the generic rtw88 table loaders and from the 8822C calibration functions in `rtw8822c.c`.

## Important APIs, Types, And Macros

`struct rtw_table` is the runtime descriptor that wraps each static array with `.data`, `.size`, `.parse`, optional `.do_cfg`, and `.rf_path`. `rtw_load_table()` calls the descriptor's parser.

`RTW_DECL_TABLE_TXPWR_LMT(rtw8822c_txpwr_lmt_type5)` creates `rtw8822c_txpwr_lmt_type5_tbl` with parser `rtw_parse_tbl_txpwr_lmt`.

`RTW_DECL_TABLE_DPK(...)` is the 8822C-local DPK wrapper. Its parser is `rtw8822c_parse_tbl_dpk()`, which treats the `u32` arrays as repeated triples:

```c
struct dpk_cfg_pair {
	u32 addr;
	u32 bitmask;
	u32 data;
};
```

Each triple becomes `rtw_write32_mask(rtwdev, addr, bitmask, data)`.

`RTW_DECL_TABLE_PHY_COND(rtw8822c_array_mp_cal_init, rtw_phy_cfg_bb)` exports the MP calibration initialization array as a conditional PHY table. Because the data is plain address/data pairs here, `rtw_parse_tbl_phy_cond()` walks it as BB config pairs and calls `rtw_phy_cfg_bb()`. That helper performs delays for pseudo-addresses such as `0xfe` through `0xfa`; otherwise it writes masked/full BB register values through the normal register path.

`rtw8822c_table.h` exposes all exported table descriptors, including the four DPK-related descriptors and the MP calibration-init descriptor in this chunk.

## Control Flow And Integration

For TX power limits, `rtw8822c_rfe_defs` in `rtw8822c.c` selects `RTW_DEF_RFE(8822c, 0, 5, 0)` only for RFE option 5. That macro points `txpwr_lmt_tbl` at `rtw8822c_txpwr_lmt_type5_tbl`. PHY/RFE initialization later loads that table through `rtw_parse_tbl_txpwr_lmt()`, which calls `rtw_phy_set_tx_power_limit()` for every tuple, fills missing regulatory domains from alternatives or world-wide defaults, and then cross-references the limit table with `rtw_xref_txpwr_lmt()`.

For RFK startup, `struct rtw_chip_info rtw8822c_hw_spec` assigns `.rfk_init_tbl = &rtw8822c_array_mp_cal_init_tbl`. Generic PHY table loading invokes `rtw_load_rfk_table()` from `rtw_phy_load_tables()` after AGC/BB/RFE setup and before per-path RF radio tables. The table itself is a long scripted sequence around 0x1b00/0x1b80/0x1b4c/0x1b50/0x1b58/0x1b5c/0x1bd* registers, which appear to select DPD/MP calibration subpages, load LUT entries, and initialize DPD SRAM contents.

For runtime DPK, `rtw8822c_phy_calibration()` calls `rtw8822c_do_dpk()` after GAPK and IQK. The DPK flow:

1. Skips if DPD power is disabled or reloads stored DPK data when the channel matches.
2. Backs up BB and RF registers, including registers modified by the DPK tables.
3. Calls `rtw8822c_dpk_mac_bb_setting()`, which first pauses TX and then loads `rtw8822c_dpk_mac_bb_tbl`.
4. Calls `rtw8822c_dpk_afe_setting(..., true)`, loading `rtw8822c_dpk_afe_is_dpk_tbl`.
5. Runs per-path DPK gain/loss search, one-shot DPK commands, coefficient read/write, and DPK-on sequences.
6. Calls `rtw8822c_dpk_afe_setting(..., false)`, loading `rtw8822c_dpk_afe_no_dpk_tbl`.
7. Restores RF/BB registers and performs RXBB DC calibration.

The DPK tables therefore form only part of a larger stateful calibration transaction; they are bracketed by explicit register backup/restore and by per-path RF writes in `rtw8822c.c`.

## State And Persistence Behavior

The static arrays are immutable compiled-in hardware data. They do not persist state by themselves.

TX power-limit parsing writes into `rtwdev->hal` power-limit structures through `rtw_phy_set_tx_power_limit()` and fallback/cross-reference helpers. That state persists for the driver instance and is used later by transmit power calculations.

DPK runtime state is stored in `rtwdev->dm_info.dpk_info`, including current DPK band/channel/bandwidth, per-path pass bits, DPK TX AGC, coefficients, gain-scaling values, thermal values, and reload flags. The tables in this chunk mutate hardware registers during the calibration window; the DPK code backs up selected BB/RF registers before applying them and restores those registers at the end. Calibration coefficients and per-path result flags persist in driver memory so `rtw8822c_dpk_reload()` can reapply them on the same channel without a full recalibration.

The MP calibration-init table is loaded at PHY initialization as register writes. Its effects persist in hardware registers and DPD/DPK internal memory until reset, reinitialization, or later calibration writes replace them.

## Dependencies

This chunk depends on core rtw88 table infrastructure from `main.h` and `phy.h`, including `struct rtw_table`, `rtw_load_table()`, `RTW_DECL_TABLE_*` macros, `rtw_parse_tbl_phy_cond()`, `rtw_parse_tbl_txpwr_lmt()`, and `rtw_phy_cfg_bb()`.

It depends on 8822C-specific DPK parser support in `rtw8822c.c`: `RTW_DECL_TABLE_DPK` and `rtw8822c_parse_tbl_dpk()`.

It depends on register/mask macros such as `BIT()`, `GENMASK()`, `MASKDWORD`, `MASKBYTE*`, and on register helpers `rtw_write32_mask()`, `rtw_write32()`, `rtw_write8()`, `rtw_read32_mask()`, `rtw_read_rf()`, and `rtw_write_rf()`.

The TX power rows depend on enum value contracts for regulatory domains, bands, bandwidths, rate sections, and channels. There are no named constants in the table body, so tuple field order and enum numbering must remain stable.

## Risks And Edge Cases

The main correctness risk is silent data drift. Most entries are raw register values or numeric tuple fields with no inline semantic names; a one-column shift in `rtw_txpwr_lmt_cfg_pair` rows or a missing `u32` in a DPK triple would still compile but could write wrong limits or wrong hardware registers.

`rtw8822c_array_mp_cal_init[]` is parsed as pairs, while DPK tables are parsed as triples. Accidentally declaring one with the wrong `RTW_DECL_TABLE_*` macro changes how the same raw array is walked and can cause register/value misalignment.

The DPK parser uses `tbl->size / 3`, so a DPK array whose element count is not divisible by three would silently ignore trailing words. The current arrays are intended to be exact triples.

The type5 TX power table is selected only for RFE option 5. If efuse RFE mapping changes or a board is misidentified, this chunk can materially affect regulatory transmit caps. The `127` cap values need to match the driver's `max_power_index` expectations; if that ceiling changes, these rows may need review.

DPK register scripts touch coexistence-sensitive and RF/BB state indirectly through the larger DPK flow. Failures show up as calibration timeout, failed DPK coefficients, reduced transmit quality, or coexistence problems rather than simple compile-time errors.

## Test Signals

Build-level signals:

- The file compiles and `rtw8822c_table.h` extern declarations resolve for `rtw8822c_txpwr_lmt_type5_tbl`, `rtw8822c_dpk_afe_no_dpk_tbl`, `rtw8822c_dpk_afe_is_dpk_tbl`, `rtw8822c_dpk_mac_bb_tbl`, and `rtw8822c_array_mp_cal_init_tbl`.
- Array sizes are nonzero and DPK `u32` element counts remain multiples of three.

Runtime signals:

- With an RTL8822C device using RFE option 5, `rtw_parse_tbl_txpwr_lmt()` should not report unexpected missing regulatory-domain configuration beyond the intended fallback paths, and TX power limits should reflect the type5 rows.
- During PHY init, RFK table loading should complete without register-write faults or hardware-ready timeouts.
- During calibration, `RTW_DBG_RFK` logs should show DPK start/finish per path without repeated "failed to do dpk calibration" or "DPK stuck" warnings.
- DPK reload should trigger only when the current channel matches stored `dpk_info->dpk_ch`, and per-path `dpk_path_ok`, `dpk_txagc`, coefficients, and gain-scaling values should remain coherent across reload.
- RF performance tests should cover 2.4 GHz and 5 GHz, multiple bandwidths including 80 MHz, both RF paths, and RFE option 5 boards because this chunk is dominated by board/RFE-specific power limits and calibration programming.
