# subset-b-005618 Research

Grouped source research for selected Btrfs ioctl, locking, cache, compression, messaging, ordered-data, and orphan modules. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/ioctl.c

## Purpose
`ioctl.c` is Btrfs' user-control surface for inode flags, subvolume and snapshot lifecycle, device management, scrub, balance, quotas, feature flags, tree/backref queries, encoded I/O, fs-verity delegation, sync controls, and forced shutdown. It is the switchboard behind `btrfs_ioctl()`, `btrfs_compat_ioctl()`, file attribute get/set, and the Btrfs io_uring encoded I/O command implementation. The source was read as a complete 5320-line file.

## Important APIs, Types, and Functions
Exported entry points are `btrfs_ioctl()`, `btrfs_compat_ioctl()`, `btrfs_fileattr_get()`, `btrfs_fileattr_set()`, `btrfs_ioctl_get_supported_features()`, `btrfs_sync_inode_flags_to_i_flags()`, `btrfs_update_ioctl_balance_args()`, `btrfs_uring_cmd()`, and `btrfs_uring_read_extent_endio()`. Compat-only UAPI shims define packed 32-bit variants for received-subvol timestamps, send args, and encoded I/O args.

Major helper groups are inode flag translation and validation; fitrim; subvolume and snapshot creation/deletion/status; tree search and inode/path lookup; device add/remove/resize/info/stats/replace; space-info reporting; transaction sync and wait; scrub; balance start/control/progress; quota and qgroup operations; received-subvolume metadata updates; filesystem label and feature flag updates; send ioctl adaptation; encoded read/write through ioctl and io_uring; subvolume deletion wait modes; and shutdown handling.

## Control Flow
`btrfs_ioctl()` decodes the command and dispatches directly to a command-specific helper. Mutating paths consistently check capability or ownership, call `mnt_want_write_file()` where needed, validate copied UAPI structures before changing state, then use Btrfs transactions or exclusive-operation state to serialize filesystem-wide work.

Subvolume creation flows through `btrfs_ioctl_snap_create*()` into `__btrfs_ioctl_snap_create()`, `btrfs_mksubvol()`, then either `create_subvol()` or `create_snapshot()`. New subvolumes allocate an objectid and anonymous device, reserve metadata/qgroup space, create a root item/tree block/UUID item/inode, record the new root in the transaction, set orphan cleanup state, and instantiate the dentry. Snapshots force delalloc, wait ordered extents, use `pending_snapshot`, and commit the transaction to materialize the snapshot. Deletion validates name or id, resolves out-of-mount subvolumes when requested, enforces admin or `USER_SUBVOL_RM_ALLOWED` policy, then calls `btrfs_delete_subvolume()`.

Device and allocator flows use exclusive operations. Resize parses `devid:size`, `+/-` deltas, `max`, and `cancel`, then grows in a transaction or shrinks through the volume layer. Device add/remove, balance, and device replace reject unsupported extent-tree-v2 cases where noted and use the exclusive-operation framework to avoid conflicting relocations. Scrub copies progress back even on error so userspace can resume.

Query paths either walk B-trees under allocated `btrfs_path` objects or copy aggregate in-memory state. Tree search loops through `btrfs_search_forward()` and uses fault-in plus nofault copies to avoid repeated user faults. Inode/path lookup climbs inode refs and root refs, with the unprivileged variant checking read/execute permissions while building the path.

Encoded I/O imports user iovecs, verifies access, delegates to `btrfs_encoded_read()` or `btrfs_do_write_iter()`, and accounts task I/O. io_uring encoded read can return with inode and extent locks logically held until `btrfs_uring_read_finished()` copies pages to the user iterator and releases locks in task work.

## State and Persistence Behavior
Persistent changes include root tree items, UUID tree entries, root flags, default subvolume dir items, device tree/superblock device state, qgroup items, feature flags in the superblock, filesystem label, received-subvolume UUID/time/transid fields, file inode flags/properties, and subvolume-deletion queues. Runtime-only state includes exclusive operation markers, scrub/balance/dev-replace progress structures, root and subvolume semaphores, radix/dead-root lists, pending io_uring command state, and copied UAPI buffers.

Transactions protect metadata changes, `subvol_sem` serializes root visibility and readonly flag changes, `balance_mutex` and exclusive-operation state serialize global relocation/device work, `super_lock` protects the in-memory superblock label/feature fields, and inode/extent locks protect encoded I/O ranges.

## Dependencies and Integration Points
This file integrates with VFS ioctl/fileattr/fsnotify/verity/io_uring APIs, Linux capability and usercopy helpers, Btrfs transaction/root/extent/volume/qgroup/scrub/balance/send/defrag/backref/compression/tree-log/uuid subsystems, block discard for fitrim, and userspace UAPI structures from `<linux/btrfs.h>`. It is the principal kernel endpoint for btrfs-progs operations.

