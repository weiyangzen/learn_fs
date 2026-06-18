# Group Research: group_232_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_sb_io_c_sources_c_2025af4c5b5a

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/bcachefs-tools`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io.c

Implements bcachefs superblock IO, validation, version handling, optional-field management, and human-readable dumping. It owns metadata-version name lookup, compatible/latest-compatible version helpers, incompatible-version request handling, and the persistent feature upgrade path.

Core logic includes `bch2_sb_field_get_id()`, resize/delete helpers for variable-length superblock sections, `bch2_sb_realloc()`, `validate_sb_layout()`, and `bch2_sb_validate()`. Validation checks magic/layout consistency, feature/version compatibility, UUIDs, offsets, device counts, time precision, member fields, and per-field validators.

Read path opens the block device according to mount/tool options, reads primary and backup superblocks, validates checksum and size, and chooses the highest valid sequence-number copy. If the primary cannot be used, it reads the standalone layout sector and scans backups. It also retries with buffered IO when direct IO is incompatible with the device block size in userspace builds.

Write path updates clean/dirty state, sequence numbers, per-member sequence fields, timestamps, counters, members, downgrade info, and extent-type metadata, then validates each online device superblock before writing every configured superblock slot. It reads back the primary slot before writing to detect dropped writes or concurrent modification, tracks per-device/per-offset write failures, and forces emergency read-only if the resulting set of written devices could not safely mount the filesystem.

The file registers optional-field ops for the `ext` section, dispatches field validation/text rendering by type, and prints full superblock details including UUIDs, versions, layout, options, features, compat bits, and selected sections.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io.h

Public interface for superblock IO and optional-field manipulation. It defines the scratch read buffer size, version compatibility predicate, field access/resize macros, `field_to_type()`, and `bch_sb_field_ops`.

Exports read/write/validate functions, superblock copy functions between disk and in-memory fs/device handles, feature-setting helpers, version downgrade/upgrade entry points, and text printers for superblocks, layouts, and fields. Inline magic helpers derive bset/jset magic from the filesystem UUID.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io_types.h

Defines `struct bch_sb_cpu`, the endian-converted in-memory summary populated by `bch2_sb_update()`. It mirrors stable superblock identity, version fields, device count, clean/encryption state, feature/compat bits, extent encoding metadata, time conversion values, required recovery passes, silenced fsck errors, and btrees with lost data.

This structure is the runtime cache used outside direct superblock parsing paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/io_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members.c

Implements superblock member-device metadata handling. It reports missing/removed devices referenced by keys, tracks member error string tables, migrates `members_v1` to `members_v2`, resizes v2 entries to the current `struct bch_member`, and writes compatibility v1 copies while old metadata versions require them.

Validation enforces bucket count limits, first-bucket minimums, bucket size relative to block and btree-node size, valid btree bitmap shift, and consistency between freespace initialization and allocation-info features. Text output prints full and short device identity, size, errors, IOPS estimates, bucket geometry, state, data masks, durability, discard/freespace flags, hardware strings, and flush errors.

Runtime sync functions copy atomic device error counters into the superblock and convert member records into `bch_member_cpu` cache entries. It also implements IO error reset persistence, btree-allocation bitmap marking/checking/GC, scheduled bitmap GC heuristics, member slot allocation, deleted-member cleanup, and device identity/rotational-field upgrades.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members.h

Header for member access, iteration, refcounting, lookup, and property helpers. It provides v1/v2 member readers that copy variable-sized on-disk entries into padded `struct bch_member` values, plus mutable v2 accessors.

Defines RCU and refcounted device iteration macros, online/rw/readable member loops using enumerated IO refs, percpu-ref device lifetime helpers, outer memory-lifetime refs, and device lookup variants that either tolerate missing devices or report fs inconsistency. It also exposes bucket validity checks and bkey/bucket-specific tryget helpers.

Member utilities include alive/existing predicates, endian conversion to `bch_member_cpu`, btree bitmap inline checks, GC/marking prototypes, member allocation/cleanup, device metadata upgrade entry points, and member-name printing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members_format.h

Defines the on-disk member-device format and limits. Important constants include `BCH_SB_MEMBERS_MAX` 256, invalid member sentinel 255, deleted-member UUID, minimum bucket count, member bucket-count cap, and max btree bitmap shift.

`struct bch_member` stores UUID, bucket geometry, flags, IOPS estimates, persistent error counters, sequence, btree allocation bitmap, last journal position, device identity strings, flush errors, and serial. Bitfield macros encode state, discard, allowed data types, disk group, durability, freespace/resize/rotational/initialized flags. Also defines v1 fixed-size entries and v2 variable-size member sections.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members_types.h

Defines `struct bch_member_cpu`, the runtime endian-converted member cache. It stores bucket geometry, group/state, discard/data/durability flags, initialization state, resize and rotational flags, validity, and btree allocation bitmap data.

Used after superblock parsing to avoid repeated endian/bitfield extraction.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/sb/members_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/scripts/getdents-layout.sh -->
# File Research: sources/cow-pools/bcachefs-tools/fs/scripts/getdents-layout.sh

Build helper script that generates layout-check macros for a copied `getdents_callback64` structure used by `fs/dirent.c`. It supports trusted in-tree mode when no vmlinux is available, verified external/DKMS mode when `pahole` can inspect `getdents_callback64`, and unverified fallback mode that disables the fast path.

The script writes to a temp file, emits either trust/verify/unverified macros plus offsets/size from `pahole`, and only replaces the output if content changed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/scripts/getdents-layout.sh -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/check_snapshots.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/check_snapshots.c

Implements snapshot fsck/recovery checks. It validates `snapshot_tree` keys against root snapshot nodes and master subvolumes, repairing or deleting bad tree records and choosing replacement master subvolumes when needed.

Snapshot checks verify parent/child backpointers, subvolume links, snapshot-tree pointers, depth fields, and skiplist ancestors. Repairs can clear invalid subvol references, recreate/repair snapshot tree pointers, update depths, regenerate skiplist entries, and sort skiplists.

It can reconstruct missing single-node snapshot trees by scanning snapshot-aware btrees, recreating snapshot nodes when possible, and requiring recovery passes before deleting keys in missing snapshots. `__bch2_check_key_has_snapshot()` deletes keys in definitively deleted snapshots and carefully gates deletion for missing snapshots behind consistency/reconstruction checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/check_snapshots.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/delete.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/delete.c

Implements asynchronous and recovery-time snapshot deletion. The file documents dead leaf snapshots, redundant interior nodes, `WILL_DELETE`, and `NO_KEYS` states. Runtime deletion removes keys and marks interior nodes `NO_KEYS`; actual interior-node tree surgery is deferred to recovery.

Deletion builds lists of trees being cleaned, leaf IDs, interior IDs with surviving children, and an Eytzinger-searchable delete list. It scans snapshot-aware btrees, deletes keys in dying snapshots, and moves keys from dead interior nodes to surviving children when needed. Version 2 accelerates scanning by using inodes first to target extents/dirents/xattrs.

It marks leaf nodes deleted, updates parent/child and snapshot-tree root pointers, handles old/new deletion formats through incompatible-version negotiation, and removes snapshot accounting. Async entry points run under write refs and expose progress/status, while recovery deletion fixes depths/skiplists before removing `NO_KEYS` interior nodes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/delete.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/format.h

Defines on-disk subvolume, snapshot, and snapshot-tree records. `bch_subvolume` stores flags, snapshot ID, root inode, creation parent, filesystem-path parent, and creation time. Flags encode read-only, snapshot-subvolume, and unlinked state.

`bch_snapshot` stores flags, parent, two children, subvol, tree ID, depth, three skiplist entries, and birth time. Flags encode `WILL_DELETE`, `SUBVOL`, `DELETED`, and `NO_KEYS`. `bch_snapshot_tree` records master subvolume and root snapshot for a persistent snapshot-tree identity.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.c

Implements core snapshot-tree operations and includes extensive design documentation. It defines snapshot-tree text/validation/lookup/create helpers, accelerated ancestor checks using skiplists plus 128-ID ancestor bitmaps, and slow early-recovery fallback walks.

The in-memory snapshot table is RCU-managed and indexed by reversed snapshot IDs. Snapshot triggers populate table entries, state, parent/children, subvol/tree/depth/skip data, ancestor bitmaps, and queue dead-snapshot deletion when `WILL_DELETE` appears.

Also implements snapshot-tree traversal, snapshot lookup, overwrite detection, snapshot-ID allocation for new trees or child pairs, initial snapshot table read, empty-interior cleanup scheduling, snapshot subsystem init/exit, and textual tree reports with per-snapshot accounting/path output.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.h

Public snapshot API. It declares bkey ops for snapshot and snapshot-tree keys, lookup/create/validate/text functions, trigger entry points, tree reporting, deletion checks, and fsck/reconstruction passes.

Inline helpers access the RCU snapshot table, compare tree IDs, get parents/root/depth/state, test live/deleted/existing snapshots, identify leaves/internal nodes, find live descendants through `NO_KEYS` nodes, and manage snapshot ID lists. It also defines iteration macros over snapshot trees and wrappers for overwrite and key-snapshot validation fast paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/snapshot.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.c

Implements subvolume validation, fsck repair, lookup, creation, unlink, deletion, and upgrade initialization. Check paths verify subvolume-to-snapshot links, root subvolume parent rules, `subvolume_children` index entries, root inode existence and `bi_subvol`, and master-subvolume consistency for non-snapshot subvolumes.

Bkey ops validate positions, snapshot IDs, and root inode fields; triggers maintain the `subvolume_children` btree when filesystem path parents change. Lookup helpers can report missing subvolumes by scheduling inode checks.

Deletion reparents snapshot-subvolume creation children, clears master-subvolume references if needed, deletes the subvolume key, and marks the associated snapshot node deleted. Unlink first marks a subvolume unlinked and schedules pagecache eviction before deletion. Creation allocates a new subvolume slot and either creates a new snapshot tree or splits an existing snapshot node into two children.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.h

Public subvolume API and bkey ops. It declares checkers, validation/text/trigger functions, child detection, subvolume lookup, snapshot ID lookup, read-only checks, unlink/create/init/upgrade entry points, and early init.

Provides iterator helpers/macros for reading btree keys within a subvolume by lazily resolving the subvolume’s snapshot ID and setting the iterator snapshot, with transaction-restart handling variants.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/subvolume.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/types.h

Defines in-memory snapshot subsystem types. `snapshot_t` stores state, parent, skiplist, depth, normalized children, subvol, tree, and a 128-bit ancestor bitmap. `snapshot_table` is an RCU flexible-array container.

Also defines dynamic-array aliases for snapshot ID lists and interior-deletion lists, `snapshot_delete` background-progress state, `bch_fs_snapshots` subsystem state including create lock and unlinked list, and `subvol_inum`. Comments document the page-cache dirtying race avoided by taking `create_lock` as a writer during snapshot creation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/snapshots/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock.c

Implements approximate IO-sector clocks with min-heap timers. Timers are added under a spinlock, fire immediately if already expired, and are deduplicated before heap insertion. Delete scans the heap and removes matching timers.

Wait helpers schedule the current task until IO-clock expiration or CPU timeout, with kthread stop/freezer awareness. Clock increments add sector deltas to `now`, pop expired timers, and invoke callbacks. Text output prints current time and pending timers; init/exit allocate/free percpu buffers and timer heaps.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock.h

Declares IO clock/timer functions and provides `bch2_increment_clock()`, which batches sector increments per CPU and flushes to the shared atomic clock when the per-CPU threshold is reached. Exposes timer add/delete, kthread waits, timeout scheduling, diagnostics, init, and exit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock_types.h

Defines IO-clock types. Timers contain callback, secondary debug/function pointer, and expiration sector. `io_clock` stores atomic current time, per-CPU sector buffer, max slop, timer spinlock, and min heap. Constants set timer capacity to three per member device and per-CPU buffering to 128 sectors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/clock_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/darray.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/darray.c

Implements dynamic-array resizing. Growth rounds requested element count up to a power of two, checks multiplication overflow, uses `kvmalloc`/aligned kernel allocation for smaller allocations and `vmalloc` for very large allocations, copies existing entries, RCU-publishes the new data pointer, updates capacity, and frees old storage immediately or via RCU as requested.

It supports preallocated inline storage by avoiding freeing the embedded buffer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/darray.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/darray.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/darray.h

Macro-based dynamic-array library. It defines preallocated and heap-only array shapes, init/exit helpers, cleanup classes, typed aliases, push/pop/resize/make-room helpers, iteration macros, insert/remove/find helpers, and sort/search wrappers.

RCU resize variants preserve readers, and free-item variants run per-element destructors. Eytzinger sort/find wrappers support one-based arrays with a reserved element at index 0.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/darray.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.c

Implements enumerated refs. In normal builds it wraps `percpu_ref` and invokes an optional stop callback when killed. In debug builds it keeps one atomic refcount per enumerated user, allowing diagnostics to show which users are still holding refs.

Stop logic kills refs asynchronously, waits with periodic 10-second diagnostic dumps, supports restart/reinit, and frees debug arrays/percpu refs on exit. Text output lists per-user counts in debug mode or notes that debug mode is disabled.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.h

Public enumerated-ref API. Provides `get`, `tryget`, live `tryget`, and `put` as either debug function calls or inline `percpu_ref` wrappers. Also exposes zero test, stop/start, init/exit, and diagnostic text rendering.

Callers pass an index naming the ref user; in non-debug builds the index is ignored but retained for instrumentation-compatible call sites.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref_types.h

Defines `struct enumerated_ref`. Debug builds store user count, dying flag, and atomic array; normal builds store a `percpu_ref`. Both variants include an optional stop callback and completion used by stop/wait paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/enumerated_ref_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.c

Implements Eytzinger-layout sorting for one-based and zero-based arrays. It includes optimized swap helpers for aligned 64-bit, aligned 32-bit, and byte-wise copying, plus wrapper support for comparator/swap signatures.

`eytzinger1_sort_r()` heapifies and sorts using Eytzinger index conversion so final array order supports cache-friendly Eytzinger search/traversal. Zero-based sort is implemented by biasing the base pointer and reusing the one-based routine. Contains disabled benchmark/test code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.h

Header for Eytzinger array layout helpers. It documents why the layout improves branch prediction/cache behavior compared with binary search and provides child, first/last, next/prev, inorder conversion, and traversal macros for one-based and zero-based indexing.

Inline search helpers return exact matches or lower/upper bounds, with one-based functions returning 0 for not found and zero-based functions returning -1. Sort function prototypes cover comparator-only and comparator-with-private-data variants.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fast_list.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/fast_list.c

Implements a fast unordered list backed by a generic radix tree, IDA slot allocator, and per-CPU free-slot buffers. `fast_list_get_idx()` reserves a slot with allocation failures handled early, refilling the per-CPU buffer in batches. `fast_list_add()` reserves and stores an item; `fast_list_remove()` clears the radix slot and returns the index to the per-CPU buffer.

`fast_list_put_idx()` drains excess per-CPU buffered entries back to the IDA. Init sets up radix/IDA/percpu state; exit frees buffered slots, warns if live objects remain, destroys the IDA, and frees radix storage.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fast_list.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fast_list.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/util/fast_list.h

Public fast-list interface. Defines `struct fast_list` as a generic radix tree of pointers plus IDA and per-CPU buffer. Iteration skips NULL slots with a `genradix_iter`, and macros provide full or start-offset iteration.

Exports slot reservation/return, add/remove, direct set, init, and exit. The design supports lockless add/remove/iteration except when per-CPU slot buffers refill or drain.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/util/fast_list.h -->