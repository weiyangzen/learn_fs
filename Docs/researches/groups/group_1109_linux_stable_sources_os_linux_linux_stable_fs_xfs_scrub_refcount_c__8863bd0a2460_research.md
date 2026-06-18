# Group Research: group_1109_linux_stable_sources_os_linux_linux_stable_fs_xfs_scrub_refcount_c__8863bd0a2460

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/refcount.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/refcount.c

## Purpose
Scrubs per-AG XFS refcount btrees. It verifies refcount records structurally, cross-checks them against allocation, inode, and rmap metadata, validates shared-vs-CoW ordering, and exposes helper xref checks for other scrubbers.

## Major Components
- `xchk_setup_ag_refcountbt`: enables intent draining when needed, runs repair setup if repair is possible, then initializes AG btree scrub context.
- Fragment-based rmap verification:
  - `xchk_refcountbt_rmap_check`
  - `xchk_refcountbt_process_rmap_fragments`
  - `xchk_refcountbt_xref_rmap`
- Record validation:
  - `xchk_refcountbt_rec`
  - `xchk_refcountbt_check_mergeable`
  - `xchk_refcountbt_xref_gaps`
- Whole-tree scrub:
  - `xchk_refcountbt`
- Public xref helpers:
  - `xchk_xref_is_cow_staging`
  - `xchk_xref_is_not_shared`
  - `xchk_xref_is_not_cow_staging`

## Control Flow and Invariants
The scrubber walks each refcountbt record with `xchk_btree`. For each record it:
- Converts the ondisk record to `xfs_refcount_irec`.
- Calls `xfs_refcount_check_irec`.
- Tracks CoW block count.
- Verifies shared records precede CoW records.
- Checks whether adjacent records should have been merged.
- Cross-references with used-space and inode-allocation metadata.
- Verifies refcount values by counting overlapping rmap records.

The rmap cross-check handles full-covering rmap records immediately and stores partial overlaps as ordered fragments. It then ensures the fragment working set maintains exactly the missing reference count over the whole refcount extent.

Gaps between shared refcount records are checked against rmap records to ensure no unrecorded shared extents exist.

## Dependencies and Integration
Depends on:
- `xfs_refcount_*` for refcountbt record conversion, lookup, and range queries.
- `xfs_rmap_query_range` and rmap cursors for ownership validation.
- `xchk_btree` framework for btree walking.
- `repair.h` setup hooks for optional online repair preparation.

Other scrubbers call the xref helpers to assert that blocks are not shared, not CoW staging, or are known CoW staging extents.

## Risk and Edge Cases
- Fragment verification assumes rmap records arrive in increasing block order; disorder is treated as corruption.
- Single-reference refcount records must represent CoW staging and are corrupt if owned by anything else.
- Gap checking short-circuits if rmap xref is unavailable or skipped.
- The mergeability helper as written returns false when the previous record has nonzero length, which means mergeability detection is effectively disabled after initialization; this is notable because the comment says the opposite.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/refcount_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/refcount_repair.c

## Purpose
Rebuilds a corrupt per-AG refcount btree from reverse mapping records. It reconstructs shared and CoW staging refcount records, bulk-loads a new refcountbt, commits it into the AGF, and reaps old refcountbt blocks.

## Major Components
- `struct xrep_refc`: repair state, including staged refcount records, new-btree state, old-tree bitmap, cursor position, and block counters.
- `xrep_setup_ag_refcountbt`: allocates xfbtree backing storage for the rmap record bag.
- `xrep_refc_find_refcounts`: sweep-line algorithm over rmap records using `rcbag`.
- `xrep_refc_stash` / `xrep_refc_stash_cow`: validate and store generated refcount records.
- `xrep_refc_build_new_tree`: stages, reserves, bulk-loads, and commits the new refcountbt.
- `xrep_refc_remove_old_tree`: reaps old refcountbt blocks.
- `xrep_refcountbt`: top-level repair entry point.

## Control Flow and Invariants
Repair requires rmapbt support. It scans the AG rmapbt and:
- Records CoW staging extents as CoW-domain refcount records with count 1.
- Records old refcountbt blocks in a bitmap for later reaping.
- Ignores non-shareable mappings when computing shared data extents.
- Uses a bag of active rmap intervals to emit a refcount record whenever overlap count changes and the previous count exceeds 1.

Generated records are sorted in ondisk refcountbt order, including shared records before CoW records. The sorter rejects overlap and domain ordering violations.

The new tree is built with `xrep_newbt_init_ag`, staged with an fake AG root, bulk-loaded, committed to the AGF, and followed by AGF counter reinitialization and transaction roll.