## Risks and Edge Cases
High-risk areas are UAPI structure validation, compat packing, user pointer copy/fault behavior, and keeping ioctl output useful on partial failures. Mutating ioctls must not start transactions before cheap validation that avoids malicious transaction aborts, as shown by UUID tree overflow checks. Subvolume deletion by id has idmapped-mount restrictions to prevent deleting unrelated subvolumes through a remapped fd. Snapshot creation and deletion are explicitly blocked for extent-tree-v2. Encoded io_uring read deliberately spans async completion with locks held and therefore relies on explicit lockdep annotations and exact cleanup. Exclusive-operation cancellation must distinguish no-op, in-progress, and cancel states.

## Test Signals
Useful signals include xfstests for subvolume create/delete/sync, snapshot readonly transitions during send, idmapped mount deletion restrictions, tree-search v1/v2 overflow behavior, 32-bit compat ioctl packing, device add/remove/resize/cancel conflicts, balance pause/resume/cancel/progress, scrub progress on cancellation, qgroup enable/assign/limit/rescan, feature flag safe set/clear rejection, label length validation, encoded read/write and io_uring encoded read/write including `NOWAIT`/reissue, fsverity ioctl passthrough, shutdown modes, and fault injection for usercopy/allocation/transaction failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ioctl.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/ioctl.h

## Purpose
`ioctl.h` is the private declaration boundary for Btrfs ioctl and file-attribute helpers. It lets inode/file operation tables, io_uring command paths, and other Btrfs modules call the implementation in `ioctl.c` without exposing implementation details. The source was read as a complete 29-line header.

## Important APIs, Types, and Functions
The header forward-declares kernel and Btrfs types used by the prototypes: `struct file`, `dentry`, `mnt_idmap`, `file_kattr`, `io_uring_cmd`, `btrfs_inode`, `btrfs_fs_info`, and `btrfs_ioctl_balance_args`. It declares `btrfs_ioctl()`, `btrfs_compat_ioctl()`, `btrfs_fileattr_get()`, `btrfs_fileattr_set()`, `btrfs_ioctl_get_supported_features()`, `btrfs_sync_inode_flags_to_i_flags()`, `btrfs_update_ioctl_balance_args()`, `btrfs_uring_cmd()`, and `btrfs_uring_read_extent_endio()`.

## Control Flow
There is no independent runtime flow. The prototypes connect VFS file operations and io_uring command dispatch to `ioctl.c`, and allow shared helpers such as inode flag synchronization and balance-argument reporting to be reused elsewhere.

## State and Persistence Behavior
The header defines no state. It advertises functions that may alter persistent filesystem metadata, inode state, or async I/O command state in the implementation.

## Dependencies and Integration Points
The only direct include is `<linux/types.h>`. The declarations integrate with Btrfs inode operations, file operations, balance code, and io_uring command handling.

## Risks and Edge Cases
Prototype drift here would break cross-module builds or cause mismatches in compat/io_uring call signatures. The `void __user *` prototype for supported features preserves UAPI-copy semantics from the implementation.

## Test Signals
Build coverage with Btrfs, compat ioctl, fileattr, and io_uring enabled is the main signal. Runtime coverage comes through the `ioctl.c` tests for each declared operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/locking.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/locking.c

## Purpose
`locking.c` implements Btrfs extent-buffer tree locking and the double-reader-writer-exclusion lock used by snapshot/COW coordination. It also assigns debug lockdep classes to tree blocks based on Btrfs root objectid and tree level. The source was read as a complete 383-line file.

## Important APIs, Types, and Functions
Lockdep helpers are `btrfs_set_buffer_lockdep_class()` and `btrfs_maybe_reset_lockdep_class()` under `CONFIG_DEBUG_LOCK_ALLOC`. Tree-locking APIs are `btrfs_tree_read_lock_nested()`, `btrfs_try_tree_read_lock()`, `btrfs_tree_read_unlock()`, `btrfs_tree_lock_nested()`, `btrfs_tree_unlock()`, `btrfs_unlock_up_safe()`, `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()`. DREW APIs are `btrfs_drew_lock_init()`, `btrfs_drew_try_write_lock()`, `btrfs_drew_write_lock()`, `btrfs_drew_write_unlock()`, `btrfs_drew_read_lock()`, and `btrfs_drew_read_unlock()`.

## Control Flow
Extent-buffer locking is a thin rwsem wrapper. Read and write lock calls optionally capture start timestamps for tracepoints, acquire the rwsem with a lockdep nesting subclass, and emit trace events. Write locking records `eb->lock_owner` in debug builds and clears it on unlock.

