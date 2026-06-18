# Research: sources/distributed-fs/ceph-client/fs/ceph/file.c

## Purpose

`file.c` implements CephFS regular file operations and the file-open side of directory operations. It translates Linux VFS open/read/write/splice/llseek/fallocate/copy_file_range calls into Ceph MDS capability management and Ceph OSD object I/O. It chooses between page-cache buffered I/O, synchronous OSD I/O, direct I/O, async OSD requests, inline-data reads, encrypted read/write adjustment, async create, and remote object copy offload.

The file is central to CephFS consistency: it acquires and releases file capabilities, coordinates read/write/direct I/O locks, updates inode size and dirty caps, handles snapshot contexts, invalidates page cache/fscache around direct or remote changes, records client/subvolume metrics, and falls back to VFS helpers when Ceph-specific fast paths are not safe.

## Important APIs, Types, and Functions

- `ceph_record_subvolume_io()` records per-subvolume read/write operation metrics for successful non-zero I/O.
- `ceph_flags_sys2wire()` maps Linux open flags to Ceph wire flags.
- `iter_get_bvecs_alloc()`, `__iter_get_bvecs()`, and `put_bvecs()` pin iterator pages into `bio_vec` arrays for direct/asynchronous OSD I/O and release/dirty them afterward.
- `prepare_open_request()` allocates and initializes MDS OPEN/CREATE requests, including requested fmode and wire flags.
- `ceph_init_file_info()` and `ceph_init_file()` allocate per-open `ceph_file_info` or `ceph_dir_file_info`, acquire fmode refs, initialize read/write context tracking, handle no-page-cache sync mode, and uninline data before write opens.
- `ceph_renew_caps()` reacquires caps after session loss by sending an open request if local caps cannot satisfy wanted state.
- `ceph_open()` is the VFS open implementation. It handles fscrypt, access checks, snap read-only enforcement, fast open from existing caps, snapdir opens, and MDS OPEN fallback.
- Async create helpers `try_prep_async_create()`, `restore_deleg_ino()`, `wake_async_create_waiters()`, `ceph_async_create_cb()`, and `ceph_finish_async_create()` implement local create completion using delegated inode numbers, cached layouts, and directory create caps.
- `ceph_atomic_open()` combines lookup/create/open through MDS and optionally performs async create. It is registered from `dir.c`.
- `ceph_release()` frees per-file/per-directory private state, releases fmode refs, releases fscache cookies, and wakes cap waiters.
- `__ceph_sync_read()` and `ceph_sync_read()` perform blocking OSD reads, including sparse reads, encrypted extent decryption, EOF/hole zeroing, page-vector copyout, and retry signaling.
- `struct ceph_aio_request`, `struct ceph_aio_work`, `ceph_aio_complete_req()`, `ceph_aio_retry_work()`, and `ceph_aio_complete()` track asynchronous direct OSD requests and complete kiocbs.
- `ceph_direct_read_write()` handles direct read/write by building OSD requests from iterator-backed bvecs, with optional AIO and EOLDSNAPC retry.
- `ceph_sync_write()` performs blocking OSD writes, including fscrypt read-modify-write for partial crypto blocks and object-boundary splitting.
- `ceph_read_iter()`, `ceph_splice_read()`, and `ceph_write_iter()` are the main VFS read/write/splice entry points and perform cap acquisition, I/O mode selection, retries, and dirty-cap updates.
- `ceph_llseek()` refreshes size for SEEK_END/SEEK_DATA/SEEK_HOLE before delegating to generic llseek.
- `ceph_fallocate()`, `ceph_zero_pagecache_range()`, `ceph_zero_objects()`, and `ceph_zero_partial_object()` implement punch-hole support through page-cache invalidation/zeroing and OSD ZERO/TRUNCATE/DELETE operations.
- Copy offload helpers `get_rd_wr_caps()`, `is_file_size_ok()`, `ceph_alloc_copyfrom_request()`, `ceph_do_objects_copy()`, `__ceph_copy_file_range()`, and `ceph_copy_file_range()` implement object-aligned OSD copy-from2 and VFS fallback.
- `ceph_file_fops` registers regular file operations.

## Control Flow

### Open and Atomic Create

`ceph_open()` rejects duplicate opens, normalizes flags, runs fscrypt open checks for regular files, does a local MDS auth access check when it can build a path, rejects write opens on snapshots, and trivially initializes snapdir opens. If the inode already has usable caps, it touches fmode and initializes file private state without sending a synchronous open, possibly scheduling `ceph_check_caps()` to expand wanted caps. Otherwise it sends an MDS OPEN request and initializes private state from the returned fmode.

