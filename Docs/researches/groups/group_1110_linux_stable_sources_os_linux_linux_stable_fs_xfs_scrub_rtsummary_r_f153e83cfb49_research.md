# Group Research: group_1110_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_rtsummary_r_f153e83cfb49

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary_repair.c

Implements online repair for the XFS realtime summary metadata file.

Key behavior:
- `xrep_setup_rtsummary` creates a hidden regular tempfile and reserves enough blocks for a complete replacement rtsummary plus worst-case bmbt overhead for preallocation and extent exchange.
- `xrep_rtsummary_prep_buf` copies generated summary words from the in-memory summary buffer into each tempfile block and installs either rtgroup-aware rtsummary headers/ops or legacy rt buffer ops.
- `xrep_rtsummary` requires `rmapbt` and atomic exchange-range support, repairs metadata inode forks first, preallocates the tempfile, copies rebuilt summary blocks, sets tempfile size, atomically exchanges contents, resets in-core rtsummary cache/state, and reaps the old fork blocks from the tempfile.

Important constraints:
- Repair aborts with `-EOPNOTSUPP` without reverse mappings or exchange-range support.
- If the scrubbed realtime bitmap block count disagrees with the superblock, repair returns success without changing anything.
- Tempfile locking is polled with termination checks because the rtsummary inode lock is already held.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.c

Provides the top-level online scrub and repair dispatcher for XFS.

Key behavior:
- Defines `meta_scrub_ops`, mapping every `XFS_SCRUB_TYPE_*` to its setup, scrub, optional repair, optional repair-evaluation, feature predicate, and input type.
- `xchk_validate_inputs` sanitizes userspace scrub requests, enforces per-type input rules, handles realtime group compatibility, rejects force-rebuild without repair, and limits repair to writable v5/crc filesystems.
- `xfs_scrub_metadata` runs the full operation lifecycle: shutdown/norecovery checks, setup, scrub, health update, optional repair, retry-on-`-EDEADLOCK`, retry-with-drain-on-`-ECHRNG`, teardown, stats merge, and final trace emission.
- `xchk_teardown` centralizes cleanup of AG/RT cursors, transactions, inode locks/references, freeze protection, xfiles, buffers, tempfiles, orphanage state, and enabled fs gates.
- `xfs_ioc_scrub_metadata` implements the single scrub ioctl with `CAP_SYS_ADMIN`, copy-in, dispatch, and copy-out.
- `xfs_ioc_scrubv_metadata` implements vectored scrub, including vector validation, optional scrub-by-handle inode pinning, barrier vectors, per-item results, optional rest delays, and signal interruption.

Important supporting logic:
- Probe scrub forces the corrupt flag when userspace probes repair on repair-capable kernels.
- Subordinate scrub contexts can temporarily switch scrub type while sharing selected parent resources.
- Postmortem logging differs depending on whether online repair is configured.
- Stats are collected only for non-`ENOENT` outcomes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.h

Defines core scrub state, dispatch contracts, scheduler-yield helpers, and scrubber prototypes.

Key structures:
- `struct xchk_relax` and `xchk_maybe_relax` rate-limit `cond_resched` and fatal-signal checks during long scans.
- `enum xchk_type` categorizes scrub inputs as disabled, per-AG, per-filesystem, per-inode, generic, or realtime-group metadata.
- `struct xchk_meta_ops` is the per-scrub-type operation table contract.
- `struct xchk_ag` stores per-AG buffers and btree cursors.
- `struct xchk_rt` stores realtime group state and realtime btree cursors.
- `struct xfs_scrub` is the central operation context, carrying mount, metadata request, transaction, target inode, temp inode, buffers, xfile/xmbuf state, lock flags, health masks, retry/gate flags, and AG/RT substate.
- `struct xfs_scrub_subord` snapshots state for nested scrub operations.

Important constants:
- `XCHK_GFP_FLAGS` standardizes scrub allocations as retryable/no-warning kernel allocations.
- `XCHK_IGET_FLAGS` marks scrub-by-handle inode lookups as untrusted and non-cache-polluting.
- `XCHK_TRY_HARDER`, `XCHK_NEED_DRAIN`, `XCHK_FSGATES_*`, and `XREP_*` flags encode retry, live-update gate, and repair state.

Exports:
- Declares all major scrub entrypoints for metadata, inode data, realtime metadata, quota checks, filesystem counters, nlinks, and cross-reference helpers.
- Provides no-op fallbacks when realtime or quota support is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/stats.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/stats.c

Implements optional online scrub statistics collection and debugfs reporting.

