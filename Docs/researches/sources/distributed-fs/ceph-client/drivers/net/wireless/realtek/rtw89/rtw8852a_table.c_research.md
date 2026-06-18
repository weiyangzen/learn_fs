# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004940`: lines 1-8205, `Docs/researches/chunks/subset-b-004940_research.md`
- `subset-b-004941`: lines 8206-15450, `Docs/researches/chunks/subset-b-004941_research.md`
- `subset-b-004942`: lines 15451-22867, `Docs/researches/chunks/subset-b-004942_research.md`
- `subset-b-004943`: lines 22868-30637, `Docs/researches/chunks/subset-b-004943_research.md`
- `subset-b-004944`: lines 30638-37904, `Docs/researches/chunks/subset-b-004944_research.md`
- `subset-b-004945`: lines 37905-45612, `Docs/researches/chunks/subset-b-004945_research.md`
- `subset-b-004946`: lines 45613-51011, `Docs/researches/chunks/subset-b-004946_research.md`

## Chunk Research

### subset-b-004940: lines 1-8205

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 1-8205

## Scope

This chunk covers the start of the RTL8852A PHY table translation unit. It includes:

- File prologue and dependencies on `phy.h`, `reg.h`, and `rtw8852a_table.h`.
- The full `static const struct rtw89_reg2_def rtw89_8852a_phy_bb_regs[]` baseband initialization table, lines 9-1209.
- The opening prefix of `static const struct rtw89_reg2_def rtw89_8852a_phy_radioa_regs[]`, starting at line 1213 and continuing past this chunk. The assigned range ends inside this RF path-A table at line 8205, so the RF table is intentionally incomplete here and must be reconciled with later chunks before whole-file conclusions are finalized.

## Purpose

`rtw8852a_table.c` is a data-heavy chip-parameter file for Realtek's `rtw89` RTL8852A 802.11ax driver. This chunk provides register-programming data consumed by the generic PHY initialization machinery rather than executable policy code. The data establishes initial BB and RF register state for different RTL8852A RFE/CV/package cases.

The complete file later exports `rtw89_8852a_phy_bb_table`, `rtw89_8852a_phy_radioa_table`, `rtw89_8852a_phy_radiob_table`, `rtw89_8852a_phy_nctl_table`, transmit-power tracking config, and default RFE parameters. This chunk supplies the backing arrays for the BB table and the beginning of the radio path-A table.

## Important Types and APIs

- `struct rtw89_reg2_def`: simple `{ addr, data }` register table entry. In these tables, `addr` is not always a literal hardware register. It can be a Realtek PHY parser pseudo-address for conditions, delays, or block delimiters.
- `struct rtw89_phy_table`: wrapper used later in the file to bind a `reg2_def` array, element count, RF path, and optional config callback.
- `rtw89_phy_init_reg()`: generic parser in `phy.c` that walks a `struct rtw89_phy_table`, selects a headline for current `rtwdev->efuse.rfe_type` and chip cut/version, evaluates conditional blocks, and calls the selected table's config function for matched rows.
- `rtw89_phy_config_bb_reg()`: BB-row writer used for `rtw89_8852a_phy_bb_regs`; handles small delay sentinel addresses `0xfe` through `0xf9`, bypass data, PHY0/PHY1 address offsets, then writes via `rtw89_phy_write32()`.
- `rtw89_phy_config_rf_reg()` and RF H2C staging in `rtw89_phy_init_rf_reg()`: RF-row path used for radio tables. RF table rows may be sent through firmware H2C batching or written directly depending on init mode and chip support.
- `rtw8852a_chip_info` in `rtw8852a.c`: integrates the complete table exports through `.bb_table = &rtw89_8852a_phy_bb_table`, `.rf_table = { &rtw89_8852a_phy_radioa_table, &rtw89_8852a_phy_radiob_table }`, and `.nctl_table = &rtw89_8852a_phy_nctl_table`.

## Data Covered

`rtw89_8852a_phy_bb_regs[]` begins with headline entries such as `0xF0FF0001`, `0xF03300FF`, `0xF03500FF`, `0xF03200FF`, `0xF03400FF`, and `0xF03600FF`. These are parser metadata used to pick the best RFE/CV-specific case before real writes start. The table then configures BB blocks around addresses such as `0x704`, `0x714`, `0x980`, `0xC3C`-`0xC70`, path-paired regions `0x12xx`/`0x32xx`, and path-paired high ranges `0x58xx`/`0x78xx`. Repeated path-paired writes indicate mirrored PHY/RF front-end setup for the two receive/transmit chains.

The BB table includes many parser control rows such as `0x80ff0001`, `0x903300ff`, `0xA0000000`, `0xB0000000`, and `0x40000000`. These are part of the Realtek table language: conditional start/end and delay/control markers rather than ordinary CR addresses. In the assigned range there are 8,193 brace-style entries; roughly 2,959 have high-bit pseudo/control-looking addresses, and `0x40000000` delay/control pairs account for a large fraction of conditional sequencing.

`rtw89_8852a_phy_radioa_regs[]` starts at line 1213 with many headline rows for RF path A. The initial headline matrix covers target combinations including `0xF0010000`, `0xF0010001`, `0xF0020001`, `0xF0030001`, `0xF0250001`, `0xF0260001`, `0xF0320001` through `0xF0360001`, then the same family for a second selector value. After the headline, the table repeatedly gates writes to RF registers such as `0x005`, `0x033`, `0x03e`, and `0x03f` behind conditional pseudo-addresses. In this chunk, `0x03f` and `0x03e` are the dominant real RF register addresses, suggesting extensive RF synthesizer/channel/filter or mode-value table programming. The table continues beyond line 8205.

## Control Flow

There is no local function control flow in this chunk; behavior is parser-driven:

1. Driver startup or PHY/RF init reaches the chip info table in `rtw8852a.c`.
2. Generic PHY initialization retrieves `chip->bb_table` and `chip->rf_table[path]`.
3. `rtw89_phy_init_reg()` scans initial headline rows and chooses the best entry for the current RFE type and CV/ACV.
4. It then iterates the remaining rows, tracking conditional-block state from pseudo-addresses.
5. Matched BB rows call `rtw89_phy_config_bb_reg()` and are written as BB CRs or delays.
6. Matched RF rows call RF config handling, which may stage rows into firmware H2C structures before issuing RF programming for the selected path.

The ordering of rows is part of the hardware contract. Repeated writes to the same address are deliberate state transitions; they should not be deduplicated mechanically.

## State and Persistence Behavior

The arrays are `static const` data and hold no runtime mutable state. Runtime persistence is entirely in hardware/firmware side effects: once parsed, rows program BB/RF registers on the device. Conditional selection depends on persistent device descriptors already read into runtime state, especially efuse RFE type and HAL chip cut/version. The table itself does not store calibration output or counters.

Because BB/RF initialization mutates hardware state, failures are externally visible as bring-up failure, degraded receive/transmit performance, wrong RF path behavior, regulatory/power anomalies in later code, or broken RF calibration assumptions.

## Dependencies and Integration Points

- Depends on `phy.h` for PHY write helpers, RF table parser declarations, and PHY init functions.
- Depends on `reg.h` for named register constants used elsewhere in the same driver family; this chunk itself is mostly numeric vendor table data.
- Depends on `rtw8852a_table.h` for exported table declarations used by `rtw8852a.c`.
- Integrated by `rtw8852a_chip_info` fields for BB/RF/NCTL/default power data.
- RF init is integrated with firmware H2C RF-register configuration when available, so malformed RF table rows can affect both direct I/O and firmware-mediated init paths.
- BB entries interact with later RFK/TSSI/channel code by establishing the baseline register state those routines expect before calibration or channel changes.

