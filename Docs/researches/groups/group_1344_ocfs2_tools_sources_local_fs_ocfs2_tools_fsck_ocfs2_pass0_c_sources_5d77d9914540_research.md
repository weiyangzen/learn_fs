# Group Research: group_1344_ocfs2_tools_sources_local_fs_ocfs2_tools_fsck_ocfs2_pass0_c_sources_5d77d9914540

Scope: `Docs/research_subset_a.md`; source tree `sources/local-fs/ocfs2-tools` is included in subset A.

Read coverage: complete read of all listed files, 9,279 total source lines.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass0.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass0.c

Purpose: implements fsck pass 0 for OCFS2, validating and repairing the structural linkage of cluster, inode, and extent block chain allocators before later passes rely on allocator iteration.

Read coverage: complete file read, 1,573 lines.

Key responsibilities:
- Verifies global bitmap chain allocator descriptors, including the special rule that cluster bitmap group descriptors live at predictable block offsets.
- Verifies global and per-slot inode allocation chains, then loads their cached chain allocator state into `ost_global_inode_alloc` and `ost_inode_allocs` for pass 1.
- Verifies per-slot extent allocation chains.
- Repairs group descriptor metadata: generation, parent dinode, recorded block number, chain number, free-bit counts, discontiguous group extent-list fields, and chain/inode aggregate counts.
- Detects bad chain links, out-of-range group references, invalid descriptor magic/generation, duplicate descriptors, and loops; can truncate a chain or break loops.
- Reinitializes and relinks expected global bitmap descriptors that are missing from their chains.
- Handles global bitmap size disagreements with the superblock after failed resize-like operations and reinitializes fsck state if the user chooses to trust the repaired global bitmap.

Important entry points:
- `o2fsck_pass0()` runs pass 0a, 0b, and 0c.
- `verify_bitmap_descs()` checks predictable global bitmap descriptors and reconciles allowed/forbidden descriptor bitmaps.
- `verify_chain_alloc()` validates generic chain allocator inodes.
- `check_chain()` walks one chain record and repairs or truncates damaged links.
- `repair_group_desc()`, `check_discontig_bg()`, and `unlink_group_desc()` perform descriptor-level repair.
- `maybe_fix_clusters_per_group()` fixes an old mkfs edge case for single-group global bitmaps.
- `break_loop()` severs group descriptor cycles.

Dependencies:
- Uses libocfs2 chain allocator, group descriptor, bitmap, system inode, cached inode, and block/cluster conversion APIs.
- Uses fsck state bitmaps to mark allocator metadata clusters as in use.
- Uses `prompt()` problem codes for all user-authorized repairs and resource tracking helpers from `util.c`.

Risk and edge cases:
- Later passes assume pass 0 left allocator chains iterable; unrepaired damage can abort the fsck run.
- Global bitmap repair can change `fs_clusters` and force `o2fsck_state_reinit()`, requiring a retry of bitmap descriptor scanning.
- `unlink_group_desc()` updates allocator counts after unlinking a descriptor and comments note rollback would be difficult if the inode write fails.
- Discontiguous block group repair must decide between correcting a single bad extent length and dropping the entire group when the extent list is inconsistent.
- If `cl_next_free_rec` is not trusted, empty chain removal is refused because shifting records would be unsafe.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass0.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1.c

Purpose: implements fsck pass 1, scanning all discoverable inodes, validating inode fields and extent-backed data, building in-memory accounting for links/directories/files/clusters, and reconciling inode and cluster allocation bitmaps.

Read coverage: complete file read, 1,572 lines.

Key responsibilities:
- Scans inodes with `ocfs2_open_inode_scan()` / `ocfs2_get_next_inode()`.
- Validates active inode basics: generation, `i_blkno`, root directory type, `i_dtime`, inline-data/refcount feature compatibility, type counters, link-count bookkeeping, local allocs, and truncate logs.
- Tracks directory inodes, regular inodes, directory parent state, link counts from inodes, directory blocks, file type counts, inline counts, tree depth counts, reflink counts, and duplicate cluster discovery.
- Validates symlink target storage, including fast symlink inline data, slow symlink NUL termination, target length, and `i_size`.
- Checks extent trees and directory index trees, marking metadata/data clusters through extent helpers and scheduling corrupt directory indexes for reset.
- Marks local alloc reserved clusters and truncate-log clusters as allocated so global allocation reconciliation preserves recoverable state.
- Reconciles global cluster bitmap against `ost_allocated_clusters`, including backup superblock exceptions.
- Writes corrected inode allocator bitmaps if inode validity differs from allocator chain state.

