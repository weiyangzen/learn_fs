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
