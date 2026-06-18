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
