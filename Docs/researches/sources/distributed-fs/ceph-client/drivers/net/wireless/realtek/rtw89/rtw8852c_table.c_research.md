# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004955`: lines 1-8653, `Docs/researches/chunks/subset-b-004955_research.md`
- `subset-b-004956`: lines 8654-17858, `Docs/researches/chunks/subset-b-004956_research.md`
- `subset-b-004957`: lines 17859-26919, `Docs/researches/chunks/subset-b-004957_research.md`
- `subset-b-004958`: lines 26920-35031, `Docs/researches/chunks/subset-b-004958_research.md`
- `subset-b-004959`: lines 35032-41891, `Docs/researches/chunks/subset-b-004959_research.md`
- `subset-b-004960`: lines 41892-49275, `Docs/researches/chunks/subset-b-004960_research.md`
- `subset-b-004961`: lines 49276-57136, `Docs/researches/chunks/subset-b-004961_research.md`
- `subset-b-004962`: lines 57137-57159, `Docs/researches/chunks/subset-b-004962_research.md`

## Chunk Research

### subset-b-004955: lines 1-8653

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

### subset-b-004956: lines 8654-17858

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 8654-17858

## Scope

This chunk covers `subset-b-004956`, the second generated-table slice of `rtw8852c_table.c`. It starts inside `static const struct rtw89_reg2_def rtw89_8852c_phy_radioa_regs[]` at line 8654 and continues through line 17858, after `rtw89_8852c_phy_radiob_regs[]` begins at line 16715. The chunk is almost entirely RF register table data for RTL8852C/RTW89 PHY initialization, not procedural C logic.

## Purpose

The entries in this range are Realtek RF path initialization packages. Each row is a `struct rtw89_reg2_def` pair of `{ addr, data }`, where normal RF rows become register writes and high-nibble encoded rows act as package/condition-control metadata. The tables are later exported through `rtw89_8852c_phy_radioa_table` and `rtw89_8852c_phy_radiob_table`, which bind these arrays to `RF_PATH_A` and `RF_PATH_B` and select `rtw89_phy_config_rf_reg_v1` as the writer.

The line range has two practical roles:

- Lines 8654-16713 finish the RF path A table (`rtw89_8852c_phy_radioa_regs[]`), including many conditional blocks keyed by RFE/CV target.
- Lines 16715-17858 begin the RF path B table (`rtw89_8852c_phy_radiob_regs[]`) with the same headline/package structure and early RF register sequences for the second path.

## Important Types And APIs

- `struct rtw89_reg2_def` in `core.h` is the storage format: `u32 addr; u32 data;`.
- `struct rtw89_phy_table` in `core.h` wraps a register array with `n_regs`, `rf_path`, and an optional config callback.
- `rtw89_8852c_phy_radioa_table` and `rtw89_8852c_phy_radiob_table` are defined near the end of `rtw8852c_table.c`; both point at these static arrays and use `rtw89_phy_config_rf_reg_v1`.
- `rtw8852c.c` installs the RF tables into the chip descriptor as `.rf_table = { &rtw89_8852c_phy_radiob_table, &rtw89_8852c_phy_radioa_table }`. The table order is intentionally chip-specific, so consumers should not assume array index names match lexical A/B order without checking `rf_path`.
- `rtw89_phy_init_rf_reg()` in `phy.c` loads each `chip->rf_table[path]`, applies package filtering through `rtw89_phy_init_reg()`, and sends stored RF writes to firmware H2C pages with `rtw89_phy_config_rf_reg_fw()`.
- `rtw89_phy_config_rf_reg_v1()` performs the hardware write with `rtw89_write_rf(..., RFREG_MASK, ...)` and stores entries with `addr >= 0x100` into the firmware RF-reg H2C buffer.

## Table Encoding And Control Flow

The RF table loader interprets the high nibble of `addr`:

- `0xf...` headline rows at the start of each RF array describe available RFE/CV packages. `rtw89_phy_sel_headline()` scans these and selects the best target for `rtwdev->efuse.rfe_type` and `rtwdev->hal.cv`, with fallback handling for wildcard CV/RFE.
- `0x8...` and `0x9...` are branch-if/branch-elif markers.
- `0xa0000000` is branch-else.
- `0xb0000000` is branch-end.
- `0x40000000` is a check row used after branch markers to decide whether subsequent ordinary register rows apply to the selected package.
- Other rows are passed to the RF config callback when the current branch is active.

Within this chunk, the table is dominated by repeated conditional packages. A quick source count over the requested lines shows 9,205 lines total, about 1,594 branch marker/check pairs, 144 else/end markers, 4,672 writes to RF register `0x10030`, 1,898 writes to RF register `0x03f`, 144 writes to RF register `0x030`, and 17 writes to RF register `0x0ef`. This repetition is expected for vendor-generated RF calibration/init tables that enumerate different package/CV/RFE cases.

`rtw89_phy_init_reg()` is the core interpreter. After selecting a headline target, it walks from the first non-headline entry to the end of the table, tracks the active branch target, toggles `is_matched` and `target_found` on condition/check/end rows, and invokes the table's config function only for rows in the selected branch.

## State And Persistence

The table data itself is immutable static storage. Loading it mutates device state through MMIO/RF writes and through a temporary firmware H2C staging buffer:

- Direct RF writes program the chip's RF path registers for boot/reinit.
- For `rtw89_phy_config_rf_reg_v1()`, entries with `addr >= 0x100` are packed into `rtw89_fw_h2c_rf_reg_info` as `(addr << 20) | data`; lower RF addresses are written but not staged.
- The staging buffer has `RTW89_H2C_RF_PAGE_NUM` pages of `RTW89_H2C_RF_PAGE_SIZE` entries, currently 3 * 500. Overflow is detected in `rtw89_phy_cofig_rf_reg_store()` and `rtw89_phy_config_rf_reg_fw()`, which warn and return `-EINVAL`.
- No filesystem persistence or runtime allocation is introduced by this chunk. Persistence is in compiled `.rodata` plus device/firmware state after initialization.

## Dependencies And Integration Points

This chunk depends on shared RTW89 infrastructure:

- Linux kernel bitfield helpers used by `get_phy_headline()`, `get_phy_target()`, and `get_phy_cond()` in `phy.h`.
- `rtwdev->efuse.rfe_type`, `rtwdev->hal.cv`, and sometimes `rtwdev->hal.acv` for package selection.
- RF path definitions such as `RF_PATH_A`, `RF_PATH_B`, `RF_PATH_MAX`, and `RFREG_MASK`.
- Chip descriptor wiring in `rtw8852c.c`, which binds the tables to RTL8852C setup.
- Firmware command support through `rtw89_fw_h2c_rf_reg()` for the staged RF-register H2C records.
- Optional firmware element override path: `rtw89_phy_init_rf_reg()` prefers `rtwdev->fw.elm_info.rf_radio[path]` if present, otherwise uses these compiled tables.

The data also aligns with adjacent `rtw8852c_table.c` chunks. Chunk 1 contains the start of `rtw89_8852c_phy_radioa_regs[]`; chunk 3 continues after line 17858 inside `rtw89_8852c_phy_radiob_regs[]`.

## Risks

- Because this is generated RF configuration, single-value edits can silently degrade RF bring-up, calibration, band support, regulatory power behavior, or path symmetry without compile-time errors.
- Branch marker integrity is critical. Removing or inserting a `0x8...`, `0x9...`, `0x40000000`, `0xa0000000`, or `0xb0000000` row can redirect large blocks of writes to the wrong RFE/CV package.
- The chunk boundary splits logical blocks: it starts in the middle of path A table data and ends in the middle of path B data. Review or merge logic must reconcile with neighboring chunks before drawing per-file conclusions.
- The table order in `.rf_table` is non-obvious (`radiob` then `radioa`), so downstream work should rely on the `rf_path` member rather than array-position assumptions.
- H2C staging size is finite. Large generated-table updates that increase `addr >= 0x100` entries can exceed the 1,500-entry H2C capacity and trigger runtime warnings/failures.
- There is little semantic naming inside the table; validation depends on hardware/vendor baselines more than code readability.

