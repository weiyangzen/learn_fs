# Group Research: group_868_linux_sources_os_linux_linux_fs_xfs_scrub_rtsummary_repair_c_sources_e11352939d09

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rtsummary_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/rtsummary_repair.c

This file implements online repair for the XFS realtime summary metadata file. It stages a freshly generated realtime summary into a hidden temporary regular file, atomically exchanges the mappings with the real summary file, resets incore summary state, and reaps the old blocks.

Key entry points:
- `xrep_setup_rtsummary(struct xfs_scrub *sc, struct xchk_rtsummary *rts)`: creates the repair tempfile and adds a conservative block reservation for a complete summary rewrite plus bmbt overhead.
- `xrep_rtsummary(struct xfs_scrub *sc)`: main repair path for the realtime summary.
- `xrep_rtsummary_prep_buf(...)`: per-block copy-in callback used by `xrep_tempfile_copyin`.

Control flow:
1. Setup creates an `S_IFREG` tempfile and reserves `m_rsumblocks + 2 * xfs_bmbt_calc_size(...)`.
2. Repair requires `rmapbt` and exchange-range support.
3. It refuses to proceed if the checked bitmap block count disagrees with the superblock.
4. It repairs metadata inode forks first with `xrep_metadata_inode_forks`.
5. It try-locks the tempfile inode while already holding the realtime summary inode lock.
6. It joins both inodes to the transaction, preallocates summary file blocks, copies generated summary bytes from `xfsum_copyout`, and sets the tempfile size.
7. It reserves exchange resources, exchanges contents, invalidates/reset caches and mount summary geometry, then reaps the old fork blocks from the tempfile.

Important dependencies:
- `scrub/tempfile.h` and `scrub/tempexch.h` provide staging and atomic mapping exchange.
- `scrub/rtsummary.h` provides the generated summary data and `xfsum_copyout`.
- `scrub/reap.h` frees the old mapping set after exchange.
- `xfs_rtbitmap.h`, `xfs_rtalloc.h`, and realtime group state define summary formats and rtgroup behavior.

Data/format handling:
- For rtgroup-enabled filesystems, copied buffers receive `XFS_RTSUMMARY_MAGIC`, owner inode, block address, metadata UUID, and `xfs_rtsummary_buf_ops`.
- For older non-rtgroup realtime layouts, buffers use `xfs_rtbuf_ops`.
- Transaction buffer type is set to `XFS_BLFT_RTSUMMARY_BUF`.

Risk notes:
- Repair is intentionally unavailable without `rmapbt` and exchange-range support.
- Block reservation must be made before the replacement summary extent count is known, so it intentionally overestimates.
- The function cannot drop the realtime summary ILOCK once dirty transaction state exists, which explains the early reservation strategy.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/rtsummary_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/scrub.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/scrub.c

This is the central online scrub and repair dispatcher for XFS. It validates ioctl inputs, maps scrub type numbers to setup/scrub/repair callbacks, manages scrub context lifetime, records health and stats, implements retry modes, and exposes both scalar and vectored scrub ioctls.

Major responsibilities:
- Defines `meta_scrub_ops[]`, the dispatch table for every `XFS_SCRUB_TYPE_*`.
- Implements `xfs_scrub_metadata`, the core setup/scrub/repair/teardown state machine.
- Implements `xfs_ioc_scrub_metadata`, the single-operation ioctl path.
- Implements `xfs_ioc_scrubv_metadata`, the vectored ioctl path with barriers, optional rest periods, and scrub-by-handle support.
- Handles subordinate scrub contexts for repair code that needs to run a nested scrub type.

Important entry points:
- `xchk_probe`: probe scrub/repair availability.
- `xchk_scrub_create_subord` / `xchk_scrub_free_subord`: clone a scrub context with a different metadata type while preserving parent state.
- `xchk_teardown`: releases AG/rtgroup cursors, transactions, inode locks, xfiles, xmbuf targets, tempfiles, orphanage references, and fsgates.
- `xchk_validate_inputs`: validates scrub metadata fields based on operation type.
- `xfs_scrub_metadata`: full single metadata scrub/repair execution engine.
- `xfs_ioc_scrub_metadata`: user copy wrapper for one scrub.
- `xfs_ioc_scrubv_metadata`: user copy wrapper for scrub vectors.
- `xfs_scrubv_check_barrier`: cancels later vectored work if earlier operations failed according to a barrier mask.

