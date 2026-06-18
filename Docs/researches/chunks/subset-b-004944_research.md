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
