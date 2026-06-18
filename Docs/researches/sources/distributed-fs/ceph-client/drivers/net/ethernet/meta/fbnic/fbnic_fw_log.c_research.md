# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw_log.c

## Purpose

`fbnic_fw_log.c` implements the driver's in-memory firmware log cache and log-stream enable/disable helpers. It allocates a fixed-size vmalloc buffer, stores variable-length firmware log entries in a circular layout, maintains a list of live entries, and asks firmware to start or stop sending logs. Debugfs and devlink health reporting consume or write this cache.

## Important APIs, Types, And Functions

Public functions are `fbnic_fw_log_init()`, `fbnic_fw_log_free()`, `fbnic_fw_log_enable()`, `fbnic_fw_log_disable()`, and `fbnic_fw_log_write()`. `fbnic_fw_log_enable()` checks readiness and suppresses historical-log requests for firmware older than `MIN_FW_VER_CODE_HIST`, then calls `fbnic_fw_xmit_send_logs()`. `fbnic_fw_log_disable()` sends a disable request and warns on unexpected errors. `fbnic_fw_log_write()` inserts a log entry with index, firmware timestamp, and message text.

## Control Flow

Initialization rejects double init, vmallocs `FBNIC_FW_LOG_SIZE`, initializes the spinlock/list, and records buffer start/end pointers. Free clears the list, zeroes size, releases the vmalloc region, and nulls pointers.

Write flow first checks `fbnic_fw_log_ready()`. Under `fw_log.lock`, it chooses the next entry address: buffer start for an empty list, otherwise 8-byte aligned after the current head entry. If the new entry would pass `data_end`, it wraps to `data_start`. It then walks the list from the tail backward and removes entries whose memory range overlaps the new entry. Finally it fills metadata, copies the string with `strscpy()`, and adds the entry at the list head.

## State And Persistence

State is `struct fbnic_fw_log` embedded in `struct fbnic_dev`: vmalloc data range, total size, entry list, and spinlock. Entries are stored inside the vmalloc buffer as `struct fbnic_fw_log_entry` plus flexible message bytes. Logs persist only in memory until driver unload, device removal, or explicit free.

## Dependencies And Integration Points

The file depends on vmalloc, spinlocks, firmware version gates, firmware send-logs TLV transmitters, and `fbnic_fw_log_ready()` from the header. It integrates with `fbnic_fw.c` log TLV parsing, `fbnic_debugfs.c` firmware log display, and `fbnic_devlink.c` health-report mirroring.

## Risks And Edge Cases

The circular allocator must remove every overlapped old entry before linking the new one. Very long messages are bounded by firmware/TLV max sizes but `msg_len` accounting includes the NUL and the code computes `entry_end = entry->msg + msg_len + 1`, so entry capacity assumptions should be audited if sizes change. Writes from unexpected firmware log messages before initialization return `-ENOSPC` and emit an error. Enablement intentionally disables historical replay on older firmware to avoid mailbox flooding from a known firmware bug.

## Test Signals

Useful tests include init/free idempotence, writing enough messages to wrap and evict old entries, debugfs newest-to-oldest output, enable requests with and without historical logs across firmware version thresholds, disable errors, and concurrent write/read lock behavior. No executable tests were run for this research item.