Important entry points:
- `o2fsck_pass1()` is the pass driver.
- `o2fsck_verify_inode_fields()` validates and classifies each dinode.
- `o2fsck_check_blocks()` validates file data, directory blocks, inline data, sparse/non-sparse size and cluster counts.
- `verify_local_alloc()` and `verify_truncate_log()` validate slot-local recovery structures.
- `mark_local_allocs()` and `mark_truncate_logs()` preserve allocated accounting for unreplayed recovery metadata.
- `write_cluster_alloc()` and `write_inode_alloc()` commit allocator reconciliation.
- `o2fsck_free_inode_allocs()` releases cached inode allocators created by pass 0.

Dependencies:
- Uses pass 0 cached inode allocators, directory block and parent trackers, inode-count maps, extent checking, xattr checking, refcount checking, libocfs2 inode scans, block iteration, chain allocator APIs, and backup superblock helpers.

Risk and edge cases:
- Invalid inodes are cleared by dropping `OCFS2_VALID_FL`, but comments note full freeing of attached data is incomplete.
- Duplicate cluster detection lazily allocates `ost_duplicate_clusters`; if allocation fails, fsck aborts via signal.
- For sparse files, `i_size` may legitimately exceed allocated extents; the code only corrects sizes smaller than visible data.
- Directory index corruption can be reset for later rebuild; inline directories are handled as directory blocks at the inode block itself.
- Local allocs and truncate logs are not fully replayed here; they are accounted as allocated and handled later/recovery-aware.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1b.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1b.c

Purpose: implements extra fsck passes 1B through 1D, invoked when pass 1 found clusters claimed by more than one object; it discovers ownership, names affected inodes, and repairs duplicate claims by refcount conversion, cloning, or deletion.

Read coverage: complete file read, 1,615 lines.

Key responsibilities:
- Pass 1B rescans valid inodes and records owners of clusters present in `ost_duplicate_clusters`.
- Tracks duplicate clusters in an rbtree keyed by physical cluster and duplicate inodes in an rbtree keyed by inode block.
- Handles duplicate ownership in normal extent trees, chain allocator group descriptors, discontiguous block groups, inline/external xattrs, xattr trees, and xattr buckets.
- Pass 1C walks root and system directory trees to attach paths to duplicate-owning inodes for user-facing repair prompts.
- Pass 1D reports duplicate clusters and first attempts to turn shared data into proper refcounted extents when refcount-tree support makes that safe.
- If refcount conversion is not possible or declined, repairs duplicate claims by cloning file data to a new inode, swapping extent trees, deleting the temporary clone, or deleting the original inode.
- Prevents deletion of system files and refuses clone/delete repair of chain allocator inodes.

Important entry points:
- `ocfs2_pass1_dups()` orchestrates 1B, 1C, and 1D and frees duplicate tracking structures.
- `o2fsck_pass1b()` performs the duplicate owner rescan.
- `pass1b_process_inode()` routes inode-owned storage through extent, chain, and xattr processors.
- `o2fsck_pass1c()` names duplicate inodes by directory traversal.
- `o2fsck_pass1d()` performs user-driven repair.
- `o2fsck_create_refcount()` creates or attaches refcount trees and marks shared extents refcounted.
- `clone_one_inode()`, `new_clone()`, `copy_clone()`, `swap_clone()`, and `delete_one_inode()` implement clone/delete repair.

Dependencies:
- Uses `ost_duplicate_clusters` from pass 1, libocfs2 extent/xattr/chain iteration, cached inode I/O, file read/write, allocation, truncation, delete, and refcount APIs.
- Uses kernel rbtree/list compatibility headers, directory iteration, inode count maps, and prompt problem codes.

Risk and edge cases:
- These passes are explicitly expensive and avoid relying on the I/O cache as heavily as pass 1.
- Clone repair intentionally does not link the temporary clone into the orphan directory because during the process it may temporarily point at multiply claimed clusters.
- If fsck crashes between clone inode and original inode writes, comments describe the next fsck as able to recover by detecting the remaining duplicate/unreferenced state.
- Refcount conversion is only attempted when all owners are non-system files and either share the same refcount tree or have none.
- Chain allocators with duplicate clusters cannot be cloned or deleted; fsck only warns that the filesystem may need read-only data evacuation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass1b.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass2.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass2.c

