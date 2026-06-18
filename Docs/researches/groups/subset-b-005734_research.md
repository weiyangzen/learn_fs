# subset-b-005734 Research

Grouped research report for the requested OCFS2 cluster transport, dcache, directory, and DLM subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.c

## Purpose

`tcp.c` implements the OCFS2 O2CB cluster network transport (`o2net`) over kernel TCP sockets. It provides synchronous message send APIs for higher layers such as DLM, handler registration for inbound message types keyed by domain key, connection establishment/teardown tied to heartbeat state, protocol handshaking, keepalive/idle timeout handling, and quorum notification when a peer becomes unreachable or suspicious.

The file deliberately presents a simple blocking RPC-like contract to callers: send a message to a target node, wait for a status response from the remote handler, and translate network/system failure into Linux errno values. Internally, it is event-driven through socket callbacks, an ordered workqueue, per-node status waiters, and per-socket framing state.

## Important APIs, Types, and Functions

Exported APIs are `o2net_send_message()`, `o2net_send_message_vec()`, `o2net_register_handler()`, `o2net_unregister_handler_list()`, `o2net_fill_node_map()`, `o2net_register_hb_callbacks()`, `o2net_unregister_hb_callbacks()`, `o2net_start_listening()`, `o2net_stop_listening()`, `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()`.

Global state includes the handler red-black tree protected by `o2net_handler_lock`, `o2net_nodes[O2NM_MAX_NODES]`, the listening socket, ordered workqueue `o2net_wq`, heartbeat callbacks, static handshake and keepalive message buffers, and the connected peer count. Per-node runtime state is manipulated through `o2net_set_nn_state()`, which owns the connection pointer, validity bit, persistent transmit error, status waiter completion, reconnect scheduling, and quorum notifications.

Message waiting is built around `struct o2net_status_wait`. `o2net_prep_nsw()` allocates a per-node ID with `idr_alloc()`, links it onto `nn_status_list`, and gives the outgoing `msg_num` its waiter. `o2net_complete_nsw()` and `o2net_complete_nodes_nsw()` wake waiters for status responses or node shutdown.

Connection state is represented by `struct o2net_sock_container`. `sc_alloc()`, `sc_get()`, `sc_put()`, and `sc_kref_release()` manage the socket, node dependency, receive page, work items, idle timer, keepalive work, debugfs hooks, and refcounted lifetime. Socket callbacks are installed and removed by `o2net_register_callbacks()` and `o2net_unregister_callbacks()`.

## Control Flow

Initialization starts in `o2net_init()`: quorum/debugfs are initialized, one zeroed folio is carved into `o2net_hand`, `o2net_keep_req`, and `o2net_keep_resp`, protocol magic fields are filled, and every `o2net_node` is initialized with locks, wait queues, status IDR/list, delayed work, and initial `-ENOTCONN` persistent error.

Listening is started by node manager via `o2net_start_listening()`, which allocates the ordered `o2net` workqueue, opens a listening socket with `o2net_open_listening_sock()`, replaces the listen socket data-ready callback, and reports the local connection up to quorum. Accepted connections are drained by `o2net_accept_many()`. `o2net_accept_one()` validates remote IP, enforces the node-number direction rule, requires heartbeat to already be visible, rejects duplicate connections, allocates an `sc`, attaches it to the node, registers callbacks, queues receive work, and sends the local handshake.

Outbound connection attempts are driven by heartbeat and loss events through `o2net_start_connect()`. Only the higher-numbered node initiates. The worker gets local and remote node config, avoids attempts when an existing socket or non-retryable persistent error exists, creates/binds a TCP socket, sets no-delay and TCP user timeout, registers callbacks, attaches the `sc`, and issues a nonblocking connect. Completion of either an accepted or connected socket queues `o2net_sc_connect_completed()`, which sends the current handshake.

Receive framing is handled by `o2net_rx_until_empty()` and `o2net_advance_rx()`. The receive page first accumulates `struct o2net_handshake`; `o2net_check_handshake()` validates protocol version, idle timeout, keepalive delay, and heartbeat timeout, then marks the socket valid and starts idle/keepalive. After handshake, the same page accumulates an `o2net_msg` header and payload. Oversized payloads, bad magic, EOF, and protocol failures close the connection.

Sending flows through `o2net_send_message_vec()`. It validates payload size and target, waits for `o2net_tx_can_proceed()` to yield either a valid socket or persistent error, allocates a header and combined kvec array, prepares an `o2net_status_wait`, sets `msg_num`, serializes the send under `sc_send_lock`, then blocks until the waiter completes. Remote handler status is delivered by `O2NET_MSG_STATUS_MAGIC`; transport/system errors use `O2NET_ERR_*` translation and do not overwrite caller status.

Inbound messages are processed by `o2net_process_message()`. Status frames wake local waiters, keepalive requests send keepalive responses, keepalive responses only refresh idle state, and normal messages look up a registered handler by type/key. Payload length is checked against the handler's `nh_max_len`; the handler is called with the receive buffer; a status frame is sent back; and optional post-handler callbacks run after the response.

## State and Persistence Behavior

There is no disk persistence in this file. Long-lived kernel state consists of per-node connection state, status waiter IDRs, delayed reconnect/expiry/quorum work, the handler tree, and the shared static protocol buffers. Runtime status is intentionally reset by heartbeat transitions: node down forces `-ENOTCONN`, cancels reconnect and quorum work, completes pending status waiters, and prevents reconnect until heartbeat returns.

Connection validity is separated from socket existence. A socket may be present while handshaking (`nn_sc` set, `nn_sc_valid` false), and transmitters only proceed when valid or when a persistent error wakes them. Idle timeout does not immediately close the socket; it marks `nn_timeout`, reports a quorum connection error, queues delayed still-up handling, and resets the timer. Any later received data clears the timeout/quorum suspicion in `o2net_sc_postpone_idle()`.

## Dependencies and Integration Points

`tcp.c` depends on Linux kernel sockets, TCP helpers, workqueues, timers, krefs, IDR, wait queues, spin/rw locks, folios/pages, NOFS allocation guards, tracepoints, debugfs hooks, and optional stats. OCFS2-specific integration is with heartbeat (`o2hb_*`), node manager (`o2nm_*`), quorum (`o2quo_*`), masklog, and the public/private transport headers.

