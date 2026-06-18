# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.c

## Purpose

`debug.c` provides the optional debug and observability surface for the Realtek `rtw88` wireless driver. Under `CONFIG_RTW88_DEBUGFS`, it builds a `debugfs` directory named `rtw88` below the wiphy debugfs root and exposes register dumps, arbitrary MAC/BB/RF reads and writes, firmware H2C injection, reserved-page FIFO dumps, security CAM dumps, PHY statistics, coexistence controls, EDCCA toggling, firmware crash triggering, fixed-rate control, and dynamic-mechanism capability masking. Under `CONFIG_RTW88_DEBUG`, it also implements the exported `rtw_dbg()` logging helper gated by the global debug mask.

## Important APIs, Types, and Functions

The central private type is `struct rtw_debugfs_priv`. Each debugfs file stores a back pointer to `struct rtw_dev`, optional read and write callbacks, and a small union of callback-specific state such as register address/length, RF path/address/mask, reserved-page offset/count, CAM entry index, or selected dynamic-mechanism capability bit.

`struct rtw_debugfs` is a per-device aggregate of these private objects. `rtw_debugfs_templ` initializes callback mappings for all exposed files, and `rtw_debugfs_init()` `kmemdup()`s the template into `rtwdev->debugfs` before registering files. `rtw_debugfs_deinit()` only frees that allocation; debugfs dentry lifetime is left to the surrounding wiphy/device teardown.

Notable debugfs file handlers include:

- `rtw_debugfs_get_read_reg()` and `rtw_debugfs_set_read_reg()` for staged 8/16/32-bit MMIO reads.
- `rtw_debugfs_set_write_reg()` for raw MMIO writes through `rtw_write8/16/32`.
- `rtw_debugfs_get_rf_read()`, `rtw_debugfs_set_rf_read()`, `rtw_debugfs_set_rf_write()`, and `rtw_debugfs_get_rf_dump()` for RF register access under `rtwdev->mutex`.
- `rtw_debugfs_set_h2c()` for manually sending an eight-byte firmware command via `rtw_fw_h2c_cmd_dbg()`.
- `rtw_debugfs_get_dump_cam()` for reading a selected security CAM entry through `RTW_SEC_CMD_REG`.
- `rtw_debugfs_get_rsvd_page()` and `rtw_debugfs_set_rsvd_page()` for dumping firmware reserved pages via `rtw_fw_dump_fifo()`.
- `rtw_debugfs_get_tx_pwr_tbl()` for reporting per-path/rate power table values and regulatory/offset/limit/SAR inputs.
- `rtw_debugfs_get_phy_info()` and exported `rtw_debugfs_get_simple_phy_info()` for link, throughput, rate, RSSI, EVM, SNR, CFO, and packet counter summaries.
- `rtw_debugfs_set_coex_enable()`, `rtw_debugfs_get_coex_info()`, `rtw_debugfs_set_edcca_enable()`, `rtw_debugfs_set_fw_crash()`, `rtw_debugfs_set_force_lowest_basic_rate()`, and `rtw_debugfs_set_dm_cap()` for mutable runtime debug controls.

## Control Flow

Open/read/write flow is intentionally small. Read-only and read-write files use `single_open()` with `rtw_debugfs_single_show()`, which dispatches to the stored `cb_read`. Read-write files receive writes through `rtw_debugfs_single_write()`, which unwraps the `seq_file` private pointer before dispatching to `cb_write`. Write-only files use `simple_open()` and `rtw_debugfs_common_write()`, where `filp->private_data` is already the callback state.

Initialization copies the static template, creates the top directory, and calls three registration groups. `rtw_debugfs_add_basic()` creates active control and summary nodes. `rtw_debugfs_add_sec0()` and `rtw_debugfs_add_sec1()` create fixed MAC and BB page dump nodes, with additional 8822C BB pages in section 1. The page dump callbacks iterate a 0x100-byte register window in 32-bit steps.

