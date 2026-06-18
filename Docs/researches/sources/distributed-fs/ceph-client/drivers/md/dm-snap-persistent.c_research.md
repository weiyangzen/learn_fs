# sources/distributed-fs/ceph-client/drivers/md/dm-snap-persistent.c

## Purpose
Implements the persistent snapshot exception store. It records copy-on-write exceptions on the COW device so snapshots survive reboot and supports metadata removal during snapshot merge.

## Important APIs, Types, And Functions
On-disk structures are `struct disk_header` and `struct disk_exception`, both little-endian. `struct pstore` tracks metadata buffers, current metadata area, committed entries, `next_free`, pending commits, callback batching, dm-io client, and metadata workqueue. The registered store methods include `persistent_read_metadata()`, `persistent_prepare_exception()`, `persistent_commit_exception()`, `persistent_prepare_merge()`, `persistent_commit_merge()`, `persistent_drop_snapshot()`, `persistent_usage()`, and `persistent_status()`.

## Control Flow
Construction allocates `pstore`, initializes version/valid state, and creates a workqueue. Metadata read loads or initializes the header, sets chunk size, allocates buffers and callback array, then reads metadata areas with dm-bufio until an exception with `new_chunk == 0` terminates the list. COW allocation assigns `next_free`, skips metadata chunks, and increments pending count. Commit writes exceptions into the current area, batches callbacks, writes metadata with preflush/FUA/sync when safe, advances areas, and reports validity to waiting snapshot IO.

## State And Persistence
Persistent state lives on the COW device: header chunk followed by metadata areas separated from data chunks. A cleared valid flag makes a snapshot unrecoverable. `next_free` is exact for normal operation and conservative/status-only after merge handling.

## Dependencies And Integration Points
Depends on `dm-exception-store.h`, `dm_snap_cow()`, dm-io, dm-bufio, vmalloc/kv allocation, and the snapshot store registry. `dm-snap.c` consumes the method table.

## Risks
Metadata ordering, FUA writes, area zeroing, and valid-flag handling are correctness-critical. Chunk-size header overrides must reallocate buffers correctly. Out-of-order COW commits can leave holes, so metadata and status accounting must not assume dense allocation.

## Test Signals
Test persistent snapshot creation, reload after teardown, explicit/default chunk sizes, COW overflow with `PO`, corrupt or invalid headers, metadata IO failure, and snapshot-merge. Verify `dmsetup status` allocated/total/metadata sectors and valid/invalid behavior.
