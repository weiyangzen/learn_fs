# Research Report: subset-b-005741

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stack_user.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/stack_user.c

Purpose: implements the OCFS2 "user" cluster stack plugin, bridging OCFS2 to the kernel `fs/dlm` lockspace and to userspace cluster control through `/dev/ocfs2_control`. It supports two operating modes: older userspace-controlled notification via the misc device and newer `dlm_controld` recovery callbacks from `dlm_new_lockspace`.

Important APIs and types: the module registers `ocfs2_user_plugin` with stackglue. Internal state is carried by `struct ocfs2_live_connection` for a mounted filesystem lockspace and `struct ocfs2_control_private` for each control-device opener. The text protocol accepts `T01`, then `SETN`, `SETV`, and later `DOWN` messages. Stack operations include `user_cluster_connect`, `user_cluster_disconnect`, `user_cluster_this_node`, `user_dlm_lock`, `user_dlm_unlock`, `user_plock`, and LVB/status helpers.

Control flow: module init registers the misc control device and stack plugin. A control client must read the protocol tag to enter `READ`, write `T01` to enter `PROTOCOL`, then send node and protocol messages; only after both are installed does `ocfs2_control_opened` increment and mounts that require controllerd notification proceed. Mount connection creates a DLM lockspace, attaches a live connection, negotiates locking protocol through a DLM `VERSION_LOCK` LVB when not using controllerd, waits for its own node id, and validates the negotiated protocol. DLM lock callbacks unwrap `struct ocfs2_dlm_lksb` and dispatch to OCFS2 lock AST, blocking AST, or unlock AST.

State and persistence behavior: all state is runtime kernel state. Global `ocfs2_control_this_node`, `running_proto`, live connection list, and opened count are protected by `ocfs2_control_lock`; dropping the last valid control opener resets node/protocol state, and if live filesystems still exist it triggers `emergency_restart`. The protocol version for uncontrolled operation is persisted only in the DLM lock value block for the active lockspace.

Dependencies and integration points: depends on `fs/dlm` lockspaces, DLM lock callbacks, DLM POSIX lock helpers, Linux miscdevice/uaccess APIs, reboot emergency handling, and `stackglue.h`. It is selected by stackglue for non-classic stack labels and is consumed by OCFS2 DLM glue, flock/plock paths, node recovery, and mount/unmount cluster connection setup.

Risks: the text control protocol is strict about exact message sizes and state transitions, so userspace tooling must match it exactly. The live connection list is dereferenced during DOWN notifications under a mutex; invalid lifetime handling would call recovery on stale mount state. Protocol negotiation mixes global state, DLM LVB state, and mount-time version compatibility. The emergency restart on unexpected control-device release is intentionally drastic and makes daemon lifetime a correctness boundary.

Test signals: open/read/write `/dev/ocfs2_control` handshake order, malformed `SETN`/`SETV`/`DOWN` sizes, multiple control openers with conflicting node or protocol values, mount without daemon in `WITH_CONTROLD` mode, DLM recovery callbacks, LVB version negotiation between two nodes, POSIX lock operations, and teardown with active and inactive live connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stack_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.c

Purpose: provides the central OCFS2 abstraction over cluster stack plugins. It selects and pins one active stack, exposes stack and protocol state through `/sys/fs/ocfs2`, runs the heartbeat cleanup helper on hangup, and forwards generic OCFS2 DLM and plock requests into the selected plugin operations.

Important APIs and functions: exported entry points include `ocfs2_stack_glue_register`, `ocfs2_stack_glue_unregister`, `ocfs2_stack_glue_set_max_proto_version`, `ocfs2_cluster_connect`, `ocfs2_cluster_connect_agnostic`, `ocfs2_cluster_disconnect`, `ocfs2_cluster_hangup`, `ocfs2_cluster_this_node`, `ocfs2_dlm_lock`, `ocfs2_dlm_unlock`, `ocfs2_dlm_lock_status`, `ocfs2_dlm_lvb_valid`, `ocfs2_dlm_lvb`, `ocfs2_dlm_dump_lksb`, `ocfs2_stack_supports_plocks`, and `ocfs2_plock`.

