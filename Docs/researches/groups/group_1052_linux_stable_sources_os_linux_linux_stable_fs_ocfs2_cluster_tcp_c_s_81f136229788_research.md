# Group Research: group_1052_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_cluster_tcp_c_s_81f136229788

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.c

## Summary
Implements the O2CB/OCFS2 TCP transport layer. It owns node-to-node socket lifecycle, protocol handshakes, framed message send/receive, synchronous status waits, message handler registration, keepalive and idle-timeout behavior, heartbeat callbacks, listening/accepting, outbound connect attempts, debug/stat tracking hooks, and quorum notifications on connection failure or recovery.

## Main Responsibilities
- Maintain per-node `struct o2net_node` connection state and per-socket `struct o2net_sock_container` lifetime/refcounting.
- Register and unregister typed message handlers in an rb-tree keyed by message type and cluster key.
- Send payload vectors as `struct o2net_msg` frames and wait for remote handler status replies.
- Receive and demultiplex status, keepalive request/response, and application messages from a single page buffer per socket.
- Negotiate protocol and timing parameters through the initial `struct o2net_handshake`.
- Drive active connects from the higher-numbered node and passive accepts from the lower-numbered node.
- Integrate heartbeat up/down callbacks with connect retry, disconnect, and quorum state.
- Start and stop the ordered `o2net` workqueue and listening socket.

## Key Interfaces
- `o2net_send_message_vec()` and `o2net_send_message()` are the exported synchronous transmit APIs.
- `o2net_register_handler()` and `o2net_unregister_handler_list()` manage receive handlers.
- `o2net_fill_node_map()` reports currently reachable peer nodes.
- `o2net_start_listening()` and `o2net_stop_listening()` manage the local TCP listener.
- `o2net_register_hb_callbacks()` and `o2net_unregister_hb_callbacks()` attach transport behavior to heartbeat events.
- `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()` expose lifecycle and status helpers.

## Important Behavior
Messages are framed with magic, payload length, message type, key, message id, system status, and handler status. Transmit allocates a message id from the target node's `idr`, sends the header plus caller vectors under `sc_send_lock`, then waits on `ns_wq` until the receive path completes the matching status wait. If the remote side reports a transport/system condition, that is translated through `o2net_sys_err_to_errno()` before any handler status is returned.

Receive is incremental and nonblocking. Before the handshake completes, `o2net_advance_rx()` reads exactly a handshake and validates protocol version, idle timeout, keepalive delay, and heartbeat write timeout. After that, it reads a message header, validates payload length against `O2NET_MAX_PAYLOAD_BYTES`, reads the payload, and calls `o2net_process_message()`. Any framing error or non-EAGAIN receive failure shuts down the socket.

The socket callback layer queues work before invoking original socket callbacks. `data_ready` queues receive work; `state_change` queues connect-complete work on `TCP_ESTABLISHED` and shutdown work on other terminal states. Callback unregistration restores the original socket callbacks and drops the callback-held socket-container reference.

Connection establishment is deliberately asymmetric: the higher numbered node initiates outbound connects when heartbeat says the lower numbered node is alive; the lower numbered node accepts only if the connecting peer is known, lower/higher ordering is correct, and heartbeat confirms the peer. This prevents duplicate cross-connects.

Keepalive uses a delayed work item to send `O2NET_MSG_KEEP_REQ_MAGIC` and a timer for idle detection. Idle timeout does not immediately close the socket; it marks the node timed out, notifies quorum, queues delayed "still up" work, and resets the idle timer. Any later message activity clears that timeout and tells quorum the connection is up again.

## State and Synchronization
Per-node state is protected by `nn_lock`; handler tree access uses `o2net_handler_lock`; socket callback mutation uses `sk_callback_lock`; socket sends use `sc_send_lock`; work items hold socket-container references while queued. Pending sends are tracked in `nn_status_idr` and `nn_status_list`. The ordered workqueue serializes most blocking transport work, and shutdown carefully detaches callbacks before socket shutdown and workqueue teardown.

## Cross-File Interactions
This file is the transport used by the OCFS2 DLM and cluster modules. It depends on nodemanager for node numbers/IP configuration, heartbeat for node up/down events, quorum for fencing decisions, `tcp_internal.h` for private state and wire constants, `tcp.h` for exported message APIs, and debugfs helpers for optional transport state exposure. DLM files such as `dlmast.c` send and receive DLM messages through these APIs.

## Risks
Correctness depends on exact connection state transitions and reference ownership: queued work, socket callbacks, timers, and node state can race during shutdown. Handler status waits must always be completed on disconnect to avoid blocked senders. Handshake timeout mismatches are treated as fatal because inconsistent liveness windows can cause split-brain or corruption. The receive page is only valid during handler execution, so handlers must not retain pointers into it. The ordered workqueue and `memalloc_nofs_save()` usage are important to avoid filesystem reclaim recursion during socket allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.h