## Dependencies and Integration
Uses:
- `rcbag` for sweep-line overlap accounting.
- `xfarray` for generated refcount records.
- `xagb_bitmap` for old-tree block tracking.
- `xrep_newbt` for staging a new btree.
- `xrep_reap_agblocks` for safe old-block disposal.
- `xrep_reinit_pagf` and `xrep_roll_ag_trans` from `repair.c`.

## Risk and Edge Cases
- The repair cannot run without rmapbt because rmaps are the source of truth.
- Records are clamped to `XFS_REFC_REFCOUNT_MAX` if overlap exceeds representable refcount.
- It checks generated extents are not free space and not inode chunks before storing them.
- Alternate in-core refcountbt height is used during replacement to prevent verifier failures while old blocks may still be checkpointed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/refcount_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/repair.c

## Purpose
Provides shared online repair infrastructure for XFS scrub. It coordinates repair attempts, transaction rolling, reservation estimation, per-AG and realtime cursor setup, btree root discovery, quota handling, metadata inode repair, temporary in-memory btree setup, and reservation reset helpers.

## Major Components
- Repair orchestration:
  - `xrep_attempt`
  - `xrep_will_attempt`
  - `xrep_failure`
  - `xrep_probe`
- Transaction helpers:
  - `xrep_roll_ag_trans`
  - `xrep_roll_trans`
  - `xrep_defer_finish`
- Reservation helpers:
  - `xrep_ag_has_space`
  - `xrep_calc_ag_resblks`
  - `xrep_calc_rtgroup_resblks`
  - `xrep_reset_perag_resv`
  - `xrep_reset_metafile_resv`
- AG and rtgroup setup:
  - `xrep_ag_btcur_init`
  - `xrep_ag_init`
  - `xrep_rtgroup_btcur_init`
  - `xrep_rtgroup_init`
- Root discovery:
  - `xrep_find_ag_btree_roots`
  - `xrep_findroot_rmap`
  - `xrep_findroot_block`
- Metadata inode repair:
  - `xrep_metadata_inode_subtype`
  - `xrep_metadata_inode_forks`
  - `xrep_ino_ensure_extent_count`
  - `xrep_inode_set_nblocks`
- Quota helpers under `CONFIG_XFS_QUOTA`.

## Control Flow and Invariants
`xrep_attempt` clears scrub btree cursors, invokes the scrub operation’s repair callback, updates statistics, and returns `-EAGAIN` when scrub should rerun. It handles:
- success by clearing output flags and setting `XREP_ALREADY_FIXED`;
- `-ECHRNG` by requesting intent drain;
- `-EDEADLOCK` by retrying with `XCHK_TRY_HARDER`.

Transaction rolling preserves AG header buffer locks by logging, holding, rolling, and rejoining AGI/AGF buffers. Deferred work uses similar hold/release logic around `xfs_defer_finish`.

Reservation estimation computes worst-case rebuild space for per-AG btrees from AGI/AGF counters, with fallback assumptions when headers are corrupt. Realtime group reservation estimates currently calculate rtrmapbt size from rtgroup extents.

Metadata inode repair runs subordinate scrub/repair passes for inode core and forks, clears illegal reflink state, and removes attr forks on non-metadir metadata files.

## Dependencies and Integration
This is the shared repair layer used by nearly every specialized repair file in this group:
- Refcount/rmap repairs rely on transaction rolling, btree root/cursor helpers, and reservation reset.
- Realtime repairs use rtgroup setup and `xrep_require_rtext_inuse`.
- Metadata-inode btree repairs use `xrep_setup_xfbtree`, `xrep_metadata_inode_forks`, `xrep_inode_set_nblocks`, and buffer verification helpers.

## Risk and Edge Cases
- Repair transaction code deliberately holds clean AG header buffers across rolls, which normal code avoids; the comments explain this is required to preserve AG locks.
- Root discovery is best-effort and depends on healthy rmap data and recognizable buffer verifiers.
- Quota repair cannot allocate dquot blocks in transaction context; quota corruption forces a later quotacheck instead.
- Realtime reservation sizing only accounts for rtrmapbt in this file, despite nearby rtrefcount repair users.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/repair.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/repair.h

## Purpose
Declares the online repair API used by XFS scrub and provides no-op or unsupported stubs when online repair or realtime/quota support is not compiled.