Control flow: stack drivers register into `ocfs2_stack_list`. Mount calls `ocfs2_cluster_connect`, which checks the requested locking protocol, allocates `ocfs2_cluster_connection`, selects a plugin based on the on-disk stack label (`o2cb` uses the classic plugin, all others use the user plugin), requests the module if missing, pins the active plugin, and calls its `connect`. Disconnect calls the plugin and drops the active-stack reference unless a later heartbeat hangup is pending. Sysfs allows reading the maximum locking protocol, loaded plugins, active plugin, and selected cluster stack; writes to `cluster_stack` are rejected while a different active stack is in use.

State and persistence behavior: `active_stack`, plugin counts, global `locking_max_version`, and configured `cluster_stack_name` are in-memory and protected by `ocfs2_stack_lock`. The active plugin is module-pinned while any connection exists. `ocfs2_hb_ctl_path` is mutable via sysctl and used for post-unmount heartbeat cleanup, but no filesystem metadata is changed here.

Dependencies and integration points: integrates with plugin modules such as `ocfs2_stack_o2cb` and `ocfs2_stack_user`, `request_module`, sysfs under the exported `ocfs2_kset`, proc sysctl, usermode helper execution, and the DLM-facing wrappers used throughout OCFS2 lock management. `super.c` relies on `ocfs2_kset` for per-device sysfs and on `ocfs2_cluster_hangup` during unmount.

Risks: only one active stack is allowed globally, so mixed-stack mounts should fail cleanly. Module reference counting depends on balanced connect, disconnect, and hangup paths. `ocfs2_cluster_stack_store` must not permit switching stacks after a plugin is active. The `call_usermodehelper` heartbeat cleanup is outside the journal/DLM transaction model and can fail after unmount decisions have been made.

Test signals: register/unregister duplicate stack plugins, mount with default `o2cb`, mount with a userspace stack label, request-module failure, concurrent mounts with conflicting stack labels, sysfs reads/writes while active and inactive, plock support checks for stacks with and without `.plock`, and unmount paths with `hangup_pending` both set and clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.h

Purpose: declares the public contract between OCFS2 filesystem code, the stackglue core, and cluster stack plugins. It hides stack-specific lock status block layouts behind common OCFS2 types and defines the callback surface a plugin must implement.

Important APIs and types: key definitions are `struct ocfs2_protocol_version`, `struct fsdlm_lksb_plus_lvb`, `struct ocfs2_dlm_lksb`, `struct ocfs2_locking_protocol`, `struct ocfs2_cluster_connection`, `struct ocfs2_stack_operations`, and `struct ocfs2_stack_plugin`. It also defines `DLM_LKF_LOCAL`, `GROUP_NAME_MAX`, and `CLUSTER_NAME_MAX`, and declares all cluster connect/disconnect, DLM lock, LVB, plock, protocol, and plugin registration functions.

Control flow: the header has no active control flow, but it establishes that filesystem code calls `ocfs2_cluster_connect`, then uses `ocfs2_dlm_lock` and related wrappers without inspecting stack-specific lksb internals. Stack plugins fill `ocfs2_stack_operations`; their connect callbacks must not return until recovery notifications and lock processing are operational.

State and persistence behavior: `ocfs2_cluster_connection` stores per-mount runtime state: group name, cluster name, negotiated protocol version, recovery callback and private data, plugin lockspace pointer, and plugin-private state. `ocfs2_dlm_lksb` embeds either o2dlm or fsdlm status storage plus the owning connection pointer. No on-disk state is represented directly.

Dependencies and integration points: includes Linux DLM public headers and OCFS2 DLM API definitions. It is included by filesystem lock glue, stack implementations, mount code, and sysfs setup. The `ocfs2_kset` export declared here links stackglue sysfs to per-device sysfs created by `super.c`.

Risks: the union size and embedded LVB padding must remain sufficient for every supported stack lock status block. Callback contracts are strong: disconnect must not return while a plugin can still reference the connection. The fake `DLM_LKF_LOCAL` flag must not collide with upstream DLM flags. Any protocol version mismatch is a mount-safety issue.

Test signals: build coverage for both o2cb and user stack plugins, lock/unlock/LVB operations through the opaque `ocfs2_dlm_lksb`, protocol negotiation with incompatible major/minor versions, stack plugins with NULL `.plock`, and module unload while no active connection exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/stackglue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.c

