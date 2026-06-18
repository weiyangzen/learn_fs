# Group Research: group_817_linux_sources_os_linux_linux_fs_ocfs2_stack_user_c_sources_os_linux__f7022ff874a1

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This grouped report covers the OCFS2 cluster stack glue, userspace stack adapter, suballocator, mount/superblock path, system inode lookup, fast symlink handling, and clustered metadata uptodate cache files listed in the work item. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stack_user.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/stack_user.c

## Purpose

`stack_user.c` implements the OCFS2 cluster stack plugin named `user`, which connects OCFS2 to Linux `fs/dlm` and, for older userspace-controlled stacks, to `/dev/ocfs2_control`. It bridges OCFS2's generic cluster stack operations from `stackglue.h` to `dlm_lockspace_t`, `dlm_lock()`, `dlm_unlock()`, and DLM POSIX lock helpers.

## Major Components

- `/dev/ocfs2_control` miscdevice protocol:
  - Performs a text handshake using protocol tag `T01\n`.
  - Requires a `SETN <8-hex-node>\n` node-number message.
  - Requires a `SETV <2-hex-major> <2-hex-minor>\n` locking protocol version message.
  - Accepts `DOWN <32-hex-uuid> <8-hex-node>\n` recovery notifications once the handshake is valid.
- `struct ocfs2_live_connection`:
  - Tracks a mounted filesystem's cluster connection, connection type, local node id, slot, DLM version lock state, LVB, completion, and waitqueue.
  - Is shared between mount-side cluster connection state and miscdevice-side recovery notifications.
- `struct ocfs2_control_private`:
  - Per-open miscdevice state for handshake progress, proposed node id, and proposed protocol version.
- `ocfs2_user_plugin`:
  - Registers stack operations for connect, disconnect, local node lookup, DLM lock/unlock/status/LVB helpers, POSIX plocks, and debug dumping.

## Control Protocol Behavior

The control device is stateful per file descriptor:

- Initial state rejects writes until userspace reads the whole protocol list.
- `ocfs2_control_read()` returns the supported protocol tag and advances to `OCFS2_CONTROL_HANDSHAKE_READ` after EOF of that tag.
- The next write must match `OCFS2_CONTROL_PROTO`.
- Configuration messages are accepted in `OCFS2_CONTROL_HANDSHAKE_PROTOCOL`.
- Valid runtime `DOWN` messages require `OCFS2_CONTROL_HANDSHAKE_VALID`.

Global control state is protected by `ocfs2_control_lock`:

- `ocfs2_control_this_node` is global for the active control daemon.
- `running_proto` is the selected filesystem locking protocol.
- `ocfs2_control_opened` counts valid control daemon opens.
- `ocfs2_live_connection_list` allows `DOWN` messages to find a mounted filesystem by UUID/name and call its recovery handler.

If the last valid control fd is released while live controlled connections remain, the code logs a severe error and calls `emergency_restart()`. This is intentional fail-fast behavior because cluster recovery notifications are no longer reliable.

## DLM Integration

The file wraps `fs/dlm` APIs in OCFS2 stack operations:

- `user_dlm_lock()` ensures an LVB pointer exists inside the `ocfs2_dlm_lksb` storage and calls `dlm_lock()` with `DLM_LKF_NODLCKWT`.
- `user_dlm_unlock()` calls `dlm_unlock()` with the `fs/dlm` lock id.
- `fsdlm_lock_ast_wrapper()` maps `-DLM_EUNLOCK` and `-DLM_ECANCEL` statuses to OCFS2 unlock ASTs; other statuses call the OCFS2 lock AST.
- `fsdlm_blocking_ast_wrapper()` forwards blocking ASTs to the OCFS2 locking protocol.
- `user_plock()` demultiplexes POSIX lock operations to `dlm_posix_cancel()`, `dlm_posix_get()`, `dlm_posix_unlock()`, or `dlm_posix_lock()`.

## Locking Protocol Negotiation

For modern `NO_CONTROLD` mode, protocol negotiation uses the LVB of a special DLM lock named `version_lock`:

- First mount takes `version_lock` in EX mode with `NOQUEUE`, writes the local max protocol to the LVB, then converts to PR mode.
- Later mounts take PR mode and read the LVB.
- A major-version mismatch or peer minor version greater than local max fails the mount.
- `fs_protocol_compare()` enforces that major versions match and clamps the connection minor version down to the already-running minor if needed.

For `WITH_CONTROLD` mode, userspace must provide node id and locking version through `/dev/ocfs2_control`; `ocfs2_control_install_private()` only publishes global state after both are available and compatible with active mounts.

## Mount/Recovery Flow

`user_cluster_connect()`:

- Allocates `ocfs2_live_connection`, initializes wait/completion state, and creates a DLM lockspace with `dlm_new_lockspace()`.
- Detects older dlm_controld behavior via `ops_rv == -EOPNOTSUPP` and switches to `WITH_CONTROLD`.
- Attaches the live connection to the control list.
- In `NO_CONTROLD` mode, negotiates protocol through `version_lock` and waits until `recover_done` supplies a positive node id.
- Verifies the connection protocol against `running_proto`.

DLM lockspace callbacks:

- `user_recover_slot()` logs node-down events and invokes OCFS2 recovery.
- `user_recover_done()` records the local node id and slot, then wakes the mount path.
- `user_recover_prep()` is intentionally empty.

`user_cluster_disconnect()` releases the version lock, releases the lockspace, drops the live connection, and clears connection private state.

## Dependencies

- Uses `stackglue.h` types and registration functions.
- Uses Linux `fs/dlm` and `dlm_plock` APIs.
- Calls OCFS2 recovery through `cc_recovery_handler`.
- Exposes a loadable module with `module_init()`/`module_exit()` that registers/unregisters the `user` stack plugin.

## Correctness Notes

