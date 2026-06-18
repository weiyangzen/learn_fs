# Group Research: group_731_linux_sources_os_linux_linux_fs_dlm_lowcomms_c_sources_os_linux_linu_b63ff56bd832

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/linux/linux`, and every listed source file was read completely in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lowcomms.c -->
# File Research: sources/os/linux/linux/fs/dlm/lowcomms.c

## Role

`lowcomms.c` is the DLM low-level transport layer. It owns kernel sockets, address resolution, connection setup/teardown, send buffering, receive buffering, and the handoff of validated byte streams to `midcomms`.

It supports TCP and SCTP, selected by `dlm_config.ci_protocol`, and deliberately sends from workqueues instead of caller context so DLM locking paths do not block on socket flow control.

## Core State

The main structure is `struct connection`, keyed by nodeid in `connection_hash` under SRCU. It stores:
- active `struct socket *sock`
- per-node address list, socket mark, and retry index
- send/receive work items
- a page-backed write queue
- leftover receive bytes for partial DLM messages
- `othercon`, used for crossed incoming/outgoing connection races

`struct writequeue_entry` owns a page of outgoing bytes and a list of `struct dlm_msg` records that refer to messages packed into that page. Krefs keep pages/messages alive for retransmission support in midcomms.

## Address and Connection Handling

`dlm_lowcomms_addr()` adds configured peer addresses and creates a connection object if needed. `nodeid_to_addr()` and `addr_to_nodeid()` translate between DLM nodeids and socket addresses, honoring per-node marks.

Accepted sockets are matched to configured peer addresses. If a connection already exists, the incoming socket is stored in `othercon`, preserving backward-compatible handling of simultaneous connects.

`dlm_connect()` creates a kernel socket, binds it to local cluster address state, applies TCP/SCTP options, installs lowcomms callbacks, and calls `kernel_connect()`.

## Receive Path

Socket callbacks set flags and queue work:
- `lowcomms_data_ready()` queues receive work.
- `lowcomms_write_space()` clears application-limited state and queues send work.
- `lowcomms_listen_data_ready()` queues listener accept work.

`receive_from_sock()` reads nonblocking into a process queue buffer, prepends any previous leftover bytes, asks `dlm_validate_incoming_buffer()` how many complete messages exist, saves incomplete tail bytes, then queues `process_dlm_messages()`.

The process queue is bounded by `DLM_MAX_PROCESS_BUFFERS`; if it grows too large, receive work waits for the process queue to drain to avoid unbounded memory growth.

## Send Path

Callers allocate messages through `dlm_lowcomms_new_msg()`, fill returned memory, then must call `dlm_lowcomms_commit_msg()`. Messages are packed into page-sized write queue entries when space permits.

`send_to_sock()` sends page bytes with `MSG_SPLICE_PAGES | MSG_DONTWAIT | MSG_NOSIGNAL`. Partial sends mark entries dirty; if a dirty entry is interrupted by connection close, the whole entry is dropped so a peer never sees the remainder of a half message after reconnect.

`dlm_lowcomms_resend_msg()` creates a duplicate queued message from an original committed message and marks the original as retransmitting.

## Protocol Variants

The `dlm_proto_ops` table abstracts TCP and SCTP:
- TCP binds only the first local address and warns on multihoming.
- SCTP binds all local addresses and uses a larger receive buffer.
- TCP uses `SHUT_WR`; SCTP uses `SHUT_RDWR`.

## Shutdown and Cleanup

`dlm_lowcomms_shutdown()` stops listener callbacks, closes the listener, shuts down all peer connections, drains workqueues, closes sockets, cleans write queues, then re-enables connection I/O state.

`dlm_lowcomms_close()` is used when recovery knows a node has left. It stops I/O, closes the socket(s), removes the connection from the hash, frees queued messages, and releases objects through SRCU callbacks.

## Important Behaviors and Invariants

- Message allocation and commit carry an SRCU read-side section across the caller fill path.
- Send work is suppressed while `CF_APP_LIMITED` or `CF_IO_STOP` is set.
- Receive parsing accepts complete DLM messages only and preserves leftovers for the next read.
- `othercon` exists only for connection race compatibility and is recursively stopped/closed with the primary connection.
- Socket callbacks must be restored before socket release to avoid callbacks into freed DLM state.

## Research Notes

Read completely. This file is the transport foundation used by `midcomms.c`; correctness hinges on message boundary preservation, kref lifetime rules, SRCU connection lifetime, and shutdown ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lowcomms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lowcomms.h -->
# File Research: sources/os/linux/linux/fs/dlm/lowcomms.h

## Role

`lowcomms.h` declares the public interface from DLM mid-level communication and memory code into the low-level socket layer.

## Key Definitions

- `DLM_MIDCOMMS_OPT_LEN` is the size of a `struct dlm_opts` wrapper.
- `DLM_MAX_APP_BUFSIZE` subtracts midcomms option overhead from the socket buffer size.
- `CONN_HASH_SIZE` is 32.
- `nodeid_hash()` maps nodeids to connection buckets with `nodeid & (CONN_HASH_SIZE - 1)`.

## Exported Interface

The header exposes lifecycle functions, peer address registration, node close/shutdown, message allocation/commit/put/resend, explicit connect, socket mark update, and slab-cache factory functions.

## Important Behaviors and Invariants

Callers that successfully allocate a `struct dlm_msg` must commit or release it according to the lowcomms API contract. The simple nodeid hash assumes common cluster nodeids are sequential.

## Research Notes

Read completely. This header is tightly paired with `lowcomms.c` and is consumed by `midcomms.c`, `memory.c`, recovery, and membership code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lowcomms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lvb_table.h -->
# File Research: sources/os/linux/linux/fs/dlm/lvb_table.h

## Role

`lvb_table.h` declares the global `dlm_lvb_operations[8][8]` table.

## Function

The table is used by DLM user/callback paths to determine lock value block behavior across lock mode transitions.

## Research Notes

Read completely. The file is declaration-only and depends on the implementation of the table elsewhere in the DLM subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lvb_table.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/main.c -->
# File Research: sources/os/linux/linux/fs/dlm/main.c

## Role

`main.c` is the DLM module entry/exit file. It wires initialization and cleanup ordering for memory caches, communication, lockspaces, configfs/debugfs, user devices, plock support, and the DLM workqueue.

## Initialization Flow

`init_dlm()` runs:
1. `dlm_memory_init()`
2. `dlm_midcomms_init()`
3. `dlm_lockspace_init()`
4. `dlm_config_init()`
5. `dlm_register_debugfs()`
6. `dlm_user_init()`
7. `dlm_plock_init()`
8. `alloc_workqueue("dlm_wq", WQ_PERCPU, 0)`

Failures unwind in reverse order for already initialized components.

## Exit Flow

`exit_dlm()` destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms, unregisters debugfs, and destroys memory caches.

## Exports

The module exports `dlm_new_lockspace`, `dlm_release_lockspace`, `dlm_lock`, and `dlm_unlock`.

## Important Behaviors and Invariants

The shared `dlm_wq` must be destroyed before subsystem exit so pending freeing or callback work is complete. Midcomms initialization happens before lockspace/config use, but actual lowcomms socket startup is controlled later by lockspace/config paths.

## Research Notes

Read completely. This file defines module-level ordering rather than lock protocol logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/member.c -->
# File Research: sources/os/linux/linux/fs/dlm/member.c

## Role

`member.c` manages DLM lockspace membership during recovery. It tracks current members, removed members, slot assignments, member weights, and communication state changes for nodes entering or leaving a lockspace.

## Slot Handling

The slot functions support lockspace slot negotiation:
- `dlm_slots_version()` checks whether a remote header supports slots.
- `dlm_slot_save()` records a member slot/generation from RCOM status.
- `dlm_slots_copy_out()` serializes current slots into an RCOM reply.
- `dlm_slots_copy_in()` imports slot data from the low-node coordinator.
- `dlm_slots_assign()` assigns slots for all nodes when the local node is the low nodeid.

Slot assignment preserves existing slots, rejects slot changes after assignment, increments generation, logs the resulting map, and checks that the serialized slot list fits in `DLM_MAX_APP_BUFSIZE`.

## Membership Lists

Members are stored in `ls_nodes` ordered by nodeid, with removed members moved to `ls_nodes_gone`. `dlm_is_member()` and `dlm_is_removed()` query these lists.

`dlm_add_member()` allocates a member, starts/connects remote communication for nonlocal nodes, and inserts the member. `dlm_clear_members()` removes all active members and informs midcomms for remote nodes.

`make_member_array()` builds a weighted nodeid array for directory/master selection, treating all weights as one if every node has weight zero.

## Recovery Integration

`dlm_recover_members()` reconciles config-layer recovery membership input with DLM’s active lists:
- Counts previously removed members as negative recovery.
- Moves gone or re-added members to `ls_nodes_gone`.
- Calls midcomms removal and lockspace ops slot recovery for removed members.
- Adds new members.
- Updates `ls_low_nodeid`.
- Rebuilds the weighted member array.
- Pings all members with status RCOMs to establish communications.

## Lockspace Stop/Start

`dlm_ls_stop()` stops normal locking and receive processing for a recovery cycle. It sets recovery stop flags, clears running state, activates request queue blocking, waits until recovery owns `ls_in_recovery`, suspends recoverd, clears slot state, resumes recoverd, and calls optional `recover_prep`.

`dlm_ls_start()` reads current config nodes, creates a `dlm_recover` argument block with a new recovery sequence, stores it in the lockspace, and wakes recoverd.

## Important Behaviors and Invariants

- Membership changes must be reported to lockspace ops and midcomms before recovery may abort.
- Removed members stay in `ls_nodes_gone` until recovery completes so purging and remastering can recognize them.
- Userspace guarantees all nodes stop before any node starts the next recovery.
- `ls_recv_active`, `ls_recover_lock`, and `ls_requestqueue_lock` order the transition into recovery.

## Research Notes

Read completely. This file is the bridge between configfs/cluster membership and the recovery state machine.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/member.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/member.h -->
# File Research: sources/os/linux/linux/fs/dlm/member.h

## Role

`member.h` declares membership and slot-management APIs used by recovery, RCOM, and lockspace code.

## Exported Interface

It exposes lockspace stop/start, member clearing, recovery membership reconciliation, member/removed queries, slot version/copy/assign helpers, and `dlm_lsop_recover_done()`.

## Research Notes

Read completely. The declarations correspond directly to `member.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/member.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/memory.c -->
# File Research: sources/os/linux/linux/fs/dlm/memory.c