The most important consumer is OCFS2 DLM, whose message handlers register with `o2net_register_handler()` and whose remote operations rely on the synchronous status response. Node manager owns listening lifecycle, while heartbeat callbacks drive connect/disconnect policy.

## Risks and Edge Cases

Ordering and lifetime are the main risks. Socket callbacks queue work while teardown unregisters callbacks and flushes work; missed refs or callback races can become use-after-free. `o2net_set_nn_state()` has many side effects and must be called under `nn_lock`; incorrect callers can desynchronize connected peer counts, waiter completion, reconnect work, and quorum state.

Handshake mismatches are treated as persistent enough to stop reconnect for that peer, because mismatched protocol/timeouts can corrupt cluster assumptions. Payload max-length protection is per-handler; handler registration mistakes can reject valid traffic or allow oversized handler input. `o2net_sendpage()` loops on `-EAGAIN` with `cond_resched()` and shuts down on other short sends, so TCP behavior under memory pressure or partial sends is important.

Node-number direction is integral: higher-numbered nodes connect, lower-numbered nodes accept. Split-brain or duplicate socket attempts are rejected, but testing must cover races where heartbeat visibility and inbound connect ordering differ across nodes.

## Test Signals

Useful signals include multi-node O2CB mount/unmount, heartbeat up/down cycles, higher-to-lower connection establishment, accept rejection from unknown IPs or wrong node-number direction, duplicate connection attempts, protocol version/timeout mismatch logs, keepalive timeout and recovery, DLM message round trips, pending sender wakeup on disconnect, and clean `o2net_stop_listening()` teardown under traffic.

Fault injection should cover allocation failures in `sc_alloc()` and send path, `idr_alloc()` failure, partial/short sends, EOF while receiving header/payload, payload overflow, missing handler, handler status propagation, and delayed reconnect expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.h

## Purpose

`tcp.h` is the public O2CB network transport interface used by OCFS2 cluster components. It defines the wire header `struct o2net_msg`, payload limits, default timing constants, link-down classification, exported send/handler APIs, connection lifecycle hooks, heartbeat callback registration, module init/exit hooks, and optional debugfs tracking hooks.

## Important APIs, Types, and Functions

`struct o2net_msg` is the fixed header on the wire. It carries a magic value, payload length, message type, system status, handler/user status, domain key, message number, and flexible payload buffer. `O2NET_MAX_PAYLOAD_BYTES` caps payloads to one page minus the header, and DLM message structures size themselves against that limit.

`o2net_msg_handler_func` is the inbound handler signature: it receives a full message buffer, total length, registered private data, and optional post-handler return data. `o2net_post_msg_handler_func` runs after the status response is sent.

The main caller APIs are `o2net_send_message()` for a single contiguous payload and `o2net_send_message_vec()` for kvec payloads. Handler lifecycle uses `o2net_register_handler()` and `o2net_unregister_handler_list()`, where an unregister list lets a subsystem remove all handlers it registered for a domain. `o2net_fill_node_map()` reports currently connected peers.

Cluster lifecycle APIs are `o2net_register_hb_callbacks()`, `o2net_unregister_hb_callbacks()`, `o2net_start_listening()`, `o2net_stop_listening()`, `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()`.

`o2net_link_down()` is an inline classifier used by DLM and transport users to treat socket state or errors such as `-ECONNREFUSED`, `-ENOTCONN`, `-ECONNRESET`, and `-EPIPE` as link-down conditions.

## Control Flow

Callers register message handlers before sending or accepting domain traffic. A sender calls `o2net_send_message*()`, which constructs an `o2net_msg`, waits for a valid node connection, sends header plus payload, and waits for a status frame keyed by `msg_num`. The remote transport dispatches the registered handler based on `msg_type` and `key`, then sends a status frame using the same header identity.

Node manager calls the listening APIs as the local cluster node is configured or torn down. Heartbeat callback registration wires `tcp.c` into heartbeat up/down events so peer sockets are established and destroyed as nodes join or leave.

## State and Persistence Behavior

The header itself stores no state. It defines the wire-visible state contract: magic values are private to `tcp_internal.h`, but this header fixes the public header layout, status fields, payload size, and timing defaults. Runtime state lives in `tcp.c`.

## Dependencies and Integration Points

The header bridges Linux socket/kvec types with OCFS2 cluster code. It is included by DLM files such as `dlmast.c` and by node/heartbeat/lifecycle code. It conditionally exposes debugfs hooks when `CONFIG_DEBUG_FS` is enabled and compiles them into empty inline stubs otherwise.

## Risks and Edge Cases

`struct o2net_msg` is a wire ABI. Field size/order changes would break inter-node compatibility. `O2NET_MAX_PAYLOAD_BYTES` is a hard constraint for all cluster messages; any DLM structure that grows past it will fail registration or send validation. `o2net_link_down()` mixes socket state and errno classification; adding or removing errors changes DLM failure semantics.

## Test Signals

Build coverage should include both `CONFIG_DEBUG_FS=y` and `n`. Runtime signals include successful handler registration/unregistration, oversized handler registration rejection, oversized send rejection, correct status propagation, DLM behavior after link-down errors, and node map consistency with active cluster peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp_internal.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp_internal.h

## Purpose

`tcp_internal.h` is the private implementation header for `tcp.c`. It defines transport magic values, the O2NET protocol version, handshake layout, per-node connection state, per-socket receive/send state, registered handler records, system error values, send waiters, and optional debugfs send tracking.

## Important APIs, Types, and Functions

Magic constants identify normal messages, status responses, keepalive requests, and keepalive responses. `O2NET_QUORUM_DELAY_MS` delays quorum decisions until heartbeat has had time to declare truly dead nodes. `O2NET_PROTOCOL_VERSION` is currently `11` and documents historical protocol/locking semantic changes.

`struct o2net_handshake` is exchanged before a connection becomes valid. It contains protocol version, connector ID, heartbeat timeout, idle timeout, keepalive delay, and reconnect delay. The timeout fields intentionally force cluster-wide timing agreement.

