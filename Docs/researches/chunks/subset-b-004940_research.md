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