## Risks and Review Notes

- The assigned chunk ends in the middle of `rtw89_8852a_phy_radioa_regs[]`; line 8205 is not a semantic boundary. The merge lane must combine later chunks before reporting full radio path-A coverage.
- Pseudo-address rows are easy to mistake for literal register writes. Any parser or table editing must preserve `0xF...` headline rows, `0x8...`/`0x9...` conditional rows, and `0xA0000000`/`0xB0000000` block delimiters.
- The arrays are highly order-sensitive. Reordering, sorting, removing duplicates, or normalizing repeated writes would likely change hardware behavior.
- Numeric-only vendor data has little compiler-level validation. The compiler checks array shape, but not semantic validity of register addresses, condition masks, RF path applicability, or delay placement.
- BB path-paired writes to `0x12xx`/`0x32xx` and `0x58xx`/`0x78xx` must remain aligned; asymmetric edits risk one RF/PHY chain diverging from the other.
- RF path-A rows in this chunk use repeated conditional programming of `0x03e`/`0x03f`; accidental truncation at chunk boundaries would silently omit a large part of path-A setup.

## Test Signals

- Build-level signal: the driver must compile with `rtw8852a_table.c` and its header exports consistent; missing braces or renamed arrays will fail compilation or linkage.
- Init-path signal: booting an RTL8852A device should complete BB/RF init without `invalid PHY package` errors from `rtw89_phy_sel_headline()` and without RF H2C config warnings.
- Runtime signal: device association, scan, TX/RX throughput, RFK/TSSI calibration logs, and thermal/tx-power tracking should remain stable after table changes.
- Regression signal: compare register traces or debug logs before/after edits for the selected RFE/CV case; table changes should be reviewed against vendor-generated reference tables, not inferred by local cleanup.

### subset-b-004941: lines 8206-15450

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 8206-15450

## Scope

This chunk is a middle slice of `rtw89_8852a_phy_radioa_regs[]`, the RF path A initialization table for the Realtek RTL8852A rtw89 wireless driver. It contains generated `struct rtw89_reg2_def` entries rather than C control-flow code. The assigned range begins inside a conditional RF-table block around register page/index `0x033 == 0x12` and ends inside the following block after `0x033 == 0x55`; the complete array spans lines 1213-21599 and is exported through `rtw89_8852a_phy_radioa_table` near the end of the file.

## Purpose

The data programs RF path A calibration/configuration values during PHY/RF initialization. Within this range, the dominant payload is repeated writes to RF register `0x03f` after selecting an RF sub-index with register `0x033`. The slice covers sequential `0x033` selector values from `0x00` through `0x87`, with repeated per-condition payload groups for RFE/CV/package variants. Most groups set one selected `0x033` row and then apply `0x03f` values for several conditional branches, likely Realtek-provided RF gain/TSSI/calibration lookup values.

## Important APIs, Types, And Data

- `struct rtw89_reg2_def` in `core.h` is the table element shape: `{ .addr, .data }`.
- `rtw89_8852a_phy_radioa_regs[]` is a static const register table. This chunk contributes thousands of entries to that array.
- `rtw89_8852a_phy_radioa_table` wraps the array as `struct rtw89_phy_table` with `.rf_path = RF_PATH_A`.
- Encoded table-control entries use the high nibble of `.addr`, interpreted by helpers/macros in `phy.h`: `PHY_COND_BRANCH_IF` (`0x8...`), `PHY_COND_BRANCH_ELIF` (`0x9...`), `PHY_COND_BRANCH_ELSE` (`0xa...`), `PHY_COND_BRANCH_END` (`0xb...`), and `PHY_COND_CHECK` (`0x4...`).
- Real RF writes in this chunk mainly target `0x033` and `0x03f`; there are also two direct writes to `0x0ee`.

## Control Flow

There is no local function body in the chunk. Runtime flow is supplied by the common PHY loader in `phy.c`:

1. `rtw8852a.c` installs `&rtw89_8852a_phy_radioa_table` in chip info at `.rf_table[RF_PATH_A]`.
2. `rtw89_phy_init_rf_reg()` selects the chip table or a firmware element replacement, allocates an RF H2C staging buffer, and iterates RF paths.
3. `rtw89_phy_init_reg()` scans table headlines to choose the best RFE/CV target for the current device, then walks entries after the headline area.
4. Branch/check entries update the loader's `target`, `is_matched`, and `target_found` state. Only data entries inside the matched conditional branch reach the RF writer.
5. `rtw89_phy_config_rf_reg()` writes matched RF entries with `rtw89_write_rf(rtwdev, RF_PATH_A, addr, 0xfffff, data)` and stores the same `(addr, data)` pair in the H2C RF register staging buffer for firmware.

Within this chunk, the repeated structure is:

- select a table row/sub-index using `{0x033, value}`;
- start conditionals such as `{0x80010000, 0}` and `{0x90010001, 0}`;
- consume `{0x40000000, 0}` check markers;
- write the branch-specific `0x03f` payload;
- close the conditional group with `{0xA0000000, 0}` / `{0xB0000000, 0}` around fallback/end handling.

## State And Persistence Behavior

The table itself is immutable `.rodata`. Runtime state changes are hardware and firmware-facing:

- RF path A hardware registers are programmed directly through `rtw89_write_rf()`.
- The same RF entries are packed into `struct rtw89_fw_h2c_rf_reg_info` via `rtw89_phy_cofig_rf_reg_store()` so firmware can receive the RF register sequence page by page.
- Conditional loader state is transient and derived from `rtwdev->efuse.rfe_type` and `rtwdev->hal.cv` for this chip path.
- No filesystem persistence, heap ownership, or long-lived software state is created by the table entries themselves.

## Dependencies And Integration Points

- Depends on `phy.h` encoding macros for headline/conditional interpretation.
- Depends on `core.h` declarations for `struct rtw89_reg2_def` and `struct rtw89_phy_table`.
- Integrated into RTL8852A chip setup through `rtw8852a.c` chip info fields `.rf_table`, `.bb_table`, `.nctl_table`, and related PHY initialization sequencing.
- Shares the common rtw89 RF table loader with other chips and with firmware-provided replacement tables from `rtwdev->fw.elm_info.rf_radio[path]`.
- Register semantics are hardware-specific Realtek RF knowledge; symbolic names are not present for these RF addresses in this generated table.

## Risks

- The assigned range begins and ends inside larger generated structures. Editing only this slice can break surrounding conditional groups, even if the local syntax remains valid.
- The branch/check encodings are positional and stateful. Adding, removing, or reordering `0x8/0x9/0xA/0xB/0x4...` control entries can silently load the wrong RF values for an RFE/CV variant.
- Register `0x03f` values are dense hardware calibration data. A single wrong constant can degrade RF performance, regulatory power behavior, sensitivity, or channel stability.
- The RF H2C staging buffer has page/size limits. Large table growth can hit the `RF parameters exceed size` warning or make `rtw89_phy_config_rf_reg_fw()` fail.
- Because this is path A only, path symmetry with `rtw89_8852a_phy_radiob_regs[]` matters; path A-only fixes may create path imbalance unless intentionally hardware-specific.

## Test Signals

- Build coverage: compile the rtw89 driver with RTL8852A enabled to catch syntax, array, and exported-table issues.
- Boot/probe logs: absence of `invalid PHY package`, `failed to load CR`, `RF parameters exceed size`, and `rf path 0 reg h2c config failed` warnings during device initialization.
- Hardware smoke tests: RTL8852A probe, firmware load, RF init, scan, association, and traffic on 2.4 GHz and 5 GHz bands.
- RF sanity signals: compare RSSI/sensitivity, per-chain behavior, throughput, thermal/TSSI stability, and regulatory TX power against a known-good driver build.
- Table integrity checks: ensure the full `rtw89_8852a_phy_radioa_regs[]` still has balanced conditional branch/end control entries around the edited area and that `rtw89_8852a_phy_radioa_table.n_regs` remains `ARRAY_SIZE(...)`.