## Test Signals

Useful validation signals for this chunk are mostly build and hardware bring-up oriented:

- Compile coverage for `rtw89_8852c_table.c`, `rtw8852c.c`, and `phy.c` confirms the array syntax, exported table descriptors, and callback signatures remain valid.
- Runtime boot/probe logs should not show `invalid PHY package`, `failed to load CR`, `RF parameters exceed size`, `rf reg h2c total len ... larger than`, or `rf path ... reg h2c config failed`.
- RTL8852C hardware smoke tests should verify both RF paths initialize, scan, associate, and pass traffic on 2.4 GHz, 5 GHz, and 6 GHz where supported by regulatory domain and hardware SKU.
- RF regression should include multiple RFE/CV variants when available, because most of this chunk is condition-selected data.
- Because this chunk contains the transition from RF path A to RF path B, path-specific sanity checks such as RSSI per chain, TX/RX chain enablement, calibration completion, and thermal/power tracking are more valuable than generic unit tests.

### subset-b-004957: lines 17859-26919

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 17859-26919

## Scope

This chunk covers a middle section of the Realtek RTL8852C RF table source. The exact range is inside the static `rtw89_8852c_phy_radiob_regs[]` array, which begins earlier at line 16715 and is exported near the end of the file through `rtw89_8852c_phy_radiob_table`. The chunk does not define normal C functions; it is generated hardware bring-up data encoded as `{addr, data}` pairs for the rtw89 PHY/RF table interpreter.

The assigned lines start in the middle of a repeated RF-B conditional package and end at an indirect register selector entry `{0x033, 0x000000AF}`. The next chunk continues the same RF-B table.

## Purpose

The data initializes RTL8852C radio path B for selected RFE/CV hardware packages. It programs RF register values, LUT windows, and indexed indirect RF pages used by gain, bias, front-end, and path-dependent radio setup. The visible sequence contains:

- conditional package blocks keyed by encoded addresses such as `0x80010000`, `0x90020000`, `0x90070001`, `0x903f0001`, `0xA0000000`, and terminated by `0xB0000000`;
- repeated direct RF writes to addresses such as `0x030`, `0x03F`, `0x06A`, `0x06B`, `0x06F`, `0x095`, and `0x10030`;
- page or access-window selects through `0x0EF`, `0x0EE`, `0x0EB`, `0x0EC`, and `0x100EE`;
- indirect index/value programming through `0x033` plus `0x03E`/`0x03F`;
- a very large `0x10030` burst, which dominates the chunk and appears to load a dense RF path lookup/ramp table for one selected access page.

The chunk is part of static device initialization. It does not compute values at runtime; runtime selection is performed by the generic PHY table loader.

## Important APIs, Types, and Data

The enclosing data type is `struct rtw89_reg2_def`, a two-field `{ u32 addr; u32 data; }` pair declared in `core.h`. The exported wrapper is `struct rtw89_phy_table`, whose fields are `regs`, `n_regs`, `rf_path`, and an optional `config` callback.

For this table, `rtw89_8852c_phy_radiob_table` points at `rtw89_8852c_phy_radiob_regs`, sets `rf_path = RF_PATH_B`, and sets `config = rtw89_phy_config_rf_reg_v1`. The header `rtw8852c_table.h` exposes this table to the chip-specific driver. `rtw8852c.c` installs the table in `rtw89_chip_info.rf_table`; notably the chip info maps `{ &rtw89_8852c_phy_radiob_table, &rtw89_8852c_phy_radioa_table }`, so generic RF init iterates this path-B table first.

Important loader functions outside this file are:

- `rtw89_phy_init_rf_reg()` selects the chip RF table for each path and calls `rtw89_phy_init_reg()`.
- `rtw89_phy_init_reg()` interprets headline and branch/check/end opcodes embedded in `reg->addr`, compares them with `rtwdev->efuse.rfe_type` and `rtwdev->hal.cv` or `hal.acv`, and only applies rows in the matched branch.
- `rtw89_phy_config_rf_reg_v1()` writes each selected row with `rtw89_write_rf(rtwdev, rf_path, reg->addr, RFREG_MASK, reg->data)` and stores rows with addresses `>= 0x100` into the firmware H2C RF register cache.
- `rtw89_phy_config_rf_reg_fw()` sends cached RF rows to firmware after the selected table pass.

The chunk itself contains 9061 assigned source lines. A local pass over the range found the most common addresses as `0x10030` with 4570 rows, `0x03F` with 1763 rows, `0x030` with 476 rows, and `0x033` with 203 rows. Conditional branch opcodes are also frequent: each of `0xA0000000`, `0xB0000000`, and several `0x90......` branch selectors appears around 78 times in the range.

## Control Flow

There is no intra-file function flow, but the table has an interpreted control flow:

1. `rtw89_phy_init_rf_reg()` chooses this table for an RF path during RTL8852C RF init.
2. `rtw89_phy_sel_headline()` scans any table headline entries before this chunk, chooses the best RFE/CV target, and returns a `cfg_target`.
3. `rtw89_phy_init_reg()` walks the table entries. High-nibble opcode values encode branch-if, branch-elif, branch-else, branch-end, and check records. In this chunk, addresses beginning with `0x8`, `0x9`, `0xA`, `0xB`, and the `0x40000000` check marker control which following RF writes are active.
4. For active rows that are not flow-control records, `rtw89_phy_config_rf_reg_v1()` writes the row to RF path B. Rows such as `0x0EF` select RF register pages or access windows; `0x033` selects an indirect entry; `0x03E` and `0x03F` then write associated fields or values.
5. After table interpretation, cached RF writes are sent to firmware as H2C RF register information.

The visible data begins with repeated `0x030` values for many package selectors, then switches to `0x0EF = 0x80` and indexed `0x033` entries `0x04` through `0x3f` with paired `0x03E`/`0x03F` values. It then clears or changes pages, writes a few direct setup registers, repeats per-package direct RF sequences for `0x06A/0x06B/0x06F`, programs additional `0x030` tables under `0x0EF = 0x200`, toggles `0x0EB`, and programs many indexed `0x03F` values under `0x0EE = 0x1000`. Around line 21349, `0x100EE = 0x4000` opens an extended page and a long stream of `0x10030` values follows until `0x100EE` is cleared near line 25972. The final visible region selects `0x0EF = 0x2000` and `0x0EF = 0x8000`, then writes indexed values for entries `0x20` through `0xAF` with package-dependent `0x03F` values.

## State and Persistence

The source file has no mutable C state, but loading the selected rows mutates device RF hardware state. The writes persist in the radio until reset, later RF table reload, channel/RFK sequence, coexistence adjustment, or another driver path overwrites the same RF registers.

Rows with RF addresses `>= 0x100` also persist in the driver's firmware RF-reg cache during initialization. With `rtw89_phy_config_rf_reg_v1()`, those rows are stored in `struct rtw89_fw_h2c_rf_reg_info` and sent to firmware after the table pass. This matters for the large extended-address portion of the chunk, especially the `0x10030` burst and `0x100EE` page control rows.

Selection state comes from runtime hardware identity: `rtwdev->efuse.rfe_type` and chip cut/version fields in `rtwdev->hal.cv` or `hal.acv`. A different board package can skip large parts of this chunk even though all rows are compiled into the driver.

## Dependencies and Integration Points

This chunk depends on:

- `phy.h` opcode macros such as `get_phy_headline()`, `get_phy_target()`, `get_phy_cond()`, and the `PHY_COND_*` constants;
- `core.h` definitions for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, RF path enums, and chip info table pointers;
- `phy.c` table interpreter and RF write callbacks;
- low-level RF I/O through `rtw89_write_rf()` and firmware H2C RF register download;
- `rtw8852c.c` chip info, which connects the exported RTL8852C tables to the device bring-up flow.

The table is tightly coupled to RTL8852C RF register layout. The nearby chip-specific runtime code also manipulates RF path B LUT registers for Bluetooth coexistence and WL RX-gain controls, so later runtime paths can intentionally overwrite a subset of LUT entries initialized here.

## Risks

- The table is opaque generated hardware data. A single wrong hex literal, missing row, or shifted line can silently misprogram RF path B.
- Conditional opcodes and data rows share the same `{addr, data}` type. Treating branch markers such as `0x90070001` or `0xB0000000` as normal RF registers, or treating normal high-address rows such as `0x10030` as branch opcodes, would break initialization.
- RFE/CV gating is fragile. If EFUSE RFE type or chip version decoding is wrong, the loader can select the wrong branch and write values meant for another front-end package.
- Indirect-page programming is order-sensitive. `0x0EF`, `0x0EE`, `0x0EB`, `0x100EE`, and `0x033` establish context for subsequent `0x03F` or `0x10030` writes. Reordering or truncating the chunk can leave writes targeting the wrong page or index.
- Firmware cache limits matter for extended-address rows. The RF-reg H2C cache warns if parameters exceed its page capacity; this chunk contributes thousands of RF rows to the full path-B table.
- Path mapping is easy to misread. The exported table is explicitly `RF_PATH_B`, but RTL8852C chip info lists it in the first `rf_table` slot before path A.
- There are no inline comments explaining the RF constants. Practical validation depends on hardware behavior and comparison with vendor-generated tables.

## Test and Validation Signals

Useful signals for this chunk are hardware and driver-init oriented:

- RTL8852C probe and RF initialization should complete without `invalid PHY package`, `failed to load CR`, `RF parameters exceed size`, or `rf path ... reg h2c config failed` messages.
- RF table loading should exercise several board/RFE variants if available, because many rows are hidden behind package conditions.
- Post-init connectivity tests should cover both 2.4 GHz and 5/6 GHz operation, different bandwidths, and RF path B sensitivity/transmit behavior.
- Bluetooth coexistence tests are relevant because later path-B LUT edits in `rtw8852c.c` assume RF-B LUT baseline state.
- Register-dump comparison against a known-good RTL8852C table load is the strongest direct validation for the chunk, especially around the `0x0EF`/`0x033`/`0x03F` indirect pages and the long `0x100EE`/`0x10030` region.
- Static review can check that the chunk remains inside `rtw89_8852c_phy_radiob_regs[]`, that braces and commas preserve array shape, and that the exported `ARRAY_SIZE()` descriptor still covers the full table.

### subset-b-004958: lines 26920-35031

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 26920-35031

## Scope

This chunk covers the tail of `rtw89_8852c_phy_radiob_regs`, all of `rtw89_8852c_phy_nctl_regs`, the complete `rtw89_8852c_txpwr_byrate` table, the RTL8852C transmit-power thermal tracking delta-swing tables, the transmit-shape limit tables, and the beginning of the 2.4 GHz and 5 GHz transmit-power regulatory limit data. The source is table-driven C data for the Realtek RTW89 RTL8852C wireless driver; it contains no local functions, but it defines data consumed by generic PHY, RF, RFK/TSSI, and transmit-power code paths.

## Purpose

The data in this range programs hardware state and policy for RTL8852C:

- The radio-B table tail continues RF path B initialization using `struct rtw89_reg2_def` register/data pairs. It includes many conditional branch markers encoded in the pseudo-address field, selecting values by RFE package and chip cut/version before writing RF register payloads.
- `rtw89_8852c_phy_nctl_regs` initializes the NCTL block used by RF calibration/control logic. It starts with control registers around `0x8000` and then loads a large microcode-like sequence across NCTL memory/register windows, ending by toggling `0x8080`.
- `rtw89_8852c_txpwr_byrate` provides packed per-rate power offsets by band, NSS, rate section, starting index, length, and packed byte data.
- `_txpwr_track_delta_swingidx_*` arrays provide thermal compensation curves for 2 GHz, 5 GHz, and 6 GHz, split by RF path A/B and positive/negative thermal direction.
- `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru` encode regulatory transmit-shaping limits per band, shaping mode, RU/non-RU mode, and regulatory domain.
- `rtw89_8852c_txpwr_lmt_2g` and the beginning of `rtw89_8852c_txpwr_lmt_5g` encode regulatory power ceilings as `s8` values indexed by bandwidth, number of transmit chains, rate-section limit bucket, beamforming flag, regulatory domain, and channel index.

## Important Types And APIs

- `struct rtw89_reg2_def`: `{ addr, data }` entries used for BB/RF/NCTL table initialization. The generic loader interprets high bits in `addr` as conditional control records and ordinary values as hardware register addresses.
- `struct rtw89_phy_table`: wraps a `rtw89_reg2_def` array with `n_regs`, `rf_path`, and an optional config callback. Later in the same file, `rtw89_8852c_phy_radiob_table` points at `rtw89_8852c_phy_radiob_regs` with `RF_PATH_B` and `rtw89_phy_config_rf_reg_v1`; `rtw89_8852c_phy_nctl_table` points at `rtw89_8852c_phy_nctl_regs`.
- `rtw89_phy_init_reg()` in `phy.c`: common table interpreter. It selects the matching headline for `rtwdev->efuse.rfe_type` and chip cut/version, tracks branch/elif/else/end/check pseudo-records, and calls the supplied config function only for matched data records.
- `rtw89_phy_init_rf_reg()` consumes chip RF tables, including path B, and can either write immediately or build firmware H2C RF config data through `rtw89_phy_config_rf_reg_v1`.
- `rtw89_phy_init_rf_nctl()` preinitializes the NCTL block, chooses either firmware-provided NCTL data or `chip->nctl_table`, then applies `rtw89_8852c_phy_nctl_table` with BB-register writes.
- `struct rtw89_txpwr_byrate_cfg`: `{ band, nss, rs, shf, len, data }`; used by `rtw89_phy_load_txpwr_byrate()` to unpack up to four byte-sized `s8` offsets into `rtwdev->byr[band][0]`.
- `struct rtw89_txpwr_track_cfg`: pointer table wired later as `rtw89_8852c_trk_cfg`; RFK/TSSI code uses these curves when firmware does not provide a dynamic tracking table.
- `struct rtw89_rfe_parms`: later `rtw89_8852c_dflt_parms` references the by-rate table, transmit-power limit arrays, RU limit arrays, and shape limit arrays. `core.c` selects RFE parameters and calls `rtw89_load_txpwr_table(rtwdev, rtwdev->rfe_parms->byr_tbl)`.

## Control Flow And Integration

The RF path B data in this chunk is not executed directly. During RF initialization, `rtw89_phy_init_rf_reg()` iterates RF paths, selects `chip->rf_table[RF_PATH_B]` or firmware override data, and invokes `rtw89_phy_init_reg()`. The branch records embedded in the table decide which RF entries apply to the current RFE/chip version. Matched path-B records are passed to `rtw89_phy_config_rf_reg_v1`, which ignores pseudo or small addresses below `0x100` and stores RF writes for the selected RF path.

NCTL initialization follows a separate PHY flow. `rtw89_phy_init_rf_nctl()` calls `rtw89_phy_preinit_rf_nctl()`, which enables IQK/DPK clock/reset bits, writes `R_NCTL_CFG`, and polls `0x8080` until the NCTL block reports ready. It then applies `rtw89_8852c_phy_nctl_regs` with `rtw89_phy_config_bb_reg`. The final entries in the NCTL array write `0x8080` to `0x4`, then `0x0`, and clear `0x8088`, which looks like an explicit trigger/reset/cleanup sequence after loading the large NCTL instruction/config image.

