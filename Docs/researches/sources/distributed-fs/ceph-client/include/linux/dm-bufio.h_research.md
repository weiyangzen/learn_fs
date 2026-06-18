<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-bufio.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-bufio.h

## Purpose
Declares Device Mapper's block-buffer cache API for metadata-like I/O on block devices.

## Important APIs, Types, And Functions
Opaque types are `struct dm_bufio_client` and `struct dm_buffer`. APIs create/destroy/reset clients, set sector offsets, read/get/new buffers, prefetch, release, mark dirty fully or partially, asynchronously or synchronously write dirty buffers, issue flush/discard, forget buffers, set minimum buffers, and query block/client metadata. `DM_BUFIO_CLIENT_NO_SLEEP` controls allocation behavior.

## Control Flow
A DM target creates a client for a block device and block size, then obtains buffer references through `read`, `get`, or `new`. Modified buffers are marked dirty, released, and later written by explicit flush/write calls or memory pressure. Prefetch starts background reads without waiting. Destroy tears down the cache after references and I/O are gone.

## State And Persistence
State includes cached blocks, dirty ranges, reference counts, auxiliary per-buffer data, reserved buffer accounting, and the sector offset mapping logical buffer numbers to device sectors. Dirty data persists only after writeback and optional device flush.

## Dependencies And Integration Points
Depends on block devices, DM low-level I/O, sectors, and callback hooks for buffer allocation and write completion. It is used by DM metadata-heavy targets.

## Risks And Edge Cases
Deadlock constraints are explicit: only one thread may hold up to the reserved buffer count, other threads may hold at most one buffer unless using `dm_bufio_get()`. Dirty buffers can be written before the explicit write-dirty call under memory pressure. Sector offset must not change while I/O is active. Forget calls are hints and ignore busy or dirty buffers.

## Test Signals
Tests should cover cache hits/misses, read/new/get semantics, dirty full and partial writes, async writeback, flush/discard propagation, minimum-buffer cleanup, sector offset mapping, memory pressure, and misuse patterns that would exceed reserved-buffer rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-bufio.h -->
