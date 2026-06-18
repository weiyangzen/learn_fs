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
