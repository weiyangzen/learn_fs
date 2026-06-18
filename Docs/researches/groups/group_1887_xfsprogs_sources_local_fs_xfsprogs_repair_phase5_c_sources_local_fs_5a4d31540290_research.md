# Group Research: group_1887_xfsprogs_sources_local_fs_xfsprogs_repair_phase5_c_sources_local_fs_5a4d31540290

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase5.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase5.c

## Role

`phase5.c` implements xfs_repair phase 5: rebuilding allocation group headers and per-AG btrees from the in-core state established by earlier phases. It reconstructs free-space btrees, inode btrees, optional rmap/refcount btrees, AGF/AGFL/AGI headers, superblock counters, and realtime metadata checks.

## Core Flow

- `mk_incore_fstree()` scans the phase bitmap for each AG and converts unknown/free regions into in-core bno/bcnt extent trees.
- `phase5_func()` rebuilds one AG: estimates btree space, initializes rebuild cursors, builds free-space, inode, rmap, and refcount trees, writes AGF/AGFL/AGI, and accounts per-AG superblock counters.
- `phase5()` preserves root/realtime fixed inodes, allocates per-AG counter arrays, decides whether packed btrees are needed, processes all AGs, syncs the primary superblock, commits AG btree rmap records, reinserts lost reserved blocks, and clears `bad_ino_btree`.
- `check_rtmetadata()` dispatches zoned filesystem checks or legacy realtime bitmap/summary validation.

## Important Data

- `sb_icount_ag`, `sb_ifree_ag`, and `sb_fdblocks_ag` accumulate per-AG counter rebuild results before aggregation.
- `lost_blocks` records blocks reserved but ultimately not consumed by btree rebuilding so they can be freed back to the filesystem.
- `need_packed_btrees` is set when realtime btree metadata could consume enough free space that denser btree packing is required.

## Dependencies

This file depends heavily on repair bulkload helpers, AG btree rebuild helpers, in-core block maps, rmap/refcount reconstruction, realtime repair code, zoned metadata checks, libxfs buffer/trans APIs, and progress reporting.

## Risk Areas

- Phase 5 trusts the in-core block and inode state built by earlier phases; bad earlier classification can create bad rebuilt metadata.
- Space accounting is delicate because btree roots, AGFL blocks, lazy superblock counters, and rmap/refcount blocks are accounted differently.
- Low-free-space filesystems depend on `are_packed_btrees_needed()` estimating metadata space conservatively enough.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase5.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase6.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase6.c

## Role

`phase6.c` implements xfs_repair phase 6: checking inode connectivity, validating and repairing directory contents, recreating required root/realtime/quota metadata inodes, moving disconnected inodes to `lost+found`, and feeding expected parent-pointer records to `pptr.c`.

## Core Flow

1. Initializes parent pointer tracking.
2. Tears down phase 5 extent state and adds inode extra data.
3. Reinitializes missing root and metadata-root directories.
4. Rebuilds realtime bitmap/summary/rmap/refcount metadata, either sb-rooted or metadata-directory rooted.
5. Recreates/relinks quota metadata files on metadir filesystems.
6. Marks standalone metadata inodes as reached.
7. Traverses all directory inodes using inode prefetch.
8. Rebuilds directories whose `..` entries had to be inferred.
9. Moves unreached inodes into `lost+found`.
10. Cross-checks and repairs parent pointer xattrs.

## Directory Repair

- Longform directories are validated by scanning data blocks, leaf blocks, node blocks, and free-space blocks.
- Shortform directories are checked in-place and can remove junk entries by compacting the local data fork.
- The directory hash table tracks entries by name and address to detect duplicate names, missing leaf entries, duplicate leaf entries, bad hash values, and bad stale counts.
- Bad entries are marked by overwriting the name with `/`, then the directory can be rebuilt from salvaged entries.
- Ftype mismatches are repaired when the filesystem supports directory file types.
- Missing `.` and selected missing `..` entries are recreated or scheduled for rebuild.

## Connectivity Repair

- Directory traversal updates reached/reference counts in the in-core inode tree.
- Directories already reached through another parent are treated as inconsistent and their duplicate entry is junked.
- Disconnected inodes are linked into `lost+found`; directories have `..` updated to point there.
- Metadata inode contents are truncated before relocation to avoid exposing metadata payloads through `lost+found`.

## Dependencies