Dispatch model:
- `ST_NONE`: probe-like calls with no object selector.
- `ST_FS`: whole-filesystem metadata.
- `ST_PERAG`: per-allocation-group metadata.
- `ST_INODE`: inode-scoped metadata.
- `ST_GENERIC`: scrubber-specific selector validation.
- `ST_RTGROUP`: realtime group metadata, with compatibility behavior for pre-rtgroups filesystems.

The dispatch table covers superblock, AG headers, AG btrees, inode record/forks, directory, xattr, symlink, parent pointers, realtime bitmap/summary/group btrees, quota types, filesystem counters, quotacheck, nlinks, health, dirtree, metapath, and rtgroup superblock.

Core scrub flow:
1. Trace start.
2. Reject shutdown and norecovery mounts.
3. Validate user inputs and filesystem feature support.
4. Allocate `struct xfs_scrub`.
5. Acquire freeze protection for repair operations.
6. Run the type-specific setup callback.
7. Run scrub or repair-evaluation callback.
8. Convert `-EDEADLOCK` into `XCHK_TRY_HARDER` retry and `-ECHRNG` into defer-op drain retry.
9. Update health if scrub completes.
10. If repair was requested and needed, call `xrep_attempt`; `-EAGAIN` loops back to setup/scrub.
11. Run postmortem logging if corruption remains.
12. Teardown and merge stats unless operation was not found.
13. Convert verifier corruption errnos into output flags with success errno.

Vectored scrub:
- Requires `CAP_SYS_ADMIN`, validates vector head and vector entries, copies at most one page of vector data from userspace, and traces every item.
- Supports `XFS_SCRUB_TYPE_BARRIER`, where `sv_flags` names output flags that should cancel later vector items if earlier work reported them.
- Can pin a scrub-by-handle inode across the vector run to avoid repeated untrusted lookups.
- Writes per-vector return code and output flags back to userspace.

Risk notes:
- Retry behavior is stateful: teardown must succeed before retry flags are applied.
- `xchk_teardown` commits a transaction only for successful repair requests; otherwise it cancels.
- Repair validation deliberately defers checking `ops->repair` until scrub proves repair is needed.
- Vectored scrub must keep ABI validation strict because vectors are copied from user memory and later copied back.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/scrub.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/scrub.h

This header defines the core online scrub context, operation dispatch contracts, scheduler-relaxation helpers, state flags, subordinate scrub support, and scrub/xref function declarations used throughout `fs/xfs/scrub`.

Key types:
- `struct xchk_relax`: rate-limited scheduler yielding and fatal signal polling state.
- `struct xchk_meta_ops`: setup/scrub/repair/repair_eval/feature-test callbacks plus operation selector type.
- `struct xchk_ag`: per-AG buffers and btree cursors.
- `struct xchk_rt`: realtime group lock state and rt btree cursors.
- `struct xfs_scrub`: central per-operation state object.
- `struct xfs_scrub_subord`: subordinate scrub context used by repair routines.

Important helpers/macros:
- `INIT_XCHK_RELAX`: initializes yielding state.
- `xchk_maybe_relax`: amortizes `cond_resched` and fatal-signal checks.
- `XCHK_GFP_FLAGS`: scrub allocation policy with no warnings and retry-mayfail behavior.
- `XCHK_IGET_FLAGS`: untrusted, donotcache inode lookup flags for fsck operations.
- `xchk_should_terminate`: standard interruption check.
- `xchk_nothing`: disabled scrubber placeholder returning `-ENOENT`.

State flags:
- `XCHK_TRY_HARDER`: retry after resource/lock-order limits.
- `XCHK_HAVE_FREEZE_PROT`: mount write protection held.
- `XCHK_FSGATES_*`: dynamic hook/fsgate state for drain/quota/dirent/rmap live updates.
- `XCHK_NEED_DRAIN`: retry setup after defer-op drain requirement.
- `XREP_RESET_PERAG_RESV`: repair must reset AG reservation.
- `XREP_ALREADY_FIXED`: repair already ran and current pass is evaluating it.

Declared scrubbers:
- Metadata scrubbers for AG headers, allocation/inode/rmap/refcount btrees, inode/forks, directory, xattr, symlink, parent pointers, dirtree, metapath, quotas, filesystem counters, nlinks, and realtime metadata.
- Realtime and quota declarations compile to `xchk_nothing` stubs when config options are off.

Declared cross-reference helpers:
- Data-device helpers check ownership, free/used state, inode chunks, CoW staging, and shared extents.
- Realtime helpers mirror ownership/shared/CoW checks for rt space and compile to no-ops without `CONFIG_XFS_RT`.