## Summary
Defines the public O2CB TCP transport API and the common network message header used by OCFS2 cluster components. It exposes send, handler registration, heartbeat/listener lifecycle, connected-node discovery, and optional debugfs hooks.

## Main Responsibilities
- Define `struct o2net_msg`, the framed network message header plus flexible payload buffer.
- Define handler and post-handler callback signatures for incoming message processing.
- Publish payload and timeout constants, including default reconnect, keepalive, idle, and TCP user-timeout values.
- Provide `o2net_link_down()` for classifying socket/errors as connection-loss conditions.
- Declare exported transport lifecycle, send, handler, and heartbeat/listener functions.
- Hide debugfs operations behind no-op inline stubs when `CONFIG_DEBUG_FS` is disabled.

## Key Interfaces
- `o2net_send_message()` and `o2net_send_message_vec()` send one message and optionally return remote handler status.
- `o2net_register_handler()` registers a message type/key callback with a maximum accepted payload length and optional post callback.
- `o2net_unregister_handler_list()` unregisters a caller-owned list of registered handlers.
- `o2net_fill_node_map()` fills a bitmap of currently connected peers.
- `o2net_start_listening()`, `o2net_stop_listening()`, and `o2net_disconnect_node()` control per-node network connectivity.
- `o2net_register_hb_callbacks()` and `o2net_unregister_hb_callbacks()` connect the transport to cluster heartbeat.

## Important Behavior
`O2NET_MAX_PAYLOAD_BYTES` is capped at one page minus the header size, matching the transport implementation's one-page receive buffer. The link-down helper treats non-established/non-close-wait sockets and selected negative errors as loss of connection, while nonnegative results are considered successful. The driver state enum distinguishes uninitialized and ready states for users that need coarse transport readiness.

## State and Synchronization
This header does not own runtime state. It forward-declares `struct o2net_send_tracking` and `struct o2net_sock_container` so debugfs helpers can observe transport internals without exposing their definitions publicly.

## Cross-File Interactions
`tcp.c` implements the declarations. `tcp_internal.h` supplies private constants and structures. DLM and other OCFS2 cluster modules include this header to register message handlers and exchange cluster messages.

## Risks
All callers must respect the maximum payload size and must not assume asynchronous completion: the send API blocks waiting for a remote status reply or connection failure. Handler callbacks receive a buffer owned by the transport receive page and cannot retain payload pointers beyond the callback. `o2net_link_down()` is intentionally conservative and any changes to its error list affect DLM recovery and quorum behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp_internal.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp_internal.h

## Summary
Defines private O2CB TCP transport wire constants and in-memory state shared by `tcp.c` and related debug/stat code. It contains message magic values, protocol version history, handshake layout, per-node state, per-socket state, handler descriptors, status-wait records, and debug send-tracking structures.

## Main Responsibilities
- Define wire magic values for normal messages, status replies, keepalive requests, and keepalive responses.
- Define `O2NET_PROTOCOL_VERSION` and document historical protocol/locking-semantic changes.
- Define `struct o2net_handshake` used to validate protocol and timeout compatibility.
- Define `struct o2net_node` for per-peer connection, error, timeout, wait, status-id, and delayed-work state.
- Define `struct o2net_sock_container` for socket lifetime, callbacks, receive framing, idle/keepalive work, and send locking.
- Define `struct o2net_msg_handler` for rb-tree handler registration.
- Define transport-level system errors and `struct o2net_status_wait` for synchronous request completion.
- Define optional debugfs timing and send-tracking fields.

## Key Interfaces
This header has no exported functions. Its key data contracts are:
- `o2net_handshake`: protocol version, connector id, heartbeat timeout, idle timeout, keepalive delay, and reconnect delay.
- `o2net_node`: `nn_sc`, `nn_sc_valid`, `nn_persistent_error`, `nn_timeout`, status `idr`, waitqueue, and connect/expiry/still-up delayed work.
- `o2net_sock_container`: socket reference, node reference, receive/connect/shutdown work, idle timer, keepalive work, receive page offset, original socket callbacks, message identity, and `sc_send_lock`.
- `o2net_system_error`: remote status classes that map to local errno values.

## Important Behavior
The protocol version is not just a packet-format version; comments state it historically covered filesystem locking semantics too. Version 11 introduced separate filesystem locking negotiation in DLM join, reducing the need to bump this transport protocol for filesystem lock changes.