Key behavior:
- Tracks per-scrub-type counters for invocations, clean/corrupt/preen/cross-reference outcomes, incomplete/warning results, retries, repair attempts/successes, and scrub/repair runtime in microseconds.
- Maintains both global stats and per-mount stats.
- `xchk_stats_merge` updates global and mount stats after scrub runs.
- `xchk_stats_format` renders a text table with one row per named scrub type.
- `xchk_stats_estimate_bufsize` computes a worst-case snapshot buffer size.
- `xchk_stats_clearall` resets counters under each per-type spinlock.
- Debugfs exposes `scrub/stats` read-only and `scrub/clear_stats` write-only; writing `1` clears counters.
- Provides setup/teardown for global stats and allocation/free for per-mount stats.

Important details:
- `XFS_SCRUB_OFLAG_UNCLEAN` groups all output flags that prevent a run from counting as clean.
- Runtime accounting converts nanoseconds to microseconds with `howmany_64`.
- Counter state is protected per scrub type by `css_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/stats.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/stats.h

Declares the scrub statistics interface.

Key elements:
- `struct xchk_stats_run` carries per-run scrub time, repair time, retry count, and repair attempted/succeeded booleans.
- When `CONFIG_XFS_ONLINE_SCRUB_STATS` is enabled, declares global setup/teardown, mount allocation/free, debugfs register/unregister, and stats merge functions.
- `xchk_stats_now` returns `ktime_get_ns`.
- `xchk_stats_elapsed_ns` guarantees at least one nanosecond for clocks that return the same timestamp twice.

Disabled configuration:
- All public stats hooks compile to no-ops or zero values when stats are disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/symlink.c

Implements online scrub for symbolic links.

Key behavior:
- `xchk_setup_symlink` allocates a `XFS_SYMLINK_MAXLEN + 1` buffer before taking inode locks and, if repair is requested, asks symlink repair to reserve resources and create a tempfile.
- `xchk_symlink` validates that the target inode is a symlink, checks zapped health state, verifies plausible `i_disk_size`, and validates either local or remote symlink contents.
- Local symlinks are checked against available fork size and embedded string length.
- Remote symlinks are read via `xfs_symlink_remote_read`; the recovered buffer must contain a non-NUL target of at least the recorded length.
- A clean remote symlink clears the symlink-zapped health flag.

Important constraints:
- Non-symlink targets return `-ENOENT`.
- Invalid length or premature NUL terminators mark data fork block zero corrupt.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/symlink_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/symlink_repair.c

Implements online repair for symlink targets.

Repair strategy:
- Salvage existing target bytes when possible.
- If salvage produces exactly `i_disk_size` bytes before NUL termination, rewrite that target.
- Otherwise replace the target with an intentionally overlong explanatory dummy target that should not resolve to a real path.
- Write the replacement into a hidden temporary symlink and commit it by file contents exchange.

Key behavior:
- `xrep_setup_symlink` creates a hidden symlink tempfile and reserves maximum symlink block and bmbt exchange overhead.
- `xrep_symlink_salvage_remote` reads remote target extents manually, accepts salvage only when headers are plausible and either verifiers pass or magic is correct, and stops at the first unsafe block.
- `xrep_symlink_salvage_inline` copies inline fork bytes unless inode repair had already zapped the target to `?`.
- `xrep_symlink_salvage` accepts salvaged data only if string length equals `i_disk_size`; otherwise installs `DUMMY_TARGET`.
- `xrep_symlink_rebuild` writes the salvaged/dummy target into the tempfile, commits, allocates exchange state, swaps contents, then resets the tempfile fork.
- `xrep_symlink_swap` optimizes local-to-local replacement by copying fork data directly if it fits; otherwise it promotes local forks to extent form and uses mapping exchange.
- `xrep_symlink_reset_fork` reaps old remote blocks and rewrites the tempfile to a minimal valid dummy target.

Important constraints:
- Requires `rmapbt` to reap the old fork and exchange-range support to commit atomically.
- Uses transaction commits and relocking to satisfy exchange reservation and locking rules.
- Does not promise that concurrent `readlink` cannot see old corrupt contents during rebuild.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/symlink_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempexch.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempexch.h

Declares the temporary-file mapping exchange interface used by online repair.

Key elements:
- `struct xrep_tempexch` wraps `struct xfs_exchmaps_req`.
- `xrep_tempexch_trans_reserve` prepares and reserves resources in an existing transaction while both inodes are already locked.
- `xrep_tempexch_trans_alloc` creates a new transaction and locks/joins both inodes for exchange.
- `xrep_tempexch_contents` performs the actual mapping exchange.

Scope:
- Only available under `CONFIG_XFS_ONLINE_REPAIR`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempexch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.c

Implements hidden temporary files used to stage reconstructed metadata for online repair.

Key behavior:
- `xrep_tempfile_create` creates an unlinked, unlinkable temporary inode rooted at the filesystem root, root-owned for quota purposes, marked private, and placed on the unlinked list so recovery/inactivation can purge it.
- Directory tempfiles are initialized with `xfs_dir_init`; symlink tempfiles get a minimal valid `.` target.
- `xrep_tempfile_adjust_directory_tree` converts eligible tempfiles into metadata-directory inodes when the scrub target lives in the metadata directory tree, including quota detachment/accounting changes.
- `xrep_tempfile_remove_metadir` reverses metadata-directory state before release so inactivation follows the normal path.
- Provides IOLOCK/ILOCK helpers for tempfiles, including nowait and polled acquisition to avoid deadlocks when another inode is already locked.
- `xrep_tempfile_prealloc` ensures a tempfile range is backed by written, zeroed extents and rejects holes/delalloc surprises.
- `xrep_tempfile_copyin` walks preallocated file blocks, obtains metadata buffers, lets a caller fill each buffer, queues delayed writes, and flushes periodically.
- `xrep_tempfile_set_isize` updates disk/VFS size and rolls the repair transaction.
- `xrep_tempfile_roll_trans` logs the tempfile and rejoins it after rolling.
- `xrep_tempexch_*` helpers prepare exchange requests, estimate reservation needs, reserve blocks/quota, lock inodes, perform mapping exchange, and keep incore sizes synchronized when sizes are exchanged.
- `xrep_tempfile_copyout_local` copies local-format fork data from tempfile to target when an exchange is unnecessary or impossible.
- `xrep_is_tempfile` identifies repair tempfiles via private inode state or, for metadata-directory files, the temporary `XFS_IRECOVERY` marker.

Important constraints:
- Tempfiles must not escape to userspace.
- Atomic exchange is the commit mechanism for file-based metadata rebuilds because tempfile contents can disappear via unlinked-list cleanup.
- Quota reservation for exchanges accounts for both net and gross mapped-block movement.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.h

Declares online-repair tempfile helpers.

Key API:
- Tempfile lifecycle: `xrep_tempfile_create`, `xrep_tempfile_rele`, `xrep_is_tempfile`.
- Directory-tree adjustment: `xrep_tempfile_adjust_directory_tree`.
- Locking: IOLOCK/ILOCK nowait, polled, lock, unlock, and lock-both helpers.
- Data preparation: `xrep_tempfile_prealloc`, `xrep_tempfile_copyin`, `xrep_tempfile_set_isize`, `xrep_tempfile_roll_trans`, `xrep_tempfile_copyout_local`.
- `xrep_tempfile_copyin_fn` lets repair code fill each mapped buffer during copy-in.

Disabled configuration:
- Without online repair, most helpers disappear; `xrep_tempfile_iolock_both` falls back to locking the scrub target inode, `xrep_is_tempfile` is false, and release/adjustment are no-ops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/trace.c

Builds the scrub tracepoint implementation unit.

Key behavior:
- Includes the XFS and scrub headers required by tracepoint field assignment code.
- Defines helper `xchk_btree_cur_fsbno`, which resolves the filesystem block number for a btree cursor level, including inode-rooted btrees.
- Defines `CREATE_TRACE_POINTS` before including `scrub/trace.h`, causing tracepoint definitions to be emitted from this compilation unit.

Role:
- This file contains little runtime logic itself; it exists to provide helper code and instantiate the trace events declared in `trace.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/trace.h

