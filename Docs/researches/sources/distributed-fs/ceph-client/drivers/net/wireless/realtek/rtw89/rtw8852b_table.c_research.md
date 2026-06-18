# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004949`: lines 1-8071, `Docs/researches/chunks/subset-b-004949_research.md`
- `subset-b-004950`: lines 8072-16047, `Docs/researches/chunks/subset-b-004950_research.md`
- `subset-b-004951`: lines 16048-22927, `Docs/researches/chunks/subset-b-004951_research.md`

## Chunk Research

### subset-b-004949: lines 1-8071

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

### subset-b-004950: lines 8072-16047

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c lines 8072-16047

## Scope

This chunk covers a large data-driven section of the RTL8852B rtw89 PHY table source. It starts in the middle of `rtw89_8852b_phy_radiob_regs[]`, includes the end of the RF path-B register script, the full `rtw89_8852b_phy_nctl_regs[]` NCTL script, the by-rate transmit-power table, thermal tracking delta-swing tables, transmit-shape limits, and the beginning of the 2.4 GHz regulatory transmit-power limit matrix.

The range is not standalone C logic. Its behavior comes from how rtw89 generic PHY and tx-power code interprets static arrays of `struct rtw89_reg2_def`, `struct rtw89_txpwr_byrate_cfg`, and multidimensional regulatory limit tables.

## Purpose

The tables in this chunk provide chip-specific calibration and policy constants for RTL8852B:

- RF path B initialization entries program radio registers for the second RF chain, including conditional branches keyed by RFE type and chip cut/version.
- NCTL entries initialize the baseband network-control/calibration engine around addresses `0x8000` through `0x8cb4`, finishing with control writes to `0x8080` and `0x8088`.
- By-rate transmit-power entries define packed per-rate power baselines for 2.4 GHz and 5 GHz across CCK/OFDM/MCS/HE-style rate sections and NSS combinations.
- Delta-swing tables define thermal compensation offsets for TSSI tracking by band, RF path, direction, subband, and CCK/OFDM distinction.
- Transmit-shape limit tables select regulatory shaping modes per band and regulatory domain.
- The 2.4 GHz power-limit matrix gives per-bandwidth, per-transmit-chain, per-rate-section, per-beamforming, per-regulatory-domain, per-channel limits used by runtime power queries.

## Important APIs, Types, and Data

- `struct rtw89_reg2_def` is a simple `{ addr, data }` pair. For normal BB/NCTL writes `addr` is a baseband register address. For RF tables, low register numbers are RF register addresses and high pseudo-addresses encode the rtw89 conditional table language.
- `rtw89_8852b_phy_radiob_regs[]` is declared earlier at line 7136 and ends in this chunk at line 13249. Lines 8072-13249 contribute about 5,177 register-table entries to RF path B.
- `rtw89_8852b_phy_nctl_regs[]` spans lines 13251-14572 and contains about 1,320 BB/NCTL register writes.
- `struct rtw89_txpwr_byrate_cfg` encodes `{ band, nss, rate-section, shift, len, data }`; each byte in `data` becomes one signed/unsigned raw by-rate power entry after `rtw89_phy_load_txpwr_byrate()` unpacks it.
- `rtw89_8852b_txpwr_byrate[]` has 24 entries. It covers band index `0` and `1`, multiple NSS/rate-section combinations, and packed values such as `0x50505050`, `0x484c5050`, `0x44484c50`, and `0x34383c40`.
- `_txpwr_track_delta_swingidx_*` arrays provide `DELTA_SWINGIDX_SIZE` thermal compensation tables. The 5 GHz tables are indexed by subband group and RF path flavor (`5ga`/`5gb`, positive/negative); the 2.4 GHz tables are flat path/rate-family tables for OFDM and CCK.
- `rtw89_8852b_tx_shape_lmt` and `rtw89_8852b_tx_shape_lmt_ru` set regulatory-domain shaping mode IDs. FCC, IC, and Mexico select nonzero shape IDs in several 2.4/5 GHz cases, while ETSI, MKK, KCC, ACMA, CN, Qatar, UK, Ukraine, and Chile are zero in this chunk.
- `rtw89_8852b_txpwr_lmt_2g` begins at line 14739. This chunk includes its worldwide defaults and early domain-specific assignments through `[0][0][2][0][RTW89_CN][10]` at line 16047, not the full array.