Risk notes:
- `xfs_scrub` owns many resource lifetimes, including transactions, inode locks, tempfiles, orphanage state, xfiles, and per-AG/per-rtgroup cursors; teardown ordering is critical.
- `xchk_maybe_relax` only checks expensive conditions every 100 calls and yields at most 10 times per second.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/stats.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/stats.c

This file implements optional online scrub statistics collection and debugfs reporting under `CONFIG_XFS_ONLINE_SCRUB_STATS`. It tracks per-scrub-type invocation outcomes, retry counts, repair attempts/successes, and cumulative runtime.

Key structures:
- `struct xchk_scrub_stats`: per-scrub-type counters and runtime totals protected by `css_lock`.
- `struct xchk_stats`: debugfs root plus an array indexed by `XFS_SCRUB_TYPE_NR`.
- `global_stats`: global aggregate stats object.
- `name_map[]`: maps scrub type numbers to debugfs text names.

Important entry points:
- `xchk_stats_merge`: merges one completed scrub run into global and per-mount stats.
- `xchk_global_stats_setup` / `xchk_global_stats_teardown`: initialize and expose global stats.
- `xchk_mount_stats_alloc` / `xchk_mount_stats_free`: allocate/free per-mount stats.
- `xchk_stats_register` / `xchk_stats_unregister`: create/remove debugfs files.
- `xchk_scrub_stats_read`: emits formatted stats snapshot.
- `xchk_clear_scrub_stats_write`: accepts `1` to clear counters.

Debugfs interface:
- Directory: `scrub`
- File `stats` is read-only and reports lines of:
  `name invocations clean corrupt preen xfail xcorrupt incomplete warning retries checktime_us repair_invocations repair_success repairtime_us`
- File `clear_stats` is write-only and clears all counters when userspace writes `1`.

Runtime accounting:
- Outcome counters are derived from scrub output flags.
- Clean means no corrupt/preen/xfail/xcorrupt/incomplete/warning output flag.
- Runtime nanoseconds from `xchk_stats_run` are rounded up into microseconds with `howmany_64`.
- Repair counters are based on `repair_attempted` and `repair_succeeded`.

Risk notes:
- Snapshot formatting is intentionally single-read: if file position is nonzero, read returns 0 to avoid fragmented/garbled text.
- Stats update uses per-type spinlocks, but formatting reads without taking those locks, so output is a best-effort live snapshot rather than a serialized transaction.
- `xchk_stats_teardown` currently has no dynamic work besides the surrounding debugfs/free paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/stats.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/stats.h

This header declares the online scrub statistics API and provides compile-time stubs when `CONFIG_XFS_ONLINE_SCRUB_STATS` is disabled.

Key type:
- `struct xchk_stats_run`: per-operation timing and retry/repair result data accumulated by `scrub.c`.

When stats are enabled, it declares:
- Global lifecycle: `xchk_global_stats_setup`, `xchk_global_stats_teardown`.
- Per-mount lifecycle: `xchk_mount_stats_alloc`, `xchk_mount_stats_free`.
- Debugfs registration: `xchk_stats_register`, `xchk_stats_unregister`.
- Merge function: `xchk_stats_merge`.
- Time helpers: `xchk_stats_now`, `xchk_stats_elapsed_ns`.

Time behavior:
- `xchk_stats_now()` returns `ktime_get_ns()`.
- `xchk_stats_elapsed_ns()` returns at least 1 ns if the clock did not advance, avoiding zero-duration runtime reports.

When stats are disabled:
- Lifecycle/register/merge operations compile to no-ops or success.
- Timing helpers compile to zero-returning expressions.

Risk notes:
- Callers can unconditionally call the stats API because disabled builds erase the overhead.
- The elapsed helper intentionally prevents “instantaneous” nonzero operations from disappearing from stats when clock resolution is coarse.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/symlink.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/symlink.c

This file implements online scrub for symbolic links. It validates symlink type, target length, local fork contents, remote symlink block readability, and target null-termination behavior.

Entry points:
- `xchk_setup_symlink(struct xfs_scrub *sc)`: allocates a max-length target buffer, optionally sets up repair resources, then delegates inode-content setup.
- `xchk_symlink(struct xfs_scrub *sc)`: validates the symlink target.

