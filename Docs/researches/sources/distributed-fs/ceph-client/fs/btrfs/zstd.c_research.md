# sources/distributed-fs/ceph-client/fs/btrfs/zstd.c

## Purpose

`zstd.c` implements the Btrfs zstd compression backend and its per-filesystem workspace manager. It supports zstd levels -15 through 15, caps the window log to a Btrfs-specific maximum, streams filemap data into compressed bios, decompresses bios and inline extents, and reclaims idle workspaces with an LRU timer while preserving forward progress.

## Important APIs, Types, And Functions

`zstd_get_btrfs_parameters()` obtains zstd parameters for a level and source size, then caps `windowLog` at `ZSTD_BTRFS_MAX_WINDOWLOG` so input remains bounded by `ZSTD_BTRFS_MAX_INPUT`.

`struct workspace` stores allocated zstd memory, workspace size, sector-sized output buffer, actual and requested level, last-used timestamp, idle/LRU list links, zstd input/output buffers, and parameters. `struct zstd_workspace_manager` owns the spinlock, global LRU, idle lists by clipped level, active bitmap, waitqueue, and reclaim timer. `clip_level()` maps zstd's user-facing level range into internal slots.

Workspace lifecycle APIs include `zstd_alloc_workspace_manager()`, `zstd_free_workspace_manager()`, `zstd_alloc_workspace()`, `zstd_free_workspace()`, `zstd_get_workspace()`, and `zstd_put_workspace()`. `zstd_calc_ws_mem_sizes()` precomputes monotonic memory bounds so a higher-level workspace can safely serve a lower level. `zstd_reclaim_timer_fn()` frees idle reclaimable workspaces after `ZSTD_BTRFS_RECLAIM_JIFFIES`.

`zstd_compress_bio()` streams folios from the inode mapping into a zstd compression stream, writes compressed output into Btrfs compressed folios, appends them to the bio, and fails with `-E2BIG` when output grows too large. `zstd_decompress_bio()` streams compressed bio folios through a dstream and copies decompressed output to destination pages via `btrfs_decompress_buf2page()`. `zstd_decompress()` handles direct single-extent decompression into a destination folio. `btrfs_zstd_compress` exposes the level range and default level 3.

## Control Flow And Integration

At filesystem initialization, Btrfs allocates a zstd workspace manager and tries to preallocate a max-level workspace. Compression calls `zstd_get_workspace()`, which first searches idle workspaces at the requested or higher clipped level, then allocates under NOFS context, and finally waits for the protected max-level workspace if allocation fails. Returned workspaces are put back on level idle lists and possibly the LRU.

Compression initializes a zstd cstream with Btrfs-capped parameters, maps input folios one at a time, compresses into a min-folio-sized output buffer, appends full folios to the bio, then calls `zstd_end_stream()` until the frame is complete and appends the final partial folio. Decompression initializes a dstream with the max input bound, iterates bio folios, refills input when exhausted, drains output into a sector-sized workspace buffer, and stops when the destination pages are satisfied or the frame ends.

## State And Persistence Behavior

Persistent data is the zstd frame produced into compressed extents by higher-level writeback. Workspace manager state is runtime-only and scoped to `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`. Idle workspaces may outlive individual IOs until reclaimed by the timer; active_map and idle lists control reuse. Error returns distinguish fallback-worthy expansion (`-E2BIG`) from IO failures or memory pressure.

## Dependencies

The file depends on Linux zstd, bitmap, bio, folio/page mapping, timers, waitqueues, spinlocks, slab/vmalloc allocation, and NOFS allocation control. Btrfs dependencies include `compression.h`, `btrfs_inode.h`, `fs.h`, `misc.h`, and `super.h`, plus helpers for compressed folio allocation, input length calculation, filemap folio lookup, and decompression copyout.

## Risks And Edge Cases

Workspace management is concurrency-sensitive: idle lists, LRU list, active bitmap, `req_level`, and waitqueue wakeups must remain consistent under `spin_lock_bh()`. The max-level workspace is protected to guarantee forward progress under allocation failure. Negative zstd levels are mapped to the level-1 workspace size slot; monotonic sizing must remain valid when zstd parameter behavior changes. Compression must unmap and put input folios on every exit path. Bio size accounting must reject output equal to or larger than input. Decompression must handle truncated input, frame-end conditions, and short output by returning `-EIO` and zero-filling in the direct path.

## Test Signals

Useful tests include reads and writes with `compress=zstd` at negative, default, and high levels; incompressible data fallback; concurrent compression to exercise workspace reuse/waiting/reclaim; forced allocation failures to verify max-workspace forward progress; corrupt or truncated compressed extents; subpage and large-folio configurations; direct inline decompression; and timer-driven idle workspace cleanup during unmount.
