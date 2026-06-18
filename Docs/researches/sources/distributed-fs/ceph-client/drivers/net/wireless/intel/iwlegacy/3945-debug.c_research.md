# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/3945-debug.c

## Purpose
Provides Intel 3945-specific debugfs read handlers for firmware/uCode statistics in the `iwlegacy` driver. It formats RX, TX, and general statistics snapshots, including current, accumulated, delta, and max-delta counters, for userspace debug inspection.

## Important APIs, Types, and Functions
The exported integration object is `const struct il_debugfs_ops il3945_debugfs_ops`, with `.rx_stats_read`, `.tx_stats_read`, and `.general_stats_read` assigned to the local handlers. Functions are `il3945_stats_flag`, `il3945_ucode_rx_stats_read`, `il3945_ucode_tx_stats_read`, and `il3945_ucode_general_stats_read`. They read fields from `struct il_priv` under the `_3945` member: `stats`, `accum_stats`, `delta_stats`, and `max_delta`.

## Control Flow
Each debugfs read handler obtains `struct il_priv` from `file->private_data`, returns `-EAGAIN` unless `il_is_alive(il)` is true, allocates a temporary zeroed text buffer sized from the relevant stats structs, formats the statistics flag header, appends rows with `scnprintf`, copies to userspace with `simple_read_from_buffer`, frees the buffer, and returns the read result. RX stats print OFDM, CCK, and general non-PHY counters. TX stats print transmit counters such as preamble, Bluetooth defer/kill, CTS/ACK timeouts, and ack counts. General stats print debug, sleep/slot, timestamp, and diversity counters.

## State and Persistence Behavior
This file does not mutate device state. It reports the latest statistics notification from uCode plus accumulated/delta/max snapshots maintained elsewhere in the iwlegacy 3945 code. Values in current snapshots are little-endian firmware fields converted with `le32_to_cpu`; accumulated/delta/max fields are treated as host-order cached counters.

## Dependencies and Integration Points
Depends on `common.h`, `3945.h`, debugfs file operations, `simple_read_from_buffer`, allocation, endian helpers, `il_is_alive`, and `IL_ERR`. The common iwlegacy debugfs setup consumes `il3945_debugfs_ops` to install chip-specific stats readers.

## Risks
The output buffer sizes are manually estimated; future struct growth or additional fields could truncate output silently through `scnprintf`. The handlers allocate on every read and can return `-ENOMEM`. They do not take an explicit stats lock, so output may reflect concurrently updated mixed snapshots unless the surrounding driver serializes stats updates. Returning `-EAGAIN` for non-alive hardware is expected but user tooling must handle it.

## Test Signals
Read each debugfs stats file while the device is alive, down, resetting, and under traffic; verify current/accum/delta/max formatting, endian conversion of current firmware stats, no buffer overflow/truncation warnings, allocation failure handling, repeated partial reads through `ppos`, and correct registration through common debugfs ops.