Declares the ftrace event surface for XFS online scrub and repair. The file explicitly states these tracepoints are not a stable kernel ABI.

Trace coverage:
- Scrub lifecycle events: start, done, deadlock retry, repair attempt/done, dirtree start/done.
- Filesystem gate events for enabling/disabling live-update hooks.
- Vectored scrub events for vector-head input, per-vector item/outcome, and barrier failures.
- Error and marking events for filesystem blocks, inode numbers, file blocks, operation errors, incomplete scans, btree operation errors, btree corruption, and cross-reference failures.
- Quota scrub events for dquot iteration and quotacheck errors.
- Inode allocation, filesystem counter calculation/range checks, fsfreeze/fsthaw, and refcount mismatch diagnostics.
- `xfile` and `xfarray` events covering create/destroy, load/store/seek/folio/discard, array creation, sort phases, sort scans, and sort stats.
- Realtime summary record-free tracing when realtime support is enabled.
- Inode scan events covering cursor movement, visited/skipped inodes, batch iget, and retry waits.
- Nlink scrub events for dirent/parent-pointer/metafile collection, live updates, zero-link checks, incore updates, and inode comparison.
- Parent pointer, directory tree, directory path, path outcome, dirtree evaluation, live path changes, and metadata path lookup events.
- Repair events for extent reaping, reap limits, selected extents, rebuilt btree discoveries, bmap/rmap/refcount records, root finding, reservation calculations, counter resets, newbt allocation/free/claim, dinode fixes, inode fixes, CoW repair, quota repair, nlink repair, rmap live updates, tempfile creation/prealloc/copyin, fork reaping, xattr/parent-pointer salvage and replay, directory salvage/rebuild/replay/adoption, symlink salvage/rebuild/reset, unlinked-list repair, dirtree repair, metadata path repair, and realtime bitmap/rtrmap repair.