`struct o2net_node` holds per-peer mutable state: `nn_lock`, current socket container, valid bit, persistent error, idle-timeout flag, transmit wait queue, status waiter IDR/list, delayed connect work, connect expiry work, and delayed still-up quorum work.

`struct o2net_sock_container` owns a refcounted socket, peer node pointer, receive/connect/shutdown work, idle timer, keepalive delayed work, handshake state, receive page and offset, original socket callbacks, current message identity for stats/debug, optional debugfs timestamps, optional stats counters, and `sc_send_lock`.

`struct o2net_msg_handler` stores one registered handler in the transport rb-tree. `struct o2net_status_wait` is a pending synchronous send completion. `struct o2net_send_tracking` is either detailed debugfs state or a dummy structure depending on configuration.

## Control Flow

The types in this header encode the control flow of `tcp.c`: peer heartbeats manipulate `o2net_node`; socket callbacks queue work on `o2net_sock_container`; inbound normal messages look up `o2net_msg_handler`; outbound calls wait on `o2net_status_wait`; and debugfs/stat code samples `o2net_send_tracking` and `o2net_sock_container` timing fields.

Handshake is a gate between socket existence and transmit validity. `nn_sc` can point at an `sc` before `nn_sc_valid` is set, but transmitters only proceed after the remote handshake is checked and `o2net_set_nn_state()` marks the connection valid.

## State and Persistence Behavior

All state is in-memory cluster runtime state. The important durability property is not persistence but cluster consistency: mismatched protocol versions or timing values prevent a connection from being considered valid. Pending waiters are transient and are completed either by status response or forced death on shutdown.

## Dependencies and Integration Points

This header depends on `tcp.h` for the public message header and handler types, node manager for `O2NM_MAX_NODES`, heartbeat constants for quorum delay, Linux IDR/list/workqueue/timer/kref/socket types, and optional debugfs/stats configuration. DLM indirectly depends on many of these limits through `O2NET_MAX_PAYLOAD_BYTES` and protocol behavior.

## Risks and Edge Cases

Refcounted socket lifetime is subtle because every queued work item must hold an `sc` reference. `nn_status_idr` IDs become wire-visible `msg_num` values, so waiter removal must be synchronized with response processing and shutdown completion. The one-page receive buffer constrains payload size and makes handler lifetime rules strict: inbound payload memory is invalid after the handler returns.

Protocol-version comments note that O2NET version once represented both transport and filesystem locking semantics. Tests must ensure that filesystem/DLM protocol negotiation remains separate from the transport version after version 11.

## Test Signals