Scrub behavior:
1. Rejects non-symlink inodes with `-ENOENT`.
2. If the symlink looks zapped via `XFS_SICK_INO_SYMLINK_ZAPPED`, marks data fork corrupt.
3. Checks `i_disk_size` is `1..XFS_SYMLINK_MAXLEN`.
4. For local-format symlinks, checks the size fits in the inode data fork and that a string-length scan reaches at least `i_disk_size`.
5. For remote symlinks, reads target bytes with `xfs_symlink_remote_read`, processes read errors through scrub error handling, then verifies the target buffer contains enough non-NUL bytes.
6. Marks the symlink zapped flag healthy if a remote symlink reads cleanly.

Dependencies:
- `xfs_symlink.h` and `xfs_symlink_remote.h` provide symlink format and remote read helpers.
- `scrub/common.h` supplies setup, corrupt marking, and error-processing helpers.
- `scrub/repair.h` supplies `xrep_setup_symlink` when repair is possible.

Risk notes:
- On-disk symlink targets are not NUL-terminated, so this scrubber uses bounded `strnlen` checks against expected length.
- The setup buffer is `XFS_SYMLINK_MAXLEN + 1` so repair/scrub code can NUL-terminate safely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/symlink_repair.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/symlink_repair.c

This file implements online repair for corrupted XFS symbolic links. It attempts to salvage a plausible target, writes a repaired target into a hidden temporary symlink, atomically exchanges data fork contents with the damaged symlink, and reaps/reset old blocks.

Key entry points:
- `xrep_setup_symlink(struct xfs_scrub *sc, unsigned int *resblks)`: creates an `S_IFLNK` tempfile and reserves enough blocks for max symlink target plus bmbt overhead.
- `xrep_symlink(struct xfs_scrub *sc)`: main repair function.

Salvage logic:
- `xrep_symlink_salvage_inline`: copies local fork bytes unless inode repair already zapped the target to `?`.
- `xrep_symlink_salvage_remote`: reads mapped remote symlink blocks manually, accepts blocks when offset/byte/owner header checks pass and either verifier passes or magic is intact, then copies payload bytes.
- `xrep_symlink_salvage`: uses salvage only if initial scrub did not already flag direct corruption; NUL-terminates the buffer; requires `strlen(buffer) == i_disk_size`; otherwise substitutes a long dummy target.

Dummy target:
- The replacement message is deliberately longer than `NAME_MAX` but within XFS symlink max length, so resolving it should fail with name-too-long instead of accidentally pointing to a real path.

Rebuild/exchange flow:
1. Require `rmapbt` for old fork reaping and exchange-range for atomic commit.
2. Salvage target into `sc->buf`.
3. Unlock the damaged inode, lock the tempfile, reserve quota/blocks, destroy dummy target fork, and write the target with `xfs_symlink_write_target`.
4. Commit the repair transaction before computing exchange reservation.
5. Allocate exchange transaction and lock both inodes.
6. If both old and new targets are local and the new target fits the repaired inode fork, copy local fork bytes directly.
7. Otherwise convert local forks to extent format as needed and call `xrep_tempexch_contents`.
8. Reap old remote blocks from the temporary file and reset its fork to a short dummy symlink.

Important helpers:
- `xrep_symlink_local_to_remote`: wraps local-to-remote conversion and fixes CRC symlink owner.
- `xrep_symlink_swap_prep`: promotes local forks to exchangeable extent format.
- `xrep_symlink_swap`: chooses direct local copy vs mapping exchange.
- `xrep_symlink_reset_fork`: frees old blocks and rewrites tempfile target to `?`.

Risk notes:
- Readlink can still see old corrupted contents while repair writes the hidden tempfile because VFS does not take IOLOCK for symlink reads.
- Salvage is conservative: mismatched length or embedded NUL causes fallback to dummy target.
- The file depends on atomic mapping exchange to avoid exposing partially rebuilt symlink contents.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/symlink_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempexch.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/tempexch.h

This header declares the temporary-file exchange wrapper used by online repair code when `CONFIG_XFS_ONLINE_REPAIR` is enabled.

Key type:
- `struct xrep_tempexch`: wraps `struct xfs_exchmaps_req`.

Declared functions:
- `xrep_tempexch_trans_reserve`: prepare exchange request and reserve resources in an existing transaction.
- `xrep_tempexch_trans_alloc`: allocate a fresh transaction, lock inodes, join them, and reserve resources.
- `xrep_tempexch_contents`: perform the mapping exchange and finish deferred work.

Scope:
- Only declared for online repair builds.
- Used by file-based metadata repairs such as symlink and realtime summary repair to atomically commit rebuilt contents staged in a tempfile.

Risk notes:
- The wrapper centralizes exchange-map request construction and transaction reservation, which keeps repair callers from open-coding low-level `xfs_exchmaps_req` setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempexch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempfile.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/tempfile.c

