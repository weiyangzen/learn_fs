# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/4965-debug.c

## Purpose

`4965-debug.c` provides the Intel 4965-specific debugfs read callbacks for firmware statistics. It does not collect counters itself; it formats the latest firmware statistics cached in `struct il_priv` into user-readable debugfs buffers. The exported integration point is `il4965_debugfs_ops`, which supplies `.rx_stats_read`, `.tx_stats_read`, and `.general_stats_read` for the iwlegacy debugfs layer.

This file is built around three firmware statistics views:

- RX PHY/non-PHY/HT counters from `il->_4965.stats.rx`.
- TX counters from `il->_4965.stats.tx`.
- General device, debug, diversity, temperature, and timestamp values from `il->_4965.stats.general.common`.

When `CONFIG_IWLEGACY_DEBUGFS` support in the wider driver tracks cumulative state, the same debugfs views also display accumulated totals, per-notification deltas, and maximum deltas from `il->_4965.accum_stats`, `il->_4965.delta_stats`, and `il->_4965.max_delta`.

## Important APIs, Types, And Functions

- `il4965_stats_flag(struct il_priv *il, char *buf, int bufsz)` decodes `il->_4965.stats.flag`, including clear-state, 2.4 GHz versus 5.2 GHz operating frequency, and TGj narrow-band status.
- `il4965_ucode_rx_stats_read()` is the debugfs file read path for RX statistics. It formats `struct stats_rx_phy` for OFDM and CCK, `struct stats_rx_non_phy` for general RX counters, and `struct stats_rx_ht_phy` for HT/OFDM aggregation counters.
- `il4965_ucode_tx_stats_read()` is the debugfs read path for `struct stats_tx`, including preamble/rx-detect, Bluetooth priority deferral/kill, timeout, ACK, collision, and aggregation scheduler counters.
- `il4965_ucode_general_stats_read()` formats `struct stats_general_common`, `struct stats_dbg`, and `struct stats_div`, including temperature, TTL timestamp, slot counters, diversity transmit/probe timing, and SOS/RX-enable counters.
- `il4965_debugfs_ops` is the externally consumed `struct il_debugfs_ops` instance used by `4965-mac.c` during PCI probe when debugfs is enabled.

The source relies on kernel helpers and driver-local structures from `common.h` and `4965.h`: `struct il_priv`, `struct il_notif_stats`, `struct stats_rx_phy`, `struct stats_rx_non_phy`, `struct stats_rx_ht_phy`, `struct stats_tx`, `struct stats_general_common`, `struct stats_dbg`, and `struct stats_div`.

## Control Flow

Each read callback follows the same pattern:

1. Read `struct il_priv *il` from `file->private_data`.
2. Refuse the operation with `-EAGAIN` if `il_is_alive(il)` is false. These files expose firmware state and require live firmware.
3. Allocate a temporary zeroed kernel buffer sized from the relevant stats structures plus formatting slack.
4. Select current, accumulated, delta, and maximum-delta views from the `_4965` substructure.
5. Append a stats flag header, a table header, and formatted rows with `scnprintf()`.
6. Return data to userspace with `simple_read_from_buffer()`, then free the temporary buffer.

The data flow is intentionally one-way: debugfs reads observe cached state and never send firmware commands, modify counters, or take ownership of the statistics. Current firmware-provided fields are little-endian and converted with `le32_to_cpu()`. Accumulated/delta/max fields are host-order `u32` values maintained elsewhere in the driver.

## State And Persistence Behavior

This file has no persistent storage of its own. Its only file-static state is the format strings `fmt_value`, `fmt_table`, and `fmt_header`. All observable state is stored in `il->_4965` and is refreshed by notification handling in `4965-mac.c`, especially `il4965_hdl_stats()` and `il4965_hdl_c_stats()`.

The debugfs output is a snapshot of the last statistics notification, not a synchronous query of the device. Comments in all three readers explicitly warn that displayed values may not reflect current firmware activity. The cumulative, delta, and max-delta columns depend on rollover-naive accumulation in the MAC file under `CONFIG_IWLEGACY_DEBUGFS`; if firmware counters wrap, the debugfs view may underreport or skip wrapped increments.

## Dependencies And Integration Points

- Depends on the firmware statistics layout and endian conventions declared in the iwlegacy headers.
- Depends on the driver liveness model through `il_is_alive()`.
- Uses memory allocation (`kzalloc`, `kfree`) and debug logging (`IL_ERR`) from the kernel/driver environment.
- Uses `simple_read_from_buffer()` to implement standard debugfs read semantics with `ppos`.
- Is attached to the rest of the driver by `il4965_debugfs_ops`; `4965-mac.c` assigns this to `il->debugfs_ops` during PCI probe under `CONFIG_IWLEGACY_DEBUGFS`, and the common debugfs registration code consumes it.

## Risks And Edge Cases

- Buffer sizing is heuristic: it multiplies structure sizes by constants and adds slack. `scnprintf()` prevents overflow, but insufficient sizing would silently truncate output.
- The read functions do not lock around the `_4965.stats` snapshot. Concurrent notification updates can produce internally mixed rows, especially between current and accumulated views.
- All current firmware stats need endian conversion; accumulated values do not. Mixing those conventions incorrectly in future edits would corrupt the printed tables.
- Allocation is per read. Very frequent debugfs polling adds allocation pressure, although this is debug-only behavior.
- If the device is not alive, users receive `-EAGAIN`; tools reading the debugfs files should tolerate transient failures during firmware load, restart, suspend, or RF-kill transitions.

## Test Signals

- With debugfs enabled and firmware alive, reading the RX, TX, and general stats files should return non-empty tables beginning with the decoded statistics flag.
- During firmware restart or interface-down states, reads should return `-EAGAIN` rather than stale-looking output.
- RX stats should include OFDM, CCK, GENERAL, and OFDM_HT sections with current/cumulative/delta/max columns.
- TX stats should include both base TX counters and `agg.*` counters.
- General stats should show temperature and TTL timestamp as single values and the rest as table rows.
- Static analysis should flag no unchecked buffer writes because all formatting uses `scnprintf()` with remaining length.