String tables and enums:
- Maps scrub types, scrub flags, scrub state flags, refcount domains, group types, rmap update operations, and directory path outcomes to readable trace output.
- Uses `TRACE_DEFINE_ENUM` for ftrace encoding of enum values.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE scrub/trace`, and `include <trace/define_trace.h>` for kernel trace generation.

Important implementation detail:
- Many events are factored through `DECLARE_EVENT_CLASS` plus `DEFINE_EVENT` wrappers to keep related tracepoint layouts consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.c

Implements large fixed-size record arrays backed by an `xfile`.

Core model:
- Stores fixed-size records in a shmem-backed xfile so online repair can handle large transient datasets without pinning all memory.
- Records can be unset; unset slots are zeroed and skipped by iteration.
- Callers provide their own concurrency control.

Key behavior:
- `xfarray_create` creates the backing xfile, allocates the array plus scratch space, records object size/log2 optimization, computes max capacity from `MAX_LFS_FILESIZE`, and enforces optional required capacity.
- `xfarray_load`, `xfarray_store`, `xfarray_unset`, `xfarray_store_anywhere`, `xfarray_length`, `xfarray_bytes`, and `xfarray_truncate` provide basic array operations.
- `xfarray_find_data` uses `SEEK_DATA` carefully to skip sparse xfile holes without instantiating pages while iterating.
- `xfarray_load_next` returns the next non-zero record and advances the cursor.
- Sorting is a nonrecursive quicksort with an explicit index stack, median-of-nine pivot selection, smaller-partition-first stack use, small-partition heapsort, direct folio heapsort when possible, and folio caching during partition scans.
- `xfarray_sort` rejects arrays with at least `2^63` records, allocates sort scratch/stack state, runs quicksort/heapsort hybrids, supports termination checks, emits trace stats, and releases cached folios.

Important constraints:
- Object size must be smaller than a page.
- Fully zeroed records are treated as unset/sparse records.
- Sort termination is driven through `xchk_maybe_relax`; the `XFARRAY_SORT_KILLABLE` flag affects interruptibility setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.h

Declares the xfile-backed fixed-record array API and sort state.

Key elements:
- `xfarray_idx_t` is a 64-bit array index type.
- Defines `XFARRAY_NULLIDX`, `XFARRAY_CURSOR_INIT`, and `foreach_xfarray_idx`.
- `struct xfarray` stores the backing xfile, current element count, maximum element count, unset slot count, object size, and optional object-size log2.
- Public operations cover create/destroy, load, sparse load, unset, store, append, store-anywhere, null-record testing, length, non-null iteration, bytes used, truncation, and sorting.
- `xfarray_iter` wraps `xfarray_load_next` into a 1/0/negative iteration API.
- Sort definitions include `xfarray_cmp_fn`, small-sort threshold, median-of-nine pivot count, and `struct xfarray_sortinfo`.
- `struct xfarray_sortinfo` documents its variable trailing allocation layout for quicksort stacks and scratch/pivot storage.
- `XFARRAY_SORT_KILLABLE` is the public sort flag.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfarray.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.c

Implements append-style variable-length blob storage over an `xfile`.

Core model:
- Each blob is stored as an `xb_key` header followed by payload bytes.
- The header records a magic value, blob size, and its own byte offset.
- The byte offset is returned as an opaque `xfblob_cookie` for later retrieval/free.

Key behavior:
- `xfblob_create` creates the backing xfile and starts blob allocation at `PAGE_SIZE`.
- `xfblob_load` validates the key magic and offset, verifies the caller buffer is large enough, then loads payload bytes.
- `xfblob_store` writes the key and payload, returns the old `last_offset` as the cookie, and advances `last_offset`; on payload write failure it discards the written key.
- `xfblob_free` validates the key and discards the key-plus-payload range.
- `xfblob_bytes` reports xfile memory consumption.
- `xfblob_truncate` discards all blob storage beyond the first page and resets `last_offset`.

Important constraints:
- Freed blob space is discarded but not reused by the allocator; storage is append-oriented.
- Invalid cookies trigger assertions and return `-ENODATA`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.h

Declares the xfile-backed blob storage API.

Key elements:
- `struct xfblob` stores the backing xfile and next append offset.
- `xfblob_cookie` is a `loff_t` offset cookie.
- Public operations cover create/destroy, load, store, free, bytes used, and truncate.
- `xfblob_storename` stores an `xfs_name` byte string as a blob.
- `xfblob_loadname` loads a blob into an `xfs_name` buffer and sets the name length to the caller-supplied size.

Important detail:
- Name helpers are thin wrappers and rely on the caller-provided size/capacity being correct.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.h -->