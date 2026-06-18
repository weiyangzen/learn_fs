# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c lines 1-8071

## Scope

This chunk covers the opening portion of the Realtek `rtw89` RTL8852B PHY table file. The assigned range contains the file header and includes, then four static `struct rtw89_reg2_def` register/data arrays:

- `rtw89_8852b_phy_bb_regs[]` at lines 9-1023, with 1,013 baseband register entries.
- `rtw89_8852b_phy_bb_reg_gain[]` at lines 1025-1092, with 66 software-parsed baseband gain entries.
- `rtw89_8852b_phy_radioa_regs[]` at lines 1094-7134, with the full 8,295-entry RF path A radio table.
- The start of `rtw89_8852b_phy_radiob_regs[]` from line 7136 through the chunk boundary at line 8071, with 1,207 entries from the RF path B table. This RF-B table continues after the assigned range.

The range is data-heavy rather than algorithmic. It contains register constants, RF table condition markers, and chip bring-up tables consumed by generic `rtw89` PHY initialization code.

## Purpose

The tables provide RTL8852B-specific PHY initialization data. During device bring-up, the driver loads the baseband table, parses the baseband gain table into software gain state, and loads RF radio tables for each RF path. The values establish baseband digital PHY behavior, receiver gain compensation, RF analog path defaults, internal RF lookup-table contents, and package/RFE/CV-specific RF settings before normal channel operation, calibration, and dynamic tracking begin.

The baseband table writes a broad set of PHY control registers, including common BB registers and mirrored path/register blocks such as `0x12xx`/`0x32xx`, `0x58xx`/`0x78xx`, and other PHY/AFE-related address ranges. The gain table is not a simple MMIO table; its encoded addresses are decoded by `rtw89_phy_config_bb_gain_ax()` into LNA/TIA gain error, replacement offset, bypass, and OP1dB state in `rtwdev->bb_gain.ax`.

The RF-A table is the largest complete object in this chunk. It starts with `0xf...` headline entries used to select the correct RFE/CV case, then programs path-A RF registers and many internal RF tables through repeated index/data patterns. The RF-B table begins with the same headline and early RF initialization shape for path B, but this chunk stops in the middle of a conditional/indexed RF programming sequence.

## Important APIs, Types, and Data

Key data type:

- `struct rtw89_reg2_def` stores one 32-bit address and one 32-bit data word. Every visible table row in this chunk is represented as `{ .addr, .data }`.

Key table objects, declared later in the same source file and exported by `rtw8852b_table.h`:

- `rtw89_8852b_phy_bb_table` wraps `rtw89_8852b_phy_bb_regs` with no custom config callback.
- `rtw89_8852b_phy_bb_gain_table` wraps `rtw89_8852b_phy_bb_reg_gain` with no custom callback in the table object; the chip PHY definition supplies `config_bb_gain`.
- `rtw89_8852b_phy_radioa_table` wraps `rtw89_8852b_phy_radioa_regs`, sets `rf_path = RF_PATH_A`, and uses `rtw89_phy_config_rf_reg_v1`.
- `rtw89_8852b_phy_radiob_table` wraps `rtw89_8852b_phy_radiob_regs`, sets `rf_path = RF_PATH_B`, and uses `rtw89_phy_config_rf_reg_v1`.

Important encoded values and patterns:

- `0xF...` entries at the start of RF-A and RF-B are headline entries. The generic loader treats top nibble `0xf` as valid headline metadata and selects one target case from current RFE type and chip version.
- `0x8...`, `0x9...`, `0xA0000000`, `0xB0000000`, and `0x40000000` entries are conditional-table control words, not normal RF register addresses. The parser maps them to IF/ELIF/ELSE/END/CHECK behavior using the high nibble.
- `0x033`/`0x03f` and `0x10033`/`0x1003f` dominate the RF data. These appear as index/data writes for RF-internal tables, with unprefixed addresses for one RF bank/page and `0x100xx` addresses for v1 extended RF addressing.
- `0x03e`, `0x03d`, `0x0ec`, `0x0ed`, `0x0ee`, and `0x0ef` are repeatedly used around indexed sequences, likely selecting banks, modes, pages, or intermediate RF table fields before payload writes.
- Delay pseudo-addresses `0xf9` through `0xfe` are supported by the generic BB/RF config callbacks. This chunk is mostly real register data and conditional/headline data, but the callbacks' delay handling is part of the contract for these arrays.

