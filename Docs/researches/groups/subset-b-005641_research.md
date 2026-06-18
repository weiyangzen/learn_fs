# subset-b-005641 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lowcomms.c -->
# sources/distributed-fs/ceph-client/fs/dlm/lowcomms.c

## Purpose
`lowcomms.c` is the DLM transport layer. It maps cluster node ids to configured socket addresses, owns TCP/SCTP listening and outgoing sockets, queues outbound bytes into page-backed write queue entries, receives raw byte streams from peers, validates complete DLM packet boundaries through midcomms, and hands full buffers to a DLM processing workqueue. It deliberately keeps callers from doing socket I/O directly so lock paths do not block under load.

## Important APIs, Types, And Functions
Key internal types are `struct connection`, `struct listen_connection`, `struct writequeue_entry`, `struct dlm_msg`, `struct processqueue_entry`, and `struct dlm_proto_ops`. Connections are hashed by `nodeid_hash()` under `connection_hash[]`, protected by SRCU plus `connections_lock`; socket lifetime is serialized by `sock_lock`.

The exported API includes `dlm_lowcomms_start()`, `dlm_lowcomms_shutdown()`, `dlm_lowcomms_stop()`, `dlm_lowcomms_init()`, `dlm_lowcomms_exit()`, `dlm_lowcomms_addr()`, `dlm_lowcomms_connect_node()`, `dlm_lowcomms_close()`, `dlm_lowcomms_new_msg()`, `dlm_lowcomms_commit_msg()`, `dlm_lowcomms_put_msg()`, and `dlm_lowcomms_resend_msg()`. Cache constructors `dlm_lowcomms_writequeue_cache_create()` and `dlm_lowcomms_msg_cache_create()` are consumed by `memory.c`.

Important workers and callbacks are `process_send_sockets()`, `process_recv_sockets()`, `process_listen_recv_socket()`, `lowcomms_data_ready()`, `lowcomms_write_space()`, `lowcomms_error_report()`, `receive_from_sock()`, `send_to_sock()`, `accept_from_sock()`, and `dlm_connect()`.

## Control Flow
Startup runs `init_local()` to load local cluster addresses from configfs, chooses TCP or SCTP `dlm_proto_ops`, creates `dlm_io` and `dlm_process` workqueues, creates a kernel socket, installs listen callbacks, binds/listens on the configured DLM port, and stores the listen socket in `listen_con`.

Outbound flow starts when midcomms calls `dlm_lowcomms_new_msg()`. The function finds the per-node connection, allocates or reuses a page-backed `writequeue_entry`, returns a writable pointer, and keeps a SRCU read-side lock until `dlm_lowcomms_commit_msg()`. Commit links a `dlm_msg` to the entry, marks the entry sendable when all users are done filling it, and queues send work. `process_send_sockets()` connects if no socket exists, then repeatedly calls `send_to_sock()` until the socket blocks, the queue drains, or an error causes reconnection.

Inbound flow starts from socket callbacks. Data-ready schedules `rwork`; `receive_from_sock()` merges previous leftovers with a nonblocking `kernel_recvmsg()`, calls `dlm_validate_incoming_buffer()` to find complete DLM messages, saves incomplete tail bytes in `rx_leftover_buf`, and queues a `processqueue_entry`. `process_dlm_messages()` calls `dlm_process_incoming_buffer()` outside the socket worker, so parsing and lock handling are separated from socket receive.

Accepted inbound sockets are matched back to cluster nodes with `addr_to_nodeid()`. If an outgoing socket already exists, the accepted socket is placed in `othercon` to support historical crossed-connect behavior. Connection close, shutdown, and node removal stop callbacks, cancel work, optionally perform socket shutdown handshakes, clean partial writes, and release connections through SRCU callbacks.

## State And Persistence
All state is in kernel memory: connection hash entries, socket pointers, per-node address arrays, write queues, process queues, leftover receive bytes, transport protocol selection, and workqueues. It persists for the lifetime of the DLM module or a live node membership entry, not across reboot. Write queue entries use krefs because a page, the queued entry, and one or more `dlm_msg` handles can share lifetime. Partial dirty entries are discarded after reconnect to avoid delivering half a message.

## Dependencies And Integration Points
This file integrates with configfs via `dlm_our_addr()`, `dlm_config`, `dlm_comm_seq`, and protocol settings; with midcomms through `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`, and `dlm_midcomms_unack_msg_resend()`; with memory cache setup through `memory.c`; with Linux sockets, TCP, SCTP, workqueues, SRCU, RCU, krefs, and tracepoints.

## Risks
The largest risks are races around socket callback replacement, `othercon` handling, SRCU connection removal, and writequeue lifetime. A protocol mismatch, bad configured addresses, or missing local address blocks startup. The code retries outbound connect forever, so cluster-manager fencing or upper-layer failure detection must handle unreachable peers. Receive-side buffering can grow pressure under bursts; `DLM_MAX_PROCESS_BUFFERS` backpressure waits for the processing queue to drain.

## Test Signals
Useful signals include successful TCP/SCTP module startup, connection establishment and reconnect under node restart, retransmission after socket error, no use-after-free under simultaneous accept/connect/close, correct handling of packet fragmentation across receives, and tracepoints `trace_dlm_send`/`trace_dlm_recv`. Fault injection for allocation failures, malformed lengths, and write-space/app-limited transitions is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lowcomms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lowcomms.h -->
# sources/distributed-fs/ceph-client/fs/dlm/lowcomms.h

## Purpose
`lowcomms.h` declares the DLM low-level communications interface and the node-id hash shared with midcomms. It defines the maximum DLM application payload size after reserving space for the midcomms options header.

## Important APIs, Types, And Functions
The header exposes lifecycle functions, address registration, node close/connect helpers, message allocation and commit helpers, retransmit helpers, and slab cache constructors. `CONN_HASH_SIZE` is fixed at 32 and `nodeid_hash()` assumes common cluster node ids are small/sequential.

## Control Flow
Callers initialize lowcomms once, start it when DLM communications should listen/connect, allocate messages by node id, commit or drop message handles, close specific nodes during recovery/fencing, and stop/shutdown transport on lockspace teardown.

## State And Persistence
The header itself owns no state. Its constants shape the in-memory connection hash and payload limits used by `lowcomms.c` and `midcomms.c`.

## Dependencies And Integration Points
It includes `dlm_internal.h` for DLM core types and exposes `struct dlm_msg` handles to midcomms/rcom users without requiring callers to know the writequeue internals. `DLM_MAX_APP_BUFSIZE` depends on `DLM_MAX_SOCKET_BUFSIZE` from config and `struct dlm_opts`.