The per-node comments describe critical lifecycle rules: `nn_sc` is set when a socket container is allocated and connection begins; `nn_sc_valid` becomes true only after handshake success; `nn_persistent_error` makes transmit fail immediately; and generation changes wake waiters on `nn_sc_wq`. Delayed connect work can requeue itself, so shutdown must first set state to prevent new connects, then cancel work and flush.

The per-socket comments document why work items hold references and why shutdown can be queued both by explicit state changes and by socket callbacks. Teardown must remove the socket from the node before waiting on work, or shutdown work can detach the socket and rearm itself.

## State and Synchronization
`o2net_node` uses `nn_lock` for node state and status lists, `nn_sc_wq` for transmit waiters, and delayed work for connect retry, connect expiry, and quorum still-up checks. `o2net_sock_container` uses `kref` for lifetime, socket callback locks indirectly through `tcp.c`, a timer for idle timeout, delayed work for keepalive, and `sc_send_lock` to serialize socket writes.

## Cross-File Interactions
`tcp.c` directly allocates, mutates, and tears down these structures. The message sizing depends on `tcp.h`'s `struct o2net_msg`. DLM code indirectly depends on the protocol version and message error semantics because DLM messages are transported over this layer.

## Risks
This header encodes concurrency and lifecycle invariants rather than mere layout. Misinterpreting `nn_sc` versus `nn_sc_valid`, failing to hold references around queued work, or changing protocol/timeout fields without matching handshake validation can break cluster liveness. The fixed one-page payload model ties `O2NET_MAX_PAYLOAD_BYTES`, DLM migratable lockres sizing, and receive-buffer safety together.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/cluster/tcp_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dcache.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dcache.c

## Summary
Implements OCFS2 dentry cache validation and cluster dentry-lock attachment. It keeps local VFS dentries coherent with clustered directory operations by associating positive dentries with lock resources keyed by parent directory block and target inode, validating stale dentries, sharing locks among local aliases, releasing dentry locks on final put, and preserving lock semantics across rename/move.

## Main Responsibilities
- Attach generation values to negative dentries so they can be invalidated when the parent directory lock generation changes.
- Revalidate positive and negative dentries for VFS lookup.
- Find local aliases for an inode under a specific parent directory block.
- Attach positive dentries to an `ocfs2_dentry_lock`, creating or reusing the per-parent/inode lock resource.
- Drop dentry-lock references and release underlying cluster lock resources.
- Provide `d_iput` cleanup and a lock-aware `d_move()` helper used by rename.
- Publish `ocfs2_dentry_ops`.

## Key Interfaces
- `ocfs2_dentry_attach_gen()` stores the parent directory lock generation on a negative dentry.
- `ocfs2_dentry_attach_lock()` attaches a positive dentry to a cluster dentry lock and briefly takes/releases the PR lock.
- `ocfs2_find_local_alias()` searches the inode alias list for another dentry with the same parent block.
- `ocfs2_dentry_lock_put()` decrements lock sharing and destroys the lock when the last dentry reference disappears.
- `ocfs2_dentry_move()` updates dentry lock ownership when a dentry moves between directories.
- `ocfs2_dentry_ops` installs `.d_revalidate` and `.d_iput`.

## Important Behavior
Negative dentry validation compares the stored generation in `d_fsdata` to `OCFS2_I(dir)->ip_dir_lock_gen`. A mismatch invalidates the dentry. Positive dentries are invalidated if they point to the root inode, a bad inode, an inode marked `OCFS2_INODE_DELETED`, an inode with zero link count, or a dentry missing cluster-lock state.

Dentry locks are per target inode within a parent directory, not per full filename. The file comments explain this as a compromise: full names are too large for cluster lock names, but parent-directory scoping plus directory locks still lets all nodes agree about unlink/rename invalidation.

`ocfs2_dentry_attach_lock()` is called with parent directory semaphore and parent directory cluster lock held. It reuses an alias lock when one already exists for the same parent block; otherwise it allocates a new `ocfs2_dentry_lock`, grabs an inode reference, initializes the lock resource, installs it under `dentry_attach_lock`, and acquires/releases the dentry lock once to establish PR-mode notification.

`ocfs2_dentry_move()` leaves lock state unchanged for same-directory moves. Cross-directory moves drop the old dentry-lock reference, clear `d_fsdata`, attach a new lock keyed by the new parent block, and then calls `d_move()`.

## State and Synchronization
The global `dentry_attach_lock` protects attachment/detachment and the shared `dl_count`. Alias search uses `inode->i_lock` and each dentry's `d_lock`. Inode deletion state is checked under `OCFS2_I(inode)->ip_lock`. Dentry-lock release delegates to `ocfs2_simple_drop_lockres()` and `ocfs2_lock_res_free()`.