### subset-b-004942: lines 15451-22867

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 15451-22867

## Scope

This chunk is a contiguous data-table slice inside the Realtek rtw89 RTL8852A PHY table source. It starts in the middle of `rtw89_8852a_phy_radioa_regs[]`, runs through the end of the RF path-A table, and continues into the opening portion of `rtw89_8852a_phy_radiob_regs[]`. It does not contain executable C control flow by itself; its behavior comes from the common rtw89 PHY table loader and RF register writer.

## Purpose

The table rows encode RTL8852A RF register initialization values for the two radio chains:

- Lines 15451-21599 are the later part of `rtw89_8852a_phy_radioa_regs[]`, completing the path-A RF programming sequence.
- Lines 21601-22867 begin `rtw89_8852a_phy_radiob_regs[]`, including its header/sentinel rows and early RF register value programming for path B.

The data is consumed during RF initialization so the chip-specific `rtw89_chip_info` can program both RF paths before higher-level channel, calibration, transmit power, and receive-gain logic operates.

## Important APIs, Types, and Data

- `struct rtw89_reg2_def` is the row type: two 32-bit fields, `addr` and `data`. The apparent simplicity is important: all conditional markers, delays, and RF register writes are encoded into these same two fields.
- `struct rtw89_phy_table` wraps a register array with `regs`, `n_regs`, `rf_path`, and an optional `config` callback.
- `rtw89_8852a_phy_radioa_regs[]` and `rtw89_8852a_phy_radiob_regs[]` are static arrays in this file. Later in the file they are exported through `rtw89_8852a_phy_radioa_table` with `rf_path = RF_PATH_A` and `rtw89_8852a_phy_radiob_table` with `rf_path = RF_PATH_B`.
- `rtw89_8852a.c` wires those wrappers into RTL8852A chip data as `.rf_table = { &rtw89_8852a_phy_radioa_table, &rtw89_8852a_phy_radiob_table }` and sets `.rf_base_addr = {0xc000, 0xd000}` for direct RF register access.
- `enum rtw89_rf_path` defines `RF_PATH_A = 0` and `RF_PATH_B = 1`, matching the table wrappers and the init loop.

Within the table data, repeated rows such as `0x80010000`, `0x90010001`, `0x90360002`, `0xA0000000`, `0xB0000000`, and early `0xF...` rows are not ordinary RF register numbers. They are table grammar entries interpreted by the PHY table loader as condition branches, target checks, or headline/config-selection metadata. Rows with small addresses such as `0x033`, `0x03F`, `0x0EF`, `0x087`, `0x002`, and `0x067` are the actual RF register writes selected by that table grammar.

## Control Flow and Loading Behavior

RF initialization is driven by `rtw89_phy_init_rf_reg()`. It allocates a firmware-H2C staging object, iterates `path` from `RF_PATH_A` up to `chip->rf_path_num`, selects either firmware-provided RF tables from `rtwdev->fw.elm_info.rf_radio[path]` or the compiled-in `chip->rf_table[path]`, then calls `rtw89_phy_init_reg()` with the selected table.

`rtw89_phy_init_reg()` applies common table handling before invoking the per-row config callback. It interprets condition rows through helper logic such as `get_phy_cond()` and `get_phy_target()`, tracks whether a branch is currently matched, and calls the config callback only for rows selected by the current target. That is why this chunk repeatedly pairs branch selector rows (`0x8...`, `0x9...`, `0xA...`, `0xB...`, and `0x4...` markers) with actual RF register writes.

For normal RF tables, the callback is `rtw89_phy_config_rf_reg()`. It treats addresses `0xfe` through `0xf9` as delay sentinels, otherwise writes the RF register with `rtw89_write_rf(rtwdev, rf_path, reg->addr, 0xfffff, reg->data)` and also stores the packed row into the firmware-H2C RF-register staging buffer. For v1-style RF tables the alternative `rtw89_phy_config_rf_reg_v1()` uses `RFREG_MASK`, but the RTL8852A wrapper does not override `.config`, so the default path is used.

After a path table has been replayed, `rtw89_phy_config_rf_reg_fw()` sends the staged RF register pages to firmware with `rtw89_fw_h2c_rf_reg()`. The result is a dual path behavior: the driver writes registers immediately during init, and firmware receives a copy of applicable RF rows for later low-power/offload use.

## State and Persistence

The arrays in this chunk are static constant data and carry no mutable state themselves. Runtime state is created by interpretation:

- Hardware RF registers for path A and path B are programmed through the chip's RF write operation and base-address mapping.
- `struct rtw89_fw_h2c_rf_reg_info` accumulates RF rows per path during initialization, then resets `curr_idx` after H2C transmission.
- The selected branch state in `rtw89_phy_init_reg()` is transient and rebuilt each time the table is replayed.
- Firmware element tables can override compiled-in tables through `rtwdev->fw.elm_info.rf_radio[path]`; when present, these static rows may not be used for that path.

Persistence is therefore hardware/firmware side effects, not in-driver persistent storage. A suspend/resume, power-cycle, or RF reinitialization path must replay the table or use firmware-held copies to restore equivalent RF state.

## Dependencies and Integration Points

This chunk depends on the rtw89 PHY table grammar and RF write abstractions:

- `core.h` provides `struct rtw89_reg2_def`, `struct rtw89_phy_table`, RF path enums, and chip-info table pointers.
- `phy.c` provides table conditional parsing, RF register config callbacks, immediate RF writes, delay handling, and firmware-H2C staging.
- `rtw8852a_table.h` exposes the final `rtw89_8852a_phy_radioa_table` and `rtw89_8852a_phy_radiob_table` symbols to the chip driver.
- `rtw8852a.c` binds the compiled tables to RTL8852A device bring-up through `rtw89_chip_info`.
- The RFK/calibration code later assumes these RF paths have been initialized before IQK/DPK/DACK/TSSI operations touch path-specific RF/BB registers.

## Risks and Edge Cases

- The chunk boundary is mid-table at both ends: line 15451 is not the start of path A, and line 22867 is not the end of path B. Any review or generated documentation must reconcile this with adjacent chunks before drawing whole-table conclusions.
- Because branch markers share the same `struct rtw89_reg2_def` shape as writes, accidental row deletion, insertion, reordering, or value corruption can silently change which RF settings apply to a package/RFE/cut/channel target.
- The path-A and path-B arrays are highly repetitive but not interchangeable. Copying values between paths can break chain-specific RF calibration, gain, or front-end routing.
- Firmware H2C staging has bounded page capacity; `rtw89_phy_cofig_rf_reg_store()` warns and drops rows if RF parameters exceed the configured page count. Large table edits should be checked against this limit.
- No source-level type safety distinguishes actual RF addresses from encoded condition/headline words, so validation depends on parser compatibility and hardware testing.
- Failures in RF writes usually surface indirectly as poor link performance, calibration errors, bad TX power, failed scans, or unstable association rather than as compile failures.

## Test Signals

Useful validation signals for changes touching this table include:

- Kernel build coverage for the rtw89 RTL8852A driver to catch syntax, array, and symbol errors.
- Boot/probe logs for absence of RF table parser warnings such as failed conditional loads, unsupported RF paths, RF H2C oversize warnings, or RF H2C config failures.
- Successful RTL8852A device probe with both RF paths initialized and no `unsupported rf path` or RF busy warnings from the PHY write path.
- Runtime Wi-Fi smoke tests on 2.4 GHz and 5 GHz: scan, associate, DHCP/IP traffic, throughput, and reconnect after suspend/resume.
- RF calibration logs or debug traces for IQK/DPK/DACK/TSSI completion on both paths.
- Regulatory/TX power sanity checks because RF init values interact with later `rtw89_8852a_dflt_parms` and transmit-power limit tables.

### subset-b-004943: lines 22868-30637

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 22868-30637

## Scope

This chunk is a middle slice of `rtw89_8852a_phy_radiob_regs[]`, the generated RF path-B register table for the Realtek RTL8852A rtw89 wireless driver. The slice starts inside a conditional body at line 22868 and ends inside another conditional body at line 30637, so it should be merged with adjacent chunk reports before drawing whole-table conclusions.

## Purpose

The visible lines provide static RF initialization values for path B. They are not executable logic by themselves; they are consumed as `struct rtw89_reg2_def { u32 addr; u32 data; }` entries by the common PHY table interpreter. At runtime, the driver selects the branch that matches the device package/RFE/CV information and writes the matching RF register/value rows to RF path B.

The repeated pattern in this range configures register groups such as `0x033`, `0x03e`, `0x03f`, `0x06d`, `0x06f`, `0x087`, `0x0a0`, and `0x0ef` under many conditional markers. The data values change gradually across cases, which indicates board-revision/RFE/channel-plan calibration constants rather than algorithmic behavior.

## Important APIs, Types, and Symbols

- `rtw89_8852a_phy_radiob_regs[]`: static path-B RF register array defined in this source file. This chunk is fully inside this array, whose definition begins at line 21601 and continues beyond the chunk.
- `struct rtw89_reg2_def`: the pair type for each table entry, with `addr` and `data` fields.
- `struct rtw89_phy_table`: wraps a register array, its length, RF path, and optional config callback.
- `rtw89_8852a_phy_radiob_table`: exported table wrapper later in the file; it points at `rtw89_8852a_phy_radiob_regs[]` and sets `.rf_path = RF_PATH_B`.
- `rtw8852a_chip_info.rf_table[RF_PATH_B]`: in `rtw8852a.c`, this integrates the path-B table into chip initialization.
- `rtw89_phy_init_rf_reg()`: iterates each RF path table during RF initialization, picks the config callback, and sends stored RF writes to firmware H2C after table replay.
- `rtw89_phy_init_reg()`: common table interpreter. It selects the matching headline from RFE/CV metadata, evaluates branch markers, and calls the RF config function for matched normal rows.
- `rtw89_phy_config_rf_reg()`: applies normal RF rows by calling `rtw89_write_rf(rtwdev, rf_path, reg->addr, 0xfffff, reg->data)` and stores rows for firmware replay. It also treats RF pseudo-registers `0xf9` through `0xfe` as delay markers.

## Control Flow

This chunk has no C functions or loops. Control flow is encoded in table addresses:

- Headline rows at the start of the full array use high nibble `0xf` and are selected by `rtw89_phy_sel_headline()` according to `rtwdev->efuse.rfe_type` and `rtwdev->hal.cv`.
- Branch rows use high-nibble condition codes from `phy.h`: `0x8` for if, `0x9` for elif, `0xa` for else, `0xb` for branch end, and `0x4` for check.
- Rows such as `{0x90010001, 0}` and `{0x40000000, 0}` therefore are not RF register writes. They steer `rtw89_phy_init_reg()` toward or away from subsequent normal RF rows.
- Normal rows in this range are small RF addresses, for example `{0x03F, 0x00003338}` or `{0x087, 0x0000042F}`. When the current branch is matched, these become RF writes to path B.
- `0xA0000000` and `0xB0000000` entries are visible else/end style delimiters that close or switch branch bodies.

The chunk repeatedly encodes branch bodies for target combinations such as `0x90010001`, `0x90250001`, `0x90360002`, and similar. A common local structure is: branch/check marker, one matched RF write, then another conditional marker. Because the chunk begins after a `0x90320001` branch/check pair and ends before its current branch group finishes, adjacent chunks define the full context.

## State and Persistence Behavior

The table is compile-time constant data stored in the kernel module image. It does not own mutable state and does not persist runtime values. Runtime effects are hardware state changes:

- Matched RF rows program RTL8852A path-B RF registers.
- `rtw89_phy_config_rf_reg()` mirrors applied RF rows into `struct rtw89_fw_h2c_rf_reg_info`, then `rtw89_phy_config_rf_reg_fw()` sends them to firmware in pages. That creates firmware-visible RF configuration state in addition to direct hardware writes.
- Conditional selection depends on runtime device metadata (`efuse.rfe_type`, `hal.cv`, and for newer chips optionally `hal.acv`, though RTL8852A uses CV in the visible flow).

Because this is initialization data, incorrect values persist until later reinitialization, RFK, channel changes, suspend/resume recovery, or module/device reset overwrites the hardware state.

## Dependencies and Integration Points

- Depends on `core.h` for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, RF path enums, and chip-info wiring.
- Depends on `phy.h` condition-marker macros such as `get_phy_cond()`, `get_phy_target()`, `get_phy_compare()`, and `PHY_COND_*`.
- Consumed by `phy.c` through `rtw89_phy_init_rf_reg()`, `rtw89_phy_init_reg()`, and RF write helpers.
- Integrated by `rtw8852a.c` through `rtw8852a_chip_info.rf_table = { &rtw89_8852a_phy_radioa_table, &rtw89_8852a_phy_radiob_table }`.
- Path-specific: these rows program `RF_PATH_B`; path A has a separate `rtw89_8852a_phy_radioa_regs[]` table earlier in the file.

## Risks and Edge Cases

- The table format is dense and branch-encoded. A single wrong high-nibble marker or missing `0x40000000` check row can silently apply a wrong calibration block or skip a required block.
- The visible range is mid-array, so edits here must preserve surrounding branch nesting from adjacent chunks. Misplaced `0xA0000000`/`0xB0000000` delimiters could affect all following cases.
- Values are hardware-specific calibration constants. Normal compiler tests cannot prove correctness; regressions may appear as weak RF performance, failed association, unstable throughput, thermal/TSSI drift, or regulatory transmit-power anomalies.
- Firmware H2C storage has bounded page capacity. Large RF tables are checked in `rtw89_phy_config_rf_reg_fw()`; unexpected table growth can trigger warnings or `-EINVAL`.
- Direct register writes and firmware replay must stay consistent. Rows skipped by `rtw89_phy_config_rf_reg_noio()` in no-I/O paths may still matter for later firmware behavior depending on address class.

## Test Signals

- Build coverage: compile the rtw89 RTL8852A driver and ensure this generated table still compiles with valid array syntax.
- Boot/probe logs: absence of `invalid PHY package`, `failed to load CR`, `RF parameters exceed size`, and `rf path ... reg h2c config failed` warnings during RTL8852A probe.
- Hardware validation: successful initialization of devices using RF path B, stable scan/association on 2.4 GHz and 5 GHz, and no path-B-only receive/transmit degradation.
- RF behavior: compare RSSI, throughput, EVM, TSSI/thermal tracking, and channel-switch behavior against a known-good table.
- Suspend/resume or reset recovery: verify RF path-B initialization is replayed correctly after power-state transitions.

## Unresolved Cross-Chunk References