## Risks
One declaration, `dlm_lowcomms_shutdown_node(int nodeid, bool force)`, has no implementation in the inspected source set, so users must verify tree-wide build status before depending on it. Payload-size constants must stay consistent with wire format changes.

## Test Signals
Compile coverage should catch declaration/definition mismatches. Runtime tests should cover max-size message allocation and correct behavior when callers pass invalid node ids or oversized messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lowcomms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lvb_table.h -->
# sources/distributed-fs/ceph-client/fs/dlm/lvb_table.h

## Purpose
`lvb_table.h` declares the lock value block operation matrix used by DLM AST and lock conversion code to decide when LVB data should be copied, invalidated, or propagated across mode transitions.

## Important APIs, Types, And Functions
It exports `extern const int dlm_lvb_operations[8][8]`. The table is defined in `lock.c` and referenced by `ast.c` and lock paths.

## Control Flow
This header has no control flow. It provides a shared declaration so user-facing callback code and core lock state transitions agree on LVB handling semantics.

## State And Persistence
The declared matrix is static read-only kernel data. It affects in-memory lock result/LVB decisions but has no persistence beyond module lifetime.

## Dependencies And Integration Points
Integrated directly with `user.c` through `dlm_user_add_ast()` and callback output handling, and with `lock.c` where the table is defined and lock mode transitions are evaluated.

## Risks
Any mismatch between table dimensions and DLM lock-mode numeric ranges can cause out-of-bounds access. Semantic changes to the matrix can alter user-visible LVB validity and callback contents.

## Test Signals
Mode conversion tests with VALBLK locks should verify expected LVB propagation for all relevant grant/request mode pairs, especially recovery and conversion cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lvb_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/main.c -->
# sources/distributed-fs/ceph-client/fs/dlm/main.c

## Purpose
`main.c` is the DLM module entry and exit point. It orders subsystem initialization, exports the public kernel DLM symbols, and tears subsystems down in reverse order.

## Important APIs, Types, And Functions
The central functions are `init_dlm()` and `exit_dlm()`. The module creates global workqueue `dlm_wq`, registers tracepoints, and exports `dlm_new_lockspace`, `dlm_release_lockspace`, `dlm_lock`, and `dlm_unlock`.

## Control Flow
Initialization creates memory caches, initializes midcomms/lowcomms state, initializes lockspace management and config, registers debugfs, registers userspace misc devices, registers the plock device, then allocates `dlm_wq`. Each failure label unwinds only the subsystems already initialized. Exit destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms/debugfs/memory.

## State And Persistence
Module-global state consists of subsystem registrations, misc devices, config/debugfs state, memory caches, and `dlm_wq`. None persists after module unload.

## Dependencies And Integration Points
This file coordinates `memory.c`, `midcomms.c`, `lockspace`, `config`, debugfs, `user.c`, and `plock.c`. Public symbols are consumed by cluster filesystems such as GFS2.

## Risks
Initialization order matters because memory cache creation asks lowcomms/midcomms for cache constructors before those layers are started. Exit ordering assumes no live lockspaces or users remain. A failure to allocate `dlm_wq` happens late and must unwind all earlier registrations.

## Test Signals
Module load/unload tests should confirm every failure path unregisters devices and frees caches. Symbol export coverage is provided by building cluster filesystem users against the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/member.c -->
# sources/distributed-fs/ceph-client/fs/dlm/member.c

## Purpose
`member.c` maintains lockspace membership, slot assignment, membership-related lockspace stop/start transitions, and callbacks to lockspace users during recovery. It is the bridge between configfs membership snapshots and DLM internal member lists.

## Important APIs, Types, And Functions
Important exports include `dlm_recover_members()`, `dlm_ls_stop()`, `dlm_ls_start()`, `dlm_clear_members()`, `dlm_clear_members_gone()`, `dlm_is_member()`, `dlm_is_removed()`, `dlm_slots_assign()`, `dlm_slots_copy_in()`, `dlm_slots_copy_out()`, `dlm_slot_save()`, `dlm_slots_version()`, and `dlm_lsop_recover_done()`.

The file uses `struct dlm_member`, `struct dlm_config_node`, `struct dlm_slot`, `rcom_config`, and `rcom_slot` structures. Membership lists live in `ls->ls_nodes` and `ls->ls_nodes_gone`.

## Control Flow
During recovery, `dlm_recover_members()` first counts prior gone members as negative changes, moves departed or re-added members from `ls_nodes` to `ls_nodes_gone`, notifies midcomms and lockspace ops of removals, adds new members from the config snapshot, recomputes the low node id and weighted node array, and pings members with `dlm_rcom_status()`.

Slot flow is led by the lowest node. It collects slot/generation data via status rcoms, runs `dlm_slots_assign()` to retain previous slots and allocate free offsets for new members, then distributes the sparse slot table through rcom status replies. Non-low nodes call `dlm_slots_copy_in()` to copy the low node's slot map.

`dlm_ls_stop()` stops normal receive processing, sets recovery-stop and locking-stopped flags, increments the recovery sequence, activates the requestqueue, waits for recovery lock acquisition when needed, suspends/resumes recoverd, clears old slot state, and invokes `recover_prep` once per stop. `dlm_ls_start()` obtains a new config snapshot, verifies the lockspace is stopped, installs a `dlm_recover` argument, and wakes recoverd.

## State And Persistence
Membership state is in lockspace lists, member slot fields, `ls_num_nodes`, `ls_low_nodeid`, `ls_node_array`, `ls_slots`, `ls_generation`, and recovery arguments. It persists while the lockspace lives and is regenerated on membership changes. Slot generation increases across successful slot assignment.

## Dependencies And Integration Points
This file integrates with `config.c` for node snapshots and communication sequence numbers, lowcomms/midcomms for connecting and member add/remove notifications, rcom for status pings, recoverd for stop/start synchronization, and lockspace ops (`recover_prep`, `recover_slot`, `recover_done`) used by filesystems.

## Risks
Incorrect membership transitions can leave midcomms user counts wrong or skip filesystem recovery callbacks. Slot assignment must preserve existing slots; slot changes are treated as errors. `dlm_ls_stop()` depends on precise lock ordering across recv, recover, requestqueue, and in-recovery locks.

## Test Signals
Test member add, remove, remove/re-add with changed `comm_seq`, slot assignment across mixed generations, low-node and non-low-node slot paths, and stop/start races with incoming messages. GFS2 mount/umount and node-failure tests should show recover_slot/recover_done callbacks in expected order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/member.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/member.h -->
# sources/distributed-fs/ceph-client/fs/dlm/member.h