Purpose: implements OCFS2 suballocator logic for metadata blocks, inode blocks, and data clusters. It manages chain allocators, block group descriptors, local-versus-global cluster reservations, per-slot resource stealing, discontiguous block groups, allocation hints, and freeing/reclaiming allocator-owned space back to the main bitmap.

Important APIs and functions: public allocation entry points include `ocfs2_reserve_new_metadata_blocks`, `ocfs2_reserve_new_metadata`, `ocfs2_reserve_new_inode`, `ocfs2_reserve_clusters`, `ocfs2_reserve_cluster_bitmap_bits`, `ocfs2_claim_metadata`, `ocfs2_claim_new_inode`, `ocfs2_find_new_inode_loc`, `ocfs2_claim_new_inode_at_loc`, `ocfs2_claim_clusters`, `__ocfs2_claim_clusters`, `ocfs2_free_suballoc_bits`, `ocfs2_free_dinode`, `ocfs2_free_clusters`, `ocfs2_release_clusters`, `ocfs2_lock_allocators`, `ocfs2_test_inode_bit`, and `ocfs2_read_group_descriptor`. Core helpers validate descriptors, find clear bits, update dinode counts, set/clear group bits, relink chain heads, grow allocators, and reclaim empty suballocator groups.

Control flow: reservation first locks the appropriate system allocator inode with `inode_lock` and `ocfs2_inode_lock`, verifies it is a chain allocator, then grows it with a new block group if needed and allowed. Cluster reservations prefer local alloc when policy allows, otherwise use the global bitmap and may flush the truncate log once before failing ENOSPC. Claims search the last hint group, then the chain with most free bits, then other chains; successful claims journal dinode count updates and group bitmap bit changes. Freeing clears bits with journal undo semantics for cluster bitmaps, updates chain/dinode counts, and can reclaim an empty metadata/inode group back to the global bitmap.

State and persistence behavior: persistent state lives in OCFS2 dinodes, chain records, group descriptors, bitmaps, extent records for discontiguous groups, and JBD2 undo/committed data. Runtime state includes `struct ocfs2_alloc_context`, last allocation group hints on directories, `osb_inode_alloc_group`, steal-slot counters, allocation statistics, and cache invalidation for released group descriptors. Allocation changes are journaled through `ocfs2_journal_access_di/gd` and dirtied before commit.

Dependencies and integration points: depends on system inode lookup, inode cluster locks, JBD2 journal access, local alloc, truncate log freeing, metadata uptodate cache, blockcheck/ECC validation, extent list helpers, reservation maps, and OCFS2 tracepoints. It is called by file growth, extent insertion/splitting, inode creation, orphan creation, local alloc, truncate/release, and filesystem consistency checks.

Risks: allocator corruption has high blast radius; descriptor validation must catch bad signatures, parent pointers, generation mismatches, invalid bit counts, and discontig extent layout. Journal undo checks avoid reusing recently freed data clusters before delete transactions commit. Discontiguous group handling has to translate logical group bits to physical blocks correctly. The reclaim path mutates both suballocator and global bitmap in one transaction and contains subtle count updates. Per-slot stealing can create locality and fairness issues if counters or reset points regress.

Test signals: metadata/inode/data allocations under ENOSPC, local alloc fallback, truncate-log retry, chain relinking, discontiguous block group creation and cleanup, inode64 max-block behavior, preferred group hints for directory inode creation, freeing dinodes and clusters, reclaiming fully free suballocator groups, `ocfs2_test_inode_bit` on live and released groups, fsck-style descriptor corruption injection, and crash recovery around bitmap undo data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.h

Purpose: defines the suballocator API used by OCFS2 allocation, inode creation, extent growth, local alloc, and free paths. It exposes `struct ocfs2_alloc_context` as the reservation/claim state object passed across reservation and journaled claim phases.

Important APIs and types: declares `group_search_t`, `struct ocfs2_alloc_context`, allocation context modes `OCFS2_AC_USE_LOCAL`, `OCFS2_AC_USE_MAIN`, `OCFS2_AC_USE_INODE`, `OCFS2_AC_USE_META`, and `OCFS2_AC_USE_MAIN_DISCONTIG`, plus reservation, claim, free, descriptor, allocator-locking, and inode-bit test functions. Inline helpers compute remaining reserved bits, suballocator group block, cluster group start, and whether an inode is the global cluster bitmap.

