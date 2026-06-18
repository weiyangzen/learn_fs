# Group Research: group_941_linux_stable_sources_os_linux_linux_stable_fs_binfmt_misc_c_sources__46b6f2e947af

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_misc.c -->
# File Research: sources/os/linux/linux-stable/fs/binfmt_misc.c

## Summary
Implements Linux `binfmt_misc`: a user-namespace-aware pseudo-filesystem and binary-format loader that matches executables by extension or magic bytes and runs a registered interpreter/wrapper.

## Main Responsibilities
- Registers the `binfmt_misc` filesystem and `linux_binfmt` handler.
- Maintains per-user-namespace handler lists, falling back to ancestor namespaces.
- Parses register strings of the form `:name:type:offset:magic:mask:interpreter:flags`.
- Exposes `/status`, `/register`, and per-entry files.
- Enables, disables, or deletes one handler or all handlers through file writes.
- Rewrites `linux_binprm` argv/interpreter state for matched binaries.
- Supports special flags: preserve argv0, open binary, credentials, and pre-open interpreter file.

## Important Behavior
`load_misc_binary()` finds the active namespace handler, rejects inaccessible script paths, optionally preserves argv0, pushes the target binary path and interpreter onto the argument stack, changes `bprm->interp`, opens or clones the interpreter file, and sets `execfd_creds` for credential-preserving handlers.

`create_entry()` validates and decodes registration input. Magic handlers parse an offset, hex-escaped magic, optional mask, and reject matches beyond `BINPRM_BUF_SIZE`. Extension handlers match the suffix after the last dot in `bprm->interp`.

The filesystem instance is lazily allocated per user namespace in `bm_fill_super()`. `load_binfmt_misc()` walks from current user namespace to ancestors, using release/acquire ordering with `bm_fill_super()` so child namespaces without their own mount can use parent handlers.

Handler lifetime is protected by `entries_lock`, the root inode lock for structural updates, dentries for pseudo-files, and a `users` refcount so removal can race safely with `load_misc_binary()`.

## Risks
Registration parsing is delimiter-sensitive and accepts escaped binary bytes, so bounds checks around `MAX_REGISTER_LENGTH`, decoded magic length, and buffer padding are critical. `MISC_FMT_OPEN_FILE` pins an interpreter file and must close it exactly once. Removal relies on list deletion plus recursive dentry removal plus inode eviction, so refcount ownership must remain balanced.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_script.c -->
# File Research: sources/os/linux/linux-stable/fs/binfmt_script.c

## Summary
Implements the kernel `#!` script binary loader. It parses the first line of a script, prepares interpreter arguments, and restarts exec with the interpreter file.

## Main Responsibilities
- Detects scripts whose first two bytes are `#!`.
- Parses interpreter path and optional single argument from `bprm->buf`.
- Rejects truncated interpreter paths.
- Replaces original `argv[0]` with script filename and interpreter argv.
- Opens the interpreter with `open_exec()`.
- Registers and unregisters the script `linux_binfmt`.

## Important Behavior
The parser does not assume `bprm->buf` is NUL-terminated. If no newline is present, it requires a terminator after the interpreter path so the path is not silently truncated. Truncated interpreter arguments are tolerated because interpreters can re-read the script.

The argument stack is rebuilt in reverse order: script path, optional interpreter argument, interpreter name. `bprm_change_interp()` records the interpreter path before `open_exec()` installs the interpreter file.

## Risks
The path-inaccessible check rejects `/dev/fd`-style scripts that would disappear after exec. Correct shebang parsing depends on distinguishing interpreter path truncation from argument truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/binfmt_script.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bpf_fs_kfuncs.c -->
# File Research: sources/os/linux/linux-stable/fs/bpf_fs_kfuncs.c

## Summary
Exports filesystem-related BPF kfuncs for BPF LSM programs: file reference management, path formatting, restricted xattr reads/writes, and cgroupfs xattr reads.