## Role

`memory.c` centralizes DLM object allocation through slab caches and RCU-delayed frees.

## Cache Lifecycle

`dlm_memory_init()` creates caches for:
- lowcomms write queue entries
- midcomms message handles
- lowcomms messages
- lock blocks (`dlm_lkb`)
- resource blocks (`dlm_rsb`)
- callbacks (`dlm_callback`)

Failure unwinds already created caches. `dlm_memory_exit()` calls `rcu_barrier()` before destroying caches so deferred frees are complete.

## Allocation Helpers

The file provides typed allocate/free wrappers for RSBs, LKBs, LVB buffers, message handles, writequeue entries, messages, and callbacks.

RSBs and LKBs are freed through `call_rcu()`. RSB release frees its LVB pointer. LKB release frees user-argument state and user LVB memory when the lock belongs to the user API.

## Important Behaviors and Invariants

- Most allocations use `GFP_ATOMIC`, reflecting DLM use from spinlocked or recovery-sensitive contexts.
- Cache destruction relies on `rcu_barrier()` to avoid freeing slabs before callbacks have run.
- User LKB cleanup must release embedded user state only for `DLM_DFL_USER_BIT` locks.

## Research Notes

Read completely. This is infrastructure code with no protocol control flow, but it defines lifetime assumptions used across the DLM subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/memory.h -->
# File Research: sources/os/linux/linux/fs/dlm/memory.h