Review signals include structure-size/layout changes, additions to `enum o2net_system_error` without translation updates, work item additions without refcount rules, and handshake field changes without `tcp.c` validation. Runtime signals are handshake rejection on timing mismatch, pending waiter completion on disconnect, debugfs send/socket tracking under `CONFIG_DEBUG_FS`, and stats updates under `CONFIG_OCFS2_FS_STATS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dcache.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dcache.c

## Purpose

`dcache.c` implements OCFS2 dentry-cache validation and cluster dentry-lock attachment. It keeps VFS dentries coherent with remote unlink/rename activity by associating positive dentries with cluster lock resources scoped to a parent directory block number and inode. It also gives negative dentries a generation-based validity check tied to the parent directory lock generation.

## Important APIs, Types, and Functions

`ocfs2_dentry_attach_gen()` stores the parent directory lock generation in a negative dentry's `d_fsdata`. `ocfs2_dentry_revalidate()` is the VFS `d_revalidate` callback. It rejects RCU lookup, validates negative dentry generation, rejects deleted/bad/root/orphaned positive dentries, and forces relookup when a positive dentry lacks lock data.

`ocfs2_find_local_alias()` scans an inode's aliases for a dentry with usable `d_fsdata` and the requested parent block. It is used to share a single `struct ocfs2_dentry_lock` across multiple local aliases for links in the same directory.

`ocfs2_dentry_attach_lock()` attaches or reuses a cluster dentry lock for a positive dentry. It handles negative-to-positive conversion, alias reuse, fresh allocation, lock resource initialization, attachment under `dentry_attach_lock`, acquisition/release of the PRMODE dentry lock, and cleanup on failure.

`ocfs2_dentry_lock_put()` decrements the shared dentry-lock attach count and calls `ocfs2_drop_dentry_lock()` when the last local dentry releases it. `ocfs2_dentry_iput()` is the VFS `d_iput` callback and drops the dentry lock before `iput()`. `ocfs2_dentry_move()` updates lock association during cross-directory rename before calling `d_move()`.

## Control Flow

Lookup creates negative dentries with a generation snapshot or positive dentries that later call `ocfs2_dentry_attach_lock()` while the parent directory semaphore and parent cluster lock are held. For positive dentries, the function first reuses an alias lock if an inode already has a dentry under the same parent; otherwise it allocates `ocfs2_dentry_lock`, grabs the inode, stores the parent block, and initializes the lock resource.

The actual `dentry->d_fsdata` update is protected by the global `dentry_attach_lock` because final `dput()` may run asynchronously. After attachment, the code obtains and releases the dentry cluster lock to establish the local PRMODE hold. Remote unlink/rename can then trigger downconvert handling elsewhere, which will delete/unhash local dentries.

Revalidation is deliberately lightweight. Negative dentries are valid only if their stored generation equals the parent `ip_dir_lock_gen`. Positive dentries rely on inode flags/link count and the presence of dentry lock data; they do not take a cluster lock in the revalidate callback.

Rename uses `ocfs2_dentry_move()`. In same-directory renames, the lock identity is unchanged. In cross-directory renames, the old dentry lock is dropped, `d_fsdata` is cleared, a new lock is attached for the new parent block, and then `d_move()` updates the VFS dentry relationship.

## State and Persistence Behavior

State is in-memory only. `dentry->d_fsdata` is overloaded: negative dentries store a parent generation cast to pointer, while positive dentries store `struct ocfs2_dentry_lock *`. The `ocfs2_dentry_lock` holds an inode reference and an `ocfs2_lock_res` until the last local attached dentry releases it.

Persistent filesystem state is not directly modified here. The cluster-visible effect is lock ownership: a node that looked up a positive name holds a protected-read dentry lock until final dput, and unlink/rename upgrades to exclusive mode elsewhere to force other nodes to drop dentries.

## Dependencies and Integration Points

This file depends on VFS dentry operations, inode alias lists, OCFS2 inode/super structures, dlm glue for dentry locks, inode flags such as `OCFS2_INODE_DELETED`, and tracepoints. It integrates with lookup/namei paths, rename, final dput/iput, and remote dentry deletion/downconvert logic implemented outside this file.

## Risks and Edge Cases

The most important edge case is the `d_fsdata` type switch between negative generation and positive lock pointer. `ocfs2_dentry_attach_lock()` explicitly clears old negative data when converting to positive. Any path that interprets `d_fsdata` without knowing dentry polarity can corrupt state.

Alias reuse assumes that an alias found with a matching parent and lock data has a valid dentry-lock reference. Races with pruning are controlled by inode/dentry locks and `dentry_attach_lock`, but cross-directory rename and dput concurrency remain sensitive. On attach failure after allocating a new lock, manual cleanup is required because `d_instantiate()` may never occur.

Missing `d_fsdata` on a positive connected dentry is logged as an error in `ocfs2_dentry_iput()`, except for disconnected or unhashed dentries. That is a strong invariant signal for lookup/attach regressions.

## Test Signals

Test with clustered lookup/unlink/rename from multiple nodes, negative lookup then remote create, positive lookup then remote unlink, hard links in the same directory sharing lock state, cross-directory rename, dcache pruning under memory pressure, final dput after failed attach, and RCU lookup fallback returning `-ECHILD`. Tracepoints for revalidate, attach, alias finding, deletion, and orphaned inode paths are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dcache.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dcache.h

## Purpose

`dcache.h` declares OCFS2's dentry-cache interface and defines `struct ocfs2_dentry_lock`, the per-parent/per-inode lock object shared by local dentries. It is the small contract between lookup/namei/rename code and the dcache implementation in `dcache.c`.

## Important APIs, Types, and Functions

`struct ocfs2_dentry_lock` contains a local attach count, parent directory block number, pinned inode pointer, and `struct ocfs2_lock_res` used by DLM glue. The inode reference keeps the lock resource's inode context alive until the lock resource is destroyed.

Exports include `ocfs2_dentry_ops`, `ocfs2_dentry_attach_lock()`, `ocfs2_dentry_lock_put()`, `ocfs2_find_local_alias()`, `ocfs2_dentry_move()`, global `dentry_attach_lock`, and `ocfs2_dentry_attach_gen()`.

## Control Flow

Name lookup uses `ocfs2_dentry_attach_gen()` for negative dentries and `ocfs2_dentry_attach_lock()` for positive dentries. VFS uses `ocfs2_dentry_ops` to call revalidate and iput hooks. Rename calls `ocfs2_dentry_move()` to keep dentry lock identity synchronized with parent directory changes.

## State and Persistence Behavior

The header defines runtime-only dcache/lock state. `dl_count` is a local reference count for dentries sharing the same lock object. `dl_parent_blkno` is part of the lock name identity, and `dl_lockres` is the cluster lock resource that gives remote coherency semantics. There is no direct on-disk persistence.

## Dependencies and Integration Points

The type embeds `struct ocfs2_lock_res`, so users must include DLM glue definitions before use through normal OCFS2 headers. The declarations integrate with VFS dentry lifecycle, OCFS2 namei, inode lifetime, and cluster locking.

## Risks and Edge Cases

Callers must not treat `dentry->d_fsdata` as always being an `ocfs2_dentry_lock`; negative dentries store a generation value. `dentry_attach_lock` must protect attach/detach count and pointer updates against asynchronous dput. Mismanaging `dl_count` can leak an inode reference or drop an active lock resource.

## Test Signals

Build and runtime signals include correct VFS dentry operations installation, no missing-lock errors during iput, balanced lock put/drop under dcache shrinkers, alias reuse for hard links, and correct lock reattachment for cross-directory rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dir.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dir.c

## Purpose

`dir.c` implements OCFS2 directory lookup, insertion, deletion, update, readdir, emptiness checks, new-directory initialization, inline-to-extent expansion, indexed-directory creation/growth/rebalancing, directory block trailer handling, metadata validation, and indexed-directory truncation. It supports three directory storage modes: inline data inside the dinode, unindexed extent-backed directory blocks, and indexed directories with a dx root plus optional dx leaf clusters.

## Important APIs, Types, and Functions

Externally used functions are `ocfs2_free_dir_lookup_result()`, `ocfs2_find_entry()`, `ocfs2_delete_entry()`, `__ocfs2_add_entry()`/`ocfs2_add_entry()`, `ocfs2_update_entry()`, `ocfs2_check_dir_for_entry()`, `ocfs2_empty_dir()`, `ocfs2_find_files_on_disk()`, `ocfs2_lookup_ino_from_name()`, `ocfs2_readdir()`, `ocfs2_dir_foreach()`, `ocfs2_prepare_dir_for_insert()`, `ocfs2_fill_new_dir()`, `ocfs2_dx_dir_truncate()`, and `ocfs2_dir_trailer_from_size()`.

Lookup state is carried by `struct ocfs2_dir_lookup_result` from `dir.h`: unindexed dirent buffer, dx root, dx leaf, dx entry, name hash, and free-list predecessor. Directory indexing uses `struct ocfs2_dx_hinfo` for TEA-derived major/minor hash values.

Validation helpers include `ocfs2_check_dir_entry()`, `ocfs2_validate_dir_block()`, `ocfs2_check_dir_trailer()`, `ocfs2_validate_dx_root()`, and `ocfs2_validate_dx_leaf()`. Read helpers are split across inline (`ocfs2_find_entry_id()`), extent/unindexed (`ocfs2_find_entry_el()`), direct physical directory reads, dx root reads, and dx leaf reads.

Indexed-directory helpers include `ocfs2_dx_dir_name_hash()`, `ocfs2_dx_dir_lookup_rec()`, `ocfs2_dx_dir_lookup()`, `ocfs2_dx_dir_search()`, `ocfs2_dx_dir_insert()`, `ocfs2_delete_entry_dx()`, `ocfs2_prepare_dx_dir_for_insert()`, `ocfs2_expand_inline_dx_root()`, `ocfs2_dx_dir_rebalance()`, and `ocfs2_dx_dir_remove_index()`.

## Control Flow

Lookup starts at `ocfs2_find_entry()`. Indexed directories call `ocfs2_find_entry_dx()`, which reads the dinode, reads the dx root, hashes the name, finds the target inline entry list or dx leaf block, then verifies the candidate by reading the unindexed dirent block and scanning it. Unindexed inline directories scan dinode inline data. Unindexed extent-backed directories scan blocks with readahead, starting from `ip_dir_start_lookup` and wrapping once.

Insertion is two-phase. `ocfs2_prepare_dir_for_insert()` finds or creates sufficient space and fills `ocfs2_dir_lookup_result`; `__ocfs2_add_entry()` then journals the necessary buffers, inserts the dirent, and updates the dx index/free-list accounting if needed. Inline directories may expand to extent-backed form through `ocfs2_expand_inline_dir()`. Existing extent-backed directories grow through `ocfs2_extend_dir()`, which may allocate a cluster, initialize a new empty dir block and trailer, link it to the indexed free list, update `i_size`, and dirty the inode.

Indexed insertion first ensures room in the index. Inline dx roots can expand to external leaf clusters with `ocfs2_expand_inline_dx_root()`. External dx leaves may rebalance with `ocfs2_dx_dir_rebalance()`: sort a full leaf, choose a split hash, allocate and format a new leaf cluster, insert a new extent into the dx root tree, and transfer entries >= split hash into the new leaves. Separately, `ocfs2_search_dx_free_list()` finds unindexed dirent space via trailer free-list records, or `ocfs2_extend_dir()` creates a new data block.

Deletion uses `ocfs2_delete_entry()`. Unindexed modes call `__ocfs2_delete_entry()`, which merges the deleted record into the previous dirent or zeros its inode. Indexed deletion additionally journals dx root/leaf state, removes the unindexed dirent, recalculates trailer free space, adds the block to the dx free list if newly free, decrements `dr_num_entries`, and removes the dx entry from the list.

Readdir is implemented by `ocfs2_readdir()`, which obtains a directory cluster lock, downgrades from EX to PR when atime forced EX, and walks inline or extent blocks. It uses inode i_version snapshots to resynchronize offsets after mutations and intentionally reads the unindexed tree even for indexed directories. `ocfs2_empty_dir()` uses dx root entry count as a fast "seen other" check for indexed directories but still scans to verify `.` and `..`.

New directory creation uses `ocfs2_fill_new_dir()`. Inline mode writes `.` and `..` inside the dinode. Extent mode allocates the first directory block, fills initial dirents, optionally initializes a trailer, sets size/link count/blocks, and marks the inode dirty. Indexed mode first creates an unindexed directory block, then attaches an inline dx root and inserts index records for `.` and `..`.

## State and Persistence Behavior

This file performs persistent filesystem mutations through OCFS2 journaling. Directory data blocks, dinodes, dx root blocks, dx leaf blocks, extent trees, allocation bitmaps, quota accounting, inode i_size/i_blocks/link count, timestamps, i_version, dynamic feature flags (`OCFS2_INLINE_DATA_FL`, `OCFS2_INDEXED_DIR_FL`), dx free-list pointers, and metadata checksums/trailers can all be changed.

`ocfs2_dir_lookup_result` owns buffer references until `ocfs2_free_dir_lookup_result()` releases them. Lookup buffers are intentionally reused by add/delete/update so the caller can avoid repeated search and so indexed operations know the exact dx/free-list context to mutate.

Directory trailers persist per block when metaecc or indexed directories require them. They carry signature, parent dinode, block number, free record length, next-free pointer, and checksum storage. Indexed directories persist a dx root block referenced from `i_dx_root`; dx roots are either inline entry arrays or extent roots for leaf clusters.

## Dependencies and Integration Points

`dir.c` integrates with OCFS2 allocation, block validation/checksum, extent maps/trees, journaling, namei, inode locking, quota, truncate/dealloc, system files, uptodate tracking, buffer-head I/O, tracepoints, and VFS readdir. Higher-level namei code is expected to hold parent `i_rwsem` and cluster locks before calling lookup/prepare/add/delete paths as documented.

The indexed-directory design keeps readdir on the unindexed directory tree while using dx entries only as lookup/insert accelerators. That means every dx entry points back to a physical unindexed dirent block, and correctness requires the two structures to be updated atomically in one transaction.

## Risks and Edge Cases

The highest-risk behavior is keeping unindexed dirents, dx entries, dx root counts, dx leaf entries, and trailer free-list metadata consistent across failures. Ordering is carefully chosen in expansion/rebalance paths so newly allocated blocks are formatted and journaled before being linked into trees. Any change to journal credit calculation, access mode, or dirty ordering can create crash-consistency regressions.

Inline-to-extent expansion is complex because it may simultaneously remove `OCFS2_INLINE_DATA_FL`, allocate directory data clusters, optionally create a dx root and dx leaf cluster, initialize trailers, set i_size, and return lookup buffers for the pending insertion. Quota rollback uses `bytes_allocated`, which must match allocations performed before an error.

Hash collision handling is subtle. Dx lookup matches major/minor hash then verifies the real name in the unindexed dir block. Rebalance has special cases for a full leaf where every entry has the same major hash; if the new entry has that same hash, it returns `-ENOSPC` because splitting cannot help.

Readdir offset recovery depends on `i_version`. Corrupt `rec_len` values can otherwise trap scans; the code performs lightweight resync checks and full dirent validation before emitting. Trailer skipping is needed so trailer bytes are not interpreted as a usable dirent.

## Test Signals

Coverage should include inline directories, expansion from inline to one-block and two-block extent directories, unindexed extent directories, indexed directories with inline dx roots, expansion to external dx leaves, dx leaf rebalance, hash collisions, delete/free-list updates, truncate/removal of dx index, readdir during concurrent mutation, and crash-recovery tests around add/delete/expand/rebalance transactions.

Fault and corruption tests should inject bad dirent `rec_len`, bad trailer signature/block/parent, bad dx root/leaf signatures and extent counts, checksum failure, allocation/quota failures, ENOSPC during index split, and read failures during directory scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dir.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dir.h

## Purpose

`dir.h` declares the OCFS2 directory manipulation interface and defines the lookup-result structures shared between name lookup, insertion, deletion, and update code. It hides whether a directory is inline, unindexed extent-backed, or indexed behind common helper APIs.

## Important APIs, Types, and Functions

`struct ocfs2_dx_hinfo` stores the major and minor hash values used by indexed directory lookup and insertion. `struct ocfs2_dir_lookup_result` stores buffer heads and pointers for the unindexed dirent, dx root, dx leaf, dx entry, computed hash, and previous free-list leaf.

The main APIs are `ocfs2_find_entry()`, `ocfs2_delete_entry()`, `__ocfs2_add_entry()`, inline `ocfs2_add_entry()`, `ocfs2_update_entry()`, `ocfs2_check_dir_for_entry()`, `ocfs2_empty_dir()`, `ocfs2_find_files_on_disk()`, `ocfs2_lookup_ino_from_name()`, `ocfs2_readdir()`, `ocfs2_dir_foreach()`, `ocfs2_prepare_dir_for_insert()`, `ocfs2_fill_new_dir()`, `ocfs2_dx_dir_truncate()`, and `ocfs2_dir_trailer_from_size()`.

## Control Flow

Callers typically allocate a zeroed `ocfs2_dir_lookup_result`, call `ocfs2_find_entry()` for lookup/delete/update or `ocfs2_prepare_dir_for_insert()` before `ocfs2_add_entry()`, then release all held buffers with `ocfs2_free_dir_lookup_result()`. `ocfs2_add_entry()` is a dentry-friendly wrapper around `__ocfs2_add_entry()`.

## State and Persistence Behavior

The header does not mutate state directly. It defines the buffer ownership contract: lookup result fields hold references that must be released. The APIs declared here mutate persistent directory contents only in the corresponding `dir.c` implementation under journaling.

## Dependencies and Integration Points

This interface is consumed by OCFS2 namei, inode creation/removal, rename, orphan directory logic, VFS readdir, and truncate paths. It depends on buffer heads, journal handles, inode/dentry structures, OCFS2 on-disk dirent/dx types, and allocation contexts.

## Risks and Edge Cases

Callers must not free or dirty buffers in `ocfs2_dir_lookup_result` independently unless the called API documents it. Passing a lookup result from one directory mode after the directory has been converted or modified can corrupt the wrong buffers. `ocfs2_prepare_dir_for_insert()` may allocate blocks and return dx/free-list context that `ocfs2_add_entry()` expects to consume.

## Test Signals

API-level signals include balanced `ocfs2_free_dir_lookup_result()` use, correct behavior for inline and indexed directories through the same public calls, lookup/add/delete/update after directory expansion, and no leaked buffer references under failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/Makefile -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/Makefile

## Purpose

`fs/ocfs2/dlm/Makefile` defines the build composition for the OCFS2 O2CB distributed lock manager when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Important APIs, Types, and Functions

The file builds `ocfs2_dlm.o` from `dlmdomain.o`, `dlmdebug.o`, `dlmthread.o`, `dlmrecovery.o`, `dlmmaster.o`, `dlmast.o`, `dlmconvert.o`, `dlmlock.o`, and `dlmunlock.o`. There are no runtime APIs in this file, but its object list decides which DLM implementation units are linked.

## Control Flow

Kbuild includes this directory's object only when O2CB support is configured. The combined object contains domain join/leave, debugfs, worker thread, recovery, mastery, AST/BAST, convert, lock, and unlock logic.

## State and Persistence Behavior

No runtime state is stored here. The file controls compilation and linking only.

## Dependencies and Integration Points

It depends on the `CONFIG_OCFS2_FS_O2CB` Kconfig option and Kbuild's composite-object rules. The resulting `ocfs2_dlm.o` links with OCFS2 filesystem code and the cluster transport.

## Risks and Edge Cases

Removing or misordering an object can cause unresolved symbols or remove a message handler implementation that another DLM unit declares in `dlmcommon.h`. Because DLM files are tightly coupled through shared internal prototypes, configuration matrix builds are the main guard.

## Test Signals

Build with `CONFIG_OCFS2_FS_O2CB=y` and as module if supported, and build with it disabled. Runtime signals include DLM domain registration, lock/unlock/convert paths, recovery, and debugfs availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmapi.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmapi.h

## Purpose

`dlmapi.h` is the externally exported OCFS2 DLM interface. It defines DLM status codes, lock modes, public lock flags, lock status block layout, AST/BAST callback signatures, lock/unlock APIs, domain registration APIs, diagnostic printing, and eviction callback registration.

## Important APIs, Types, and Functions

`enum dlm_status` enumerates DLM return/status values, including traditional DLM outcomes and OCFS2 extensions such as `DLM_RECOVERING` and `DLM_MIGRATING`. `dlm_errname()` converts them to strings, and `dlm_error()` logs non-transient statuses.

`struct dlm_lockstatus` is the caller-visible lock status block. Callers are only allowed to access `status`, `flags`, `lockid`, and the 64-byte LVB. `DLM_LKSB_*` flags describe LVB get/put direction.

Lock modes are `LKM_NLMODE`, `LKM_PRMODE`, `LKM_EXMODE`, with other modes marked unsupported/invalid. Public flags include `LKM_VALBLK`, `LKM_NOQUEUE`, `LKM_CONVERT`, `LKM_UNLOCK`, `LKM_CANCEL`, `LKM_INVVALBLK`, `LKM_FORCE`, `LKM_LOCAL`, and many reserved/unsupported compatibility flags. Internal extension flags occupy high bits: `LKM_MIGRATION`, `LKM_PUT_LVB`, `LKM_GET_LVB`, and `LKM_RECOVERY`.

The core APIs are `dlmlock()`, `dlmunlock()`, `dlm_register_domain()`, `dlm_unregister_domain()`, `dlm_print_one_lock()`, and eviction callback helpers `dlm_setup_eviction_cb()`, `dlm_register_eviction_cb()`, and `dlm_unregister_eviction_cb()`.

## Control Flow

A filesystem registers a lock domain with `dlm_register_domain()`, passing a domain name, key, and filesystem locking protocol version. It then requests locks with `dlmlock()`, supplying a mode, LKS, flags, name, AST callback, callback data, and BAST callback. Granted or converted locks complete through AST callbacks; blocking notifications use BAST callbacks. Unlocks use `dlmunlock()` and optionally an unlock AST.

Domain unregister tears down the DLM context and associated network handlers. Eviction callbacks let upper layers learn when nodes are evicted or leave, allowing filesystem-level recovery and cleanup.

## State and Persistence Behavior

This header defines API state, not storage. Lock state lives in DLM contexts/resources/locks. The LVB is cluster-visible lock metadata associated with a lock resource and can carry filesystem state across lock transfers, but it is not persistent disk state by itself.

## Dependencies and Integration Points

The API integrates OCFS2 filesystem locking code with the O2CB DLM implementation. It depends on Linux list types for eviction callbacks and on internal DLM definitions for opaque `struct dlm_ctxt` and `struct dlm_lock`. It also integrates with debug code via status-name comments.

## Risks and Edge Cases

The flag namespace contains unsupported DLM compatibility flags and internal-only high bits. Public callers using unsupported or internal flags can get rejected or corrupt protocol assumptions. `DLM_LVB_LEN` is fixed at 64 bytes and is embedded into wire structures, so changing it would be ABI-wide.

Status interpretation matters: `DLM_NORMAL` is request in progress in comments, while granted/completion may be signaled asynchronously. Callers must honor AST/BAST callbacks and not assume `dlmlock()` return alone means the lock is usable unless the API documents synchronous status.

## Test Signals

Exercise domain register/unregister, PR and EX lock acquire, convert, noqueue failure, cancel, forced unlock, LVB get/put, recovery/migration rejection, eviction callbacks, and error-name logging. ABI tests should watch `struct dlm_lockstatus` and `DLM_LVB_LEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmast.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmast.c