## Major Components
- `xrep_notsupported`: common `-EOPNOTSUPP` stub.
- Repair orchestration declarations: `xrep_attempt`, `xrep_will_attempt`, `xrep_failure`.
- Transaction and reservation declarations.
- `struct xrep_find_ag_btree`: describes per-AG btrees to locate via rmap scanning.
- Setup declarations for AG btrees, inode metadata, directory/xattr/nlink repair, realtime btrees.
- Repair entry point declarations for all scrub types.
- Conditional realtime and quota declarations.
- Stub definitions under `!CONFIG_XFS_ONLINE_REPAIR`.

## Control Flow and Invariants
When online repair is enabled, this header exposes concrete repair helpers and repairers. When disabled:
- `xrep_will_attempt` still returns true for force rebuild or detected repair need so the caller can reach `xrep_attempt`.
- `xrep_attempt` returns `-EOPNOTSUPP`.
- Repair entry points map to `xrep_notsupported`.
- Setup functions mostly become no-ops.

## Dependencies and Integration
Included throughout scrub/repair code to abstract feature availability. It mediates compile-time feature differences for:
- `CONFIG_XFS_ONLINE_REPAIR`
- `CONFIG_XFS_RT`
- `CONFIG_XFS_QUOTA`

## Risk and Edge Cases
The no-repair stubs preserve scrub behavior while reporting unsupported repair rather than silently claiming success. Consumers must still check runtime filesystem feature bits, as many repairers also require rmapbt, realtime groups, exchange-range, or reflink support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/repair.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rgb_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rgb_bitmap.h

## Purpose
Provides a type-specific wrapper around `xbitmap32` for realtime-group block numbers, `xfs_rgblock_t`.

## Major Components
- `struct xrgb_bitmap`: contains an `xbitmap32`.
- Inline helpers:
  - `xrgb_bitmap_init`
  - `xrgb_bitmap_destroy`
  - `xrgb_bitmap_set`
  - `xrgb_bitmap_walk`

## Control Flow and Invariants
The wrapper preserves type intent for rtgroup-relative block bitmaps while delegating storage and traversal to the generic 32-bit bitmap implementation.

## Dependencies and Integration
Used by realtime rmap repair to collect rtgroup-relative extents, notably CoW staging extents and generated rtrmap records.

## Risk and Edge Cases
There is no extra validation beyond the underlying `xbitmap32`; callers must pass valid `xfs_rgblock_t` ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rgb_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rgsuper.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rgsuper.c

## Purpose
Scrubs and repairs the realtime group superblock metadata. Current checking is limited to rtgroup 0 and primarily cross-references metadata ownership because the rt superblock was already validated at mount time.

## Major Components
- `xchk_setup_rgsuperblock`: allocates a zero-block transaction.
- `xchk_rgsuperblock_xref`: verifies rt block 0 is used and owned by filesystem metadata.
- `xchk_rgsuperblock`: top-level scrub entry.
- `xrep_rgsuperblock`: logs the superblock during online repair.

## Control Flow and Invariants
Only realtime group 0 is accepted; other group numbers return `-ENOENT`. The scrubber obtains an existing rtgroup reference, locks the rtbitmap shared, then cross-references:
- block 0 is used realtime space;
- block 0 is owned only by `XFS_RMAP_OINFO_FS`.

Repair asserts group 0 and logs the superblock.

## Dependencies and Integration
Uses realtime group helpers, rtbitmap locking, rmap xref helpers from `rtrmap.c`, and used-space xref from `rtbitmap.c`.

## Risk and Edge Cases
The scrubber intentionally does not revalidate superblock contents beyond mount-time validation. Its value is cross-reference consistency with realtime space and rmap metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rgsuper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rmap.c

## Purpose
Scrubs per-AG reverse mapping btrees. It validates record structure, detects illegal overlaps and mergeable records, cross-references ownership against allocation/refcount/inode metadata, and compares AG metadata bitmaps against rmap records.

## Major Components
- `xchk_setup_ag_rmapbt`: repair-aware setup and intent drain gate.
- `struct xchk_rmap`: tracks overlap/previous records and metadata-owned bitmaps.
- Record checks:
  - `xchk_rmapbt_rec`
  - `xchk_rmapbt_check_unwritten_in_keyflags`
  - `xchk_rmapbt_check_overlapping`
  - `xchk_rmapbt_check_mergeable`
- Metadata bitmap construction:
  - `xchk_rmapbt_walk_ag_metadata`
  - `xchk_rmapbt_mark_bitmap`
  - `xchk_rmapbt_check_bitmaps`
- Whole-tree scrub: `xchk_rmapbt`.
- Xref helpers:
  - `xchk_xref_is_only_owned_by`
  - `xchk_xref_is_not_owned_by`
  - `xchk_xref_has_no_owner`

