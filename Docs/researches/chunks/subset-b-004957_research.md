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