## Purpose
`member.h` declares lockspace membership and slot-management APIs for recovery, rcom, lockspace, and midcomms users.

## Important APIs, Types, And Functions
The header exposes lockspace start/stop, list clearing, membership tests, recovery member update, slot version/copy/assign helpers, and final recovery-done lockspace-op notification.

## Control Flow
Consumers call `dlm_ls_stop()` before membership recovery, then `dlm_ls_start()` to queue a new `dlm_recover` run. Recovery/rcom paths use the slot helpers while gathering and distributing per-node slot maps.

## State And Persistence
The header owns no state; it exposes functions that mutate `struct dlm_ls` membership lists, slots, generation, and recovery state.

## Dependencies And Integration Points
It depends on core DLM types from `dlm_internal.h`. `recover.c`, `recoverd.c`, `rcom.c`, `requestqueue.c`, and lockspace code all use these declarations.

## Risks
API misuse can break recovery ordering. `dlm_recover_members()` has an adjacent formatting issue in its prototype (`rv,int`) but this is syntactic only.

## Test Signals
Compile coverage across recovery and rcom users plus runtime membership-change tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/member.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/memory.c -->
# sources/distributed-fs/ceph-client/fs/dlm/memory.c

## Purpose
`memory.c` centralizes slab cache creation and allocation/free wrappers for core DLM objects: writequeue entries, midcomms handles, lowcomms messages, lock blocks, resource blocks, callbacks, and lock value blocks.

## Important APIs, Types, And Functions
Lifecycle functions are `dlm_memory_init()` and `dlm_memory_exit()`. Allocation wrappers include `dlm_allocate_rsb()`, `dlm_free_rsb()`, `dlm_allocate_lkb()`, `dlm_free_lkb()`, `dlm_allocate_lvb()`, `dlm_free_lvb()`, `dlm_allocate_mhandle()`, `dlm_free_mhandle()`, `dlm_allocate_writequeue()`, `dlm_free_writequeue()`, `dlm_allocate_msg()`, `dlm_free_msg()`, `dlm_allocate_cb()`, and `dlm_free_cb()`.

## Control Flow
Initialization creates caches in dependency order and unwinds on allocation failure. RSB and LKB frees use `call_rcu()`; callback `__free_rsb_rcu()` also frees an attached LVB, while `__free_lkb_rcu()` frees user-argument storage and user LVB pointers for user locks. Exit calls `rcu_barrier()` before destroying caches.

## State And Persistence
State is limited to static cache pointers. Allocated objects live in kernel memory until their DLM refcount/RCU lifecycle releases them.

## Dependencies And Integration Points
Cache constructors come from `lowcomms.c` and `midcomms.c`. RCU lifetime is required because locks and resources can be visible to concurrent readers. User lock cleanup integrates with `user.c` structures stored in `lkb_ua`.

## Risks
Because most allocations use `GFP_ATOMIC`, memory pressure can surface as operation failures in lock and communication paths. Missing `rcu_barrier()` would risk destroying caches before deferred frees complete. Freeing user arguments only for `DLM_DFL_USER_BIT` locks must remain consistent with lock ownership flags.

## Test Signals
Allocation-failure injection, module unload under recently freed locks/resources, and KASAN/RCU diagnostics are the primary signals. Lock/unlock tests should not leak `dlm_user_args`, LVBs, callbacks, or message handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/memory.h -->
# sources/distributed-fs/ceph-client/fs/dlm/memory.h

## Purpose
`memory.h` declares DLM memory-cache lifecycle and typed allocation/free wrappers so other DLM modules avoid direct slab-cache knowledge.

## Important APIs, Types, And Functions
It exposes cache lifecycle plus alloc/free pairs for RSBs, LKBs, LVBs, midcomms handles, writequeue entries, lowcomms messages, and callbacks.

## Control Flow
Callers initialize all caches during module load, allocate objects on demand, free through the matching wrapper, and destroy caches at module exit.

## State And Persistence
No header-owned state. The implementation's caches persist for module lifetime.

## Dependencies And Integration Points
It references core DLM types and opaque communication types used by lowcomms, midcomms, callbacks, lock, recovery, and user paths.

## Risks
Every allocation must be paired with the correct free function because several frees are RCU-deferred and object-type specific. Exposing opaque types by pointer keeps compile-time coupling low but leaves lifetime correctness to callers.

## Test Signals
Compile-time API coverage plus leak detection after stress lock/recovery/comms tests validate the wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/midcomms.c -->
# sources/distributed-fs/ceph-client/fs/dlm/midcomms.c

## Purpose
`midcomms.c` adds DLM-level reliability and protocol-version handling above lowcomms. For DLM 3.2 peers it wraps messages in `DLM_OPTS`, assigns sequence numbers, tracks unacknowledged messages, retransmits after transport errors, drops duplicate receives, and performs a DLM FIN/ACK shutdown state machine.

## Important APIs, Types, And Functions
Key types are `struct midcomms_node` and `struct dlm_mhandle`. Important exports include `dlm_midcomms_addr()`, `dlm_midcomms_get_mhandle()`, `dlm_midcomms_commit_mhandle()`, `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`, `dlm_midcomms_unack_msg_resend()`, lifecycle wrappers, member add/remove functions, `dlm_midcomms_close()`, `dlm_midcomms_shutdown()`, debug accessors, and `dlm_midcomms_rawmsg_send()`.

## Control Flow
Address registration calls lowcomms address setup, creates a `midcomms_node`, initializes sequence counters and send queues, and creates debugfs communication state. On send, `dlm_midcomms_get_mhandle()` checks node version. Version 3.1 sends a raw lowcomms message. Version 3.2 may send a threshold ACK first, allocates a wrapped lowcomms message, inserts the handle into the send queue via callback, fills an options header, and assigns a sequence. Commit finalizes `o_nextcmd`, traces, and commits the lowcomms message.

Receive validation first uses lowcomms-visible `dlm_validate_incoming_buffer()` to determine complete frame lengths. `dlm_process_incoming_buffer()` dispatches by `h_version`. Version 3.1 directly accepts RCOM/MSG after minimal length checks. Version 3.2 accepts early RCOM status/name messages for version detection without the reliability wrapper, handles `DLM_OPTS` by checking outer and inner lengths, and passes sequenced inner packets to `dlm_midcomms_receive_buffer()`. ACKs release all send-queue handles with sequence lower than the acknowledged sequence.