## Control Flow and Invariants
Before walking the rmapbt, the scrubber builds bitmaps for AG-owned metadata:
- AG headers and AGFL;
- internal log if in this AG;
- free-space btree blocks;
- inode btree blocks and finobt;
- refcountbt blocks if reflink is enabled.

During rmapbt traversal, records are checked for:
- valid conversion and `xfs_rmap_check_irec`;
- stale unwritten bits in node keys, marked as preen;
- adjacent records that could have been merged;
- illegal overlap unless both records are shareable data fork extents;
- consistency with used/free space, inode chunk ownership, CoW/refcount state.

Metadata rmap records clear corresponding bitmap regions. After traversal, any remaining set bitmap bits indicate missing rmap records.

## Dependencies and Integration
Uses `xagb_bitmap`, allocation btrees, inode btrees, refcountbt, AGFL walking, and generic scrub btree traversal. Its xref helpers are used broadly by other metadata scrubbers.

## Risk and Edge Cases
- Bitmap cross-reference is disabled if metadata walking fails, to avoid false xref corruptions.
- Shared overlap is allowed only for reflink-capable data fork mappings that are neither bmbt blocks, attr fork, nor unwritten.
- The preen path detects historical unwritten key contamination without marking corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rmap_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rmap_repair.c

## Purpose
Rebuilds per-AG reverse mapping btrees. This is the most complex AG repair path because it reconstructs ownership from primary metadata and all inodes while maintaining correctness against live filesystem updates.

## Major Components
- `struct xrep_rmap`: repair state with new-btree staging, in-memory rmapbt, live update hook, inode scanner, and counters.
- Setup:
  - `xrep_setup_ag_rmapbt`
  - `xrep_rmap_setup_scan`
  - `xrep_rmap_teardown`
- Record generation:
  - `xrep_rmap_find_rmaps`
  - `xrep_rmap_scan_inode`
  - `xrep_rmap_scan_ifork`
  - `xrep_rmap_scan_bmbt`
  - `xrep_rmap_scan_iext`
  - `xrep_rmap_find_inode_rmaps`
  - `xrep_rmap_find_refcount_rmaps`
  - `xrep_rmap_find_agheader_rmaps`
  - `xrep_rmap_find_log_rmaps`
- Space reservation and free-space metadata rmaps:
  - `xrep_rmap_reserve_space`
  - `xrep_rmap_try_reserve`
- Tree replacement:
  - `xrep_rmap_build_new_tree`
  - `xrep_rmap_get_records`
  - `xrep_rmap_reset_counters`
- Old tree reaping:
  - `xrep_rmap_remove_old_tree`
- Live updates:
  - `xrep_rmapbt_live_update`
  - `xrep_rmapbt_want_live_update`

## Control Flow and Invariants
Repair enables the rmap filesystem gate and creates an in-memory rmapbt. It first records non-free-space metadata while AG headers are locked, then cancels the transaction, unlocks AG headers, and scans filesystem inodes with an empty transaction.

The inode scan records:
- data and attr fork extents in the target AG;
- bmbt blocks through a bitmap;
- metadata btree inode blocks for realtime metadata;
- inode chunks and inode btree blocks;
- CoW staging extents and refcountbt blocks;
- AG headers and internal log.

A live rmap hook updates the in-memory btree for metadata already scanned or globally relevant while the AG lock is dropped. If live updates fail, the scan aborts and repair fails.

The new rmapbt reservation is iterative because allocating new rmapbt blocks changes free-space btree shapes and therefore the `OWN_AG` rmap records needed. After convergence, the code bulk-loads the new btree, commits it to the AGF, recalculates AGF counters, commits reservation accounting, rolls the transaction, and reaps old rmapbt blocks by finding gaps in the new rmap set minus bnobt free space.

## Dependencies and Integration
Uses:
- `xfbtree` in-memory btree support.
- `xchk_iscan` for inode scanning and visited tracking.
- `xfs_rmap_hook` for live update capture.
- `xrep_newbt` for staging.
- `xagb_bitmap` for metadata and gap tracking.
- `xrep_reap_agblocks` for old-tree cleanup.
- Common repair transaction and AG cursor helpers.

## Risk and Edge Cases
- Requires filesystem gating to block incompatible activity and prevent stale reconstruction.
- Rebuild depends on all relevant inode forks and metadata structures being readable enough to derive rmaps.
- The custom allocator uses `XFS_ALLOC_FLAG_NORMAP` to prevent recursive rmap updates while building the rmapbt itself.
- Alternate in-core rmapbt height avoids verifier failures during replacement.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rmap_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtb_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtb_bitmap.h