By-rate transmit power initialization is driven from device bring-up in `core.c`: after the driver selects default or firmware-supplied RFE parameters, it loads `rfe_parms->byr_tbl`. For the static RTL8852C defaults, `rtw89_8852c_byr_table` points at the `rtw89_8852c_txpwr_byrate` entries in this chunk. `rtw89_phy_load_txpwr_byrate()` unpacks each byte of `data` into the rate-section storage selected by `band`, `nss`, and `rs`.

Thermal tracking integration is in `rtw8852c_rfk.c`. The TSSI tracking path first checks for firmware-provided `rtwdev->fw.elm_info.txpwr_trk`; if absent, it selects the static arrays from `rtw89_8852c_trk_cfg` based on channel subband and RF path. For 6 GHz it maps channel band indexes in pairs to rows 0-3 of the 6 GHz A/B positive/negative arrays.

The transmit-shape and transmit-power limit arrays are consumed indirectly through `rtw89_8852c_dflt_parms`. Generic PHY transmit-power filling code indexes these arrays by band, channel, regulatory domain, bandwidth, beamforming, RU mode, and NSS, then combines them with offsets and dynamic limits before programming hardware.

## State And Persistence Behavior

All definitions in this chunk are static or const compile-time data. They are immutable after module load and do not persist runtime state themselves. Runtime state is produced when generic loader code copies or applies these values:

- RF and NCTL arrays persist as hardware register/NCTL RAM state until reset, power cycle, reinitialization, firmware override, or channel/RFK reconfiguration changes them.
- By-rate values are unpacked into `rtwdev->byr`, becoming per-device RAM state used for later transmit-power programming.
- Thermal tracking arrays remain read-only lookup tables. Runtime thermal offsets are computed into temporary/local state and TSSI structures in RFK/TSSI code.
- Regulatory limit arrays stay const; the selected limits are read repeatedly during channel or regulatory changes and converted into hardware/MAC transmit-power commands.

Because firmware elements can override several table sources (`elm_info->rf_radio`, `elm_info->rf_nctl`, `fw.elm_info.txpwr_trk`, firmware RFE data), this chunk is the built-in fallback/default dataset rather than the only possible runtime source.

## Dependencies

This chunk depends on RTW89 core definitions and constants from nearby driver headers:

- `core.h` for `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, RFE parameter structures, RF path enums, regulatory-domain counts, and transmit-power limit dimensions.
- `phy.h` for `struct rtw89_txpwr_byrate_cfg`, `struct rtw89_txpwr_track_cfg`, `DELTA_SWINGIDX_SIZE`, rate-section constants, and PHY loader prototypes.
- `rtw8852c_table.h` for external declarations consumed by `rtw8852c.c` and `rtw8852c_rfk.c`.
- `phy.c`, `core.c`, and `rtw8852c_rfk.c` for the consumers that interpret, copy, or apply the tables.
- Hardware/firmware contracts for RTL8852C register encodings. The many numeric values are not self-describing and must match Realtek hardware specifications and calibration expectations.

## Risks And Edge Cases

- Table corruption is high impact. A single wrong NCTL or RF value can break RF bring-up, calibration, sensitivity, transmit quality, or regulatory behavior without producing compile errors.
- Conditional branch pseudo-addresses in the RF table are fragile. Incorrect RFE/CV targets can silently select the wrong path for specific board packages or chip cuts.
- `rtw89_phy_load_txpwr_byrate()` trusts `rs`, `nss`, `shf`, and `len` to fit the destination rate arrays. Bad table dimensions would write the wrong per-rate slot or potentially overrun if constants and table entries diverge.
- Values of `127` in transmit-power limit tables appear to mean an invalid/unlimited/disabled sentinel in this driver family. Misinterpreting them as a normal high dBm value would be dangerous; consumers must preserve the existing sentinel semantics.
- Regulatory-domain tables are sparse designated initializers. Unspecified entries default to zero, so missing rows may unintentionally clamp power to zero unless zero is expected for that dimension.
- Thermal tracking rows must stay aligned with subband selection logic in `rtw8852c_rfk.c`. Adding 6 GHz subband indexes or changing subband enums without updating these arrays would choose the wrong compensation curve.
- Firmware override behavior means tests using only firmware-supplied tables may not exercise these static fallback arrays.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build with `W=1` or equivalent kernel warnings to catch malformed initializers and dimension mismatches in the large multi-dimensional arrays.
- Confirm probe/init logs do not report `invalid PHY package`, `failed to load CR`, RF H2C config failures, or `failed to poll nctl block`.
- Exercise boards with multiple `efuse.rfe_type` and chip cut/version combinations so the RF path B conditional table headlines and branches are actually selected.
- Verify RF/NCTL initialization by checking successful IQK/DPK/TSSI calibration, stable association, channel switching, scan, and throughput on both RF paths.
- Validate transmit power by reading programmed by-rate offsets and regulatory limit outputs for 2.4 GHz and 5 GHz channels, especially channels with sentinel `127`, domain-specific exceptions, and edge channels.
- Run thermal/TSSI tracking across temperature deltas and confirm path A/B swing index offsets follow the expected positive and negative curves for 2 GHz, 5 GHz subbands, and 6 GHz subbands.

### subset-b-004959: lines 35032-41891

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 35032-41891

## Purpose

This chunk is static regulatory transmit-power data for the Realtek RTL8852C `rtw89` wireless driver. It covers the tail of `rtw89_8852c_txpwr_lmt_5g` and the opening section of `rtw89_8852c_txpwr_lmt_6g`, not executable logic. The data gives per-channel absolute TX power limits for 5 GHz and 6 GHz operation, keyed by bandwidth, number of TX chains, rate section, beamforming state, regulatory domain, and, for 6 GHz, the 6 GHz power mode.

The 5 GHz table starts at line 33981 as:

```c
const s8 rtw89_8852c_txpwr_lmt_5g[RTW89_5G_BW_NUM][RTW89_NTX_NUM]
                                 [RTW89_RS_LMT_NUM][RTW89_BF_NUM]
                                 [RTW89_REGD_NUM][RTW89_5G_CH_NUM]
```

The 6 GHz table starts at line 36955 as:

```c
const s8 rtw89_8852c_txpwr_lmt_6g[RTW89_6G_BW_NUM][RTW89_NTX_NUM]
                                 [RTW89_RS_LMT_NUM][RTW89_BF_NUM]
                                 [RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER]
                                 [RTW89_6G_CH_NUM]