Shutdown uses reduced TCP-like states: `CLOSED`, `ESTABLISHED`, `FIN_WAIT1`, `FIN_WAIT2`, `CLOSE_WAIT`, `LAST_ACK`, and `CLOSING`. Member add/remove updates per-node `users`; zero users or received FIN drives active or passive FIN exchange. Forced close sets `DLM_NODE_FLAG_CLOSE`, wakes waiters, closes lowcomms, removes debugfs and the node from the hash, flushes send queues, and RCU-frees the node.

## State And Persistence
Per-node state includes detected protocol version, send and receive sequence counters, unacknowledged send queue, delivered-message ACK counters, shutdown flags/state, users count, waitqueue, and debugfs pointer. It is in-memory and tied to node membership/address lifetime. Unacknowledged 3.2 messages persist in memory until ACKed, resent, flushed, or node close.

## Dependencies And Integration Points
Midcomms depends on lowcomms message allocation/resend, config constants, DLM wire structures, lock receive dispatch `dlm_receive_buffer()`, debugfs communication files, tracepoints, memory cache wrappers, and errno conversion helpers indirectly through DLM packet handling.

## Risks
Sequence arithmetic and send-queue deletion are concurrency-sensitive; ACK receive can release message handles quickly after commit. Version detection relies on early RCOM name/status messages for backward compatibility. The comments call out known gaps: unaligned message lengths, incomplete tail-size validation, and future fencing needs for bad sequence behavior or shutdown timeouts.

## Test Signals
Exercise mixed 3.1/3.2 protocol peers, duplicate and out-of-order message receives, socket reconnect retransmission, ACK threshold behavior, active/passive shutdown state transitions, forced node fencing close, and debug raw-message injection. KASAN/KCSAN are useful around ACK/commit races and node removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/midcomms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/midcomms.h -->
# sources/distributed-fs/ceph-client/fs/dlm/midcomms.h

## Purpose
`midcomms.h` declares the reliable DLM messaging layer interface between lock/rcom code and lowcomms transport.

## Important APIs, Types, And Functions
The header forward-declares `struct midcomms_node` and exports receive validation/processing, message-handle allocation/commit, address setup, version wait, node close, lifecycle functions, member notifications, resend trigger, debug accessors, raw-message send, and cache constructor.

## Control Flow
Senders obtain a `dlm_mhandle`, fill the returned payload pointer, then must commit with `dlm_midcomms_commit_mhandle()`. Lowcomms calls validation and processing functions for incoming buffers. Membership code calls add/remove and close functions around recovery events.

## State And Persistence
No header-owned state. It exposes operations over per-node midcomms state held in `midcomms.c`.

## Dependencies And Integration Points
It integrates lock/rcom/recovery code with DLM communications while hiding lowcomms `struct dlm_msg` details. Debugfs uses the accessor functions for state, flags, version, and queue count.

## Risks
The get/commit contract is strict: failing to commit a successful handle leaks the SRCU read-side state and message resources. Callers must not send after member removal unless they intentionally use raw debug facilities.

## Test Signals
Compile coverage and send-path tests should verify all callers commit or abandon handles only through valid error paths. Debugfs output should reflect live node state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/midcomms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/plock.c -->
# sources/distributed-fs/ceph-client/fs/dlm/plock.c

## Purpose
`plock.c` delegates distributed POSIX byte-range lock coordination to userspace through the DLM plock misc device while maintaining local VFS lock bookkeeping. It exports kernel helpers used by cluster filesystems for POSIX lock, unlock, cancel, and get operations.

## Important APIs, Types, And Functions
Important exports are `dlm_posix_lock()`, `dlm_posix_unlock()`, `dlm_posix_cancel()`, `dlm_posix_get()`, `dlm_plock_init()`, and `dlm_plock_exit()`. Internal state uses `struct plock_op` and optional `struct plock_async_data`. Device operations are `dev_read()`, `dev_write()`, and `dev_poll()` on `DLM_PLOCK_MISC_NAME`.

## Control Flow
Kernel lock requests build a `dlm_plock_info`, enqueue it on `send_list`, and wake the userspace daemon. `dev_read()` moves most requests from `send_list` to `recv_list` and copies them to userspace; close-generated unlocks do not require replies and are freed after read. `dev_write()` copies a result back, matches it to a waiting operation, updates the op, and either wakes a synchronous waiter or invokes an async callback.

`dlm_posix_lock()` supports blocking, nonblocking, and async locks. Blocking waits can be interrupted; interruption sends a cancel op and either removes the original waiter or waits for completion. Successful locks are also installed in local VFS lock state. `dlm_posix_unlock()` removes local VFS lock state first, sends a distributed unlock, and treats `-ENOENT` as success. `dlm_posix_cancel()` currently supports async requests and either removes the pending op or falls back to unlock if userspace was too late. `dlm_posix_get()` asks userspace for conflicting lock info and maps remote pids to negative values.

## State And Persistence
Global in-memory state consists of `send_list`, `recv_list`, waitqueues, and `ops_lock`. State exists only while the module is loaded. Individual operations persist until userspace reads and replies, close-generated unlocks are read, or cancellation removes them.

## Dependencies And Integration Points
This file integrates with Linux file-lock APIs (`locks_lock_file_wait`, `posix_lock_file`), the misc device framework, DLM lockspace lookup, `linux/dlm_plock.h` wire structs, and userspace daemon compatibility via version fields.

## Risks
The correctness of distributed POSIX locks depends on a responsive userspace plock daemon. Async callback paths intentionally ignore some local VFS bookkeeping failures, which can leave distributed state authoritative but local state imperfect. Cancellation matching requires exact field comparisons and can be racy around userspace completion. Lists must be empty on module exit.

## Test Signals
Test blocking interruption, async NFS-style callbacks, cancel-before-grant and cancel-after-grant, close-generated unlocks, version mismatch rejection, daemon restart behavior, and local VFS lock state after distributed grants/unlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/plock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/rcom.c -->
# sources/distributed-fs/ceph-client/fs/dlm/rcom.c

## Purpose
`rcom.c` implements DLM recovery communication messages. These RCOM packets coordinate recovery status barriers, slot/config exchange, directory-name transfer, new-master lookup, and lock-copy recovery between nodes.