## Purpose
Provides a type-specific wrapper around `xbitmap64` for absolute realtime block numbers, `xfs_rtblock_t`.

## Major Components
- `struct xrtb_bitmap`: contains an `xbitmap64`.
- Inline helpers:
  - `xrtb_bitmap_init`
  - `xrtb_bitmap_destroy`
  - `xrtb_bitmap_set`
  - `xrtb_bitmap_walk`

## Control Flow and Invariants
All behavior delegates to the generic 64-bit bitmap, preserving realtime block type clarity at call sites.

## Dependencies and Integration
Available to realtime scrub/repair code that needs absolute realtime block range tracking.

## Risk and Edge Cases
No range validation is added in this wrapper; callers must provide valid realtime block ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtb_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.c

## Purpose
Scrubs realtime bitmap metadata for a realtime group. It validates realtime geometry, metadata inode shape, bitmap file extents, free-space records, and cross-references free/used realtime extents against rtrmapbt and rtrefcountbt.

## Major Components
- `xchk_setup_rtbitmap`: allocates `xchk_rtbitmap`, initializes rtgroup and repair setup, allocates transaction, installs live bitmap inode, attaches dquots, locks rtgroup metadata, and computes geometry.
- `xchk_rtbitmap_xref`: cross-references free bitmap extents.
- `xchk_rtbitmap_rec`: validates each free extent record from bitmap query.
- `xchk_rtbitmap_check_extents`: ensures bitmap file has written mappings through EOF.
- `xchk_rtbitmap`: top-level scrub.
- `xchk_xref_is_used_rt_space`: public xref helper to assert realtime blocks are not free.

## Control Flow and Invariants
The scrubber checks:
- `sb_rextents`, `sb_rextslog`, and `sb_rbmblocks` match computed values.
- bitmap file size is fsblock-aligned and large enough.
- metadata inode forks are healthy.
- all bitmap file mappings are written.
- all free extent records are valid realtime block extents.
- free extents have no rtrmap owner, are not shared, and are not CoW staging.
- used ranges between free extents have rtrmap owners.

For zoned filesystems, `xchk_xref_is_used_rt_space` validates zone rgbno rather than querying rtbitmap free state.

## Dependencies and Integration
Uses rtgroup locking, realtime allocation query APIs, metadata inode scrub, rtrmap xref helpers, rtrefcount xref helpers, and repair setup from `rtbitmap_repair.c`.

## Risk and Edge Cases
- Geometry validation can flag the bitmap inode corrupt rather than continuing.
- The final used-range check uses rtgroup extent boundaries and can detect missing rtrmap ownership after the last free record.
- The scrubber tolerates growfsrt ordering by allowing bitmap files larger than current `sb_rbmblocks`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.h

## Purpose
Defines shared state and helpers for realtime bitmap scrub and repair.

## Major Components
- `xrep_wordoff_t` and `xrep_wordcnt_t`: xfile word addressing types for staged bitmap content.
- `XREP_RTBMP_WORDMASK`: mask for rounding realtime extents to bitmap word boundaries.
- `struct xchk_rtbitmap`: per-scrub state including geometry, repair staging, expected free/used cursors, lock flags, xfile write position, and flexible word buffer.
- `xchk_rtbitmap_wordcnt`: computes repair buffer size.
- `xrep_setup_rtbitmap`: repair setup declaration or stub.

## Control Flow and Invariants
The flexible `words[]` buffer is empty for scrub-only mode and one fsblock worth of words for repair mode. Repair uses this buffer to bulk-fill staged bitmap words in an xfile.

## Dependencies and Integration
Shared by `rtbitmap.c` and `rtbitmap_repair.c`; also depends on online repair configuration for temporary exchange state.

## Risk and Edge Cases
Buffer sizing depends on whether repair can run. Callers must allocate `struct xchk_rtbitmap` with `kzalloc_flex` using `xchk_rtbitmap_wordcnt`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap_repair.c

## Purpose
Repairs realtime bitmap file contents and geometry by reconstructing free-space bits from the realtime rmapbt, staging replacement file contents in an xfile and temporary inode, exchanging mappings, and reaping old blocks.

## Major Components
- `xrep_setup_rtbitmap`: creates temporary file and xfile, estimates transaction reservation.
- xfile bitmap helpers:
  - `xfbmp_load`
  - `xfbmp_store`
  - `xfbmp_copyin`
  - `xfbmp_copyout`
  - `xrep_rtbitmap_or`