## Cross-File Interactions
This file depends on OCFS2 inode state from `inode.h`, lock resource helpers from `dlmglue.h`, allocation and file headers for filesystem context, and VFS dentry operations. Rename code calls `ocfs2_dentry_move()`, lookup/create paths call `ocfs2_dentry_attach_lock()`, and remote downconvert/delete logic relies on these lock resources to unhash aliases.

## Risks
`d_fsdata` is overloaded: negative dentries store a generation value, while positive dentries store an `ocfs2_dentry_lock *`. Converting a negative dentry to positive must clear the generation before lock attachment. Races with pruning and concurrent attachment are guarded by `dentry_attach_lock`, and mistakes can leak inode references or create duplicate lock resources. Missing dentry locks on live hashed positive dentries are logged as errors because they undermine clustered coherency.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dcache.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dcache.h

## Summary
Declares the OCFS2 dentry cache and dentry-lock interface used by lookup, rename, and dentry operation code. It defines the per-dentry-lock wrapper that ties VFS dentries to OCFS2 lock resources.

## Main Responsibilities
- Define `struct ocfs2_dentry_lock`, including reference count, parent block number, pinned inode, and lock resource.
- Expose OCFS2 dentry operations through `ocfs2_dentry_ops`.
- Declare helpers for attaching, finding, moving, and releasing dentry locks.
- Expose the global `dentry_attach_lock` for code that must synchronize dentry lock attachment.
- Declare generation attachment for negative dentries.

## Key Interfaces
- `ocfs2_dentry_attach_lock()` attaches a positive dentry to a lock resource.
- `ocfs2_dentry_lock_put()` releases one dentry's reference to a shared lock.
- `ocfs2_find_local_alias()` finds a local alias with the same parent directory block.
- `ocfs2_dentry_move()` performs a d_move while preserving OCFS2 dentry lock invariants.
- `ocfs2_dentry_attach_gen()` stores a parent generation on a negative dentry.

## Important Behavior
The dentry lock keeps an inode reference until its lock resource is destroyed. This ensures the inode remains valid for the lifetime of the lock resource, even though the usual final release path is through `->d_iput()`.

## State and Synchronization
`dl_count` tracks how many local dentries share the lock. `dl_parent_blkno` is part of the cluster lock identity. `dentry_attach_lock` serializes attaching and detaching these structures from dentries.

## Cross-File Interactions
`dcache.c` implements these declarations. Directory lookup and namei paths call into them after resolving or creating dentries. Lock helpers in `dlmglue.c` initialize, acquire, downconvert, and free the embedded `ocfs2_lock_res`.

## Risks
Callers must distinguish negative-dentry generation data from positive-dentry lock pointers in `d_fsdata`. They must also hold the directory locking required by `ocfs2_dentry_attach_lock()` so parent-block based lock naming remains valid while names are being resolved or moved.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dir.c

## Summary
Implements OCFS2 directory storage, lookup, mutation, iteration, indexed-directory support, inline-directory expansion, directory block trailers/checksums, free-space accounting, directory initialization, and directory index truncation. It handles three directory forms: inline data in the dinode, extent-backed unindexed directory blocks, and extent-backed indexed directories with a dx root and dx leaves.

## Main Responsibilities
- Validate and read directory blocks, directory trailers, dx roots, and dx leaves.
- Hash names for indexed directories using TEA-derived hashing and the filesystem dx seed.
- Lookup names in inline, unindexed extent-backed, and indexed directories.
- Add, update, and delete directory entries while journaling the correct dinode/data/index buffers.
- Maintain indexed directory entries, dx leaf blocks, root/leaf transitions, and free-space lists.
- Iterate directories for `readdir()` and internal scans.
- Check whether directories are empty for `rmdir`.
- Fill new directories with `"."` and `".."` in inline, extent, or indexed form.
- Expand inline directories into extent-backed directories and optionally attach indexes.
- Extend directory size and allocate new data/index clusters.
- Remove/truncate directory index metadata.

## Key Interfaces
- `ocfs2_find_entry()` returns a filled `ocfs2_dir_lookup_result` for name operations.
- `ocfs2_delete_entry()` removes a previously found dirent and corresponding dx entry if indexed.
- `__ocfs2_add_entry()` inserts a prepared dirent and updates dx metadata/free-list accounting.
- `ocfs2_update_entry()` changes the inode/type in an existing dirent.
- `ocfs2_prepare_dir_for_insert()` finds or creates space for a new name.
- `ocfs2_find_files_on_disk()` and `ocfs2_lookup_ino_from_name()` map names to inode block numbers.
- `ocfs2_readdir()` and `ocfs2_dir_foreach()` implement public and internal directory iteration.
- `ocfs2_fill_new_dir()` initializes a newly created directory.
- `ocfs2_dx_dir_truncate()` frees indexed-directory metadata.