## Main Responsibilities
- Provides `bpf_get_task_exe_file()` / `bpf_put_file()` with verifier acquire/release metadata.
- Provides `bpf_path_d_path()` as a safer pathname resolver.
- Allows BPF LSM reads of `user.*` and `security.bpf.*` xattrs.
- Allows BPF LSM writes/removals only for `security.bpf.*` xattrs.
- Handles locked and unlocked dentry xattr variants.
- Registers BTF kfunc IDs and filters them to BPF LSM programs.

## Important Behavior
Dynptr xattr buffers are validated through kernel dynptr helpers before VFS xattr calls. Write helpers use `inode_permission()` and `__vfs_setxattr()` / `__vfs_removexattr()`, notify fsnotify on success, and intentionally skip LSM post hooks to avoid recursive BPF LSM deadlocks.

`bpf_lsm_has_d_inode_locked()` checks the attach target against a BTF set of LSM hooks whose inode is already locked, allowing callers to choose locked xattr variants.

## Risks
The xattr namespace restrictions are the main security boundary. Calling the unlocked variant from an already-locked LSM hook would deadlock; calling the locked variant without the lock would violate VFS locking expectations. Acquire/release annotations for file refs must remain correct for verifier enforcement.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bpf_fs_kfuncs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/Kconfig

## Summary
Defines Btrfs kernel configuration options, dependencies, selected libraries, developer diagnostics, and experimental feature gating.

## Main Responsibilities
- Declares `BTRFS_FS` as tristate filesystem support.
- Selects compression, checksum, RAID, iomap, and block-cgroup dependencies.
- Defines optional POSIX ACL support.
- Defines module-load sanity tests.
- Defines debug and assertion options.
- Defines `BTRFS_EXPERIMENTAL` and documents experimental feature families.

## Important Behavior
`BTRFS_FS` depends on `PAGE_SIZE_LESS_THAN_256KB` and selects core implementation prerequisites such as CRC32, BLAKE2b, SHA256, zlib/lzo/zstd, RAID6/PQ, XOR, xxhash, and `FS_IOMAP`.

The experimental option gates unstable work including RAID read policy, send v3 fs-verity support, raid-stripe-tree, extent tree v2, large folios/block size, async checksums, and remap-tree.

## Risks
Kconfig selections encode build-time assumptions for the entire Btrfs module. Accidentally removing selects can produce missing symbols or disabled runtime features; enabling experimental features exposes users to intentionally unstable behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/Makefile

## Summary
Builds the Btrfs module object list and conditionally includes optional ACL, debug, zoned, verity, and test objects.

## Main Responsibilities
- Adds Btrfs-specific warning flags.
- Builds `btrfs.o` for `CONFIG_BTRFS_FS`.
- Lists core Btrfs object files.
- Includes conditional objects for ACL, ref verification, zoned devices, fs-verity, and sanity tests.

## Important Behavior
The core object list wires together filesystem entry points, trees, transactions, inode/file I/O, extent maps, compression, delayed refs/inodes, scrub, backrefs, qgroups, send, device replace, RAID56, block groups, bio handling, direct I/O, and more.