## Important APIs, Types, And Functions
Exports include `dlm_rcom_status()`, `dlm_rcom_names()`, `dlm_send_rcom_lookup()`, `dlm_send_rcom_lock()`, `dlm_receive_rcom()`, and `dlm_send_ls_not_ready()`. Internal helpers include `create_rcom()`, `create_rcom_stateless()`, `allow_sync_reply()`, `receive_sync_reply()`, `check_rcom_config()`, `receive_rcom_status()`, `receive_rcom_names()`, `receive_rcom_lookup()`, `receive_rcom_lock()`, and `pack_rcom_lock()`.

## Control Flow
Synchronous recovery queries set `LSFL_RCOM_WAIT`, increment `ls_rcom_seq`, clear `ls_recover_buf`, send a request, and wait through `dlm_wait_function()` until `receive_sync_reply()` copies the matching reply into `ls_recover_buf`. Status requests are sent stateless through lowcomms for backward-compatible early version detection; name/lookup/lock recovery messages use midcomms handles.

Status replies include recovery status and configuration (`lvblen`, lockspace flags, slots, generation). The low node gathers per-node slot values; non-low nodes can request the full slot table by setting `DLM_RSF_NEED_SLOTS`. Names requests ask a peer to copy master resource names that hash to this node. Lookup requests ask a directory node to assign/return a new master. Lock requests send process-copy lock details to a new master and receive the new remote id/result.

`dlm_receive_rcom()` gates messages by recovery stop state, recovery sequence, and status-stage ordering. It ignores names/lookup/lock before `DLM_RS_NODES`, and lookup/lock before `DLM_RS_DIR`, then dispatches by RCOM type.

## State And Persistence
State lives in the lockspace: `ls_recover_buf`, `ls_rcom_seq`, `ls_flags` wait/ready bits, recovery status, slots, and generation. RCOM packets are transient but can drive persistent in-memory recovery changes such as new master ids and recovered lock copies.

## Dependencies And Integration Points
RCOM integrates with midcomms/lowcomms, recovery wait helpers, directory recovery, member slot helpers, lock recovery (`dlm_recover_master_reply`, `dlm_recover_master_copy`, `dlm_recover_process_copy`), and errno/config compatibility checks.

## Risks
Recovery depends on strict sequence matching and stage gating. Config mismatches return `-EPROTO`. Timeouts retry status/name calls, so repeated communication failure can delay recovery. Length checks exist for lock messages, but correctness also depends on sender/receiver struct compatibility.

## Test Signals
Test recovery barriers, slot-table exchange, remote lockspace-not-ready replies, config mismatch, stale sequence replies, short lock messages, directory rebuild, new-master lookup, and lock copy reconstruction across node failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/rcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/rcom.h -->
# sources/distributed-fs/ceph-client/fs/dlm/rcom.h

## Purpose
`rcom.h` declares DLM recovery communication send and receive entry points.

## Important APIs, Types, And Functions
It exposes status, names, lookup, lock recovery sends, the receive dispatcher, and the special lockspace-not-ready reply helper.

## Control Flow
Recovery code uses the send helpers during barrier, directory, master, and lock recovery phases. The receive path calls `dlm_receive_rcom()` for all RCOM packets and `dlm_send_ls_not_ready()` when a packet targets a lockspace that is not ready.

## State And Persistence
The header owns no state. Implementations mutate lockspace recovery buffers and resource/lock state.

## Dependencies And Integration Points
It is used by `recover.c`, `recoverd.c`, `member.c`, lock receive paths, and low/mid communications.

## Risks
RCOM callers must pass the correct recovery sequence; stale sequence usage causes intentional ignore behavior. Lookup and lock sends require valid RSB/LKB lifetime.

## Test Signals
Build and recovery tests should cover each declared message type and lockspace-not-ready behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/rcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recover.c -->
# sources/distributed-fs/ceph-client/fs/dlm/recover.c

## Purpose
`recover.c` implements the core DLM recovery algorithms after membership changes: status barriers, new master discovery, process-lock reconstruction, LVB recovery, conversion repair, recovered-grant marking, and inactive resource cleanup.

## Important APIs, Types, And Functions
Important exports include `dlm_wait_function()`, `dlm_recover_status()`, `dlm_set_recover_status()`, `dlm_recover_members_wait()`, `dlm_recover_directory_wait()`, `dlm_recover_locks_wait()`, `dlm_recover_done_wait()`, `dlm_recover_masters()`, `dlm_recover_master_reply()`, `dlm_recover_locks()`, `dlm_recovered_lock()`, `dlm_recover_rsbs()`, and `dlm_clear_inactive()`.

Internally it uses recovery lists and an xarray (`ls_recover_list`, `ls_recover_xa`) to track outstanding lookup and lock-copy replies. Resource flags such as `RSB_NEW_MASTER`, `RSB_NEW_MASTER2`, `RSB_RECOVER_LVB_INVAL`, `RSB_RECOVER_CONVERT`, `RSB_VALNOTVALID`, and `RSB_RECOVER_GRANT` drive later stages.

## Control Flow
`dlm_wait_function()` waits for a predicate or recovery stop, with timer-based timeout handling for RCOM waits. Barrier helpers use the lowest node as an aggregator: low node polls every member and then sets an `_ALL` status bit; other nodes poll the low node for the aggregate bit.

Master recovery walks the root RSB list. If no directory mode is configured, `recover_master_static()` assigns master based on hash and purges all MSTCPY locks. Otherwise, resources whose old master left or whose directory lookup established a new master either become locally mastered or are inserted into `ls_recover_xa` and queried with `dlm_send_rcom_lookup()`. Replies call `dlm_recover_master_reply()` to set `res_master_nodeid`, `res_nodeid`, and new-master flags.

Lock recovery sends all local process-copy locks on remastered resources to the new master with `dlm_send_rcom_lock()`. The RSB stays on `ls_recover_list` until replies call `dlm_recovered_lock()` enough times to clear `res_recover_locks_count`.

Final RSB recovery fixes LVB validity and contents, resolves PR/CW conversion conflicts by downgrading incompatible converting grants to NL, and marks resources that may be able to grant waiters after recovery. Inactive resources collected on `ls_slow_inactive` are removed from the rhashtable and freed.

## State And Persistence
Recovery state is in-memory within `struct dlm_ls` and `struct dlm_rsb`: recovery status bits, waitqueues, lists, xarray ids, resource master fields, lock queue node ids/remids, LVB sequence/content, and flags. The recovered state persists for the lockspace lifetime.

## Dependencies And Integration Points
This file depends on rcom, directory hashing/lookup, lock queues, member lists, lowcomms close state, memory allocation for LVBs, and callback/AST behavior. It is orchestrated by `recoverd.c`.