## Purpose

`dlmast.c` implements AST and BAST delivery for OCFS2 DLM locks, both locally and by proxy network messages to remote lock owners. ASTs signal that a lock request/conversion has been granted; BASTs notify a holder that another request is blocked and that it should downconvert. The file also handles LVB transfer on AST delivery.

## Important APIs, Types, and Functions

`__dlm_queue_ast()` and `dlm_queue_ast()` enqueue AST delivery on `dlm->pending_asts`. `__dlm_queue_bast()` enqueues BAST delivery on `dlm->pending_basts`. `dlm_should_cancel_bast()` decides whether a newly queued AST makes a pending BAST obsolete.

`dlm_update_lvb()` copies a lock resource LVB into a lockstatus block for GET requests when the local node masters the resource, and clears LVB flags on the LKS. `dlm_do_local_ast()` invokes a local lock's AST callback after LVB update. `dlm_do_remote_ast()` updates LVB state and sends a proxy AST to the remote node. `dlm_do_local_bast()` invokes a local BAST callback.

`dlm_proxy_ast_handler()` processes remote proxy AST/BAST messages received over `o2net`. `dlm_send_proxy_ast_msg()` formats and sends a `struct dlm_proxy_ast` using `o2net_send_message_vec()`. Inline wrappers in `dlmcommon.h` provide `dlm_send_proxy_ast()` and `dlm_send_proxy_bast()`.

