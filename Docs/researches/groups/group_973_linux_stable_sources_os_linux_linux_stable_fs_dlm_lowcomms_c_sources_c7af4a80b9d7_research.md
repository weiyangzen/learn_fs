# Group Research: group_973_linux_stable_sources_os_linux_linux_stable_fs_dlm_lowcomms_c_sources_c7af4a80b9d7

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lowcomms.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lowcomms.c

## Purpose
`lowcomms.c` is the DLM low-level transport layer. It owns kernel sockets, peer address mapping, connection setup/teardown, send buffering, receive buffering, and delivery of complete byte-stream messages to `midcomms`.

It supports TCP and SCTP through `dlm_proto_ops`, selected by `dlm_config.ci_protocol`.

## Core State
- `struct connection`: per-node transport state, including socket, address list, socket mark, write queue, receive leftovers, work items, shutdown waitqueue, and optional `othercon`.
- `struct writequeue_entry`: page-backed outgoing buffer containing one or more `struct dlm_msg` records.
- `struct dlm_msg`: lowcomms message handle with kref lifetime, committed page location, retransmit state, and SRCU index exchange.
- `struct processqueue_entry`: buffered complete incoming bytes queued for DLM processing.

Connections are stored in `connection_hash[CONN_HASH_SIZE]` under SRCU with `connections_lock` protecting hash mutations.

## Receive Path
Socket callbacks queue work:
- `lowcomms_data_ready()` sets `CF_RECV_INTR` and queues receive work.
- `lowcomms_write_space()` clears app-limited send state and queues send work.
- `lowcomms_listen_data_ready()` queues accept work.

`receive_from_sock()` reads nonblocking from the socket, prepends `rx_leftover_buf`, calls `dlm_validate_incoming_buffer()` to find complete messages, stores incomplete tail bytes, and queues `process_dlm_messages()` on `process_workqueue`.

The process queue is bounded with `DLM_MAX_PROCESS_BUFFERS`; when it grows too large, receive work waits for the process queue to drain.

## Send Path
Callers use `dlm_lowcomms_new_msg()` to reserve a message buffer, fill it, then must call `dlm_lowcomms_commit_msg()`. Messages are packed into page-backed writequeue entries.

`send_to_sock()` sends with `MSG_SPLICE_PAGES | MSG_DONTWAIT | MSG_NOSIGNAL`. Partial sends mark an entry dirty. On reconnect, a dirty first entry is dropped so the peer cannot receive the tail of a half-sent DLM message.

`dlm_lowcomms_resend_msg()` duplicates a committed message for midcomms retransmission and marks the original as retransmitting.

## Connection Handling
`dlm_lowcomms_addr()` registers peer addresses and creates connection objects. `nodeid_to_addr()` and `addr_to_nodeid()` translate configured addresses to node ids and socket marks.

`accept_from_sock()` matches incoming sockets to configured peers. If an active socket already exists, the accepted socket is placed in `othercon` to preserve compatibility with crossed simultaneous connects.

`dlm_connect()` creates a kernel socket, applies TCP/SCTP options, binds local cluster addresses, installs callbacks, and calls `kernel_connect()`.

## Protocol Variants
- TCP binds only the first local address and warns when multiple local addresses exist.
- SCTP binds all local addresses, requests the SCTP module, sets a larger receive buffer, and cycles peer addresses.
- TCP shutdown uses `SHUT_WR`; SCTP uses `SHUT_RDWR`.

## Shutdown and Cleanup
`dlm_lowcomms_shutdown()` stops the listener callback, closes the listener, shuts down every peer connection, drains workqueues, closes sockets, cleans write queues, and re-enables connection I/O flags.

`dlm_lowcomms_close()` is called when recovery/fencing knows a node has left. It stops I/O, closes sockets, removes the connection from the SRCU hash, cleans queued messages, and defers freeing through `call_srcu()`.

## Risks and Notes
Correctness depends on message boundary preservation, kref/SRCU lifetime pairing, callback restoration before socket release, and ordering between close/shutdown/workqueue cancellation. `othercon` is explicitly compatibility debt and recursively stopped/closed with the primary connection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lowcomms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lowcomms.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lowcomms.h

## Purpose
`lowcomms.h` declares the DLM low-level socket transport API used primarily by `midcomms.c`, recovery, membership, and memory-cache setup.

