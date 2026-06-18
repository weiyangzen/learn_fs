# sources/distributed-fs/ceph-client/fs/nfs/iostat.h

## Purpose
`iostat.h` defines the NFS client per-mount I/O statistics storage and fast-path update helpers. It provides cacheline-aligned per-CPU counters for byte and event statistics so common I/O paths can update mount statistics with low contention.

## Important APIs, Types, And Functions
`struct nfs_iostats` contains `bytes[__NFSIOS_BYTESMAX]` and `events[__NFSIOS_COUNTSMAX]`, aligned to a cacheline. `nfs_inc_server_stats()` increments an event counter on the current CPU for a `struct nfs_server`; `nfs_inc_stats()` derives the server from an inode. `nfs_add_server_stats()` and `nfs_add_stats()` add byte counts. `nfs_alloc_iostats()` is deliberately a macro around `alloc_percpu(struct nfs_iostats)` so allocations get distinct accounting tags. `nfs_free_iostats()` safely frees non-null per-CPU storage.

## Control Flow And Integration Points
The helpers are inlined into I/O and RPC completion paths such as `nfs3proc.c`, where `nfs3_async_handle_jukebox()` increments `NFSIOS_DELAY`. Superblock/server allocation code is expected to allocate the per-CPU structure, and stats reporting code folds per-CPU values when exposing mount statistics.

## State And Persistence Behavior
Counters persist for the lifetime of the mounted `nfs_server` object. Updates are per-CPU and not individually synchronized, trading exact instantaneous reads for low overhead on hot paths. State is memory-resident only and reset when the server object is destroyed.

## Dependencies
The header depends on Linux per-CPU allocation, cacheline alignment, `linux/nfs_iostat.h` counter enumerations, and the `NFS_SERVER(inode)` accessor.

## Risks And Edge Cases
Callers assume `server->io_stats` is allocated. Mis-sized counter enumerations or use after server teardown would corrupt memory. Because counters are per-CPU, readers must aggregate correctly and tolerate concurrent updates. The `long addend` byte helper should only be used with sane positive or intentional signed deltas.

## Test Signals
Mount statistics should change under reads, writes, readdir, commits, retries, and server delay cases. Build-time coverage should catch enum size mismatch. Runtime tests should include mount teardown under active I/O and stats reads while workloads run.
