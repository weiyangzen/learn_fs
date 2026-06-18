# Group Research: group_699_linux_sources_os_linux_linux_fs_binfmt_misc_c_sources_os_linux_linux_fb33e38421d5

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`, files listed in the work item. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/binfmt_misc.c -->
# File Research: sources/os/linux/linux/fs/binfmt_misc.c

Purpose: Implements the `binfmt_misc` filesystem and binary-format loader, allowing userspace to register executable handlers by filename extension or file magic.

Main structures and state:
- `Node`: one registered handler, including list linkage, flags, magic/extension, optional mask, interpreter path, dentry, optional pinned interpreter file, and a refcount used to synchronize removal with exec.
- `struct binfmt_misc`: per-user-namespace registry reached through `user_ns->binfmt_misc`, with an enabled flag, handler list, and list rwlock.
- `misc_format`: Linux binary format registered through `insert_binfmt()`.
- `bm_fs_type`: `binfmt_misc` pseudo filesystem, mountable in user namespaces.

Execution flow:
- `load_binfmt_misc()` finds the nearest mounted `binfmt_misc` instance from the current user namespace upward, falling back to `init_binfmt_misc`.
- `search_binfmt_handler()` scans enabled entries and matches either extension or magic/mask bytes in `bprm->buf`.
- `get_binfmt_handler()` takes a refcount under `entries_lock`; `put_binfmt_handler()` closes pinned interpreter files and frees the handler when the last exec/removal user drops it.
- `load_misc_binary()` rewrites arguments for the interpreter, handles preserve-argv0/open-binary/credential flags, opens or clones the interpreter file, and stores it in `bprm->interpreter`.

Registration and control interface:
- `/register` accepts strings shaped like `:name:type:offset:magic:mask:interpreter:flags`.
- `create_entry()` validates names, parses `E` extension or `M` magic entries, decodes `\x` hex escapes, validates magic length against `BINPRM_BUF_SIZE`, and parses flags `P`, `O`, `C`, and `F`.
- `/status` accepts `0`, `1`, or `-1` to disable, enable, or clear all handlers.
- Per-entry files accept the same commands to disable, enable, or delete one handler.
- `entry_status()` reports interpreter, flags, and extension or hex-encoded magic/mask details.

Namespace and filesystem behavior:
- `bm_fill_super()` lazily allocates one `binfmt_misc` registry per user namespace and publishes it with release semantics paired with loader-side acquire reads.
- The filesystem uses `simple_fill_super()` to expose `status` and `register`; entries are persistent dentries created by `add_entry()`.
- `bm_evict_inode()` removes list entries during inode eviction and releases the handler reference.
- `remove_binfmt_handler()` removes the list entry and recursively removes the dentry.

Concurrency and safety:
- The root inode lock serializes register/remove operations, while `entries_lock` protects the handler list against concurrent exec lookup.
- Refcounting prevents a handler from being freed while `load_misc_binary()` is using it.
- `MISC_FMT_OPEN_FILE` opens the interpreter at registration time using the credentials that opened `/register`, important for unprivileged mounts.
- `BINPRM_FLAGS_PATH_INACCESSIBLE` is rejected because the interpreter must be able to access the target binary after exec.

Risk notes: This file sits on the exec path and exposes a writable control filesystem. Parser validation, namespace publication ordering, handler refcounting, and interpreter credential handling are the critical correctness and security points.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/binfmt_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/binfmt_script.c -->
# File Research: sources/os/linux/linux/fs/binfmt_script.c

Purpose: Implements the kernel `#!` script binary format handler.

Main behavior:
- `load_script()` accepts only files whose initial bytes are `#!`.
- It parses the first line of `bprm->buf` into interpreter path and optional single argument.
- It carefully handles non-NUL-terminated buffers and rejects cases where the interpreter path may be truncated.
- It permits truncated interpreter arguments because the interpreter can reopen and parse the script itself.
- It rejects execution when `BINPRM_FLAGS_PATH_INACCESSIBLE` is set, because the interpreter usually needs to open the script by path.