This file implements hidden temporary inodes and atomic content exchange support for online repair. Repairs rebuild file-based metadata in an unlinkable private inode, then exchange fork mappings with the damaged metadata inode.

Major entry points:
- `xrep_tempfile_create`: creates an unlinkable private tempfile of a requested mode.
- `xrep_tempfile_rele`: releases and cleans up `sc->tempip`.
- `xrep_tempfile_adjust_directory_tree`: converts temp regular/dir files into metadata-directory files when repairing metadata-directory inodes.
- Tempfile lock helpers: IOLOCK/ILOCK nowait, polled, lock, unlock, both-inode lock/unlock.
- `xrep_tempfile_prealloc`: ensures a tempfile range has written extents.
- `xrep_tempfile_copyin`: writes block data to preallocated tempfile extents through a callback.
- `xrep_tempfile_set_isize`: updates disk and VFS inode size.
- `xrep_tempfile_roll_trans`: logs tempfile core and rolls repair transaction.
- `xrep_tempexch_trans_reserve`, `xrep_tempexch_trans_alloc`, `xrep_tempexch_contents`: exchange-map transaction support.
- `xrep_tempfile_copyout_local`: direct local fork copy for shortform forks.
- `xrep_is_tempfile`: identifies repair tempfiles.

Tempfile creation:
- Uses root inode as parent context and `XFS_ICREATE_TMPFILE | XFS_ICREATE_UNLINKABLE`.
- Allocates root-owned dquots so quota limits do not block repair.
- Drops realtime inheritance flags because tempfiles are metadata staging objects.
- Marks VFS inode `S_PRIVATE` and clears `IOP_XATTR` so LSM/ACL/xattr layers ignore it.
- Initializes directories with `xfs_dir_init`.
- Initializes symlinks with a harmless one-byte target.
- Places the inode on the unlinked list so recovery/inactivation purges it if repair aborts.

Metadata-directory handling:
- Since tempfiles are created before scrub knows if `sc->ip` is a metadir inode, `xrep_tempfile_adjust_directory_tree` later marks eligible temp dir/reg files as metadata files, subtracting quota inode count and detaching dquots.
- `xrep_tempfile_remove_metadir` reverses that before normal inactivation.

Preallocation/copy-in:
- `xrep_tempfile_prealloc` walks mappings, rejects delalloc, converts holes/unwritten extents into written zeroed extents, and finishes deferred work.
- `xrep_tempfile_copyin` reads each mapping, gets the metadata buffer at the mapped disk address, invokes a caller callback to populate/verify it, queues delayed writes, and flushes every 512 KiB.

Exchange support:
- `xrep_tempexch_prep_request` fills `xfs_exchmaps_req`.
- `xrep_tempexch_estimate` handles local-format forks by estimating required local-to-extent conversion overhead.
- `xrep_tempexch_reserve_quota` reserves quota when exchanging blocks between inodes with distinct dquots.
- `xrep_tempexch_trans_reserve` is for callers that already hold dirty locked inodes.
- `xrep_tempexch_trans_alloc` creates a new truncate-style transaction and uses exchange-range locking.
- `xrep_tempexch_contents` calls `xfs_exchange_mappings`, finishes deferred work, and swaps incore VFS sizes when `XFS_EXCHMAPS_SET_SIZES` is set.

Risk notes:
- Locking is deliberately try/poll based in places to avoid deadlocks while another inode lock is held.
- `xrep_is_tempfile` must distinguish repair tempfiles from metadata-directory files that also use private flags; it uses `XFS_IRECOVERY` for temporary metadir inodes.
- The exchange path rejects COW fork exchange because COW forks do not exist on disk.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempfile.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/tempfile.h

This header declares the temporary-file API used by online repair.

When `CONFIG_XFS_ONLINE_REPAIR` is enabled, it exposes:
- Creation/release: `xrep_tempfile_create`, `xrep_tempfile_rele`.
- Metadata-directory adjustment: `xrep_tempfile_adjust_directory_tree`.
- IOLOCK helpers: `xrep_tempfile_iolock_nowait`, `xrep_tempfile_iolock_polled`, `xrep_tempfile_iounlock`.
- ILOCK helpers: `xrep_tempfile_ilock`, `xrep_tempfile_ilock_nowait`, `xrep_tempfile_iunlock`, `xrep_tempfile_iunlock_both`, `xrep_tempfile_ilock_both`.
- Storage prep/copy: `xrep_tempfile_prealloc`, `xrep_tempfile_copyin`.
- Size/transaction/local-fork helpers: `xrep_tempfile_set_isize`, `xrep_tempfile_roll_trans`, `xrep_tempfile_copyout_local`.
- Predicate: `xrep_is_tempfile`.