Root-node locking loops until the locked extent buffer reference is still the current `root->node`; if the root changed after taking a reference, the code unlocks/frees that buffer and retries. The try-read variant returns `ERR_PTR(-EAGAIN)` instead of sleeping when the initial read lock cannot be acquired.

DREW write acquisition increments the writer count only if there are no readers, then uses a memory barrier before rechecking readers. If a reader appeared, it releases and retries through a waitqueue. Reader acquisition increments the reader count first, barriers, then waits for writers to drain, which gives pending readers priority over new writers. Unlock paths wake the opposite side when the active count drops to zero.

## State and Persistence Behavior
There is no durable state. Runtime state lives in extent-buffer rwsems, optional debug lock-owner fields, per-root/per-level lockdep class keys, `btrfs_path->locks[]`, and `struct btrfs_drew_lock` atomics/waitqueues.

## Dependencies and Integration Points
The file depends on Btrfs `ctree.h`, `extent_io.h`, and `locking.h`, Linux rwsem/spin/page/scheduler facilities, lockdep, and Btrfs tracepoints. Tree traversal, COW, balancing, root replacement, snapshot creation, and path cleanup rely on these primitives.

## Risks and Edge Cases
Incorrect lockdep class assignment can hide real deadlocks or create false positives across roots and tree levels. Root-node locking must retry because root replacement can race with grabbing a buffer reference. `btrfs_unlock_up_safe()` intentionally ignores normal search-slot lock retention rules and is only valid when higher-level updates are done. DREW is reader-priority; sustained readers can delay writers, and its memory barriers are essential for preventing A/B overlap.

## Test Signals
Signals include lockdep-enabled fstests for tree COW/split/balance/snapshot paths, tracepoint sanity for read/write lock timings, stress tests with root node replacement during traversal, nowait root read-lock returning `-EAGAIN`, and snapshot/delalloc stress that validates DREW exclusion without reader/writer overlap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/locking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/locking.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/locking.h

## Purpose
`locking.h` declares Btrfs tree-locking primitives, lockdep wait-event annotations, transaction-state lockdep maps, lock nesting subclasses, and the DREW lock structure. The source was read as a complete 251-line header.

## Important APIs, Types, and Functions
Constants `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` encode path lock kinds. `enum btrfs_lock_nesting` defines the normal, COW, left/right sibling, split, and new-root subclasses constrained by `MAX_LOCKDEP_SUBCLASSES`. `enum btrfs_lockdep_trans_states` names transaction state wait maps.

Macros include `btrfs_might_wait_for_event()`, `btrfs_lockdep_acquire()`, `btrfs_lockdep_release()`, inode-lock handoff annotations for io_uring encoded I/O, transaction-state wait annotations, and lockdep map initializers. Inline helpers wrap normal read/write tree lock acquisition, tree unlock by lock kind, and debug assertions. `struct btrfs_drew_lock` contains reader/writer atomics and waitqueues.

## Control Flow
The header provides inline call paths from generic tree code into the nested lock implementations in `locking.c`. The lockdep annotation macros model wait-event conditions as rwsem dependencies so lockdep can reason about threads that wait for ordered extents or transaction states without holding the concrete wakeup condition.

## State and Persistence Behavior
No persistent state is defined. Runtime state includes lockdep maps embedded in owning structures, extent-buffer rwsems, path lock arrays, and DREW reader/writer counters.

## Dependencies and Integration Points
The header includes Linux atomic, waitqueue, lockdep, percpu-counter support, and Btrfs `extent_io.h`. It is included widely by Btrfs tree, transaction, ordered extent, snapshot, and io_uring code.

## Risks and Edge Cases
The nesting enum consumes all currently allowed lockdep subclasses; adding values without raising limits trips the static assertion. Annotation misuse can either create noisy lockdep reports or fail to model a real wait dependency. `btrfs_tree_unlock_rw()` BUGs on invalid lock kind, so path lock bookkeeping must be exact.

## Test Signals
All Btrfs builds exercise prototype consistency. Lockdep builds with snapshot, tree balance, relocation, qgroup, and ordered-extent wait tests are the strongest coverage. io_uring encoded read tests cover the inode-lock annotation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/locking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.c

## Purpose
`lru_cache.c` implements a small generic Btrfs LRU cache built from a global LRU list plus a maple tree keyed by the low bits of a u64 key. It supports optional generations per key and evicts the least-recently-used entry when a bounded cache reaches capacity. The source was read as a complete 166-line file.

## Important APIs, Types, and Functions
The exported functions are `btrfs_lru_cache_init()`, `btrfs_lru_cache_lookup()`, `btrfs_lru_cache_store()`, `btrfs_lru_cache_remove()`, and `btrfs_lru_cache_clear()`. The internal `match_entry()` scans the list stored for a maple-tree key and matches the full u64 key plus generation.