Argument rewriting:
- Removes the original argv[0].
- Pushes the script filename, optional interpreter argument, and interpreter path in reverse order.
- Calls `bprm_change_interp()` to update the interpreter name.
- Opens the interpreter with `open_exec()` and stores it in `bprm->interpreter`.

Registration:
- `script_format` registers `load_script` through `register_binfmt()` at `core_initcall`.
- Module exit unregisters the format.

Risk notes: The key edge cases are first-line truncation, whitespace trimming, optional argument splitting, and path-inaccessible scripts such as `/dev/fd/...` with close-on-exec descriptors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/binfmt_script.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bpf_fs_kfuncs.c -->
# File Research: sources/os/linux/linux/fs/bpf_fs_kfuncs.c

Purpose: Exposes selected filesystem operations as BPF kfuncs, primarily for BPF LSM programs.

Provided kfuncs:
- `bpf_get_task_exe_file()`: acquires a referenced `struct file *` for a task’s executable file.
- `bpf_put_file()`: releases file references acquired by BPF.
- `bpf_path_d_path()`: safer path-to-string resolver built on `d_path()`.
- `bpf_get_dentry_xattr()` and `bpf_get_file_xattr()`: read allowed xattrs into BPF dynptr buffers.
- `bpf_set_dentry_xattr()` and `bpf_remove_dentry_xattr()`: set/remove allowed BPF security xattrs with inode locking.
- `bpf_cgroup_read_xattr()`: when cgroups are enabled, reads `user.*` xattrs from cgroupfs kernfs nodes.
- `bpf_real_inode()`: resolves a dentry to its real backing inode for overlay/union filesystems.

Permission model:
- Xattr reads are limited to `user.*` and `security.bpf.*`, then checked with `inode_permission(..., MAY_READ)`.
- Xattr writes/removes are limited to `security.bpf.*`, then checked with `inode_permission(..., MAY_WRITE)`.
- Cgroup xattr reads are limited to `user.*`.

Locking and LSM integration:
- Locked helpers `bpf_set_dentry_xattr_locked()` and `bpf_remove_dentry_xattr_locked()` are provided for LSM hooks that already hold `d_inode`.
- Unlocked kfuncs take and release `inode_lock()`.
- Post-xattr security hooks are deliberately not called for BPF LSM-originated xattr changes to avoid recursive deadlocks.
- `d_inode_locked_hooks` lists BPF LSM hooks where the inode is already locked.

