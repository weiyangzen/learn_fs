# sources/distributed-fs/openafs/src/afs/IRIX/osi_vnodeops.c

## Purpose
This SGI IRIX-specific file binds the portable OpenAFS cache manager to the IRIX vnode layer. It defines the AFS vnode operation vector, implements IRIX read/write paging integration, byte-lock handling, vnode inactive/reclaim behavior, vnode read/write serialization, MP wrapper entry points, and helpers used by XFS-backed cache code to derive inode/device/size metadata from vnodes.

## Important APIs, types, and functions
- `Afs_vnodeops` / `afs_lockedvnodeops` map IRIX VOP slots to OpenAFS operations such as `afs_open`, `afs_lookup`, `afs_fsync`, plus local wrappers `afs_xread`, `afs_xwrite`, `afs_xbmap`, `afs_strategy`, `afs_map`, `afs_xinactive`, `afs_rwlock`, and `afs_rwunlock`.
- `afs_frlock` delegates byte-range locks to IRIX `fs_frlock` but falls back to AFS whole-file lock handling through `afs_lockctl` for full-file locks and `F_GETLK`.
- `afs_xread` and `afs_xwrite` validate regular-file access, handle append offsets, take the vnode rwlock unless already locked, and call `afsrwvp`.
- `afsrwvp` is the main read/write engine. It verifies the vcache, flushes stale VM pages, coordinates chunk reads/writes, prefetch, dirty-state updates, NFS translator fake opens, and synchronous storeback.
- `afs_xbmap` builds IRIX `bmapval` mappings for the virtual AFS block/page cache.
- `afs_strategy` is the buffer strategy callback used by `chunkread`/`getchunk` to call portable `afs_read` or `afs_write` with saved credentials.
- `afs_map` handles memory mapping by verifying the vnode, flushing stale pages, and tracking mappings that may require store-on-last-reference.
- `afs_xinactive` performs last-reference cleanup, deferred unlink removal, dirty mmap storeback, credential release, and page tossing.
- `afs_rwlock`, `afs_rwunlock`, and `afs_rwlock_nowait` wrap the IRIX semaphore in per-vcache ownership/trip-count bookkeeping.
- `afs_fid2` supports IRIX checkpoint/restart or R5000 workaround behavior, depending on compile-time options.
- `VnodeToIno`, `VnodeToDev`, and `VnodeToSize` query backing vnode attributes for XFS cache support.

## Control flow and behavior
The VFS calls into the operation vector. Read/write VOPs enter `afs_xread`/`afs_xwrite`, obtain a per-vcache rwlock, and call `afsrwvp`. `afsrwvp` creates an AFS request, verifies cache status, invalidates stale pages, saves credentials for later asynchronous strategy calls, optionally fake-opens NFS-translator writes, marks write vnodes dirty, drops `AFS_GLOCK`, and loops over page-sized `bmapval` ranges. Reads build one or two mappings for normal read and read-ahead, call `chunkread`, optionally trigger `afs_PrefetchChunk`, copy buffer data into the caller `uio`, and release or asynchronously write delayed buffers. Writes use `getchunk` or `chunkread`, copy caller data into buffers, update cached length/time, schedule writes, and periodically call `afs_DoPartialWrite`. After the loop, the code reacquires `AFS_GLOCK`, drains partial writes, performs `afs_fsync` for sync writes when not an NFS translator request, and fake-closes any translator write.

`afs_strategy` is reached from IRIX buffer/page cache code. It guards against recursive dirty-buffer deadlocks, handles EOF reads by zeroing the buffer, skips delayed writes already being written to UFS, uses `avc->cred` for background calls, maps the buffer to a one-element `uio`, calls portable `afs_read`/`afs_write`, stores write errors in `avc->vc_error`, and completes the buffer with `iodone`.

Inactive handling first verifies that the vnode is really inactive, then tries to acquire AFS locks without blocking. It resolves unlinked files immediately or defers deletion with `CUnlinkedDel` if vcache/dcache locks are already held. Dirty or potentially writable mappings call `afs_StoreOnLastReference`; failures warn and invalidate segments. The final path clears saved credentials and tosses pages for link-count-zero vnodes.

## State and persistence
The file mutates vcache runtime state including `f.states` (`CDirty`, `CUnlinked`, `CUnlinkedDel`), `f.m.Length`, `f.m.Date`, `vc_error`, `lastr`, `cred`, `opens`, `execsOrWriters`, and `mapcnt`. Persistent file contents are written through AFS chunk/cache mechanisms and storeback routines, not directly here. Page and buffer cache state is aggressively flushed or written to avoid stale or recursive delayed-write conditions on IRIX. Saved credentials persist in the vcache until inactive cleanup.

## Dependencies and integration points
This code depends on IRIX vnode, buffer, semaphore, VM, lock, and XFS APIs; OpenAFS vcache/dcache/request/chunk/prefetch/storeback APIs; `afs_stats` tracing; and NFS translator globals such as `root_exported`. MP builds wrap almost every operation with `AFS_GLOCK` in `mp_afs_*` functions and install those wrappers in the externally visible `Afs_vnodeops`.

## Risks
Risk is concentrated in lock ordering between `AFS_GLOCK`, vnode rwlocks, vcache locks, IRIX buffer locks, and page-cache operations. `afs_strategy` depends on saved credentials and can be called asynchronously; missing credentials panic. Dirty mmap behavior is handled late at inactive time, so storeback failures can only warn and invalidate. The buffer recursion comments show known deadlock hazards around delayed-write AFS buffers and UFS/EFS cache writes. `afs_fid2` behavior changes by checkpoint/R5000 build options and can affect restart/export users. The implementation is tightly tied to obsolete IRIX kernel structures, so portability regression risk is high.

## Test signals
Useful signals include IRIX kernel module build coverage with MP and non-MP variants; vnode read/write tests across page boundaries, EOF, append, mmap dirty writeback, and sync writes; NFS translator read/write paths that exercise fake open/close and credential retention; byte-range and whole-file lock tests; unlink-while-open cleanup; induced cache write errors to verify `vc_error` and warning behavior; and XFS cache metadata helper tests for vnode attribute extraction.