## Role

`memory.h` declares DLM memory initialization and typed object allocation/free helpers.

## Interface

It exposes cache lifecycle functions and wrappers for RSB, LKB, LVB, mhandle, writequeue, lowcomms message, and callback allocation.

## Research Notes

Read completely. The declarations match `memory.c` and are used broadly by lock, comms, recovery, and user paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/midcomms.c -->
# File Research: sources/os/linux/linux/fs/dlm/midcomms.c

## Role

`midcomms.c` implements DLM’s reliable application-layer communication over lowcomms. It adds protocol version detection, sequence numbers, acknowledgements, retransmission, and a DLM-level FIN/ACK termination state machine.

## Node State

`struct midcomms_node` is keyed by nodeid in `node_hash`. It stores protocol version, send and receive sequence counters, an unbounded send queue of committed message handles, termination flags, delivered-message counters, a shutdown waitqueue, and a reduced TCP-like close state.

`struct dlm_mhandle` represents one outgoing midcomms message. For protocol 3.2, it is linked on the node send queue until acknowledged.

## Version Handling

Protocol version is detected from early RCOM traffic:
- 3.1 messages are passed through without reliable retransmission support.
- 3.2 messages use `DLM_OPTS` wrappers carrying sequence numbers and inner commands.

`dlm_midcomms_version_wait()` waits for all nodes to detect a version, close, or be force-closed.

## Reliable Delivery