BTF registration:
- `BTF_KFUNCS_START(bpf_fs_kfunc_set_ids)` publishes kfuncs with flags such as `KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, and `KF_SLEEPABLE`.
- `bpf_fs_kfuncs_filter()` allows these kfuncs for BPF LSM programs and rejects other program types.
- Registration happens at `late_initcall`.

Risk notes: The security boundary is the xattr prefix filtering plus inode permissions. Dynptr size/data validation and correct locked-vs-unlocked helper selection are central to avoiding verifier, memory, and deadlock problems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bpf_fs_kfuncs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/btrfs/Kconfig

Purpose: Defines the kernel configuration surface for Btrfs.

Key options:
- `BTRFS_FS`: main tristate filesystem option. Selects block cgroup bio punting, CRC/checksum libraries, compression libraries, iomap, RAID6/XOR helpers, and xxhash. Depends on `PAGE_SIZE_LESS_THAN_256KB`.
- `BTRFS_FS_POSIX_ACL`: enables POSIX ACL support through `FS_POSIX_ACL`.
- `BTRFS_FS_RUN_SANITY_TESTS`: runs Btrfs regression/sanity tests at module load.
- `BTRFS_DEBUG`: enables expensive debugging checks, leak checks, extra sysfs debug output, forced fragmentation, and `REF_TRACKER` when stack traces are supported.
- `BTRFS_ASSERT`: enables runtime invariant assertions that may panic on violation.
- `BTRFS_EXPERIMENTAL`: gates unstable features, including COW fixup warning, mirror read policies, send stream v3 fs-verity, raid-stripe-tree, extent tree v2, large folio/block-size support, async data-write checksumming, and remap-tree.

Integration: These options directly control objects and code paths in the Btrfs Makefile and implementation files, including ACL support, debug-only ref verification, sanity tests, and experimental async checksum behavior in `bio.c`.

Risk notes: `BTRFS_EXPERIMENTAL` enables several unrelated unstable features at once, and `BTRFS_ASSERT` can intentionally panic on invariant failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/Makefile -->
# File Research: sources/os/linux/linux/fs/btrfs/Makefile

Purpose: Builds the Btrfs kernel module and applies Btrfs-local compiler warning flags.

Build behavior:
- Adds a subset of `W=1` diagnostics such as `-Wextra`, unused warnings, missing declarations/prototypes, missing format attributes, old-style definitions, and missing include dirs.
- Adds compiler-supported optional diagnostics for unused-but-set variables, unused const variables, packed alignment, string truncation, and maybe-uninitialized.
- Suppresses selected `-Wextra` warnings for missing field initializers, sign comparisons, and negative shifts.
- Builds `btrfs.o` when `CONFIG_BTRFS_FS` is enabled.

Core object list: Includes superblock, trees, extents, items, disk I/O, transactions, inode/file paths, extent maps, sysfs, accessors, xattrs, ordered data, volumes, async workers, ioctl, locking, orphan handling, export, tree-log, free-space cache/tree, compression backends, delayed refs/inodes, scrub, backrefs, qgroups, send, device replace, RAID56, UUID tree, props, tree checker, space info, block reservations, block groups, discard, reflink, subpage, tree-mod-log, fs support, messages, bio, raid-stripe-tree, fiemap, and direct I/O.

Conditional objects:
- `acl.o` under `CONFIG_BTRFS_FS_POSIX_ACL`.
- `ref-verify.o` under `CONFIG_BTRFS_DEBUG`.
- `zoned.o` under `CONFIG_BLK_DEV_ZONED`.
- `verity.o` under `CONFIG_FS_VERITY`.
- Sanity test objects under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, with zoned tests only when zoned block device support is enabled.

Integration notes: In this work item, `accessors.o`, `async-thread.o`, `backref.o`, and `bio.o` are core Btrfs objects; `acl.o` is config-gated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/accessors.c -->
# File Research: sources/os/linux/linux/fs/btrfs/accessors.c

Purpose: Implements generic low-level read/write helpers for Btrfs on-disk metadata fields stored in `extent_buffer` folios.

Main behavior:
- Generates `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()` with `DEFINE_BTRFS_SETGET_BITS`.
- Treats metadata item pointers as logical offsets into an extent buffer.
- Supports fields crossing folio boundaries, needed when metadata block size exceeds page size.
- Performs bounds checking against `eb->len`; violations are reported through `report_setget_bounds()`.
- Uses little-endian unaligned loads/stores for serialized fields.
- Implements `btrfs_node_key()` by reading a key from a node pointer slot via `read_eb_member`.

Important details:
- Cross-folio two-byte fields are copied byte by byte; wider fields use a small byte buffer and split copy.
- Writes mirror the same contiguous/cross-folio handling as reads.
- The helper assumes the extent buffer folio array represents a linear metadata address space.

Risk notes: This is foundational metadata access code. Incorrect offsets, field sizes, folio indexing, or missing bounds checks can corrupt on-disk metadata; the generated typed accessors in `accessors.h` are the main guardrail.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/accessors.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/accessors.h -->
# File Research: sources/os/linux/linux/fs/btrfs/accessors.h

Purpose: Declares and generates Btrfs typed accessors for serialized on-disk structures in extent buffers and in-memory stack copies.

Core macro families:
- `DECLARE_BTRFS_SETGET_BITS`: declares generic scalar extent-buffer accessors.
- `BTRFS_SETGET_FUNCS`: generates extent-buffer field accessors.
- `BTRFS_SETGET_HEADER_FUNCS`: optimized metadata header accessors from the first extent-buffer folio.
- `BTRFS_SETGET_STACK_FUNCS`: generates accessors for materialized disk-format structs in memory.
- `read_eb_member` and `write_eb_member`: copy non-scalar members between extent buffers and memory.

Major accessor groups:
- Device, chunk, stripe, block group, block group v2, and free-space metadata.
- Inode refs, inode extrefs, inode items, timespecs, RAID stride records, and dev extents.
- Extent items, tree block info, extent data refs, shared data refs, owner refs, and inline refs.
- B-tree nodes, leaf items, item keys, item offsets/sizes, directory items, root refs, and free-space headers.
- Disk key conversion helpers, with optimized little-endian memcpy paths and explicit conversion for other architectures.
- Metadata headers, root items, root backups, balance items, superblock fields, file extents, qgroups, device replace, verity descriptors, and remap items.

Important helpers:
- `btrfs_extent_inline_ref_size()` maps inline ref types to serialized sizes and returns zero for unknown types.
- `btrfs_node_blockptr()`, `btrfs_node_ptr_generation()`, and node key helpers access internal node slots.
- `btrfs_item_ptr()` and `btrfs_item_ptr_offset()` cast into the leaf data area.
- `btrfs_header_flag()`, `btrfs_set_header_flag()`, and `btrfs_clear_header_flag()` manipulate header flags.
- `btrfs_is_leaf()` checks header level.
- `btrfs_set_device_total_bytes()` warns if device size is not sectorsize-aligned.

Invariants:
- Generated field accessors use `static_assert` to ensure the requested integer width matches the on-disk field size.
- Header accessors assume the metadata header is reachable in the first folio at `offset_in_page(eb->start)`.
- Pointer-shaped values are logical offsets into an extent buffer, not normal kernel pointers.

Risk notes: This header underpins most Btrfs metadata code. It intentionally provides fast typed wrappers over serialized disk structures, so callers still must supply valid slots, item types, and extent buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/accessors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/acl.c -->
# File Research: sources/os/linux/linux/fs/btrfs/acl.c

Purpose: Implements Btrfs POSIX ACL get/set operations using xattrs.

Main functions:
- `btrfs_get_acl()`: rejects RCU lookup with `-ECHILD`, maps ACL type to the access/default ACL xattr name, reads size, allocates a value buffer when present, reads the xattr, and converts it with `posix_acl_from_xattr()`.
- `__btrfs_set_acl()`: validates ACL type, rejects default ACLs on non-directories unless clearing, converts ACLs to xattr format in a NOFS allocation context, writes the xattr with or without an existing transaction, and updates the cached ACL.
- `btrfs_set_acl()`: updates inode mode for access ACLs through `posix_acl_update_mode()`, calls the internal setter, and restores the old mode on failure.

Error handling:
- Invalid ACL types return `-EINVAL`.
- Missing ACL xattrs return `NULL`, not an error.
- Allocation failure returns `-ENOMEM`.
- Default ACL on a non-directory returns `-EINVAL` when setting and succeeds when clearing.
- Xattr write errors propagate to the caller.

Risk notes: The NOFS allocation context avoids reclaim recursion while holding transaction state. The mode update and xattr update are not a single primitive, so restoring `i_mode` after failure is important.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/acl.h -->
# File Research: sources/os/linux/linux/fs/btrfs/acl.h

Purpose: Declares the Btrfs ACL API and stubs it out when POSIX ACL support is disabled.

Interfaces when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled:
- `btrfs_get_acl(struct inode *, int type, bool rcu)`.
- `btrfs_set_acl(struct mnt_idmap *, struct dentry *, struct posix_acl *, int type)`.
- `__btrfs_set_acl(struct btrfs_trans_handle *, struct inode *, struct posix_acl *, int type)`.

Stub behavior when disabled:
- `btrfs_get_acl` and `btrfs_set_acl` are defined as `NULL`, matching VFS operation table expectations.
- `__btrfs_set_acl()` returns `-EOPNOTSUPP`.

Integration: Included by inode and xattr paths that need optional ACL support without open-coded config conditionals at each call site.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/async-thread.c -->
# File Research: sources/os/linux/linux/fs/btrfs/async-thread.c

Purpose: Implements Btrfs workqueue wrappers with filesystem ownership, optional ordered completion, tracing, and dynamic concurrency thresholding.

Main structures:
- `struct btrfs_workqueue`: wraps a kernel workqueue, owner `fs_info`, ordered work list, pending count, max/current active counts, threshold state, and locks.
- `struct btrfs_work`: declared in the header; contains normal and ordered callbacks plus embedded `work_struct`, list entry, owner queue, and flags.

Workqueue creation:
- `btrfs_alloc_workqueue()` creates a named `btrfs-%s` workqueue. Threshold values below `DEFAULT_THRESHOLD` disable dynamic scaling; otherwise active workers start at 1 and grow toward `limit_active`.
- `btrfs_alloc_ordered_workqueue()` creates a kernel ordered workqueue with `limit_active = current_active = 1` and thresholding disabled.

Execution flow:
- `btrfs_queue_work()` assigns the owner queue, applies queue threshold accounting, appends ordered work to `ordered_list`, traces, and queues the kernel work.
- `btrfs_work_helper()` runs the normal callback, then either traces completion or marks `WORK_DONE_BIT` and invokes ordered completion.
- `run_ordered_work()` walks only from the head of the ordered list, runs ordered callbacks in queue order, removes completed items, and invokes the final free phase.

Concurrency details:
- `thresh_queue_hook()` increments pending work count in queue/IRQ context.
- `thresh_exec_hook()` runs in worker context, decrements pending, occasionally adjusts max active workers with `workqueue_set_max_active()`, and clamps concurrency.
- `smp_mb__before_atomic()` and `smp_rmb()` ensure ordered callbacks see writes from normal callbacks before `WORK_DONE_BIT`.
- Current work is not freed until ordered traversal is done to avoid workqueue address-reuse deadlocks.

Public operations:
- Owner accessors: `btrfs_work_owner()` and `btrfs_workqueue_owner()`.
- Congestion check: `btrfs_workqueue_normal_congested()`.
- Lifecycle: `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_flush_workqueue()`, and `btrfs_destroy_workqueue()`.
- Tuning: `btrfs_workqueue_set_max()`.

Risk notes: Ordered completion correctness depends on list locking, memory barriers, and delayed freeing. Misusing the two-phase `ordered_func(work, do_free)` contract can race with list traversal or object lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/async-thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/async-thread.h -->
# File Research: sources/os/linux/linux/fs/btrfs/async-thread.h

Purpose: Declares the public interface for Btrfs asynchronous workqueues.

Key types:
- `btrfs_func_t`: normal work callback.
- `btrfs_ordered_func_t`: ordered/free callback taking a boolean phase argument.
- `struct btrfs_work`: stores callbacks plus private kernel work item, ordered list entry, owner workqueue, and flags.

Public API:
- Allocation: `btrfs_alloc_workqueue()` and `btrfs_alloc_ordered_workqueue()`.
- Work lifecycle: `btrfs_init_work()`, `btrfs_queue_work()`, `btrfs_flush_workqueue()`, `btrfs_destroy_workqueue()`.
- Tuning/inspection: `btrfs_workqueue_set_max()`, `btrfs_work_owner()`, `btrfs_workqueue_owner()`, and `btrfs_workqueue_normal_congested()`.

Integration: Used by Btrfs worker paths that need filesystem-owned workqueue tracing, throttling, or ordered completion, including async checksum submission in `bio.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/async-thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/backref.c -->
# File Research: sources/os/linux/linux/fs/btrfs/backref.c