Callback type:
- `xrep_tempfile_copyin_fn`: caller-provided function to populate one tempfile buffer during copy-in.

When online repair is disabled:
- `xrep_tempfile_iolock_both` falls back to locking the scrub inode with `xchk_ilock`.
- `xrep_is_tempfile` is false.
- `xrep_tempfile_adjust_directory_tree` is success.
- `xrep_tempfile_rele` is a no-op.

Risk notes:
- The header lets scrub/repair code compile in non-repair kernels without scattering config checks through callers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/tempfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/trace.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/trace.c

This file instantiates XFS scrub tracepoints. It includes the XFS and scrub headers needed by trace event definitions, defines a helper used by trace formatting, then includes `scrub/trace.h` with `CREATE_TRACE_POINTS`.

Key helper:
- `xchk_btree_cur_fsbno(struct xfs_btree_cur *cur, int level)`: computes the filesystem block number for a btree cursor level.
  - Uses the buffer at that level if present.
  - For inode-rooted btrees at root level, returns the inode’s containing block.
  - Returns `NULLFSBLOCK` otherwise.

Tracepoint instantiation:
- `#define CREATE_TRACE_POINTS`
- `#include "scrub/trace.h"`

Dependencies:
- Pulls in inode, btree, AG, realtime bitmap, quota, directory, rmap, parent, metadata-file, rtgroup, and scrub helper headers so trace events can access field definitions.
- Includes `scrub/xfarray.h`, `scrub/xfblob.h`, `scrub/iscan.h`, `scrub/orphanage.h`, `scrub/nlinks.h`, `scrub/fscounters.h`, and bitmap/dirtree helpers for trace data structures.

Risk notes:
- This file should remain the single tracepoint-definition translation unit; other users include `trace.h` without `CREATE_TRACE_POINTS`.
- The helper exists so trace events can render btree cursor locations consistently without duplicating cursor logic in the generated trace code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/trace.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/trace.h

This is the tracepoint catalog for XFS online scrub and repair. It defines ftrace event classes, symbolic strings, and concrete trace events for scrub dispatch, errors, btree traversal, xfile/xfarray operations, inode scans, link/count repair, directory tree repair, temporary files, symlink repair, and realtime repair. The header explicitly states these tracepoints are not stable kernel ABI.

Top-level definitions:
- `TRACE_SYSTEM xfs_scrub`
- Forward declarations for scrub, xfile, xfarray, quota iterator, inode scan, nlink, fscounters, rmap updates, parent records, and dirtree state.
- `TRACE_DEFINE_ENUM` entries for scrub types, refcount domains, group types, rmap ops, dirtree outcomes, and other symbolic values.
- String tables: `XFS_SCRUB_TYPE_STRINGS`, `XFS_SCRUB_FLAG_STRINGS`, `XFS_SCRUB_STATE_STRINGS`, `XCHK_DIRPATH_OUTCOME_STRINGS`.

Major scrub trace groups:
- Scrub lifecycle: `xchk_start`, `xchk_done`, `xchk_deadlock_retry`, `xrep_attempt`, `xrep_done`.
- Fsgates: `xchk_fsgates_enable`, `xchk_fsgates_disable`.
- Vectored scrub: `xchk_scrubv_start`, `xchk_scrubv_item`, `xchk_scrubv_outcome`, `xchk_scrubv_barrier_fail`.
- General errors: op errors, file op errors, block/inode/file-block corruption, warnings, preen events, incomplete scans.
- Btree tracing: btree operation errors, btree corruption, inode-fork btree events, btree record/key events, xref errors.
- Filesystem counters and freeze/thaw events.
- Quota-specific iterator and quotacheck events under `CONFIG_XFS_QUOTA`.

xfile and xfarray events:
- `xfile_create`, `xfile_destroy`, `xfile_load`, `xfile_store`, `xfile_seek_data`, `xfile_get_folio`, `xfile_put_folio`, `xfile_discard`.
- `xfarray_create`, `xfarray_isort`, `xfarray_foliosort`, `xfarray_qsort`, `xfarray_sort`, `xfarray_sort_scan`, `xfarray_sort_stats`.

