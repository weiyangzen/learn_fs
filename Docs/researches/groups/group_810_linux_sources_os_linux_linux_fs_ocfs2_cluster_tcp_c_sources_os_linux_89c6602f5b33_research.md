# Group Research: group_810_linux_sources_os_linux_linux_fs_ocfs2_cluster_tcp_c_sources_os_linux_89c6602f5b33

Scope: `Docs/research_subset_a.md` subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp.c

## Purpose
Implements the OCFS2 O2CB cluster TCP transport. It manages per-node TCP connections, wire-message framing, synchronous request/status exchange, unsolicited message dispatch, heartbeat-driven connect/disconnect policy, keepalive/idle timeout behavior, and integration with quorum handling.

## Main Responsibilities
- Maintains global per-node state in `o2net_nodes[O2NM_MAX_NODES]`.
- Owns the listening socket, ordered workqueue `o2net_wq`, heartbeat callbacks, and prebuilt handshake/keepalive messages.
- Provides exported send APIs:
  - `o2net_send_message()`
  - `o2net_send_message_vec()`
  - `o2net_fill_node_map()`
  - handler registration/unregistration APIs.
- Converts wire-level system statuses to Linux errno values through `o2net_sys_err_to_errno()`.

## Connection Lifecycle
Each remote node has an `o2net_node` tracking:
- active socket container `nn_sc`
- validity bit `nn_sc_valid`
- persistent transmit error `nn_persistent_error`
- status waiter IDR/list
- delayed connect, connect-expired, and quorum-still-up work.

The higher-numbered node initiates a connection when heartbeat reports a lower-numbered node up. The lower-numbered node accepts only if the peer is heartbeating. `o2net_set_nn_state()` centralizes state transitions, reference management, connected-peer accounting, wakeups for senders, status waiter completion on disconnect, reconnect scheduling, and quorum notifications.

## Socket Container Model
`struct o2net_sock_container` wraps a kernel socket with:
- `kref` lifetime control
- receive page and offset
- socket callbacks
- send mutex
- RX, connect-complete, shutdown, and keepalive work
- idle timer
- debug/stat timing fields when enabled.

`sc_alloc()`, `sc_get()`, `sc_put()`, and `sc_kref_release()` ensure sockets, pages, node references, and debug state are released only after queued work and callback references are gone.

## Wire Protocol and Framing
Incoming data is copied into the per-socket page. `o2net_advance_rx()` first reads and validates the handshake, then repeatedly reads:
1. fixed `struct o2net_msg` header
2. bounded payload up to `O2NET_MAX_PAYLOAD_BYTES`
3. dispatch/status/keepalive handling.

Framing errors, oversized payloads, failed handshakes, EOF, and non-`EAGAIN` receive failures trigger shutdown.

## Send Path
`o2net_send_message_vec()`:
- validates workqueue availability, vector length, payload length, and target node.
- waits until `o2net_tx_can_proceed()` returns either a valid socket or a persistent error.
- allocates a status waiter in the node IDR.
- prepends an `o2net_msg` header with the waiter ID in `msg_num`.
- sends under `sc_send_lock`.
- waits for the peer’s `O2NET_MSG_STATUS_MAGIC`.
- returns translated system status, optionally filling caller status.

This is synchronous and can block on socket readiness, send completion, and remote handler completion.

## Receive Dispatch
`o2net_process_message()` handles:
- `O2NET_MSG_STATUS_MAGIC`: completes a pending status waiter.
- `O2NET_MSG_KEEP_REQ_MAGIC`: sends a keepalive response.
- `O2NET_MSG_KEEP_RESP_MAGIC`: refreshes idle state without further action.
- `O2NET_MSG_MAGIC`: looks up registered handler by `(msg_type, key)`, validates payload length, invokes handler, sends status response, and invokes optional post-handler.

Handlers are stored in an RB tree guarded by `o2net_handler_lock`; handler references are protected by `kref`.

## Handshake and Timeout Validation
`o2net_check_handshake()` requires peers to match:
- `O2NET_PROTOCOL_VERSION`
- O2NET idle timeout
- keepalive delay
- heartbeat write timeout.

Mismatch causes persistent `-ENOTCONN` shutdown to avoid unsafe cluster behavior.