Purpose: Implements Btrfs backreference walking, inode/path resolution from extents, data-extent sharedness checks, tree-backref iteration, and backref cache construction for relocation and generic tree analysis.

Major responsibilities:
- Resolve direct and indirect extent backrefs to parent tree blocks or roots.
- Merge on-disk inline/keyed refs with delayed refs from running transactions.
- Find all leaves or roots referencing a target extent.
- Iterate inodes and file offsets that reference a logical data extent.
- Convert inode refs/extrefs into filesystem-relative paths.
- Determine whether a data extent is shared for fiemap-like callers.
- Iterate metadata tree backrefs.
- Build and maintain a bidirectional backref cache used by relocation and related code.

Backref collection model:
- `struct btrfs_backref_walk_ctx` supplies the target `bytenr`, optional data offset filtering, transaction/time sequence, result ulists, and optional cache/callback hooks.
- Temporary refs are represented by `struct prelim_ref` and stored in three rbtrees: direct refs, indirect refs with keys, and indirect refs missing keys.
- `prelim_ref_insert()` merges identical refs and preserves negative counts from delayed drops so add/drop refs can cancel.
- `add_delayed_refs()` folds delayed refs whose sequence is within the requested tree-mod-log view.
- `add_inline_refs()` parses inline refs inside an extent item.
- `add_keyed_refs()` scans following keyed backref items for the same bytenr.
- `add_missing_keys()` reads tree blocks to obtain first keys for indirect metadata refs that lack keys.
- `resolve_indirect_refs()` turns indirect refs into concrete parent bytenrs, reinserting them as direct refs.