## Important Behavior
Directory trailers are used when metadata ECC is enabled or directories are indexed. The trailer stores signature, parent dinode block, block number, free record length, and free-list linkage. Reads validate ECC first, then validate trailer identity when the directory format requires it. New blocks initialize trailers before being exposed to lookup or free-list code.

Lookup dispatches by directory type. Inline directories search the dinode inline-data area. Unindexed extent directories scan blocks with small readahead and remember `ip_dir_start_lookup` for the next search. Indexed directories read `i_dx_root`, hash the target name, locate the dx leaf through the dx root extent list, scan matching dx entries, and then search the referenced unindexed dirent block to confirm the actual name.

Deletion in indexed directories is a two-part operation. It journals the dx root and possibly dx leaf, deletes the unindexed dirent by merging/freeing records, recomputes the data block's largest free record, links the block into the indexed free list if it was not already there, decrements `dr_num_entries`, and removes the dx entry from its entry list.

Insertion is deliberately split. `ocfs2_prepare_dir_for_insert()` hashes the name when indexing is possible, ensures there is index capacity, finds a data block through the indexed free list or unindexed scan, and extends/expands the directory if needed. `__ocfs2_add_entry()` then journals the relevant buffers, splits an existing record if necessary, writes the new dirent, updates timestamps/version, inserts dx metadata, and recalculates free-list state.

Inline directory expansion is heavily ordered. The code allocates data and optional index storage, copies inline dirents into the first data block, expands the last record to the block/trailer boundary, initializes trailers, converts the dinode from inline data to an extent list, inserts the first data extent, attaches a dx root when supported, indexes existing records, and only then returns buffers for the pending insertion.

Indexed directories start with inline dx entries in the dx root when small. When the root fills, `ocfs2_expand_inline_dx_root()` allocates a leaf cluster, formats leaves, redistributes root entries by minor hash, clears the inline flag, and inserts the new dx extent. When a dx leaf fills, `ocfs2_dx_dir_rebalance()` sorts entries, chooses a split major hash, allocates a new cluster, inserts it in the dx extent tree, and transfers entries whose major hash belongs to the new range.

`readdir()` takes an inode lock with atime handling, may downgrade from EX to PR to reduce contention, then iterates only enough entries for one userspace call. Iterators use inode version checks to resynchronize offsets if the directory changed between calls.

## State and Synchronization
Directory metadata changes occur inside OCFS2 journal transactions. Allocation paths use `ip_alloc_sem`, quota reservations, allocation contexts, and extent-tree helpers. Inode dynamic features are changed under `ip_lock`. Readdir and name operations assume callers hold appropriate VFS inode semaphores and OCFS2 cluster locks; `ocfs2_readdir()` takes the inode lock itself.

## Cross-File Interactions
This file is central to OCFS2 namei and directory operations. It uses allocation/suballocation, extent maps and extent trees, journaling, block checksum validation, inode locking/state, quota accounting, truncate/deallocation, system file inode access, and dentry/namei code. The public structures and prototypes are in `dir.h`.

## Risks
Directory correctness depends on keeping unindexed dirent blocks and dx index entries in sync. Failures after one side is journaled can corrupt lookup unless transaction ordering is preserved. Trailer and free-list accounting must accurately reflect the largest free record or indexed insertion can miss available space or overwrite trailers. Hash split corner cases with identical major hashes can return `-ENOSPC` even during rebalance. Inline-to-extent conversion is particularly sensitive because it changes on-disk format, size, extents, optional index metadata, quota state, and returned insertion context in one operation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dir.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dir.h

## Summary
Declares the OCFS2 directory manipulation interface and lookup-result structures used by namei, readdir, and directory maintenance code. It abstracts inline, unindexed, and indexed directory details behind one lookup-result container.

## Main Responsibilities
- Define `struct ocfs2_dx_hinfo` for indexed-directory major/minor hash results.
- Define `struct ocfs2_dir_lookup_result`, which carries data-block, dx-root, dx-leaf, dx-entry, hash, and free-list predecessor context.
- Declare lookup, add, delete, update, existence-check, emptiness-check, readdir, initialization, insert-preparation, index truncation, and trailer helper functions.
- Provide `ocfs2_add_entry()` as a dentry-oriented wrapper around `__ocfs2_add_entry()`.

## Key Interfaces
- `ocfs2_find_entry()` fills an `ocfs2_dir_lookup_result`.
- `ocfs2_free_dir_lookup_result()` releases all buffer heads carried by a lookup result.
- `ocfs2_delete_entry()` and `ocfs2_update_entry()` mutate a previously found entry.
- `ocfs2_add_entry()` and `__ocfs2_add_entry()` insert new entries after preparation.
- `ocfs2_prepare_dir_for_insert()` performs space and index preparation before insertion.
- `ocfs2_fill_new_dir()` initializes `"."` and `".."` for new directories.
- `ocfs2_dx_dir_truncate()` removes indexed-directory metadata.
- `ocfs2_dir_trailer_from_size()` locates a directory trailer at the end of an arbitrary block-sized buffer.