## Keepalive, Idle Timeout, and Quorum
`o2net_sc_reset_idle_timer()` schedules keepalive work and idle timer. Any valid incoming message calls `o2net_sc_postpone_idle()`, which clears timeout/quorum error state if the connection recovered. Idle timeout does not immediately shut down the socket; it marks timeout, reports quorum connection error, schedules delayed still-up quorum work, and restarts the timer.

## Listening and Accept
`o2net_start_listening()` allocates an ordered reclaim-safe workqueue and opens a TCP listening socket. `o2net_accept_many()` drains pending accepts to avoid queued connections being stranded under interrupt moderation. Accepted sockets are validated by source IP, node-number direction, heartbeat state, and duplicate connection checks before a socket container is attached.

## Shutdown
`o2net_stop_listening()` detaches listen callbacks, disconnects all configured nodes, destroys the workqueue, releases the listening socket, and reports local quorum connection error. `o2net_disconnect_node()` sets persistent `-ENOTCONN`, cancels delayed work, and flushes the workqueue.

## Important Dependencies
- OCFS2 cluster heartbeat and node manager.
- O2CB quorum subsystem.
- Linux kernel socket/TCP APIs.
- `idr`, `kref`, workqueues, timers, spinlocks, mutexes.
- `tcp_internal.h` protocol structures and constants.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp.h

## Purpose
Public header for the OCFS2 cluster TCP transport. It defines the on-wire message header, payload limits, timeout defaults, public send/handler APIs, lifecycle entry points, and debugfs hooks.

## Key Types
- `struct o2net_msg`: fixed network message header followed by flexible payload:
  - `magic`
  - `data_len`
  - `msg_type`
  - `sys_status`
  - `status`
  - `key`
  - `msg_num`
  - `buf[]`
- `o2net_msg_handler_func`: called for incoming application messages.
- `o2net_post_msg_handler_func`: optional post-processing callback after status send.

## Limits and Defaults
- `O2NET_MAX_PAYLOAD_BYTES` is one page minus `struct o2net_msg`.
- Default reconnect and keepalive delay: 2000 ms.
- Default idle timeout: 30000 ms.
- `O2NET_TCP_USER_TIMEOUT` is set to `0x7fffffff`.

## Link Failure Helper
`o2net_link_down()` classifies socket state and selected errno values as link failures. It treats non-established/non-close-wait sockets and errors such as `-ECONNREFUSED`, `-ENOTCONN`, `-ECONNRESET`, and `-EPIPE` as down.

## Public API Surface
- Message send:
  - `o2net_send_message()`
  - `o2net_send_message_vec()`
- Handler management:
  - `o2net_register_handler()`
  - `o2net_unregister_handler_list()`
- Connectivity:
  - `o2net_fill_node_map()`
  - `o2net_num_connected_peers()`
  - `o2net_disconnect_node()`
- Heartbeat/listener lifecycle:
  - `o2net_register_hb_callbacks()`
  - `o2net_unregister_hb_callbacks()`
  - `o2net_start_listening()`
  - `o2net_stop_listening()`
- Module lifecycle:
  - `o2net_init()`
  - `o2net_exit()`

## Debugfs Hooks
Declares debugfs setup/teardown and tracking hooks for send tracking and socket containers. When `CONFIG_DEBUG_FS` is disabled, all hooks compile to no-ops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp_internal.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/cluster/tcp_internal.h

## Purpose
Internal transport definitions for OCFS2 O2CB TCP. It captures message magic values, protocol version, handshake layout, per-node/socket state, handler tracking, status waiters, and debug send tracking.

## Wire Constants
Defines message magic values:
- `O2NET_MSG_MAGIC`
- `O2NET_MSG_STATUS_MAGIC`
- `O2NET_MSG_KEEP_REQ_MAGIC`
- `O2NET_MSG_KEEP_RESP_MAGIC`

`O2NET_PROTOCOL_VERSION` is `11`, with comments documenting historical protocol changes and explaining that version 11 separates filesystem locking negotiation from the transport protocol.

## Handshake
`struct o2net_handshake` includes:
- protocol version
- connector ID
- heartbeat timeout
- idle timeout
- keepalive delay
- reconnect delay.

These values are validated during connection setup to avoid unsafe mixed-timeout cluster behavior.

