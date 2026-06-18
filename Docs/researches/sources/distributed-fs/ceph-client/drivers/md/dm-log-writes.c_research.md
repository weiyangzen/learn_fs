
# sources/distributed-fs/ceph-client/drivers/md/dm-log-writes.c

## Purpose
Implements the `log-writes` device-mapper target, which forwards I/O to a data device while recording completed writes, flushes, FUA writes, discards, metadata writes, and user marks to a sequential log device. The log is intended for replay tools that validate filesystem consistency at chosen points.

## Important APIs, Types, And Functions
On-media structures are `struct log_write_super` and `struct log_write_entry`. `struct log_writes_c` tracks data/log devices, sector size, next log sector, entry count, pending/logging queues, inflight counters, logging state, and the logger kthread. `struct pending_block` holds copied write data or mark payloads. `log_writes_ctr()` opens devices and starts `log_writes_kthread()`. `log_writes_map()` copies write bio contents into private pages, records flush/FUA/discard flags, and maps the original bio to the data device. `normal_end_io()` moves completed writes to unflushed or logging queues. `log_one_block()`, `write_metadata()`, `write_inline_data()`, and `log_super()` write log entries. `log_writes_message()` supports `mark <data>`.

## Control Flow
Writes are logged after lower-device completion. Non-FUA writes enter `unflushed_blocks`; FUA and flush-associated writes enter `logging_blocks` immediately. A pure flush splices all unflushed blocks ahead of the flush marker so the log approximates durable order. The kthread drains `logging_blocks`, reserves space, writes metadata and data to the log device, updates the super on FUA/mark entries, and disables logging on log I/O errors or log-device exhaustion. Reads and uninteresting bios pass through.

## State And Persistence
Runtime state lives in queues, counters, and copied bio pages. Persistent state is a simple sequential log: sector 0 superblock with magic/version/entry count/sector size, followed by one-sector entries and optional data payloads. Log writes are append-only until the log device fills.

## Dependencies And Integration Points
Depends on device-mapper target hooks, block bio submission/completion, kthreads/freezer, DAX passthrough, queue-limit hints, target messages, and user-space replay tooling that understands the log format.

## Risks
The target must copy bio data before forwarding because original pages may disappear. Log space accounting must match metadata/data sector conversion. If log writes fail, logging is disabled while data I/O continues, so status must be monitored. Discards are logged by completion order and can be emulated if the data device lacks discard support. Superblock updates are synchronous via completion to avoid stale entry counts.

## Test Signals
Run write/flush/FUA/discard ordering tests, mark message tests, log replay validation, log-device-full behavior, log I/O error behavior, teardown with pending blocks, pure flush and flush-with-data cases, unsupported discard emulation, status output, ioctl forwarding size checks, DAX hook builds, and freezer/kthread stop handling.