- The chunk starts inside a conditional branch body; earlier lines define the active branch target and preceding RF writes.
- The chunk ends before the branch group around target `0x90320001`/`0x90260001` completes; later lines provide the rest of that case and the final end of `rtw89_8852a_phy_radiob_regs[]`.
- Whole-file exports, tx-power tables, and default RFE parameter wiring are outside this chunk and should be covered by later merge/reconciliation from all chunks.

### subset-b-004944: lines 30638-37904

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 30638-37904

## Scope

This chunk covers 7,267 lines in the middle of `rtw89_8852a_phy_radiob_regs[]`, the RTL8852A RF Path B initialization table. It is not executable control logic by itself; it is dense `struct rtw89_reg2_def` data consumed by the common rtw89 PHY table interpreter. The range begins mid-conditional block after an RF package/CV branch marker and ends at a branch-end marker after programming RF register `0x0EC`. The surrounding array starts at line 21601 and is exported later as `rtw89_8852a_phy_radiob_table` with `.rf_path = RF_PATH_B`.

The chunk is dominated by conditional RF register writes for register `0x03F`, with repeated selector writes to RF register `0x033`. The same table grammar also uses pseudo-addresses such as `0x80010000`, `0x90010001`, `0xA0000000`, `0xB0000000`, and `0x40000000` as branch markers, not hardware RF registers.

## Purpose

The data programs RTL8852A radio path B calibration or lookup values for many RF package and cut-version combinations. Most blocks select an index through RF register `0x033`, then write a package-specific value to RF register `0x03F`. This creates a per-index table in the RF block with different constants for RFE/CV variants such as `0x80010000`, `0x90010001`, `0x90250001`, `0x90330002`, and related branch targets.

The first major sequence in this chunk continues an index sweep from `0x033 = 0x3A` through `0x87`, where each index is followed by a full conditional fan-out over many RFE/CV targets. Around line 34259 the chunk switches RF register `0x0EE` from `0` to `0x4000`, then starts another indexed sequence from `0x033 = 0x00` through `0x8F`. Near the end, it performs smaller direct control writes: `0x0EE`, `0x0EF`, `0x03E`, `0x03F`, then a conditional fan-out for `0x0EC`.

## Important APIs, Types, and Data

The local data type is `struct rtw89_reg2_def`, defined as a simple pair of `u32 addr` and `u32 data`. The array is wrapped in `struct rtw89_phy_table`, which records the table pointer, entry count, RF path, and optional per-table config callback. For this table, `rtw89_8852a_phy_radiob_table` sets:

- `.regs = rtw89_8852a_phy_radiob_regs`
- `.n_regs = ARRAY_SIZE(rtw89_8852a_phy_radiob_regs)`
- `.rf_path = RF_PATH_B`

The conditional table grammar is defined by helpers in `phy.h`: `get_phy_cond()`, `get_phy_target()`, `get_phy_compare()`, `get_phy_cond_rfe()`, and `get_phy_cond_cv()`. High address nibbles encode control records:

- `0x8...` means `PHY_COND_BRANCH_IF`.
- `0x9...` means `PHY_COND_BRANCH_ELIF`.
- `0xA...` means `PHY_COND_BRANCH_ELSE`.
- `0xB...` means `PHY_COND_BRANCH_END`.
- `0x4...` means `PHY_COND_CHECK`.
- `0xF...` headline records exist earlier in the full table and select the active RFE/CV target before this chunk is interpreted.

Real RF register addresses visible in this chunk include `0x033`, `0x03F`, `0x0EE`, `0x0EF`, `0x03E`, `0x0EC`, `0x03C`, `0x03D`, and `0x02F`. The overwhelming write target is `0x03F`; `0x033` appears as the index selector for the repeated table programming.

## Control Flow

Runtime control starts outside this file. `rtw89_phy_init_rf_reg()` loops over RF paths, chooses `chip->rf_table[path]`, and for RTL8852A receives this array as `chip_info.rf_table[RF_PATH_B]`. The chip integration in `rtw8852a.c` installs `&rtw89_8852a_phy_radiob_table` alongside path A, BB, NCTL, and power tables.

`rtw89_phy_init_reg()` interprets the table. It first selects a headline based on `rtwdev->efuse.rfe_type` and `rtwdev->hal.cv`, then scans from the non-headline body. When it sees an `IF` or `ELIF` pseudo-entry, it records the branch target. The following `CHECK` pseudo-entry compares that branch target against the selected headline target. Only the matching branch calls the RF config callback for the subsequent real register entries. `ELSE` handles the fallback branch, and `END` resets branch state.

For matched RF entries, the default callback is `rtw89_phy_config_rf_reg()`. Delay pseudo-registers `0xfe` through `0xf9` are handled specially, but this chunk does not use those delay addresses. Normal entries call `rtw89_write_rf(rtwdev, RF_PATH_B, reg->addr, 0xfffff, reg->data)` and also store the entry into firmware H2C RF-reg staging data. Wake-on-wireless can reuse the same table through the no-I/O callback, which stores eligible RF entries for firmware instead of directly writing hardware.

The repeated block shape is:

1. Write `0x033` with the RF table index.
2. Enter an `IF`/`ELIF` chain for specific RFE/CV targets.
3. Use `0x40000000` as the condition check record.
4. Write one real RF value, most often to `0x03F`.
5. Close the chain with `0xA0000000`/`0xB0000000` fallback and end records.

## State and Persistence

There is no C-level mutable state declared in this chunk. Persistence is hardware state: each matched table entry writes RF Path B registers and the values remain active until later RF initialization, reset, firmware RF configuration, power management restore, or another RF calibration path changes them.

Selection state comes from device state outside the table: efuse RFE type and hardware cut version determine which branch is applied. The table also affects firmware-side persistence because normal RF config stores writes into `struct rtw89_fw_h2c_rf_reg_info`; after table parsing, `rtw89_phy_config_rf_reg_fw()` pages the accumulated RF configuration to firmware and clears the staging index.

Because the chunk begins and ends inside the larger `rtw89_8852a_phy_radiob_regs[]` array, branch correctness depends on the earlier headline records and adjacent chunks. This chunk includes complete repeated branch blocks for many indices, but the first visible line is already inside a block and the final visible line is an `END` marker for a block whose following entries continue after the chunk.

## Dependencies and Integration Points

Important dependencies are:

- `core.h` for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, `struct rtw89_chip_info`, and RF path constants.
- `phy.h` and `phy.c` for conditional table parsing, RF register write dispatch, firmware RF-reg staging, and PHY init entry points.
- `rtw8852a.c` for installing `rtw89_8852a_phy_radiob_table` in RTL8852A chip metadata.
- `rtw8852a_table.h` for exporting the table descriptor to the chip module.
- efuse and HAL state, especially `rtwdev->efuse.rfe_type`, `rtwdev->hal.cv`, and for newer chips ACV selection, though RTL8852A uses CV here.
- RF base address and RF write helpers selected by chip generation. `rtw89_phy_write_rf()` maps RF path B through `chip->rf_base_addr[RF_PATH_B]` when direct RF access is used.

The chunk is also integrated with low-power and firmware-offload flows. `wow.c` can call RF initialization in no-I/O mode, causing these table entries to be captured for firmware restore rather than written immediately.

## Risks