## Per-Node State
`struct o2net_node` stores:
- lock-protected socket container pointer and validity bit
- persistent error for future sends
- timeout flag
- waitqueue for socket state changes
- IDR/list for pending status waiters
- delayed connect, connect-expired, and quorum still-up work.

## Socket State
`struct o2net_sock_container` stores:
- kref
- socket and node pointer
- RX/connect/shutdown/keepalive work
- idle timer
- handshake state
- receive page and offset
- saved original socket callbacks
- current message key/type for stats/debug
- send mutex
- optional debug/stat timing counters.

## Handler and Status Wait Structures
`struct o2net_msg_handler` is the RB-tree entry for registered handlers, keyed by message type and key, with max payload length, handler callbacks, kref, and unregister-list linkage.

`struct o2net_status_wait` records a pending synchronous send’s system status, user status, IDR ID, waitqueue, and per-node list linkage.

## System Error Enum
`enum o2net_system_error` defines wire-level transport statuses:
- none
- no handler
- overflow
- died.

These are translated by tcp.c into Linux errno values.

## Debug Tracking
`struct o2net_send_tracking` records task, socket container, message ID/type/key, target node, and timing points when debugfs is enabled; otherwise it is reduced to a dummy field.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/cluster/tcp_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dcache.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dcache.c

## Purpose
Implements OCFS2 dentry cache behavior, including dentry revalidation, negative dentry generation tracking, cluster dentry-lock attachment/sharing, alias lookup, dentry lock cleanup, and dentry movement during rename.

## Negative Dentry Handling
`ocfs2_dentry_attach_gen()` stores the parent directory lock generation in `dentry->d_fsdata` for negative dentries. `ocfs2_dentry_revalidate()` compares that stored generation to the parent’s current `ip_dir_lock_gen`; mismatches invalidate the negative dentry.

## Positive Dentry Revalidation
`ocfs2_dentry_revalidate()` rejects:
- RCU lookup mode with `-ECHILD`
- root inode and bad inode cases
- inodes marked `OCFS2_INODE_DELETED`
- inodes with `i_nlink == 0`
- positive dentries without attached dentry-lock data.

Valid positive dentries rely on cluster dentry locks to receive invalidation on remote unlink/rename.

## Alias Lookup
`ocfs2_find_local_alias()` walks an inode’s alias list under `inode->i_lock`, checks parent block number and dentry fsdata, optionally skips unhashed dentries, and returns a pinned matching alias. This lets multiple local dentries for links in the same parent share one dentry lock.

## Dentry Lock Attachment
`ocfs2_dentry_attach_lock()` attaches a positive dentry to an `ocfs2_dentry_lock`, requiring the parent directory semaphore and cluster lock to already be held. It:
- ignores negative dentries.
- handles negative-to-positive conversion by clearing generation fsdata.
- reuses an existing alias lock if possible.
- otherwise allocates a new `ocfs2_dentry_lock`, grabs an inode reference, initializes a lock resource, and stores parent block number.
- increments `dl_count` under global `dentry_attach_lock`.
- briefly obtains/releases the PR-mode dentry lock to establish cluster notification.

## Lock Cleanup
`ocfs2_dentry_iput()` is the dentry operation for final inode put. It drops the dentry lock count and eventually frees the lock resource and inode reference through `ocfs2_dentry_lock_put()` and `ocfs2_drop_dentry_lock()`.

If a positive hashed dentry lacks lock data, it logs an error because cluster invalidation would be missing.

## Rename Move Handling
`ocfs2_dentry_move()` performs `d_move()` while keeping lock data consistent. If the parent directory changes, it drops the old dentry lock and attaches a new one based on the new parent block number before moving the dentry.

## Synchronization
The file uses:
- inode alias lock and dentry lock for alias traversal
- global `dentry_attach_lock` for attach/detach count changes
- OCFS2 cluster lock/resource APIs for distributed invalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dcache.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dcache.h

## Purpose
Declares OCFS2 dcache operations and dentry lock structures.

## Main Structure
`struct ocfs2_dentry_lock` contains:
- reference count `dl_count`
- parent directory block number
- held inode reference
- embedded OCFS2 lock resource.

The inode reference is kept until the lock resource is destroyed.