## Control Flow

When DLM thread logic grants a lock or conversion, it reserves AST capacity elsewhere and calls queue helpers under `dlm->ast_lock`. Queueing takes a lock reference, sets `ast_pending` or `bast_pending`, and links the lock into the pending AST/BAST list. If an AST moves a lock to a mode that no longer blocks anything, `dlm_should_cancel_bast()` removes an unsent BAST, clears `highest_blocked`, drops the extra lock reference, and releases the reserved AST slot.

Local delivery calls the callback stored on the lock. AST delivery first updates the LVB for mastered resources, then invokes `lock->ast(lock->astdata)`. BAST delivery calls `lock->bast(lock->astdata, blocked_type)`.

Remote AST delivery uses DLM proxy messages. The master constructs `dlm_proxy_ast`, including lock cookie, resource name, AST/BAST type, blocked type, sender node, and optional LVB data when the target requested GET_LVB. It sends the message to `lock->ml.node` and treats `DLM_RECOVERING` or `DLM_MIGRATING` responses as fatal logic errors.

On the receiving node, `dlm_proxy_ast_handler()` grabs the DLM domain, validates full join state, name length, AST type, and LVB flags, looks up the lock resource, rejects resources in recovery or migration, then searches converting/granted/blocked queues for the lock cookie. For ASTs it moves the lock to granted, applies the convert type, sets LKS status to `DLM_NORMAL`, copies incoming LVB when requested, releases the resource spinlock, and invokes the local AST. For BASTs it invokes the local BAST unless the lock has pending unlock state.