- The data is branch-sensitive. A malformed `IF`/`ELIF`/`CHECK`/`ELSE`/`END` sequence can silently skip required RF writes or apply fallback values to the wrong RFE/CV package.
- The chunk begins mid-block, so local review alone cannot prove the first visible branch group is balanced. It must be reconciled with the previous chunk.
- Most values are opaque vendor RF constants. Numeric edits are high risk because they may affect gain, calibration, linearity, sensitivity, coexistence, or regulatory transmit behavior without compiler-visible symptoms.
- Register `0x033` acts as an index selector before many `0x03F` writes. Dropping or moving a selector write would send later data to the wrong RF table slot.
- Conditional blocks repeat for many similar RFE/CV targets. Copy/paste drift in one target value can affect only a specific board package or cut version, making regressions hard to reproduce.
- Firmware H2C RF-reg staging has a bounded page capacity. Large RF tables depend on `rtw89_phy_config_rf_reg_fw()` accepting the total staged count; unexpected table growth can trigger the driver's "rf reg h2c total len" warning.
- RF writes are hardware-timing-sensitive. Even though this chunk has no explicit delay pseudo-registers, it is part of a larger initialization sequence that relies on ordering relative to earlier and later RF writes.

## Test and Validation Signals

Useful validation is hardware and log driven:

- Boot/probe an RTL8852A device and verify RF initialization completes without `invalid PHY package`, `failed to load CR`, `unsupported rf path`, or `rf path ... reg h2c config failed` messages.
- Test multiple boards or efuse configurations so different RFE/CV branches in this table are exercised, especially targets represented by `0x9001...`, `0x9025...`, `0x9032...`, and the fallback branch.
- Validate both RF paths after init. This chunk is path B only, so path A/path B asymmetry in RSSI, TX power, or EVM can indicate wrong Path B table programming.
- Run association, throughput, RSSI, and packet error tests across 2.4 GHz and 5 GHz channels after cold boot, suspend/resume, and WoW restore.
- Compare conducted TX power, receive sensitivity, and calibration results against known-good driver/table revisions. The table values do not expose semantic unit tests, so RF measurements are the strongest signal.
- Confirm no firmware H2C RF-reg staging overflow warnings occur when the full `rtw89_8852a_phy_radiob_regs[]` table is parsed.

## Chunk Boundary Notes

This is a partial oversized-file chunk. The final per-file research report must merge this with adjacent chunks for `rtw8852a_table.c`, including the start and end of `rtw89_8852a_phy_radiob_regs[]`, the exported table descriptors near the end of the file, and the following NCTL and transmit-power tables.

### subset-b-004945: lines 37905-45612

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 37905-45612

## Scope

This chunk covers the tail portion of `rtw89_8852a_phy_radiob_regs`, the full
`rtw89_8852a_phy_nctl_regs` table, the complete
`rtw89_8852a_txpwr_byrate` table, all 8852A thermal delta swing index arrays,
the complete `rtw89_8852a_txpwr_lmt_2g` table, and the opening entries of
`rtw89_8852a_txpwr_lmt_5g`. It is data-heavy chip-parameter code rather than
procedural C, but these constants directly drive RF/BB register programming and
transmit-power policy for RTL8852A.

## Purpose

The data in this range supplies RTL8852A-specific PHY/RF initialization and
power-control parameters to the generic rtw89 AX PHY code:

- The Radio-B register records finish configuring RF path B. The entries are
  `struct rtw89_reg2_def` address/data pairs consumed through
  `rtw89_8852a_phy_radiob_table`.
- The NCTL register table initializes the RF calibration control block after
  the generic AX NCTL preinit sequence has enabled IQK/DPK clocks, path resets,
  and the NCTL state machine.
- The by-rate table seeds `rtwdev->byr` with per-band, per-NSS, per-rate-section
  power values used when programming `R_AX_PWR_BY_RATE` and rate-offset control.
- The delta swing index arrays provide temperature compensation curves for 2 GHz
  and 5 GHz, path A and path B, positive and negative thermal deltas.
- The 2 GHz and beginning 5 GHz power-limit arrays encode regulatory and
  operating-mode limits indexed by bandwidth, transmit-chain count, rate
  section, beamforming state, regulatory domain, and channel index.

## Important APIs, Types, And Symbols

- `struct rtw89_reg2_def`: register initializer pair `{ addr, data }`. In this
  chunk it represents Radio-B RF writes and NCTL/baseband writes.
- `rtw89_8852a_phy_nctl_regs`: static NCTL table beginning at line 42246. It is
  later exported through `rtw89_8852a_phy_nctl_table`.
- `struct rtw89_txpwr_byrate_cfg`: compact by-rate power record with fields
  `band`, `nss`, `rs`, `shf`, `len`, and packed byte `data`.
- `rtw89_8852a_txpwr_byrate`: 24 compact entries that initialize CCK, OFDM, MCS,
  HEDCM, and offset sections for 2 GHz and 5 GHz.
- `struct rtw89_txpwr_track_cfg`: points to the thermal swing arrays defined in
  this chunk. The file later exposes them through `rtw89_8852a_trk_cfg`.