Purpose: implements fsck pass 2, iterating directory blocks discovered by pass 1, repairing directory entry structure/content, counting directory-entry references, and building parent linkage for pass 3.

Read coverage: complete file read, 1,049 lines.

Key responsibilities:
- Tests directory entry inode targets for allocation and range validity.
- Validates and repairs `.` and `..` entries, including inline-directory offsets and parent tracking.
- Repairs directory block trailer compatibility fields, block number, and parent inode fields.
- Detects and repairs corrupt `rec_len` / `name_len` combinations enough to continue scanning, or wipes the rest of an unsafe block into a deleted entry.
- Clears zero-length names, invalid inode references, and duplicate parent claims for subdirectories.
- Replaces invalid slash/NUL name characters with dots.
- Synchronizes dirent `file_type` with the referenced inode type.
- Detects duplicate names within bounded in-memory windows and renames duplicates by adding/replacing underscores.
- Checks indexed directory lookup consistency, schedules index rebuilds, and truncates invalid index trees on filesystems without indexed-dir support.
- Optionally compresses directory entries by moving live entries forward.

Important entry points:
- `o2fsck_pass2()` allocates buffers, initializes duplicate-name tracking, seeds root/system parent records, iterates directory blocks, and rebuilds marked indexed dirs.
- `pass2_dir_block_iterate()` is the main per-directory-block callback.
- `fix_dirent_dots()`, `fix_dirent_lengths()`, `fix_dirent_name()`, `fix_dirent_inode()`, `fix_dirent_filetype()`, `fix_dirent_linkage()`, `fix_dirent_dups()`, and `fix_dirent_index()` perform individual repair classes.
- `release_re_idx_dirs_rbtree()` frees rebuild-tracking entries.
- `o2fsck_test_inode_allocated()` wraps allocation tests with conservative fallback.

Dependencies:
- Uses directory block tracking from pass 1, dir-parent rbtrees, icount maps, the string rbtree helper from `strings.c`, libocfs2 directory read/write/lookup/index APIs, and prompt problem codes.

Risk and edge cases:
- Duplicate-name detection is intentionally bounded; when the string rbtree exceeds 4 MiB it is reset, so it does not guarantee whole-directory duplicate detection.
- If a dirent’s length fields are too corrupt to trust, the code wipes the remaining block area rather than risk parsing filename bytes as entries.
- Inline directory blocks are repaired by copying the whole inode block image and writing the inode.
- Indexed directory repair is deferred by recording directories for rebuild after block iteration.
- `o2fsck_test_inode_allocated()` treats allocation-test errors as allocated to avoid cascading destructive repairs from uncertain state.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass3.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass3.c

Purpose: implements fsck pass 3, ensuring directory tree connectivity, recreating root or `/lost+found` when needed, reconnecting disconnected directories/files, and fixing inconsistent `..` entries.

Read coverage: complete file read, 448 lines.

Key responsibilities:
- Verifies that the superblock root inode is allocated and a directory; can create a new root directory and update the primary superblock.
- Ensures `/lost+found` exists under root, creating and linking it if needed.
- Reconnects orphaned files or directories into `/lost+found` with names of the form `#<inode>`.
- Walks directory parent records built in pass 2 to mark connected directories, detect cycles, and graft disconnected subtrees into `/lost+found`.
- Repairs `..` dirents when recorded parent dirent and on-disk `..` disagree.
- Special-cases orphan directory members, adjusting in-memory link accounting because orphan dirs do not necessarily update child `..` entries.

Important entry points:
- `o2fsck_pass3()` is the pass driver.
- `check_root()` validates or recreates root.
- `check_lostfound()` validates or creates `/lost+found`.
- `o2fsck_reconnect_file()` links an inode into `/lost+found`.
- `connect_directory()` walks parent chains and handles disconnected/cyclic directory trees.
- `fix_dot_dot()` and `fix_dot_dot_dirent()` update `..` directory entries and link counts.

Dependencies:
- Uses dir-parent state from passes 1/2, inode count maps, libocfs2 inode allocation, directory initialization, link, lookup, delete, superblock write, and directory iteration APIs.

Risk and edge cases:
- Creating a new root updates both `fs_root_blkno` and superblock `s_root_blkno`; failure rolls back the in-memory value and deletes the newly allocated inode.
- `/lost+found` creation must update icount and dir-parent state because pass 2 already completed directory scanning.
- Cycle detection uses a monotonically increasing `loop_no` per parent-chain walk.
- `fix_dot_dot()` logs but does not fully mark the filesystem invalid if it cannot find a `..` entry.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass4.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass4.c