## Risks
Incorrect wait predicates can hang recovery. Resource id tracking differs between list and xarray paths and must keep `ls_recover_list_count` consistent. LVB recovery is subtle: invalidating too often or choosing the wrong highest sequence changes user-visible lock value semantics. Recovery aborts must clear outstanding lists or references leak.

## Test Signals
Tests should cover failed master remapping, no-directory mode, RCOM lookup reply loss/timeout, lock-copy reply counting, recovery abort and restart, LVB selection among grant/convert queues, PR/CW conversion conflict repair, and inactive RSB cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recover.h -->
# sources/distributed-fs/ceph-client/fs/dlm/recover.h

## Purpose
`recover.h` declares the recovery wait, master, lock, RSB, and inactive-cleanup APIs used by the recovery daemon and recovery message handlers.

## Important APIs, Types, And Functions
The header exposes general wait/status functions, phase barriers for members/directory/locks/done, master recovery send/reply functions, lock recovery send/reply accounting, RSB finalization, and inactive cleanup.

## Control Flow
`recoverd.c` calls the phase functions in order. `rcom.c` calls reply entry points when lookup or lock recovery replies arrive. Lock and directory code consult recovery flags established by these APIs.

## State And Persistence
No header-owned state. Implementations mutate lockspace, resource, and lock state for the active recovery generation.

## Dependencies And Integration Points
The header connects recoverd, rcom, dir, lock, lowcomms, member, and ast code around a common recovery sequence.

## Risks
Callers must honor recovery phase order; calling lock recovery before directory/master recovery will operate on incomplete master data.

## Test Signals
Compile coverage and integration tests that drive full recovery sequences validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recoverd.c -->
# sources/distributed-fs/ceph-client/fs/dlm/recoverd.c

## Purpose
`recoverd.c` is the per-lockspace recovery kernel thread and high-level recovery orchestrator. It sequences membership updates, directory rebuild, master recovery, lock recovery, requestqueue draining, callback resume, and post-recovery grants.

## Important APIs, Types, And Functions
Externally visible functions are `dlm_recoverd_start()`, `dlm_recoverd_stop()`, `dlm_recoverd_suspend()`, and `dlm_recoverd_resume()`. Internal orchestration is in `ls_recover()`, `do_ls_recovery()`, `enable_locking()`, `dlm_recoverd()`, and root/master list helpers.

## Control Flow
The recoverd thread starts with `ls_in_recovery` held and `LSFL_RECOVER_LOCK` set. It sleeps until `LSFL_RECOVER_DOWN` or `LSFL_RECOVER_WORK` is set. Down events reacquire the recovery write lock and notify waiters. Work events call `do_ls_recovery()`.

`ls_recover()` suspends callbacks, clears inactive resources, snapshots active RSBs, recovers membership, computes directory node ids, snapshots locally mastered resources for directory copying, sets `DLM_RS_NODES`, waits for member/slot barrier, rebuilds directory, waits for directory barrier, prepares waiters, optionally purges locks and remasters resources on negative membership changes, recovers locks, finalizes RSBs, purges invalid requestqueue messages, sets done status, waits for done barrier, clears gone members, resumes callbacks, enables locking, drains saved messages, posts recovered waiters, grants now-eligible locks, and logs elapsed time.

Failures release root/master lists and return to wait for another recovery if interrupted. Non-interrupt errors complete `ls_recovery_done` so lockspace creation can observe critical failure.

## State And Persistence
State is per lockspace: recoverd task pointer, flags, recovery arguments, recovery result completion, root/master temporary lists, callback suspended state, requestqueue contents, and locking/recovery semaphores. Successful recovery updates persistent in-memory lockspace membership, directory, resource, and waiter state.

## Dependencies And Integration Points
It coordinates `member.c`, `recover.c`, `dir.c`, `lock.c`, `ast.c`, `requestqueue.c`, `lowcomms.c`, and lockspace user callbacks. It relies heavily on the recovery sequence number to avoid enabling stale recoveries.

## Risks
Recovery ordering is critical. Enabling locking before requestqueue state is stable could race with `dlm_recv`, so `enable_locking()` takes `ls_recv_active`. Root/master lists hold RSB refs and must be released on every failure path. Interrupt handling intentionally leaves recovery to be retried.

## Test Signals
Node join/leave tests should show ordered phase logs. Recovery abort/restart, requestqueue drain, callback suspension, and lock grant after recovery are key integration signals. Lockdep coverage is important for recovery locks and recv/requestqueue ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recoverd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recoverd.h -->
# sources/distributed-fs/ceph-client/fs/dlm/recoverd.h

## Purpose
`recoverd.h` declares the lifecycle and synchronization interface for the DLM recovery daemon thread.

## Important APIs, Types, And Functions
It exposes start/stop plus suspend/resume functions for a lockspace's recoverd task.

## Control Flow
Lockspace setup starts recoverd. Membership stop/start paths suspend or resume it around recovery state reset. Teardown stops the thread.

## State And Persistence
No header-owned state. The implementation stores the task pointer and recovery synchronization state in `struct dlm_ls`.

## Dependencies And Integration Points
Used by membership and lockspace code to coordinate recovery thread execution with lockspace stop/start.

## Risks
Suspend/resume must be balanced because it locks/unlocks `ls_recoverd_active`. Stopping recoverd while recovery lock is held must release `ls_in_recovery` correctly.

## Test Signals
Lockspace create/destroy and membership recovery tests should verify no stuck recoverd tasks or unreleased recovery locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/recoverd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/requestqueue.c -->
# sources/distributed-fs/ceph-client/fs/dlm/requestqueue.c

## Purpose
`requestqueue.c` stores normal DLM lock messages received while a lockspace is stopped for recovery, then replays or purges them after recovery makes normal locking safe again.

## Important APIs, Types, And Functions
The internal type is `struct rq_entry`, which stores the sending node, low 32 bits of the recovery sequence, and an inline copy of `struct dlm_message` plus extra payload. Exports are `dlm_add_requestqueue()`, `dlm_process_requestqueue()`, and `dlm_purge_requestqueue()`.

## Control Flow
`dlm_add_requestqueue()` copies a received message and appends it to `ls_requestqueue`. `dlm_process_requestqueue()` runs after locking is enabled, pops entries in FIFO order, logs message identifiers, calls `dlm_receive_message_saved()`, frees entries, and schedules between entries. If locking stops again, it aborts with `-EINTR`. When the queue drains it clears `LSFL_RECV_MSG_BLOCKED`.

`dlm_purge_requestqueue()` removes entries that are unsafe or invalid after recovery: messages from removed nodes, directory remove/lookup/lookup-reply messages, all messages if the lockspace is being freed, and all messages in no-directory mode.

