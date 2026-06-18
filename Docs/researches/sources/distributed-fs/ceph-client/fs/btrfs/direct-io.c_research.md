# sources/distributed-fs/ceph-client/fs/btrfs/direct-io.c

## Purpose

`direct-io.c` implements Btrfs direct read/write support through iomap. It maps file extents to bios, coordinates extent locks and DIO locks with ordered extents and page cache invalidation, creates ordered extents for direct writes, chooses between COW, NOCOW, prealloc, and buffered fallback, and completes direct I/O through Btrfs bio submission and ordered extent completion.

## Important APIs, Types, and Functions

Public APIs are `btrfs_direct_write()`, `btrfs_direct_read()`, `btrfs_init_dio()`, and `btrfs_destroy_dio()`. Core iomap callbacks are `btrfs_dio_iomap_begin()`, `btrfs_dio_iomap_end()`, and `btrfs_dio_submit_io()`, registered through `btrfs_dio_iomap_ops` and `btrfs_dio_ops`.

Important helpers include `lock_extent_direct()`, `btrfs_create_dio_extent()`, `btrfs_new_extent_direct()`, `btrfs_get_blocks_direct_write()`, `btrfs_dio_end_io()`, `btrfs_extract_ordered_extent()`, `check_direct_IO()`, and `check_direct_read()`. `struct btrfs_dio_data` tracks submitted bytes, data reservation changeset, current ordered extent, and COW/NOCOW reservation flags. `struct btrfs_dio_private` embeds a `btrfs_bio` with file offset and byte count.

## Control Flow

Direct reads and writes enter iomap after alignment checks. Reads reject fsverity and duplicate iovec base pointers, take a shared inode lock, disable page faults around iomap, and retry after faulting user pages when progress is possible. Writes choose a shared inode lock only for within-EOF no-security-bit cases, reject true direct writes for duplicated/RAID56 data profiles because user buffers can mutate while mirrors are written, reject DATASUM direct writes to avoid checksum/data divergence, and otherwise run iomap with fault retry. When direct write cannot proceed or only partially proceeds, it falls back to buffered write, flushes/waits the written range, and invalidates mapping pages.

`btrfs_dio_iomap_begin()` flushes async compressed pages if needed, optionally reserves data space before locking, locks DIO and extent ranges, rejects inline/compressed extents to buffered fallback, restricts NOWAIT requests to a single extent, and for writes calls `btrfs_get_blocks_direct_write()`. That helper tries prealloc/NODATACOW NOCOW first, reserves metadata, creates ordered extent state, or allocates a fresh extent for COW using previously reserved data space. It releases unused data reservations and staged outstanding extents after ordered extents take ownership.

`btrfs_dio_submit_io()` initializes a Btrfs bio, tracks submitted bytes, splits ordered extents for partial write bios when needed, and submits through `btrfs_submit_bbio()`. Completion logs errors, finishes ordered extents for writes, unlocks DIO extents for reads, restores the iomap private pointer, and calls `iomap_dio_bio_end_io()`. `btrfs_dio_iomap_end()` cancels unsubmitted tails by finishing ordered extents as failed or unlocking read ranges.

## State and Persistence Behavior

Persistent data changes happen through allocated or existing extents and ordered extent completion. For COW direct writes, `btrfs_new_extent_direct()` reserves an extent, creates an extent map and ordered extent, and later finish-ordered-io inserts file extent items and delayed refs. For NOCOW/prealloc writes, the ordered extent records writes into existing/preallocated disk space. Reads hold DIO locks until bio completion to keep extent state stable. The file owns the `btrfs_dio_bioset` lifecycle for private direct-I/O bios.

## Dependencies and Integration Points

Dependencies include iomap direct I/O, Btrfs extent maps, extent locking, ordered extents, delalloc space reservations, extent allocation, transactions/ordered completion, Btrfs bio/volume mapping, file write checks, inode locks, page cache writeback/invalidation, fsverity, and block profile selection. It integrates with buffered I/O fallback, qgroup/delalloc metadata accounting, COW/NOCOW extent logic, and Btrfs checksum policy.

## Risks and Edge Cases

Direct I/O is intentionally conservative. Inline and compressed extents fall back. NOWAIT refuses multi-extent ranges and blocking page/writeback conditions. Data checksummed inodes fall back because user buffers may change after checksum calculation. Duplicated and parity data profiles fall back for the same user-buffer mutability reason across mirrors. Lock ordering must avoid deadlocks with buffered writes, readahead, and mmap self-I/O; the code disables user faults and retries to avoid waiting on ordered extents it has not submitted yet. Reservation cleanup must handle partial extent allocation, ordered extent splitting, and submitted-byte shortfalls.

## Test Signals

Tests should cover aligned and unaligned direct reads/writes, NOWAIT success and `-EAGAIN`, inline/compressed fallback, fsverity read fallback, checksummed direct write fallback, RAID1/RAID56 buffered fallback, NODATACOW and prealloc direct writes, COW direct writes with ENOSPC/EDQUOT, mmap-to-self direct I/O deadlock avoidance, partial user fault retries, partial bio ordered-extent splitting, read holes/prealloc extents, page cache invalidation after buffered fallback, and bioset init/exit.