## Public Declarations
- `ocfs2_dentry_ops`: dentry operation table.
- `ocfs2_dentry_attach_lock()`: attach positive dentry to cluster dentry lock.
- `ocfs2_dentry_lock_put()`: decrement/free dentry lock.
- `ocfs2_find_local_alias()`: find alias in same parent.
- `ocfs2_dentry_move()`: rename-aware dentry move.
- `ocfs2_dentry_attach_gen()`: attach parent generation to negative dentry.
- `dentry_attach_lock`: global spinlock protecting lock attach/detach accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dir.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dir.c

## Purpose
Implements OCFS2 directory operations: lookup, validation, insertion, deletion, readdir, empty-dir checks, new directory initialization, inline-to-extent directory expansion, indexed directory creation/maintenance, free-space tracking, index splitting/rebalancing, and dx-index truncation.

## Directory Formats
The code supports:
- inline-data directories stored inside the dinode.
- extent-backed unindexed directories.
- indexed directories with a dx root and optional dx leaf blocks.
- directory block trailers for metadata ECC and indexed-directory free-list accounting.

`ocfs2_supports_dir_trailer()` and `ocfs2_new_dir_wants_trailer()` decide whether a directory block reserves trailing trailer space.

## Validation
The file validates:
- dirent record length, alignment, name length, and block bounds via `ocfs2_check_dir_entry()`.
- directory block ECC via `ocfs2_validate_dir_block()`.
- directory trailers via `ocfs2_check_dir_trailer()`.
- dx root and dx leaf signatures/ECC/layout via `ocfs2_validate_dx_root()` and `ocfs2_validate_dx_leaf()`.

Read helpers intentionally squash many read/validation failures to `-EIO` after logging.

## Lookup
`ocfs2_find_entry()` dispatches by format:
- inline: `ocfs2_find_entry_id()`
- extent/unindexed: `ocfs2_find_entry_el()` with readahead and wraparound search
- indexed: `ocfs2_find_entry_dx()`.

Indexed lookup hashes the name using TEA-derived ext3-style hashing, locates the correct dx root/leaf entry, then reads the referenced unindexed dirent block and confirms the actual name.

## Hashing and Index Mapping
`ocfs2_dx_dir_name_hash()` computes major/minor hash values using the filesystem dx seed. Major hash selects a dx cluster range; minor hash selects a block offset within the cluster using `osb_dx_mask`.

## Directory Entry Modification
- `ocfs2_update_entry()` changes an existing dirent’s inode and file type.
- `ocfs2_delete_entry()` dispatches deletion by format.
- `__ocfs2_delete_entry()` removes a dirent by merging record length into the previous entry or clearing inode when first.
- Indexed deletion also removes the corresponding dx entry and updates dx root entry counts and free-list trailer state.

## Insert Path
The public preparation/add flow is:
1. `ocfs2_prepare_dir_for_insert()` finds or creates a block with space and fills `ocfs2_dir_lookup_result`.
2. `__ocfs2_add_entry()` journals the needed buffers, optionally inserts a dx entry, splits an existing dirent if needed, writes the new dirent, recalculates indexed free-list state, updates mtime/ctime and i_version, and dirties buffers.

For indexed directories, preparation first ensures index capacity, may expand inline dx root to external leaves, searches the dx free list for unindexed dirent space, and extends the directory if needed.

## Readdir
`ocfs2_readdir()` takes the inode lock, updates atime, downgrades from EX to PR when possible, and calls `ocfs2_dir_foreach_blk()`. Iteration supports inline and extent-backed directories, handles i_version changes by rescanning to a safe dirent boundary, validates each emitted entry, and performs simple buffer-head readahead for extent directories.

## Empty Directory Check
`ocfs2_empty_dir()` uses a dir-context callback to verify `.` and `..` at expected offsets and detect any other entries. For indexed directories it first checks `dr_num_entries == 2`, then still scans the directory for dot/dotdot validation.

## New Directory Creation
`ocfs2_fill_new_dir()` selects:
- inline initialization if inline data is enabled on the inode.
- indexed directory initialization if filesystem supports indexed dirs.
- plain extent-backed initialization otherwise.

`ocfs2_fill_initial_dirents()` writes `.` and `..`. Extent-backed creation can initialize trailers. Indexed creation first builds an unindexed directory block, then attaches a dx root and indexes `.` and `..`.