For 3.2:
- Outgoing messages are wrapped in `struct dlm_opts`.
- `seq_send` is assigned when the lowcomms message buffer is allocated.
- Committed messages stay on `send_queue`.
- Receivers deliver only expected sequence numbers and ignore duplicates/out-of-order messages.
- `DLM_ACK` acknowledges all messages before the supplied sequence number.
- `dlm_midcomms_unack_msg_resend()` retransmits committed unacknowledged messages after lowcomms socket errors.

ACKs are sent opportunistically when delivered-message thresholds are exceeded and directly for FIN or duplicate sequence handling.

## Receive Path

`dlm_process_incoming_buffer()` walks complete lowcomms messages and dispatches based on header version.

`dlm_midcomms_receive_buffer_3_2()` validates `DLM_OPTS` lengths, checks supported inner commands, handles early RCOM version detection messages specially, processes ACKs, and routes reliable messages through `dlm_midcomms_receive_buffer()`.

3.1 receive handling only validates basic RCOM/message lengths and dispatches to `dlm_receive_buffer()`.

## Termination State Machine

The file implements reduced TCP-style states: closed, established, fin-wait-1, fin-wait-2, close-wait, last-ack, and closing.

`dlm_midcomms_shutdown()` performs active shutdown for all nodes, sends FIN for established 3.2 peers, waits for closed state or timeout, then calls lowcomms shutdown and resets nodes.

`dlm_midcomms_add_member()` and `dlm_midcomms_remove_member()` maintain a user count per node. When the count reaches zero, passive close handling may send FIN after receiving a peer FIN.

`dlm_midcomms_close()` force-closes a node, wakes shutdown waiters, removes the midcomms node, calls lowcomms close, flushes pending messages, and releases through SRCU.

## Raw Debug Send

`dlm_midcomms_rawmsg_send()` sends a user-provided raw DLM message for debug use and can fill a missing sequence in a raw `DLM_OPTS` message.

## Important Behaviors and Invariants

- For 3.2, committed messages must remain queued until acknowledged.
- SRCU lifetime protects node lookup while callers allocate and commit mhandles.
- ACK processing may release message handles, so commit holds RCU read-side protection while committing.
- STOP_TX/STOP_RX flags guard sends/receives during DLM-level shutdown.
- The close mutex serializes force close with stop/remove paths.

## Research Notes

Read completely. This file is the reliability layer between byte-stream transport and DLM lock/recovery message processing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/midcomms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/midcomms.h -->
# File Research: sources/os/linux/linux/fs/dlm/midcomms.h

## Role

`midcomms.h` declares DLM mid-level communication APIs.

## Interface

It exposes incoming buffer validation/processing, outgoing mhandle allocation/commit, address registration, version wait, node close/start/stop/init/exit/shutdown, member add/remove notifications, retransmission trigger, debug state accessors, raw message send, and cache creation.

## Research Notes

Read completely. This header is the contract between transport, recovery, member management, debugfs, and message-sending code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/midcomms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/plock.c -->
# File Research: sources/os/linux/linux/fs/dlm/plock.c

## Role

`plock.c` bridges kernel POSIX byte-range locks to userspace `dlm_controld` through the `dlm_plock` misc device. It exports the kernel-facing DLM POSIX lock API and implements the device protocol used by userspace to arbitrate locks cluster-wide.

## Operation Queues

`send_list` holds plock operations waiting for userspace to read. `recv_list` holds operations waiting for userspace replies. `ops_lock` protects both lists. `send_wq` wakes the daemon for new requests; `recv_wq` wakes kernel waiters when replies arrive.

`struct plock_op` contains `dlm_plock_info` plus optional async callback data for NFS-style asynchronous lock handling.

## Kernel Lock APIs

`dlm_posix_lock()` sends lock requests. Blocking requests wait for replies and handle signal interruption by sending a cancel. Async requests store a copy of the file lock and return `FILE_LOCK_DEFERRED`.

`dlm_posix_unlock()` first updates the local VFS lock state, then sends an unlock to userspace. Close-generated unlocks do not wait for a reply.

`dlm_posix_cancel()` supports async cancellation, finds the matching waiter, calls the original grant callback with `-EINTR`, or falls back to unlock if cancellation was too late.

`dlm_posix_get()` asks userspace for conflicting lock information and converts positive conflict replies into a VFS `file_lock` result.

## Device Protocol

`dev_read()` returns one `dlm_plock_info` from `send_list`; ordinary requests move to `recv_list`, while close unlocks are freed immediately.

`dev_write()` copies in one result, checks protocol version, matches it to a waiting op, copies the result, and either wakes waiters or invokes the async callback.

`dev_poll()` reports readable state when `send_list` is non-empty.

## Important Behaviors and Invariants