This file depends on libxfs directory, inode, transaction, parent pointer, realtime, quota, and metadir APIs; repair inode trees; prefetch; progress; parent pointer tracking; quota skip handling; and rmap/realtime rebuild helpers.

## Risk Areas

- Directory salvage must balance preserving recoverable entries against avoiding links to free, missing, metadata/regular mismatched, or already-connected inodes.
- Parent pointer correctness depends on every surviving directory entry being recorded through `add_parent_ptr()`.
- Rebuilding metadata directories and quota/realtime metadata changes inode reachability and quota-check behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase6.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase7.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase7.c

## Role

`phase7.c` implements the final link-count verification and correction phase. It compares each live inode’s disk link count against the reference count accumulated during directory traversal and fixes mismatches when not in no-modify mode.

## Core Flow

- `phase7()` sets the progress message, initializes quotacheck, creates a workqueue, and queues one link-count update task per AG.
- `do_link_updates()` walks all confirmed non-free inodes in an AG, compares recorded disk nlinks to counted references, updates mismatches, and feeds each inode to `quotacheck_adjust()`.
- `update_inode_nlinks()` opens the inode in a transaction and logs the core after calling `set_nlink()`.
- After all AGs complete, phase 7 verifies user, group, and project quota counters and tears down quotacheck state.

## Dependencies

It depends on the in-core inode tree populated by earlier phases, libxfs inode/transaction APIs, workqueues, progress reporting, and `quotacheck.c`.

## Risk Areas

- In write mode, assertions assume all non-free inodes were reached and have positive reference counts.
- If phase 6 reachability/reference accounting is wrong, phase 7 will make link counts match that wrong model.
- Quotacheck is coupled to this phase because it piggybacks on the final live-inode scan.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase7.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/pptr.c -->
# File Research: sources/local-fs/xfsprogs/repair/pptr.c

## Role

`pptr.c` validates and repairs XFS directory parent pointer xattrs. It builds a filesystem-wide expected parent-pointer index from phase 6 directory entries, then compares that index against actual `ATTR_PARENT` extended attributes on every live inode.

## Data Model

- `nameblobs` stores deduplicated directory entry names globally.
- `fs_pptrs[agno].pptr_recs` stores expected parent pointer records per child AG.
- `ag_pptr` records expected `(child_agino, parent_ino, parent_gen, namehash, name_cookie)`.
- `file_pptr` records actual xattr parent pointers found on a single inode.
- Garbage parent-pointer xattrs are staged in slabs plus xfblob name/value storage for later removal.

## Core Flow

- `parent_ptr_init()` allocates per-AG slabs and global string storage if the filesystem has parent pointers.
- `add_parent_ptr()` is called by phase 6 for each surviving directory entry to record the expected child-parent-name tuple.
- `check_parent_ptrs()` processes AGs in parallel.
- `check_ag_parent_ptrs()` sorts expected records and scans every live inode in the AG.
- `check_file_parent_ptrs()` walks xattrs, records valid parent pointers, stages malformed parent xattrs, removes garbage, and calls `crosscheck_file_parent_ptrs()`.
- `crosscheck_file_parent_ptrs()` lockstep-compares expected and actual records, adding missing pptrs, removing extra pptrs, and replacing mismatched generation/name records.
- `try_erase_parent_ptrs()` removes all parent pointer xattrs from metadata files before they are relinked into metadata directories.

## Dependencies

This file uses libxfs parent pointer helpers, xattr walking, slabs, xfblob/strblobs temporary storage, workqueues, repair inode trees, and global no-modify behavior.

## Risk Areas

- Correctness depends on phase 6 only recording entries that survive directory repair.
- Name cookies are used as comparison keys, so global name storage consistency is critical.
- Duplicate records can arise from `..` reprocessing; `AG_PPTR_POSSIBLE_DUP` suppresses exact duplicate additions.
- The implementation repairs parent pointers from directory entries, not directories from parent pointer data.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/pptr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/pptr.h -->
# File Research: sources/local-fs/xfsprogs/repair/pptr.h

## Role

`pptr.h` declares the parent pointer repair interface used by phase 6 and metadata repair code.

## Interface

- `parent_ptr_init()` and `parent_ptr_free()` manage global parent-pointer checking state.
- `add_parent_ptr()` records an expected parent pointer from a surviving directory entry.
- `check_parent_ptrs()` scans and repairs on-disk parent pointer xattrs.
- `try_erase_parent_ptrs()` removes parent pointers from an inode, mainly for metadata relinking paths.

## Dependencies