Sanity tests are compiled only with `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, with zoned tests additionally gated by `CONFIG_BLK_DEV_ZONED`.

## Risks
Object ordering and conditional compilation define which subsystems are linked into the module. Missing `acl.o`, `zoned.o`, `verity.o`, or test objects under the wrong config would create feature or symbol mismatches.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/accessors.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/accessors.c

## Summary
Implements generic little-endian get/set helpers for Btrfs extent-buffer metadata fields, including fields that span folio boundaries.

## Main Responsibilities
- Reads and writes 8/16/32/64-bit values from extent buffers.
- Handles metadata items split across two folios.
- Reports out-of-bounds member access.
- Implements `btrfs_node_key()` for reading node key pointers.

## Important Behavior
The generated helper macro computes a linear member offset, maps it to extent-buffer folio index and folio offset, validates bounds against `eb->len`, then either performs direct unaligned little-endian access or copies split bytes through a temporary buffer.

For setters, values are encoded into little-endian bytes and split back across folios when needed.

## Risks
These helpers are used throughout Btrfs metadata parsing and mutation. Incorrect split-folio handling or bounds checks would corrupt on-disk metadata or hide tree-checker problems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/accessors.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/accessors.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/accessors.h

## Summary
Declares and generates Btrfs typed accessors for on-disk structures in extent buffers and stack copies.

## Main Responsibilities
- Defines macros for extent-buffer, header, and stack get/set helpers.
- Provides endian-safe accessors for device, chunk, block group, inode, extent, node, item, dir, root, superblock, file extent, qgroup, dev replace, verity, and remap structures.
- Provides key conversion helpers between disk and CPU representations.
- Provides item pointer and item offset helpers.

## Important Behavior
`BTRFS_SETGET_FUNCS` and variants enforce field-size expectations with `static_assert()`. Little-endian builds optimize key conversion by `memcpy()`, while other builds convert objectid/offset explicitly.

Header accessors use the first extent-buffer folio and `offset_in_page(eb->start)`. Item helpers compute leaf item array offsets and data-area pointers, forming the standard typed bridge from B-tree slots to on-disk records.

## Risks
This header is a broad metadata ABI layer. Field size mismatches, wrong endian conversions, or pointer offset errors would affect many independent Btrfs subsystems. Some setters add invariants, such as sector alignment for device total bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/accessors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/acl.c

## Summary
Implements Btrfs POSIX ACL get/set operations on top of Btrfs xattrs.

## Main Responsibilities
- Reads access and default ACL xattrs.
- Converts xattr bytes to `struct posix_acl`.
- Converts ACLs to xattr bytes for storage.
- Updates cached ACLs after successful writes.
- Adjusts inode mode when setting access ACLs.

## Important Behavior
`btrfs_get_acl()` does not support RCU lookup and returns `-ECHILD` when called in RCU mode. ACL values are fetched with a size probe followed by allocation and a second `btrfs_getxattr()`.

`__btrfs_set_acl()` supports either an existing transaction or creating its own xattr transaction. ACL-to-xattr conversion runs under `memalloc_nofs_save()` because callers may hold a Btrfs transaction. Default ACLs are valid only for directories.

## Risks
On access ACL set failure, `btrfs_set_acl()` restores the old inode mode. Allocation inside a transaction must remain NOFS to avoid filesystem reclaim deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/acl.h

## Summary
Declares the Btrfs ACL interface and provides no-ACL stubs when POSIX ACL support is disabled.

## Main Responsibilities
- Exposes `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()` under `CONFIG_BTRFS_FS_POSIX_ACL`.
- Maps VFS ACL hooks to `NULL` when ACL support is disabled.
- Provides an `-EOPNOTSUPP` internal setter stub without ACL support.

## Risks
Callers that use `__btrfs_set_acl()` must handle `-EOPNOTSUPP` in non-ACL builds. Public VFS operation tables rely on `NULL` hooks to disable ACL behavior cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/async-thread.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/async-thread.c

## Summary
Implements Btrfs workqueue wrappers with dynamic concurrency throttling and ordered completion callbacks.

## Main Responsibilities
- Allocates normal and ordered Btrfs workqueues.
- Initializes and queues `btrfs_work` items.
- Tracks pending work and adjusts max active workers.
- Provides ordered work completion in queue order.
- Flushes and destroys Btrfs workqueues.

## Important Behavior
Normal workqueues can start with low concurrency and grow or shrink based on pending work thresholds. The queue hook runs in IRQ-capable context and only updates counters; the execution hook runs in worker context and may call `workqueue_set_max_active()`.

Ordered work uses a separate ordered list. The normal work function runs first, sets `WORK_DONE_BIT` with a memory barrier, and `run_ordered_work()` invokes ordered callbacks in list order. The ordered callback receives `false` for completion and later `true` for freeing.

Special care prevents freeing and recycling the currently executing work item before all ordered dependencies are complete, preserving kernel workqueue non-reentrancy assumptions.

## Risks
Ordered work correctness depends on `WORK_DONE_BIT`, `WORK_ORDER_DONE_BIT`, list locking, and memory barriers. Threshold updates are intentionally approximate but must avoid calling sleepable workqueue APIs from queue-time contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/async-thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/async-thread.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/async-thread.h

## Summary
Declares Btrfs asynchronous workqueue types and APIs.

## Main Contents
- Function pointer types for normal and ordered work.
- `struct btrfs_work`, embedding kernel work item, ordered-list node, owning Btrfs workqueue, and flags.
- Workqueue allocation, ordered allocation, initialization, queue, destroy, max-active update, owner lookup, congestion query, and flush declarations.

## Risks
`struct btrfs_work` documents that fields below callbacks are internal. Callers must not touch work internals after queueing or after callbacks that may free the work item.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/async-thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/backref.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/backref.c

## Summary
Implements Btrfs backreference walking, data-extent sharedness checks, inode/path resolution from extents, metadata backref iteration, and the backref cache used by relocation and related tree-block tracking.

## Main Responsibilities
- Finds leaves, roots, inodes, and paths that reference a logical extent.
- Merges delayed refs, inline refs, keyed refs, direct refs, and indirect refs.
- Resolves indirect refs by searching owner roots for parent blocks or file extent items.
- Determines whether a data extent is shared, with path and recent-extent caches.
- Converts logical addresses to extent items.
- Iterates tree-block backrefs in commit roots.
- Builds and maintains a bidirectional metadata backref cache of nodes and edges.

## Important Behavior
The core walk uses three preliminary-ref rbtrees: direct refs, indirect refs with keys, and indirect refs missing keys. Delayed refs are merged first when a transaction/time sequence is available. Inline and keyed refs from the extent tree are added next. Missing keys are filled by reading the referenced tree block, then indirect refs are resolved to parent bytenrs and merged into the direct tree.

For data extents, indirect refs identify inode, file offset, and root. `find_extent_in_eb()` scans file extent items in a leaf, filters by target disk byte and optionally by `extent_item_pos`, and builds inode element lists. `iterate_extent_inodes()` first finds referencing leaves, then finds all roots referencing each leaf, then invokes the caller iterator for each inode/offset/root tuple.

`btrfs_is_data_extent_shared()` short-circuits as soon as it proves sharing. It accounts for delayed add/drop refs, detects different inodes or roots, climbs parent tree blocks when sharing can come from snapshots, and caches path sharedness by tree level. It also has a small cache for recently checked data extents with multiple file extent items.

Path helpers walk `BTRFS_INODE_REF_KEY` and `BTRFS_INODE_EXTREF_KEY` items to produce filesystem-relative paths. Buffers are filled backward so callers can detect how much space was missing.

The backref iterator supports metadata backrefs in commit roots. It starts at an extent item, walks inline refs first, then keyed `TREE_BLOCK_REF` / `SHARED_BLOCK_REF` items.

The backref cache represents tree blocks as `btrfs_backref_node` objects and parent/child relationships as `btrfs_backref_edge` objects. Direct tree backrefs link to known parent bytenrs; indirect tree backrefs search the owner root to discover parents. Link finalization inserts newly discovered nodes into the cache and resolves pending edges breadth-first.

## State And Data Structures
- `extent_inode_elem` stores inode number, file offset, referenced byte count, and next pointer.
- `prelim_ref` stores root id, search key, level, ref count, inode list, parent, and wanted disk byte.
- `preftrees` separates direct, indirect, and missing-key preliminary refs.
- `share_check` tracks target inode/root, target data extent, share count, self refs, and delayed delete refs.
- `btrfs_backref_walk_ctx` carries the target bytenr, extent offset policy, transaction/time sequence, result ulists, caches, and callbacks.
- `btrfs_backref_share_check_ctx` caches path-level sharedness and recent data extent results.
- `btrfs_backref_cache`, `btrfs_backref_node`, and `btrfs_backref_edge` form the metadata backref cache.

## Risks
Backref walking is sensitive to transaction consistency. Mixing current delayed refs, tree mod log sequences, and commit-root searches incorrectly can report wrong owners or sharing. Negative delayed ref counts must merge with on-disk refs before early sharedness decisions. Inode lists are transferred between preliminary refs and ulists, so ownership must be nulled after transfer to avoid double free or use-after-free.

The backref cache has strict graph invariants: nodes must not be inserted twice, upper/lower edge lists must be symmetric after finalization, and error cleanup must walk pending edges and useless nodes without leaking or freeing cached nodes still in use.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/backref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/backref.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/backref.h

## Summary
Declares Btrfs backreference walking APIs, sharedness-check contexts, inode/path containers, metadata backref iterators, and relocation backref-cache structures.

## Main Contents
- `iterate_extent_inodes_t` callback protocol and stop code.
- `struct btrfs_backref_walk_ctx` for generic extent backref walks.
- `struct inode_fs_paths` and data-container helpers.
- `struct btrfs_backref_share_check_ctx` and caches.
- Public APIs for logical extent lookup, inode iteration, path resolution, leaf/root discovery, extref lookup, and sharedness checks.
- `struct prelim_ref` and `struct btrfs_backref_iter`.
- Backref cache node/edge/cache structures and cache management APIs.

## Important Behavior
The walk context distinguishes data extent position filtering, whole-extent matching, optional inode-list suppression, transaction versus commit-root walking, and callbacks for leaf-root caching, early indirect data iteration, extent-item checking, and data-ref skipping.

The backref cache is explicitly a bidirectional map of tree blocks and parents. Nodes track bytenr, new bytenr, owner, root, extent buffer, level, lock/processed/checked/pending/detached state, and relocation-root status. Edges link lower and upper nodes through separate list heads.

## Risks
The header exposes several multi-step protocols: allocate/init/release contexts, prepare iterator/start/next, add tree node then finish upper links, and error cleanup. Callers must preserve context fields and ownership rules expected by `backref.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/backref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/bio.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/bio.c