## Control Flow
Initialization sets up the LRU list, maple tree, size, and max size. Lookup loads the per-key list from the maple tree, scans for matching key/generation, and moves a hit to the LRU tail. Store allocates a new list head, attempts maple-tree insert, folds into an existing key list on `-EEXIST`, rejects duplicate key/generation pairs, evicts the oldest entry if the bounded cache is full, then appends the new entry to both the per-key list and the LRU list. Remove unlinks both list memberships, erases and frees an empty maple-tree bucket, frees the entry, and decrements size. Clear repeatedly removes entries from the LRU list.

## State and Persistence Behavior
All state is volatile memory in `struct btrfs_lru_cache`, per-key list heads stored in the maple tree, and caller-allocated entries that this module frees with `kfree()`. There is no locking in this module; callers must serialize access.

## Dependencies and Integration Points
The file depends on Linux maple tree and list APIs through `lru_cache.h`, allocation helpers, and Btrfs `ASSERT()` from `messages.h`. It is intended as an embedded-entry utility for Btrfs code that needs a small keyed cache.

## Risks and Edge Cases
Entries must embed `struct btrfs_lru_cache_entry` at offset zero and be `kmalloc()`-allocated because removal frees the entry directly. Duplicate key/generation insertion returns `-EEXIST` after the caller has already allocated the entry, so the caller owns cleanup. The per-key linked-list design handles 32-bit maple-tree key truncation but is efficient only when generation collisions are small. The lack of internal locking is a contract that must be respected by users.

## Test Signals
Unit-style tests should cover lookup recency updates, duplicate rejection, max-size eviction, unlimited-size mode, removal of the last entry in a maple-tree bucket, mixed generations for the same key, 32-bit key-collision behavior, and clear assertions leaving an empty tree and zero size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.h

## Purpose
`lru_cache.h` defines the public structure contract for the generic Btrfs LRU cache implemented in `lru_cache.c`. The source was read as a complete 71-line header.

## Important APIs, Types, and Functions
`struct btrfs_lru_cache_entry` contains LRU linkage, a u64 key, an optional generation, and linkage for the per-maple-tree bucket list. `struct btrfs_lru_cache` contains the LRU list, maple tree, current size, and maximum size. The header declares all cache operations and provides `btrfs_lru_cache_for_each_entry_safe()` plus `btrfs_lru_cache_lru_entry()`.

## Control Flow
There is no independent flow. Consumers embed the entry as the first field of their own allocation, initialize a cache, store and lookup entries, and either explicitly remove/clear them or allow bounded store to evict the oldest entry.

## State and Persistence Behavior
The header defines in-memory cache state only. Entries are owned by the cache after successful store and are freed by removal or eviction.

## Dependencies and Integration Points
It includes Linux `types.h`, `maple_tree.h`, and `list.h`. It integrates with `lru_cache.c` and any Btrfs subsystem that needs u64-keyed LRU caching with optional generations.

## Risks and Edge Cases
The offset-zero and `kmalloc()` allocation requirements are semantic, not compiler-enforced. On 32-bit systems, the maple tree indexes only the lower unsigned-long part of a u64 key, so correctness depends on retaining and comparing the full key in each entry.

## Test Signals
Build coverage catches API drift. Behavioral signals are the `lru_cache.c` tests around duplicate generations, key collisions, eviction order, and clear/remove ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lzo.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/lzo.c

## Purpose
`lzo.c` implements Btrfs' LZO compression backend. It allocates per-worker LZO workspaces, compresses file data into Btrfs' segmented LZO on-disk format, and decompresses both regular compressed bios and inline compressed extents. The source was read as a complete 583-line file.

## Important APIs, Types, and Functions
Public functions are `lzo_alloc_workspace()`, `lzo_free_workspace()`, `lzo_compress_bio()`, `lzo_decompress_bio()`, `lzo_decompress()`, and the `btrfs_lzo_compress` level descriptor. `struct workspace` owns LZO working memory, an uncompressed buffer, a compressed buffer, and list linkage. Internal helpers include workspace size helpers, `write_and_queue_folio()`, `copy_compressed_data_to_bio()`, `get_current_folio()`, and `copy_compressed_segment()`.

## Control Flow
Compression allocates an output folio, reserves the first 4-byte total-length header, walks input file folios sector by sector, compresses each sector with `lzo1x_1_compress()`, writes a 4-byte segment length plus payload, pads with zeros when needed so the next segment header never crosses a sector boundary, and finally patches the total compressed length into the first header. It aborts with `-E2BIG` if compression grows too much, especially after the first two sectors.