Core walking flow:
- `find_parent_nodes()` searches the extent tree for the target extent item, collects delayed/on-disk refs, resolves indirect refs, and emits parent bytenrs into `ctx->refs`.
- It supports commit-root searches, tree-mod-log time sequences, and active transactions.
- It can collect root IDs in `ctx->roots` when a ref has no parent and reaches a tree root.
- It attaches inode reference lists to leaf bytenrs for data extents unless `skip_inode_ref_list` is set.

Data extent handling:
- `find_extent_in_eb()` scans a leaf for non-inline `BTRFS_EXTENT_DATA_KEY` items pointing at `ctx->bytenr`.
- `check_extent_in_eb()` adjusts file offsets for bookend extents, honors `extent_item_pos` unless ignored, and records inode/offset/length triples.
- `iterate_extent_inodes()` finds referencing leaves, maps leaves to roots, and invokes a caller iterator for each inode reference.
- `iterate_inodes_from_logical()` maps a logical address to an extent, rejects metadata extents, and builds inode/root/offset triples.

Sharedness checks:
- `btrfs_is_data_extent_shared()` short-circuits as soon as it proves a data extent is shared or not shared.
- It accounts for delayed refs by attaching to the current transaction when possible; otherwise it uses `commit_root_sem`.
- `share_check` tracks references from other roots/inodes, self-reference counts, delayed delete refs, and data extent generation.
- It uses a path cache per tree level and a small previous-extents cache to speed repeated checks over nearby file extent items.
- It disables the path cache when multiple parent paths appear at a level.

