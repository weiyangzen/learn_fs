# Group Research: group_985_linux_stable_sources_os_linux_linux_stable_fs_ext4_mballoc_c_sources_79c0f8a2ce19

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable`; files under `fs/ext4`.

This group covers ext4 multiblock allocation, its private allocator data model, indirect/extent mapping migration, and multiple-mount protection.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc.c

## Purpose

Implements ext4's multiblock allocator. It maintains in-memory buddy allocation state derived from on-disk block bitmaps plus preallocation descriptors, chooses allocation groups and free extents, manages inode/locality-group preallocations, updates allocation bitmaps and counters, processes delayed frees after journal commit, supports discard/FITRIM, and exposes free-space iteration for fsmap.

## Main Responsibilities

- Build and maintain per-block-group buddy structures and group free-space summaries.
- Load block bitmaps into the buddy-cache inode and regenerate buddy data from on-disk bitmaps plus preallocations.
- Select allocation groups using allocation criteria, goal hints, optimized xarray indexes, linear fallback, and bitmap prefetching.
- Allocate blocks through `ext4_mb_new_blocks()`, including quota/free-space reservation, preallocation reuse, request normalization, buddy allocation, and bitmap/journal update.
- Track, consume, create, discard, and release inode preallocations and per-CPU locality-group preallocations.
- Free blocks through `ext4_free_blocks()`, with bigalloc cluster rounding, metadata revocation, delayed reuse until journal commit, discard, and buddy/counter updates.
- Initialize and tear down mount-level mballoc state, slab caches, proc/debug sequence views, and KUnit test exports.
- Support fast-commit replay with simple idempotent allocation/free helpers.
- Implement `FITRIM` scanning and `ext4_mballoc_query_range()` free-extent callbacks used by fsmap.

## Key Operations

- `ext4_mb_generate_buddy()` scans a block-group bitmap for free runs, populates buddy-order counters, records first free cluster and fragment count, validates descriptor free-cluster counts, and updates optimized scan indexes.
- `ext4_mb_init_cache()`, `ext4_mb_init_group()`, and `ext4_mb_load_buddy_gfp()` populate and pin the buddy-cache folios that hold each group's bitmap and buddy block.
- `mb_mark_used()` and `mb_free_blocks()` update in-memory allocation state, fragment counters, largest-free-order index, and average-fragment-size index.
- `ext4_mb_scan_groups()` dispatches between linear scanning and optimized xarray scanning across allocator criteria.
- `ext4_mb_regular_allocator()` coordinates goal-first search, criteria progression, best-found fallback, and retry after lost races.
- `ext4_mb_use_preallocated()` searches inode PA rbtrees and locality-group PA lists before buddy allocation.
- `ext4_mb_mark_context()` updates allocation bitmap bits, group/flex counters, and checksums under optional journaling.
- `ext4_mb_clear_bb()` and `ext4_free_blocks()` validate and free ranges, defer reuse when journaling requires it, and update quota/free-cluster accounting.
- `ext4_process_freed_data()` makes committed freed extents available in buddy state and optionally queues discard.
- `ext4_trim_fs()` implements FITRIM by walking free extents and issuing discard.
- `ext4_mballoc_query_range()` reports free extents through callbacks.

## Dependencies

Includes `ext4_jbd2.h`, `mballoc.h`, tracepoints, KUnit stubs, slab/page-cache helpers, block discard APIs, freezer checks, and xarray/list/rbtree facilities. It depends on ext4 bitmap loading, group descriptors, quota APIs, JBD2, flex_bg counters, and fast-commit replay checks.

## Important Invariants

Buddy state represents on-disk allocated clusters plus active preallocation clusters. Group locks protect buddy/group-info mutation; PA locks protect descriptor state. Bitmap folios are pinned until selected buddy extents are committed to on-disk bitmaps. Deferred freed metadata is not returned to reusable buddy space until the relevant journal transaction commits. Bigalloc operations are cluster-based internally.

## Research Notes

This is ext4's central allocator. Its correctness comes from keeping on-disk bitmap state, in-core buddy state, and preallocation descriptors coherent while still allowing high concurrency.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc.h

## Purpose

Defines private data structures, defaults, helpers, and test declarations for ext4's multiblock allocator.

## Main Responsibilities

- Provide allocator tuning defaults for scan lengths, stream thresholds, order-2 requests, group preallocation, linear scanning, and best-available trimming.
- Define pending freed extents, preallocation descriptors, free extents, locality groups, allocation contexts, and loaded buddy handles.
- Define inode-specific and group/locality PA types.
- Provide helpers for group-offset conversion and logical end calculations.
- Declare free-space query and bitmap-marking APIs.
- Expose KUnit test wrappers when enabled.

## Key Structures

- `struct ext4_free_data` describes clusters freed by a transaction but not yet available for reuse.
- `struct ext4_prealloc_space` describes reserved clusters linked into inode or locality-group structures plus a block group list.
- `struct ext4_free_extent` describes candidate or selected free extents in cluster units.
- `struct ext4_locality_group` stores per-CPU locality PA buckets.
- `struct ext4_allocation_context` carries original, goal, best, and final allocation state plus scan and PA resources.
- `struct ext4_buddy` packages loaded buddy bitmap state for one group.

## Important Interfaces

- `ext4_grp_offs_to_block()` converts group/cluster offsets to physical blocks.
- `extent_logical_end()` and `pa_logical_end()` compute logical range ends with overflow-safe type width.
- `ext4_mballoc_query_range()` iterates free extents in a block group.
- `ext4_mb_mark_context()` marks allocation bitmap state and updates counters/checksums.

## Research Notes

The header makes the allocator's unit split explicit: free extents and PA lengths are in clusters, while public block interfaces often convert to filesystem blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mballoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/migrate.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/migrate.c

## Purpose

Implements ext4 inode block-mapping migration between legacy indirect-block mappings and extent mappings.

## Main Responsibilities

- Walk direct, indirect, double-indirect, and triple-indirect block maps and coalesce contiguous physical blocks into extents.
- Insert generated extents into a temporary extent inode while managing journal credits.
- Swap generated extent metadata into the original inode while detecting concurrent allocations.
- Free obsolete indirect metadata after successful indirect-to-extent conversion.
- Free temporary extent metadata after failures.
- Convert simple extent inodes back to direct block pointers when supported.
- Mark migration transactions fast-commit ineligible.

## Key Operations

- `finish_range()` converts the accumulated contiguous logical/physical range into an extent and inserts it into the temporary inode.
- `update_extent_range()` extends or flushes migration runs.
- `update_ind_extent_range()`, `update_dind_extent_range()`, and `update_tind_extent_range()` read indirect blocks and feed data blocks into the extent builder.
- `free_dind_blocks()`, `free_tind_blocks()`, and `free_ind_block()` recursively free indirect metadata.
- `ext4_ext_swap_inode_data()` verifies migration state, sets `EXT4_INODE_EXTENTS`, copies extent-root data, adjusts `i_blocks`, frees old indirect metadata, and marks the inode dirty.
- `ext4_ext_migrate()` is the main indirect-to-extent path using a hidden temporary inode with matching checksum seed.
- `ext4_ind_migrate()` converts only a single root-level extent that fits within direct pointers.

## Important Invariants

`EXT4_STATE_EXT_MIGRATE` detects racing allocations. The temporary inode uses the original inode's checksum seed so generated extent metadata remains valid after copying. Extent-to-indirect migration is intentionally narrow: no bigalloc, depth zero, at most one extent, and direct-pointer capacity only.

## Research Notes

The indirect-to-extent path avoids in-place transformation by building the target tree in a temporary inode, then swapping root mapping data under `i_data_sem`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/migrate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mmp.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/mmp.c

## Purpose

Implements ext4 Multiple Mount Protection. MMP uses a dedicated on-disk block with sequence, timestamp, node, device, interval, and checksum fields to detect whether a filesystem is already active elsewhere.

## Main Responsibilities

- Compute, verify, and set MMP checksums when metadata checksums are enabled.
- Read the MMP block directly from disk and validate magic/checksum.
- Write MMP updates synchronously with metadata-priority I/O.
- Start and stop the `kmmpd` thread that refreshes MMP state.
- Detect competing mounts or fsck activity during mount-time checks.
- Log diagnostic information about the last updater on failure.

## Key Operations

- `ext4_mmp_csum*()` handles checksum calculation, verification, and storage.
- `write_mmp_block_thawed()` writes the MMP buffer with synchronous metadata-priority I/O.
- `read_mmp_block()` forces a fresh read, validates magic, verifies checksum, and warns on failure.
- `kmmpd()` periodically increments/writes the sequence, updates time/node/check interval, verifies delayed updates, and writes `EXT4_MMP_SEQ_CLEAN` on clean shutdown.
- `ext4_multi_mount_protect()` validates the MMP block, waits and rereads active-looking state, rejects fsck activity, writes a new random sequence, verifies it stayed unchanged, records device name, and starts `kmmpd`.

## Important Invariants

The MMP block must be inside filesystem bounds. Mount proceeds only if the observed sequence is clean or remains unchanged across the wait/check cycle. `EXT4_MMP_SEQ_FSCK` causes `-EBUSY`. If `kmmpd` observes a changed sequence or node after excessive delay, it treats the filesystem as multiply mounted and aborts.

## Research Notes

MMP is intentionally conservative and time-based, using direct synchronous reads/writes plus wait/recheck logic to distinguish stale state from another active node.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/mmp.c -->