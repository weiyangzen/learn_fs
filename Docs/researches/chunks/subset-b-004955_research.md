# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 1-8653

## Scope

This chunk covers the beginning of the Realtek `rtw89` RTL8852C PHY table source. It contains three top-level static `struct rtw89_reg2_def` arrays:

- `rtw89_8852c_phy_bb_regs[]`, complete in this chunk, from line 9 through line 1921.
- `rtw89_8852c_phy_bb_reg_gain[]`, complete in this chunk, from line 1923 through line 2538.
- `rtw89_8852c_phy_radioa_regs[]`, starting at line 2540 and continuing beyond the assigned line range. This chunk covers only its first 6113 register rows through line 8653.

The assigned range is data-heavy and does not define local functions. The executable behavior comes from the generic PHY table loader in `phy.c`, the table descriptors exported near the end of `rtw8852c_table.c`, and the RTL8852C chip descriptor in `rtw8852c.c`.

## Purpose

The chunk provides hardware initialization and calibration baseline data for RTL8852C PHY bring-up:

- The BB table programs baseband CRs for receive/transmit processing, packet detection, CCK/OFDM/HE behavior, path control, counters, lookup tables, and other PHY blocks.
- The BB gain table is not written directly as ordinary registers. Its encoded addresses are parsed into `rtwdev->bb_gain.ax`, including LNA/TIA gain-error data, RSSI replacement offsets, bypass gain, and OP1dB values used later by RTL8852C channel/gain setup code.
- The RF path-A table programs the radio register file for one RF chain. The visible region contains many repeated RF-internal table programming sequences, especially selector/data patterns using RF registers `0x033`, `0x03e`, `0x03f`, `0x030`, and page/bank selector `0x0ef`.
- Conditional control rows allow one compiled table to carry values for multiple RFE/cut/package variants. Runtime efuse and chip-version state select the matching blocks.

This file is essentially a generated hardware contract. Small changes to constants can alter radio/baseband behavior without changing C control flow.

## Important APIs, Types, and Data

The central data type is `struct rtw89_reg2_def`, a pair of `u32 addr` and `u32 data`. `struct rtw89_phy_table` wraps an array pointer, row count, RF path, and optional config callback.

Important local arrays in this chunk:

- `rtw89_8852c_phy_bb_regs[]`: about 1911 register rows. It begins with headline rows such as `0xF0FF0000`, `0xF03300FF`, `0xF03400FF`, `0xF03500FF`, and `0xF03600FF`, then contains ordinary baseband writes and many conditional branch rows.
- `rtw89_8852c_phy_bb_reg_gain[]`: about 614 rows. Its addresses are packed fields consumed by `rtw89_phy_config_bb_gain_ax()`, not normal MMIO CR addresses.
- `rtw89_8852c_phy_radioa_regs[]`: starts with headline rows for RFE/CV matching, then RF writes. In the covered slice the most frequent pseudo/real addresses are `0x03f`, `0x030`, `0x033`, and repeated conditional selectors such as `0x80010000`, `0x90020000`, `0x90320000`, `0x90330000`, `0x90340000`, `0x90350000`, `0x90360000`, their `...0001` variants, `0xA0000000`, and `0xB0000000`.

Important consumers outside this chunk:

- `rtw89_phy_init_reg()` interprets headline rows and branch rows. It selects a target using efuse RFE type and chip cut/version, then only emits rows from matching conditional blocks.
- `rtw89_phy_config_bb_reg()` applies BB rows with `rtw89_phy_write32()`, handling special delay pseudo-addresses `0xf9` through `0xfe` and `BYPASS_CR_DATA`.
- `rtw89_phy_config_bb_gain_ax()` decodes the BB gain table into `rtwdev->bb_gain.ax`, dispatching by packed `cfg_type` to gain-error, replacement-offset, bypass, and OP1dB loaders.
- `rtw89_phy_config_rf_reg()` writes RF rows with `rtw89_write_rf()` and also stores the RF programming stream for firmware H2C RF register configuration.
- `rtw8852c_set_gain_error()` later consumes `rtwdev->bb_gain.ax` and writes the parsed values into RTL8852C-specific BB registers for the active subband and RF path.
- `rtw8852c_chip_info` wires `.bb_table`, `.bb_gain_table`, and `.rf_table` to the exported RTL8852C tables. Notably, its RF table array maps path slot 0 to `rtw89_8852c_phy_radiob_table` and path slot 1 to `rtw89_8852c_phy_radioa_table`; each table descriptor's own `rf_path` is therefore important.

## Control Flow

At probe or PHY initialization, `rtw89_phy_init_bb_reg()` chooses firmware-provided element tables when present, otherwise it uses `chip->bb_table` and `chip->bb_gain_table`. For this chip, the fallback static tables are the arrays defined in this file. It initializes BB registers first, optionally repeats for PHY1 in DBCC mode with address offsets, initializes the transmit-power unit, parses the BB gain table into runtime gain state, and finally resets BB.

For each table, `rtw89_phy_init_reg()` first scans the headline rows whose top nibble is `0xf`. It chooses the best headline by matching the runtime RFE type and cut/version, with fallback matching for don't-care CV or RFE values. It then walks the remaining rows. Branch rows with top nibbles `0x8`, `0x9`, `0xa`, and `0xb` implement if/elif/else/end behavior; rows with condition `0x4` check the branch target against the selected headline target. Ordinary rows are passed to the table-specific config callback only while the branch state is matched.