## State And Persistence
Queued messages are heap-allocated and kept on `ls->ls_requestqueue` under `ls_requestqueue_lock`. They persist only across the active recovery window.

## Dependencies And Integration Points
The queue integrates with `dlm_ls_stop()`/`enable_locking()` in membership/recoverd, lock receive replay through `dlm_receive_message_saved()`, directory rebuild semantics, and errno conversion logging via `util.c`.

## Risks
The variable-length message copy depends on trusted `h_length`; callers should have already validated packet length. Purge policy is conservative for directory messages because directory contents are rebuilt. Replay under the requestqueue lock can interact with lock receive behavior, so comments describe expected blocking semantics.

## Test Signals
Test messages arriving during recovery, replay after recovery, purge after node removal, directory lookup resend behavior, no-directory mode purge, and recovery interruption while replay is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/requestqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/requestqueue.h -->
# sources/distributed-fs/ceph-client/fs/dlm/requestqueue.h

## Purpose
`requestqueue.h` declares the API for saving, processing, waiting on, and purging DLM messages queued during recovery.

## Important APIs, Types, And Functions
It declares `dlm_add_requestqueue()`, `dlm_process_requestqueue()`, `dlm_wait_requestqueue()`, and `dlm_purge_requestqueue()`.

## Control Flow
Receive code adds messages while locking is stopped; recoverd processes and purges the queue as recovery completes. `dlm_wait_requestqueue()` is declared here and implemented elsewhere in the lock receive path.

## State And Persistence
No header-owned state. Implementations operate on lockspace requestqueue lists and flags.

## Dependencies And Integration Points
Used by recoverd, member stop/start code, and lock receive code.

## Risks
The declared wait helper is not implemented in `requestqueue.c`, so readers must look elsewhere for the wait behavior. Queue APIs require the caller to understand recovery stop/running flags.

## Test Signals
Compile/link coverage plus recovery replay tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/requestqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/user.c -->
# sources/distributed-fs/ceph-client/fs/dlm/user.c

## Purpose
`user.c` implements the DLM userspace device ABI. It provides the `dlm-control` misc device for lockspace create/remove, per-lockspace misc devices for lock/unlock/deadlock/purge requests and AST reads, and a `dlm-monitor` device used to detect userspace daemon availability.

## Important APIs, Types, And Functions
Key exports are `dlm_user_add_ast()`, `dlm_user_init()`, `dlm_user_exit()`, `dlm_device_deregister()`, and `dlm_user_daemon_available()`. Important internal functions include compat translators, `device_write()`, `device_read()`, `device_open()`, `device_close()`, `device_create_lockspace()`, `device_remove_lockspace()`, `device_user_lock()`, `device_user_unlock()`, `device_user_deadlock()`, `device_user_purge()`, and `copy_result_to_user()`.

## Control Flow
Control-device writes create or remove lockspaces after `CAP_SYS_ADMIN` checks. Creating a lockspace calls `dlm_new_user_lockspace()`, finds the lockspace, registers a per-lockspace misc device named `dlm_<name>`, and returns the minor. Removing looks up by minor, optionally force-frees, and calls `dlm_release_lockspace()`.

Per-lockspace device open allocates `struct dlm_user_proc`, initializes AST/lock/unlocking lists and waitqueue, and holds a lockspace reference. Writes validate the device ABI version, handle compat 32-bit input when needed, reject operations after close starts, and dispatch to core user lock functions. Reads either return ABI version information or block until an AST/callback is available; callback data is copied as `struct dlm_lock_result` plus optional LVB bytes.

`dlm_user_add_ast()` is called from lock/AST code. It suppresses callbacks for orphan/dead locks, marks end-of-life locks after terminal completion statuses, obtains/skips callback records through `ast.c`, snapshots user args and optional LVB data, queues callbacks on the process AST list, wakes readers, and removes EOL locks from the process lock list.

Monitor-device open/close tracks whether `dlm_controld` is live. When the final monitor fd closes, `dlm_stop_lockspaces()` is invoked.

## State And Persistence
State is in misc-device registrations, per-open `dlm_user_proc` structures, queued `dlm_callback` records, per-process lock lists, monitor open counters, and per-lockspace device names. It is volatile kernel memory tied to open file and lockspace lifetimes.

## Dependencies And Integration Points
This file integrates with UAPI headers `linux/dlm_device.h` and `linux/dlm.h`, lockspace creation/lookup, lock operations in `lock.c`, AST helpers in `ast.c`, LVB operation policy, config cluster name, memory allocators, miscdevice, poll/waitqueue, compat ABI, and tracepoints.

## Risks
The userspace ABI has strict struct size/version rules and compat pointer translation. AST delivery races with process close are guarded by `ls_clear_proc_locks` and lock flags; mistakes can use freed `lkb_ua`. End-of-life lock removal must match terminal status semantics. Device registration failure after lockspace creation must release the lockspace.

## Test Signals
Test ABI version reads, 32-bit compat requests, lock/convert/unlock/cancel/deadlock/purge commands, blocking and nonblocking AST reads, LVB copy sizing, process close with outstanding locks, control-device permission checks, monitor open/close behavior, and daemon-availability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/user.h -->
# sources/distributed-fs/ceph-client/fs/dlm/user.h

## Purpose
`user.h` declares the DLM userspace-device entry points and AST bridge used by lock code.

## Important APIs, Types, And Functions
It declares callback purge/add helpers, userspace device init/exit, per-lockspace device deregistration, and daemon availability probing.

## Control Flow
Lock code calls `dlm_user_add_ast()` when a user lock has an AST/BAST to deliver. Module init/exit registers/unregisters misc devices. Lockspace teardown calls `dlm_device_deregister()`.

## State And Persistence
No header-owned state. Implementations mutate per-lockspace misc device state and per-open user process structures.

## Dependencies And Integration Points
Used by lock, lockspace, main, and AST code. `dlm_purge_lkb_callbacks()` is declared here and implemented in callback handling code rather than `user.c`.

## Risks
The AST interface assumes valid LKB and user-args lifetime. Device deregistration must be coordinated with lockspace references and open files.

## Test Signals
Compile/link coverage plus userspace lock ABI tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/util.c -->
# sources/distributed-fs/ceph-client/fs/dlm/util.c

## Purpose
`util.c` converts selected Linux negative errno values to stable architecture-independent DLM wire errno values and back.