Path and inode utilities:
- `btrfs_find_one_extref()` finds one extended inode reference item.
- `btrfs_ref_to_path()` walks parent inode refs backward and fills the caller buffer from the end.
- `iterate_inode_refs()` and `iterate_inode_extrefs()` enumerate regular and extended inode references.
- `paths_from_inode()` combines both ref styles into returned path strings.
- `init_data_container()` and `init_ipath()` allocate result containers for inode/path reporting.

Tree-backref iteration:
- `extent_from_logical()` maps a logical address to an extent item and returns whether it is data or metadata.
- `get_extent_inline_ref()` iterates inline refs inside an extent item.
- `tree_backref_for_extent()` extracts tree backref root/level pairs.
- `btrfs_backref_iter_start()` and `btrfs_backref_iter_next()` iterate metadata tree backrefs in commit root, supporting inline and keyed refs.

Backref cache:
- `btrfs_backref_init_cache()` initializes rbtrees/lists for cached tree block nodes and edges.
- `btrfs_backref_node` represents a tree block, including bytenr, owner, root, extent buffer, level, and state flags.
- `btrfs_backref_edge` links lower and upper tree blocks.
- Direct tree refs (`BTRFS_SHARED_BLOCK_REF_KEY`) are handled by `handle_direct_tree_backref()`.
- Indirect tree refs (`BTRFS_TREE_BLOCK_REF_KEY`) are resolved by searching the owning tree in `handle_indirect_tree_backref()`.
- `btrfs_backref_add_tree_node()` parses all backrefs for a tree block and queues parent edges.
- `btrfs_backref_finish_upper_links()` completes bidirectional parent/child links and inserts nodes into the cache rb tree.
- Cleanup helpers drop buffers, edges, nodes, pending edges, and useless detached nodes.