- `rtw89_8852a_txpwr_lmt_2g`: complete 2 GHz limit tensor:
  `[RTW89_2G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `rtw89_8852a_txpwr_lmt_5g`: 5 GHz limit tensor starts in this chunk and
  continues beyond the assigned line range.
- `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`,
  `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`,
  `RTW89_QATAR`, and `RTW89_UK`: regulatory-domain indexes used by the limit
  arrays.

## Control Flow And Data Flow

There are no functions defined in this chunk. Runtime control flow enters these
tables through chip descriptors and generic PHY helpers:

1. `rtw8852a_chip_info` points `.rf_table[RF_PATH_B]` to
   `rtw89_8852a_phy_radiob_table` and `.nctl_table` to
   `rtw89_8852a_phy_nctl_table`.
2. RF initialization calls `rtw89_phy_init_rf_reg()`, which selects each RF path
   table from firmware elements if present, otherwise from `chip->rf_table[]`.
   It passes each `struct rtw89_reg2_def` to `rtw89_phy_config_rf_reg()` or the
   table-specified config hook.
3. NCTL initialization calls `rtw89_phy_init_rf_nctl()`. For AX chips this first
   calls `rtw89_phy_preinit_rf_nctl_ax()`, which enables IQK/DPK related clocks,
   resets path state, writes `R_NCTL_CFG`, and polls NCTL register `0x8080` for
   readiness. It then loads `chip->nctl_table` with `rtw89_phy_config_bb_reg()`.
4. `rtw89_8852a_dflt_parms` later points `.byr_tbl` at the local by-rate table
   and `.rule_2ghz.lmt` / `.rule_5ghz.lmt` at the power-limit tensors.
5. The by-rate table is loaded by `rtw89_phy_load_txpwr_byrate()`, which expands
   packed bytes into `rtwdev->byr[band][bw]` slots using
   `rtw89_phy_raw_byr_seek()`.
6. Channel changes eventually use `rtw89_phy_set_txpwr_byrate_ax()` and
   `rtw89_phy_set_txpwr_limit_ax()` to read the expanded by-rate and limit data,
   pack four signed bytes into 32-bit MAC power registers, and write
   `R_AX_PWR_BY_RATE` / `R_AX_PWR_LMT` pages.

The RF table entries include many high-bit encoded addresses such as
`0x80010000`, `0x90010001` through `0x90360002`, `0xA0000000`, and
`0xB0000000`, interleaved with low RF addresses such as `0x03f`, `0x033`,
`0x0de`, `0x087`, and `0x06f`. These are not ordinary MMIO offsets. They are
condition or branch marker encodings interpreted by the PHY table loader through
`get_phy_cond()`, `get_phy_target()`, and related helpers before actual writes
are issued.

## State And Persistence Behavior

All data in this range is static `const` data compiled into the driver module.
It is not persisted to disk and is not mutated in place. Runtime state changes
occur when generic PHY code copies or applies these constants:

- RF and NCTL register entries are applied to hardware registers during device
  initialization and calibration setup.
- By-rate entries are expanded into the in-memory `rtwdev->byr` cache.
- Power-limit entries remain read-only tables and are queried dynamically when
  building MAC power-limit pages for a band, bandwidth, channel, NSS/NTX count,
  rate section, and regulatory domain.
- Thermal swing arrays remain read-only and are referenced through
  `rtw89_8852a_trk_cfg` by RF calibration or tracking code outside this chunk.

Firmware element support can override some built-in tables. `rtw89_phy_init_reg`
chooses firmware-supplied RF/NCTL tables when `rtwdev->fw.elm_info` has them,
otherwise falls back to the compiled chip tables researched here.

## Dependencies And Integration Points

- Depends on `rtw8852a_table.h` for exported table declarations and on `core.h`
  / `phy.h` for `struct rtw89_phy_table`, `struct rtw89_reg2_def`,
  `struct rtw89_txpwr_byrate_cfg`, `struct rtw89_txpwr_track_cfg`, and
  regulatory/array dimension constants.
- Integrated into `rtw8852a_chip_info` in `rtw8852a.c`, which binds these tables
  to RTL8852A chip operations.
- Integrated into the generic AX PHY implementation through `rtw89_phy_gen_ax`,
  especially `preinit_rf_nctl`, `set_txpwr_byrate`, and `set_txpwr_limit`.
- Power-limit reads combine this table data with regulatory state, SAR,
  optional antenna-gain offsets, and TPE constraints before values are written
  to hardware.
- The 2 GHz table uses both world defaults and explicit regional overrides.
  If a regional entry is zero, `rtw89_phy_read_txpwr_limit()` falls back to the
  `RTW89_WW` entry for the same index. Some values are `127`, which functions
  as an effectively open or sentinel-like high limit in this table family.

## Risks And Maintenance Notes

- The chunk begins mid-table. Lines 37905-42244 are only the tail of
  `rtw89_8852a_phy_radiob_regs`, so whole-file research must combine this with
  earlier chunks to understand the full Radio-B sequence and initial branch
  headline records.
- The chunk ends at the start of `rtw89_8852a_txpwr_lmt_5g`; the 5 GHz limit
  table is incomplete here and must be reconciled with following chunks.
- Register tables are opaque hardware recipes. Small transcription errors in
  address/data pairs can silently break RF path B, calibration, channel
  switching, or transmit power.
- The high-bit table markers must remain intact. Treating encoded control
  records as normal RF writes, or reordering them, would break conditional table
  selection by RFE type and chip cut version.
- The power-limit tensors rely on exact enum ordering and array dimensions.
  Changes to `RTW89_*_NUM`, regulatory-domain enum values, or rate-section
  indexes require coordinated table regeneration.
- Signed `s8` power values are later packed into 8-bit register fields. Values
  above normal power ranges, especially `127`, should be understood as table
  sentinel/high-limit behavior before changing them.
- By-rate `data` is little-endian byte-packed by repeated `data >>= 8` in
  `rtw89_phy_load_txpwr_byrate()`. Changing `shf`, `len`, or byte order changes
  the expanded rate map.

## Test Signals

Useful validation signals after edits to this chunk include:

- Driver load and probe for RTL8852A without `invalid PHY package` or
  `failed to load CR` warnings from `rtw89_phy_init_reg()`.
- No `failed to poll nctl block` error during NCTL preinit.
- Successful RF initialization for both paths, with no RF H2C config warnings
  from `rtw89_phy_init_rf_reg()`.
- Channel switching across 2 GHz and 5 GHz with `RTW89_DBG_TXPWR` traces showing
  by-rate and limit programming for expected channel and bandwidth values.
- Regulatory-domain checks that confirm explicit regional entries override
  `RTW89_WW` and zero entries fall back as expected.
- RF calibration and thermal tracking behavior across temperature changes,
  especially path A/B delta swing application for 2 GHz CCK/non-CCK and 5 GHz.
- Over-the-air sanity tests for TX power, throughput, association stability, and
  coexistence behavior after suspend/resume and channel changes.

### subset-b-004946: lines 45613-51011

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 45613-51011

## Scope

This chunk is the final 5,399-line slice of the Realtek rtw89 RTL8852A table file. It begins inside the 5 GHz transmit-power limit initializer and continues through the end of the file. The content is almost entirely immutable calibration/regulatory data plus the exported descriptor objects that make the earlier table arrays visible to the chip, PHY, RF calibration, and transmit-power setup paths.

The chunk covers:

- The tail and majority of `rtw89_8852a_txpwr_lmt_5g`.
- All of `rtw89_8852a_txpwr_lmt_ru_2g`.
- All of `rtw89_8852a_txpwr_lmt_ru_5g`.
- The exported `rtw89_phy_table`, `rtw89_txpwr_table`, `rtw89_txpwr_track_cfg`, and `rtw89_rfe_parms` descriptors for RTL8852A.

## Purpose

The table data supplies hard-coded per-band transmit-power ceilings for RTL8852A. The ordinary 5 GHz limit table constrains non-RU rate-section power by bandwidth, transmit-chain count, rate-section limit class, beamforming state, regulatory domain, and 5 GHz channel index. The RU tables constrain HE/OFDMA resource-unit power by RU size/class, transmit-chain count, regulatory domain, and channel index for 2.4 GHz and 5 GHz.

The exported descriptors at the end of the file bind these raw arrays into the rtw89 driver framework. `rtw89_8852a_dflt_parms` is the primary integration object: it points `rule_2ghz` and `rule_5ghz` at the static non-RU and RU limit tables and points `byr_tbl` at the by-rate table loader descriptor. The RTL8852A chip-info object in `rtw8852a.c` uses this object as `.dflt_parms`.

## Important APIs, Types, And Objects

The static data follows the pointer shapes defined in `core.h`:

- `struct rtw89_txpwr_rule_5ghz` expects `lmt` with dimensions `[RTW89_5G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]` and `lmt_ru` with dimensions `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `struct rtw89_txpwr_rule_2ghz` expects `lmt_ru` with dimensions `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `struct rtw89_rfe_parms` groups the by-rate table and the 2 GHz, 5 GHz, optional 6 GHz, differential antenna, and TX-shape rules selected for a device.
- `struct rtw89_phy_table` wraps a `struct rtw89_reg2_def` array plus a count and RF path.
- `struct rtw89_txpwr_table` wraps arbitrary table data plus a loader callback.
- `struct rtw89_txpwr_track_cfg` supplies temperature compensation delta-swing arrays to RF calibration code.

Objects visible in this chunk:

- `rtw89_8852a_txpwr_lmt_5g`: 5 GHz non-RU power limits. This chunk includes 2,288 explicit assignments from line 45613 through the closing brace at line 47901.
- `rtw89_8852a_txpwr_lmt_ru_2g`: 2.4 GHz RU power limits. It contains 1,093 explicit assignments between lines 47904 and 48998.
- `rtw89_8852a_txpwr_lmt_ru_5g`: 5 GHz RU power limits. It contains 1,951 explicit assignments between lines 49001 and 50953.
- `rtw89_8852a_phy_bb_table`, `rtw89_8852a_phy_radioa_table`, `rtw89_8852a_phy_radiob_table`, and `rtw89_8852a_phy_nctl_table`: wrappers for baseband, RF path A, RF path B, and NCTL register tables declared earlier in the file.
- `rtw89_8852a_byr_table`: static by-rate table descriptor with `.load = rtw89_phy_load_txpwr_byrate`.
- `rtw89_8852a_trk_cfg`: temperature tracking config that points to the delta-swing arrays declared earlier in this file.
- `rtw89_8852a_dflt_parms`: default RFE parameter bundle for RTL8852A, referencing the by-rate table and 2 GHz/5 GHz power limit arrays.

## Data Shape And Semantics

The limit tables use designated initializers, so unspecified entries default to zero in `.rodata`. In PHY lookup code, a zero regulatory-domain entry has special behavior: for ordinary and RU power limit lookups, the driver falls back to the `RTW89_WW` entry for the same channel index when the selected regulatory-domain value is zero. This makes zero an overloaded value: it can mean either an intentional zero only where lookup code treats zero literally or, in the main regulatory lookup path, "not populated; use worldwide fallback."

The value range visible in this chunk is 0 through 127. The value `127` appears frequently and is used as a permissive/sentinel-like maximum in many regulatory/channel cells, especially where a domain/channel combination should not further constrain power beyond other limits. Ordinary values are signed `s8` table cells in RF-power units later converted through chip-specific factors.

The chunk explicitly covers regulatory domains including `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, and `RTW89_UK`.