## Exports
- Lifecycle: `dlm_lowcomms_start()`, `dlm_lowcomms_shutdown()`, `dlm_lowcomms_stop()`, `dlm_lowcomms_init()`, `dlm_lowcomms_exit()`.
- Node/socket control: `dlm_lowcomms_close()`, `dlm_lowcomms_connect_node()`, `dlm_lowcomms_nodes_set_mark()`, `dlm_lowcomms_addr()`.
- Message API: `dlm_lowcomms_new_msg()`, `dlm_lowcomms_commit_msg()`, `dlm_lowcomms_put_msg()`, `dlm_lowcomms_resend_msg()`.
- Cache factories: `dlm_lowcomms_writequeue_cache_create()`, `dlm_lowcomms_msg_cache_create()`.

## Definitions
- `DLM_MIDCOMMS_OPT_LEN` reserves space for `struct dlm_opts`.
- `DLM_MAX_APP_BUFSIZE` subtracts midcomms option overhead from socket-buffer capacity.
- `CONN_HASH_SIZE` is 32.
- `nodeid_hash()` maps node ids with `nodeid & (CONN_HASH_SIZE - 1)`.

## Notes
The header also declares `dlm_lowcomms_shutdown_node()` and `dlm_midcomms_receive_done()`, but these declarations have no matching definitions in this source tree. They appear to be stale API leftovers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lowcomms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lvb_table.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lvb_table.h

## Purpose
`lvb_table.h` declares the global lock-value-block transition table.

## Export
- `extern const int dlm_lvb_operations[8][8];`

## Use
The table is consumed by DLM lock/user/callback logic to decide how lock value blocks are copied, invalidated, or ignored across lock-mode transitions.

## Notes
This file is declaration-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lvb_table.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/main.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/main.c

## Purpose
`main.c` is the DLM module entry/exit file. It establishes subsystem initialization and teardown ordering.

## Initialization
`init_dlm()` initializes:
1. DLM memory caches.
2. Midcomms/lowcomms data structures.
3. Lockspace subsystem.
4. Config subsystem.
5. Debugfs.
6. User devices.
7. POSIX-lock device.
8. Shared `dlm_wq`.

On failure, it unwinds initialized components in reverse order.

## Exit
`exit_dlm()` destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms/debugfs, and then destroys memory caches.

## Exports
Exports the public kernel DLM API:
- `dlm_new_lockspace`
- `dlm_release_lockspace`
- `dlm_lock`
- `dlm_unlock`

## Notes
The file is ordering-focused rather than protocol-heavy. Destroying `dlm_wq` first ensures pending freeing/callback work is complete before subsystem teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/member.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/member.c

## Purpose
`member.c` manages DLM lockspace membership across recovery cycles. It tracks current members, removed members, slot assignments, node weights, low-node coordination, and midcomms membership notifications.

## Slot Handling
Slot helpers support recovery-time slot negotiation:
- `dlm_slots_version()` checks whether a peer supports slot fields.
- `dlm_slot_save()` records a member slot/generation from RCOM status replies.
- `dlm_slots_copy_out()` serializes local slots into an RCOM reply.
- `dlm_slots_copy_in()` imports the low-node slot map.
- `dlm_slots_assign()` assigns stable slots when the local node is the low nodeid.

Slot assignment preserves prior slots, rejects unexpected slot changes, increments generation, logs slot maps, and verifies the serialized slot list fits in `DLM_MAX_APP_BUFSIZE`.

## Membership Lists
Active members are stored in `ls_nodes`, ordered by nodeid. Removed members are moved to `ls_nodes_gone` until recovery finishes.

Important helpers:
- `dlm_is_member()`
- `dlm_is_removed()`
- `dlm_clear_members()`
- `dlm_clear_members_gone()`

`dlm_add_member()` allocates a `struct dlm_member`, starts remote communication for nonlocal nodes, records weight/comm sequence, and inserts it.

## Weighted Directory Mapping
`make_member_array()` creates `ls_node_array` using configured member weights. If all weights are zero, each member is treated as weight 1. This array feeds directory/master hash placement.

## Recovery Integration
`dlm_recover_members()` reconciles config-layer recovery input with current state:
- Counts prior removed nodes as negative recovery.
- Moves departed or re-added members to `ls_nodes_gone`.
- Notifies midcomms and lockspace ops for removals.
- Adds new members.
- Recomputes `ls_low_nodeid`.
- Rebuilds the weighted node array.
- Pings members with status RCOMs to establish communication.

## Lockspace Stop/Start
`dlm_ls_stop()` blocks normal receive/message processing, sets recovery stop flags, clears running state, activates request queue blocking, waits for recovery ownership, suspends/resumes recoverd, clears slot state, and calls optional `recover_prep`.