## Important Behavior
`ocfs2_dir_lookup_result` can represent multiple layouts. For unindexed directories, `dl_leaf_bh` and `dl_entry` are sufficient. For indexed directories, the caller may also receive `dl_dx_root_bh`, `dl_dx_leaf_bh`, `dl_dx_entry`, `dl_hinfo`, and `dl_prev_leaf_bh` for free-list updates.

## State and Synchronization
The header does not enforce locking but the implementation expects callers of mutating functions to hold VFS directory serialization, OCFS2 cluster locks, and active journal handles as appropriate.

## Cross-File Interactions
`dir.c` implements the functions. Namei and inode code use the interface for create, lookup, link, unlink, rename, rmdir, orphan operations, and directory truncation. The definitions depend on OCFS2 on-disk directory, dx, and allocation structures from the broader filesystem headers.

## Risks
Callers must always release lookup results with `ocfs2_free_dir_lookup_result()` to avoid buffer-head leaks. Mutating helpers rely on the lookup result still matching the prepared directory state; using stale results after dropping locks or after unrelated directory mutation can corrupt data or index state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/Makefile

## Summary
Builds the OCFS2 in-kernel DLM object when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Main Responsibilities
- Add `ocfs2_dlm.o` to the build for the O2CB-backed OCFS2 filesystem configuration.
- Define the composite object members that are linked into `ocfs2_dlm.o`.

## Key Interfaces
- `obj-$(CONFIG_OCFS2_FS_O2CB) += ocfs2_dlm.o` gates the module/object on the O2CB OCFS2 configuration.
- `ocfs2_dlm-objs` lists `dlmdomain.o`, `dlmdebug.o`, `dlmthread.o`, `dlmrecovery.o`, `dlmmaster.o`, `dlmast.o`, `dlmconvert.o`, `dlmlock.o`, and `dlmunlock.o`.

## Important Behavior
The DLM is compiled as one composite object from domain management, debug support, worker/recovery threads, mastership, AST/BAST delivery, conversion, lock, and unlock implementation files.

## State and Synchronization
The Makefile has no runtime state. Its ordering only expresses build composition, not initialization order.

## Cross-File Interactions
The listed objects implement the interfaces declared in `dlmapi.h` and `dlmcommon.h`. `dlmast.c` is one member of this composite object.

## Risks
Configuration gating is important: without `CONFIG_OCFS2_FS_O2CB`, the in-kernel O2CB DLM object is not built. Adding DLM source files requires updating this object list or the code will not be linked.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmapi.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmapi.h

## Summary
Defines the external OCFS2 DLM API used by filesystem locking code and related clients. It contains DLM status values, lock status blocks, supported lock modes and flags, callback types, lock/unlock entry points, domain registration, lock printing, and eviction callback registration.

## Main Responsibilities
- Define `enum dlm_status` and declare `dlm_errname()` for readable status reporting.
- Provide `dlm_error()` logging wrapper for noteworthy DLM status failures.
- Define lock status block flags and `struct dlm_lockstatus`.
- Define DLM lock modes, including OCFS2-supported NL, PR, and EX modes.
- Define public and internal lock/unlock flags.
- Define AST, BAST, and unlock-AST callback function types.
- Declare `dlmlock()` and `dlmunlock()`.
- Declare domain registration/unregistration and protocol-version negotiation input.
- Define DLM eviction callback registration helpers.

## Key Interfaces
- `dlmlock()` requests or converts a lock with callbacks and caller data.
- `dlmunlock()` unlocks/cancels/deallocates a lock and optionally runs an unlock AST.
- `dlm_register_domain()` joins or creates a DLM domain using a domain name, key, and filesystem locking protocol version.
- `dlm_unregister_domain()` leaves/releases a DLM domain.
- `dlm_setup_eviction_cb()`, `dlm_register_eviction_cb()`, and `dlm_unregister_eviction_cb()` manage callbacks for node eviction events.

## Important Behavior
The status enum includes both traditional DLM results and OCFS2 extensions such as `DLM_RECOVERING` and `DLM_MIGRATING`, allowing callers to treat lock-resource recovery or migration as special retry/fail cases. `DLM_MAXSTATS` is the upper validation bound.

Only selected lock modes are supported by OCFS2 in practice: null, protected-read, and exclusive. Several flags are marked unsupported, while internal extension flags (`LKM_MIGRATION`, `LKM_PUT_LVB`, `LKM_GET_LVB`, `LKM_RECOVERY`) are reserved for DLM internals.