## Inline-to-Extent Expansion
`ocfs2_expand_inline_dir()` converts an inline directory to extent-backed storage. It:
- reserves data and optional metadata/index allocations.
- handles quota accounting.
- copies inline dirents to a new block.
- expands the final dirent and initializes trailers.
- clears `OCFS2_INLINE_DATA_FL`.
- inserts data extents.
- optionally attaches and populates a dx index.
- returns lookup buffers needed to finish the pending insert.

The implementation carefully orders journal operations so partially completed conversion leaves consistent directory contents.

## Directory Extension
`ocfs2_extend_dir()` grows extent-backed directories by one block, allocating a new cluster when `i_size` reaches allocated clusters. It formats the new block as one empty dirent, initializes a trailer if needed, links it into indexed free-list state, updates size and inode blocks, and returns the new buffer.

## Indexed Directory Growth
Indexed directories use:
- inline dx root until root entry capacity is exhausted.
- external dx leaf clusters after `ocfs2_expand_inline_dx_root()`.
- `ocfs2_find_dir_space_dx()` to locate or rebalance a dx leaf.
- `ocfs2_dx_dir_rebalance()` to split full dx leaf clusters.

Rebalancing sorts a full leaf, chooses a split hash while handling same-major-hash corner cases, allocates/formats a new leaf cluster, inserts the extent, and transfers entries with major hashes greater than or equal to the split point.

## Free-Space Tracking
Directory block trailers maintain:
- largest free record length
- linked-list pointer for dx free list.

Insertion recalculates or removes a block from the free list. Deletion adds a block to the free list if it newly gains reusable space.

## Truncation and Index Removal
`ocfs2_dx_dir_truncate()` removes external dx index extents, then `ocfs2_dx_dir_remove_index()` clears `OCFS2_INDEXED_DIR_FL`, zeros `i_dx_root`, frees the dx root metadata bit, flushes truncate log work, and runs cached deallocations.

## Important Dependencies
This file is tightly coupled to OCFS2 allocation, journaling, inode locking, metadata ECC, extent maps, quota accounting, truncate/dealloc logic, and the VFS dir-context API.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dir.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dir.h

## Purpose
Public internal header for OCFS2 directory manipulation.

## Key Structures
`struct ocfs2_dx_hinfo` stores directory-name hash results:
- `major_hash`
- `minor_hash`

`struct ocfs2_dir_lookup_result` is the shared lookup/preparation context for directory operations. It can hold:
- unindexed leaf buffer and dirent
- dx root buffer
- dx leaf buffer and dx entry
- computed hash info
- previous free-list leaf buffer for indexed free-space maintenance.

## Declared Operations
- lookup/free:
  - `ocfs2_find_entry()`
  - `ocfs2_free_dir_lookup_result()`
- mutation:
  - `ocfs2_delete_entry()`
  - `__ocfs2_add_entry()`
  - inline wrapper `ocfs2_add_entry()`
  - `ocfs2_update_entry()`
- checks:
  - `ocfs2_check_dir_for_entry()`
  - `ocfs2_empty_dir()`
- name-to-inode lookup:
  - `ocfs2_find_files_on_disk()`
  - `ocfs2_lookup_ino_from_name()`
- iteration:
  - `ocfs2_readdir()`
  - `ocfs2_dir_foreach()`
- insertion preparation:
  - `ocfs2_prepare_dir_for_insert()`
- creation/truncation:
  - `ocfs2_fill_new_dir()`
  - `ocfs2_dx_dir_truncate()`
- trailer utility:
  - `ocfs2_dir_trailer_from_size()`
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/Makefile -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/Makefile

## Purpose
Builds the OCFS2 O2CB distributed lock manager object when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Build Output
Adds `ocfs2_dlm.o` to the build:
```make
obj-$(CONFIG_OCFS2_FS_O2CB) += ocfs2_dlm.o
```

## Component Objects
`ocfs2_dlm.o` is linked from:
- `dlmdomain.o`
- `dlmdebug.o`
- `dlmthread.o`
- `dlmrecovery.o`
- `dlmmaster.o`
- `dlmast.o`
- `dlmconvert.o`
- `dlmlock.o`
- `dlmunlock.o`

This places `dlmast.c` in the main DLM module with domain, recovery, mastership, conversion, lock, and unlock code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmapi.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmapi.h

## Purpose
Defines the externally exported OCFS2 DLM API used by filesystem code and other DLM clients.

