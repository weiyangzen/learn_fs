# Group Research: group_242_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_Kconfig_sources_lo_ac3a6b9fdd52

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/btrfs-linux` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/Kconfig -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/Kconfig

Defines the kernel configuration surface for Btrfs.

Key points:
- `CONFIG_BTRFS_FS` is the main tristate module/built-in option.
- Main filesystem support selects checksum, compression, iomap, RAID parity, XOR, xxhash, and block-cgroup bio punt support.
- Depends on `PAGE_SIZE_LESS_THAN_256KB`, reflecting Btrfs metadata/page-size limits in this tree.
- `CONFIG_BTRFS_FS_POSIX_ACL` enables POSIX ACL support and selects `FS_POSIX_ACL`.
- `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` enables module-load regression/sanity tests.
- `CONFIG_BTRFS_DEBUG` enables runtime debugging, leak checks, debug sysfs, optional fragmentation behavior, and `REF_TRACKER` when stack traces are supported.
- `CONFIG_BTRFS_ASSERT` enables lightweight invariant assertions.
- `CONFIG_BTRFS_EXPERIMENTAL` gates unstable/developer-facing features, including raid-stripe-tree, extent tree v2, large folio/block size support, async checksum generation, remap-tree, send protocol v3 fs-verity support, and experimental read policy work.

Role in system:
- Establishes which Btrfs subsystems are compiled and which optional code paths are available.
- The config options directly drive `fs/btrfs/Makefile` object inclusion.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/Makefile -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/Makefile

Build recipe for the Btrfs kernel module/object.

Key points:
- Adds a selected subset of `W=1` compiler warnings for the whole Btrfs subdirectory.
- Main target is `obj-$(CONFIG_BTRFS_FS) := btrfs.o`.
- Core `btrfs-y` object list includes metadata trees, inode/file paths, extent I/O, volumes, compression, delayed refs/inodes, relocation, scrub, backrefs, qgroups, send, RAID56, free-space tree, block groups, discard, reflink, subpage, tree-mod-log, messages, bio, fiemap, direct I/O, and raid-stripe-tree.
- Conditional objects:
  - `acl.o` for `CONFIG_BTRFS_FS_POSIX_ACL`.
  - `ref-verify.o` for `CONFIG_BTRFS_DEBUG`.
  - `zoned.o` for `CONFIG_BLK_DEV_ZONED`.
  - `verity.o` for `CONFIG_FS_VERITY`.
- Sanity test objects are compiled under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.
- Zoned tests are only included when both sanity tests and zoned block device support are enabled.

Role in system:
- Connects feature flags from `Kconfig` to concrete compilation units.
- The file also shows the broad subsystem boundaries of Btrfs in this source tree.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/accessors.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/accessors.c

Implements low-level extent-buffer field accessors used to read and write little-endian on-disk metadata fields.

Key points:
- Provides generated implementations for `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()`.
- Accessors treat metadata pointers as logical offsets inside an `extent_buffer`.
- Handles fields crossing folio/page boundaries, which matters when metadata block size exceeds page size.
- Uses `get_eb_folio_index()` and `get_eb_offset_in_folio()` to find the backing folio and offset.
- Bounds checks all access against `eb->len`; bad offsets emit `btrfs_warn()` through `report_setget_bounds()`.
- Uses unaligned little-endian helpers, including split-copy assembly for cross-folio reads and writes.
- Implements `btrfs_node_key()`, copying a node key pointer’s embedded key from an extent buffer.

Role in system:
- This is the implementation backing many inline accessors declared in `accessors.h`.
- It centralizes safe on-disk field access for Btrfs metadata buffers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/accessors.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/accessors.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/accessors.h

Large inline accessor header for Btrfs on-disk structures.

Key points:
- Defines generic accessor macros:
  - `BTRFS_SETGET_FUNCS()` for extent-buffer backed structures.
  - `BTRFS_SETGET_HEADER_FUNCS()` for extent-buffer header fields.
  - `BTRFS_SETGET_STACK_FUNCS()` for stack-resident on-disk structs.
- Declares `btrfs_get/set_8/16/32/64()` implemented in `accessors.c`.
- Provides read/write member helpers using `read_extent_buffer()` and `write_extent_buffer()`.
- Supplies little-endian optimized key conversion for `__LITTLE_ENDIAN`; big-endian builds perform explicit conversion.
- Covers accessors for device items, chunks, stripes, block groups, free-space info, inode refs, inode items, timespecs, raid strides, dev extents, extent items, inline refs, node pointers, leaf items, directory items, root refs, headers, root items, root backups, balance items, superblock fields, file extent items, qgroups, device replace items, verity descriptor items, and remap items.
- Includes helper pointer calculations such as `btrfs_item_nr_offset()`, `btrfs_item_ptr()`, `btrfs_stripe_nr()`, and UUID field offset helpers.
- `btrfs_extent_inline_ref_size()` maps inline-ref key type to the encoded size consumed in extent items.
- Header accessors assume the Btrfs tree header is in the first extent-buffer folio at `offset_in_page(eb->start)`.

Role in system:
- Provides type-checked, endian-correct access to nearly all Btrfs disk-format structures.
- This file is a core compatibility boundary between in-memory code and the stable on-disk format.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/accessors.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/acl.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/acl.c

Implements POSIX ACL get/set operations through Btrfs extended attributes.

Key points:
- `btrfs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`.
- Rejects RCU ACL lookup with `-ECHILD`.
- Reads ACL xattr size first, allocates storage, then reads xattr content.
- Converts xattr bytes to `struct posix_acl` with `posix_acl_from_xattr(&init_user_ns, ...)`.
- `__btrfs_set_acl()` serializes ACLs with `posix_acl_to_xattr()`.
- Uses `memalloc_nofs_save()` while allocating serialized ACL xattrs under a transaction to avoid filesystem reclaim deadlocks.
- Default ACLs are only valid for directories; setting one on a non-directory returns `-EINVAL`, while clearing one is a no-op.
- Chooses `btrfs_setxattr()` when a transaction handle is supplied and `btrfs_setxattr_trans()` otherwise.
- Updates the VFS ACL cache with `set_cached_acl()` after successful storage.
- `btrfs_set_acl()` updates inode mode for access ACLs via `posix_acl_update_mode()` and rolls back mode on storage failure.

Role in system:
- Bridges Linux POSIX ACL infrastructure to Btrfs xattr persistence.
- Compiled only when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/acl.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/acl.h

Header for Btrfs POSIX ACL integration.

Key points:
- Declares `btrfs_get_acl()`, `btrfs_set_acl()`, and `__btrfs_set_acl()` when `CONFIG_BTRFS_FS_POSIX_ACL` is enabled.
- Provides disabled-config stubs:
  - `btrfs_get_acl` and `btrfs_set_acl` are `NULL`.
  - `__btrfs_set_acl()` returns `-EOPNOTSUPP`.
- Forward declares ACL, inode, dentry, idmap, and transaction types as needed.

Role in system:
- Lets the rest of Btrfs call ACL helpers without scattering config conditionals.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.c

Btrfs wrapper around Linux workqueues with optional ordered completion and adaptive concurrency.

Key points:
- Defines `struct btrfs_workqueue`, wrapping a normal kernel workqueue plus Btrfs owner, ordered-list state, pending count, active limit, current active workers, and threshold tracking.
- `btrfs_alloc_workqueue()` creates a named `btrfs-%s` workqueue.
- Threshold behavior:
  - Threshold `0` becomes default `32`.
  - Thresholds below default disable adaptive thresholding.
  - Larger thresholds start with `max_active=1` and grow/shrink based on pending work.
- `btrfs_alloc_ordered_workqueue()` creates a strictly ordered workqueue with max active `1`.
- `btrfs_workqueue_normal_congested()` reports congestion when pending work exceeds twice the threshold.
- `thresh_queue_hook()` increments pending count in queue context, including IRQ-safe context.
- `thresh_exec_hook()` decrements pending count and adjusts `workqueue_set_max_active()` from worker context.
- Ordered work:
  - `run_ordered_work()` walks `ordered_list` and only runs ordered callbacks after each item’s normal work is done.
  - Uses memory barriers pairing `smp_mb__before_atomic()` with `smp_rmb()` so ordered callbacks see normal-work writes.
  - Handles lifetime carefully so a currently executing work item is not recycled before ordered cleanup completes.
- `btrfs_work_helper()` runs the normal callback, marks ordered work done, and invokes ordered sequencing or direct final tracing.
- Public helpers initialize, queue, flush, set max, and destroy Btrfs workqueues.

Role in system:
- Provides Btrfs-specific async execution semantics used by I/O, checksumming, compression, and other background work.
- Ordered callback support is important where completion order must match queue order even if worker execution is parallel.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.h

Public interface for Btrfs async workqueues.

Key points:
- Defines callback types:
  - `btrfs_func_t` for normal work.
  - `btrfs_ordered_func_t` for ordered completion/free callbacks.
- `struct btrfs_work` stores the callbacks, embedded `work_struct`, ordered list node, owning `btrfs_workqueue`, and flags.
- Warns consumers not to touch internal fields below the callbacks.
- Declares allocation for normal and ordered workqueues, work initialization/queueing, destruction, max active adjustment, owner queries, congestion query, and flushing.

Role in system:
- This is the small stable API used by Btrfs subsystems that need deferred work with optional ordered completion.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/async-thread.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/backref.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/backref.c

Implements Btrfs backreference walking, extent-to-inode/root/path resolution, sharedness checks, and backref cache graph construction.

Key points:
- Backref walking represents discovered references as `prelim_ref` records stored in rbtrees.
- Maintains separate trees for:
  - Direct refs with known parent bytenr.
  - Indirect refs with enough key/root information to resolve.
  - Indirect refs missing keys that require reading the child block.
- `add_prelim_ref()`, `add_direct_ref()`, and `add_indirect_ref()` merge equivalent refs and track reference counts, including negative delayed-drop refs.
- Delayed refs are integrated through `add_delayed_refs()`, accounting for add/drop actions and ref types.
- On-disk extent refs are parsed through:
  - `add_inline_refs()` for inline refs inside extent items.
  - `add_keyed_refs()` for separate keyed backref items.
- `add_missing_keys()` reads tree blocks to obtain first keys when indirect metadata refs lack keys.
- `resolve_indirect_ref()` resolves `(root_id, key, level)` to parent logical addresses by searching the appropriate fs root or old tree state.
- `find_parent_nodes()` is the core engine: it gathers delayed/on-disk refs, resolves indirect refs, merges parents, optionally collects roots, and optionally attaches inode lists for data refs.
- `btrfs_find_all_leafs()` finds leaves containing file extent items pointing to a target data extent.
- `btrfs_find_all_roots()` recursively walks metadata parents to identify all roots that reference an extent.
- `btrfs_is_data_extent_shared()` is optimized for fiemap-like sharedness checks:
  - Stops early when sharing is proven.
  - Accounts for delayed refs when a transaction can be joined.
  - Uses path-cache entries for repeated leaf/path checks.
  - Caches recent extent sharedness when the same bytenr appears in multiple file extent items.
- `extent_from_logical()` maps a logical address to the containing extent item and returns whether it is data or tree block metadata.
- `iterate_extent_inodes()` resolves a data extent to inode/file-offset/root tuples, using optional leaf-to-root caches.
- `iterate_inodes_from_logical()` is a logical-address-to-inode helper for ioctl-style reporting.
- Path reconstruction:
  - `btrfs_find_one_extref()` iterates extended inode refs.
  - `btrfs_ref_to_path()` walks parent inode refs backward into a path string.
  - `paths_from_inode()` combines regular inode refs and extended refs.
  - `init_data_container()` and `init_ipath()` allocate output containers.
- Tree backref iteration:
  - `btrfs_backref_iter_alloc()`, `btrfs_backref_iter_start()`, and `btrfs_backref_iter_next()` iterate inline/keyed metadata backrefs in commit root.
  - `tree_backref_for_extent()` extracts tree backref root/level information.
- Backref cache graph:
  - `btrfs_backref_node` represents tree blocks.
  - `btrfs_backref_edge` connects child and parent tree blocks.
  - `btrfs_backref_cache` stores nodes in an rb tree plus pending/useless lists.
  - `btrfs_backref_add_tree_node()` processes direct and indirect tree backrefs for a node.
  - Direct shared block refs use parent bytenr directly.
  - Indirect tree block refs search the owning root to find parent blocks.
  - `btrfs_backref_finish_upper_links()` finalizes bidirectional graph linkage.
  - Cleanup paths carefully release buffers, roots, edges, and detached nodes.

Role in system:
- This is central to Btrfs’s COW/reference model. It supports qgroups, fiemap shared-extent reporting, logical inode lookup, send/receive style ancestry needs, relocation, scrub/repair decisions, and consistency checking.
- The code handles multiple tricky states: delayed refs, old tree-mod-log views, commit-root searches, shared subtree detection, data reloc roots, skinny metadata, and negative refs from pending drops.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/backref.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/backref.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/backref.h

Public declarations and data structures for Btrfs backref walking and backref cache construction.

Key points:
- Defines `BTRFS_ITERATE_EXTENT_INODES_STOP` as a non-error early-stop signal for inode iteration callbacks.
- Defines `iterate_extent_inodes_t`, called with inode number, file offset, byte length, root id, and user context.
- `struct btrfs_backref_walk_ctx` is the main backref-walk context:
  - Target extent bytenr.
  - Data extent position filtering.
  - Flags to ignore position or skip inode lists.
  - Optional transaction/time-sequence.
  - Output `refs` and `roots` ulists.
  - Optional cache lookup/store callbacks.
  - Optional indirect-ref iterator, extent-item checker, and data-ref skip callback.
- `struct inode_fs_paths` groups a path object, fs root, and output path container.
- `struct btrfs_backref_share_check_ctx` caches sharedness checks:
  - Current/previous leaf bytenr.
  - Per-level path cache entries.
  - Small recent extent cache for repeated data extent bytenrs.
- Declares APIs for:
  - Extent lookup from logical address.
  - Tree backref iteration.
  - Extent-to-inode iteration.
  - Logical-to-inode iteration.
  - Inode-to-path conversion.
  - Finding all leaves/roots.
  - Data extent sharedness checks.
  - Prelim-ref cache initialization/teardown.
- Defines `struct prelim_ref`, the internal merged backref representation.
- Defines `struct btrfs_backref_iter` and helper `btrfs_backref_has_tree_block_info()`.
- Defines backref graph/cache structs:
  - `btrfs_backref_node`.
  - `btrfs_backref_edge`.
  - `btrfs_backref_cache`.
- Declares node/edge allocation, cleanup, cache release, add-tree-node, finish-link, and error-cleanup routines.
- `btrfs_backref_panic()` reports irrecoverable cache inconsistency.

Role in system:
- Provides the interface used by relocation, fiemap, qgroups, ioctl logical-inode lookup, and other code needing reference ancestry.
- Encodes the shared ownership/lifetime model for backref graph nodes and edges.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/backref.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/bio.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/bio.c

Implements Btrfs bio allocation, mapping, submission, completion, checksum handling, read repair, mirrored writes, RAID56 submission hooks, zone append handling, and bioset lifecycle.

Key points:
- Defines biosets for normal Btrfs bios, cloned bios, repair bios, and a mempool for failed-bio repair state.
- `btrfs_bio_init()` initializes the Btrfs wrapper fields around an already initialized embedded `bio`.
- `btrfs_bio_alloc()` allocates from `btrfs_bioset`; allocation is backed by mempool behavior.
- `btrfs_split_bio()` splits a bio at chunk/map boundaries and preserves Btrfs wrapper state, including ordered extents, checksum flags, scrub/remap flags, async csum mode, and zone append capability.
- `btrfs_bio_end_io()` joins split-bio completion, waits for async checksums when needed, records first error status, releases ordered extents, and calls the original completion callback once all child I/Os finish.
- Read checksum/repair:
  - `btrfs_check_read_bio()` validates data checksums sector by sector.
  - On checksum or I/O failure, `repair_one_sector()` submits a read from another mirror.
  - `btrfs_end_repair_bio()` validates repair reads, tries alternate mirrors if needed, and writes good data back to bad mirrors using `btrfs_repair_io_failure()`.
- Device error accounting:
  - `btrfs_log_dev_io_error()` increments read/write/flush device stats for relevant block statuses.
- Completion handling:
  - `btrfs_simple_end_io()` queues completion work for normal single-device I/O.
  - `btrfs_raid56_end_io()` handles RAID56 parity completion.
  - Mirrored write completions aggregate errors against the tolerated mirror threshold.
- Submission:
  - `btrfs_submit_dev_bio()` validates devices, sets block device, converts writes to zone append on sequential zones when allowed, updates read stats, and submits through cgroup punt or normal `submit_bio()`.
  - `btrfs_submit_mirrored_bio()` clones write bios across mirrors, reusing the original bio for the final mirror.
  - `btrfs_submit_bio()` dispatches to single-mirror, RAID56, or mirrored-write paths.
- Checksumming:
  - `btrfs_bio_csum()` dispatches to metadata or data checksum generation.
  - `should_async_write()` chooses whether to offload data checksum generation to Btrfs workers.
  - Async checksum submission uses `struct async_submit_bio` and ordered Btrfs work callbacks.
- Chunk mapping:
  - `btrfs_submit_chunk()` maps logical bio ranges through `btrfs_map_block()`, splits bios when map length is smaller than bio length, preloads read checksums, prepares write checksums or dummy sums, handles raid-stripe-tree association, and submits the mapped bio.
  - `btrfs_append_map_length()` caps and aligns zone-append writes.
- `btrfs_submit_bbio()` asserts alignment and loops over chunks until the full bio is submitted.
- Repair writes:
  - `btrfs_repair_io_failure()` writes a corrected block to a specific mirror, bypassing normal mirrored write submission.
  - `btrfs_submit_repair_write()` maps and submits scrub/metadata repair writes, optionally redirecting to a device-replace target.
- Bioset lifecycle:
  - `btrfs_bioset_init()` initializes all biosets and failed-bio mempool.
  - `btrfs_bioset_exit()` tears them down in reverse order.

Role in system:
- This is the main Btrfs I/O submission and completion layer between logical filesystem bios and physical devices.
- It is responsible for preserving Btrfs semantics across chunk boundaries, redundancy profiles, checksums, read repair, device replacement, zoned storage, and cgroup-aware submission.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/bio.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/bio.h

Public Btrfs bio wrapper interface.

Key points:
- Defines `BTRFS_BIO_INLINE_CSUM_SIZE` for inline checksum storage.
- Defines `btrfs_bio_end_io_t` callback type.
- `struct btrfs_bio` embeds a kernel `struct bio` as the final member and stores Btrfs-specific context before it.
- Common fields:
  - Target inode and file offset.
  - Completion callback and private data.
  - Pending split-I/O count.
  - Mirror number.
  - First saved error status.
  - Flags for commit-root checksum search, scrub, remap, async checksum, and zone append.
- Union payload covers:
  - Data reads: checksum buffer, inline checksum buffer, saved iterator.
  - Data writes: ordered extent, ordered sums, checksum work/completion, saved checksum iterator, original physical/logical addresses.
  - Metadata reads: parent-check structure.
- `btrfs_bio()` converts embedded `bio *` back to `struct btrfs_bio *`.
- Declares bioset init/exit, init/allocation, end I/O, submit, repair write, and read-repair failure APIs.
- Defines `REQ_BTRFS_CGROUP_PUNT` as `REQ_FS_PRIVATE`, used to submit through `blkcg_punt_bio_submit`.

Role in system:
- Establishes the high-level I/O container used by `bio.c` and callers throughout Btrfs.
- The layout requirement that `bio` is last is essential because `bio_alloc_bioset()` allocates enough memory for the whole wrapper.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/bio.h -->