The lock status block is intentionally limited for callers: comments say callers are only allowed to access `status` and `lvb`, although the struct also carries flags and the internal lock id.

## State and Synchronization
This header defines callback-driven asynchronous completion rather than state itself. Callers supply AST/BAST functions that the DLM may invoke while holding spinlocks, as documented in `dlmcommon.h` for the lock structure.

## Cross-File Interactions
The implementation is spread across the DLM object members in the Makefile. `dlmcommon.h` includes and extends this API with internal state, wire messages, and helper prototypes. OCFS2 `dlmglue` and filesystem lock code use these declarations.

## Risks
Status and flag values form ABI-like contracts between DLM components and network peers. Changing the enum requires synchronizing debug/status-name code, as noted in the file. Callers must not use unsupported flags or modes unless the internal DLM path explicitly owns them. LVB get/put flags are subtle because stale value-block propagation can corrupt lock metadata semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmast.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmast.c

## Summary
Implements OCFS2 DLM AST and BAST queueing and delivery for local and remote locks. It updates lock value blocks, queues AST/BAST callbacks, cancels obsolete BASTs, handles incoming proxy AST messages, and sends proxy AST/BAST messages over the O2CB TCP transport.

## Main Responsibilities
- Queue ASTs and BASTs on `dlm->pending_asts` and `dlm->pending_basts`.
- Cancel pending BASTs that are made obsolete by a newly granted lock level.
- Update or fetch lock value blocks when ASTs are delivered.
- Invoke local AST and BAST callbacks.
- Convert remote AST/BAST delivery into `DLM_PROXY_AST_MSG` messages.
- Handle incoming proxy AST/BAST messages from remote masters.
- Move locks to granted state and update lock modes/status on remote AST receipt.

## Key Interfaces
- `__dlm_queue_ast()` and `dlm_queue_ast()` add locks to the pending AST list.
- `__dlm_queue_bast()` adds locks to the pending BAST list.
- `dlm_do_local_ast()` and `dlm_do_local_bast()` invoke local callbacks.
- `dlm_do_remote_ast()` sends a proxy AST to the lock's owning node.
- `dlm_proxy_ast_handler()` processes incoming DLM proxy AST network messages.
- `dlm_send_proxy_ast_msg()` sends proxy AST/BAST messages; `dlmcommon.h` wraps it as `dlm_send_proxy_ast()` and `dlm_send_proxy_bast()`.

## Important Behavior
BAST cancellation prevents stale blocking notifications. If an AST grants a lock down to NL, or grants PR when the highest blocked mode is not EX, a queued BAST no longer describes a real blocking condition and is removed. The code also releases the reserved AST accounting for the canceled BAST.

`dlm_update_lvb()` only updates value blocks when this node masters the lock resource. GET requests copy the lock resource LVB into the lock status block before AST callback. PUT requests are deliberately not applied here; comments state they should happen at downconvert time to avoid racing GETs and PUTs.

Incoming proxy AST handling validates domain liveness, lock name length, LVB flag combinations, AST type, lock-resource existence, and recovery/migration state. For ASTs, it searches converting first, then blocked; for BASTs, it searches converting first, then granted. A matching AST moves the lock to the granted list, applies `convert_type` to `type`, clears conversion state, sets lksb status to `DLM_NORMAL`, copies LVB data when requested, then invokes the local AST.

Unknown locks in a proxy AST are usually treated as `DLM_NORMAL` rather than fatal after logging, while recovery or migration states return `DLM_RECOVERING` or `DLM_MIGRATING`. Sending code treats those two statuses as impossible for a successful AST target and calls `BUG()`.

## State and Synchronization
AST/BAST queues are protected by `dlm->ast_lock`; individual pending bits and list links are updated under each lock's `spinlock`. Lock-resource list searches and state checks use `res->spinlock`. Lock references are taken when adding to pending lists and released if list insertion is canceled. Domain references are acquired with `dlm_grab()` while handling network messages.

## Cross-File Interactions
This file uses `o2net_send_message_vec()` from the cluster TCP layer and the DLM wire structures from `dlmcommon.h`. The DLM thread consumes pending AST/BAST lists. Lock, convert, unlock, recovery, and migration code set lock states that determine whether these callbacks are queued or accepted.

## Risks
The AST/BAST paths run at the boundary between distributed state changes and local callbacks. List placement, pending bits, and lock references must stay consistent or callbacks can be lost, duplicated, or use freed locks. LVB propagation has explicit ordering constraints. Remote AST handling trusts wire fields after validation, so name length, type, and flag checks are important. The use of `BUG()` for unexpected recovery/migration replies makes protocol-state mismatches fatal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmcommon.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmcommon.h