Within lines 1-8071 there are 10,581 `{addr, data}` entries. The most frequent address/control tokens are `0x40000000` condition checks, `0x03f`, `0x1003f`, `0x033`, the repeated `0x900...`/`0x800...` branch markers, and `0xA0000000`/`0xB0000000` ELSE/END markers.

## Control Flow

There are no local functions in the assigned range. Runtime control flow is supplied by the generic PHY table loader:

1. RTL8852B chip metadata in `rtw8852b.c` points `.bb_table`, `.bb_gain_table`, `.rf_table[RF_PATH_A]`, `.rf_table[RF_PATH_B]`, and `.nctl_table` at table objects from this file.
2. `rtw89_phy_init_bb_reg()` chooses firmware-provided BB elements if present, otherwise uses `chip->bb_table`. It calls `rtw89_phy_init_reg()` with `rtw89_phy_config_bb_reg()`, then loads `chip->bb_gain_table` through the chip's BB-gain config callback, then resets BB.
3. `rtw89_phy_init_rf_reg()` loops from `RF_PATH_A` to `chip->rf_path_num`, chooses firmware override RF tables if present, otherwise uses `chip->rf_table[path]`, and invokes `rtw89_phy_init_reg()` with either `rtw89_phy_config_rf_reg_v1`, the table's custom callback, the default RF callback, or a no-I/O RF collector.
4. `rtw89_phy_init_reg()` first scans any `0xf...` headline entries and selects the best target for current `efuse.rfe_type` and `hal.cv` or `hal.acv`.
5. After the headline area, each row is interpreted by the high-nibble condition field. Branch rows record a target, check rows compare it with the selected headline target, ELSE/END rows update the active branch state, and ordinary rows are passed to the selected config callback only when the branch is active.
6. BB rows are written with `rtw89_phy_write32()`, with PHY-1 address offsetting when DBCC loads a second PHY instance. RF rows in these RTL8852B tables use `rtw89_phy_config_rf_reg_v1()`, which writes the full `RFREG_MASK` to the selected RF path and stores extended-address rows into the RF H2C staging buffer for firmware.

The chunk boundary matters for control flow. Line 8071 falls inside `rtw89_8852b_phy_radiob_regs[]`, after a `0x90060001` conditional marker and its `0x03f` payload. The active conditional block continues in later lines, so this chunk is not a complete RF-B initialization table by itself.

## State and Persistence

The arrays in this chunk are static read-only kernel data. They do not mutate after build or module load.

Loading the BB table writes persistent hardware state into RTL8852B baseband registers. Those values remain until later PHY reconfiguration, channel changes, power transitions, firmware-driven updates, reset, or unload/reload changes them.

Loading the BB gain table persists decoded values in driver software state under `rtwdev->bb_gain.ax`, including per-band/per-path gain error, replacement offsets for channel widths/subchannels, bypass values, and OP1dB values. Later receive gain logic and PHY tracking depend on this software state.

Loading the RF tables writes persistent RF path state through `rtw89_write_rf()`. For v1 RF addresses below `0x100`, the callback only performs the direct RF write. For extended RF addresses at or above `0x100`, it also stores packed `(addr << 20) | data` words in `struct rtw89_fw_h2c_rf_reg_info`, which are sent to firmware after each path table load. Temporary parser state such as `is_matched`, `target_found`, `headline_idx`, and selected target exists only during `rtw89_phy_init_reg()`.

## Dependencies and Integration Points

Direct includes in this chunk:

- `phy.h` provides conditional-table macros, PHY init function declarations, and RF config callback declarations.
- `reg.h` provides register definitions used by surrounding RTL8852B PHY code.
- `rtw8852b_table.h` declares the exported table objects for the chip implementation.