Bio decompression reads the total LZO length from the first folio, validates it against the compressed bio size and maximum compressed extent size, then iterates segment headers and payloads. Each segment payload is copied into the workspace compressed buffer, decompressed with `lzo1x_decompress_safe()`, and copied into destination inode pages through the generic Btrfs decompression helper. Inline decompression validates the two headers expected for a single segment, decompresses into the workspace buffer, copies to the destination folio, zero-fills short output, and returns an error on early end.

## State and Persistence Behavior
Workspace allocations are runtime-only. Persistent format state is the bytes written into compressed extents: a little-endian total length followed by per-segment little-endian payload lengths, payloads, and at most three bytes of sector padding before the next segment header. The compression level descriptor advertises only level 1.

## Dependencies and Integration Points
The file integrates with Linux LZO, bio/folio APIs, Btrfs compression infrastructure, compressed bio lifecycle, inode/root metadata for error logging, and filesystem sector/minimum-folio sizing. It is selected through Btrfs compression type dispatch.

## Risks and Edge Cases
The on-disk segment layout is strict: segment headers must fit in one sector, total length must not exceed the actual compressed bio, and padding must be skipped correctly. Corrupt headers can cause `-EUCLEAN` or `-EIO`; diagnostics include root, inode, and offset. Large folio and subpage behavior depends on offset calculations and `bio_get_size()`. `write_and_queue_folio()` assumes bio vector merging behaves as expected and returns `-E2BIG` on bvec-limit pressure. Inline decompression treats short decompressed output as an error after zero-filling.

## Test Signals
Signals include compression/decompression round trips with multiple sectors, sector-boundary header padding, incompressible data returning `-E2BIG`, inline LZO extents, corrupt total length, oversized segment length, decompressor failure injection, large folio/min-folio configurations, non-4K sectors, and mount/read tests that verify logged root/inode/offset diagnostics on corrupted compressed extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/lzo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/messages.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/messages.c

## Purpose
`messages.c` implements Btrfs logging, filesystem-error handling, fatal panic reporting, and 32-bit logical-address warnings. It centralizes message prefixes, filesystem-state suffixes, rate limiting, and the transition to forced-readonly on serious errors. The source was read as a complete 301-line file.

## Important APIs, Types, and Functions
Important functions are `btrfs_decode_error()`, `__btrfs_handle_fs_error()`, `_btrfs_printk()` under `CONFIG_PRINTK`, `btrfs_warn_32bit_limit()` and `btrfs_err_32bit_limit()` on 32-bit builds, and `__btrfs_panic()`. Internal helpers include `btrfs_state_to_string()`, the state-character table, log-level names, and per-log-level ratelimit states.

## Control Flow
Generic Btrfs printk macros call `_btrfs_printk()`, which formats messages as `BTRFS <level> (device <id><state>): ...`, appends compact state flags when unusual filesystem states are set, and applies per-level ratelimiting unless debug builds disable it. `__btrfs_handle_fs_error()` ignores benign `-EROFS` on an already readonly superblock, logs a critical error with decoded errno and caller location, records `fs_info->fs_error`, and after mount completion stops discard and marks the superblock readonly. `__btrfs_panic()` formats a fatal message and either calls `panic()` when the mount option requests it or logs a critical message before the caller's BUG.

## State and Persistence Behavior
There is no file-backed persistence. Runtime state changes include `fs_info->fs_error`, superblock readonly state, discard state, and one-shot 32-bit warning/error flags. The state-string reflects `fs_info->fs_state` and `BTRFS_FS_ERROR()`.

## Dependencies and Integration Points
The file depends on Btrfs `fs.h`, `messages.h`, `discard.h`, and `super.h`, plus kernel printk, ratelimit, panic, and superblock APIs. It is used by nearly all Btrfs modules through macros in `messages.h`.

## Risks and Edge Cases
Error handling must avoid forcing readonly before the superblock is fully born and must avoid noisy repeated messages. The compact state string intentionally omits non-error RO state but adds emergency/error characters. Device replace is not canceled during forced readonly to avoid deadlock, so status persistence can lag. Rate limiting is per log level globally, which prevents low-severity floods from suppressing critical messages but can still hide repeated same-level diagnostics.

## Test Signals
Signals include printk-prefix tests under normal and stateful filesystems, forced-readonly behavior after injected transaction/metadata errors, no-op behavior for `-EROFS` on readonly mounts, panic-on-fatal-error mount option tests, ratelimit behavior, discard stop observation, and 32-bit threshold warning/error one-shot behavior on 32-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/messages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/messages.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/messages.h

## Purpose
`messages.h` declares and defines the Btrfs diagnostic API: printk wrappers, dynamic debug hooks, assertions, debug warnings, filesystem error handling, fatal panic handling, and 32-bit address-limit helpers. The source was read as a complete 207-line header.