`ceph_atomic_open()` handles lookup/open/create from VFS. It strips `O_TRUNC` because VFS does truncation after permission checks, waits for conflicting async unlink, performs quota and fscrypt setup, allocates a new inode for create, builds an OPEN/CREATE request, and either:

- uses async create when `ASYNC_DIROPS`, directory create caps, cached layout, delegated inode number, and dentry lease/complete-dir conditions are satisfied; or
- sends a synchronous MDS request, finishes lookup/open/no-open depending on reply, caches the file layout after create, initializes ACLs, and calls `finish_open()`.

The async create path submits the MDS request but locally fills the new inode from synthesized MDS reply data, attaches it to the dentry, marks `FMODE_CREATED`, and opens the file. Completion later validates the MDS result, propagates errors, shuts down locally-created inodes on failure, releases directory caps, and wakes waiters.

### Read

`ceph_read_iter()` starts read/direct I/O exclusion, decides wanted cache/lazy caps, and calls `ceph_get_caps()` for `CEPH_CAP_FILE_RD`. If cache/lazy caps are unavailable, the file is direct, or the file is forced sync, it reads through OSD paths: direct unencrypted reads use `ceph_direct_read_write()`, otherwise `ceph_sync_read()`. Inline data triggers a getattr for inline data and copies from a temporary page. Buffered reads add a read/write context to the file and call `generic_file_read_iter()`.

`__ceph_sync_read()` flushes dirty page-cache data in range, splits reads by object mapping, adjusts encrypted reads to crypto block boundaries, uses sparse reads when needed, waits for OSD completion, updates metrics, decrypts encrypted extents, zero-fills short holes before EOF, copies pages to the iterator, updates `ki_pos`, and signals EOF/hole retry through `retry_op`.

`ceph_splice_read()` follows similar cap logic for pipe splicing. If page-cache caps are unavailable or inline/sync mode applies, it falls back to `copy_splice_read()`; otherwise it uses `filemap_splice_read()` under cap references and a read/write context.

### Write

`ceph_write_iter()` rejects shutdown and snapshot writes, preallocates a cap flush, starts direct or buffered write exclusion, handles append size refresh, runs generic write checks and size/quota/full-pool checks, removes file privileges, acquires `CEPH_CAP_FILE_WR` plus buffer/lazy caps where possible, updates file time and i_version, then chooses an I/O path.

If buffer/lazy caps are unavailable, direct I/O is requested, sync mode is set, or the inode is in write-error mode, it gets the current snap context and performs direct or synchronous OSD writes. Otherwise it uses `generic_perform_write()` into page cache. Successful writes mark FILE_WR caps dirty, may flush caps near quota limits, release cap refs, retry on `-EOLDSNAPC`, and call `generic_write_sync()` when required or near full.

`ceph_sync_write()` flushes overlapping page cache, invalidates fscache, loops by object boundary, adjusts encrypted writes to crypto block boundaries, performs read-modify-write for partial encrypted blocks with version assertion or exclusive create, encrypts pages, writes to OSD, retries RMW on version conflicts, invalidates local page cache range after successful OSD writes, and updates inode size/caps.

`ceph_direct_read_write()` builds bvec-backed OSD requests directly from the iterator. For writes it invalidates cache pages first and sets OSD write flags/mtime. It may queue multiple async OSD requests for non-sync kiocbs when the I/O is inside i_size or fits in one OSD request; completion updates size and dirty caps. Reads zero-fill holes and dirty user-backed pages when needed.