Purpose: implements fsck pass 4, replaying orphan directories and reconciling inode link counts with directory-entry reference counts.

Read coverage: complete file read, 371 lines.

Key responsibilities:
- Pass 4a iterates all slot orphan directories, truncating orphan inode contents, deleting normal orphan inodes, and clearing orphan dirents.
- Preserves DIO orphan inodes from deletion while still truncating their orphaned state.
- Creates missing orphan directories during normal pass 4 when they are absent, commonly after failed slot removal.
- Updates in-memory inode/link reference accounting when orphan entries are replayed during a forced check.
- Pass 4b walks the union of inodes seen in directory references and in inode link counts, reconnecting unreferenced inodes to `/lost+found` and correcting `i_links_count`.

Important entry points:
- `o2fsck_pass4()` runs orphan replay and link-count reconciliation.
- `replay_orphan_dir()` is shared by pass 4 and slot recovery.
- `replay_orphan_iterate()` handles each orphan dirent.
- `create_orphan_dir()` recreates missing slot orphan dirs.
- `check_link_counts()` compares `ost_icount_refs` and `ost_icount_in_inodes`.
- `next_inode_any_ref()` merges iteration over both icount maps.

Dependencies:
- Uses pass 3 reconnection, inode-count maps, libocfs2 orphan directory naming, lookup, dir iteration, truncate, delete inode, new system inode, init dir, link, and inode write APIs.

Risk and edge cases:
- In read-only/no-write mode, orphan replay is skipped and directory iteration aborts.
- During slot recovery, orphan directory errors are returned to force a full check; during pass 4, missing orphan dirs can be repaired.
- Orphaned directories affect both child and parent link counts, so replay has type-specific icount deltas.
- Link-count repair depends on pass 2 having cleared invalid directory references.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass5.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass5.c

Purpose: implements fsck pass 5, validating global quota files enough to preserve quota limits, recomputing quota usage from the repaired filesystem, and recreating global/local quota files.

Read coverage: complete file read, 541 lines.

Key responsibilities:
- Checks whether user and/or group quota ro-compat features are enabled.
- Initializes quota info for each enabled quota type and reads global quota metadata.
- Validates quota header magic/version, quota file block counts, free block references, free entry references, and metadata ECC.
- Recursively scans quota tree blocks and leaf data blocks, ignoring invalid or duplicate references.
- Extracts quota limits into quota hash tables, prompting on duplicate or corrupted quota structures.
- Resets current inode/space usage fields before recomputing actual usage.
- Runs `ocfs2_compute_quota_usage()` and, if writable, truncates and recreates quota files with rebuilt usage and preserved limits.
- Initializes local quota files after rebuilding global quota files.

Important entry points:
- `o2fsck_pass5()` is the pass driver.
- `load_quota_file()` initializes quota info, allocates quota block bitmap, and scans the quota tree.
- `o2fsck_check_info()` validates quota info block and sets default grace/sync values if needed.
- `o2fsck_check_tree_blk()` recursively walks quota tree references.
- `o2fsck_check_data_blk()` validates and imports quota entries.
- `recreate_quota_files()` truncates and rebuilds quota files.
- `truncate_cached_inode()` zeros/truncates cached quota inode data.

Dependencies:
- Uses libocfs2 quota hash, quota file, quota format swap, file read, ECC, quota usage computation, truncate, and initialization APIs.
- Uses `qbmp` bitmaps to avoid rescanning quota blocks and `qhash` to preserve per-id quota limits.

Risk and edge cases:
- Node-local quota files are not checked for limits; comments state they are discarded/reinitialized.
- Corrupt quota metadata can still be scanned if the user chooses to trust referenced content.
- Quota file block counts are capped at 32-bit maximum when copied into quota info.
- On errors, cleanup iterates quota hashes and releases cached dquots.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/problem.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/problem.c

Purpose: implements fsck user prompting, including interactive single-character input, defaults, non-interactive answers, and abort handling.

Read coverage: complete file read, 165 lines.

Key responsibilities:
- Prints a problem code tag and caller-provided repair question.
- Applies non-interactive answers from fsck state when `ost_ask` is disabled.
- Displays default yes/no hints based on `PY` / `PN` flags.
- Reads one terminal character with canonical mode and echo disabled.
- Treats Ctrl-C and Escape as cancellation, exiting with fsck error/canceled status.
- Accepts space or newline as the configured default answer.