## Important APIs, Types, and Functions
It declares `_btrfs_printk()`, `__btrfs_handle_fs_error()`, `btrfs_decode_error()`, `__btrfs_panic()`, and 32-bit limit helpers. Macros include `btrfs_crit/err/warn/info`, ratelimited variants, `btrfs_debug`, `btrfs_debug_rl`, `ASSERT()`, `DEBUG_WARN()`, `btrfs_handle_fs_error()`, and `btrfs_panic()`. `ASSERT()` supports optional printf-style context under `CONFIG_BTRFS_ASSERT` and compiles only the expression otherwise.

## Control Flow
Callers use severity macros that wrap `_btrfs_printk()` in RCU read-side protection when printk is enabled, or compile to no-op/no-printk paths when disabled. Ratelimited macros create static per-callsite ratelimit state. `btrfs_handle_fs_error()` injects function and line into the implementation. `btrfs_panic()` calls the implementation and then BUGs unless the implementation panicked first.

## State and Persistence Behavior
The header defines no durable state. It shapes runtime behavior through callsite ratelimit states, assertions that can BUG, and error/panic wrappers that may force readonly or crash the kernel via the implementation.

## Dependencies and Integration Points
The header depends on Linux printk and bug APIs and forward-declares `struct btrfs_fs_info`. It is a ubiquitous dependency for Btrfs modules that need diagnostics or invariants.

## Risks and Edge Cases
The debug branch contains a typo-like `LOGLEVEl_DEBUG` in the non-dynamic `DEBUG` `btrfs_debug_rl` path, which would matter only under that compile path. Assertion varargs are carefully constructed around `__VA_OPT__`; compiler support assumptions matter. Panic and ASSERT macros intentionally stop the kernel, so they must be reserved for impossible invariants.

