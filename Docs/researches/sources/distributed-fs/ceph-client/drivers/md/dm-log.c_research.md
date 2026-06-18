
# sources/distributed-fs/ceph-client/drivers/md/dm-log.c

## Purpose
Provides the dirty-region-log registry plus built-in `core` and `disk` dirty-log implementations used by dm mirror-style targets to track clean, dirty, syncing, and recovering regions. The `core` log is volatile; the `disk` log persists clean-region state on a log device.

## Important APIs, Types, And Functions
Registry APIs are `dm_dirty_log_type_register()`, `dm_dirty_log_type_unregister()`, `dm_dirty_log_create()`, and `dm_dirty_log_destroy()`. `get_type()` requests `dm-log-<type>` modules with suffix fallback. `struct log_c` stores region geometry, clean/sync/recovering bitsets, sync mode, dm-io request state, and disk-log header/device fields. Disk metadata uses `struct log_header_disk` with `MIRROR_MAGIC`, version, and region count. Constructors include `core_ctr()` and `disk_ctr()` via `create_log_context()`. Operations cover resume, flush, mark/clear, clean/in-sync queries, resync work, region sync updates, sync count, and status.

## Control Flow
Creation loads and references a log type, allocates context, validates region size, allocates bitsets, and optionally opens/initializes a log device and dm-io client. Disk resume reads the on-disk header, handles new/incompatible logs, adjusts region bits for grown/shrunk devices, copies clean bits to sync bits, and writes/flushed the updated header. Runtime mark clears clean bits; clear sets clean bits unless a previous flush failure made cleanliness unknowable. Resync scans zero sync bits while avoiding regions already marked recovering.

## State And Persistence
`core` state is entirely in memory and lost on reload. `disk` state persists header plus clean bitset in the log device starting after `LOG_OFFSET`; sync and recovering bitsets remain runtime. Flags `log_dev_failed`, `log_dev_flush_failed`, and `flush_failed` influence status and conservative behavior.

## Dependencies And Integration Points
Depends on dm dirty-log interfaces, dm-io, vmalloc bitsets, module loading, device-mapper table events, and mirror callbacks for flushing target data before marking regions clean on persistent logs.

## Risks
Region-size validation and bitset sizing must match target length. Disk flush failure forces all regions dirty because clean state cannot be trusted. Persistent header version is not backward-compatible except little-endian v1 promotion. Error paths must fail the log device and trigger table events. Bit operations use little-endian layout to preserve disk format.

## Test Signals
Test registry duplicate/unregister behavior, module autoload fallback names, core and disk constructors, invalid region sizes, sync/nosync modes, disk log read/write/flush failures, device grow/shrink handling, resync scanning and recovering bits, status for healthy/degraded/flush-failed logs, and mirror behavior after flush callback failure.