The BB table rows are direct baseband writes. The BB gain table rows are decoded into arrays rather than immediately touching hardware registers. The RF table rows are full RF register writes for the table's path and are also accumulated into H2C RF register pages so firmware can mirror or reuse the same RF configuration stream.

## State and Persistence Behavior

The arrays in this chunk are static read-only kernel data. They do not persist state by themselves.

The BB table persists state into the device's baseband register file until later channel changes, calibration, reset, suspend/resume, firmware table overrides, or explicit PHY writes replace those values. DBCC mode can apply the same BB table to PHY1 by adding the PHY0-to-PHY1 offset in the generic BB config callback.

The BB gain table persists decoded values in `rtwdev->bb_gain.ax`. Those values are in driver memory and are later applied by RTL8852C-specific code when configuring gain for a subband/path. This separation matters because the table parse occurs during BB init, while the eventual register writes depend on channel/subband and path context.

The RF table persists state into the RF path register file. The same emitted RF rows are also stored transiently in `struct rtw89_fw_h2c_rf_reg_info` and sent to firmware in pages after each RF path table is parsed. Conditional-table parser state is transient: selected headline, target, branch match state, and target-found flags only exist while loading the table.

## Dependencies and Integration Points

This chunk depends on:

- `phy.h` for conditional-table macros such as `get_phy_headline()`, `get_phy_target()`, `PHY_COND_BRANCH_IF`, `PHY_COND_BRANCH_ELIF`, `PHY_COND_BRANCH_ELSE`, `PHY_COND_BRANCH_END`, and `PHY_COND_CHECK`.
- `core.h` for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, RF path enums, chip table pointers, and `struct rtw89_phy_bb_gain_info`.
- `phy.c` for the generic table parser and BB/RF/BB-gain config callbacks.
- `rtw8852c.c` for chip descriptor wiring and RTL8852C-specific use of parsed gain data.
- Efuse and HAL state: `rtwdev->efuse.rfe_type`, `rtwdev->hal.cv`, and for some chips ACV selection decide which conditional rows are active.
- Firmware element table loading: `rtwdev->fw.elm_info` can replace static BB, BB-gain, and RF tables, so this file is the static fallback/compiled-in table set.

The practical integration point is PHY bring-up for an RTL8852C device. MAC/PCI/USB probing reaches chip initialization, chip initialization exposes these table pointers through `rtw8852c_chip_info`, and the PHY layer executes the tables to program hardware.

## Risks and Edge Cases

- Table structure is fragile. The parser treats some values as control flow based on high address bits; editing a branch marker as if it were a normal register row can silently select the wrong hardware variant.
- Headline matching failure aborts table load with `invalid PHY package`. Missing or malformed `0xf...` headline rows can prevent all subsequent rows from being applied.
- The BB gain table's addresses are packed metadata. They must stay within `RTW89_BB_GAIN_BAND_NR`, `chip->rf_path_num`, known `cfg_type` values, and known row subtypes; otherwise rows are skipped or warnings are emitted and later gain programming uses incomplete data.
- RF path mapping is easy to misread. The RTL8852C chip descriptor lists radiob then radioa in the RF table pointer array, so the table descriptor's `rf_path` must remain correct when the final table object is created.
- RF register rows are often whole-register writes. Wrong constants in repeated `0x033`/`0x03f` or `0x030` sequences can break RF-internal lookup tables, calibration baselines, transmit quality, receive sensitivity, or regulatory power behavior.
- The assigned range ends in the middle of `rtw89_8852c_phy_radioa_regs[]`. Final per-file research must merge this with later chunks before describing the complete RF-A table.
- Firmware-provided element tables can override these static arrays. Testing only the compiled-in path may miss systems where firmware table elements are loaded instead.

## Test Signals

Useful validation signals include:

- Build coverage for the `rtw89` RTL8852C driver to catch syntax, array, and descriptor regressions.
- Probe logs on RTL8852C hardware showing no `invalid PHY package`, BB gain unknown-type warnings, RF parameter overflow warnings, or RF H2C config failures.
- PHY initialization traces confirming BB table load, BB gain parse, BB reset, RF path table load, and RF H2C page send complete in order.
- Hardware smoke tests across RFE/cut variants where possible, because the conditional rows are selected from efuse and chip-version state.
- Channel-change and subband tests that exercise `rtw8852c_set_gain_error()` after BB gain parsing; watch RSSI, EVM, sensitivity, and throughput for path or band asymmetry.
- RF calibration and recovery tests after reset, suspend/resume, and SER recovery, since these table values are the baseline for later RFK/DPK/TSSI flows.
- Static checks that table row counts remain sane, top-level array boundaries are not split accidentally, conditional branch markers remain balanced, and the final `struct rtw89_phy_table` descriptors use the intended `ARRAY_SIZE()` and RF path.

## Cross-Chunk Notes

Later chunks of the same file complete `rtw89_8852c_phy_radioa_regs[]`, define the RF-B and NCTL tables, define transmit-power and regulatory limit tables, and export the final `struct rtw89_phy_table` objects. The merge lane should avoid treating this chunk's RF-A analysis as complete until those later RF-A rows and the final table descriptor are reconciled.