## Summary
Defines the internal OCFS2 DLM data model, wire message formats, state flags, helper macros, inline functions, and cross-file prototypes. It is the common contract among DLM domain management, mastership, locking, conversion, unlock, AST delivery, recovery, migration, debug, and network handler files.

## Main Responsibilities
- Define lock-name limits, hash sizing, hash helpers, and owner constants.
- Define master-list entry types and `struct dlm_master_list_entry`.
- Define AST types and valid lock flags.
- Define DLM context, recovery context, work item, lock resource, migratable lock, and lock structures.
- Define lock-resource state flags and recovery state flags.
- Define all DLM network message numbers and wire packet layouts.
- Define migratable lock-resource sizing to fit O2NET one-page payloads.
- Declare internal DLM helper and network-handler functions implemented across DLM source files.
- Provide inline helpers for lock compatibility, lock-resource state mapping, node iteration, cookie decoding, and ownership updates.

## Key Interfaces
- Core state structures: `dlm_ctxt`, `dlm_lock_resource`, `dlm_lock`, `dlm_recovery_ctxt`, and `dlm_master_list_entry`.
- Wire structs: create/convert/unlock/proxy AST, master/assert/migrate/requery, join/cancel/exit, recovery, region/nodeinfo, deref, and migratable lock-resource packets.
- Handler prototypes: `dlm_create_lock_handler()`, `dlm_convert_lock_handler()`, `dlm_proxy_ast_handler()`, `dlm_unlock_lock_handler()`, mastership handlers, migration handlers, recovery handlers, and domain join/exit handlers.
- Lock-resource helpers: lookup, allocation, reference, hash insertion/removal, dirtying, purge, migration, refmap, and inflight refs.
- AST helpers: queue, local delivery, remote delivery, and proxy send wrappers.

## Important Behavior
`dlm_ctxt` is the DLM domain object. It owns lock-resource and master hash tables, dirty/purge/pending AST lists, live/domain/recovery bitmaps, recovery context, debugfs root, domain reference/state fields, worker and recovery threads, workqueue/list state, eviction callbacks, and filesystem/DLM protocol versions.

`dlm_lock_resource` is the master object for one lock name. It carries granted, converting, and blocked lists in a fixed order, purge/dirty/recovering/tracking links, owner, state flags, LVB, inflight counts, AST reservation count, waitqueue, and node refmap. Comments warn that field layout changes must respect initialization code in other files.

`dlm_lock` stores the migratable wire lock state plus local list links, AST/BAST list links, resource pointer, spinlock, reference count, callback pointers, callback data, lock status block, and pending flags for AST, BAST, convert, lock, cancel, unlock, and kernel-allocated LKSB.

Message payload sizing is tied to the transport: `DLM_MAX_MIGRATABLE_LOCKS` is chosen so one `dlm_migratable_lockres` plus 240 locks plus reserved padding fits within `O2NET_MAX_PAYLOAD_BYTES`. This is central to efficient recovery/migration of lock resources.

Lock compatibility is intentionally simple: NL is compatible with all, EX conflicts with every non-NL lock, and PR is compatible only with PR or NL. `__dlm_lockres_state_to_status()` maps recovery/migration/in-progress flags to retry statuses while holding `res->spinlock`.

## State and Synchronization
The structures embed the synchronization used throughout the DLM: domain `spinlock`, `ast_lock`, `track_lock`, `master_lock`, work locks, lock-resource `spinlock`, waitqueues for join/thread/recovery/AST/migration/resource waits, krefs for domains, locks, lock resources, and MLEs, atomic counters for statistics and AST reservations, and bitmaps for node membership and responses.

## Cross-File Interactions
Every DLM implementation file depends on this header. `dlmast.c` uses AST types, proxy AST wire structures, lock-resource/lock fields, and send wrapper declarations. `tcp.h` supplies `O2NET_MAX_PAYLOAD_BYTES` and `struct o2net_msg` used by network handlers. `dlmapi.h` supplies public status, modes, flags, LVB size, callback types, and lock status blocks.

## Risks
This header is a dense internal ABI. Wire structure layout, message ids, lock mode/status values, and migratable payload sizing must remain consistent across all nodes in a cluster. Many inline helpers assume callers hold specific spinlocks. The same structures participate in normal locking, migration, recovery, purge, AST delivery, and network handler paths; incorrect state flag transitions can make callers return `DLM_FORWARD`, `DLM_RECOVERING`, or `DLM_MIGRATING` at the wrong time. Changing payload sizes without considering `O2NET_MAX_PAYLOAD_BYTES` can break recovery message framing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmcommon.h -->