## Control Flow

At device initialization, `rtw8852b.c` installs these tables into `struct rtw89_chip_info`: `.rf_table[RF_PATH_B] = &rtw89_8852b_phy_radiob_table`, `.nctl_table = &rtw89_8852b_phy_nctl_table`, `.dflt_parms = &rtw89_8852b_dflt_parms`, and `.bb_table`/`.bb_gain_table` for earlier arrays outside this chunk.

RF initialization calls `rtw89_phy_init_rf_reg()`. It selects the compiled radio-B table unless firmware elements override it, then calls `rtw89_phy_init_reg()`. The generic table interpreter first chooses a headline branch based on RFE type and chip cut using `get_phy_headline()`, `get_phy_target()`, and `get_phy_compare()`. It then walks conditional opcodes in the `addr` high nibble: `0x8`/`0x9` branch-if/elif, `0xa` else, `0xb` end, and `0x4` check. Matched RF path-B entries are applied through `rtw89_phy_config_rf_reg_v1()`, which writes RF registers and stores larger-address entries for firmware H2C replay.

NCTL initialization calls `rtw89_phy_init_rf_nctl()`. Before consuming this table, the driver runs an NCTL preinit path that enables IQK/DPK clocks and polls `R_NCTL_CFG`/`0x8080`. It then applies `rtw89_8852b_phy_nctl_regs[]` through `rtw89_phy_config_bb_reg()`, so delay pseudo-registers and `BYPASS_CR_DATA` are handled generically while normal entries become baseband writes.

Transmit-power setup is indirect. `rtw89_8852b_dflt_parms` points `.byr_tbl` at `rtw89_8852b_byr_table`; that table's `.load` callback is `rtw89_phy_load_txpwr_byrate()`. The loader iterates each packed config, seeks the target by-rate slot via `rtw89_phy_raw_byr_seek()`, and writes one byte per rate index. Power-limit queries later read `rtw89_8852b_txpwr_lmt_2g` through `rtw89_phy_get_txpwr_limit()` and use regulatory fallback: if the selected regulatory domain entry is zero, the driver uses the `RTW89_WW` entry for that channel.

Thermal tracking uses `rtw89_8852b_trk_cfg`, which is declared later in the file and points at the delta-swing arrays in this chunk. Runtime TSSI code chooses the appropriate table by band/subband/path and expands the 30-entry delta-swing data into a 128-entry firmware compensation table around the programmed package thermal value.

## State and Persistence Behavior

All data here is compiled into the driver image as static `const` tables. The chunk does not allocate memory, mutate state, or persist anything to disk.

Runtime state changes happen only when other code consumes the tables:

- RF and NCTL table application writes hardware registers and may also stage RF entries into `struct rtw89_fw_h2c_rf_reg_info` so firmware can mirror RF settings.
- By-rate loading writes decoded values into `rtwdev->byr`.
- Regulatory limit tables remain read-only and are referenced through `struct rtw89_rfe_parms` in `rtw89_8852b_dflt_parms`.
- Thermal tracking tables remain read-only and are referenced through `rtw89_8852b_trk_cfg`; generated compensation data is placed into firmware H2C payloads at runtime.

## Dependencies and Integration Points

This chunk depends on:

- `phy.h` for conditional table macros, `struct rtw89_txpwr_byrate_cfg`, and `struct rtw89_txpwr_track_cfg`.
- `core.h` for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, `struct rtw89_rfe_parms`, and regulatory/power-limit array shapes.
- `phy.c` for `rtw89_phy_init_reg()`, `rtw89_phy_config_rf_reg_v1()`, `rtw89_phy_config_bb_reg()`, `rtw89_phy_load_txpwr_byrate()`, TSSI thermal-table expansion, and tx-power-limit query logic.
- `rtw8852b.c` for chip-info wiring that makes these tables active on RTL8852B.
- rtw89 regulatory code for mapping country/domain state to `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, `RTW89_UK`, and fallback `RTW89_WW`.

## Risks and Edge Cases

- The requested range starts inside `rtw89_8852b_phy_radiob_regs[]`, so any isolated review must remember that headline entries and earlier path-B setup are outside this chunk. Misreading the range as a complete table would miss branch-selection context.
- RF pseudo-addresses and real RF register addresses share the same `{ addr, data }` structure. A wrong conditional opcode, missing branch end, or malformed headline can make `rtw89_phy_init_reg()` skip or wrongly apply large sections of path-B initialization.
- `rtw89_phy_config_rf_reg_v1()` treats RF addresses below `0x100` differently from larger entries when staging firmware replay data. Changing table address conventions can affect both direct RF writes and firmware-side RF state.
- NCTL writes are order-sensitive. The tail writes to `0x8080`/`0x8088` are control-state transitions, not arbitrary constants; reordering them around the preinit poll or calibration data block can break RFK/NCTL readiness.
- By-rate entries pack four byte-sized values into one `u32`. Endianness of the unpacking is logical little-endian via shifting, so editing a hex literal changes rate indexes from low byte upward.
- Power-limit table values use zero as "no explicit domain limit, fall back to WW" in query code, while nonzero values are real quarter-dB-style RF-domain limits later converted to MAC units. The sentinel value `127` appears as an effectively disabled/not-applicable cap in parts of these regulatory matrices.
- This chunk ends mid-`rtw89_8852b_txpwr_lmt_2g`; later assignments may override or complete additional indices. Merge-level research should reconcile the full array before drawing complete regulatory conclusions.
- Regulatory data is compliance-sensitive. Off-by-one channel indexes, wrong regulatory-domain constants, or swapped NTX/rate-section dimensions can produce incorrect EIRP limits.

## Test Signals

Useful validation signals for this chunk include:

- Boot or module-load logs on RTL8852B with `RTW89_DBG_PHY_TRACK`, `RTW89_DBG_TXPWR`, and `RTW89_DBG_TSSI` enabled; look for invalid PHY package, NCTL poll failure, RF H2C config failure, unknown by-rate section, or unexpected tx-power warnings.
- RF bring-up checks that both RF paths initialize, especially path B, and that scan/association work on both antennas after `rtw89_phy_init_rf_reg()`.
- Calibration smoke tests covering IQK/DPK/TSSI after NCTL initialization; failures around `0x8080` readiness or RFK sequencing point back to the NCTL script.
- Tx-power unit tests or debugfs inspection comparing decoded by-rate values in `rtwdev->byr` against the packed `rtw89_8852b_txpwr_byrate[]` byte order.
- Regulatory tx-power tests on 2.4 GHz channels 1-14 across FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, UK, and WW fallback domains.
- Thermal chamber or simulated-thermal tests that verify positive/negative delta-swing index selection for 2.4 GHz CCK/OFDM and 5 GHz path A/path B subbands.

## Cross-Chunk Notes

Earlier chunks for this file contain the start of `rtw89_8852b_phy_radiob_regs[]`, the full BB and radio-A tables, and BB gain data. Later chunks contain the rest of `rtw89_8852b_txpwr_lmt_2g`, the 5 GHz limit matrices, RU-limit matrices, final `struct rtw89_phy_table` wrappers, `rtw89_8852b_trk_cfg`, and `rtw89_8852b_dflt_parms`. The final reconciled report should connect this chunk's data with those wrappers rather than treating the static arrays as independent exported APIs.

### subset-b-004951: lines 16048-22927

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c lines 16048-22927

## Scope

This chunk is the final 6,880-line tail of the RTL8852B rtw89 table source. It starts in the middle of `rtw89_8852b_txpwr_lmt_2g[]`, completes that 2.4 GHz regulatory transmit-power limit matrix, then defines the complete 5 GHz non-RU limit matrix, the complete 2.4 GHz and 5 GHz OFDMA RU limit matrices, and the exported descriptor objects that connect all earlier arrays in `rtw8852b_table.c` to the rest of the driver.

The range is almost entirely static `const` data. Its behavior is produced by generic rtw89 PHY, RF, firmware, and transmit-power code that dereferences these tables through `struct rtw89_chip_info` and `struct rtw89_rfe_parms`.

## Purpose

- Finish `rtw89_8852b_txpwr_lmt_2g`, the per-bandwidth/per-chain/per-rate/per-beamforming/per-regulatory-domain/per-channel 2.4 GHz power-limit table begun in the previous chunk.
- Define `rtw89_8852b_txpwr_lmt_5g`, the equivalent 5 GHz limit matrix for 20/40/80/160 MHz channel widths, 1TX/2TX, CCK/OFDM/MCS-style rate-section indexes where applicable, non-BF/BF modes, regulatory domains, and 53 channel indexes.
- Define `rtw89_8852b_txpwr_lmt_ru_2g` and `rtw89_8852b_txpwr_lmt_ru_5g`, the OFDMA resource-unit transmit-power caps used for RU26/RU52/RU106 and wider AX RU sections.
- Export `rtw89_phy_table` wrappers for the baseband, BB gain, RF path A, RF path B, and NCTL register scripts declared earlier in the file.
- Export `rtw89_8852b_trk_cfg`, which binds thermal tracking delta-swing tables declared in the previous chunk to RTL8852B RFK/TSSI code.
- Export `rtw89_8852b_dflt_parms`, the default RTL8852B RFE power-parameter bundle used when no firmware/ACPI RFE override is selected.

## Important APIs, Types, and Data

- `rtw89_8852b_txpwr_lmt_2g` has type `s8 [RTW89_2G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`. This chunk owns the table's tail from `[0][0][2][0][RTW89_QATAR][10]` through the closing brace at line 16926.
- `rtw89_8852b_txpwr_lmt_5g` spans lines 16928-19571 with shape `s8 [RTW89_5G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `rtw89_8852b_txpwr_lmt_ru_2g` spans lines 19573-20668 with shape `s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `rtw89_8852b_txpwr_lmt_ru_5g` spans lines 20670-22857 with shape `s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `RTW89_2G_BW_NUM` covers 20/40 MHz; `RTW89_5G_BW_NUM` covers 20/40/80/160 MHz; `RTW89_NTX_NUM` is 1TX/2TX; `RTW89_BF_NUM` is non-BF/BF; `RTW89_2G_CH_NUM` is 14 and `RTW89_5G_CH_NUM` is 53.
- Regulatory-domain indexes include `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, and `RTW89_UK`. Zero-initialized cells are meaningful because runtime code falls back from a selected domain to `RTW89_WW` when the selected cell is zero.
- The repeated `127` values are explicit high/sentinel caps used for unsupported or effectively unconstrained combinations. They differ from zero because zero triggers WW fallback in the generic readers.
- `rtw89_8852b_phy_bb_table`, `rtw89_8852b_phy_bb_gain_table`, `rtw89_8852b_phy_radioa_table`, `rtw89_8852b_phy_radiob_table`, and `rtw89_8852b_phy_nctl_table` are `struct rtw89_phy_table` descriptors. They point to register arrays defined earlier, set `n_regs` with `ARRAY_SIZE`, and assign `RF_PATH_A`/`RF_PATH_B` plus `rtw89_phy_config_rf_reg_v1` for RF tables.
- `rtw89_8852b_byr_table` is a file-local `struct rtw89_txpwr_table` wrapper around `rtw89_8852b_txpwr_byrate[]`; its loader is `rtw89_phy_load_txpwr_byrate`.
- `rtw89_8852b_trk_cfg` maps each thermal delta-swing member to the 2.4 GHz/5 GHz, path A/path B, positive/negative, and CCK/OFDM tables declared before this chunk.
- `rtw89_8852b_dflt_parms` is the exported `struct rtw89_rfe_parms` bundle. It points `.byr_tbl` at the by-rate wrapper, `.rule_2ghz`/`.rule_5ghz` at normal and RU limit matrices, and `.tx_shape` at shaping-limit tables from the previous chunk.

## Control Flow

There is no executable control flow in this chunk. Runtime paths are table-driven:

1. `rtw8852b.c` installs the exported PHY descriptors into `rtw8852b_chip_info`: `.bb_table`, `.bb_gain_table`, `.rf_table[RF_PATH_A]`, `.rf_table[RF_PATH_B]`, `.nctl_table`, and `.dflt_parms`.
2. Generic PHY initialization calls `rtw89_phy_init_bb_reg()`, `rtw89_phy_init_rf_reg()`, and `rtw89_phy_init_rf_nctl()`. Those functions choose these descriptors from chip info and pass their `regs`, `n_regs`, `rf_path`, and optional `.config` callback into `rtw89_phy_init_reg()`.
3. RF path A and B tables use `rtw89_phy_config_rf_reg_v1`; BB, BB gain, and NCTL use the generic BB register writer path. The register arrays themselves are outside this chunk, but this tail makes them externally visible through `rtw8852b_table.h`.
4. During transmit-power setup, rtw89 selects `rtwdev->rfe_parms` from chip defaults or firmware/ACPI overrides. For RTL8852B default operation, `rtw89_8852b_dflt_parms` supplies the by-rate, normal limit, RU limit, and shaping tables.
5. `rtw89_phy_load_txpwr_byrate()` decodes `rtw89_8852b_byr_table` into `rtwdev->byr`; later MAC/firmware power programming combines by-rate data with regulatory limits.
6. `rtw89_phy_read_txpwr_limit()` indexes the 2.4/5 GHz normal matrices by band, bandwidth, transmit chain count, rate section, beamforming state, regulatory domain, and channel index. If the selected regulatory value is zero, it retries the same tuple with `RTW89_WW`.
7. `rtw89_phy_read_txpwr_limit_ru()` does the same for RU limits, keyed by band, RU type, transmit chain count, regulatory domain, and channel index.
8. The limit readers convert RF-domain values to MAC-domain units with `rtw89_phy_txpwr_rf_to_mac()` and then clamp against SAR, TPE constraint, and optional antenna-gain/DA limits.
9. RTL8852B RFK/TSSI code reads `rtw89_8852b_trk_cfg` directly to select thermal compensation tables based on band, subband, RF path, and temperature direction.

## State and Persistence Behavior

All tables in this chunk are compile-time constants in the driver image. The chunk does not allocate memory, write files, mutate global state, or perform I/O.

State changes happen only in consumers:

- PHY/RF/NCTL descriptors cause hardware register writes when the generic init path consumes their earlier register arrays.
- The by-rate table is decoded into `rtwdev->byr`.
- `rtwdev->rfe_parms` points at `rtw89_8852b_dflt_parms` unless firmware elements or board-specific RFE configuration replace it.
- Normal and RU limit matrices remain read-only and are consulted whenever tx-power H2C payloads or limit structures are filled for the current channel.
- Thermal delta-swing arrays remain read-only; runtime RFK/TSSI code derives compensation offsets from them and sends/uses those derived values elsewhere.

## Dependencies and Integration Points

- `rtw8852b_table.h` declares the exported symbols defined at the end of this chunk.
- `rtw8852b.c` is the chip-info integration point that makes these tables active for RTL8852B devices.
- `core.h` defines `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, `struct rtw89_rfe_parms`, regulatory-domain enums, channel-count constants, bandwidth constants, and matrix shapes.
- `phy.h` and `phy.c` provide `rtw89_phy_config_rf_reg_v1`, `rtw89_phy_load_txpwr_byrate`, PHY register initialization, by-rate loading, normal tx-power limit reading, and RU tx-power limit reading.
- `fw.c` can load firmware-provided transmit-power/RFE data and can clone/override `struct rtw89_rfe_parms`; this matters because `rtw89_8852b_dflt_parms` is a default, not necessarily the only possible runtime source.
- `rtw8852b_rfk.c` consumes `rtw89_8852b_trk_cfg` for chip-specific thermal tracking.
- mac80211/cfg80211 regulatory state feeds `rtw89_regd_get()`, which selects the regulatory-domain dimension used to index these matrices.

## Risks and Edge Cases

- The requested range starts mid-`rtw89_8852b_txpwr_lmt_2g`; conclusions about the full 2.4 GHz matrix must include the previous chunk.
- Regulatory power data is compliance-sensitive. Swapping dimension order, channel indexes, NTX indexes, rate-section indexes, or regulatory-domain enum positions can produce illegal or overly restrictive transmit power.
- Zero and `127` are not interchangeable. Zero means "no explicit value here, fall back to WW"; `127` is an explicit table value and prevents fallback.
- 5 GHz channel indexes are not simple IEEE channel numbers. Runtime conversion uses `rtw89_channel_to_idx()`, so table edits must align with the driver's internal 53-entry channel index scheme.
- Wider bandwidth fill paths read multiple adjacent channel offsets, such as `ch +/- 2`, `+/- 4`, `+/- 6`, `+/- 8`, `+/- 10`, and `+/- 14`. Missing edge entries or incorrect center-channel assumptions can affect 40/80/160 MHz limit generation.
- RU limit tables are separate from normal MCS/OFDM limits. Keeping one updated while leaving the other stale can make OFDMA behavior diverge from non-OFDMA behavior on the same regulatory domain and channel.
- `rtw89_8852b_byr_table` is intentionally `static`; external code accesses it only through `rtw89_8852b_dflt_parms`. Removing or exporting it directly would change the table ownership model.
- The RF table wrappers depend on `.config = rtw89_phy_config_rf_reg_v1` for both radio paths. Accidentally omitting `.config` would route RF table entries through the default init behavior and break RF register programming semantics.
- `rtw89_8852b_dflt_parms` has no 6 GHz rules and no DA-specific rules populated. That is consistent with RTL8852B 2.4/5 GHz support, but consumers must continue to validate band support before indexing.

## Test Signals

- Build coverage for `rtw8852b_table.c` catches type/shape mismatches in the multidimensional initializers and exported descriptors.
- Module load or boot on RTL8852B should show successful BB/RF/NCTL initialization with no invalid PHY package, invalid RF table, or NCTL polling failures.
- Regulatory smoke tests should compare reported/programmed tx-power limits across 2.4 GHz channels 1-14 and representative 5 GHz channels for FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, UK, and WW fallback.
- 20/40/80/160 MHz 5 GHz channel tests should verify the multi-offset fill paths do not read unintended zero fallback or sentinel values.
- OFDMA validation should exercise RU26/RU52/RU106 limit generation in both 2.4 GHz and 5 GHz, especially domains/channels where normal and RU limits intentionally differ.
- Debug output around `RTW89_DBG_TXPWR` and tx-power H2C payloads can confirm that `rtw89_phy_read_txpwr_limit()` and `rtw89_phy_read_txpwr_limit_ru()` select expected domain values and fall back to `RTW89_WW` only when the selected cell is zero.
- Thermal or simulated-temperature tests should verify `rtw89_8852b_trk_cfg` still selects the expected positive/negative delta-swing table for path A/path B and 2.4/5 GHz operation.

## Cross-Chunk Notes

The previous chunk contains the by-rate table, thermal delta-swing arrays, transmit-shape tables, and the beginning of `rtw89_8852b_txpwr_lmt_2g`. This chunk finishes the power-limit data and publishes the descriptor objects that make the entire file usable by the RTL8852B driver. The later merge/reconciliation report should describe `rtw8852b_table.c` as one cohesive data provider rather than treating this tail's exported wrappers separately from the earlier static arrays they reference.