## Test Signals
Build matrices with `CONFIG_PRINTK`, `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, `CONFIG_BTRFS_ASSERT`, and 32-bit builds are the strongest signals. Runtime signals come from injected errors, assertion-only debug builds, ratelimited logging, and fatal error mount-option tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/misc.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/misc.h

## Purpose
`misc.h` collects small Btrfs utility macros and inline helpers for cleanup attributes, enum bit generation, bio/block iteration, conditional wakeups, percent arithmetic, power-of-two checks, simple bytenr-indexed rbtrees, and bitmap range predicates. The source was read as a complete 227-line header.

## Important APIs, Types, and Functions
Important macros and helpers are `AUTO_KFREE`, `AUTO_KVFREE`, `ENUM_BIT`, `bio_iter_phys()`, `btrfs_bio_for_each_block()`, `bio_get_size()`, `init_bvec_iter_for_bio()`, `btrfs_bio_for_each_block_all()`, `cond_wake_up()`, `cond_wake_up_nomb()`, `mult_perc()`, `is_power_of_two_u64()`, `has_single_bit_set()`, `struct rb_simple_node`, `rb_simple_search()`, `rb_simple_search_first()`, `rb_simple_insert()`, `bitmap_test_range_all_set()`, and `bitmap_test_range_all_zero()`.

## Control Flow
Bio helpers iterate over bio vectors in filesystem block-size increments and expose physical addresses for each step. Conditional wake helpers avoid wakeups when no waiter is present; `cond_wake_up()` relies on `wq_has_sleeper()` for the needed barrier, while `cond_wake_up_nomb()` is for callers that already established ordering. Rbtree helpers search exact bytenr, first entry at or after bytenr, and insert using `rb_find_add()`.

## State and Persistence Behavior
The header owns no global state. It manipulates caller-owned bios, waitqueues, rbtrees, bitmap ranges, and cleanup-attributed local pointers.

## Dependencies and Integration Points
It includes Linux bitmap, scheduler, waitqueue, MM/page cache, math64, rbtree, and bio APIs. Ordered-data, checksum, extent, and block-group paths use these utilities to reduce duplicate helper code.

## Risks and Edge Cases
`bio_get_size()` is documented for non-cloned bios only. Bio block iteration assumes folios cover at least one block and that advancing by blocksize is valid. `cond_wake_up_nomb()` is only correct when a prior atomic or lock/unlock sequence provides the memory ordering. `rb_simple_node` requires bytenr fields at the beginning of embedding structures.

## Test Signals
Signals include build coverage across bio API changes, large-folio and highmem bio iteration tests, waitqueue race tests for ordered extents, rbtree exact/first insertion tests, bitmap range edge cases, and static analysis for cleanup-attribute use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.c

## Purpose
`ordered-data.c` manages Btrfs ordered extents: in-memory records that bridge data writeback completion and metadata insertion. Ordered extents serialize overlapping writes, track checksums, qgroup reservations, outstanding extent accounting, root-wide wait lists, fsync logging state, completion work, and error propagation. The source was read as a complete 1357-line file.

## Important APIs, Types, and Functions
Public APIs include `btrfs_alloc_ordered_extent()`, `btrfs_add_ordered_sum()`, `btrfs_mark_ordered_extent_error()`, `btrfs_finish_ordered_extent()`, `btrfs_mark_ordered_io_finished()`, `btrfs_dec_test_ordered_pending()`, `btrfs_put_ordered_extent()`, `btrfs_remove_ordered_extent()`, `btrfs_wait_ordered_extents()`, `btrfs_wait_ordered_roots()`, `btrfs_start_ordered_extent_nowriteback()`, `btrfs_wait_ordered_range()`, lookup helpers, logging collection, ordered-range lock helpers, `btrfs_split_ordered_extent()`, `ordered_data_init()`, and `ordered_data_exit()`. Internal rb-tree helpers implement non-overlap insertion, cached searches, and range-overlap detection.

## Control Flow
Allocation validates flag combinations, transfers or frees qgroup reservations depending on COW versus NOCOW/PREALLOC, initializes the ordered extent, grabs the inode, increments outstanding extents, inserts into the per-inode rb-tree, adds it to the per-root ordered list, and adds the root to the filesystem ordered-root list when needed.

I/O completion decrements `bytes_left` under `ordered_tree_lock`. When the final byte finishes, it sets `BTRFS_ORDERED_IO_DONE`, wakes waiters, takes a reference, and queues `finish_ordered_fn()` to the appropriate endio workqueue. Error completion marks mapping error and, for failed COW writes, sets an inode runtime flag forcing future fast fsync to wait for completion before logging extent maps.

Removal is called after metadata completion. It updates outstanding extents, releases delalloc metadata, subtracts ordered bytes, erases the rb-node, clears cached lookup state, sets `BTRFS_ORDERED_COMPLETE`, wakes transaction waiters if `BTRFS_ORDERED_PENDING` was set, removes the root-list entry, and wakes extent waiters. Refcount release frees checksum sums, schedules delayed iput, and returns the object to the kmem cache.

Wait flows either target one inode range, one root list, or all roots. `btrfs_wait_ordered_range()` starts writeback, waits writeback errors, then walks ordered extents backward through the range and waits each one. `btrfs_wait_ordered_extents()` splices root extents, queues flush work for up to `nr` matching extents, waits completions, and restores skipped entries. Range lock helpers repeatedly lock the extent state, check for overlapping ordered extents, unlock and wait until none remain.

Splitting creates a new leading ordered extent, trims the original offsets/lengths/checksum list, and updates both the inode rb-tree and root list under the root and inode locks to avoid races with ordered-extent waiters.

## State and Persistence Behavior
Ordered extents are volatile memory but represent pending persistent changes to file extent items and checksums. State lives in `struct btrfs_ordered_extent`, per-inode `ordered_tree` and cache pointer, per-root `ordered_extents` and count, global `ordered_roots`, `fs_info->ordered_bytes`, transaction `pending_ordered`, qgroup reservations, and workqueue/completion objects. Persistent metadata is written by the finish path declared externally, not by this file directly.

## Dependencies and Integration Points
The module integrates with transactions, Btrfs inode and extent I/O trees, compression/encoded writes, delalloc space accounting, qgroups, subpage support, file writeback, block groups, tracepoints, and lockdep wait-event annotations from `locking.h`/`misc.h`. It depends on `btrfs_finish_one_ordered()` and `btrfs_finish_ordered_io()` implementations elsewhere.

## Risks and Edge Cases
Overlapping ordered extents are fatal and trigger `btrfs_panic()`. Accounting must keep `bytes_left`, delalloc metadata, qgroup reservations, and outstanding extents consistent across success, errors, truncation, direct I/O, compressed writes, encoded writes, and NOCOW/PREALLOC. Failed COW writeback can otherwise let fast fsync log unwritten extent maps. Range wait logic intentionally waits all extents even after writeback error to avoid re-dirty races and `-EEXIST` on reinsertion. Splitting rejects compressed or partially inconsistent extents and has careful lock ordering to avoid races with root-level waiters.

## Test Signals
Signals include xfstests for buffered and direct writes, compressed and encoded writes, NOCOW/PREALLOC writes, qgroup accounting, ENOSPC/error injection during writeback, fast fsync after write errors, truncate/split ordered extents, ordered-range lock nowait behavior, root-wide waits during snapshot/balance, transaction pending-ordered waits, and KCSAN/lockdep stress around splitting and root ordered lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.h

## Purpose
`ordered-data.h` defines the ordered-extent state model and public API used by Btrfs writeback, direct I/O, fsync, transaction commit, compression, and range-locking code. The source was read as a complete 232-line header.

## Important APIs, Types, and Functions
`struct btrfs_ordered_sum` stores checksum ranges and variable-length checksum bytes. The flag enum defines status bits (`IO_DONE`, `COMPLETE`, `IOERR`, `TRUNCATED`, `LOGGED`, `LOGGED_CSUM`, `PENDING`) plus mutually exclusive type bits (`REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`) and extra `ENCODED`/`DIRECT` bits. `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` define valid masks.

`struct btrfs_ordered_extent` records file and disk offsets/lengths, compression, qgroup reservation, refcount, owning inode, checksum/log/root/work/bioc lists, rb-node, waitqueue, work items, and completion. `struct btrfs_file_extent` mirrors the file extent item details needed to allocate an ordered extent.

## Control Flow
The header has no standalone flow. It defines the state transitions used by `ordered-data.c`: allocate and insert, add checksum sums, mark I/O done or errored, queue finish work, remove from trees/lists, wait for completion, collect for logging, lock ranges with ordered extents flushed, and split a leading portion when needed.

## State and Persistence Behavior
The structures are in-memory records for pending on-disk file extent and checksum updates. They persist only until writeback completion metadata is inserted and the final reference is dropped. Flags encode both completion state and the kind of file extent that will be committed.

## Dependencies and Integration Points
It includes list/refcount/completion/rbtree/waitqueue primitives and Btrfs async work support. It forward-declares inode/root/fs/block-group/extent-state types and is consumed by writeback, compression, direct I/O, fsync/tree-log, transaction, and ordered-data implementation code.

## Risks and Edge Cases
Exactly one exclusive type flag must be set by callers. `ENCODED` must pair with `COMPRESSED`, while `DIRECT` must not pair with compressed/encoded. Mismanaging `log_list`, root list, or rb-node membership can leak references or let fsync miss pending extents. `qgroup_rsv` is declared as `int` while reservations are u64 in the implementation context, so value range assumptions should stay visible.

## Test Signals
Compile coverage catches flag and prototype drift. Runtime coverage comes from ordered-data tests for each flag combination, compressed/encoded/direct paths, fsync logging, checksum insertion, truncation, splitting, and transaction waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/orphan.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/orphan.c

## Purpose
`orphan.c` provides the minimal helpers for inserting and deleting Btrfs orphan items. Orphan items record objectids that need cleanup after unlink/truncate/crash recovery. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions
The file exports `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()`. Both construct a key with `objectid = BTRFS_ORPHAN_OBJECTID`, `type = BTRFS_ORPHAN_ITEM_KEY`, and caller-provided `offset`.

## Control Flow
Insertion allocates a path and calls `btrfs_insert_empty_item()` with zero item size. Deletion allocates a path, searches with modification intent (`ins_len = -1`, cow allowed), returns search errors or `-ENOENT` if absent, and deletes the found item with `btrfs_del_item()`.

## State and Persistence Behavior
The helpers mutate persistent B-tree items inside the provided root and transaction. There is no local runtime state beyond the temporary path and key. Orphan cleanup elsewhere consumes these records after mount or subvolume lookup.

## Dependencies and Integration Points
The file depends on `ctree.h` for B-tree path/key/item operations and `orphan.h` for declarations. It is used by inode lifecycle and orphan cleanup code.

## Risks and Edge Cases
Callers must provide a valid transaction and root and reserve enough metadata. Deleting a missing orphan reports `-ENOENT`; callers must decide whether that is expected. Since item size is zero, the key is the entire persistent payload.

## Test Signals
Signals include orphan insert/delete round trips, mount recovery after crash with orphan items, deletion of absent items, allocation failure for `btrfs_alloc_path()`, and transaction abort handling in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/orphan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/orphan.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/orphan.h

## Purpose
`orphan.h` declares the Btrfs orphan-item insertion and deletion helpers. The source was read as a complete 16-line header.

## Important APIs, Types, and Functions
It forward-declares `struct btrfs_trans_handle` and `struct btrfs_root`, and declares `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()` with a transaction, root, and u64 offset.

## Control Flow
There is no runtime flow in the header. Callers include it to create or remove zero-length `BTRFS_ORPHAN_ITEM_KEY` records through `orphan.c`.

## State and Persistence Behavior
The header defines no state. The declared functions mutate persistent orphan items in Btrfs trees.

## Dependencies and Integration Points
It includes `<linux/types.h>` for `u64` and integrates with Btrfs inode lifecycle, truncate/unlink, and orphan cleanup paths.

## Risks and Edge Cases
The small API hides required transaction reservation and caller policy for missing items. Prototype drift would break orphan cleanup users.

## Test Signals
Build coverage plus orphan recovery tests validate the header and implementation contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/orphan.h -->