- Free-space reconstruction:
  - `xrep_rtbitmap_mark_free`
  - `xrep_rtbitmap_walk_rtrmap`
  - `xrep_rtbitmap_find_freespace`
- Output preparation:
  - `xrep_rtbitmap_prep_buf`
  - `xrep_rtbitmap_data_mappings`
  - `xrep_rtbitmap_geometry`
- Top-level repair: `xrep_rtbitmap`.

## Control Flow and Invariants
Repair requires rtrmapbt and atomic exchange-range support. It:
- Fixes metadata inode forks.
- Ensures the bitmap file’s data mappings are real written extents, converting unwritten extents with zeroing when necessary.
- Repairs superblock geometry and bitmap inode size.
- Flushes busy extents before reuse.
- Walks rtrmapbt records and marks gaps between owned regions as free in an xfile bitmap.
- Verifies free gaps are rt extent aligned, valid, and neither shared nor CoW staging.
- Preallocates a temporary file, copies staged bitmap blocks into it with proper rtbitmap buffer headers, exchanges contents with the real bitmap inode, then reaps old bitmap blocks from the temp inode.

## Dependencies and Integration
Uses:
- `xfile` for staged bitmap contents.
- temporary file/exchange helpers from scrub repair.
- rtrmapbt as source of truth for used realtime extents.
- rtrefcountbt to reject shared/CoW extents from being marked free.
- `xrep_metadata_inode_forks`, `xrep_defer_finish`, and `xrep_reap_ifork`.

## Risk and Edge Cases
- Impossibly large bitmap block counts return without attempting unsafe repair.
- The code cannot use `xfs_exchmaps_estimate` because replacement extent count is unknown before reconstruction.
- Free ranges must align to realtime extent boundaries; misalignment is corruption.
- Zoned filesystems alter used-space checking elsewhere, but reconstruction still depends on rtrmapbt ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtbitmap_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount.c

## Purpose
Scrubs realtime refcount btrees. It mirrors AG refcount scrub logic but operates on rtgroup-relative block numbers and realtime metadata inode btrees.

## Major Components
- `xchk_setup_rtrefcountbt`: repair-aware setup, rtgroup initialization, live refcount inode install, and rtgroup locking.
- Fragment-based rmap verification:
  - `xchk_rtrefcountbt_rmap_check`
  - `xchk_rtrefcountbt_process_rmap_fragments`
  - `xchk_rtrefcountbt_xref_rmap`
- Record checks:
  - `xchk_rtrefcountbt_rec`
  - `xchk_rtrefcountbt_check_mergeable`
  - `xchk_rtrefcountbt_xref_gaps`
- Whole-tree scrub: `xchk_rtrefcountbt`.
- Xref helpers:
  - `xchk_xref_is_rt_cow_staging`
  - `xchk_xref_is_not_rt_shared`
  - `xchk_xref_is_not_rt_cow_staging`

## Control Flow and Invariants
The scrubber first validates metadata inode forks, then walks the rtrefcountbt. Each record must:
- Pass `xfs_rtrefcount_check_irec`.
- Start and end on full realtime extent boundaries.
- Keep shared records before CoW records.
- Not be mergeable with adjacent records.
- Cross-reference with used realtime space and rtrmapbt ownership.

It also compares counted rtrefcountbt blocks against data-device rmap records for the rtrefcount metadata inode and compares CoW block counts against rtrmapbt CoW ownership.

## Dependencies and Integration
Uses rtgroup cursors, rtrmapbt, rtbitmap used-space xref, metadata inode fork checks, and AG rmap cursor for metadata-inode block ownership.

## Risk and Edge Cases
- Requires both rtgroup rmap/refcount context and data-device rmap context for full xref.
- As in `refcount.c`, the mergeability helper appears to return false when the previous record has nonzero length, limiting its intended detection.
- `xchk_xref_is_rt_cow_staging` sets corruption through `sc->sa.refc_cur` in one branch, which is notable because realtime checks otherwise use `sc->sr.refc_cur`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount_repair.c

## Purpose
Rebuilds a realtime refcount btree from realtime reverse mappings. It constructs shared and CoW refcount records, stages a new metadata-inode btree, commits it into the rtrefcount inode, and reaps old rtrefcountbt blocks.

## Major Components
- `struct xrep_rtrefc`: repair state with generated records, new-btree state, old block bitmap, and cursor position.
- `xrep_setup_rtrefcountbt`: sets up xfbtree backing storage.
- `xrep_rtrefc_find_refcounts`: scans old metadata blocks and performs sweep-line overlap accounting over rtrmapbt.
- `xrep_rtrefc_stash` / `xrep_rtrefc_stash_cow`: validate and store generated records.
- `xrep_rtrefc_scan_ag`: scans data-device rmapbt for blocks owned by the rtrefcount inode.
- `xrep_rtrefc_build_new_tree`: bulk-loads and commits a staged metadata-inode btree.
- `xrep_rtrefcountbt`: top-level repair.