The header assumes libxfs mount and inode types are already available to includers.

## Risk Areas

The interface is intentionally global-state oriented; callers must initialize before recording entries and free only after `check_parent_ptrs()` completes.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/pptr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/prefetch.c -->
# File Research: sources/local-fs/xfsprogs/repair/prefetch.c

## Role

`prefetch.c` implements threaded inode and metadata read-ahead for repair phases. It primes the libxfs buffer cache with inode clusters, directory data, directory bmap btree blocks, and selected metadata so later phase processing blocks less on disk I/O.

## Core Behavior

- `init_prefetch()` records the mount, device fd, and batch sizing.
- `start_inode_prefetch()` creates per-AG prefetch state and a queueing worker, optionally chained after a previous AG.
- `pf_queuing_worker()` walks inode records in an AG, queues non-sparse inode clusters, starts I/O workers, and throttles read-ahead with a semaphore.
- `pf_io_worker()` drains queued buffers with batched `pread()` operations.
- `pf_read_inode_dirs()` verifies inode buffers and queues directory data or bmap btree blocks when useful.
- `do_inode_prefetch()` chooses between cache-only parallel processing, single-thread prefetch, or segmented threaded prefetch.
- `wait_for_inode_prefetch()` gates processing until enough data is queued or ready.
- `cleanup_inode_prefetch()` joins workers and destroys per-AG state.

## Queueing Strategy

Buffers are held in an AVL/btree keyed by fsblock. Primary and secondary queues avoid running too far ahead of processing. Directory metadata receives higher cache priority than generic inode buffers because later phases reuse it more often.

## Dependencies

This file uses pthreads, semaphores, libxfs buffers, bmap parsing, directory geometry, repair inode trees, workqueues, and progress/thread RCU registration.

## Risk Areas

- Prefetch intentionally ignores I/O errors; real repair logic must still validate buffers later.
- Buffer locks are acquired with trylock to avoid deadlocks with repair code.
- Aggressive prefetch can thrash the libxfs cache, so the chaining and semaphore limits are part of correctness for performance.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/prefetch.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/prefetch.h -->
# File Research: sources/local-fs/xfsprogs/repair/prefetch.h

## Role

`prefetch.h` declares the repair prefetch subsystem and its per-AG state structure.

## Interface

- `do_prefetch` enables or disables read-ahead globally.
- `PF_THREAD_COUNT` fixes four I/O workers per prefetch context.
- `prefetch_args_t` contains locks, condition variables, worker thread IDs, the I/O queue, AG number, state flags, throttling semaphore, and AG chaining pointer.
- `init_prefetch()`, `start_inode_prefetch()`, `do_inode_prefetch()`, `wait_for_inode_prefetch()`, and `cleanup_inode_prefetch()` form the public lifecycle.
- Optional `XR_PF_TRACE` hooks emit prefetch traces.

## Dependencies

It depends on pthreads, semaphores, repair `incore.h`, and the repair workqueue type.

## Risk Areas

Callers must pass `prefetch_args_t` through the intended wait/process/cleanup sequence; skipping cleanup would leak threads, conditions, semaphores, and queued buffers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/prefetch.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/progress.c -->
# File Research: sources/local-fs/xfsprogs/repair/progress.c

## Role

`progress.c` implements periodic and final progress reporting for xfs_repair phases. It maintains per-AG done counters, report message metadata, phase timestamps, a background timer thread, and summary duration output.

## Core Behavior

- `init_progress_rpt()` allocates `prog_rpt_done`, initializes `global_msgs`, and starts the reporting thread.
- `progress_rpt_thread()` waits for timer signals, sums progress counters, prints formatted status, and for selected phases prints rate/percentage/ETA.
- `set_progress_msg()` switches the active report format and resets counters.
- `print_final_rpt()` prints the current report’s final count.
- `timestamp()` records phase start/end times and optionally reports libxfs buffer cache state.
- `duration()` formats elapsed seconds into weeks/days/hours/minutes/seconds.
- `summary_report()` prints phase timing summaries.

## Data Model

`progress_rpt_reports` maps the progress IDs in `progress.h` to a message, count type, and format style. `phase_times[8]` stores per-phase and total timing.

## Dependencies

It uses pthreads, POSIX timers/signals, global repair settings such as `glob_agcount`, `ag_stride`, `report_interval`, `verbose`, `no_modify`, and repair logging helpers.

## Risk Areas