Control flow: callers reserve resources with functions such as `ocfs2_reserve_new_inode`, `ocfs2_reserve_new_metadata`, or `ocfs2_reserve_clusters`, then consume them under a journal handle with `ocfs2_claim_*`, and finally release the context with `ocfs2_free_alloc_context`. The special find-location APIs split inode location choice from final claim to support orphan/reflink ordering.

State and persistence behavior: `ocfs2_alloc_context` holds referenced and locked allocator inode state, allocator buffer head, slot, requested and granted bits, search function, chain, last group hint, max block limit, optional reservation map, and deferred inode-location result. It is runtime-only but points at persistent allocator dinodes and group descriptors.

Dependencies and integration points: includes OCFS2 allocator consumers across `alloc.c`, file growth, inode creation, local alloc, and truncate/free logic. It relies on OCFS2 superblock fields for bitmap geometry and on chain allocator on-disk structures declared elsewhere.

Risks: callers must respect the reserve-then-claim lifetime and release locks through `ocfs2_free_alloc_context`. `ac_bits_given` must never exceed `ac_bits_wanted`. The inline group math assumes standard OCFS2 block group placement, with a special case for the first cluster group. Misusing `ocfs2_is_cluster_bitmap` changes journal undo behavior.

Test signals: compile coverage of all allocator consumers, allocation-context leak checks, reserve/claim/free under failures, inode location preclaim followed by exact-location claim, cluster group translation at first and later bitmap groups, and local alloc callers using `ocfs2_reserve_cluster_bitmap_bits`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/suballoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/super.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/super.c

Purpose: owns OCFS2 module initialization, mount-context parsing, superblock probing and initialization, mount and dismount sequencing, system inode loading, quota setup, debugfs/sysfs device exposure, statfs, sync, inode slab construction, and filesystem error handling.

Important APIs and functions: it defines `ocfs2_fs_type`, `ocfs2_sops`, fs_context operations, mount option parser tables, `ocfs2_fill_super`, `ocfs2_initialize_super`, `ocfs2_mount_volume`, `ocfs2_dismount_volume`, `ocfs2_check_volume`, `ocfs2_verify_volume`, `ocfs2_sb_probe`, `ocfs2_reconfigure`, `ocfs2_statfs`, `ocfs2_sync_fs`, `ocfs2_init_global_system_inodes`, `ocfs2_init_local_system_inodes`, `ocfs2_release_system_inodes`, `__ocfs2_error`, `__ocfs2_abort`, and signal mask helpers.

Control flow: module init creates the uptodate and inode/quota caches, debugfs root, locking protocol, quota format, and filesystem type. Mount probes possible block sizes, rejects OCFS1, validates the OCFS2 superblock, initializes `struct ocfs2_super`, parses mount options against features, handles hard-readonly devices, verifies heartbeat and userspace stack arguments, mounts the volume through DLM/super lock/slot/system inode/journal/local alloc/recovery setup, creates the root dentry, completes recovery and quota recovery, and starts orphan scanning. Dismount reverses this: removes filecheck/sysfs, stops orphan/quota/recovery/local alloc/truncate log, returns slot, releases system inodes, shuts down journal and DLM, optionally runs heartbeat hangup, and frees `osb`.

State and persistence behavior: persistent inputs are the superblock dinode, feature flags, system inode locations, bitmap geometry, journal state, quota system files, and slot maps. Runtime state is concentrated in `struct ocfs2_super`: mount options, UUID/label, cluster stack/name, size geometry, slot/node state, recovery maps, local alloc state, workqueues, debug objects, journal object, system inode references, and allocation stats. Journal load/wipe/recovery can change persistent journal and local alloc state during mount.

Dependencies and integration points: integrates with Linux fs_context, block devices, VFS super/inode/dentry operations, debugfs, sysfs via `ocfs2_kset`, quota APIs, JBD2, cluster stack/DLM, heartbeat, slot map, orphan scan, local alloc, truncate log, refcount trees, filecheck sysfs, xattrs/ACLs, export ops, and blockcheck metadata ECC.