Important external dependencies:

- `core.h` defines `struct rtw89_reg2_def`, `struct rtw89_phy_table`, `struct rtw89_chip_info`, RF path identifiers, and chip table pointers.
- `phy.c` implements `rtw89_phy_init_reg()`, `rtw89_phy_config_bb_reg()`, `rtw89_phy_config_bb_gain_ax()`, `rtw89_phy_config_rf_reg_v1()`, and RF H2C staging/sending.
- `rtw8852b.c` wires the tables into the RTL8852B chip descriptor, with RF base addresses `{0xe000, 0xf000}` and RF table order `{ radioa, radiob }`.
- Firmware element support can override BB, BB-gain, or RF radio tables through `rtwdev->fw.elm_info`; these static tables are the fallback/default tables.
- Efuse/HAL state supplies `rfe_type`, `cv`, and possibly `acv`, which controls which conditional RF/BB entries are applied.

The initialized state feeds later PHY functions: RFK/DPK calibration, channel setup, transmit power control, dynamic gain/tracking, EDCCA, BT coexistence-sensitive PHY settings, suspend/resume restore paths, and any firmware commands expecting RF tables to have been staged.

## Risks

- The tables are opaque hardware data. A one-word change can degrade RF performance without obvious compile-time or runtime errors.
- Conditional marker corruption is especially dangerous. Values such as `0x80010000`, `0x90020001`, `0x40000000`, `0xA0000000`, and `0xB0000000` are parser control words. Treating them as normal registers or altering their order changes which RFE/CV variants receive subsequent writes.
- RF-B is split by this chunk. Analysis or edits based only on lines 7136-8071 would miss the rest of the path-B initialization and could misinterpret an incomplete conditional sequence.
- RF path binding is outside the raw arrays. The raw RF-A and RF-B arrays look structurally similar, so correctness depends on the later `rtw89_phy_table` wrappers preserving `RF_PATH_A` and `RF_PATH_B`.
- `rtw89_phy_config_rf_reg_v1()` writes with `RFREG_MASK`; incorrect constants can replace full RF register contents.
- BB gain entries are software-decoded bitfields, not MMIO addresses. Invalid encoded addresses may be silently ignored for out-of-range gain band/path or may trigger warnings for unknown config types, leaving receive gain compensation incomplete.
- The loader's headline selection depends on accurate `efuse.rfe_type` and chip version. A board with missing or unexpected efuse data can fall back to less specific cases or hit `invalid PHY package` errors.
- Firmware override tables can replace these static tables. Debugging hardware behavior must confirm whether the static table or firmware element table was actually used.

## Test and Validation Signals

Static validation:

- Confirm the table objects at the end of `rtw8852b_table.c` still point to these arrays with the expected `ARRAY_SIZE()` and RF path values.
- Check that `rtw89_8852b_phy_bb_regs[]`, `rtw89_8852b_phy_bb_reg_gain[]`, and `rtw89_8852b_phy_radioa_regs[]` remain syntactically complete, and that `rtw89_8852b_phy_radiob_regs[]` remains complete in the later chunk.
- Check condition rows for balanced IF/ELIF/CHECK/ELSE/END patterns across the full table, especially across chunk boundaries.
- Build with the relevant `rtw89` configuration enabled; malformed initializers or missing declarations should fail compilation.

Runtime and hardware validation:

- Probe an RTL8852B device and verify BB/RF initialization completes without `invalid PHY package`, `failed to load CR`, BB gain warnings, or RF H2C config warnings.
- Test multiple RFE/CV combinations if boards are available, because this data is heavily conditional.
- Verify both RF paths: path-A performance after the complete RF-A table and path-B performance after the complete RF-B table should show sane RSSI balance, receive sensitivity, transmit power/EVM, and MIMO throughput.
- Exercise 2.4 GHz and 5 GHz association, channel changes, suspend/resume, and reset/reprobe flows to catch missing persistence or stale RF/BB state.
- Watch later RFK/DPK, TSSI, TX power, EDCCA, and PHY tracking logs; failures there often surface incorrect base RF/BB table contents.