Most setters parse small user strings through `kstrto*()` or `rtw_debugfs_copy_from_user()` plus `sscanf()`, store state in the debugfs private union, and return the byte count on success. Stateful readbacks then use that stored state on subsequent reads. Several operations that touch RF, firmware command paths, coexistence state, restart state, or security CAMs take `rtwdev->mutex`; simple MAC/BB register dumping does not.

The firmware-crash control is a deliberate restart path. Writing true leaves deep LPS, sets `RTW_FLAG_RESTART_TRIGGERING`, writes `REG_HRCV_MSG`, and refuses to run while `RTW_FLAG_RESTARTING` is already set. Dynamic mechanism capability control interprets a positive number as enable and a negative number as disable by clearing or setting a bit in `dm_info->dm_flags`, then a read of `dm_cap` either dumps TXGAPK status or lists all capabilities.

## State and Persistence

Debugfs state persists in `rtwdev->debugfs` for the device lifetime. The per-file private union stores the latest input for staged reads, CAM selection, reserved-page ranges, and dynamic-mechanism status selection. Writes can persistently alter driver and hardware state: fixed rate is stored in `dm_info->fix_rate`; coexistence manual control is stored in `coex->manual_control`; EDCCA uses the global `rtw_edcca_enabled` and reapplies PHY adaptivity mode; lowest-basic-rate forcing changes `rtwdev->flags`; raw register/RF writes directly modify hardware; and firmware crash writes trigger recovery state.

The report-oriented reads sample live state rather than caching. The TX power table locks `hal->tx_power_mutex` while walking `hal->tx_pwr_tbl`, and PHY information reads from current `dm_info`, `hal`, `stats`, and ewma fields. Reserved-page dumps allocate a temporary buffer with `vzalloc()` and free it after formatting.

## Dependencies and Integration Points

This file depends on Linux debugfs, `seq_file`, user-copy helpers, Realtek register accessors from `hci.h`, firmware helpers from `fw.c`, security CAM helpers, coexistence display/control functions, PHY adaptivity, power-save exit helpers, regulatory helpers, and driver-wide structures from `main.h`. It is only compiled when the relevant config options are enabled, while `debug.h` provides no-op stubs for non-debug builds.

Debugfs operations intentionally bypass normal high-level policy in several places. The raw write nodes are maintenance tools and can modify any accessible MAC/BB/RF register. H2C injection bypasses typed command constructors in `fw.c`. Firmware crash injection integrates with the recovery path by setting restart flags and poking the firmware receive-message register.

## Risks

The largest risk is that writable debugfs nodes are powerful. Incorrect `write_reg`, `rf_write`, or `h2c` input can corrupt hardware state, violate sequencing assumptions, or trigger firmware behavior not expected by normal driver paths. Most parsers cap input to 32 bytes but otherwise trust numeric values, including register addresses and RF masks.

Some debugfs reads can be expensive or disruptive. Full RF dumps iterate every path and 0x100 RF addresses under the device mutex. Reserved-page dumping allocates `page_num * page_size` without a local upper bound beyond user input and firmware FIFO validation. Register dump nodes perform many direct MMIO reads without taking the device mutex.

Mutable diagnostic flags can affect normal operation. EDCCA toggling changes PHY adaptivity, fixed-rate control changes rate selection, force-lowest-basic-rate changes transmit policy, and coexistence manual control disables the normal coexistence mechanism. Tests that use these nodes must restore state afterward.

## Test Signals

Useful validation includes enabling `CONFIG_RTW88_DEBUGFS` and verifying that each debugfs file is created, readable/writable with valid input, and returns `-EINVAL` or `-EFAULT` on malformed input. Hardware tests should verify MAC/BB page dumps, RF read/write round trips under mutex, reserved-page dumps on chips with FIFO dump support, CAM dumping after key install, TX power table output across 2.4/5 GHz and bandwidth changes, and firmware crash recovery. `CONFIG_RTW88_DEBUG` builds should confirm `rtw_dbg()` emits only when `rtw_debug_mask` contains the requested mask.