Risks: mount and unmount ordering is critical because many subsystems depend on DLM, slot ownership, journal state, and system inode references. Remount forbids changing heartbeat/data mode and inode64 enablement for safety. Hard-readonly mounts must skip recovery unless journals are clean. Feature flag validation controls read-write eligibility. Error handling can remount read-only, return EIO, or panic based on mount options; `__ocfs2_abort` forces panic behavior for clustered mounts.

Test signals: mounts across block sizes, invalid OCFS1/OCFS2 signatures, unsupported incompat/ro-compat features, hard-readonly devices with dirty and clean journals, heartbeat local/global/none combinations, userspace stack label mismatch, remount RO/RW and forbidden option changes, quota-enabled mounts, statfs from global bitmap, sync with truncate-log flush, mount failure unwind at each phase, clean unmount with heartbeat hangup, and error-policy behavior for `errors=panic|continue|remount-ro`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/super.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/super.h

Purpose: provides the small public superblock/error interface shared by OCFS2 source files. It centralizes formatted filesystem error and abort reporting and exposes signal-mask helpers used around kernel threads or blocking sections.

Important APIs and types: declares `__ocfs2_error`, `ocfs2_error`, `__ocfs2_abort`, `ocfs2_abort`, `ocfs2_block_signals`, and `ocfs2_unblock_signals`. The macros pass `__PRETTY_FUNCTION__` into the underlying implementation so diagnostics identify the failing call site.

Control flow: callers invoke `ocfs2_error` for detected on-disk corruption that should follow the mount error policy, or `ocfs2_abort` for more critical journal-style failures. Signal helpers wrap `sigprocmask` to block all signals and later restore the saved mask.

State and persistence behavior: the header itself carries no state. Its functions in `super.c` set runtime error flags, may mark the VFS superblock read-only, may panic, and do not themselves repair metadata.

Dependencies and integration points: used by allocator, inode, journal, and metadata validation code to report corruption consistently. The error behavior depends on mount options stored in `struct ocfs2_super`.

Risks: choosing `ocfs2_error` versus `ocfs2_abort` affects whether the filesystem continues, remounts read-only, or panics. Signal helper misuse could leave kernel context with an incorrect signal mask, though the implementations BUG on impossible `sigprocmask` failures.

Test signals: corruption injection paths that call `ocfs2_error`, journal abort paths that call `ocfs2_abort`, mount options for all error policies, and lockdep/runtime checks around signal blocking and restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/symlink.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/symlink.c

Purpose: implements OCFS2 symlink inode operations, including the fast-symlink address-space operation that reads inline symlink targets stored inside the dinode.

Important APIs and functions: exports `ocfs2_fast_symlink_aops` with `.read_folio = ocfs2_fast_symlink_read_folio`, and `ocfs2_symlink_inode_operations` with `page_get_link`, `ocfs2_getattr`, `ocfs2_setattr`, `ocfs2_listxattr`, and `ocfs2_fiemap`. The core helper is `ocfs2_fast_symlink_read_folio`.

Control flow: for fast symlinks, VFS page-cache link resolution calls `ocfs2_fast_symlink_read_folio`; it reads the inode block, interprets the buffer as an OCFS2 dinode, copies the inline target from `id2.i_symlink` into the folio, ends folio read success or failure, and releases the buffer head. Non-fast symlink link resolution uses `page_get_link` with normal address-space backing.

State and persistence behavior: fast symlink data is persistent inline dinode payload. The read path does not modify metadata; it populates the page cache folio with a NUL-terminated copy bounded by `ocfs2_fast_symlink_chars`.

Dependencies and integration points: depends on `ocfs2_read_inode_block`, dinode layout, VFS folio/page symlink helpers, OCFS2 getattr/setattr/filemap/xattr handlers, and buffer_head I/O. `symlink.h` supplies the predicate for selecting fast symlink handling during inode setup.

Risks: correctness depends on only assigning fast symlink aops to symlink inodes with inline data and `i_blocks == 0`. The copy includes `len + 1`, so the source must be NUL-terminated within the inline symlink capacity. Read errors must end the folio read with failure to avoid stale page-cache data.