- Blocking waiter replies may arrive out of order, so waiting lock replies match on full lock identity.
- Non-waiting replies are matched to the first non-waiting op for the same filesystem id.
- The filesystem's local VFS lock state is updated after successful cluster lock grant.
- Async callback failure after grant is logged as a dangling-lock risk because cancellation is not fully implemented there.
- Device protocol version mismatch rejects userspace replies.

## Research Notes

Read completely. This file is one of the user/kernel boundary points for DLM and depends on a userspace daemon for cluster-wide POSIX lock arbitration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/plock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/rcom.c -->
# File Research: sources/os/linux/linux/fs/dlm/rcom.c

## Role

`rcom.c` implements DLM recovery communication messages. RCOMs coordinate recovery status barriers, directory name transfer, resource master lookup, and lock-copy rebuilding.

## Message Creation

`create_rcom()` allocates a midcomms reliable message. `create_rcom_stateless()` allocates a lowcomms message directly for early/status exchanges that must remain compatible with version detection and their own retry handling.

`_create_rcom()` fills the DLM RCOM header, type, lockspace id, sender nodeid, length, and recovery sequence.

## Status and Config

`dlm_rcom_status()` sends a status request and waits synchronously for a reply using `ls_rcom_seq` and `LSFL_RCOM_WAIT`. It retries on timeout and validates remote config values such as LVB length and lockspace flags.

`receive_rcom_status()` replies with current recovery status and optional slot data when requested.

`receive_sync_reply()` copies the reply into `ls_recover_buf` only if the reply id matches the current wait sequence.

## Directory and Master Recovery

`dlm_rcom_names()` requests resource names from a peer during directory rebuild. `receive_rcom_names()` replies with names selected by `dlm_copy_master_names()`.

`dlm_send_rcom_lookup()` asks a directory node for the new master of a resource. `receive_rcom_lookup()` performs `dlm_master_lookup()` and replies with the selected nodeid. Lookup replies are handed to `dlm_recover_master_reply()`.

## Lock Recovery

`pack_rcom_lock()` serializes an LKB and optional LVB into `struct rcom_lock`.

`dlm_send_rcom_lock()` sends local process-copy lock state to the new master. `receive_rcom_lock()` calls `dlm_recover_master_copy()` and replies with remid/result data. Lock replies are processed by `dlm_recover_process_copy()`.

## Lockspace Not Ready

`dlm_send_ls_not_ready()` sends a status reply with `-ESRCH` for a lockspace that is not ready or not present. The requester treats this as a remote lockspace with zero status during early recovery.

## Receive Filtering

`dlm_receive_rcom()` gates messages by recovery stop state, recovery sequence, and stage:
- name/lookup/lock messages are ignored before node status is reached
- lookup/lock messages are ignored before directory recovery is reached
- replies with stale sequence ids are ignored
- short lock recovery messages are rejected

## Important Behaviors and Invariants

- RCOM status messages are part of version detection and use stateless lowcomms paths.
- `ls_recover_buf` is the single synchronous reply buffer for recovery waits.
- Recovery stage bits prevent future-stage messages from being processed too early.
- Reply sequence checks avoid applying stale recovery replies after a new recovery generation begins.

## Research Notes