Important entry points:
- `prompt_input()` is the exported prompting implementation behind problem prompts.
- `read_a_char()` sets terminal mode and reads a single character.
- `handle_sigint()` records interrupt state for the input loop.

Dependencies:
- Uses POSIX `termios`, `sigaction`, `read`, `tolower`, and fsck state flags from `problem.h` / `fsck.h`.

Risk and edge cases:
- `read_a_char()` installs a one-shot SIGINT handler and restores terminal settings after the read.
- If both default-yes and default-no flags are supplied, default-yes is cleared.
- The file comments call out missing persistent answers for repeated identical questions.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/problem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/refcount.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/refcount.c

Purpose: validates and repairs OCFS2 refcount trees and reconciles refcount records with refcounted extents discovered in files during pass 1.

Read coverage: complete file read, 1,098 lines.

Key responsibilities:
- Validates refcount block headers, generation, `rf_blkno`, parent/root fields, extent tree layout, record list counts, used counts, ordering, and cluster ranges.
- Builds an rbtree of refcount trees keyed by root block and tracks files attached to each tree.
- Records every refcounted extent encountered by pass 1 into per-file rbtrees.
- Removes invalid leaf refcount blocks from tree extent records when possible.
- Clears invalid refcount roots from inodes and removes `OCFS2_HAS_REFCOUNT_FL` when accepted by the user.
- Compares each physical cluster range claimed by refcounted file extents against corresponding refcount records.
- Updates refcount records to the actual number of files, removes redundant records, clears refcount flags, punches holes in refcount trees, or falls back to duplicate-cluster handling when repairs are declined.
- Marks refcounted clusters allocated so global allocation reconciliation sees shared physical clusters.

Important entry points:
- `o2fsck_check_refcount_tree()` validates and registers a file’s refcount tree during inode scanning.
- `o2fsck_mark_clusters_refcounted()` records refcounted extents from extent checking.
- `o2fsck_check_mark_refcounted_clusters()` performs final refcount reconciliation and frees all tracking structures.
- `check_rb()` validates a refcount block or refcount-tree block.
- `check_rl()` validates refcount record lists.
- `o2fsck_check_refcount()` reconciles one tree.
- `o2fsck_check_refcount_clusters()` and `o2fsck_check_clusters_in_refcount()` compare discovered extents to records.
- `o2fsck_remove_refcount_range()`, `o2fsck_refcount_punch_hole()`, `o2fsck_change_refcount()`, and `o2fsck_clear_refcount()` perform repair operations.

Dependencies:
- Uses libocfs2 refcount block read/write, refcount get/change/punch-hole, refcount flag manipulation, extent-list checking, cluster bitmaps, rbtree/list compatibility headers, and prompt problem codes.
- Cooperates with `extent.c` through `o2fsck_mark_clusters_refcounted()` callbacks and with pass 1 duplicate cluster tracking.

Risk and edge cases:
- The code allows an empty root refcount block but can invalidate empty non-root leaves.
- Refcount records must be monotonic by cluster; collisions or out-of-range references can be removed only if `rl_used` is trusted.
- When discovered refcount does not match the number of files and the user declines correction, clusters are marked duplicate and refcount metadata is removed/cleared to let duplicate repair handle them.
- Several internal assumptions are enforced with `assert()`, including prior tree/file registration and non-overlapping extent tuples.
- Root and leaf buffers are reread after libocfs2 refcount mutations because tree structure may change.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/slot_recovery.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/slot_recovery.c

Purpose: implements slot recovery helpers for fsck, replaying per-slot truncate logs, local alloc windows, and orphan directories before or during full checking.

Read coverage: complete file read, 205 lines.

Key responsibilities:
- Replays truncate logs by verifying all referenced clusters are allocated, freeing them, clearing log records, and writing the truncate log inode.
- Replays local allocs by freeing clear bits still reserved in the global bitmap, then clearing local alloc inode state.
- Replays orphan directories through shared pass 4 orphan replay logic, then resets orphan directory link counts to 2.
- Applies recovery callbacks to each per-slot system file via `handle_slots_system_file()`.

Important entry points:
- `o2fsck_replay_truncate_logs()`
- `o2fsck_replay_local_allocs()`
- `o2fsck_replay_orphan_dirs()`
- Internal callbacks: `ocfs2_clear_truncate_log()`, `ocfs2_clear_local_alloc()`, and `ocfs2_clear_link_count()`.

