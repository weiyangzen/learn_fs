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