Risk notes: This is high-risk metadata code. Correctness depends on combining delayed refs, old tree views, direct refs, indirect refs, root ownership, and negative ref counts without double-freeing inode lists or missing shared paths. Error paths are extensive because corruption or missing extent roots must not produce false backref answers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/backref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/backref.h -->
# File Research: sources/os/linux/linux/fs/btrfs/backref.h

Purpose: Declares Btrfs backreference walking APIs, sharedness-check state, prelim-ref state, tree-backref iteration, and backref-cache structures.

Public backref context:
- `BTRFS_ITERATE_EXTENT_INODES_STOP`: non-error sentinel for iterator-driven early stop.
- `iterate_extent_inodes_t`: callback for inode/file-offset/root references to a data extent.
- `struct btrfs_backref_walk_ctx`: top-level walk parameters and outputs, including target bytenr, data extent offset filtering, transaction, fs info, tree-mod-log sequence, refs/roots ulists, cache callbacks, iterator hooks, extent-item filter, data-ref skip callback, and user context.

Sharedness context:
- `struct btrfs_backref_share_check_ctx`: stores a temporary refs ulist, current/previous leaf bytenrs, per-level path cache, and a small previous-extents cache.
- `BTRFS_BACKREF_CTX_PREV_EXTENTS_SIZE` is 8.

Main APIs:
- Allocation/free for share-check contexts.
- `extent_from_logical()`: find the extent item containing a logical address.
- `tree_backref_for_extent()`: iterate tree refs from an extent item.
- `iterate_extent_inodes()` and `iterate_inodes_from_logical()`.
- `paths_from_inode()`, `btrfs_ref_to_path()`, and result container initialization.
- `btrfs_find_all_leafs()` and `btrfs_find_all_roots()`.
- `btrfs_find_one_extref()` and `btrfs_is_data_extent_shared()`.
- Prelim-ref slab init/exit.

Internal/prelim structures exposed for related code:
- `struct prelim_ref`: temporary ref record used during backref resolution, with root ID, search key, level, count, inode list, parent, and wanted disk bytenr.
- `struct btrfs_backref_iter`: state for iterating one extent’s tree block refs in commit root.

Backref cache structures:
- `struct btrfs_backref_node`: cached tree block node with rb/simple node linkage, current/new bytenr, owner, lists, root, extent buffer, level, and state flags such as locked, processed, checked, pending, detached, and reloc-root.
- `struct btrfs_backref_edge`: links upper and lower backref nodes.
- `struct btrfs_backref_cache`: rb tree of nodes, per-level pending lists, pending/useless edge lists, counters, fs info, and relocation mode flag.

Cache APIs:
- Init, allocate/free node/edge, unlock/drop node buffers, cleanup/drop nodes, release cache.
- `btrfs_backref_add_tree_node()`, `btrfs_backref_finish_upper_links()`, and `btrfs_backref_error_cleanup()`.
- `btrfs_backref_panic()` reports cache inconsistency as a filesystem panic.

Risk notes: The header exposes subtle ownership and state-machine structures shared with relocation code. Mismanaging node/edge linkage, extent buffer lifetime, or root references can corrupt the cache or leak/over-release metadata resources.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/backref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/bio.c -->
# File Research: sources/os/linux/linux/fs/btrfs/bio.c

Purpose: Implements Btrfs bio allocation, splitting, submission, end I/O handling, data checksum verification, read repair, mirrored/RAID56 I/O dispatch, async write checksumming, zoned append handling, and bioset lifecycle.

Main state:
- `btrfs_bioset`: primary `struct btrfs_bio` allocation pool.
- `btrfs_clone_bioset`: pool for split/clone bios.
- `btrfs_repair_bioset`: pool for repair reads.
- `btrfs_failed_bio_pool`: mempool of `struct btrfs_failed_bio` tracking repair state.