`dlm_ls_start()` reads config nodes, creates a new `struct dlm_recover` with a fresh sequence, stores it as `ls_recover_args`, and wakes recoverd.

## Risks and Notes
Membership change reporting must not abort early because lockspace ops and midcomms must observe every add/remove. `ls_recv_active`, `ls_recover_lock`, and `ls_requestqueue_lock` are central to avoiding receive/recovery races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/member.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/member.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/member.h

## Purpose
`member.h` declares DLM membership and slot-management APIs.

## Exports
- Lockspace transitions: `dlm_ls_stop()`, `dlm_ls_start()`.
- Membership cleanup: `dlm_clear_members()`, `dlm_clear_members_gone()`.
- Recovery reconciliation: `dlm_recover_members()`.
- Queries: `dlm_is_removed()`, `dlm_is_member()`.
- Slot protocol: `dlm_slots_version()`, `dlm_slot_save()`, `dlm_slots_copy_out()`, `dlm_slots_copy_in()`, `dlm_slots_assign()`.
- Lockspace-op callback bridge: `dlm_lsop_recover_done()`.

## Notes
The declarations map directly to `member.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/member.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/memory.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/memory.c

## Purpose
`memory.c` centralizes DLM allocation through slab caches and RCU-delayed frees.

## Cache Lifecycle
`dlm_memory_init()` creates caches for:
- lowcomms writequeue entries
- midcomms message handles
- lowcomms messages
- lock blocks (`dlm_lkb`)
- resource blocks (`dlm_rsb`)
- callbacks (`dlm_callback`)

Failures unwind already-created caches. `dlm_memory_exit()` calls `rcu_barrier()` before destroying caches so deferred frees have completed.

## Allocation Helpers
The file provides typed allocate/free wrappers for:
- RSBs and LKBs
- LVB buffers
- midcomms handles
- lowcomms writequeue entries
- lowcomms messages
- callbacks

RSBs and LKBs are freed with `call_rcu()`. RSB free releases `res_lvbptr`. LKB free releases user arguments and user LVB state for `DLM_DFL_USER_BIT` locks.

## Notes
Most allocation wrappers use `GFP_ATOMIC`, matching DLM use from spinlocked or recovery-sensitive contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/memory.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/memory.h

## Purpose
`memory.h` declares DLM memory-cache lifecycle and typed object allocation APIs.

## Exports
- Lifecycle: `dlm_memory_init()`, `dlm_memory_exit()`.
- Object allocation/free: RSB, LKB, LVB, mhandle, writequeue entry, lowcomms message, callback.

## Notes
The header hides cache implementation details from the rest of DLM while preserving typed allocation calls.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/midcomms.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/midcomms.c

## Purpose
`midcomms.c` implements DLM’s mid-level communication reliability layer above lowcomms sockets. For protocol 3.2 peers it adds sequence numbers, ACKs, retransmission of unacknowledged messages, version detection, and a DLM-level FIN handshake.

## Core State
`struct midcomms_node` tracks per-node state:
- protocol version
- send and receive sequence counters
- unacknowledged send queue
- delivered-message ACK thresholds
- close/stop flags
- shutdown waitqueue
- reduced TCP-like termination state
- lockspace user count
- debugfs state

Nodes are stored in `node_hash[CONN_HASH_SIZE]` under SRCU.

`struct dlm_mhandle` wraps a lowcomms message and, for protocol 3.2, records the `struct dlm_opts` outer header, inner packet pointer, sequence number, ACK callback, and send-queue linkage.

## Version Detection
Version is inferred from early RCOM traffic:
- 3.1 messages are processed without the reliable wrapper.
- 3.2 messages use `DLM_OPTS` wrappers, ACKs, retransmit queues, and FIN messages.

The code treats RCOM status/names traffic specially because those recovery messages have their own retransmission behavior and are used for compatibility/version setup.

## Receive Path
`dlm_validate_incoming_buffer()` validates outer message lengths and returns the number of complete bytes available.

`dlm_process_incoming_buffer()` walks complete messages and dispatches by protocol version:
- `dlm_midcomms_receive_buffer_3_1()`
- `dlm_midcomms_receive_buffer_3_2()`

For 3.2:
- `DLM_OPTS` extracts the inner message and sequence.
- Expected sequence numbers are delivered to `dlm_receive_buffer()`.
- Duplicate/old sequence numbers are ACKed again.
- Unexpected future sequence numbers are ignored and logged.
- `DLM_ACK` removes acked messages from the send queue.
- `DLM_FIN` drives termination state.

## Send Path
`dlm_midcomms_get_mhandle()` allocates a message handle. For 3.2, it reserves `DLM_MIDCOMMS_OPT_LEN`, inserts the handle into the send queue, assigns a sequence, and returns the inner payload pointer.

`dlm_midcomms_commit_mhandle()` commits through lowcomms. For 3.2, it sets `o_nextcmd`, marks the handle committed, emits tracepoints, and relies on ACK processing to delete the mhandle.

`dlm_midcomms_unack_msg_resend()` walks committed unacknowledged messages and asks lowcomms to duplicate them after socket errors/reconnects.

## Termination
The file implements a DLM-level four-way FIN/ACK shutdown state machine using states:
- `DLM_CLOSED`
- `DLM_ESTABLISHED`
- `DLM_FIN_WAIT1`
- `DLM_FIN_WAIT2`
- `DLM_CLOSE_WAIT`
- `DLM_LAST_ACK`
- `DLM_CLOSING`

This is needed because SCTP lacks TCP-style half-close semantics and because lowcomms supports `othercon` compatibility sockets.

## Membership Integration
- `dlm_midcomms_add_member()` increments node use and moves closed nodes to established state.
- `dlm_midcomms_remove_member()` decrements use and can trigger passive FIN when the node is no longer used.
- `dlm_midcomms_shutdown()` actively shuts down all nodes, calls lowcomms shutdown, then resets node state.
- `dlm_midcomms_close()` aborts waiters, closes lowcomms state, removes debugfs/node hash entries, flushes queued messages, and defers freeing.

## Debug Raw Message Path
`dlm_midcomms_rawmsg_send()` lets debugfs send a raw DLM message through lowcomms. `midcomms_new_rawmsg_cb()` may fill a missing sequence number for wrapped messages.

## Risks and Notes
This file is protocol-sensitive. Known issues are documented in comments: unaligned message payloads, limited version-detection compatibility, incomplete tail-size validation for some payloads, and future fencing hooks for bad sequence behavior/timeouts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/midcomms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/midcomms.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/midcomms.h

## Purpose
`midcomms.h` declares the DLM mid-level communications API.

## Exports
- Incoming validation/processing: `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`.
- Send handle API: `dlm_midcomms_get_mhandle()`, `dlm_midcomms_commit_mhandle()`.
- Node address/version/lifecycle: `dlm_midcomms_addr()`, `dlm_midcomms_version_wait()`, `dlm_midcomms_close()`, `dlm_midcomms_start()`, `dlm_midcomms_stop()`, `dlm_midcomms_init()`, `dlm_midcomms_exit()`, `dlm_midcomms_shutdown()`.
- Membership notifications: `dlm_midcomms_add_member()`, `dlm_midcomms_remove_member()`.
- Retransmit: `dlm_midcomms_unack_msg_resend()`.
- Debugfs state readers and raw send.
- Cache factory: `dlm_midcomms_cache_create()`.

## Notes
`struct midcomms_node` is intentionally opaque outside midcomms/debugfs helper use.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/midcomms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/plock.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/plock.c

## Purpose
`plock.c` implements DLM-assisted POSIX file locking. It forwards lock/unlock/get/cancel operations to userspace `dlm_controld` through a misc device and mirrors successful locks into the local VFS lock state.

## Core State
- `send_list`: operations waiting for userspace to read.
- `recv_list`: operations sent to userspace and waiting for a reply.
- `ops_lock`: protects both lists.
- `send_wq` and `recv_wq`: wake readers and waiting kernel callers.
- `struct plock_op`: one operation plus `dlm_plock_info` and optional async data.
- `struct plock_async_data`: saved `file_lock`, callback, and file pointer for async lock handling.

## Kernel API
Exports:
- `dlm_posix_lock()`
- `dlm_posix_unlock()`
- `dlm_posix_cancel()`
- `dlm_posix_get()`

`dlm_posix_lock()` sends a lock request. Blocking calls wait on `recv_wq`; interruptible waits try to send a cancel request. Async locks with `fl_lmops->lm_grant` return `FILE_LOCK_DEFERRED`.

`dlm_posix_unlock()` first unlocks locally through VFS, then sends an unlock to userspace unless it is a close-generated unlock that does not need a reply.

`dlm_posix_cancel()` currently only supports async requests and relies on userspace cancel synchronization.

`dlm_posix_get()` asks userspace for conflicting lock information and converts positive conflict results into a `struct file_lock`.

## Misc Device
`dlm_plock_init()` registers the `DLM_PLOCK_MISC_NAME` misc device. Its operations are:
- `dev_read()`: userspace reads one pending operation from `send_list`.
- `dev_write()`: userspace writes one result matching an operation on `recv_list`.
- `dev_poll()`: signals when operations are available.

Waiting lock replies can arrive out of order and are matched by all lock identity fields. Non-waiting replies are matched to the first non-waiting op for the same filesystem id.

## Risks and Notes
The async callback path logs a “dangling lock” warning if a granted lock notification fails after local state is updated. Comments explicitly note cancellation limitations for non-async waiting requests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/plock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/rcom.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/rcom.c

## Purpose
`rcom.c` implements DLM recovery communication messages: status, directory-name transfer, master lookup, lock-copy transfer, and replies.

## Message Creation
- `create_rcom()` creates recovery messages through midcomms, using reliable 3.2 handling when available.
- `create_rcom_stateless()` sends directly through lowcomms for status messages used by version detection and recovery polling.
- `_create_rcom()` fills the common `struct dlm_rcom` header.

## Status and Config
`dlm_rcom_status()` sends status requests and waits synchronously for replies through `ls_recover_buf`. It retries on timeout and verifies remote config compatibility with `check_rcom_config()`.

Status replies include:
- recovery status bits
- LVB length
- lockspace flags
- local slot/generation data
- optional serialized slot map when requested

`dlm_send_ls_not_ready()` sends an `-ESRCH` status reply when a lockspace does not yet exist or is not ready.

## Directory Recovery
`dlm_rcom_names()` requests chunks of master resource names from another node. `receive_rcom_names()` calls `dlm_copy_master_names()` to fill the reply with directory-rebuild records.

## Master Lookup Recovery
`dlm_send_rcom_lookup()` sends a resource-name lookup to a directory node. `receive_rcom_lookup()` calls `dlm_master_lookup(..., DLM_LU_RECOVER_MASTER, ...)` and replies with the selected master node. `receive_rcom_lookup_reply()` passes replies to `dlm_recover_master_reply()`.

## Lock Recovery
`dlm_send_rcom_lock()` serializes a process-copy lock into `struct rcom_lock`, including modes, ids, flags, AST availability, resource name, and optional LVB bytes.

`receive_rcom_lock()` calls `dlm_recover_master_copy()` to rebuild master-copy state, then replies with remid/result. `DLM_RCOM_LOCK_REPLY` is handled by `dlm_recover_process_copy()`.

## Receive Filtering
`dlm_receive_rcom()` filters recovery messages by:
- current stop state
- recovery sequence
- recovery phase status bits
- message type
- minimum length for lock-copy messages

It ignores messages that arrive too early for the local recovery phase, logging limited diagnostics.

## Risks and Notes
Synchronous reply state uses `ls_rcom_seq`, `LSFL_RCOM_WAIT`, `LSFL_RCOM_READY`, and `ls_recover_buf`. Correctness depends on sequence checks and phase gating so stale recovery replies cannot mutate current recovery state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/rcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/rcom.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/rcom.h

## Purpose
`rcom.h` declares the DLM recovery-communication API.

## Exports
- `dlm_rcom_status()`
- `dlm_rcom_names()`
- `dlm_send_rcom_lookup()`
- `dlm_send_rcom_lock()`
- `dlm_receive_rcom()`
- `dlm_send_ls_not_ready()`

## Notes
The header is used by recovery, directory, lock, and receive paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/rcom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recover.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/recover.c

## Purpose
`recover.c` implements core DLM recovery helpers: recovery barriers, master remapping, lock-copy replay, LVB recovery, conversion repair, inactive RSB cleanup, and recovery-status coordination.

## Wait and Barrier Helpers
`dlm_wait_function()` waits for a condition or recovery stop, with periodic timeout checks and `LSFL_RCOM_WAIT` timeout handling.

Recovery barrier helpers use the low-node protocol:
- Low node polls all members for a status.
- Non-low nodes poll the low node for the `_ALL` status bit.
- Status stages include nodes, directory, locks, and done.

`dlm_recover_members_wait()` also coordinates slot assignment/copying.

## Recovery Tracking Structures
Two mechanisms track outstanding recovery work:
- `ls_recover_list` for RSBs waiting on recovered lock replies.
- `ls_recover_xa` for RSBs waiting on async master lookup replies, keyed by temporary ids.

Both hold RSB references while work is pending and clear state on errors.

## Master Recovery
`dlm_recover_masters()` walks the recovery root list. For RSBs mastered by removed nodes, it either:
- assigns static masters in no-directory mode, or
- sends async RCOM lookup requests to directory nodes.

Replies are handled by `dlm_recover_master_reply()`, which updates `res_master_nodeid`, `res_nodeid`, and marks RSBs as new masters.

## Lock Recovery
`dlm_recover_locks()` sends local process-copy locks for remastered RSBs to their new masters. It counts outgoing locks per RSB and waits until all replies are processed.

`dlm_recovered_lock()` decrements the per-RSB count, clears `RSB_NEW_MASTER`, removes the RSB from the recover list, and wakes the general waitqueue when complete.

## RSB Finalization
`dlm_recover_rsbs()` finalizes master RSB state:
- fixes incompatible PR/CW conversion recovery with `recover_conversion()`
- recovers or invalidates lock value blocks with `recover_lvb()`
- marks resources needing grant processing with `recover_grant()`
- clears recovery flags

`recover_lvb()` chooses LVB content from the strongest granted/converting lock with LVB data, or the highest LVB sequence among NL/CR locks, and sets `RSB_VALNOTVALID` where appropriate.

## Inactive Cleanup
`dlm_clear_inactive()` removes all inactive/tossed RSBs from the hash table and scan lists before recovery rebuilds current state.

## Risks and Notes
The file is highly recovery-order dependent. The comments explain why all MSTCPY locks are purged/rebuilt even when a master remains the same: aborted recoveries can otherwise make waiters unable to distinguish valid replies from stale replies.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recover.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/recover.h

## Purpose
`recover.h` declares recovery helpers used by recoverd, RCOM, lock, and membership code.

## Exports
- Wait/status helpers: `dlm_wait_function()`, `dlm_recover_status()`, `dlm_set_recover_status()`.
- Barrier waits: members, directory, locks, done.
- Master recovery: `dlm_recover_masters()`, `dlm_recover_master_reply()`.
- Lock recovery: `dlm_recover_locks()`, `dlm_recovered_lock()`.
- RSB cleanup/finalization: `dlm_clear_inactive()`, `dlm_recover_rsbs()`.

## Notes
The header exposes only recovery-stage orchestration, not lower-level RSB list internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recover.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recoverd.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/recoverd.c

## Purpose
`recoverd.c` implements the per-lockspace recovery kernel thread and orchestrates the full DLM recovery sequence.

## Recovery Flow
`ls_recover()` performs:
1. Suspend callbacks.
2. Clear inactive RSBs.
3. Snapshot active RSBs into a root list.
4. Reconcile membership.
5. Recompute directory node ids.
6. Snapshot locally mastered RSBs for directory rebuild.
7. Set and wait for node recovery status.
8. Rebuild directory from peer master-name dumps.
9. Mark outstanding waiters before recovery.
10. If negative membership change or no-directory mode: purge, recover masters, recover locks, wait for lock barrier, recover RSB state.
11. Release root list.
12. Purge invalid queued directory requests.
13. Set/wait done barrier.
14. Clear removed-member list.
15. Resume callbacks.
16. Re-enable locking.
17. Process queued normal messages.
18. Recover waiters post-recovery.
19. Grant pending locks.

## Root and Master Lists
`dlm_create_root_list()` snapshots all active RSBs and holds references. `dlm_create_masters_list()` snapshots RSBs mastered locally for directory-name transfer during recovery.

Both lists are explicitly released after use.

## Locking Re-enable
`enable_locking()` only re-enables if the recovery sequence still matches. It sets `LSFL_RUNNING`, resumes the scan timer, releases `ls_in_recovery`, and clears `LSFL_RECOVER_LOCK`.

It holds `ls_recv_active` to avoid races with receive threads adding messages to the request queue while recoverd drains it.

## Recoverd Thread
`dlm_recoverd()` owns `ls_in_recovery` during stopped periods and wakes on:
- `LSFL_RECOVER_DOWN`
- `LSFL_RECOVER_WORK`
- kthread stop

`do_ls_recovery()` consumes `ls_recover_args`, clears `LSFL_RECOVER_STOP` only if the sequence still matches, records success or critical errors, completes `ls_recovery_done`, and calls lockspace `recover_done` ops on success.

## Risks and Notes
Recovery is intentionally non-abortable until membership changes have been reported to lockspace ops and midcomms. Later phases abort on `-EINTR` and wait for a newer recovery cycle.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recoverd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recoverd.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/recoverd.h

## Purpose
`recoverd.h` declares per-lockspace recovery-thread lifecycle helpers.

## Exports
- `dlm_recoverd_start()`
- `dlm_recoverd_stop()`
- `dlm_recoverd_suspend()`
- `dlm_recoverd_resume()`

## Notes
Suspend/resume is used by membership stop logic to ensure recoverd has noticed abort flags before state is reset.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/recoverd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/requestqueue.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/requestqueue.c

## Purpose
`requestqueue.c` saves normal DLM messages received while a lockspace is in recovery and replays or purges them after recovery reaches a safe point.

## Queue Entries
`struct rq_entry` stores:
- list linkage
- low 32 bits of recovery sequence
- sender node id
- copied `struct dlm_message` plus extra payload bytes

`dlm_add_requestqueue()` copies a received message into an allocated queue entry using the message header length.

## Replay
`dlm_process_requestqueue()` runs after locking is re-enabled. It processes entries in order through `dlm_receive_message_saved()`, then frees them. It clears `LSFL_RECV_MSG_BLOCKED` once the queue is empty.

The function drops and reacquires `ls_requestqueue_lock` between entries to avoid monopolizing CPU, but aborts if locking becomes stopped again.

## Purge
`dlm_purge_requestqueue()` removes messages invalidated by recovery:
- messages for removed nodes
- messages during lockspace teardown
- directory operations (`REMOVE`, `LOOKUP`, `LOOKUP_REPLY`)
- all messages in no-directory mode

## Risks and Notes
The comments describe a race with `dlm_recv` and `dlm_ls_stop()` while saved messages drain. The code keeps receive-side blocking state explicit with `LSFL_RECV_MSG_BLOCKED`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/requestqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/requestqueue.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/requestqueue.h

## Purpose
`requestqueue.h` declares recovery-time request queue helpers.

## Exports
- `dlm_add_requestqueue()`
- `dlm_process_requestqueue()`
- `dlm_wait_requestqueue()`
- `dlm_purge_requestqueue()`

## Notes
`dlm_wait_requestqueue()` is declared here but not defined in the listed source file; it is either defined elsewhere in the DLM tree or a stale declaration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/requestqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/user.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/user.c

## Purpose
`user.c` implements the userspace DLM misc-device interface. It lets userspace create/remove lockspaces, issue lock/unlock/cancel/deadlock/purge commands, and read AST/BAST completion events.

## Device Model
The file registers:
- `dlm-control`: control device for creating/removing lockspaces and reading version.
- `dlm-monitor`: monitor device used to detect daemon availability and stop lockspaces when the monitor closes.
- Per-lockspace devices named `dlm_<lockspace>`.

Each opener of a lockspace device gets a `struct dlm_user_proc` that tracks owned locks and pending callbacks for that process.

## User Request Handling
`device_write()` validates request size/version, handles compat conversion when needed, rejects lock operations on closing processes, and dispatches:
- `DLM_USER_LOCK`
- `DLM_USER_UNLOCK`
- `DLM_USER_DEADLOCK`
- `DLM_USER_CREATE_LOCKSPACE`
- `DLM_USER_REMOVE_LOCKSPACE`
- `DLM_USER_PURGE`

Lock requests allocate `struct dlm_user_args` and call lower lock-layer helpers:
- `dlm_user_request()`
- `dlm_user_convert()`
- `dlm_user_adopt_orphan()`
- `dlm_user_unlock()`
- `dlm_user_cancel()`
- `dlm_user_deadlock()`
- `dlm_user_purge()`

## Callback Delivery
`dlm_user_add_ast()` queues user-visible callbacks unless the lock is orphaned/dead or the callback can be skipped. It copies callback state into `struct dlm_callback`, optionally copies LVB data, wakes the process waitqueue, and removes end-of-life locks from the process lock list.

A lock becomes end-of-life for noqueue failures, unlock completion, and cancel/deadlock/timeout cases involving an IV-mode request.

`device_read()` returns one callback as `struct dlm_lock_result`, optionally followed by LVB bytes. Reads of exactly `struct dlm_device_version` return only version information.

## Process Lifecycle
`device_open()` creates a `dlm_user_proc` and takes a lockspace reference. `device_close()` marks the proc closing, calls `dlm_clear_proc_locks()`, frees proc state, and drops both the open-time and local lookup references.

## Compat Support
Under `CONFIG_COMPAT`, the file converts 32-bit write requests and lock results to/from native structures, including user pointer fields.

## Daemon Availability
`dlm_user_daemon_available()` reports availability based on configured local node id and whether the monitor device is opened, while preserving compatibility with older `dlm_controld` that never opened the monitor.

## Risks and Notes
The user path is sensitive to callback lifetime: `ls_clear_proc_locks` prevents AST delivery from racing with process cleanup. Device input size/version checks are the primary boundary for userspace command parsing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/user.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/user.h

## Purpose
`user.h` declares userspace-device integration points for DLM.

## Exports
- `dlm_purge_lkb_callbacks()`
- `dlm_user_add_ast()`
- `dlm_user_init()`
- `dlm_user_exit()`
- `dlm_device_deregister()`
- `dlm_user_daemon_available()`

## Notes
`dlm_purge_lkb_callbacks()` is declared here but is not defined in the listed `user.c`; it may be implemented elsewhere in DLM or be a stale declaration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/util.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/util.c

## Purpose
`util.c` provides wire-stable errno translation for DLM protocol messages.

## Behavior
Higher errno values differ across architectures, so DLM maps selected Linux errno values to fixed numeric DLM errno constants before sending them on the wire:
- `EDEADLK`
- `EBADR`
- `EBADSLT`
- `EPROTO`
- `EOPNOTSUPP`
- `ETIMEDOUT`
- `EINPROGRESS`

`to_dlm_errno()` converts Linux errno values to DLM wire values. `from_dlm_errno()` converts them back.

## Notes
Unlisted errno values pass through unchanged.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/util.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/util.h

## Purpose
`util.h` declares DLM errno translation helpers.

## Exports
- `to_dlm_errno(int err)`
- `from_dlm_errno(int err)`

## Notes
The declarations correspond directly to `util.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/drop_caches.c -->
# File Research: sources/os/linux/linux-stable/fs/drop_caches.c