## Status Model
`enum dlm_status` defines DLM return/status codes, including:
- normal/granted/denied states
- blocked and async-working states
- resource and argument errors
- value-block validity errors
- recovery and migration extension statuses
- protocol/version and device-related errors.

`dlm_errname()` returns printable names, and `dlm_error()` logs most statuses while suppressing routine recovery/migration/forward statuses.

## Lock Status Block
`struct dlm_lockstatus` exposes:
- `status`
- `flags`
- opaque `lockid`
- 64-byte LVB buffer.

Callers are documented as only allowed to access `status` and `lvb`.

## Lock Modes
Defines DLM modes:
- invalid
- null
- concurrent read/write placeholders
- protected read
- protected write placeholder
- exclusive.

OCFS2 compatibility logic mainly supports NL, PR, and EX.

## Lock Flags
Defines public lock/unlock flags such as:
- `LKM_VALBLK`
- `LKM_NOQUEUE`
- `LKM_CONVERT`
- `LKM_UNLOCK`
- `LKM_CANCEL`
- `LKM_INVVALBLK`
- `LKM_FORCE`.

Also defines internal OCFS2 extensions:
- `LKM_MIGRATION`
- `LKM_PUT_LVB`
- `LKM_GET_LVB`
- `LKM_RECOVERY`.

## Callback Types
- `dlm_astlockfunc_t`: lock grant AST.
- `dlm_bastlockfunc_t`: blocking AST.
- `dlm_astunlockfunc_t`: unlock AST.

## Public Operations
- `dlmlock()`: request or convert a lock.
- `dlmunlock()`: unlock/cancel/deallocate lock.
- `dlm_register_domain()`: join/register a DLM domain with filesystem protocol version.
- `dlm_unregister_domain()`: leave/unregister domain.
- `dlm_print_one_lock()`: debug print a lock.
- eviction callback setup/register/unregister functions.

## Protocol Version Type
`struct dlm_protocol_version` stores major/minor protocol values for DLM/filesystem locking negotiation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmast.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmast.c

## Purpose
Implements OCFS2 DLM AST and BAST handling for local and remote locks. ASTs notify lock grant/conversion completion; BASTs notify that a granted lock blocks another request and should be downconverted.

## AST/BAST Queueing
`__dlm_queue_ast()` and `__dlm_queue_bast()` place locks on DLM pending AST/BAST lists under `dlm->ast_lock`, taking an extra lock reference while queued. Public `dlm_queue_ast()` wraps the AST queue path with locking.

`dlm_should_cancel_bast()` suppresses obsolete BASTs when an AST changes a lock mode so it no longer blocks the highest blocked mode. For example, a lock downconverted to NL no longer needs a BAST.

## LVB Handling
`dlm_update_lvb()` updates lock value block state when this node owns the lock resource:
- GET requests copy the resource LVB into the lockstatus block.
- PUT requests are intentionally not applied here because downconvert paths should already apply them in place.
- GET/PUT flags are cleared afterward.

## Local AST/BAST Execution
`dlm_do_local_ast()`:
- verifies the lock is local
- updates LVB state
- invokes the lock’s AST callback with `astdata`.

`dlm_do_local_bast()`:
- verifies local ownership
- invokes the BAST callback with `astdata` and blocked mode.

These callbacks are expected to be callable in the DLM execution context.

## Remote AST Execution
`dlm_do_remote_ast()` updates LVB state and sends a proxy AST to the remote lock holder via `dlm_send_proxy_ast()`.

`dlm_send_proxy_ast_msg()` constructs `struct dlm_proxy_ast`, optionally appends LVB data for GET_LVB, and sends it over `o2net_send_message_vec()` with message type `DLM_PROXY_AST_MSG`. It treats `DLM_RECOVERING` and `DLM_MIGRATING` responses as fatal inconsistencies.

## Proxy AST Handler
`dlm_proxy_ast_handler()` receives proxy AST/BAST messages from the lock resource master. It:
- grabs the DLM context.
- validates domain join state, name length, LVB flags, and AST type.
- looks up the lock resource.
- rejects recovery/migration states with `DLM_RECOVERING` or `DLM_MIGRATING`.
- finds the target lock in converting/blocked/granted lists depending on AST type.
- for AST, moves the lock to granted, applies convert mode, sets `lksb->status`, and copies incoming LVB if requested.
- drops the resource lock and invokes local AST or BAST callback.