Bio setup and completion:
- `btrfs_bio_init()` initializes Btrfs-specific fields around an embedded block-layer bio.
- `btrfs_bio_alloc()` allocates from the Btrfs bioset and initializes the wrapper.
- `btrfs_split_bio()` splits bios at mapping boundaries, propagating inode, offsets, ordered extent references, checksum mode, scrub/remap flags, and async checksum state.
- `btrfs_bio_end_io()` joins split completions back to the original bio, preserves the first error, waits for async checksums when needed, drops ordered extent refs, and invokes the caller endio callback.

Read checksumming and repair:
- `btrfs_check_read_bio()` verifies data read checksums sector by sector.
- Bad sectors trigger `repair_one_sector()`, which reads from alternate mirrors and tracks outstanding repair attempts through `struct btrfs_failed_bio`.
- `btrfs_end_repair_bio()` checks the repair read, retries additional mirrors if needed, and writes good data back to failed mirrors with `btrfs_repair_io_failure()`.
- Repair uses page/sector stepping to support block sizes larger than page size.

Device error reporting:
- `btrfs_log_dev_io_error()` records read/write/flush errors in device stats and rate-limits unexpected status warnings.
- Read-ahead errors do not increment read error stats.

End I/O workqueues:
- `btrfs_simple_end_io()` decrements the bio counter, logs errors, and queues task-context endio work.
- `simple_end_io_work()` handles data read checksum/repair, metadata read completion, zone append physical recording, and final completion.
- RAID56 endio is handled in task context by `btrfs_raid56_end_io()`.
- Mirrored write completions use separate original and clone endio work functions to aggregate errors against the mirror tolerance threshold.

Submission path:
- `btrfs_submit_dev_bio()` validates target device presence/writeability, sets the block device, transforms eligible writes into zone append writes, records stats, and either punts cgroup submission or calls `submit_bio()`.
- `btrfs_submit_bio()` dispatches a mapped bio to the single-mirror fast path, RAID56 parity path, or mirrored write fanout.
- `btrfs_submit_mirrored_bio()` clones bios for all but the last mirror and submits each stripe.

Checksumming and async submission:
- `btrfs_bio_csum()` computes metadata or data checksums; experimental builds pass a different data checksum mode.
- `async_submit_bio` wraps a bio, mapping context, stripe map, mirror number, and Btrfs work item.
- `run_one_async_start()` computes checksums in worker context.
- `run_one_async_done()` either completes on checksum error or marks `REQ_BTRFS_CGROUP_PUNT` and submits the bio.
- `should_async_write()` avoids async checksumming for experimental mode, fast checksum implementations, synchronous I/O, and zoned metadata writes.
- `btrfs_wq_submit_bio()` allocates async work and queues it on `fs_info->workers`.

Chunk mapping:
- `btrfs_submit_chunk()` maps a logical range with `btrfs_map_block()`, handles data-read checksum preloading, splits at map or zone-append boundaries, records original logical addresses for data writes, attaches raid-stripe-tree ordered contexts, computes or allocates checksums, and submits the mapped bio.
- `btrfs_submit_bbio()` asserts alignment and repeatedly submits chunks until the full bio is consumed.

Repair writes:
- `btrfs_repair_io_failure()` bypasses normal multi-copy submission to write one bad mirror synchronously, with read-only and zoned-repair checks.
- `btrfs_submit_repair_write()` submits metadata scrub repair writes, optionally redirecting to the device-replace target.

Lifecycle:
- `btrfs_bioset_init()` initializes all biosets and the failed-bio mempool.
- `btrfs_bioset_exit()` tears them down in reverse order.

Risk notes: This file coordinates block-layer lifetime, Btrfs ordered extents, checksum state, device replacement, RAID profiles, zoned append semantics, and read repair. The most sensitive areas are split-bio completion accounting, ordered extent reference ownership, checksum/repair iteration for block-size-greater-than-page-size cases, and bypass paths that intentionally avoid normal multi-mirror submission.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/bio.c -->