Dependencies:
- Uses libocfs2 cluster test/free, inode write, local alloc sizing, truncate-log sizing, and per-slot system inode lookup through `util.c`.
- Calls `replay_orphan_dir()` from `pass4.c`.

Risk and edge cases:
- Each recovery callback validates expected system inode flags and returns invalid-argument/internal errors on unexpected metadata.
- Local alloc replay verifies clusters are still allocated before freeing; missing bits become `OCFS2_ET_INVALID_BIT`.
- Orphan directory replay returns errors during slot recovery to trigger broader fsck handling.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/slot_recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/strings.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/strings.c

Purpose: provides a small rbtree-backed string set used by pass 2 to detect duplicate directory entry names.

Read coverage: complete file read, 149 lines.

Key responsibilities:
- Stores variable-length strings in an rbtree ordered by length first and then byte comparison.
- Checks whether a string already exists without insertion.
- Inserts a string and optionally reports whether it was already present.
- Tracks approximate allocated bytes so pass 2 can bound memory use.
- Frees all string entries and resets allocation accounting.

Important entry points:
- `o2fsck_strings_init()`
- `o2fsck_strings_insert()`
- `o2fsck_strings_exists()`
- `o2fsck_strings_free()`
- `o2fsck_strings_bytes_allocated()`

Dependencies:
- Uses libocfs2/kernel rbtree types exposed through fsck headers and standard `malloc`/`free`.

Risk and edge cases:
- Ordering is not lexicographic by design; it only needs a stable equality-search ordering for duplicate detection.
- Stored strings are compared by explicit length and bytes. The comment says “null terminated,” but allocation/copying stores exactly the supplied bytes; current callers do not rely on a terminator for stored entries.
- `o2fsck_strings_init()` sets the root but does not explicitly zero `s_allocated`; callers should use freshly initialized storage or ensure the field is clear.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/util.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/util.c

Purpose: provides shared fsck helpers for inode writing, cluster allocation accounting, inode type lookup, per-slot system file iteration, resource statistics, I/O cache sizing, bitmap wrappers, and emergency abort.

Read coverage: complete file read, 493 lines.

Key responsibilities:
- Wraps inode writes with `i_blkno` sanity checking and fsck error-state updates.
- Marks clusters allocated/unallocated in fsck’s in-memory allocation bitmap and creates the duplicate-cluster bitmap on first collision.
- Counts bits in byte arrays for group descriptor free-bit validation.
- Reads an inode to map mode bits to OCFS2 directory entry file type.
- Iterates all slots for a given system inode type and applies a callback.
- Tracks per-pass wall/user/system time and I/O/cache statistics, then aggregates and prints optional stats.
- Initializes libocfs2 I/O cache based on requested cache mode, available memory, filesystem size, and journal estimates.
- Provides bounded pre-cache accounting with `o2fsck_worth_caching()` and `o2fsck_reset_blocks_cached()`.
- Wraps bitmap set/clear failures as fatal fsck aborts.
- Aborts by sending SIGTERM to the current process so fsck signal handlers can clean up.

Important entry points:
- `o2fsck_write_inode()`
- `o2fsck_mark_cluster_allocated()`, `o2fsck_mark_clusters_allocated()`, `o2fsck_mark_cluster_unallocated()`
- `o2fsck_type_from_dinode()`
- `o2fsck_bitcount()`
- `handle_slots_system_file()`
- `o2fsck_init_resource_track()`, `o2fsck_compute_resource_track()`, `o2fsck_add_resource_track()`, `o2fsck_print_resource_track()`
- `o2fsck_init_cache()`, `o2fsck_worth_caching()`, `o2fsck_reset_blocks_cached()`
- `__o2fsck_bitmap_set()`, `__o2fsck_bitmap_clear()`, `o2fsck_abort()`

Dependencies:
- Uses libocfs2 bitmap, cached I/O, inode, system inode, cluster conversion, and I/O stats APIs.
- Uses POSIX `getrusage`, `gettimeofday`, `sysconf`, `getpagesize`, `kill`, and process signal handling.

Risk and edge cases:
- Duplicate cluster bitmap allocation failure aborts the process immediately because later repair depends on that tracking.
- Cache sizing intentionally limits use to a fraction of available physical pages and retries with smaller allocations.
- `o2fsck_print_resource_track()` protects against negative computed walltime but can still divide by very small elapsed time.
- Fatal bitmap wrapper errors call `o2fsck_abort()` rather than returning, so callers rely on process-level cleanup.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/util.c -->