Read completely. This file is recovery’s network protocol implementation and is tightly coupled to `recover.c`, `recoverd.c`, `member.c`, and `dir.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/rcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/rcom.h -->
# File Research: sources/os/linux/linux/fs/dlm/rcom.h

## Role

`rcom.h` declares recovery communication APIs.

## Interface

It exposes status/name RCOM requests, master lookup and lock-copy sends, the RCOM receive dispatcher, and the not-ready status reply helper.

## Research Notes

Read completely. The declarations correspond to `rcom.c` and are consumed by recovery, directory, and receive paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/rcom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/recover.c -->
# File Research: sources/os/linux/linux/fs/dlm/recover.c

## Role

`recover.c` implements the internal DLM recovery algorithms for waiting on recovery barriers, recovering resource masters, rebuilding lock copies, and finalizing resource state after membership changes.

## Barrier Waiting

`dlm_wait_function()` waits for a condition or recovery stop, with periodic timeout checks for synchronous RCOM waits.

Recovery status uses a low-node coordination pattern:
- the lowest node polls every member for a status bit
- once all have it, the low node sets the corresponding `_ALL` bit
- other nodes poll the low node for `_ALL`

This is used for members, directory, locks, and done stages.

## Member Slot Recovery

`dlm_recover_members_wait()` initializes member slots, waits for all nodes to reach the node stage, and either assigns slots as the low node or imports slots from the low node.

## Master Recovery

For resources whose master departed, `dlm_recover_masters()` walks active root resources and either:
- computes a static new master when no directory is used, or
- sends async lookup RCOMs to directory nodes.

Outstanding master lookups are tracked in `ls_recover_xa` with local resource ids. `dlm_recover_master_reply()` updates the resource master and removes the lookup from the xarray.

`set_new_master()` updates lock nodeids and marks resources for later lock and LVB recovery.

## Lock Recovery

`dlm_recover_locks()` sends every local grant/convert/wait LKB on remastered resources to the new master. Outstanding resource lock-copy operations are tracked on `ls_recover_list`.

`dlm_recovered_lock()` decrements the per-resource recovery count, clears `RSB_NEW_MASTER` when done, and wakes recovery when all copies are complete.

## LVB and Grant Finalization

`recover_lvb()` determines the recovered resource LVB and `RSB_VALNOTVALID` state:
- invalidates when a master lost an EX/PW lock from a failed node
- for new masters, chooses an LVB from the strongest lock above CR, or the highest LVB sequence among NL/CR locks
- invalidates if only NL/CR LVB locks remain

`recover_conversion()` handles PR/CW conversion conflicts by dropping incompatible granted conversion mode to NL so recovery grant can re-evaluate.

`recover_grant()` marks new masters with waiting/converting locks for recovery grant processing.

`dlm_recover_rsbs()` runs these finalization steps for all mastered resources and clears recovery flags.

## Inactive Cleanup

`dlm_clear_inactive()` removes and frees slow-inactive RSBs from the rhashtable before recovery proceeds.

## Important Behaviors and Invariants

- Recovery list and xarray counts must return to zero; error paths clear outstanding state.
- Resource locks are held while modifying master and queue state.
- All MSTCPY locks are purged/rebuilt even if a master remains effectively the same, because aborted recovery can make request replies ambiguous.
- LVB recovery must occur before recovery grant so completions present the correct LVB state.

## Research Notes

Read completely. This file contains the main data-structure recovery logic, while `recoverd.c` sequences it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/recover.h -->
# File Research: sources/os/linux/linux/fs/dlm/recover.h

## Role

`recover.h` declares recovery wait, status, master recovery, lock recovery, LVB/resource finalization, and inactive cleanup APIs.

## Research Notes

Read completely. The header is the shared contract between `recover.c`, `recoverd.c`, `rcom.c`, `member.c`, and lock receive paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/recover.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/recoverd.c -->
# File Research: sources/os/linux/linux/fs/dlm/recoverd.c

## Role

`recoverd.c` implements the per-lockspace recovery kernel thread and the top-level recovery sequence.

## Recovery Lists

`dlm_create_root_list()` snapshots all active RSBs for recovery work. `dlm_create_masters_list()` snapshots active local-master RSBs for directory rebuild. Both hold references and have matching release helpers.

## Recovery Sequence

`ls_recover()` performs the staged recovery:
1. suspend callbacks
2. clear inactive RSBs
3. snapshot root RSBs
4. reconcile membership
5. recompute directory nodeids
6. snapshot local masters
7. mark node stage and wait for all members
8. rebuild the directory from peer master-name data
9. mark/wait directory stage
10. recover waiters before remastering
11. if nodes departed or no directory exists, purge departed locks, recover masters, recover locks, wait lock stage, and recover RSB state
12. otherwise still participate in the lock-stage barrier
13. purge stale requestqueue entries
14. mark/wait done stage
15. clear gone members
16. resume callbacks
17. re-enable locking
18. process saved requestqueue
19. recover waiters post-recovery
20. grant recoverable locks

## Locking Re-enable

`enable_locking()` only re-enables locking if the recovery sequence has not been superseded. It resumes scan timers, releases `ls_in_recovery`, clears `LSFL_RECOVER_LOCK`, and synchronizes against receive paths with `ls_recv_active`.

## Recovery Thread

`dlm_recoverd()` starts with `ls_in_recovery` held and `LSFL_RECOVER_LOCK` set. It sleeps until `LSFL_RECOVER_DOWN` or `LSFL_RECOVER_WORK` is set. DOWN reacquires recovery exclusion; WORK runs `do_ls_recovery()`.

`do_ls_recovery()` consumes `ls_recover_args`, clears stop state if current, runs recovery, completes `ls_recovery_done` on success or fatal error, and leaves interrupted recovery to be queued again.

## Important Behaviors and Invariants

- Recovery may not abort until membership changes are reported to lsops and midcomms.
- Normal locking is enabled before saved requestqueue processing.
- Requestqueue purge happens after directory rebuild because old directory requests are invalid.
- `ls_recoverd_active` lets stop/start paths suspend the daemon at safe points.

## Research Notes

Read completely. This is the orchestration layer for the recovery protocol implemented across member, rcom, recover, dir, and lock code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/recoverd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/recoverd.h -->
# File Research: sources/os/linux/linux/fs/dlm/recoverd.h

## Role

`recoverd.h` declares the recovery daemon lifecycle and suspend/resume operations.

## Interface

It exposes start, stop, suspend, and resume for the per-lockspace recovery thread.

## Research Notes

Read completely. The declarations correspond to `recoverd.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/recoverd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/requestqueue.c -->
# File Research: sources/os/linux/linux/fs/dlm/requestqueue.c