## State and Persistence Behavior

AST/BAST state is in-memory DLM runtime state: pending AST/BAST lists, per-lock pending bits, lock resource lists (`granted`, `converting`, `blocked`), lock modes, convert modes, highest blocked mode, LKS status/flags/LVB, and lock references. The LVB is cluster state attached to a lock resource and can be propagated in proxy AST messages, but this file does not write filesystem metadata.

## Dependencies and Integration Points

The file depends on O2NET transport, DLM API/common structures, lock resource lookup/refcounting, DLM thread pending-list processing, recovery/migration state flags, and DLM message type `DLM_PROXY_AST_MSG`. It is integrated with lock/convert/unlock code that queues ASTs/BASTs and with network handler registration in domain code.

## Risks and Edge Cases

AST/BAST cancellation is correctness-sensitive. A stale BAST can cause unnecessary downconvert pressure, but canceling a valid BAST can starve a blocked requester. The logic relies on `highest_blocked`, current mode, and pending/list state while holding both `dlm->ast_lock` and `lock->spinlock`.

Proxy handling trusts lock cookies and resource names after validation. If the target has already unlocked or recovered, unknown proxy ASTs are mostly ignored with `DLM_NORMAL` or rejected with `DLM_IVLOCKID`; migration/recovery states return special statuses. LVB GET and PUT flags are mutually exclusive, and mishandling them can propagate stale filesystem metadata.

Callbacks are invoked after releasing resource spinlocks in proxy handling, but comments in common structures note AST/BAST callbacks must be callable in constrained contexts. Lock lifetime depends on references taken when queued.