```

## Important Data and Types

- `rtw89_8852c_txpwr_lmt_5g`: 5 GHz absolute power-limit table. This chunk begins in the middle of the table at `[0][0][2][0][RTW89_KCC][15]` and continues through the end of the 5 GHz initializer before the 6 GHz declaration.
- `rtw89_8852c_txpwr_lmt_6g`: 6 GHz absolute power-limit table. This chunk begins the table with `RTW89_WW` defaults and then country/domain-specific rows such as `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`, `RTW89_MEXICO`, `RTW89_UKRAINE`, `RTW89_CHILE`, `RTW89_QATAR`, and `RTW89_THAILAND`.
- `struct rtw89_txpwr_rule_5ghz` and `struct rtw89_txpwr_rule_6ghz` in `core.h`: typed pointers that describe the exact dimensions consumed by generic PHY TX power code.
- `struct rtw89_rfe_parms`: binds these generated chip tables into the runtime RFE parameter set. At the end of the file, `rtw89_8852c_dflt_parms.rule_5ghz.lmt` points to `rtw89_8852c_txpwr_lmt_5g`, and `.rule_6ghz.lmt` points to `rtw89_8852c_txpwr_lmt_6g`.

The table values are signed 8-bit power quantities in the driver's RF power representation. Later PHY code converts selected values through `rtw89_phy_txpwr_rf_to_mac()` before writing MAC TX power pages. The value `0` is significant because lookup code treats it as "no explicit value, fall back to `RTW89_WW`." The value `127` is a sentinel-like high limit frequently used for unsupported/prohibited/not-constraining combinations; it is still data and is carried through the same min/fallback logic.

## Control Flow and Integration

There is no local control flow in this range; all behavior comes from consumers:

1. `rtw8852c_chip_info.dflt_parms` points to `rtw89_8852c_dflt_parms`.
2. Channel/power setup in `rtw8852c_set_txpwr()` calls `rtw89_phy_set_txpwr_limit()` after by-rate power, offsets, and TX shape are configured.
3. The AX implementation, `rtw89_phy_set_txpwr_limit_ax()`, builds per-NSS power-limit pages by calling `rtw89_phy_fill_txpwr_limit_ax()`.
4. Fill helpers call `rtw89_phy_read_txpwr_limit()` for each rate/bandwidth/beamforming/channel slot.
5. `rtw89_phy_read_txpwr_limit()` chooses the 5 GHz or 6 GHz rule pointer based on `chan->band_type`, indexes by channel-to-table index, regulatory domain from `rtw89_regd_get()`, and 6 GHz power type from `rtwdev->regulatory.reg_6ghz_power`.
6. If a domain-specific entry is zero, the code falls back to the `RTW89_WW` entry. The selected RF-limit value is combined with optional dynamic antenna-gain offset, SAR, and 6 GHz TPE constraint, then converted and written to MAC registers via `rtw89_mac_txpwr_write32()`.

The RU-limit path is adjacent in the same driver architecture but not in this line range: `rtw89_8852c_txpwr_lmt_ru_*` begins later in this file. This chunk feeds absolute power limits, not RU-specific OFDMA limits.

## State and Persistence

The tables are compile-time `static const` data in the kernel image. They are not mutated after load. Runtime state affected by this data is indirect:

- Current country/regulatory mapping in `rtwdev->regulatory` chooses the regulatory-domain index.
- Current channel context chooses band, bandwidth, primary channel, and 6 GHz power mode.
- SAR, antenna-gain, and TPE state can further reduce the selected table value.
- The resolved values are written into hardware/MAC power-limit pages during channel or TX-power reconfiguration.

Firmware RFE element handling can replace RFE parameter pointers when valid firmware-provided TX-power data exists, but the default RTL8852C path wires these arrays through `rtw89_8852c_dflt_parms`.

## Dependencies

- Dimension constants and enums from `core.h`: `RTW89_5G_BW_NUM`, `RTW89_6G_BW_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_REGD_NUM`, `RTW89_5G_CH_NUM`, `RTW89_6G_CH_NUM`, and `NUM_OF_RTW89_REG_6GHZ_POWER`.
- Regulatory-domain definitions such as `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`, `RTW89_MEXICO`, `RTW89_UKRAINE`, `RTW89_CHILE`, `RTW89_QATAR`, and `RTW89_THAILAND`.
- Generic PHY power-limit helpers in `phy.c`, especially `rtw89_phy_read_txpwr_limit()`, `rtw89_phy_fill_txpwr_limit_ax()`, and `rtw89_phy_set_txpwr_limit_ax()`.
- RTL8852C chip glue in `rtw8852c.c`, especially `rtw8852c_set_txpwr()` and the `.dflt_parms` chip-info assignment.

## Risks and Edge Cases

- The multidimensional initializer is easy to corrupt manually. A wrong index order changes regulatory behavior without compiler errors because the type still matches.
- Zero has fallback semantics, so accidentally changing a legitimate low limit to zero can silently select the `RTW89_WW` limit.
- `127` entries are intentionally common; treating them as ordinary dBm values in documentation or generated tooling would be misleading. They are table sentinels/high non-limiting values in the driver's power-limit space.
- 6 GHz rows include an extra power-mode axis. Mixing `[regd][reg6][ch_idx]` order with 5 GHz's `[regd][ch_idx]` order would cause severe regulatory misapplication.
- This is compliance-sensitive data. Regressions can cause underpowered links, certification failure, or over-limit transmission in specific countries/channels.

## Test Signals

- Build coverage: compile the `rtw89` driver with `rtw8852c_table.c`; type/dimension mismatches in these arrays or `rtw89_rfe_parms` pointers should fail at compile time.
- Runtime debug: enable `RTW89_DBG_TXPWR` and verify channel changes log `set txpwr limit with ch=... bw=...`, then inspect resulting TX power pages through existing debugfs/register tooling.
- Regulatory matrix checks: exercise 5 GHz and 6 GHz channels across domains such as FCC, ETSI, MKK, KCC, ACMA, CN, UK, and WW fallback, confirming zeros fall back and `127` entries do not become unintended caps.
- Channel-width checks: verify 20/40/80/160 MHz 5 GHz paths and 6 GHz power-mode selections, because both axes are present in this chunk.
- SAR/TPE interaction checks: confirm final MAC limits are the minimum of the table-derived value, SAR, and 6 GHz TPE constraint where applicable.

### subset-b-004960: lines 41892-49275

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 41892-49275

## Scope and Purpose

This chunk is a data-only section of the Realtek rtw89 RTL8852C PHY table source. It contributes regulatory transmit-power limits used by the 8852C default RFE parameters. The chunk contains no executable functions; its behavior comes from large `static const s8` designated-initializer tables that are later referenced through `rtw89_8852c_dflt_parms`.

Visible coverage in this chunk:

- Tail of `rtw89_8852c_txpwr_lmt_6g`, a 6 GHz non-RU transmit-power limit table declared earlier at line 36955.
- Entire `rtw89_8852c_txpwr_lmt_ru_2g`, declared at lines 46234-46235.
- Beginning and middle of `rtw89_8852c_txpwr_lmt_ru_5g`, declared at lines 47415-47416; this table continues past the assigned end line at 49275.

The data maps regulatory domains, channel indexes, transmit-chain count, bandwidth/RU category, rate section, beamforming flag, and 6 GHz power mode into signed RF-domain power-limit values. It is part of the default static regulatory baseline for 8852C unless firmware RFE data overrides the corresponding rule pointers.

## Important APIs, Types, and Data Contracts

- `rtw89_8852c_txpwr_lmt_6g` has shape `[RTW89_6G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER][RTW89_6G_CH_NUM]`. The visible tail writes 6 GHz regulatory entries for bandwidth/rate/beamforming combinations, including many `RTW89_REG_6GHZ_POWER_*` subindexes.
- `rtw89_8852c_txpwr_lmt_ru_2g` has shape `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`, where `RTW89_RU_NUM` includes `RTW89_RU26`, `RTW89_RU52`, `RTW89_RU106`, `RTW89_RU52_26`, and `RTW89_RU106_26`. The 2 GHz table covers channel indexes 0-13, matching the 14 2.4 GHz channels.
- `rtw89_8852c_txpwr_lmt_ru_5g` has shape `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`. The visible section covers RU indexes 0-2, both NTX indexes, and 5 GHz channel indexes through 35 at the chunk boundary; the remaining entries continue after this chunk.
- `enum rtw89_regulation_type` defines the regulatory indexes used here: `RTW89_WW`, `RTW89_ETSI`, `RTW89_FCC`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_MEXICO`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_CN`, `RTW89_QATAR`, `RTW89_UK`, and `RTW89_THAILAND`.
- `struct rtw89_txpwr_rule_2ghz`, `struct rtw89_txpwr_rule_5ghz`, and `struct rtw89_txpwr_rule_6ghz` in `core.h` define the pointer shapes consumed by the PHY code. `rtw89_8852c_dflt_parms` wires `.rule_2ghz.lmt_ru`, `.rule_5ghz.lmt_ru`, `.rule_6ghz.lmt`, and `.rule_6ghz.lmt_ru` to the 8852C tables.

## Control Flow and Runtime Use

There is no local control flow in this chunk. Runtime control flow is indirect:

1. The device selects `rtw89_8852c_dflt_parms` as the default RFE parameter set.
2. `rtw89_phy_read_txpwr_limit_ru()` receives band, RU size, NTX, and channel.
3. It derives the channel index with `rtw89_channel_to_idx()`, chooses the active regulatory domain with `rtw89_regd_get()`, and for 6 GHz also uses `rtwdev->regulatory.reg_6ghz_power`.
4. For 2 GHz and 5 GHz, it reads `(*rule_*ghz->lmt_ru)[ru][ntx][regd][ch_idx]`; for 6 GHz it reads `(*rule_6ghz->lmt_ru)[ru][ntx][regd][reg6][ch_idx]`.
5. If a regional RU limit is zero, the lookup falls back to the `RTW89_WW` default row. Nonzero values, including negative limits and `127`, bypass that fallback.
6. The selected RF-domain value is combined with optional dynamic antenna-gain RFE limits, converted with `rtw89_phy_txpwr_rf_to_mac()`, then bounded by SAR and TPE constraints.
7. `rtw89_phy_fill_txpwr_limit_ru_ax()` arranges those reads into a hardware page according to channel width, and `rtw89_phy_set_txpwr_limit_ru_ax()` writes the packed bytes to `R_AX_PWR_RU_LMT`.

The non-RU 6 GHz entries visible at the start of this chunk flow through the analogous `rtw89_phy_read_txpwr_limit()` path and are written by `rtw89_phy_set_txpwr_limit_ax()` to `R_AX_PWR_LMT`.

## State and Persistence Behavior

The data in this chunk is `static const` and has no runtime mutation or persistence of its own. It persists only as compiled kernel module image data. Runtime state that affects interpretation lives outside the table:

- `rtwdev->rfe_parms` selects either these defaults or firmware-loaded override tables.
- `rtwdev->regulatory` stores the current regulatory domain and 6 GHz power mode.
- SAR, TPE, and antenna-gain logic apply additional runtime caps after table lookup.

Because C designated initializers leave omitted elements as zero, zero is semantically important: in the lookup path, a zero regional value means "fall back to WW" for the default table. A deliberate zero power limit is therefore hard to represent in these static regional rows without being interpreted as missing.

## Data Characteristics in This Chunk

- The assigned span contains 7,376 designated assignments.
- Values range from `-30` to `127`. Common values include ordinary positive RF power limits such as 16, 20, 28, 30, 44, 52, 58, 70, and 74.
- `127` is heavily used as a sentinel-style permissive/invalid/no-specific-limit value in many regional/channel combinations. Since it is nonzero, it will not trigger WW fallback.
- Negative values such as `-30`, `-20`, `-6`, `-4`, and `-2` appear in edge or restricted combinations. These are still valid signed table entries and flow through the same RF-to-MAC conversion and final min caps.
- The 2 GHz RU table includes `RTW89_WW` defaults for all 14 channel indexes, then regional overrides for ETSI/FCC/MKK/IC/KCC/ACMA/CN/UK/MEXICO/UKRAINE/CHILE/QATAR/THAILAND where needed.
- The 5 GHz RU table visible here covers lower and middle channel-index ranges and regulatory domains including WW defaults plus FCC/ETSI/MKK/IC/KCC/ACMA/CN/UK/MEXICO/UKRAINE/CHILE/QATAR/THAILAND. The table continues after line 49275.

## Dependencies and Integration Points

- Depends on `core.h` constants for channel counts, RU indexes, regulatory-domain indexes, NTX count, 6 GHz power-mode count, and bandwidth counts. Reordering enum values would silently remap regulatory limits, which is why the regulation enum warns not to insert values in the middle.
- Integrated into 8852C default parameters at the bottom of `rtw8852c_table.c` through `rtw89_8852c_dflt_parms`.
- Consumed by common AX PHY power code in `phy.c`, especially `rtw89_phy_read_txpwr_limit()`, `rtw89_phy_read_txpwr_limit_ru()`, `rtw89_phy_fill_txpwr_limit_ru_ax()`, and `rtw89_phy_set_txpwr_limit_ru_ax()`.
- May be superseded by firmware RFE tables loaded in `fw.c` when firmware-provided `lmt_ru_*ghz`, `da_lmt_ru_*ghz`, or related configs validate. In that case the same pointer contract is used, but data comes from `struct rtw89_rfe_data`.
- Debug visibility is through the tx-power debug mappings in `debug.c`, which can expose the filled hardware-facing RU limit pages rather than these source initializers directly.

## Risks and Edge Cases

- Table-shape drift is high risk. Any mismatch between `RTW89_*_CH_NUM`, `RTW89_RU_NUM`, `RTW89_REGD_NUM`, or 6 GHz power-mode enum values and the generated initializer indexes can silently change effective transmit limits or fail compilation only for out-of-range indexes.
- `0` means fallback in the lookup code. If regulatory data needs an actual zero limit, this convention can encode the wrong behavior unless the lookup logic changes or another sentinel is used.
- `127` is nonzero and bypasses fallback. If treated as an ordinary high limit, later `min()` operations normally constrain it with SAR/TPE/other caps, but a misplaced `127` in a regulatory row can remove the intended regional restriction.
- Negative values are legal signed `s8` table entries. They should be reviewed carefully at band edges because they can materially reduce or alter programmed power and may interact with RF-to-MAC conversion behavior.
- The chunk boundary cuts through `rtw89_8852c_txpwr_lmt_ru_5g`; whole-file conclusions must merge the next chunk to understand all 5 GHz RU channel indexes and RU categories.
- Regulatory compliance risk is the main behavioral risk. These values directly influence the power limits written to hardware for OFDMA RU transmissions and, for the leading part of the chunk, 6 GHz non-RU transmissions.

## Test Signals

- Build-time signals: compile this driver with `W=1` or normal kernel build to catch out-of-range designated initializers and type-shape mismatches. Existing `BUILD_BUG_ON()` checks in the PHY write path validate hardware page struct sizes, not the regulatory correctness of this source data.
- Runtime debug signals: enable rtw89 TX power debug output and verify `set txpwr limit` / `set txpwr limit ru` messages for expected channel and bandwidth selections, then inspect the debugfs tx-power maps if available.
- Regulatory matrix tests should exercise multiple domains visible in this chunk: WW fallback, FCC/IC/CHILE restricted negative or low entries, ETSI/UK/QATAR low 5 GHz ranges, CN-specific 5 GHz rows, and KCC/MKK special cases.
- Boundary tests should cover 2.4 GHz channels 12-14, 5 GHz lower/mid channels around indexes 0, 15, 37, and 48 where many sentinel transitions appear, and 6 GHz channel indexes around 75-119 from the visible 6 GHz tail.
- Firmware override tests should confirm that valid RFE data replaces these defaults and invalid firmware entries are rejected by the `fw_txpwr_lmt_ru_*ghz_entry_valid()` validators before pointer reassignment.

## Cross-Chunk Notes

- This chunk starts inside `rtw89_8852c_txpwr_lmt_6g`, whose declaration and earlier bandwidth/regulatory data are in previous chunks.
- `rtw89_8852c_txpwr_lmt_ru_5g` continues beyond line 49275 and must be reconciled with later chunk research before producing the final per-file report.
- `rtw89_8852c_txpwr_lmt_ru_6g` begins later at line 49772 and is outside this chunk.

### subset-b-004961: lines 49276-57136

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 49276-57136

## Scope

This chunk covers the end of the RTL8852C HE/EHT RU transmit-power limit table data. It starts in the final portion of `rtw89_8852c_txpwr_lmt_ru_5g` and then defines nearly all of `rtw89_8852c_txpwr_lmt_ru_6g`, a static `s8` multidimensional regulatory table for 6 GHz RU-specific transmit-power limits.

The range is data-heavy rather than algorithmic. Its behavior comes from designated initializers, array dimensions, default zero-fill semantics, and the PHY lookup code in `phy.c` that consumes these tables. The chunk ends immediately before the exported PHY/RFE table descriptors that register `rtw89_8852c_txpwr_lmt_ru_6g` into `rtw89_8852c_dflt_parms`.

## Purpose

The chunk provides chip-specific regulatory power caps for resource-unit transmissions on RTL8852C:

- The opening lines finish 5 GHz RU limit entries for RU index `2`, NTX indexes `0` and `1`, multiple regulatory domains, and high 5 GHz channel indexes.
- `rtw89_8852c_txpwr_lmt_ru_6g` maps `(RU size, transmit-chain count, regulatory domain, 6 GHz power class, channel index)` to an RF-domain power limit byte.
- The 6 GHz table includes worldwide defaults under `RTW89_WW`, then overrides for domains such as `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_QATAR`, `RTW89_UK`, and `RTW89_THAILAND`.
- Values of `127` are used as sentinel-like "not constrained/not applicable" entries in the same table shape as other rtw89 generated power tables. Nonzero concrete values, including negative values, are actual limit data consumed by the PHY power decision path.

## Important APIs, Types, and Data

- `rtw89_8852c_txpwr_lmt_ru_6g` is declared as:
  `const s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER][RTW89_6G_CH_NUM]`.
- `RTW89_RU_NUM` covers `RTW89_RU26`, `RTW89_RU52`, `RTW89_RU106`, `RTW89_RU52_26`, and `RTW89_RU106_26`; this chunk populates RU indexes `0`, `1`, and `2`.
- `RTW89_NTX_NUM` indexes transmit stream/chain counts. This table populates NTX indexes `0` and `1`.
- `NUM_OF_RTW89_REG_6GHZ_POWER` covers VLP, LPI, and STD. The lookup fallback uses `RTW89_REG_6GHZ_POWER_DFLT`, which aliases VLP.
- `RTW89_6G_CH_NUM` is 120 and indexes the driver's internal ordered 6 GHz channel table rather than raw IEEE channel numbers.
- `struct rtw89_txpwr_rule_6ghz` stores the `lmt_ru` pointer used by runtime PHY code.
- `struct rtw89_txpwr_lmt_ru_6ghz_data` and `struct rtw89_fw_txpwr_lmt_ru_6ghz_entry` mirror this shape for firmware-provided RFE table overlays, including the extra `reg_6ghz_power` dimension.

## Control Flow

This source chunk has no executable branches. Its control flow is compile-time initialization followed by runtime indexing elsewhere:

1. The C compiler zero-fills unspecified cells in the static array.
2. Designated initializers assign selected legal cells with RF power-limit values.
3. The nearby `rtw89_8852c_dflt_parms` descriptor assigns `.rule_6ghz.lmt_ru = &rtw89_8852c_txpwr_lmt_ru_6g`.
4. `rtw89_phy_get_txpwr_limit_ru()` selects the correct band table during transmit-power limit calculation.
5. For 6 GHz, the lookup reads `(*rule_6ghz->lmt_ru)[ru][ntx][regd][reg6][ch_idx]`; if that cell is zero, it falls back to the worldwide default `RTW89_WW` plus `RTW89_REG_6GHZ_POWER_DFLT`.
6. The selected limit is converted from RF to MAC units, then clamped with optional antenna-gain offset handling, SAR, and transmit-power-envelope constraints.

The most important data-flow detail is that `0` is not just a power value in this path. It also triggers fallback to the worldwide default. Entries that need to avoid fallback use nonzero values, including `127` when the generated table wants an unconstrained/not-applicable marker.

## State and Persistence Behavior

The table is immutable static driver data. It is compiled into the module image and persists for the life of the loaded driver. Runtime state is not stored in this chunk.

The table affects persistent in-memory PHY behavior through `rtw89_8852c_dflt_parms`: once the chip's RFE parameters point to this static table, every RU transmit-power limit query can use it. Firmware RFE loading can instead populate `rtwdev->rfe_data.lmt_ru_6ghz` and update the active parameter pointers; that overlay uses the same dimensions and lookup semantics but is filled dynamically from firmware records.

## Dependencies and Integration Points

- The file includes `phy.h`, `reg.h`, and `rtw8852c_table.h`, which provide table types, chip declarations, register helpers, and PHY integration declarations.
- Regulatory domain selection comes from `rtw89_regd_get()` and the country/regulatory mapping in `regd.c`.
- The 6 GHz power-class dimension comes from `rtwdev->regulatory.reg_6ghz_power`.
- Channel indexes come from `rtw89_channel_to_idx()`, so table coordinates must match the driver's internal 6 GHz channel ordering.
- Runtime clamping integrates with `rtw89_phy_ant_gain_offset()`, `rtw89_phy_txpwr_rf_to_mac()`, `rtw89_query_sar()`, and `rtw89_phy_get_tpe_constraint()`.
- Firmware override support in `fw.c` validates `rtw89_fw_txpwr_lmt_ru_6ghz_entry` bounds before writing `data->v[ru][nt][regd][reg_6ghz_power][ch_idx]`.

## Risks and Edge Cases

- Table values are regulatory-critical. A wrong index, copied value, or domain assignment can either over-limit transmit power or unnecessarily reduce throughput.
- The table relies on generated designated initializers. Missing entries are zero, and zero means "try worldwide default" in the lookup path, so accidental omission can silently alter behavior instead of producing a compile error.
- `127` is a meaningful sentinel-like value in the power table ecosystem. Replacing it with `0` changes behavior because zero falls back, while `127` is consumed as a nonzero table result.
- The 6 GHz table has five dimensions. Any mismatch between `RTW89_6G_CH_NUM`, regulatory enum ordering, power-class enum ordering, or RU enum ordering would compile but select the wrong regulatory value at runtime.
- The chunk starts inside the 5 GHz table, so merge-level documentation should connect this report with the preceding chunk to describe the full `rtw89_8852c_txpwr_lmt_ru_5g` declaration and earlier entries.
- Per-regulatory overrides are sparse. Domains without explicit entries inherit through zero fallback, but only after the lookup tests the exact selected domain/power-class cell.

## Test Signals

Useful validation signals include:

- Build coverage for `rtw8852c_table.c` to catch initializer bounds and declaration-shape mismatches.
- Static checks comparing the declared dimensions against `struct rtw89_txpwr_rule_6ghz`, `struct rtw89_txpwr_lmt_ru_6ghz_data`, and `struct rtw89_fw_txpwr_lmt_ru_6ghz_entry`.
- Runtime debug or trace checks around `rtw89_phy_get_txpwr_limit_ru()` for 6 GHz channels, confirming selected `(ru, ntx, regd, reg6, ch_idx)` cells and worldwide fallback behavior.
- Regulatory smoke tests across US/FCC, EU/ETSI, Japan/MKK, Canada/IC, Korea/KCC, Australia/ACMA, UK, Qatar, Thailand, and Chile mappings.
- 6 GHz VLP/LPI/STD power-class tests, especially channel indexes where the table switches from concrete limits to `127`.
- Throughput and RF conformance tests using HE/EHT RU transmissions on 6 GHz to confirm the final MAC-programmed limit is the minimum of RU table, SAR, antenna-gain adjusted dual-antenna limit when present, and TPE constraint.

## Cross-Chunk Notes

The final per-file report should merge this with adjacent chunks that define the full non-RU 6 GHz table, the 2 GHz and 5 GHz RU tables, and the `rtw89_8852c_dflt_parms` registration immediately after this range. The key connection is that this chunk supplies static RTL8852C 6 GHz RU regulatory data, while `phy.c` supplies the lookup semantics and `fw.c` supplies optional firmware override loading for the same table shape.

### subset-b-004962: lines 57137-57159

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 57137-57159

## Scope And Purpose

This chunk is the final exported data section of the RTL8852C table file. It closes the `RTW89_TSSI_BANDEDGE_HIGH` row of `rtw89_8852c_tssi_dbw_table` and defines `rtw89_8852c_dflt_parms`, the default radio front-end parameter bundle for the 8852C chip.

The code is table-driven rather than procedural. Its purpose is to bind previously declared 8852C transmit-power tables into the common rtw89 core contract: by-rate power loading, per-band regulatory power limits for 2 GHz, 5 GHz, and 6 GHz, RU-specific power limits for OFDMA, and TX-shape limit tables used when programming band-edge/TSSI behavior. These objects are immutable `const` data and are exported through `rtw8852c_table.h` for the 8852C chip descriptor in `rtw8852c.c`.

## Important APIs, Types, And Data

`rtw89_8852c_tssi_dbw_table` is a `struct rtw89_phy_tssi_dbw_table`, whose shape is `u32 data[RTW89_TSSI_CFG_NUM][RTW89_TSSI_SBW_NUM]`. The specific visible lines complete the `RTW89_TSSI_BANDEDGE_HIGH` profile with 15 sub-band width entries. The full table also includes flat, low, and mid band-edge profiles just above this chunk.

`rtw89_8852c_dflt_parms` is a `struct rtw89_rfe_parms`. The fields populated here are:

- `byr_tbl`: points at `rtw89_8852c_byr_table`, a `struct rtw89_txpwr_table` wrapper around the 8852C by-rate power data and the `rtw89_phy_load_txpwr_byrate` loader.
- `rule_2ghz`, `rule_5ghz`, `rule_6ghz`: each binds normal channel-width power-limit tables through `.lmt` and RU/OFDMA power-limit tables through `.lmt_ru`.
- `tx_shape`: binds `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru`.

The `struct rtw89_rfe_parms` definition also supports dedicated-antenna rules and a `has_da` flag, but this default 8852C initializer leaves those zeroed. That matters because common PHY code checks `has_da` before consulting dedicated-antenna power tables.

## Control Flow And Integration

The chunk itself has no branches or calls. Runtime flow enters through the chip descriptor in `rtw8852c.c`, where `.dflt_parms = &rtw89_8852c_dflt_parms` and `.tssi_dbw_table = &rtw89_8852c_tssi_dbw_table`.

During device setup, `rtw89_core_setup_rfe_parms()` selects the RFE parameters. For RTL8852C, `rfe_parms_conf` is `NULL`, so the core selects `chip->dflt_parms`. It then calls `rtw89_load_rfe_data_from_fw(rtwdev, sel)`, allowing firmware-provided RFE data to override parts of this static default, and finally loads the selected by-rate table with `rtw89_load_txpwr_table(rtwdev, rtwdev->rfe_parms->byr_tbl)`.

The TX-shape pointers are consumed by `rtw8852c_set_tx_shape()`. That function reads the regulatory domain with `rtw89_regd_get()`, indexes `rfe_parms->tx_shape.lmt` by band/rate-section/regdomain, and uses the OFDM TX-shape value as a TSSI band-edge configuration. The value is passed to `rtw89_phy_tssi_ctrl_set_bandedge_cfg()`, which indexes `chip->tssi_dbw_table->data[bandedge_cfg]` and writes the corresponding per-subband values into MAC/PHY registers.

Power-limit pointers are consumed by common TX power paths in `phy.c`, including code that assembles per-band power constraints for 2 GHz, 5 GHz, and 6 GHz and RU-specific limits. The table shapes are fixed by `struct rtw89_txpwr_rule_2ghz`, `struct rtw89_txpwr_rule_5ghz`, and `struct rtw89_txpwr_rule_6ghz`, so each pointer in this initializer must match the expected compile-time dimensions.

## State And Persistence Behavior

The objects in this chunk are static kernel image data. They do not mutate and do not persist runtime state by themselves.

At runtime, `rtwdev->rfe_parms` persists a pointer to the selected parameter bundle for the lifetime of the device. If firmware RFE data is available, `rtw89_load_rfe_data_from_fw()` copies the static defaults into `rtwdev->rfe_data->rfe_parms` and replaces only the tables that have valid firmware configuration. In that case, this chunk acts as the fallback baseline for any fields the firmware does not provide.

The TSSI DBW values are not persisted after table selection except as programmed hardware register state. `rtw89_phy_tssi_ctrl_set_bandedge_cfg()` writes the selected row to registers and updates the band-edge configuration index; subsequent channel/band/regdomain changes can reprogram these values.

## Dependencies

This chunk depends on many earlier definitions in the same source file:

- `rtw89_8852c_byr_table`, which wraps `rtw89_8852c_txpwr_byrate`.
- `rtw89_8852c_txpwr_lmt_2g`, `rtw89_8852c_txpwr_lmt_5g`, and `rtw89_8852c_txpwr_lmt_6g`.
- `rtw89_8852c_txpwr_lmt_ru_2g`, `rtw89_8852c_txpwr_lmt_ru_5g`, and `rtw89_8852c_txpwr_lmt_ru_6g`.
- `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru`.

It also depends on shared rtw89 type definitions from `core.h` and `phy.h`, and on enum constants such as `RTW89_TSSI_BANDEDGE_HIGH`, `RTW89_TSSI_CFG_NUM`, `RTW89_TSSI_SBW_NUM`, `RTW89_BAND_NUM`, and regulatory/rate-section dimension constants.

## Risks And Edge Cases

The highest-risk behavior is silent miscalibration from a wrong table pointer or wrong table dimensions. The compiler enforces much of the array shape through the pointer types, but it cannot validate that the numeric contents are correct for RTL8852C hardware, board layout, or regulatory requirements.

The TSSI DBW table is indexed by a TX-shape/band-edge value. If `rtw89_8852c_tx_shape_lmt` contains a value outside `RTW89_TSSI_CFG_NUM`, `rtw89_phy_tssi_ctrl_set_bandedge_cfg()` returns early and skips programming. If the value is in range but semantically wrong, the driver will write a valid-looking but incorrect band-edge profile.

Because 8852C sets `rfe_parms_conf = NULL`, all boards use this default unless firmware RFE data overrides it. Missing or invalid firmware data therefore falls back to these static tables, making this initializer the compatibility baseline for all 8852C devices.

The `has_da` flag remains false by default. If an 8852C variant requires dedicated-antenna power rules but firmware does not provide them, common code will not use the zero-initialized `rule_da_*` fields.

## Test Signals

Useful validation signals include successful rtw89 module build with no pointer-type or missing-symbol errors from `rtw8852c_table.c`, `rtw8852c_table.h`, and `rtw8852c.c`.

Runtime test signals are hardware-oriented:

- Device probe reaches `rtw89_core_setup_rfe_parms()` and loads `rtw89_8852c_byr_table` without null-pointer faults.
- Channel setup on 2 GHz, 5 GHz, and 6 GHz completes while applying TX power limits and TX-shape settings.
- TSSI band-edge programming writes the expected number of subband entries and does not hit the out-of-range early return for normal regulatory/channel combinations.
- RF certification, conducted power, EVM, and spectral-mask tests remain within limits, especially at band edges and RU/OFDMA transmit modes.
- Regression logs show no WARN/OOPS around `rtw89_phy_tssi_ctrl_set_bandedge_cfg()`, `rtw8852c_set_tx_shape()`, or common TX power setup.