- The reporting thread relies on signal/timer behavior and shared globals guarded by `global_msgs.mutex`.
- `PROG_RPT_INC` increments shared counters from worker threads without per-counter locking, so counters are approximate progress telemetry rather than transactional state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/progress.h -->
# File Research: sources/local-fs/xfsprogs/repair/progress.h

## Role

`progress.h` defines progress report IDs and declares the progress-reporting API.

## Interface

- Phase and report constants map repair phases to progress messages.
- `init_progress_rpt()`, `stop_progress_rpt()`, `set_progress_msg()`, `print_final_rpt()`, `timestamp()`, `duration()`, and `summary_report()` are exported.
- `PROG_RPT_INC(a,b)` increments progress only when AG striding and progress reporting are active.
- `do_parallel` is declared as a shared repair setting.

## Dependencies

Consumers rely on global `ag_stride`, `prog_rpt_done`, and phase-specific constants matching `progress.c`.

## Risk Areas

The report ID constants must stay in sync with the `progress_rpt_reports` array ordering in `progress.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/protos.h -->
# File Research: sources/local-fs/xfsprogs/repair/protos.h

## Role

`protos.h` is a central declaration header for major xfs_repair phase entry points and shared setup/superblock helpers.

## Interface

It declares initialization, superblock verification/read/write helpers, geometry extraction, AG buffer allocation, inode list printing, error string formatting, thread initialization, phase functions `phase1` through `phase7`, realtime metadata checking, and `verify_set_agheader()`.

## Dependencies

The declarations reference libxfs initialization, XFS mount/superblock/AG buffer types, and repair phase implementation files.

## Risk Areas

This header is broad and shared; signature drift between phase files and this header would break repair orchestration.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/protos.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/quotacheck.c -->
# File Research: sources/local-fs/xfsprogs/repair/quotacheck.c

## Role

`quotacheck.c` verifies that quota files match the live inode/block accounting observed by xfs_repair. It builds in-core dquot counters during phase 7 and compares them against on-disk dquot records.

## Core Behavior

- `quotacheck_setup()` decides which quota types to check based on quota flags, discovered quota inodes, lost quota state, and `quotacheck_skip()`.
- `quotacheck_adjust()` opens each live non-quota inode, skips metadata directory files, counts data/realtime blocks, and increments user/group/project quota counters.
- `quotacheck_verify()` opens the quota inode, walks its data extents, reads dquot clusters, compares on-disk counters and types to in-core counts, and reports missing on-disk records.
- `quotacheck_results()` returns checked quota flags, or zero if any mismatch/runtime error cleared the state.
- `discover_quota_inodes()` finds quota metadata inodes from the metadata directory before inode scanning.
- `update_sb_quotinos()` synchronizes superblock quota inode numbers from repair’s discovered state.

## Data Model

Each quota type has a `qc_dquots` AVL64 tree keyed by dquot id. `qc_rec` tracks block count, realtime block count, inode count, and whether a corresponding on-disk record was seen.

## Dependencies

This file uses libxfs quota/dquot/inode/bmap/buffer APIs, repair quota inode tracking globals, AVL64 helpers, and repair logging.

## Risk Areas

- Any allocation, read, extent, or mismatch error clears `chkd_flags`, causing repair not to preserve quota checked flags.
- Realtime block counting requires reading file extents and subtracting realtime blocks from ordinary block counts.
- V4 group/project quota type handling has special root-dquot tolerance because old filesystems can reuse the non-user quota file.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/quotacheck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/quotacheck.h -->
# File Research: sources/local-fs/xfsprogs/repair/quotacheck.h

## Role

`quotacheck.h` declares quota verification and quota inode discovery/update hooks for xfs_repair.

## Interface

- `quotacheck_skip()` disables quota checking.
- `quotacheck_setup()`, `quotacheck_adjust()`, `quotacheck_verify()`, `quotacheck_results()`, and `quotacheck_teardown()` manage the quota check lifecycle.
- `update_sb_quotinos()` updates superblock quota inode fields.
- `discover_quota_inodes()` finds quota metadata inodes before scanning.

## Dependencies

It references XFS mount, buffer, inode number, and quota type types from libxfs.

## Risk Areas

The lifecycle is split across phases: setup/adjust/verify happen in phase 7, while discovery and superblock update are used earlier/later by repair orchestration.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/quotacheck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag.c -->
# File Research: sources/local-fs/xfsprogs/repair/rcbag.c

## Role

`rcbag.c` implements an in-memory “refcount bag” used by rmap/refcount repair logic to track currently overlapping reverse mappings and derive shared refcount extents.

## Core Behavior

- `rcbag_init()` allocates the bag, reserves an in-memory xmbuf-backed btree sized for expected rmaps, and initializes the xfbtree.
- `rcbag_add()` inserts or increments a record keyed by `(startblock, blockcount, owner)`.
- `rcbag_count()` returns the total stacked item count.
- `rcbag_next_edge()` finds the next block boundary where the current sharing set changes.
- `rcbag_remove_ending_at()` removes all bag records ending at a block boundary and decrements the item count by their refcounts.
- `rcbag_ino_iter_*()` iterates distinct owners when at least two mappings are stacked.
- `rcbag_dump()` prints all records for debugging.

## Dependencies

It wraps `rcbag_btree.c`, xfbtree, xmbuf, libxfs btree cursors, repair error handling, and rmap record types.

## Risk Areas

- `nr_items` counts references, not simply distinct btree records; updates and removals must preserve that meaning.
- The code aborts on unexpected btree lookup/update/delete failures because this structure is internal repair state.
- Edge detection scans the whole bag to find the minimum ending block, which is simple but dependent on bag size.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag.h -->
# File Research: sources/local-fs/xfsprogs/repair/rcbag.h

## Role

`rcbag.h` declares the refcount bag abstraction used by rmap/refcount reconstruction.

## Interface

It exposes bag lifecycle, add/count operations, edge calculation, removal by ending block, distinct-inode iteration, and debug dumping. `struct rcbag_iter` carries a btree cursor and current inode owner.

## Dependencies

The API references XFS mount, rmap record, and btree cursor types.

## Risk Areas

Callers must bracket inode iteration with `rcbag_ino_iter_start()` and `rcbag_ino_iter_stop()` and must not treat `rcbag_count()` as a distinct-record count.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag_btree.c -->
# File Research: sources/local-fs/xfsprogs/repair/rcbag_btree.c

## Role

`rcbag_btree.c` defines the in-memory btree implementation backing `rcbag.c`. It adapts libxfs btree operations to fixed-size refcount bag records keyed by start block, block count, and inode owner.

## Core Behavior

- Defines key/record initialization, key comparison, ordering checks, and record ordering.
- Verifies in-memory btree blocks with `RCBAG_MAGIC`, v5 btree headers, max levels, and max records.
- Provides `rcbagbt_mem_ops`, an `XFS_BTREE_TYPE_MEM` operation table using xfbtree allocation/free/root helpers.
- `rcbagbt_mem_cursor()` allocates cursors from a dedicated kmem cache.
- `rcbagbt_mem_init()` initializes an xfbtree over an xmbuf buffer target.
- `rcbagbt_maxrecs()`, `rcbagbt_calc_size()`, and `rcbagbt_maxlevels_possible()` size the tree.
- Lookup/get/update/insert helpers translate between rmap records, rcbag records, and libxfs btree cursors.

## Dependencies

It depends on libxfs btree internals, xfbtree memory btrees, xfs buffer verification, kmem cache allocation, and `rcbag_btree.h`.

## Risk Areas

- The btree ordering contract must match `rcbag.c` expectations exactly.
- The cursor cache must be initialized and destroyed by repair startup/shutdown.
- CRC checks are skipped for speed, so structural verification is the main guard for this in-memory tree.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag_btree.h -->
# File Research: sources/local-fs/xfsprogs/repair/rcbag_btree.h

## Role

`rcbag_btree.h` defines the record layout, block addressing macros, and public helper API for the in-memory refcount bag btree.

## Data Structures

- `RCBAG_MAGIC` identifies refcount bag btree blocks.
- `struct rcbag_key` contains `startblock`, `blockcount`, and `ino`.
- `struct rcbag_rec` adds `refcount` to the key fields.
- `rcbag_ptr_t` is the long-pointer type used by internal btree blocks.
- `RCBAG_REC_ADDR`, `RCBAG_KEY_ADDR`, and `RCBAG_PTR_ADDR` compute on-block addresses.

## Interface

The header declares sizing helpers, cursor-cache lifecycle, memory cursor creation, memory tree initialization, and lookup/get/update/insert operations.

## Dependencies

It references libxfs btree, mount, transaction, buffer target, and xfbtree types.

## Risk Areas

The record/key layouts are cast into libxfs btree unions, so size and ordering assumptions must remain compatible with the generic btree code.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/rcbag_btree.h -->