## Important APIs, Types, And Functions
Exports are `to_dlm_errno(int err)` and `from_dlm_errno(int err)`. The file defines DLM wire constants for `EDEADLK`, `EBADR`, `EBADSLT`, `EPROTO`, `EOPNOTSUPP`, `ETIMEDOUT`, and `EINPROGRESS`.

## Control Flow
Both functions are switch-based mappings. Unknown errors pass through unchanged.

## State And Persistence
No mutable state. The constants define wire compatibility behavior for DLM messages.

## Dependencies And Integration Points
Lock reply senders call `to_dlm_errno()` before writing result fields to DLM messages. Receivers and requestqueue logging call `from_dlm_errno()` before interpreting or printing results.

## Risks
Only higher errno values known to vary across architectures are mapped. Adding new wire-visible errno values requires stable constant selection and peer compatibility consideration.

## Test Signals
Unit-style tests or compile-time checks can verify round-trip mapping for all listed errors and pass-through behavior for common low-numbered errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/util.h -->
# sources/distributed-fs/ceph-client/fs/dlm/util.h

## Purpose
`util.h` declares DLM errno conversion helpers.

## Important APIs, Types, And Functions
It exposes `to_dlm_errno()` and `from_dlm_errno()`.

## Control Flow
Callers convert before sending result codes on the wire and convert back after receiving them.

## State And Persistence
No state. The implementation's constants are part of DLM protocol compatibility.

## Dependencies And Integration Points
Included by lock, requestqueue, rcom, and other files that log or transmit DLM result codes.

## Risks
Forgetting to convert a wire-visible error can create architecture-dependent behavior in mixed clusters.

## Test Signals
Build coverage and cross-architecture protocol tests should validate the mapping remains consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/drop_caches.c -->
# sources/distributed-fs/ceph-client/fs/drop_caches.c

## Purpose
`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl. It lets privileged users request pagecache and/or slab reclaim for testing and operations.

## Important APIs, Types, And Functions
The file defines global `sysctl_drop_caches`, `drop_pagecache_sb()`, `drop_caches_sysctl_handler()`, the `drop_caches_table`, and initcall `init_vm_drop_caches_sysctls()`.

## Control Flow
Writing the sysctl is parsed by `proc_dointvec_minmax()` with allowed values 1 through 4. Bit 1 drains LRU additions, iterates all superblocks, and invalidates inode mappings through `drop_pagecache_sb()`. Bit 2 calls `drop_slab()`. Bit 4 suppresses future informational logging. Successful pagecache/slab drops increment `DROP_PAGECACHE` and `DROP_SLAB` VM events.

`drop_pagecache_sb()` scans each superblock inode list under `s_inode_list_lock`, skips freeing/new inodes and empty mappings unless rescheduling is needed, takes an inode reference before dropping the list lock, invalidates mapping pages, drops the previous inode reference, calls `cond_resched()`, and resumes the scan.

## State And Persistence
The sysctl integer and static `stfu` flag are in-memory kernel state. Cache contents are not persistent; writing this sysctl intentionally discards reclaimable cache state.

## Dependencies And Integration Points
It integrates with sysctl registration, VFS superblock/inode lists, pagecache invalidation, slab reclaim, scheduler rescheduling, VM event counters, and filesystem initcalls.

## Risks
Dropping caches can cause large performance disruption and lock contention while scanning inode lists. The code avoids unusual inode states and holds references carefully, but it still depends on VFS locking correctness. The log suppression bit changes future observability.

## Test Signals
Manual sysctl writes with values 1, 2, 3, and 4 should update VM counters and logs as expected. Stress tests should verify no inode reference leaks or lockdep issues while filesystems are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/drop_caches.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the eCryptfs filesystem layer and optional userspace key wrap/unwrap messaging support.

## Important APIs, Types, And Functions
It defines `CONFIG_ECRYPT_FS` as a tristate depending on `KEYS`, `CRYPTO`, and either `ENCRYPTED_KEYS` enabled or absent. It selects ECB, CBC, MD5 library crypto support. It also defines boolean `CONFIG_ECRYPT_FS_MESSAGING`, dependent on `ECRYPT_FS`.

## Control Flow
At kernel configuration time, enabling `ECRYPT_FS` builds the eCryptfs filesystem built-in or as module `ecryptfs`. Enabling messaging adds `/dev/ecryptfs` support for the ecryptfs daemon to wrap or unwrap file encryption keys via userspace backends.

## State And Persistence
Kconfig symbols persist in the kernel build configuration, not at runtime. They control which object files and runtime interfaces exist.

## Dependencies And Integration Points
Integrated with the crypto subsystem, key management, encrypted keys, documentation, and the eCryptfs Makefile. `ECRYPT_FS_MESSAGING` controls compilation of `messaging.o` and `miscdev.o`.

## Risks
Selecting legacy crypto modes such as ECB/CBC and MD5 reflects eCryptfs format needs; disabling dependencies removes the filesystem option. Messaging support creates a userspace device surface and depends on an external daemon.

## Test Signals
Configuration tests should cover built-in, module, disabled, and messaging-enabled builds. Runtime smoke tests should mount eCryptfs and, with messaging enabled, verify `/dev/ecryptfs` userspace interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/Makefile

## Purpose
The eCryptfs Makefile maps Kconfig symbols to compiled object lists for the eCryptfs filesystem.

## Important APIs, Types, And Functions
It builds `ecryptfs.o` when `CONFIG_ECRYPT_FS` is enabled. The composite object includes `dentry.o`, `file.o`, `inode.o`, `main.o`, `super.o`, `mmap.o`, `read_write.o`, `crypto.o`, `keystore.o`, `kthread.o`, and `debug.o`. With `CONFIG_ECRYPT_FS_MESSAGING`, it also includes `messaging.o` and `miscdev.o`.

## Control Flow
Kernel kbuild uses `obj-$(CONFIG_ECRYPT_FS)` to decide whether to build the filesystem and `ecryptfs-y`/`ecryptfs-$(CONFIG_ECRYPT_FS_MESSAGING)` to assemble the module or built-in composite.

## State And Persistence
The file has no runtime state. It controls build artifacts based on the kernel configuration.

## Dependencies And Integration Points
It is paired with the eCryptfs Kconfig and the source files in `fs/ecryptfs`. Messaging object inclusion must match the optional Kconfig symbol.

## Risks
Omitting an object from `ecryptfs-y` can create unresolved symbols or missing functionality. Adding optional code without guarding it by the correct config symbol can break disabled-message builds.

## Test Signals
Build eCryptfs as built-in and module, with and without messaging, and verify no missing symbols and expected module contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/Makefile -->