## Control Flow and Invariants
Repair requires rtrmapbt. It first repairs metadata inode forks, then:
- Scans every AG rmapbt for old blocks owned by the rtrefcount inode.
- Walks realtime rmaps to derive shared and CoW refcount records.
- Rejects sb metadata inode owners, attr fork records, bmbt blocks, and invalid realtime refcount extents.
- Ensures refcount records are full realtime extent aligned and in-use.
- Sorts records in ondisk order.
- Builds the new btree with `xrep_newbt_init_metadir_inode`, reserves inode blocks, bulk-loads, commits the staged rtrefcountbt, updates `i_nblocks`, commits newbt accounting, rolls transaction, and reaps old blocks.

## Dependencies and Integration
Uses `rcbag`, `xfarray`, `xfsb_bitmap`, metadata inode repair helpers, rtgroup btree cursors, AG rmap scanning, and `xrep_reap_metadir_fsblocks`.

## Risk and Edge Cases
- The generated record array is sized for one record per realtime extent.
- Rebuild fails if rtrmapbt is unavailable.
- Old rtrefcountbt blocks live on the data device as metadata inode btree blocks, so the repair scans all AG rmapbts to find them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrefcount_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap.c

## Purpose
Scrubs realtime reverse mapping btrees. It validates realtime rmap records, detects illegal overlaps and mergeable records, and cross-references realtime ownership with rtbitmap and rtrefcount metadata.

## Major Components
- `xchk_setup_rtrmapbt`: repair-aware setup, rtgroup initialization, live rmap inode install, and rtgroup locking.
- `struct xchk_rtrmap`: previous and furthest-overlap tracking.
- Record checks:
  - `xchk_rtrmapbt_rec`
  - `xchk_rtrmapbt_check_overlapping`
  - `xchk_rtrmapbt_check_mergeable`
  - `xchk_rtrmapbt_xref`
  - `xchk_rtrmapbt_xref_rtrefc`
- Whole-tree scrub: `xchk_rtrmapbt`.
- Xref helpers:
  - `xchk_xref_has_no_rt_owner`
  - `xchk_xref_has_rt_owner`
  - `xchk_xref_is_only_rt_owned_by`

## Control Flow and Invariants
The scrubber validates metadata inode forks, derives the rmap inode owner info, then walks the rtrmapbt. Records must:
- Decode cleanly and pass `xfs_rtrmap_check_irec`.
- Not overlap unless realtime reflink permits sharing and records are not unwritten.
- Not be mergeable with adjacent records.
- Refer to used realtime space.
- If shared, correspond to shareable data fork mappings.

## Dependencies and Integration
Uses realtime bitmap xref for used/free validation and rtrefcountbt xref for shared-state validation. Other realtime scrubbers call this file’s xref helpers to assert ownership or absence of ownership.

## Risk and Edge Cases
- Realtime rmap records are simpler than AG rmap records because they describe realtime data fork extents, but live consistency still depends on rtgroup locking.
- In the CoW branch, `xchk_rtrmapbt_xref` calls the AG CoW xref helper rather than the realtime-specific helper; this is a notable integration detail to verify against surrounding code expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap_repair.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap_repair.c

## Purpose
Rebuilds realtime reverse mapping btrees. It scans realtime file mappings and CoW staging extents, records old rtrmapbt blocks from data-device rmapbts, bulk-loads a new metadata-inode rtrmapbt, and reaps the old tree.

## Major Components
- `struct xrep_rtrmap`: repair state with in-memory rtrmapbt, new-btree staging, old block bitmap, live update hook, inode scan, and counters.
- Setup/teardown:
  - `xrep_setup_rtrmapbt`
  - `xrep_rtrmap_setup_scan`
  - `xrep_rtrmap_teardown`
- Record collection:
  - `xrep_rtrmap_find_rmaps`
  - `xrep_rtrmap_scan_inode`
  - `xrep_rtrmap_scan_dfork`
  - `xrep_rtrmap_scan_bmbt`
  - `xrep_rtrmap_scan_iext`
  - `xrep_rtrmap_find_refcount_rmaps`
  - `xrep_rtrmap_scan_ag`
- Tree build:
  - `xrep_rtrmap_build_new_tree`
  - `xrep_rtrmap_get_records`
  - `xrep_rtrmap_iroot_size`