Scrub-side higher-level events:
- Realtime summary free-record tracing under `CONFIG_XFS_RT`.
- Inode scan cursor, visit, skip, batch iget, and retry-wait events.
- Nlink collection, live updates, zero-link checks, incore updates, and inode comparison.
- Parent pointer slowpath/defer tracing.
- Dirtree/path construction, upward walks, disappeared/bad-generation/nondirectory/unlinked/crossing path states, outcome setting/evaluation, live updates, and metapath lookup.

Repair trace groups under `CONFIG_XFS_ONLINE_REPAIR`:
- Reaping and extent disposal/binval limits.
- Rebuild discovery events for allocation btrees, inode btrees, refcount, bmap, rmap, and findroot.
- AG and rtgroup repair reservation sizing.
- Counter reset and new-btree allocation/claiming.
- Dinode and inode repair decisions.
- CoW repair mapping and staging-free events.
- Quota repair events.
- Nlink repair updates.
- Rmap live update events.
- Temporary file creation/preallocation/copy-in and old fork extent reaping.
- Xattr salvage/rebuild, parent pointer stash/replay, and xattr parent scans.
- Directory recovery, dirent salvage/replay, adoption, parent finding, and dentry invalidation.
- Symlink salvage target, rebuild, and reset-fork events.
- Inode unlinked-list walking, reload, resolve, relink, add, and commit events.
- Metapath repair lookup/link/unlink events.
- Realtime bitmap and realtime rmap repair events under `CONFIG_XFS_RT`.