Test signals: create/read short fast symlinks, longer non-fast symlinks, corrupted or unreadable inode block during symlink read, xattr/listxattr/getattr on symlink inodes, and page-cache repeated lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/symlink.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/symlink.h

Purpose: declares OCFS2 symlink operation tables and provides the fast-symlink predicate used by inode setup.

Important APIs and types: exports `ocfs2_symlink_inode_operations`, `ocfs2_fast_symlink_aops`, and inline `ocfs2_inode_is_fast_symlink`.

Control flow: the inline predicate returns true for symlink inodes with `i_blocks == 0`, identifying targets stored inline in the dinode rather than in allocated data clusters. Callers use that decision to attach fast symlink address-space operations.

State and persistence behavior: no state is stored in the header. The predicate encodes the on-disk convention that zero-block symlink inodes are fast symlinks.

Dependencies and integration points: used by OCFS2 inode initialization and symlink handling, and tied to the implementation in `symlink.c`.

Risks: if inode block accounting is wrong, a symlink may be treated as fast when no inline target exists, or as slow when inline data should be used. That would surface as failed link resolution or stale target data.

Test signals: inode setup for symlink modes with zero and nonzero `i_blocks`, fast-symlink read path selection, and fsck/corruption cases where symlink metadata is inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/symlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.c

Purpose: resolves and caches OCFS2 system file inodes, including global system inodes and slot-local system inodes such as journals, local allocators, quotas, and inode/extent allocators.

Important APIs and functions: public `ocfs2_get_system_file_inode` returns a referenced inode for a system inode type and slot. Helpers include `_ocfs2_get_system_file_inode`, `is_global_system_inode`, and `get_local_system_inode`. Under `CONFIG_DEBUG_LOCK_ALLOC`, per-system-inode lock class keys are installed for lockdep.

Control flow: lookup first identifies the cache slot: global array for global system inodes or lazily allocated `local_system_inodes` matrix for local types by slot. Under `system_file_mutex`, it returns an extra `igrab` reference if cached; otherwise it constructs the system inode name, looks up the block number in `sys_root_inode`, calls `ocfs2_iget`, stores an array reference when possible, and returns the caller reference.

State and persistence behavior: persistent state is the system directory entry naming scheme and dinode blocks. Runtime state is the cached inode pointer arrays in `struct ocfs2_super`, protected by `system_file_mutex`; the arrays hold their own inode references until `ocfs2_release_system_inodes` drops them. The local-system-inode array is allocated lazily under `osb_lock`.

Dependencies and integration points: depends on system inode name formatting, directory lookup, `ocfs2_iget`, OCFS2 superblock fields, inode lock resources, and lockdep. It is used by mount initialization, allocators, quotas, journals, statfs, local alloc, and truncate/recovery paths.

Risks: missing or corrupt system directory entries prevent mount or allocator operation. Lazy local array allocation can fail; the code falls back to uncached lookup for that attempt. Slot/type validation relies on BUG_ON for impossible callers. Cached references must be released in the matching superblock teardown path.

Test signals: global system inode lookup, local system inode lookup across all slots, lazy array allocation race, allocation failure fallback, missing system inode directory entry, lockdep class assignment for quota/journal versus other system files, and repeated lookup reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.h

Purpose: declares the system-file lookup interface for OCFS2 subsystems.

Important APIs and types: exposes `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`.

Control flow: callers pass a system inode type and slot, receiving a referenced inode or NULL. Global system inode types ignore slot semantics; local types are resolved per slot.

State and persistence behavior: the function declared here uses runtime inode caches in `struct ocfs2_super` and persistent system directory entries on disk, but the header stores no state.

Dependencies and integration points: included by mount, allocator, quota, statfs, journal, and recovery code needing system inodes.

Risks: callers must `iput` successful returns and must pass valid slot values for local system inodes. Treating NULL as a recoverable condition where a system inode is mandatory can hide filesystem corruption.

Test signals: compile coverage for all system inode consumers, reference leak checks around repeated get/iput cycles, and error paths where mandatory system files are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.c

Purpose: implements OCFS2's cluster-aware metadata buffer uptodate cache. Standard `buffer_uptodate` is insufficient because another node can change metadata after a local buffer was read, so this file tracks trusted metadata block numbers per caching object without pinning buffer_heads.