## Role

`requestqueue.c` stores normal DLM messages received while locking is stopped for recovery, then replays or purges them when recovery completes.

## Queue Entry

`struct rq_entry` stores the recovery sequence low bits, sender nodeid, and a copied `struct dlm_message` plus variable extra payload.

## Queueing

`dlm_add_requestqueue()` allocates an entry with `GFP_ATOMIC`, copies the message and extra bytes, records `ls_recover_seq`, and appends it to `ls_requestqueue`.

## Replay

`dlm_process_requestqueue()` runs after normal locking has been re-enabled. It drains messages under `ls_requestqueue_lock`, logs each saved message, calls `dlm_receive_message_saved()`, frees the entry, and aborts if locking stops again.

## Purge Policy

`dlm_purge_requestqueue()` removes entries if:
- the lockspace is being freed
- the sender was removed
- the message is directory remove/lookup/lookup-reply
- the lockspace has no directory

Directory requests are purged because recovery rebuilds the directory and requesters must resend.

## Important Behaviors and Invariants

`LSFL_RECV_MSG_BLOCKED` is cleared only when the queue is empty. Receive paths can wait for this drain before processing new normal messages.

## Research Notes

Read completely. This file protects normal lock message ordering across recovery boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/requestqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/requestqueue.h -->
# File Research: sources/os/linux/linux/fs/dlm/requestqueue.h

## Role

`requestqueue.h` declares requestqueue operations.

## Interface

It exposes add, process, wait, and purge functions for saved recovery-time messages.

## Research Notes

Read completely. `dlm_wait_requestqueue()` is declared here but implemented outside this file group.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/requestqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/user.c -->
# File Research: sources/os/linux/linux/fs/dlm/user.c

## Role

`user.c` implements the DLM userspace character-device interface. It provides the control device for lockspace create/remove, per-lockspace devices for lock/unlock/deadlock/purge operations, AST/BAST callback delivery, compat translation, and monitor-device integration with `dlm_controld`.

## Compat Support

Under `CONFIG_COMPAT`, 32-bit request/result structures are translated by `compat_input()` and `compat_output()`. Lock parameter pointers and callback addresses are widened from 32-bit user values.

## Callback Delivery

`dlm_user_add_ast()` adds completion or blocking callbacks to the owning process queue unless the lock is orphaned/dead or the callback can be skipped. End-of-life locks are removed from the process lock list after final AST generation.

Callbacks copy LVB data into callback-local storage when needed so later user reads see stable data.

## User Commands

`device_write()` validates request size and device protocol version, translates compat input when needed, rejects lock operations during close, and dispatches:
- `DLM_USER_LOCK` to request/convert/adopt-orphan paths
- `DLM_USER_UNLOCK` to unlock/cancel
- `DLM_USER_DEADLOCK` to deadlock handling
- `DLM_USER_CREATE_LOCKSPACE` on control device
- `DLM_USER_REMOVE_LOCKSPACE` on control device
- `DLM_USER_PURGE` on lockspace devices

Create/remove lockspace operations require `CAP_SYS_ADMIN`.

## Device Lifecycle

`device_create_lockspace()` creates a user lockspace and registers a per-lockspace misc device named `dlm_<name>`. `dlm_device_deregister()` removes that misc device.

Opening a lockspace device creates a per-file `dlm_user_proc` with AST, lock, and unlocking lists. Closing marks the proc closing, clears process locks, frees the proc, and drops references held by open/find.

## Read and Poll

`device_read()` either returns the device version or waits for one callback from the process AST queue. It copies a `dlm_lock_result` or compat result to userspace, optionally followed by LVB data.

`device_poll()` reports readable state when ASTs are queued.

## Control and Monitor Devices

`dlm_user_init()` registers:
- `dlm-control` for create/remove and version reads
- `dlm-monitor` for daemon availability monitoring