The 5 GHz non-RU table indexes include bandwidth, transmit-chain count, rate-section limit class, beamforming flag, regulatory domain, and a compact Realtek channel index. The chunk shows dense worldwide default entries first, followed by region-specific overrides. The 2 GHz RU table indexes 14 channel slots and includes dense worldwide defaults followed by regional overrides; channel index 13 commonly uses `127` for region-specific rows. The 5 GHz RU table mirrors the 5 GHz regulatory/channel override style using the smaller RU index shape.

## Control Flow And Integration

There is no executable control flow in this chunk beyond C initializers, but the runtime path is direct:

1. `rtw8852a.c` stores `&rtw89_8852a_dflt_parms` in the RTL8852A chip-info `.dflt_parms` field and uses the PHY table descriptors for BB, RF path A, RF path B, and NCTL setup.
2. `rtw89_core_setup_rfe_parms()` chooses an RFE parameter set from chip defaults or an RFE-specific config. For RTL8852A, `rfe_parms_conf` is `NULL`, so the default parameter object is selected unless firmware RFE data overrides it.
3. `rtw89_load_rfe_data_from_fw()` may replace pieces of the static `rtw89_rfe_parms` with firmware-provided by-rate or limit data when valid firmware tables exist. Otherwise these static tables remain authoritative.
4. `rtw89_load_txpwr_table()` calls the table's load callback. For `rtw89_8852a_byr_table`, `rtw89_phy_load_txpwr_byrate()` expands compact by-rate entries into `rtwdev->byr`.
5. Transmit-power limit readers in `phy.c` consult `rtwdev->rfe_parms`. For RU limits, `rtw89_phy_read_txpwr_limit_ru()` indexes `rule_2ghz.lmt_ru`, `rule_5ghz.lmt_ru`, or `rule_6ghz.lmt_ru`, applies regulatory fallback to `RTW89_WW`, applies optional antenna-gain differential limits, converts RF units to MAC units, then clamps against SAR and TPE constraints.
6. Fill helpers such as `rtw89_phy_fill_txpwr_limit_ru_*_ax()` repeatedly call the reader to populate hardware command structures for each bandwidth/RU arrangement.

The temperature tracking descriptor integrates separately with `rtw8852a_rfk.c`, where thermal tracking logic selects arrays from `rtw89_8852a_trk_cfg` by band, RF path, and subband.

## State And Persistence Behavior

The tables in this chunk are compile-time constants stored in the kernel image. They do not mutate at runtime, allocate memory, or persist state externally. Runtime state is created by consumers:

- `rtwdev->rfe_parms` stores the selected static or firmware-augmented parameter bundle.
- `rtwdev->byr` stores expanded by-rate offsets loaded from `rtw89_8852a_byr_table`.
- Regulatory state, SAR state, TPE constraints, current channel, and firmware feature flags are held elsewhere and determine how these constants are interpreted.

Because the data is static, any update requires rebuilding the driver. Firmware RFE data can override supported pieces at runtime, but the static tables remain fallback/default behavior.

## Dependencies

This chunk depends on dimension and enum constants from the rtw89 core/PHY headers, including `RTW89_5G_BW_NUM`, `RTW89_2G_CH_NUM`, `RTW89_5G_CH_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_RU_NUM`, and `RTW89_REGD_NUM`, plus regulatory enum values such as `RTW89_WW`, `RTW89_FCC`, and `RTW89_ETSI`.

It also depends on arrays declared earlier in the same file:

- `rtw89_8852a_phy_bb_regs`
- `rtw89_8852a_phy_radioa_regs`
- `rtw89_8852a_phy_radiob_regs`
- `rtw89_8852a_phy_nctl_regs`
- `rtw89_8852a_txpwr_byrate`
- `_txpwr_track_delta_swingidx_*`
- `rtw89_8852a_txpwr_lmt_2g`, which is referenced in `rtw89_8852a_dflt_parms` but is declared before this chunk

The exported declarations are in `rtw8852a_table.h`, and the chip-info consumer is in `rtw8852a.c`.

## Risks And Edge Cases

- Dimension/order mismatches are high risk. The arrays are positional and deeply nested; swapping bandwidth, NTX, rate-section, BF, regulatory, or channel dimensions can compile while producing wrong power limits at runtime.
- Zero values are semantically sensitive because PHY code treats zero regulatory entries as missing and falls back to `RTW89_WW`. An intended low limit encoded as zero may not behave as a strict zero limit in the main lookup path.
- `127` values likely represent a maximum/unlimited policy cell. Misplacing them can silently remove a regulatory cap for a domain/channel/RU combination.
- The chunk starts after the declaration of `rtw89_8852a_txpwr_lmt_5g`, so reviewers of this chunk alone must remember that the initializer shape is inherited from line 45571.
- RTL8852A advertises 2.4 GHz and 5 GHz support only in `rtw8852a.c`; 6 GHz rule fields in `rtw89_rfe_parms` remain unused/default for this chip. Accidentally wiring 6 GHz consumers to these defaults would be invalid.
- `support_ant_gain` is false for RTL8852A in the observed chip info, so differential antenna-gain rules are not populated here. If that feature were enabled later, default `rule_da_*` pointers would need valid data before `rtw89_can_apply_ant_gain()` could safely allow DA limit use.
- The final descriptors are external ABI-like symbols inside the driver. Renaming or making them static without updating `rtw8852a_table.h` and `rtw8852a.c` breaks chip registration or module linkage.

## Test And Validation Signals

Useful validation signals for this chunk are mostly build-time and hardware/regulatory behavior oriented:

- Compile with the rtw89 RTL8852A objects enabled to catch descriptor type mismatches, missing externs, and array-shape errors.
- Confirm `ARRAY_SIZE()` values in the final `rtw89_phy_table`/`rtw89_txpwr_table` descriptors match the intended source arrays.
- Exercise RTL8852A bring-up paths that load BB, RF A, RF B, NCTL, by-rate, and default RFE parameters.
- On hardware, test 2.4 GHz and 5 GHz association across representative channels and bandwidths, especially DFS/high-5 GHz channel indexes where the tables contain many region-specific overrides.
- Use rtw89 debugfs transmit-power views, where available, to inspect selected normal and RU power limits for multiple regulatory domains and verify fallback from domain-specific zero cells to `RTW89_WW`.
- Regulatory regression tests should compare effective limits for FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, and UK against vendor/regulatory reference data.
- RF thermal tracking tests should verify that `rtw89_8852a_trk_cfg` still maps path A/path B and 2 GHz/5 GHz arrays expected by `rtw8852a_rfk.c`.

## Cross-Chunk Notes

This chunk cannot fully describe the source file alone because many referenced arrays are declared earlier. The final merge lane should combine this report with earlier chunks covering the BB/RF/NCTL register arrays, by-rate table, delta-swing arrays, and the beginning of the 2 GHz and 5 GHz transmit-power limit tables.
