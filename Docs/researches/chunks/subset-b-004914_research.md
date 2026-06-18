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