Integration:
- Included by ordinary scrub/repair files for trace event declarations.
- Included by `trace.c` with `CREATE_TRACE_POINTS` to instantiate events.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE scrub/trace`, and `<trace/define_trace.h>`.

Risk notes:
- The file is dense generated-trace infrastructure rather than normal control flow; mistakes in event field extraction can break builds or produce misleading diagnostics.
- Several events are config-gated, so consumers must account for missing events depending on kernel config.
- Trace output includes names and symlink targets in some repair paths, so it can expose filesystem metadata to privileged trace readers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfarray.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfarray.c

This file implements `xfarray`, a sparse, xfile-backed array of fixed-size records for online repair. It stores large in-memory working sets in shmem-backed `xfile` storage so they can be paged out, and provides load/store/unset/append/iteration plus an xfile-aware sorting implementation.

Core data model:
- `struct xfarray` owns an `xfile`, record count `nr`, capacity `max_nr`, sparse zero-slot count `unset_slots`, object size, and optional log2 object-size optimization.
- All-zero records represent unset sparse entries and are skipped by iteration.
- Callers provide concurrency control.

Basic API:
- `xfarray_create`: creates backing xfile, validates capacity, computes max record count, and allocates scratch space after the struct.
- `xfarray_destroy`: destroys backing xfile and frees the array.
- `xfarray_load`: loads an element or returns `-ENODATA` beyond current length.
- `xfarray_store`: stores a nonzero element, extends `nr`, and rejects indexes beyond `max_nr`.
- `xfarray_unset`: truncates if unsetting the tail element, otherwise writes a zero record and increments `unset_slots`.
- `xfarray_store_anywhere`: reuses an unset slot if available, otherwise appends.
- `xfarray_load_next`: iterates to the next nonzero record, using `SEEK_DATA` to avoid instantiating sparse holes.
- `xfarray_bytes`: reports backing xfile memory usage.
- `xfarray_truncate`: discards backing storage and resets length.

Offset/index helpers:
- `xfarray_idx`: converts xfile byte offset to array index, using shift when object size is power-of-two.
- `xfarray_pos`: converts index to byte offset.
- `xfarray_scratch`: returns inline scratch buffer after the `xfarray` struct.

Sorting:
- `xfarray_sort` sorts array records with a custom nonrecursive quicksort plus optimizations:
  - Uses explicit index stacks instead of recursion.
  - Chooses pivots by median-of-nine sampling.
  - Processes smaller partitions first to cap stack depth.
  - Uses in-memory heapsort for small ranges.
  - Sorts directly in one backing folio when a range fits.
  - Caches folios during partition scans to reduce load/store overhead.
- `xfarray_sortinfo_alloc` builds the stack and scratch area.
- `xfarray_isort`, `xfarray_foliosort`, `xfarray_qsort_pivot`, `xfarray_qsort_push`, and `xfarray_sort_scan` implement the optimized sort.
- Debug builds count loads, stores, compares, and heapsorts.

Risk notes:
- Stored records must not be all zero, because zero means unset.
- Sorting assumes array contents are valid records; sparse/unset handling is mostly in pivot sampling and iteration paths.
- `xfarray_sort` rejects arrays with `>= 2^63` records.
- Large sorts can be interrupted through `xchk_maybe_relax` behavior controlled by sort flags.
- Any xfile load/store/folio error aborts the sort and returns the error.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfarray.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfarray.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfarray.h

This header declares the xfile-backed fixed-size array API and sort support.

Key definitions:
- `xfarray_idx_t`: 64-bit array index type.
- `XFARRAY_NULLIDX`: invalid index sentinel.
- `XFARRAY_CURSOR_INIT`: initial iterator cursor.
- `foreach_xfarray_idx`: simple full-index iteration macro.

Key type:
- `struct xfarray`: backing `xfile`, current length, max length, unset-slot count, object size, and object-size log2 cache.

Basic functions:
- Lifecycle: `xfarray_create`, `xfarray_destroy`.
- Element operations: `xfarray_load`, `xfarray_load_sparse`, `xfarray_store`, `xfarray_unset`, `xfarray_append`, `xfarray_store_anywhere`.
- Iteration: `xfarray_length`, `xfarray_load_next`, `xfarray_iter`.
- Utility: `xfarray_element_is_null`, `xfarray_truncate`, `xfarray_bytes`.

Sort declarations:
- `xfarray_cmp_fn`: comparator type.
- `XFARRAY_ISORT_SHIFT`, `XFARRAY_ISORT_NR`: small-range sort thresholds.
- `XFARRAY_QSORT_PIVOT_NR`: median-of-nine pivot sample count.
- `struct xfarray_sortinfo`: state for xfile-backed quicksort, including stack depth, flags, relax state, cached folio, and debug counters.
- `XFARRAY_SORT_KILLABLE`: sort can be interrupted by fatal signal.
- `xfarray_sort`: public sort entry point.

Risk notes:
- The sortinfo structure uses extra bytes after the struct for variable-size stacks and scratch records; the header documents the implied layout because C cannot express multiple VLAs in a struct.
- `xfarray_load_sparse` treats `-ENODATA` as an all-zero record for callers that want sparse semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfarray.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfblob.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfblob.c

This file implements `xfblob`, an append-only blob store backed by an `xfile`. It stores variable-length byte strings and returns xfile offsets as cookies for later retrieval/freeing.

Data format:
- Every blob is preceded by a packed `struct xb_key`:
  - `xb_magic`: `XB_KEY_MAGIC`
  - `xb_size`: blob payload size
  - `xb_offset`: byte offset of this key
- Blob data follows the key immediately.
- `last_offset` starts at `PAGE_SIZE`, leaving the first page unused/reserved.

Entry points:
- `xfblob_create`: creates backing xfile and initializes blob metadata.
- `xfblob_destroy`: destroys xfile and frees object.
- `xfblob_store`: writes key and payload, returns cookie, advances `last_offset`.
- `xfblob_load`: validates key magic/offset and loads payload into caller buffer.
- `xfblob_free`: validates key and discards key+payload range.
- `xfblob_bytes`: reports backing xfile usage.
- `xfblob_truncate`: discards all blobs after the first page and resets `last_offset`.

Error behavior:
- Invalid key magic or offset returns `-ENODATA` and asserts.
- Loading into too-small caller buffer returns `-EFBIG` and asserts.
- If payload store fails after key store succeeds, the key range is discarded.

Risk notes:
- Freed blobs are discarded but not reused; new stores always append at `last_offset`.
- Cookies are raw offsets and must come from this blob store.
- The implementation is simple variable-size storage for repair scratch data, not a general allocator.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfblob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfblob.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/xfblob.h

This header declares the xfile-backed variable-length blob store API used by scrub/repair scratch structures.

Key types:
- `struct xfblob`: owns backing `xfile` and the next append offset.
- `xfblob_cookie`: `loff_t` offset cookie identifying a stored blob.

Declared functions:
- Lifecycle: `xfblob_create`, `xfblob_destroy`.
- Blob operations: `xfblob_store`, `xfblob_load`, `xfblob_free`.
- Utility: `xfblob_bytes`, `xfblob_truncate`.

Name helpers:
- `xfblob_storename`: stores an `xfs_name` byte string.
- `xfblob_loadname`: loads bytes into an `xfs_name` and sets `xname->len`.

Risk notes:
- `xfblob_loadname` casts `xname->name` to mutable storage, so callers must provide an `xfs_name` whose name buffer is writable and large enough.
- Size checking is enforced by `xfblob_load`; callers must track expected blob size separately.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/xfblob.h -->