- Live update hook:
  - `xrep_rtrmapbt_live_update`
  - `xrep_rtrmapbt_want_live_update`
- Top-level repair: `xrep_rtrmapbt`.

## Control Flow and Invariants
Repair fixes metadata inode forks, initializes an in-memory rtrmapbt and old-block bitmap, then:
- Records rt superblock ownership for rtgroup 0 if present.
- Records realtime CoW staging extents from rtrefcountbt.
- Unlocks rt metadata and scans inodes using an empty transaction.
- For realtime files, records data fork mappings in the target rtgroup, coalescing adjacent compatible extents.
- Re-locks rtgroup metadata, scans all AG rmapbts for old rtrmapbt inode blocks, and counts/validates generated records.
- Builds a new metadata-inode btree, reserves inode blocks, bulk-loads from the in-memory rtrmapbt, commits the staged tree, updates inode block count, rolls the transaction, and reaps old btree blocks.

Live rtrmap updates are captured through an rmap hook while the inode scan is running. Updates for non-inode owners are always wanted because CoW staging extents were scanned before the iscan.

## Dependencies and Integration
Uses:
- `xfbtree` in-memory rtrmapbt.
- `xchk_iscan`.
- `xfs_rmap_hook`.
- `xrgb_bitmap` for rtgroup-relative CoW extent collection.
- `xfsb_bitmap` for old data-device metadata blocks.
- metadata-inode newbt helpers and reap helpers.

## Risk and Edge Cases
- Repair assumes realtime rmap reconstruction only needs realtime file data fork mappings plus CoW staging and rt superblock metadata.
- Old rtrmapbt blocks are not on the realtime device; they are data-device blocks owned by the rtrmap metadata inode and found via all AG rmapbts.
- A failed live update aborts the scan and causes repair failure to avoid installing stale metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtrmap_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.c

## Purpose
Scrubs the realtime summary file by recomputing summary counters from the realtime bitmap into an xfile and comparing the computed data against the ondisk rtsummary inode.

## Major Components
- `xchk_setup_rtsummary`: allocates state and xfile, initializes rtgroup, optional repair setup, transaction, live summary inode, quota attachment, locking, and geometry.
- xfile suminfo helpers:
  - `xfsum_load`
  - `xfsum_store`
  - `xfsum_copyout`
- Computation:
  - `xchk_rtsum_record_free`
  - `xchk_rtsum_compute`
- Comparison:
  - `xchk_rtsum_compare`
- Top-level scrub: `xchk_rtsummary`.

## Control Flow and Invariants
Setup computes expected realtime geometry while bitmap/summary metadata are locked. The scrubber checks:
- `sb_rextents` matches computed rextents.
- `m_rsumlevels` and `m_rsumblocks` match computed summary geometry.
- summary inode size is fsblock-aligned and large enough.
- metadata inode forks are healthy.

It then queries all free extents from the rtbitmap. For each free extent, it computes the summary offset from bitmap block offset and length log, increments the staged suminfo word in the xfile, and later compares staged blocks to ondisk rtsummary blocks. Summary file mappings must be written and not extend past EOF.

## Dependencies and Integration
Uses realtime allocation query APIs, xfile storage, metadata inode scrub, rtgroup locking, and repair setup from the rtsummary repair path declared in `rtsummary.h`.

## Risk and Edge Cases
- If recomputation returns `-EFSCORRUPTED`, the bitmap is marked corrupt because rtsummary scrub depends on bitmap correctness.
- Supports both old and rtgroup suminfo raw formats via `xchk_rtsum_inc`.
- Allows summary file to be larger than current required size because growfsrt expands files before updating geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.h

## Purpose
Defines shared state and declarations for realtime summary scrub and repair.

## Major Components
- `struct xchk_rtsummary`: contains optional temp-exchange state, rtalloc args, computed geometry, reservation blocks, xfile copyout position, and flexible suminfo buffer.
- `xfsum_copyout`: exported helper to copy staged summary words out of the xfile.
- `xrep_setup_rtsummary`: repair setup declaration or no-op stub.

## Control Flow and Invariants
The flexible `words[]` buffer is used as a block-sized comparison/copy buffer for staged summary data. Geometry fields are computed during setup and consumed by scrub and repair.

## Dependencies and Integration
Shared by `rtsummary.c` and the corresponding repair implementation. Uses realtime allocation args and online repair temporary exchange state when available.

## Risk and Edge Cases
Callers must allocate the flexible array large enough for `mp->m_blockwsize` suminfo words, as done by `xchk_setup_rtsummary`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.h -->