Unknown lock/resource cases generally return `DLM_IVLOCKID` or `DLM_NORMAL` depending on whether the condition can be safely ignored.

## Important Dependencies
- O2CB TCP transport for proxy messaging.
- DLM lock-resource list discipline and reference counting.
- DLM recovery/migration state flags.
- LVB flags from `dlmapi.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmcommon.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmcommon.h

## Purpose
Internal common header for the OCFS2 DLM. It defines core DLM data structures, message IDs and wire formats, lock/resource state flags, helper functions, and cross-file function declarations.

## Core Constants
- Heartbeat callback priorities for DLM node up/down.
- `DLM_LOCKID_NAME_MAX` of 32 bytes.
- unknown owner marker `DLM_LOCK_RES_OWNER_UNKNOWN`.
- hash sizing constants for lock resources and master-list entries.
- recovery lock name `$RECOVERY`.

## Master List Entries
`struct dlm_master_list_entry` tracks lock-resource mastership discovery/migration:
- hash/list linkage
- DLM context
- spinlock, waitqueue, refs
- maybe/vote/response/node maps
- master/new master
- MLE type
- heartbeat callbacks
- associated lock resource/name/hash.

## DLM Context
`struct dlm_ctxt` is the domain-level state object. It includes:
- lock resource hash
- dirty/purge/pending AST/BAST/tracking lists
- domain node maps
- recovery context
- master hash and MLE heartbeat events
- counters
- debugfs root
- refs/domain state/join count
- heartbeat callbacks
- DLM and recovery threads
- worker queue and work list
- domain message handlers and eviction callbacks
- filesystem and DLM protocol versions.

## Lock Resource
`struct dlm_lock_resource` represents one named lock resource:
- hash node and qstr name
- kref
- granted/converting/blocked lock lists
- purge/dirty/recovering/tracking lists
- last-used timestamp
- owner node
- state flags
- LVB
- inflight lock/assert-worker counters
- AST reservations
- refmap.

State flags include uninitialized, recovering, ready, dirty, in-progress, migrating, dropping-ref, block-dirty, setref-in-progress, and recovery-waiting.

## Lock
`struct dlm_lock` wraps `struct dlm_migratable_lock` plus:
- list links for resource and AST/BAST queues
- lock resource pointer
- spinlock and kref
- AST/BAST callbacks and data
- lockstatus pointer
- pending flags for AST, BAST, convert, lock, cancel, unlock
- kernel-allocated LKSB flag.

## Wire Message IDs
Defines DLM message IDs beginning at 500:
- master request/assert/requery
- create/convert/unlock lock
- proxy AST
- deref lockres and done
- migration request/migratable lockres
- join/cancel/exit domain
- recovery begin/finalize/data done
- query region/nodeinfo.

These IDs are sent over the O2CB TCP message transport.

## Wire Structures
Defines network packet layouts for:
- master requests and assertions
- migrate requests and migratable lock resources
- create/convert/unlock lock messages
- proxy AST messages
- join/query/cancel domain messages
- recovery messages
- deref lockres messages
- region/nodeinfo query responses.

The migratable lock-resource layout is designed to fit up to 240 locks in one O2NET payload, leaving reserved bytes for future use.

## Helper Functions
Inline helpers cover:
- list index to text/list pointer
- empty LVB check
- lock-resource state to DLM status
- lock-cookie node/sequence decoding
- recovery lock name test
- lock mode printable name
- NL/PR/EX compatibility
- lock membership on a list
- errno-to-DLM-status conversion
- bitmap node iteration
- setting/changing lock-resource owner.

## Function Declaration Surface
Declares internal functions for:
- lock allocation/refcounting/attachment
- network message handlers
- pending convert/lock rollback and cancel/unlock commit
- DLM and recovery thread lifecycle
- recovery waits and node death checks
- DLM context refs and domain state
- lock-resource hash lookup/insert/remove
- lock-resource refmaps and inflight refs
- AST/BAST queueing and proxy sends
- dirtying/kicking lock resources
- heartbeat callbacks
- migration/recovery/mastership handlers
- purge and dealloc helpers
- slab cache lifecycle.

## Architectural Role
This header is the central contract between DLM implementation files. It binds together the domain state machine, lock-resource lifecycle, distributed mastership protocol, recovery protocol, and O2NET wire protocol.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmcommon.h -->