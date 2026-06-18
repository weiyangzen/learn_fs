# sources/distributed-fs/ceph-client/fs/btrfs/raid56.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/raid56.h` declares the Btrfs RAID5/6 parity interface and the shared `struct btrfs_raid_bio` layout used by `raid56.c` and scrub callers. It documents how a full stripe is represented across higher-layer bios, internally allocated pages, sector indexes, parity stripes, and page-size/block-size steps. The source was read as a complete 291-line file.

## Important APIs, Types, and Functions

The file defines `enum btrfs_rbio_ops` with `BTRFS_RBIO_WRITE`, `BTRFS_RBIO_READ_REBUILD`, and `BTRFS_RBIO_PARITY_SCRUB`. `struct btrfs_raid_bio` is the main state container: it holds the `btrfs_io_context`, hash/cache/workqueue links, bio list and lock, plug list, operation flags, stripe geometry (`nr_data`, `real_stripes`, `stripe_nsectors`, `sector_nsteps`), scrub parity index, refcount, pending I/O counter, data/error/uptodate/checksum bitmaps, and page/paddr arrays. `struct raid56_bio_trace_info` carries devid, offset, and stripe number for tracepoints.

Inline helpers `nr_data_stripes()` and `nr_bioc_data_stripes()` subtract parity stripes from a chunk map or IO context. `RAID5_P_STRIPE`, `RAID6_Q_STRIPE`, and `is_parity_stripe()` encode special parity markers. Public prototypes expose parity write, read recovery, scrub allocation/submission, scrub data caching, and stripe hash table allocation/free.

## Control Flow

This header has no executable control flow beyond trivial inline helpers. Its declarations define the entry points used by Btrfs bio mapping, scrub, mount initialization, and unmount cleanup to enter the implementation in `raid56.c`.

## State and Persistence Behavior

The header defines transient in-memory state rather than persistent on-disk structures. `struct btrfs_raid_bio` instances exist for one full-stripe operation and may be cached in memory after completion for future RMW optimization. No on-disk format fields are declared here, but the structure controls writes that update persistent data/parity sectors.

## Dependencies and Integration Points

Direct dependencies are Linux list/spinlock/bio/refcount/workqueue types and Btrfs `volumes.h` for chunk map and IO context definitions. Public functions integrate with the Btrfs volume mapping layer, async RMW workqueue setup, device scrub/replace code, and tracepoints that consume `raid56_bio_trace_info`.

## Risks and Edge Cases

The layout is shared with implementation code and scrub users, so field semantics are tightly coupled to locking and lifetime rules. The paddr model must distinguish invalid sectors from real physical addresses; geometry fields are small integer types and rely on RAID56 stripe limits. Public scrub helpers assume callers provide a mapped `bioc`, correct `dbitmap`, and stable data folios when using the cache-data optimization.

## Test Signals

Compile coverage should catch include-order and prototype drift. Functional signals come from the same RAID56 tests as `raid56.c`, especially scrub callers that allocate rbios and cache data folios. Tracepoint tests or build checks should verify `struct raid56_bio_trace_info` consumers remain compatible.