- The control protocol deliberately requires exact write sizes so one write maps to one command.
- `ocfs2_control_lock` serializes global handshake state, live connection list changes, and control release behavior.
- The code assumes `ocfs2_live_connection_attach()` is called from the VFS mount path, where duplicate `fill_super()` calls for the same mount are prevented.
- The LVB protocol version fields are two `u8` values, so no endian conversion is required.
- In `user_cluster_connect()`, the error path has to avoid double-freeing `lc` after `user_cluster_disconnect()` has already dropped it; the code sets `lc = NULL` before the final cleanup path.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stack_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stackglue.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/stackglue.c

## Purpose

`stackglue.c` is the OCFS2 cluster stack abstraction layer. It lets the filesystem mount path request either the classic `o2cb` stack or the generic userspace stack, pins the chosen stack module while active, forwards lock operations to the selected plugin, and exposes OCFS2 cluster-stack status/configuration through sysfs and sysctl.

## Major State

- `locking_max_version`: global maximum OCFS2 locking protocol version set by `ocfs2_stack_glue_set_max_proto_version()`.
- `ocfs2_stack_list`: registered stack plugins.
- `cluster_stack_name`: selected stack label, defaulting to `o2cb`.
- `active_stack`: currently selected plugin while one or more cluster connections are active.
- `ocfs2_hb_ctl_path`: helper path for `ocfs2_hb_ctl`, exposed through `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.
- `ocfs2_stack_lock`: spinlock protecting plugin list, active stack, stack count, and stack-name configuration.

## Stack Selection

`ocfs2_stack_driver_get()` normalizes stack selection:

- Empty or missing stack name means classic `o2cb`.
- Stack names must be exactly `OCFS2_STACK_LABEL_LEN`.
- Anything other than `o2cb` selects plugin `user`.
- If the plugin is absent, it requests `ocfs2_stack_<plugin_name>` and retries.
- It refuses to switch stacks while another active stack is pinned.

`ocfs2_stack_driver_request()` performs the protected lookup:

- Rejects a requested stack label that differs from `cluster_stack_name`.
- If `active_stack` already exists, only the same plugin can be reused.
- Otherwise, looks up the plugin, pins its module owner, sets `active_stack`, and increments `sp_count`.

`ocfs2_stack_driver_put()` decrements the active plugin reference count and drops the module reference when the count reaches zero.

## Plugin Registration

- `ocfs2_stack_glue_register()` adds a unique plugin by name, initializes its `sp_count`, copies the current max protocol, and logs registration.
- `ocfs2_stack_glue_unregister()` verifies the plugin is registered, not active, and not referenced before removing it.
- `ocfs2_stack_glue_set_max_proto_version()` sets the global max protocol once and propagates it to all already-registered plugins.

## Exported Cluster API

The filesystem-facing functions are thin wrappers around the active stack:

- `ocfs2_cluster_connect()` allocates `struct ocfs2_cluster_connection`, fills group/cluster names, protocol callbacks, recovery callback, and starting version, pins/selects the stack, then calls plugin `connect`.
- `ocfs2_cluster_connect_agnostic()` uses the configured global `cluster_stack_name` if set.
- `ocfs2_cluster_disconnect()` calls plugin `disconnect`, frees the connection, and optionally drops the stack reference depending on `hangup_pending`.
- `ocfs2_cluster_hangup()` runs `ocfs2_hb_ctl -K -u <group>` and drops the deferred stack reference.
- `ocfs2_cluster_this_node()` forwards local-node lookup to the active plugin.

DLM wrappers:

- `ocfs2_dlm_lock()` stores the connection pointer in the LKSb on first use and forwards lock requests.
- `ocfs2_dlm_unlock()`, `ocfs2_dlm_lock_status()`, `ocfs2_dlm_lvb_valid()`, `ocfs2_dlm_lvb()`, and `ocfs2_dlm_dump_lksb()` forward through `active_stack->sp_ops`.
- `ocfs2_stack_supports_plocks()` and `ocfs2_plock()` expose optional cluster-aware POSIX locks.

## Sysfs and Sysctl Surface

Creates `/sys/fs/ocfs2` via `ocfs2_kset` with attributes:

- `max_locking_protocol`: current max OCFS2 locking protocol.
- `loaded_cluster_plugins`: registered plugin names.
- `active_cluster_plugin`: active plugin name, if any.
- `cluster_stack`: selected cluster stack label; writable only when no active stack conflicts.
- `dlm_recover_callback_support`: constant `1`.

Registers sysctl path `/proc/sys/fs/ocfs2/nm/hb_ctl_path` to configure the helper path used during unmount hangup.

## Correctness Notes

- `active_stack` means both module pinning and locking protocol stability.
- Stack labels are fixed length to match on-disk OCFS2 cluster stack labels.
- `ocfs2_cluster_hangup()` is separate from `ocfs2_cluster_disconnect()` because ocfs2-tools expects heartbeat cleanup on unmount even in cases where DLM setup did not fully occur.
- The global `active_stack` model means mixed stack plugins cannot be used concurrently in one kernel instance.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stackglue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stackglue.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/stackglue.h

## Purpose

`stackglue.h` defines the public OCFS2 cluster stack abstraction used by filesystem code and implemented by stack plugins such as `o2cb` and `user`. It hides stack-specific DLM lock status structures behind `struct ocfs2_dlm_lksb`, defines the connection and callback contracts, and declares exported stack glue functions.

## Key Types

- `struct ocfs2_protocol_version`:
  - Two-byte major/minor locking protocol version for inter-node OCFS2 behavior.
- `struct fsdlm_lksb_plus_lvb`:
  - Combines an `fs/dlm` `struct dlm_lksb` with inline LVB storage so the union has enough room.
- `struct ocfs2_dlm_lksb`:
  - Union of the classic o2dlm lock status, fs/dlm lock status, and padding/LVB storage.
  - Includes `lksb_conn` so callbacks can verify and recover the owning cluster connection.
- `struct ocfs2_locking_protocol`:
  - Filesystem callback table supplied to stack plugins.
  - Contains max version and lock AST, blocking AST, and unlock AST callbacks.
- `struct ocfs2_cluster_connection`:
  - Opaque-to-filesystem connection record carrying group name, cluster name, negotiated version, recovery callback, lockspace pointer, and plugin private state.
- `struct ocfs2_stack_operations`:
  - Plugin operation table for connect/disconnect, local node lookup, DLM lock/unlock/status/LVB access, optional plocks, and optional lock-status dumping.
- `struct ocfs2_stack_plugin`:
  - Registration record containing plugin name, operation table, module owner, list node, reference count, and max protocol.

## Constants

- `DLM_LKF_LOCAL` is locally defined because the public DLM constants header lacks it.
- `GROUP_NAME_MAX` shadows the internal DLM lockspace-name length.
- `CLUSTER_NAME_MAX` shadows the OCFS2 cluster name length.

## API Surface

Filesystem-facing API:

- `ocfs2_cluster_connect()`
- `ocfs2_cluster_connect_agnostic()`
- `ocfs2_cluster_disconnect()`
- `ocfs2_cluster_hangup()`
- `ocfs2_cluster_this_node()`
- `ocfs2_dlm_lock()` / `ocfs2_dlm_unlock()`
- `ocfs2_dlm_lock_status()`
- `ocfs2_dlm_lvb_valid()`
- `ocfs2_dlm_lvb()`
- `ocfs2_dlm_dump_lksb()`
- `ocfs2_stack_supports_plocks()`
- `ocfs2_plock()`
- `ocfs2_stack_glue_set_max_proto_version()`

Plugin-facing API:

- `ocfs2_stack_glue_register()`
- `ocfs2_stack_glue_unregister()`

## Correctness Notes

- The stack `connect()` contract is strong: it must not return until node-down notifications and lock processing are guaranteed.
- The stack `disconnect()` contract requires no further references to the connection after return.
- AST arguments are intentionally not passed through the generic lock API; stack implementations wrap stack-specific callbacks and pass the `ocfs2_dlm_lksb` back to OCFS2.
- `plock` is optional and must be checked through `ocfs2_stack_supports_plocks()`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/stackglue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/suballoc.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/suballoc.c

## Purpose

`suballoc.c` implements OCFS2 suballocator mechanics: metadata block allocation, inode allocation, cluster allocation through local/global bitmaps, block group creation and growth, suballocator frees, empty group reclaim, and helper checks for allocated inode bits. It is the core allocator for OCFS2 metadata and data-space bitmap management.

## Core Concepts

- Chain allocator dinodes contain `struct ocfs2_chain_list` records.
- Each chain points to group descriptors (`struct ocfs2_group_desc`) containing allocation bitmaps.
- Metadata and inode allocators are per-slot system inodes and can steal from other node slots under pressure.
- The global cluster bitmap allocates file data clusters and can be assisted by local allocation.
- Block groups can be contiguous or discontiguous when the filesystem supports discontiguous block groups.

`struct ocfs2_suballoc_result` carries allocation search results:

- Group descriptor block (`sr_bg_blkno`) and stable descriptor block (`sr_bg_stable_blkno`).
- First allocated block (`sr_blkno`) for metadata/inode allocations.
- Bitmap offset, number of bits claimed, and max contiguous-free hint.

## Alloc Context Lifetime

`ocfs2_alloc_context` resources are owned through:

- `ocfs2_free_ac_resource()`: unlocks allocator inode, drops bh, clears reservation/find-location private data.
- `ocfs2_free_alloc_context()`: frees resources then the context.

Allocator reservation functions populate:

- `ac_inode`: locked system allocator inode.
- `ac_bh`: locked allocator dinode buffer.
- `ac_bits_wanted` / `ac_bits_given`.
- `ac_which`: local, main, inode, meta, or main-discontiguous allocator mode.
- `ac_group_search`: group search strategy.

## Group Descriptor Validation

Validation is split into:

- `ocfs2_validate_gd_self()`:
  - Signature, `bg_blkno`, generation, free count, bitmap size, and discontiguous extent list bounds.
- `ocfs2_validate_gd_parent()`:
  - Parent dinode pointer, group bit count relative to parent chain geometry, and chain index bounds.
- `ocfs2_validate_group_descriptor()`:
  - ECC validation plus self-validation; parent validation is done by readers that know the parent.
- `ocfs2_check_group_descriptor()`:
  - Resize-oriented version that logs errors rather than taking the filesystem down.

`ocfs2_read_hint_group_descriptor()` handles a stale hint: if the hinted group no longer has a valid group descriptor signature, it removes the buffer from the metadata cache, reports `released=1`, and lets the caller continue with a full chain search.

## Block Group Creation and Growth

`ocfs2_block_group_fill()` initializes a new group descriptor:

- Sets signature, generation, bitmap size, chain id, parent dinode, self block number, and first descriptor bit.
- For full contiguous groups, sets `bg_bits` directly.
- For shorter/discontiguous groups, adds extent records through `ocfs2_bg_discontig_add_extent()`.

Group allocation paths:

- `ocfs2_block_group_alloc_contig()` claims one contiguous cluster run, gets the descriptor block, marks it uptodate, and fills it.
- `ocfs2_block_group_alloc_discontig()` claims an initial region, fills the group, then grows it with additional extent records through `ocfs2_block_group_grow_discontig()`.
- `ocfs2_bg_alloc_cleanup()` frees clusters and removes the descriptor from cache if discontiguous group creation fails.
- `ocfs2_block_group_alloc()` reserves clusters, starts a transaction, creates the group, links it into the allocator chain, updates dinode usage/size/cluster counts, and records `last_alloc_group`.

## Reservation Paths

`ocfs2_reserve_suballoc_bits()` locks a system allocator inode and ensures enough free bits exist. For non-cluster bitmaps it may grow the allocator by allocating a new block group.

Public reservation APIs:

- `ocfs2_reserve_new_metadata_blocks()`: reserves extent allocator bits, first using local slot, then stealing from other slots if needed.
- `ocfs2_reserve_new_metadata()`: computes metadata need from an extent list root.
- `ocfs2_reserve_new_inode()`: reserves one inode bit, respects `inode64` by limiting max block when disabled, and supports inode stealing.
- `ocfs2_reserve_cluster_bitmap_bits()`: reserves bits from the global cluster bitmap.
- `ocfs2_reserve_clusters()`: chooses local allocation when appropriate, otherwise global bitmap; may free truncate-log space and retry.

Steal-slot state:

- `ocfs2_init_steal_slots()` initializes inode/meta steal slots and counters.
- A successful steal records the donor slot and continues stealing up to `OCFS2_MAX_TO_STEAL` before trying the local slot again.

## Allocation Search

Bitmap search and updates:

- `ocfs2_test_bg_bit_allocatable()` avoids reusing bits that are free in memory but still allocated in JBD2 committed data.
- `ocfs2_find_max_contig_free_bits()` scans a bitmap for the largest free run.
- `ocfs2_block_group_find_clear_bits()` finds the best available run in a group.
- `ocfs2_block_group_set_bits()` journals and sets bits, updates free count and contiguous-free hints.

Group search variants:

- `ocfs2_cluster_group_search()` searches cluster bitmaps with `min_bits`, `max_block`, tail-group safety for failed resize, and contig-free hints.
- `ocfs2_block_group_search()` searches metadata/inode block groups, where `min_bits` must be 1.

Chain search:

- `ocfs2_find_victim_chain()` chooses the chain with the most free bits.
- `ocfs2_search_one_group()` tries a specific hinted group.
- `ocfs2_search_chain()` walks a chain and may relink a reasonably empty group to the head to speed future searches.
- `ocfs2_claim_suballoc_bits()` tries last-group hint, then victim chain, then other chains, and falls back to discontiguous main bitmap mode when contiguous cluster allocation fails.

## Public Claim APIs

- `ocfs2_claim_metadata()` claims metadata blocks and returns suballocator location, bit start, block start, and number of bits.
- `ocfs2_find_new_inode_loc()` searches for an inode location without setting allocation bits, used for reflink/orphan ordering.
- `ocfs2_claim_new_inode_at_loc()` later claims the pre-found inode bit and verifies the block number is unchanged.
- `ocfs2_claim_new_inode()` combines search and allocation for ordinary inode allocation.
- `__ocfs2_claim_clusters()` claims data clusters from local allocation or global bitmap, with min/max cluster controls.
- `ocfs2_claim_clusters()` claims remaining reserved cluster bits.

## Free and Reclaim Paths

- `ocfs2_block_group_clear_bits()` journals and clears allocation bits, updates free counts, updates undo buffers for cluster bitmap frees, and refreshes contiguous-free hints.
- `_ocfs2_free_suballoc_bits()` clears bits in a metadata/inode/global bitmap allocator, updates parent chain record and dinode used count, and may reclaim a fully empty non-first suballocator group back to the global bitmap.
- `_ocfs2_reclaim_suballoc_to_main()` removes an empty suballocator group from its chain accounting and frees its clusters into the main global bitmap.
- `ocfs2_free_suballoc_bits()` wraps metadata/inode free without undo handling.
- `ocfs2_free_dinode()` computes an inode's allocator group from `i_suballoc_loc` or block/bit and frees one bit.
- `ocfs2_free_clusters()` frees previously used data clusters with undo protection.
- `ocfs2_release_clusters()` releases never-used clusters without protecting old allocations in the undo buffer.

## Allocator Lock Coordination

`ocfs2_lock_allocators()` decides whether metadata and/or data allocators must be reserved for extent operations:

- It checks free extent records in the destination extent tree.
- Sparse filesystems reserve metadata more conservatively because allocation happens while a journal handle is open.
- It reserves data clusters only when `clusters_to_add` is nonzero.
- On error, it frees any metadata allocation context it created.

## Inode Bit Testing

`ocfs2_test_inode_bit()`:

- Reads the target inode block directly to discover `i_suballoc_slot`, `i_suballoc_loc`, and `i_suballoc_bit`.
- Locks the corresponding inode allocator system inode.
- Reads the group descriptor, tolerating stale released groups as `-ESTALE`.
- Tests the relevant bitmap bit.

This is used by paths that need to verify whether an inode block is still allocated, with comments noting that callers must coordinate with `nfs_sync_lock` to avoid concurrent delete races.

## Correctness Notes

- Group descriptor validation distinguishes fatal normal reads from resize checks that should not force readonly.
- Cluster bitmap allocations use JBD2 undo access to avoid crash windows where recently freed data could be reallocated before transaction commit.
- Many `BUG_ON()` assertions reflect assumptions guaranteed by caller-held locks and prior validation.
- Discontiguous group handling carefully fixes allocation results because bitmap offsets may map into non-contiguous extent records.
- Empty suballocator reclaim intentionally skips the first chain record and non-empty records.
- One suspicious expression in `_ocfs2_reclaim_suballoc_to_main()` subtracts the new on-disk `fe->i_clusters` from `OCFS2_I(alloc_inode)->ip_clusters` after already reducing `fe->i_clusters`; this is worth checking against upstream history if allocator reclaim bugs are being investigated.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/suballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/suballoc.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/suballoc.h

## Purpose

`suballoc.h` declares the OCFS2 suballocator API and defines `struct ocfs2_alloc_context`, the shared reservation/claim state used by inode, metadata, and cluster allocation paths.

## Key Types and Fields

`group_search_t` is the callback type used by allocation contexts to search a group descriptor for suitable bits.

`struct ocfs2_alloc_context` contains:

- `ac_inode`: allocator bitmap inode.
- `ac_bh`: allocator dinode buffer.
- `ac_alloc_slot`: slot associated with allocator.
- `ac_bits_wanted` / `ac_bits_given`: reservation accounting.
- `ac_which`: allocator source:
  - `OCFS2_AC_USE_LOCAL`
  - `OCFS2_AC_USE_MAIN`
  - `OCFS2_AC_USE_INODE`
  - `OCFS2_AC_USE_META`
  - `OCFS2_AC_USE_MAIN_DISCONTIG`
- Chain-search state: `ac_chain`, `ac_disable_chain_relink`, `ac_group_search`, `ac_last_group`, and `ac_max_block`.
- Find-location-only state for ordering-sensitive inode creation: `ac_find_loc_only`, `ac_find_loc_priv`.
- `ac_resv`: reservation record for local allocation reservations.

## API Surface

Reservation:

- `ocfs2_init_steal_slots()`
- `ocfs2_reserve_new_metadata()`
- `ocfs2_reserve_new_metadata_blocks()`
- `ocfs2_reserve_new_inode()`
- `ocfs2_reserve_clusters()`
- `ocfs2_reserve_cluster_bitmap_bits()`

Claim:

- `ocfs2_claim_metadata()`
- `ocfs2_claim_new_inode()`
- `ocfs2_find_new_inode_loc()`
- `ocfs2_claim_new_inode_at_loc()`
- `ocfs2_claim_clusters()`
- `__ocfs2_claim_clusters()`

Free/release:

- `ocfs2_free_alloc_context()`
- `ocfs2_free_ac_resource()`
- `ocfs2_free_suballoc_bits()`
- `ocfs2_free_dinode()`
- `ocfs2_free_clusters()`
- `ocfs2_release_clusters()`

Helpers:

- `ocfs2_alloc_context_bits_left()`
- `ocfs2_which_suballoc_group()`
- `ocfs2_cluster_from_desc()`
- `ocfs2_is_cluster_bitmap()`
- `ocfs2_which_cluster_group()`
- `ocfs2_find_max_contig_free_bits()`
- `ocfs2_block_group_set_bits()`
- `ocfs2_read_group_descriptor()`
- `ocfs2_check_group_descriptor()`
- `ocfs2_lock_allocators()`
- `ocfs2_test_inode_bit()`

## Correctness Notes

- The header explicitly requires callers to pass the root extent list to `ocfs2_reserve_new_metadata()`.
- `ocfs2_is_cluster_bitmap()` identifies the global bitmap by comparing the OSB bitmap block number with the inode's disk block number.
- `ocfs2_which_suballoc_group()` assumes a normal contiguous mapping where group block is `block - bit`; callers use `i_suballoc_loc` for discontiguous cases when available.
- The find-then-claim inode APIs are specifically documented as used by `ocfs2_create_inode_in_orphan()`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/suballoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/super.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/super.c

## Purpose

`super.c` implements OCFS2 module initialization, filesystem registration, fs_context parsing, superblock probing and initialization, mount and dismount flow, quota setup, system inode initialization, statfs, memory-cache management, debugfs reporting, and OCFS2 error/abort behavior.

## Module and Filesystem Registration

Module initialization in `ocfs2_init()`:

- Initializes the OCFS2 metadata uptodate cache.
- Creates inode/dquot/quota chunk slab caches.
- Creates top-level debugfs directory `ocfs2`.
- Sets the OCFS2 locking protocol.
- Registers the OCFS2 quota format.
- Registers the `ocfs2` filesystem type.

Exit reverses these operations and unregisters the filesystem.

`ocfs2_fs_type` uses:

- `.name = "ocfs2"`
- `.kill_sb = kill_block_super`
- `.fs_flags = FS_REQUIRES_DEV | FS_RENAME_DOES_D_MOVE`
- `.init_fs_context = ocfs2_init_fs_context`
- `.parameters = ocfs2_param_spec`

## Mount Options

`struct mount_options` stores parsed options:

- Commit interval, mount option bitmask, atime quantum, preferred slot.
- Localalloc size option.
- Reservation levels for file and directory allocation.
- Cluster stack label and whether it is a userspace stack.

`ocfs2_param_spec` supports options including:

- `barrier`
- `errors=panic|remount-ro|continue`
- `intr` / `nointr`
- `heartbeat=local|none|global`
- `data=writeback|ordered`
- `atime_quantum`
- `preferred_slot`
- `commit`
- `localalloc`
- `localflocks`
- `cluster_stack`
- `user_xattr`
- `inode64`
- `acl`
- `usrquota`
- `grpquota`
- `coherency=buffered|full`
- `resv_level`
- `dir_resv_level`
- `journal_async_commit`

`ocfs2_check_set_options()` validates heartbeat mode exclusivity for non-userspace stacks, quota feature availability, ACL feature availability, and default ACL behavior based on xattr feature support.

`ocfs2_reconfigure()` handles remount:

- Syncs the filesystem first.
- Rejects heartbeat mode, data mode, and enabling `inode64` changes on remount.
- Handles readonly transitions, including quota suspend/resume/enable.
- Refuses read-write remount when hard-readonly, error-marked, or unsupported readonly-compatible features are present.

`ocfs2_show_options()` emits mount options for `/proc/mounts`.

## Superblock Probe and Verification

`ocfs2_sb_probe()`:

- Determines logical sector size and clamps minimum to OCFS2 minimum.
- Checks block zero for old OCFS1 headers/signatures and rejects them.
- Probes possible OCFS2 block sizes from sector size through 4096 bytes at `OCFS2_SUPER_BLOCK_BLKNO`.
- Calls `ocfs2_verify_volume()` for each candidate.

`ocfs2_verify_volume()`:

- Checks superblock signature.
- Validates metadata ECC if the feature is present.
- Verifies blocksize bits, actual probed block size, OCFS2 major/minor revision, superblock block number, cluster size bits, root/system directory block numbers, and max slots.
- Returns `-EAGAIN` when the candidate block size is not the superblock.

## OSB Initialization

`ocfs2_initialize_super()` allocates and fills `struct ocfs2_super`:

- Installs super operations, dentry ops, export ops, quota ops, xattr handlers, time granularity, and default `SB_NOATIME`.
- Calculates `s_maxbytes` using `ocfs2_max_file_offset()`.
- Copies UUID into VFS superblock and builds OCFS2 UUID string.
- Initializes locks, waitqueues, work items, node maps, allocation stats, reservation maps, orphan scan/recovery state, refcount tree, quota work, and local allocation state.
- Reads feature flags and rejects unsupported incompat features, or unsupported ro-compat features for read-write mounts.
- Copies cluster stack/name information if valid.
- Allocates journal state and DLM debug state.
- Loads root, system directory, and global system inodes.
- Locates the global bitmap inode and records bitmap block, cluster count at boot, and bitmap bits per group.
- Initializes slot info and the ordered workqueue.

Cleanup labels unwind allocated OSB substructures in reverse order.

## Mount Flow

`ocfs2_fill_super()`:

- Probes and initializes the superblock.
- Applies parsed options, localalloc sizes, and reservation levels.
- Verifies userspace stack compatibility with on-disk cluster info.
- Handles readonly block devices:
  - Requires readonly mount.
  - Rejects local heartbeat.
  - Checks journals without cluster locks.
  - Sets hard-readonly and skips cluster services/recovery.
- Verifies heartbeat constraints.
- Creates debugfs entries and ECC stats debugfs when enabled.
- Calls `ocfs2_mount_volume()`.
- Builds the VFS root dentry from `osb->root_inode`.
- Creates per-device `/sys/fs/ocfs2/<devname>` kset and filecheck sysfs.
- Completes mount recovery, logs mount details, enables quotas on read-write mounts, completes quota recovery, and starts orphan scanning.

`ocfs2_mount_volume()` for non-hard-readonly mounts:

- Initializes DLM.
- Takes the super lock.
- Finds/claims this node's slot.
- Loads local system inodes.
- Checks/replays journal state and local alloc state through `ocfs2_check_volume()`.
- Initializes truncate log.
- Releases the super lock.

`ocfs2_check_volume()`:

- Initializes the journal and verifies the journal can address the full volume.
- Wipes clean journals or loads dirty journals for replay.
- Configures JBD2 async commit feature according to mount option.
- Begins local allocation recovery for dirty local journals.
- Loads local allocation.
- Marks dead nodes and computes replay slots.

## Dismount Flow

`ocfs2_put_super()` syncs the block device and calls `ocfs2_dismount_volume()`.

`ocfs2_dismount_volume()`:

- Removes filecheck sysfs and per-device kset.
- Stops orphan scan and quota recovery.
- Disables quotas and drains quota drop work.
- Shuts down local allocation and truncate log.
- Exits recovery and syncs the block device.
- Purges refcount trees.
- Takes the super lock if cluster connection exists, releases this node's slot, then unlocks.
- Releases system inodes and shuts down journal.
- Determines whether cluster heartbeat hangup is needed.
- Shuts down DLM and, if needed, calls `ocfs2_cluster_hangup()`.
- Removes debugfs/ECC stats, marks dismounted, logs unmount, deletes OSB, and clears `sb->s_fs_info`.

`ocfs2_delete_osb()` destroys the workqueue, frees slot info, orphan wipe arrays, journal, local alloc copy, UUID string, volume label, and DLM debug state, then clears the OSB memory.

## System Inodes and Slab Caches

- `ocfs2_init_global_system_inodes()` loads root, system directory, and global online system inodes.
- `ocfs2_init_local_system_inodes()` loads all local-slot system inodes needed for the mounted slot.
- `ocfs2_release_system_inodes()` drops global and local cached inode references and frees the local inode array.
- `ocfs2_alloc_inode()` allocates `ocfs2_inode_info`, initializes journal inode state and dquot pointers.
- `ocfs2_inode_init_once()` initializes inode locks, extent map, IO markers, allocation semaphores, metadata cache, lock resources, and VFS inode base.

## Quotas

Quota helpers:

- `ocfs2_enable_quotas()` loads local user/group quota system inodes and enables quota usage accounting.
- `ocfs2_disable_quotas()` disables loaded quotas, cancels sync work, and lets global quota files receive synced dquot state.
- `ocfs2_susp_quotas()` suspends or resumes quotas around readonly remount transitions.

Quota support depends on `OCFS2_FEATURE_RO_COMPAT_USRQUOTA` and `OCFS2_FEATURE_RO_COMPAT_GRPQUOTA`.

## Debugfs and Statfs

With `CONFIG_DEBUG_FS`, `ocfs2_osb_dump()` produces a one-page textual state dump containing device, volume, size, feature, mount, cluster, recovery, commit, journal, allocation, local alloc, steal slot, orphan scan, and slot generation data.

`ocfs2_statfs()` locks the global bitmap inode, reads total and used bits, and fills `kstatfs`, including a two-part fsid generated from CRC32 over the UUID string.

## Error Handling

- `ocfs2_handle_error()` marks the OSB error flag and applies the selected `errors=` behavior:
  - Panic.
  - Return `-EIO`.
  - Default remount-readonly behavior with `OCFS2_OSB_SOFT_RO`.
- `__ocfs2_error()` logs the function name and formatted corruption message, then calls `ocfs2_handle_error()`.
- `__ocfs2_abort()` logs a critical abort and forces panic behavior for clustered mounts.
- `ocfs2_block_signals()` / `ocfs2_unblock_signals()` wrap in-kernel signal mask changes.

## Correctness Notes

- Hard-readonly mounts skip cluster services and recovery and require journals to be clean enough for readonly access.
- Userspace stack mounts must pass a cluster stack matching the on-disk stack label.
- Quotas are enabled after mount recovery because cluster lock recovery may be needed before quota operations can safely wait.
- `ocfs2_show_options()` appears to print `osb->osb_resv_level` for `dir_resv_level` rather than `osb->osb_dir_resv_level`; this is worth checking if mount option display accuracy matters.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/super.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/super.h

## Purpose

`super.h` declares OCFS2 superblock-level error/abort helpers and signal mask helpers used outside `super.c`.

## API Surface

- `__ocfs2_error(struct super_block *sb, const char *function, const char *fmt, ...)`
  - `__printf(3, 4)` annotated.
  - Wrapped by `ocfs2_error(sb, fmt, ...)`, which passes `__PRETTY_FUNCTION__`.
- `__ocfs2_abort(struct super_block *sb, const char *function, const char *fmt, ...)`
  - `__printf(3, 4)` annotated.
  - Wrapped by `ocfs2_abort(sb, fmt, ...)`.
- `ocfs2_block_signals(sigset_t *oldset)`
- `ocfs2_unblock_signals(sigset_t *oldset)`

## Correctness Notes

- The macros preserve caller function names in corruption/abort logs without each caller passing its function manually.
- Signal helpers are documented as void because in-kernel `sigprocmask()` only fails for invalid signal constants, which these wrappers do not use.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/symlink.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/symlink.c

## Purpose

`symlink.c` implements OCFS2 symlink inode operations, including a fast-symlink read path for symlink targets stored inline in the inode dinode.

## Fast Symlink Read

`ocfs2_fast_symlink_read_folio()`:

- Gets the target inode from `folio->mapping->host`.
- Reads the inode block with `ocfs2_read_inode_block()`.
- Treats `fe->id2.i_symlink` as the inline symlink target.
- Uses `strnlen()` bounded by `ocfs2_fast_symlink_chars(inode->i_sb)`.
- Copies the string plus NUL terminator into the folio with `memcpy_to_folio()`.
- Ends folio read with success based on the inode-block read status and releases the buffer head.

The address-space operation table `ocfs2_fast_symlink_aops` installs this as `.read_folio`.

## Inode Operations

`ocfs2_symlink_inode_operations` provides:

- `.get_link = page_get_link`
- `.getattr = ocfs2_getattr`
- `.setattr = ocfs2_setattr`
- `.listxattr = ocfs2_listxattr`
- `.fiemap = ocfs2_fiemap`

## Dependencies

This file uses inode read helpers, file attribute handling, xattr listing, and fiemap from other OCFS2 subsystems. The fast-symlink predicate is declared in `symlink.h`.

## Correctness Notes

- Fast symlink length is bounded by filesystem-specific inline symlink capacity before copying.
- The read path copies the NUL terminator so `page_get_link` can return a normal string.
- Errors from reading the inode block propagate through `folio_end_read(folio, false)`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/symlink.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/symlink.h

## Purpose

`symlink.h` declares OCFS2 symlink operation tables and provides the inline predicate for detecting fast symlinks.

## API Surface

- `ocfs2_symlink_inode_operations`
- `ocfs2_fast_symlink_aops`
- `ocfs2_inode_is_fast_symlink(struct inode *inode)`

## Fast Symlink Predicate

`ocfs2_inode_is_fast_symlink()` returns true when:

- The inode mode is a symbolic link.
- `inode->i_blocks == 0`.

This matches the OCFS2 convention that fast symlink contents are stored inline in the inode rather than in allocated data blocks.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/sysfile.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/sysfile.c

## Purpose

`sysfile.c` implements lookup and caching for OCFS2 system file inodes. System files include global filesystem metadata files and per-slot local metadata files such as journals, local allocators, and quota files.

## Cache Layout

- Global system inodes are cached in `osb->global_system_inodes[type]`.
- Local system inodes are cached in a lazily allocated flat array:
  - `NUM_LOCAL_SYSTEM_INODES * osb->max_slots`.
  - Index is `(slot * NUM_LOCAL_SYSTEM_INODES) + (type - OCFS2_FIRST_LOCAL_SYSTEM_INODE)`.
- `osb->system_file_mutex` serializes lookup and cache insertion.
- `osb->osb_lock` protects lazy publication of `local_system_inodes`.

## Main Flow

`ocfs2_get_system_file_inode(osb, type, slot)`:

- Chooses the global cache entry or local cache entry based on inode type.
- If a cached inode exists, returns an extra reference from `igrab()`.
- Otherwise calls `_ocfs2_get_system_file_inode()`.
- If a cache slot exists, stores an additional array reference with `igrab()`.

`_ocfs2_get_system_file_inode()`:

- Builds the system inode name using `ocfs2_sprintf_system_inode_name()`.
- Looks up its block number in `osb->sys_root_inode` with `ocfs2_lookup_ino_from_name()`.
- Loads the inode with `ocfs2_iget(..., OCFS2_FI_FLAG_SYSFILE, type)`.
- Under `CONFIG_DEBUG_LOCK_ALLOC`, assigns lockdep classes to system inode cluster locks, while suppressing lockdep for local quota and journal locks that do not belong to a normal process.

## Correctness Notes

- Local system inode cache allocation is opportunistic; if allocation fails, lookup still proceeds without caching.
- The local array publication handles a race where another thread initializes the array first, freeing the loser allocation.
- Cached inode arrays hold their own references; callers always receive an additional reference and must `iput()`.
- The code asserts local inode requests never use `OCFS2_INVALID_SLOT`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/sysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/sysfile.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/sysfile.h

## Purpose

`sysfile.h` declares the system-file inode lookup API used across OCFS2 subsystems.

## API Surface

- `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`

The function returns an inode reference for a global or slot-local system inode. Callers are responsible for dropping the returned reference.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/sysfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/uptodate.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/uptodate.c

## Purpose

`uptodate.c` implements OCFS2's clustered metadata buffer uptodate cache. Standard `buffer_uptodate` state is only local to a node, so OCFS2 tracks which metadata blocks are known valid relative to cluster locking without pinning `buffer_head` objects.

## Cache Model

Each cache is embedded in an owner-specific `struct ocfs2_caching_info` and uses owner-provided operations for:

- Owner id logging.
- Superblock lookup.
- Non-sleeping cache lock/unlock.
- Sleeping I/O lock/unlock.

The cache stores block numbers, not buffer heads:

- Starts as an inline fixed array with `OCFS2_CACHE_INFO_MAX_ARRAY` entries.
- Expands to an RB-tree of `struct ocfs2_meta_cache_item` when the array fills.
- Does not shrink back to the inline representation.

`ocfs2_uptodate_cachep` is a slab cache for RB-tree items.

## Public Operations

- `ocfs2_metadata_cache_init()` sets operations and resets state.
- `ocfs2_metadata_cache_exit()` purges and resets the cache.
- `ocfs2_metadata_cache_purge()` clears all cached block numbers and frees tree nodes outside the cache lock.
- `ocfs2_metadata_cache_owner()` returns owner id through callbacks.
- `ocfs2_metadata_cache_get_super()` gets the backing superblock through callbacks.
- `ocfs2_metadata_cache_io_lock()` / `ocfs2_metadata_cache_io_unlock()` call owner-provided I/O serialization.
- `ocfs2_buffer_uptodate()` decides whether a buffer can be trusted.
- `ocfs2_buffer_read_ahead()` detects an in-flight readahead buffer that is already tracked in the cache.
- `ocfs2_set_buffer_uptodate()` inserts a buffer block into the cache.
- `ocfs2_set_new_buffer_uptodate()` marks a newly allocated buffer locally uptodate and inserts it under the I/O lock.
- `ocfs2_remove_from_cache()` removes one block.
- `ocfs2_remove_xattr_clusters_from_cache()` removes all blocks covered by xattr clusters.
- `init_ocfs2_uptodate_cache()` and `exit_ocfs2_uptodate_cache()` manage the slab cache.

## Trust Rules

`ocfs2_buffer_uptodate()` returns false if `buffer_uptodate(bh)` is false. If the buffer is journaled on the local node (`buffer_jbd(bh)`), it returns true because OCFS2 prevents multiple nodes from modifying the same metadata block simultaneously. Otherwise it requires the block number to be present in the OCFS2 metadata cache.

This gives a strong hint without pinning buffer heads and relies on the I/O path, DLM lock invalidation, and journal access rules to purge or trust entries correctly.

## Insert Path

`ocfs2_set_buffer_uptodate()`:

- Avoids duplicate work if `ocfs2_buffer_cached()` already finds the block.
- Uses a fast path when the cache is still inline and has capacity.
- Switches to the slow path when allocation or tree expansion is needed.

`__ocfs2_set_buffer_uptodate()`:

- Allocates the new tree item before taking the cache lock.
- If expansion is needed, allocates one tree item per existing inline-array entry.
- Rechecks whether removals made array insertion possible while allocation was in progress.
- Expands the array to an RB-tree with `ocfs2_expand_cache()` and inserts the new item.

The insertion path relies on the owner I/O lock to prevent concurrent duplicate inserts and concurrent tree expansions.

## Removal and Purge

- Inline removal uses `memmove()` to keep the array compact.
- Tree removal erases the RB node under lock and frees the item after unlocking.
- Purge saves the RB root, resets the cache under lock, then frees all copied tree nodes outside the lock.
- Purge tracks the expected count and logs if the number of freed nodes differs.

## Correctness Notes

- A true result from `ocfs2_buffer_cached()` alone does not prove the buffer is safe; callers use `ocfs2_buffer_uptodate()` so local buffer state and journal state are also considered.
- Readahead can insert buffers before I/O completion; `ocfs2_buffer_read_ahead()` handles the locked-buffer case.
- `ocfs2_set_new_buffer_uptodate()` asserts the block is not already cached, sets the normal buffer uptodate flag, and serializes insertion with the I/O lock.
- Allocation failure in the slow insert path is non-fatal and only reduces caching performance.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/uptodate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/uptodate.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/uptodate.h

## Purpose

`uptodate.h` declares the OCFS2 clustered metadata uptodate cache interface and the callback operations required from cache owners.

## Key Type

`struct ocfs2_caching_operations` supplies:

- `co_owner()`: returns a `u64` owner identifier, usually a block number.
- `co_get_super()`: returns the relevant superblock for block/cluster conversion.
- `co_cache_lock()` / `co_cache_unlock()`: non-sleeping cache lock hooks.
- `co_io_lock()` / `co_io_unlock()`: sleeping I/O serialization hooks.

These callbacks let the generic cache code work for different OCFS2 owners while relying on owner-specific locking.

## API Surface

- `init_ocfs2_uptodate_cache()`
- `exit_ocfs2_uptodate_cache()`
- `ocfs2_metadata_cache_init()`
- `ocfs2_metadata_cache_purge()`
- `ocfs2_metadata_cache_exit()`
- `ocfs2_metadata_cache_owner()`
- `ocfs2_metadata_cache_io_lock()`
- `ocfs2_metadata_cache_io_unlock()`
- `ocfs2_buffer_uptodate()`
- `ocfs2_set_buffer_uptodate()`
- `ocfs2_set_new_buffer_uptodate()`
- `ocfs2_remove_from_cache()`
- `ocfs2_remove_xattr_clusters_from_cache()`
- `ocfs2_buffer_read_ahead()`

## Correctness Notes

- The header makes explicit that locking is provided by the cache owner, not by the generic type itself.
- Cache-lock callbacks must not sleep; I/O-lock callbacks may sleep.
- This separation is central to safe cache checks under buffer locks while still serializing I/O submitters.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/uptodate.h -->