### Fallocate and Copy Offload

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE` on unencrypted regular head files. It acquires write caps, marks the file modified, locks page-cache invalidation, invalidates fscache, zeroes/truncates page-cache coverage, sends OSD ZERO/TRUNCATE/DELETE operations across affected objects, and marks FILE_WR caps dirty.

`ceph_copy_file_range()` first attempts `__ceph_copy_file_range()`. The offload path requires same cluster, writable head destination, copy-from enabled and supported, compatible non-striped layouts, unencrypted files, length at least one object, successful writeback of both ranges, source read caps and destination write caps, valid file sizes/quotas, matching object offsets, and page-cache invalidation on the destination. It manually splices initial/final partial-object ranges and uses OSD copy-from2 for full objects. Unsupported or cross-device cases fall back to `splice_copy_file_range()`.

## State and Persistence Behavior

This file coordinates multiple state layers:

- Per-open state in `ceph_file_info` / `ceph_dir_file_info`: fmode refs, sync flags, read/write contexts, generation, and directory readdir state.
- Per-inode cap state in `ceph_inode_info`: file modes, issued/wanted caps, dirty caps, snap contexts, layout, inline-data state, size, write-error state, async-create flags, and cached layout.
- Page cache and fscache state: flushed before sync reads/writes, invalidated before/after direct writes, punch-hole, and remote copy.
- Ceph cluster persistence: metadata/open/create state goes through MDS requests; file data, zeroing, and copy offload go through OSD requests.
- Metrics: latency/size counters and subvolume metrics are updated for OSD reads, writes, and copy-from operations.

Write persistence is split: data writes complete through OSD requests or page-cache writeback; metadata such as size/mtime is represented by dirty caps and later flushed to the MDS. Snap contexts are captured for writes so OSD writes land in the correct snapshot epoch, and `-EOLDSNAPC` causes retry after dropping caps and allowing pending capsnap state to settle.

## Dependencies and Integration Points

- VFS file operations call `ceph_file_fops`; directory operation tables in `dir.c` call `ceph_open()`, `ceph_release()`, and `ceph_atomic_open()`.
- MDS client integration covers OPEN, CREATE, cap renewal, access checks, async create callbacks, cap flush allocation, and cap dirtying.
- OSD client integration covers read/write/sparse-read/zero/delete/truncate/copy-from requests, request allocation, callbacks, object layout mapping, snap contexts, object versions, and OSD map full/nearfull flags.
- Netfs/fscache integration uses `ceph_fscache_use_cookie()`, `ceph_fscache_unuse_cookie()`, and `ceph_fscache_invalidate()`.
- Fscrypt integration adjusts offsets/lengths, decrypts sparse extents, encrypts write pages, and requires RMW for partial crypto blocks.
- Linux generic helpers provide buffered read/write, splice, direct I/O accounting, page-cache invalidation, write checks, file time updates, llseek, and copy fallback.
- Quota helpers reject max-file/max-byte violations before sending work likely to fail.
- `metric.h` and `subvolume_metrics.h` collect client and subvolume I/O statistics.

## Risks and Edge Cases

- Capability selection determines consistency. Taking the buffered path without cache/buffer caps would violate coherency, while unnecessary sync/direct fallback hurts performance.
- Async create relies on delegated inode numbers, cached layouts, and directory caps. Failures must shut down speculative inodes and wake waiters; `-EJUKEBOX` must restore delegated inode numbers and retry synchronously.
- Encrypted writes that do not align to crypto blocks require RMW with object version assertions. Races can force retry, and sparse extent validation failures return `-EIO`.
- Short OSD reads may represent holes rather than EOF; both sync and direct paths zero-fill holes and sometimes getattr/retry to distinguish EOF from stale size.
- Direct/AIO requests pin user pages; completion must dirty read pages when appropriate, put all pages, drop cap refs, call `inode_dio_end()`, and complete the kiocb exactly once.
- `ceph_write_iter()` returns `written ? written : err`, so partial success masks later errors in the standard Linux style.
- Hole punching is unsupported for encrypted files and only supports one fallocate mode.
- Remote copy offload is safe only for compatible object-aligned layouts and unencrypted files. It intentionally falls back to splice copy for unsupported conditions, stale source size, cross-cluster copies, disabled copy-from, or OSD lack of copy-from2.
- Full and nearfull OSD map/pool flags alter write behavior: full returns `-ENOSPC`; nearfull pushes writes toward synchronous durability.

## Test Signals

Important test coverage includes:

- Fast open from existing caps, synchronous MDS open, cap renewal after session reconnect, snapdir open, and write-open rejection on snapshots.
- Atomic open for existing files, negative dentries, symlink/no-open cases, synchronous create, async create success, async create `-EJUKEBOX`, and async create failure cleanup.
- Buffered reads/writes under cache/buffer caps and sync/direct fallback when caps are absent or mount options force sync.
- Direct read/write AIO completion, page pin release, dirtying of user-backed read pages, and `-EOLDSNAPC` retry.
- Sparse reads, holes before EOF, short reads at EOF, inline-data reads, and encrypted read decrypt/zero behavior.
- Encrypted partial-block writes with RMW, version assertion conflict retry, and object creation race retry.
- Quota exceeded, max file size, full/nearfull pool handling, append size refresh, dirty cap marking, and generic write sync.
- Punch-hole fallocate over partial and full object-set ranges, including page-cache/fscache invalidation.
- Copy_file_range offload for object-aligned compatible files and fallback for encrypted, striped, short, cross-cluster, unsupported, and partial-object cases.
