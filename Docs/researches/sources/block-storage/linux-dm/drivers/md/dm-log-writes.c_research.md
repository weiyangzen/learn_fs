# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-writes.c

## Purpose

`dm-log-writes.c` implements the Device Mapper `log-writes` target. It passes I/O through to a backing device while sequentially recording completed writes, flushes, FUA writes, discards, metadata writes, and userspace marks to a separate log device. The target is intended for filesystem crash-consistency testing: replay the log up to a mark and inspect the reconstructed block-device state.

## Log Format And State

The log device starts with a `log_write_super` at sector 0 containing magic, version, entry count, and sector size. Each logged operation then consumes one sector of `log_write_entry` metadata followed by operation data when applicable. Mark entries store their string payload inline in the metadata sector; normal write data is copied into private pages and written after the entry. Discards log only metadata.

`struct log_writes_c` owns the pass-through device, log device, logical sector conversion state, next log sector, entry count, enabled flag, pending/log I/O counters, `unflushed_blocks`, `logging_blocks`, a waitqueue, a completion for superblock writes, and the logging kthread. `pending_block` snapshots a completed operation’s target sector, size, flags, optional mark/inline data, and copied bio vectors.

## Ordering Model

Normal completed writes go to `unflushed_blocks`. A completed flush splices previously unflushed writes ahead of the flush block into `logging_blocks`. FUA writes go straight to `logging_blocks`, and FUA or mark entries trigger a superblock update after the entry is logged. This models “what should have reached stable media” rather than raw submission order.

`log_writes_kthread()` serializes logging. It removes blocks from `logging_blocks`, reserves log sectors under `blocks_lock`, disables logging if the log device fills, increments `logged_entries`, submits metadata/data bios, and updates the log super for FUA/mark entries. `io_blocks` and `pending_blocks` allow destructor shutdown to wait until all submitted log bios and pending records drain.

## Mapping And End I/O

`log_writes_map()` ignores reads, zero-length non-flushes, and all I/O when logging has been disabled. For writes, it allocates a pending block before remapping the bio to the backing device. Non-discard write payloads are copied into fresh pages to avoid retaining caller-owned pages, including O_DIRECT pages. Discards allocate metadata-only records; if the backing queue lacks discard support, target limits advertise discard and the target completes the discard while still allowing logging behavior.

`normal_end_io()` attaches completed write records to the correct list: flushes splice their predecessor list into `logging_blocks`, FUA writes are logged immediately, and ordinary writes remain unflushed until a later flush or teardown.

## Control And Integration

The constructor syntax is `log-writes <dev_path> <log_dev_path>`. The target advertises one flush and one discard bio, per-bio private data, pass-through ioctls only when sizes match, and queue limits derived from the data device. The `mark <data>` message queues a `LOG_MARK_FLAG` entry with data truncated to fit one log sector. Teardown splices remaining unflushed blocks, appends `dm-log-writes-end`, waits for all logging, stops the kthread, and releases both devices.

When `CONFIG_FS_DAX` is enabled, DAX direct access and zero-page operations pass through to the backing device with page-offset adjustment.

## Invariants And Risks

- Log record order is based on completion and flush/FUA semantics, not submission order.
- Normal writes are durable in the log only after a later flush, FUA, mark, or teardown-driven drain.
- `logging_enabled` is turned off on log allocation/write errors or log-device exhaustion; status reports `logging_disabled`.
- Log-sector accounting uses target logical sector size and 512-byte bio sectors, so sector-size conversion is central.
- Error paths must balance `io_blocks` and `pending_blocks`; destructor waits on both.
- Superblock writes are serialized by waiting for `super_done`, preventing older super writes from racing newer entry counts.

## Test Focus

Test write/flush/FUA ordering, flush-with-data handling, discard with and without backing discard support, mark truncation and super update, log-device-full behavior, log write errors disabling logging, teardown drain with outstanding unflushed writes, DAX pass-through offsets, sector sizes larger than 512 bytes, and status output before/after logging disables.