## Purpose
`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl for manually dropping page cache and slab reclaimable objects.

## Sysctl
A write-only sysctl named `vm/drop_caches` accepts values from 1 to 4:
- bit 0: drop page cache
- bit 1: drop slab objects
- bit 2: suppress future informational logging

The handler is `drop_caches_sysctl_handler()`.

## Page Cache Dropping
`drop_pagecache_sb()` iterates a superblock’s inode list under `s_inode_list_lock`. It skips inodes being freed/new and, when rescheduling is not needed, skips mappings without pages.

For eligible inodes it:
1. Takes an inode reference with `__iget()`.
2. Drops the superblock inode-list lock.
3. Calls `invalidate_mapping_pages()`.
4. Releases the prior inode reference.
5. Calls `cond_resched()`.
6. Continues iteration.

## Slab Dropping
When bit 1 is set, the handler calls `drop_slab()` and records `DROP_SLAB`.

## Initialization
`init_vm_drop_caches_sysctls()` registers the sysctl table during `fs_initcall`.

## Notes
The global `sysctl_drop_caches` is intentionally simple. Page-cache dropping drains per-CPU LRU state first with `lru_add_drain_all()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/drop_caches.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/Kconfig

## Purpose
This Kconfig file defines build options for eCryptfs.

## Options
- `ECRYPT_FS`: tristate option for the eCryptfs stacked encrypted filesystem.
  - Depends on `KEYS`, `CRYPTO`, and either `ENCRYPTED_KEYS` enabled or unavailable.
  - Selects ECB, CBC, MD5 library crypto support.
  - Builds module `ecryptfs` when selected as module.
- `ECRYPT_FS_MESSAGING`: optional bool for `/dev/ecryptfs` userspace key wrap/unwrap notifications.
  - Depends on `ECRYPT_FS`.

## Notes
The help text points to `Documentation/filesystems/ecryptfs.rst` and notes that userspace components are required.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/Makefile

## Purpose
This Makefile defines the eCryptfs module object composition.

## Build Rules
- `obj-$(CONFIG_ECRYPT_FS) += ecryptfs.o`
- Core objects:
  - `dentry.o`
  - `file.o`
  - `inode.o`
  - `main.o`
  - `super.o`
  - `mmap.o`
  - `read_write.o`
  - `crypto.o`
  - `keystore.o`
  - `kthread.o`
  - `debug.o`
- Messaging-specific objects when `CONFIG_ECRYPT_FS_MESSAGING` is enabled:
  - `messaging.o`
  - `miscdev.o`

## Notes
The file is build metadata only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/Makefile -->