Important APIs and functions: public functions include `ocfs2_metadata_cache_init`, `ocfs2_metadata_cache_exit`, `ocfs2_metadata_cache_purge`, `ocfs2_metadata_cache_owner`, `ocfs2_metadata_cache_io_lock`, `ocfs2_metadata_cache_io_unlock`, `ocfs2_buffer_uptodate`, `ocfs2_buffer_read_ahead`, `ocfs2_set_buffer_uptodate`, `ocfs2_set_new_buffer_uptodate`, `ocfs2_remove_from_cache`, `ocfs2_remove_xattr_clusters_from_cache`, `init_ocfs2_uptodate_cache`, and `exit_ocfs2_uptodate_cache`. Internally it uses inline arrays for small caches and an rb-tree of `struct ocfs2_meta_cache_item` after expansion.

Control flow: cache initialization installs owner/super/lock/io-lock callbacks and starts in inline-array mode. Lookup checks local buffer uptodate first, trusts journaled buffers, then searches the per-object cache. Insertion avoids duplicates, appends to the inline array when possible, expands to an rb-tree when full, and tolerates allocation failure as a performance loss. Purge swaps out the tree under the cache lock and frees nodes outside it. Removal deletes a block from either array or tree and frees rb-tree nodes.

State and persistence behavior: the cache is runtime-only and stores block numbers plus transaction tracking fields in `struct ocfs2_caching_info`. It never pins buffer_heads and is only a strong hint paired with buffer flags and journal state. A slab cache named `ocfs2_uptodate` owns rb-tree items. New buffers are marked buffer-uptodate and inserted under the caching object's I/O lock.

Dependencies and integration points: depends on caching operations supplied by inode/system objects, buffer_head state, JBD2 `buffer_jbd`, OCFS2 cluster lock invalidation, xattr cluster removal, tracepoints, and superblock geometry for xattr cluster-to-block removal. It is used by metadata read, journal access, inode eviction, allocation group creation/removal, and xattr deletion.

Risks: cache validity relies on callers purging/removing entries when cluster locks are dropped or metadata is deleted. Inline-to-tree expansion allocates several objects and must handle concurrent purge/removal between allocation and insertion. Missing cache insertion is nonfatal but can increase disk I/O; stale cache retention is dangerous. Count mismatches during purge are logged because they indicate internal accounting bugs.

Test signals: metadata read after remote invalidation, journaled buffer trust, inline cache fill and rb-tree expansion, purge during concurrent insertion, remove from array and tree, xattr cluster removal across multiple blocks, allocation failure in slow insertion path, and slab init/exit leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.h

Purpose: declares the cluster-aware metadata uptodate cache interface and the callback table that lets generic cache code lock and identify different OCFS2 caching objects.

Important APIs and types: defines `struct ocfs2_caching_operations` with owner, superblock, cache lock/unlock, and I/O lock/unlock callbacks. Declares cache lifecycle, lookup, insertion, removal, readahead, and slab init/exit functions implemented in `uptodate.c`.

Control flow: users initialize an embedded `struct ocfs2_caching_info` with callbacks, wrap disk I/O with `ocfs2_metadata_cache_io_lock/unlock`, test buffers with `ocfs2_buffer_uptodate`, mark successful reads or new metadata with set helpers, and purge or remove cached block numbers when metadata validity changes.

State and persistence behavior: the header defines no storage itself, but its callbacks operate on runtime cache state in OCFS2 inode or metadata objects. No on-disk format changes are made by this layer.

Dependencies and integration points: consumed by inode initialization, buffer-head I/O, allocators, xattrs, journal access, and cluster lock invalidation paths. The callback abstraction avoids hardcoding inode locks into the cache implementation.

Risks: callback implementations must obey locking expectations: cache locks should not sleep, I/O locks may sleep, and owner/super callbacks must remain valid for the cache lifetime. Incorrect locking around set/remove can produce stale metadata reads on clustered mounts.

Test signals: cache users with lockdep enabled, purge under cluster lock invalidation, readahead detection while a buffer is locked, metadata creation with `ocfs2_set_new_buffer_uptodate`, and build-time coverage of all declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/uptodate.h -->
