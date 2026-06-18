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