## Test Signals

Exercise local AST and BAST delivery, remote proxy AST/BAST delivery, convert grants, noqueue fast grants, BAST cancellation when a lock downconverts before delivery, LVB GET propagation, unknown lock/resource proxy messages, recovery/migration responses, unlock-pending BAST ignore, and multi-node lock contention with PR/EX modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmcommon.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmcommon.h

## Purpose

`dlmcommon.h` is the private shared header for the OCFS2 DLM implementation. It defines core DLM context/resource/lock structures, mastery list entries, recovery context, work items, lock resource state flags, wire message structures, message IDs, migration payload limits, helper functions, and cross-file prototypes.

## Important APIs, Types, and Functions

Hashing and sizing constants include `DLM_LOCKID_NAME_MAX`, `DLM_HASH_SIZE_DEFAULT`, `DLM_HASH_BUCKETS`, and `dlm_lockid_hash()`. Recovery and context state are represented by `struct dlm_recovery_ctxt` and `enum dlm_ctxt_state`.

`struct dlm_ctxt` is the domain-wide DLM object. It holds lockres and master hashes, dirty/purge/pending AST/BAST/tracking lists, domain maps, recovery context, master-list state, counters, debugfs root, refcount/state, heartbeat callbacks, DLM/recovery threads, workqueue, work list, network handler list, eviction callbacks, and filesystem/DLM locking protocol versions.

`struct dlm_lock_resource` is a named lock resource with hash/list nodes, refcount, granted/converting/blocked/purge/dirty/recovering/tracking lists, owner, state flags, LVB, inflight counters, AST reservation count, waitqueue, and refmap. `struct dlm_lock` stores the migratable lock header, list nodes, lock resource pointer, spinlock/refcount, AST/BAST callbacks, callback data, LKS pointer, and pending bits.

Wire structures cover mastery, migration, create/convert/unlock/proxy AST, domain join/exit, recovery, node/region query, and deref flows. Message IDs range from `DLM_MASTER_REQUEST_MSG` through `DLM_DEREF_LOCKRES_DONE`. Migration sizing is explicitly tied to `O2NET_MAX_PAYLOAD_BYTES`.

Inline helpers include lockres hash accessors, work item initialization, joining-node wakeup, LVB empty check, list index mapping, lock resource state-to-status mapping, cookie node/sequence extraction, proxy AST/BAST wrappers, lock compatibility, error-to-DLM-status mapping, node iterators, and owner changes.

## Control Flow

The header describes the DLM's major flows. Domain setup creates a `dlm_ctxt`, registers O2NET handlers, starts the DLM and recovery threads, and tracks live/domain/recovery maps. Lock acquisition creates or looks up a `dlm_lock_resource`, negotiates mastery through MLEs and mastery messages, then moves `dlm_lock` objects through blocked, converting, and granted lists. AST and BAST work is queued on pending lists and processed by DLM thread code.

Recovery and migration use the recovery context, recovery node data states, migratable lock resource payloads, request-all-locks flows, migration requests, and finalize messages. Work items allow handlers to defer operations that cannot run directly from network message context.

The wire structs and prototypes make O2NET the communication substrate: every `*_handler()` takes `struct o2net_msg`, payload length, handler data, and optional return data, matching the transport API.

## State and Persistence Behavior

All core state is in-memory cluster lock state. It is persistent only for the lifetime of a DLM domain and is reconstructed/recovered through cluster protocols after node death. The LVB in `dlm_lock_resource` is cluster-visible logical state and is migrated/recovered with lock resources, but it is not directly disk-persistent.

State flags on lock resources (`UNINITED`, `RECOVERING`, `READY`, `DIRTY`, `IN_PROGRESS`, `MIGRATING`, `DROPPING_REF`, `BLOCK_DIRTY`, `SETREF_INPROG`, `RECOVERY_WAITING`) gate whether handlers return `DLM_RECOVERING`, `DLM_MIGRATING`, or `DLM_FORWARD`, and whether callers must wait.

Migration payloads persist across the network only for one operation. `DLM_MAX_MIGRATABLE_LOCKS` is chosen so one lock resource plus 240 locks and reserved bytes fit into the O2NET payload limit.

## Dependencies and Integration Points

`dlmcommon.h` depends on `dlmapi.h`, O2NET payload limits/link classification, node manager limits, heartbeat callbacks, Linux list/hlist/kref/workqueue/waitqueue/bitmap/spinlock types, full-name hash, and OCFS2 debugfs/logging code. It is included by all DLM implementation units and is the glue between domain, mastery, recovery, AST, conversion, locking, and unlocking files.

The header also integrates DLM protocol negotiation with filesystem locking protocol versions through `struct dlm_protocol_version` fields in `dlm_ctxt` and join packets.

## Risks and Edge Cases

This header is high blast radius. Changes to structures used on the wire require coordinated protocol handling and length checks. Endianness annotations are mixed with fixed-size fields; missing conversions in implementations can break multi-architecture clusters. Lock resource list ordering is documented as significant because some functions iterate granted/converting/blocked in order.

State flag combinations are subtle. `__dlm_lockres_state_to_status()` prioritizes recovery over migration over in-progress forwarding; callers depend on that ordering. Refcounts are layered: DLM context refs, lock resource refs, lock refs, inflight refs, and list-held refs all coexist.

Migration sizing depends on `O2NET_MAX_PAYLOAD_BYTES`; changing the transport header size or payload limit affects `DLM_MIG_LOCKRES_RESERVED`. Lock names are capped at 32 bytes for DLM resources while some network messages have larger name arrays from node-manager constants.

## Test Signals

Configuration/build signals include all DLM object files compiling against this header and no wire-size overflows. Runtime tests should cover domain join/protocol negotiation, lock mastery, remote create/convert/unlock, AST/BAST, lock resource purge, node death recovery, lock resource migration, refmap deref flows, recovery lock handling, hash lookup, and DLM shutdown.

Fault injection should target O2NET link-down errors, message payload length boundaries, lock name length rejection, recovery/migration state races, duplicate or stale mastery messages, and multi-node recovery with many locks approaching `DLM_MAX_MIGRATABLE_LOCKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmcommon.h -->