## Summary
Implements the Btrfs bio submission and completion layer: logical-to-physical mapping, bio splitting, mirrored/parity submission, checksum preparation and verification, endio workqueue handoff, read repair, and repair writes.

## Main Responsibilities
- Allocates and initializes `btrfs_bio` objects.
- Splits bios at mapping, segment, or zone-append boundaries.
- Maps logical ranges to devices and stripes.
- Submits single-mirror, mirrored, and RAID56 bios.
- Computes write checksums synchronously or through Btrfs workers.
- Looks up and verifies data read checksums.
- Performs read repair by trying alternate mirrors and writing repaired sectors.
- Tracks device I/O errors and per-device stats.
- Initializes and tears down bio sets and failed-bio mempool.

## Important Behavior
`btrfs_submit_bbio()` loops through chunks until the whole logical bio is mapped. `btrfs_submit_chunk()` calls `btrfs_map_block()`, saves original logical addresses for data writes, handles zone append limits, splits partial mappings, preloads checksums for data reads, and computes or schedules checksums for data writes.

Read completion for data bios runs in task context. `btrfs_check_read_bio()` verifies checksums sector by sector and starts repair reads for bad sectors. Repair reads try alternate mirrors; successful repair data is written back to earlier failed mirrors through `btrfs_repair_io_failure()`.

Mirrored writes clone bios for all but the last mirror. Completion tolerates errors up to `bioc->max_errors`; only excess errors propagate upward. RAID56 uses the RAID56 parity layer and reports completion from workqueue context.

Zone append support rewrites device bio sectors to zone starts and records physical positions after successful completion. NODATASUM zoned writes may allocate dummy checksums where the ordered path expects them.

## Risks
The original `btrfs_bio` tracks split pending I/Os and first error status; clone completion must decrement and free in the right order. Checksum ownership differs between reads, normal writes, relocation roots, NODATASUM writes, remap writes, and async checksum workers. Repair writes intentionally bypass normal mirrored submission to update only the bad copy, so mirror mapping and device lifetime protection through the bio counter are critical.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/bio.c -->