`dlm_user_daemon_available()` treats a configured nodeid as enough for old daemons that never open monitor; otherwise it requires the monitor device to be open. Closing the last monitor fd calls `dlm_stop_lockspaces()`.

## Important Behaviors and Invariants

- User lock operations require a process context from a lockspace device, not the control device.
- Create/remove require the control device, not a lockspace device.
- Protocol major must match and user minor cannot exceed kernel minor.
- AST queues are per open file, so each process sees callbacks for its own locks.
- `ls_clear_proc_locks` protects AST delivery against process lock cleanup.

## Research Notes

Read completely. This is the primary userspace DLM API implementation and coordinates with lock, AST, config, and lockspace code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/user.h -->
# File Research: sources/os/linux/linux/fs/dlm/user.h

## Role

`user.h` declares the DLM user-device API hooks used by lock and module code.

## Interface

It exposes callback purging/addition, user device init/exit, per-lockspace device deregistration, and daemon availability detection.

## Research Notes

Read completely. The implementation is in `user.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/util.c -->
# File Research: sources/os/linux/linux/fs/dlm/util.c

## Role

`util.c` translates Linux errno values to stable DLM wire errno values and back.

## Behavior

Higher Linux errno numbers vary across architectures, so DLM uses fixed numeric values for selected errors on the wire:
- `EDEADLK`
- `EBADR`
- `EBADSLT`
- `EPROTO`
- `EOPNOTSUPP`
- `ETIMEDOUT`
- `EINPROGRESS`

`to_dlm_errno()` maps kernel errors to fixed negative wire values. `from_dlm_errno()` maps them back to local kernel errno values.

## Research Notes

Read completely. This file protects cross-architecture protocol compatibility for recovery and lock messages.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/util.h -->
# File Research: sources/os/linux/linux/fs/dlm/util.h

## Role

`util.h` declares DLM errno translation helpers.

## Interface

It exposes `to_dlm_errno()` and `from_dlm_errno()`.

## Research Notes

Read completely. The implementation is in `util.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/drop_caches.c -->
# File Research: sources/os/linux/linux/fs/drop_caches.c

## Role

`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl for manually dropping page cache and/or slab caches.

## Page Cache Dropping

`drop_pagecache_sb()` iterates a superblock’s inode list, skips inodes in freeing/new states and usually skips empty mappings, takes a temporary inode reference, drops the superblock inode-list lock, invalidates mapping pages, releases the previous inode reference, and reschedules as needed.

The delayed `toput_inode` avoids dropping the final reference while holding the superblock inode-list lock.

## Sysctl Handler

`drop_caches_sysctl_handler()` uses `proc_dointvec_minmax()` for writes in the range 1 through 4. On write:
- bit 1 drains LRU additions and invalidates page cache for all superblocks
- bit 2 calls `drop_slab()`
- bit 4 suppresses future informational logging

VM events are counted for pagecache and slab drops.

## Registration

`drop_caches_table` registers write-only `drop_caches` under `vm` during `fs_initcall()`.

## Important Behaviors and Invariants

- This is an explicit manual cache drop path, not normal reclaim.
- Inode references and lock dropping are arranged to avoid inode-list deadlocks.
- The sysctl variable is global and intentionally simple.

## Research Notes

Read completely. This file is standalone VFS/MM sysctl glue outside DLM.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/drop_caches.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/ecryptfs/Kconfig

## Role

`fs/ecryptfs/Kconfig` defines build configuration options for the eCryptfs filesystem layer.

## Options

`ECRYPT_FS` is a tristate option for eCryptfs. It depends on keys and crypto support, and on encrypted keys being available or disabled. It selects ECB, CBC, MD5 crypto support, and notes that userspace components are required.

`ECRYPT_FS_MESSAGING` is a bool depending on `ECRYPT_FS`. It enables `/dev/ecryptfs` notifications for userspace key wrap/unwrap operations, including OpenSSL-backed handling.

## Research Notes

Read completely. This file controls feature availability; implementation files are outside this group.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/Makefile -->
# File Research: sources/os/linux/linux/fs/ecryptfs/Makefile

## Role

`fs/ecryptfs/Makefile` defines object composition for the eCryptfs kernel module.

## Build Composition

`obj-$(CONFIG_ECRYPT_FS) += ecryptfs.o` builds eCryptfs when enabled.

The base module includes dentry, file, inode, main, super, mmap, read/write, crypto, keystore, kthread, and debug objects.

When `CONFIG_ECRYPT_FS_MESSAGING` is enabled, messaging and miscdev objects are added.

## Research Notes

Read completely. This file is build glue and has no runtime logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/Makefile -->