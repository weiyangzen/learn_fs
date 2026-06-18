# subset-b-003908 research

Grouped research for RDMA/InfiniBand core MAD, RMPP, multicast, memory-registration pool, and netlink support under `sources/distributed-fs/ceph-client/drivers/infiniband/core`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad.c

## Purpose
`mad.c` implements the kernel InfiniBand Management Datagram access layer for QP0 SMI and QP1 GSI traffic. It registers MAD agents, creates the per-port PD/CQ/QP plumbing, routes inbound MADs to either device firmware hooks or registered clients, handles outgoing sends, retries, timeouts, local directed-route SMP completions, and integrates RMPP support for kernel agents.

## Important APIs, types, and functions
- Exported client APIs include `ib_register_mad_agent()`, `ib_unregister_mad_agent()`, `ib_create_send_mad()`, `ib_free_send_mad()`, `ib_post_send_mad()`, `ib_modify_mad()`, `ib_free_recv_mad()`, `ib_response_mad()`, `ib_get_mad_data_offset()`, `ib_is_mad_class_rmpp()`, `ib_get_rmpp_segment()`, and `ib_mad_kernel_rmpp_agent()`.
- `ib_mad_port_private` owns one port's MAD resources: device/port identity, PD, CQ, ordered workqueue, QP0/QP1 state, and registration tables keyed by class version, management class, method, and optional vendor OUI.
- `ib_mad_agent_private` wraps the public `ib_mad_agent` with send, wait, local-completion, RMPP, and backlog lists plus reference counting and timeout work.
- `ib_mad_send_wr_private` is the send state object. It carries the UD WR, SGEs, DMA mappings, TID, retry counters, RMPP segment cursor, and `enum ib_mad_state`.
- `ib_register_mad_agent()` validates QP type, class/version, RMPP mode, SMI/GSI class restrictions, security setup, and non-overlapping method registration before publishing the agent in the xarray TID namespace.
- `ib_post_send_mad()`, `ib_send_mad()`, `ib_mad_send_done()`, `ib_mad_complete_send_wr()`, `timeout_sends()`, and `retry_send()` form the send pipeline.
- `ib_mad_recv_done()`, `validate_mad()`, `find_mad_agent()`, `ib_find_send_mad()`, and `ib_mad_complete_recv()` form the receive and response-matching path.
- `handle_outgoing_dr_smp()`, `handle_ib_smi()`, `handle_opa_smi()`, and `local_completions()` implement locally consumed or locally generated directed-route SMP behavior.
- `ib_mad_init()` and `ib_mad_cleanup()` register the `mad` `ib_client`; device add/remove callbacks open and close all MAD-capable ports.

## Control flow
Initialization clamps the `send_queue_size` and `recv_queue_size` module parameters, initializes the global port list, and registers an `ib_client`. For each RDMA device, `ib_mad_init_device()` opens every port that advertises MAD capability, then opens the agent helper side. `ib_mad_port_open()` allocates a per-port object, PD, CQ, optional SMI QP0, optional GSI QP1, and ordered workqueue, links the port into the global list, transitions QPs through INIT/RTR/RTS, requests CQ notifications, and posts receive buffers.

Agent registration first checks protocol capability and registration consistency: QP0 only accepts subnet management classes, QP1 rejects them, non-RMPP classes cannot request RMPP, and newer vendor classes require a nonzero OUI. It allocates private state, security context, a high-TID xarray ID, then installs method ownership under `port_priv->reg_lock`. Responses route by high 32 bits of TID through `ib_mad_clients`; requests route through version/class/method tables and vendor OUI tables.

Sending starts in `ib_post_send_mad()`. Directed-route SMPs may be handled locally; otherwise the work request is given a timeout/retry budget and enters `IB_MAD_STATE_SEND_START` or `IB_MAD_STATE_QUEUED` if solicited flow-control limits are exceeded. `ib_send_mad()` maps header and payload DMA, posts to the QP if active slots are available, or appends to the overflow list. Send completions unmap DMA, drain overflow sends, update the state machine, call RMPP completion logic when active, move timed requests to the wait list, and notify the client send handler. Timeout work retries until `retries_left` is exhausted and then reports `IB_WC_RESP_TIMEOUT_ERR`.

Receive completions unmap the receive buffer, build an `ib_mad_recv_wc`, validate base version and QP/class pairing, allocate a response buffer, run SMI directed-route processing for DR SMPs, then give `device->ops.process_mad()` first refusal. Device replies are sent immediately through `agent_send_response()`. Otherwise `find_mad_agent()` selects a client and `ib_mad_complete_recv()` applies security, RMPP reassembly, response matching, callback ordering, and send completion for matched responses. Unmatched GET/SET requests can receive an unsupported-method response.

## State and persistence
State is in kernel memory and RDMA core objects, not durable storage. The global port list is protected by `ib_mad_port_list_lock`; per-port registration tables use `reg_lock`; each agent's send/wait/backlog/local/RMPP lists use `agent->lock`; QP send/receive queues use `ib_mad_queue.lock`. Agent lifetime is reference counted and unregistration waits for completions, cancels sends, removes method registrations, flushes the port workqueue, cancels RMPP receives, and RCU-frees the private agent.

The send state machine moves through INIT, QUEUED, SEND_START, WAIT_RESP, EARLY_RESP, CANCELED, and DONE. Solicited flow-control counters cap outstanding CM, SA, and subnet-management requests and release backlog entries when responses or failures retire work. Receive buffers are continuously reposted; buffers consumed by clients are freed through `ib_free_recv_mad()`.

## Dependencies and integration points
This file is central to `ib_core`. It depends on RDMA device capability helpers, verbs object APIs, DMA mapping, xarray allocation, security hooks from `agent.h`, tracing events, `smi.h` and `opa_smi.h` directed-route helpers, `mad_rmpp.c` for RMPP, `agent_send_response()` for generated responses, and device driver `process_mad` callbacks. It exports symbols used by SA, CM, user MAD, and other kernel RDMA clients.

## Risks
- The send and receive paths are highly concurrent. Incorrect list movement or state transitions can double-complete a send, leak an agent reference, or make responses match canceled requests.
- Registration-table overlap checks must remain exact, especially for class 0 aliasing of directed-route SMPs and vendor OUI slots.
- DMA mapping and unmapping paths differ for normal sends, overflow sends, retries, receive reposting, and local SMP handling. Error path changes can leak mappings or free posted receive buffers.
- RMPP integration changes can affect both request completion ordering and response matching.
- `ib_mad_port_close()` still notes unhandled deallocation of registration tables; correctness depends on agents unregistering before port teardown.
- OPA MAD sizing and pkey-index handling differ from classic IB MADs; mixed IB/OPA paths need careful bounds checks.

## Test signals
- Build with InfiniBand core, MAD, SA, CM, user MAD, and OPA-capable configurations to catch symbol/API drift.
- Exercise agent registration conflicts for duplicate method masks, invalid class versions, SMI/GSI class mismatch, vendor OUI exhaustion, and send-only agents.
- Runtime tests should cover QP0 and QP1 send/receive, solicited request timeout and retry, cancel through `ib_modify_mad(..., 0)`, overflow queue drain, and response-before-send-completion ordering.
- Directed-route SMP tests should cover local consume, local response, switch forwarding, permissive LID validation, and OPA base-version behavior.
- Fault injection around `ib_post_send()`, `ib_post_recv()`, DMA mapping, `process_mad()`, and workqueue teardown is valuable because most bugs here are lifetime or cleanup bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_priv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_priv.h

## Purpose
`mad_priv.h` defines the private data model shared by the MAD core and RMPP implementation. It captures queue limits, registration-table dimensions, per-agent and per-port state, send work request state, local completion records, and internal helper prototypes.

## Important APIs, types, and functions
- Queue constants define default, minimum, and maximum MAD send/receive depths plus SGE counts for MAD WRs.
- Registration constants define maximum management class, class version, vendor OUI slots, and vendor range-2 table size.
- `struct ib_mad_private_header` and `struct ib_mad_private` wrap receive buffers with the CQE/list linkage, receive WC, raw WC, DMA mapping, GRH, variable MAD data, and the port's maximum MAD size.
- `struct ib_mad_agent_private` adds private queues, counters, RMPP receive list, timeout and local work items, registration request, and lifetime management around a public `struct ib_mad_agent`.
- `enum ib_mad_state` documents the legal lifecycle of a send work request from construction through backlog, send, wait, early response, cancellation, and completion.
- `struct ib_mad_send_wr_private` combines the public send buffer with UD send WR, two SGEs, DMA mappings, retry state, RMPP segment state, and solicited-flow-control flag.
- `expect_mad_state*()` and `not_expect_mad_state()` provide lockdep-enabled assertions for state-machine transitions.
- Internal prototypes expose `ib_send_mad()`, `ib_find_send_mad()`, `ib_mad_complete_send_wr()`, `ib_mark_mad_done()`, `ib_reset_mad_timeout()`, and `change_mad_state()` to `mad_rmpp.c`.

## Control flow
The header does not execute code directly, but it defines the structures that make `mad.c` and `mad_rmpp.c` interoperate. `mad.c` owns port creation, agent registration, state transitions, and completion dispatch. `mad_rmpp.c` uses the shared send WR fields to advance segment windows and uses the shared receive list on `ib_mad_agent_private` to track inbound multi-packet transfers.

## State and persistence
All state described here is volatile kernel state. Queue counters mirror list membership and active QP WRs. Agent reference counting is paired with a completion for synchronous teardown and an RCU head for final free. Per-port registration tables persist while a MAD-capable port is open and are expected to be empty once agents unregister.

## Dependencies and integration points
The header depends on RDMA public MAD/SMI headers, workqueues, completions, and InfiniBand WC/QP types. Its definitions are consumed by `mad.c`, `mad_rmpp.c`, and related core helpers that need private access to send matching, timeout, RMPP, and registration internals.

## Risks
- Structure layout changes can break assumptions in container-of conversions from CQEs, receive WCs, send buffers, and list entries.
- Queue counters and list membership must stay synchronized; many call sites rely on `count` as a resource limit rather than recomputing list length.
- `__packed` on receive buffer wrappers makes alignment a consideration if fields are added.
- State assertion helpers only warn under lockdep, so invalid transitions still need runtime tests.

## Test signals
- Compile all MAD/RMPP users after any structure or prototype change.
- Use lockdep-enabled tests to exercise normal sends, timeouts, cancellation, early responses, and RMPP segmentation so state assertions can fire.
- Run KASAN/KCSAN style testing around agent unregister and receive free paths because the header encodes most lifetime relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.c

## Purpose
`mad_rmpp.c` implements Reliable Multi-Packet Protocol handling for kernel MAD agents. It segments outgoing RMPP data MADs, processes ACK windows, retries unacknowledged segments, reassembles inbound DATA segments, sends ACK/ABORT responses, and cleans up timed-out or completed receive transactions.

## Important APIs, types, and functions
- `struct mad_rmpp_recv` tracks one inbound RMPP transaction by agent, TID, source QP, SLID, class/version/method/base-version, AH, receive WC chain, current contiguous segment, ACK window, response window, delayed timeout/cleanup work, state, lock, and refcount.
- `ib_process_rmpp_recv_wc()` is the receive entry point from `mad.c`; it validates RMPP version and dispatches DATA, ACK, STOP, and ABORT packets.
- `ib_send_rmpp_mad()` starts active RMPP sends and returns whether normal MAD send handling should continue.
- `ib_process_rmpp_send_wc()` advances a segmented send after each send completion or tells `mad.c` to finish the public send completion.
- `ib_retry_rmpp()` rewinds to `last_ack` and resends from the next unacknowledged segment.
- `ib_cancel_rmpp_recvs()` cancels delayed work and tears down all receive transactions during agent unregister.
- Helpers such as `start_rmpp()`, `continue_rmpp()`, `complete_rmpp()`, `process_rmpp_ack()`, `abort_send()`, `ack_recv()`, `nack_recv()`, and `ack_ds_ack()` implement protocol mechanics.

## Control flow
Inbound DATA segment 1 with FIRST set creates a receive transaction, inserts it on the agent RMPP list, schedules a long timeout if more segments are expected, advances `newwin`, and sends an ACK. Later DATA segments look up the transaction, reject timed-out or out-of-window packets, insert the receive buffer in segment order, and update the contiguous segment cursor. When the LAST segment becomes contiguous, the code ACKs it, computes the final MAD length with IB or OPA payload sizing, marks the transaction complete, schedules cleanup, and returns a reassembled `ib_mad_recv_wc` to `mad.c`.

Inbound ACK packets validate status, segment number, and advertised window. They find the matching outbound send by the normal MAD response-matching logic, update `last_ack`, refresh retries, advance `newwin`, send additional segments when the current window permits, complete no-response sends after the final ACK, or reset the timeout to wait for a response. STOP and ABORT packets abort the matching send, preserving the remote RMPP status in the send WC vendor error.

Outbound active RMPP sends call `send_next_seg()`, which stamps ACTIVE, FIRST, LAST, segment number, and payload/new-window fields, then sends the segment with a short ACK timeout cap. Response sends initialize their window from a completed inbound receive's `repwin` when possible, allowing double-sided RMPP behavior.

## State and persistence
RMPP state is volatile and anchored to `ib_mad_agent_private->rmpp_list`. Receive transactions have three states: ACTIVE, TIMEOUT, and COMPLETE. A 40 second receive timeout aborts incomplete transfers with T2L status; completed transactions stay discoverable for 10 seconds so duplicate ACK and double-sided response handling can work. Each transaction has its own lock for segment/window state and shares the agent lock for list membership.

Outbound state lives in `ib_mad_send_wr_private`: `seg_num`, `last_ack`, `newwin`, `cur_seg`, `last_ack_seg`, retry counters, and timeout. RMPP does not persist data beyond the MAD send/receive lifetime.

## Dependencies and integration points
This file depends on `mad.c` for send posting, send completion, receive freeing, response matching, and timeout integration. It uses public MAD/RMPP headers, AH creation from WC information, RDMA AH destruction, and OPA capability checks for OPA RMPP payload length calculations. Client callbacks still occur through the MAD core after RMPP returns a completed receive WC or send WC.

## Risks
- Segment insertion and contiguous-cursor updates must tolerate duplicate, out-of-order, and old-window packets without leaking receive buffers.
- ACK processing can complete sends, send more segments, or generate ACKs for double-sided transfers; lock release points must avoid using stale send WRs.
- Timeout values are fixed approximations in this version, so slow fabrics can trigger aborts if tests assume packet-lifetime-derived timing.
- OPA and IB RMPP MAD sizes differ; payload length and padding calculations are easy to regress.
- Error paths that call both `nack_recv()` and `ib_free_recv_mad()` must not leave the transaction list with a freed receive WC.

## Test signals
- Exercise single-segment and multi-segment RMPP sends, including no-response sends that complete after final ACK.
- Inject duplicate first segments, duplicate ACKs, ACK window smaller than segment number, bad RMPP versions, bad status, out-of-window DATA, STOP, and ABORT packets.
- Validate timeout cleanup by unregistering an agent with active and completed RMPP receives.
- Test OPA base-version RMPP length calculation separately from classic 256-byte IB MADs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.h

## Purpose
`mad_rmpp.h` is the private interface between the MAD core and the RMPP implementation. It keeps RMPP-specific return codes and function declarations out of the public RDMA MAD API while allowing `mad.c` to delegate segmented send/receive work.

## Important APIs, types, and functions
- The anonymous enum defines `IB_RMPP_RESULT_PROCESSED`, `IB_RMPP_RESULT_CONSUMED`, `IB_RMPP_RESULT_INTERNAL`, and `IB_RMPP_RESULT_UNHANDLED`. `mad.c` uses these values to decide whether to continue normal send completion, suppress completion because RMPP posted another segment, or call the internal RMPP send handler.
- `ib_send_rmpp_mad()` starts an outbound active DATA transfer.
- `ib_process_rmpp_recv_wc()` handles active inbound RMPP packets and returns either a completed receive WC or `NULL` when the packet was consumed.
- `ib_process_rmpp_send_wc()` advances outbound segmentation on send completion.
- `ib_rmpp_send_handler()` frees internally generated ACK/ABORT/STOP send buffers and their AHs.
- `ib_cancel_rmpp_recvs()` tears down inbound RMPP state on agent removal.
- `ib_retry_rmpp()` retries from the last acknowledged segment.

## Control flow
The header's contract is result-code driven. `mad.c` calls the send entry before normal send posting for active RMPP sends, calls the send-WC entry under the agent lock before public completion, and calls the receive-WC entry before invoking client receive callbacks. Return codes decide whether ownership remains with RMPP or returns to the regular MAD core.

## State and persistence
The header has no storage. It defines access to state held in `ib_mad_send_wr_private` and `ib_mad_agent_private` from `mad_priv.h`.

## Dependencies and integration points
It depends on the private MAD structs being visible before inclusion. It is included by both `mad.c` and `mad_rmpp.c` and should remain synchronized with the internal MAD state machine.

## Risks
- Changing return-code meanings without updating `mad.c` can double-post segments, double-complete sends, or leak internal send buffers.
- The prototypes intentionally expose private structs; type churn in `mad_priv.h` must be coordinated.

## Test signals
- Build tests catch signature drift.
- RMPP send/receive integration tests should assert each result-code path: unhandled normal MAD, consumed segment send, internal ACK/ABORT send, and processed completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mr_pool.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/mr_pool.c

## Purpose
`mr_pool.c` provides small exported helpers for maintaining a QP-associated pool of preallocated memory registrations. It lets upper-layer protocols avoid repeated MR allocation on hot I/O paths by taking and returning `struct ib_mr` objects from a caller-owned list.

## Important APIs, types, and functions
- `ib_mr_pool_get()` removes the first MR from a list under `qp->mr_lock`, increments `qp->mrs_used`, and returns `NULL` if the list is empty.
- `ib_mr_pool_put()` returns an MR to a list under the same lock and decrements `qp->mrs_used`.
- `ib_mr_pool_init()` allocates `nr` MRs using `ib_alloc_mr()` or `ib_alloc_mr_integrity()` depending on `enum ib_mr_type`, then appends them to the pool list.
- `ib_mr_pool_destroy()` removes all MRs from the list and deregisters them with `ib_dereg_mr()`.

## Control flow
Initialization loops until the requested pool size is reached. On allocation failure it destroys any MRs already added and returns the allocation error. Get/put are constant-time list operations. Destroy holds `qp->mr_lock` only while removing each list entry, releases it around `ib_dereg_mr()`, then reacquires it for the next entry.

## State and persistence
The pool is a caller-supplied `struct list_head` whose entries are linked through `ib_mr::qp_entry`. `qp->mrs_used` tracks checked-out MRs. There is no durable state; all MRs are RDMA core objects tied to the QP's PD and must be deregistered before teardown.

## Dependencies and integration points
The helpers use RDMA verbs allocation and deregistration APIs plus the QP's `mr_lock`. They export symbols for RDMA ULPs and drivers that maintain per-QP MR pools.

## Risks
- Callers must not destroy a pool while MRs are checked out; this helper only destroys entries currently on the list.
- The list must contain only MRs that belong to the same QP/PD context expected by the caller.
- `qp->mrs_used` can underflow or become inaccurate if callers put the same MR twice or mix lists.
- Because `ib_dereg_mr()` runs outside the spinlock, concurrent get/put during destroy must be prevented by higher-level teardown ordering.

## Test signals
- Unit or fault-injection tests should cover partial allocation failure and verify that already allocated MRs are deregistered.
- Concurrency tests should exercise get/put from multiple CPUs and verify `mrs_used` returns to zero.
- Integrity MR paths should be built and tested separately from regular MR allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/mr_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/multicast.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/multicast.c

## Purpose
`multicast.c` implements RDMA SA multicast join and leave management for InfiniBand-capable ports. It serializes joins for the same MGID, tracks membership by join-state bit, sends SA `MCMemberRecord` SET and DELETE requests, exposes joined records to callers, builds AH attributes from multicast records, and reacts to port, LID, pkey, and client-reregister events.

## Important APIs, types, and functions
- Exported APIs are `ib_sa_join_multicast()`, `ib_sa_free_multicast()`, `ib_sa_get_mcmember_rec()`, and `ib_init_ah_from_mcmember()`.
- `struct mcast_device` is per RDMA device and contains an event handler plus a flexible array of `mcast_port` objects.
- `struct mcast_port` owns an RB tree of groups keyed by MGID and a refcount/completion used during device removal.
- `struct mcast_group` stores the current SA member record, pending and active member lists, membership counters by join-state type, group state, active SA query, pkey index, leave state, and retry count.
- `struct mcast_member` wraps the public `ib_sa_multicast`, caller client, current state, group pointer, list entry, and lifetime completion.
- `mcast_work_handler()` is the serialized group worker that processes pending joins, SA joins, leaves, and event recovery.
- `join_handler()` and `leave_handler()` are SA query callbacks.

## Control flow
`mcast_init()` creates an ordered workqueue, registers an SA client, and registers the `ib_multicast` client. Device add allocates a `mcast_device`, initializes multicast-capable ports, stores client data, and registers an event handler. Device remove unregisters events, flushes multicast work, drops each port's base reference, waits for groups to drain, and frees the device wrapper.

`ib_sa_join_multicast()` allocates a member, takes a reference on the caller's SA client, acquires or creates the MGID group, and queues the member. The group worker processes one logical action at a time. If the group already has the requested join-state bits and the supplied record is compatible, the member joins locally and the caller callback runs immediately. Otherwise the worker sends an SA SET request and returns until `join_handler()` updates the group record and restarts the worker. After members leave, `get_leave_state()` identifies SA join-state bits with no remaining active members and sends SA DELETE requests.

`ib_sa_free_multicast()` removes a member from pending or active lists. If an active member was the last user of a join-state bit, the group is made busy and work is queued so a leave can be sent. Event handling marks groups for full error recovery or pkey-specific recovery. Group error processing reports `-ENETRESET` to active members and clears membership so callers can rejoin.

## State and persistence
All state is in memory. The RB tree is protected by `mcast_port.lock`; group lists, counters, and state are protected by `mcast_group.lock`. Group references combine an atomic group refcount with a port refcount so device removal waits until active groups finish. Member lifetime uses a refcount and completion so callbacks can safely free multicast objects after the core drops its references.

The SA maintains actual fabric membership; this file mirrors it in `group->rec.join_state` and `members[]`. It does not persist membership across driver unload, port reset, or process restart.

## Dependencies and integration points
The implementation depends on `sa.h` query helpers, RDMA device client registration, IB event handlers, GID cache helpers, pkey lookup, AH attribute helpers, netdevice-aware RoCE GID lookup, ordered workqueues, RB trees, and exported SA multicast ABI used by ULPs such as IPoIB.

## Risks
- Join serialization is deliberate. Bypassing it can race two different records for the same MGID, producing incompatible SA state.
- MGID zero permits duplicates during insertion, which is special-case behavior that must be preserved.
- Callback return values can trigger `ib_sa_free_multicast()` from inside worker or callback context; refcounts are critical.
- PKey events compare cached pkey index with a fresh lookup. Incorrect handling can either miss required resets or reset healthy groups.
- `rdma_find_gid_by_port()` in `ib_init_ah_from_mcmember()` returns a GID attribute that is moved into AH attributes; callers must later destroy AH attributes as documented.

## Test signals
- Test multiple simultaneous joins to one MGID with compatible and incompatible records.
- Verify each join-state bit type increments and decrements correctly and that SA DELETE is sent only when the last active member of a state leaves.
- Inject SA join and leave failures, including leave retry exhaustion.
- Trigger port error, LID change, client reregister, and pkey change events and verify callbacks and rejoin behavior.
- Build and runtime tests should include both IB and RoCE AH initialization paths, with net namespace filtering for netdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/multicast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/netlink.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/netlink.c

## Purpose
`netlink.c` is the generic NETLINK_RDMA dispatcher for RDMA core. It registers per-client callback tables, validates RDMA netlink message client/op IDs, autoloads protocol modules, enforces admin permissions, dispatches doit and dump callbacks, and provides unicast/multicast helpers plus per-net namespace socket setup.

## Important APIs, types, and functions
- `rdma_nl_register()` and `rdma_nl_unregister()` publish and remove callback tables for RDMA netlink clients.
- `rdma_nl_chk_listeners()`, `rdma_nl_unicast()`, `rdma_nl_unicast_wait()`, and `rdma_nl_multicast()` wrap kernel netlink operations for RDMA users.
- `ibnl_put_msg()` and `ibnl_put_attr()` are exported helpers for legacy RDMA netlink message construction.
- `rdma_nl_rcv_msg()` validates a message, obtains the callback table, checks `RDMA_NL_ADMIN_PERM`, and selects dump or doit handling.
- `rdma_nl_rcv_skb()` is a local variant of `netlink_rcv_skb()` that also permits non-request LS responses.
- `rdma_nl_net_init()` and `rdma_nl_net_exit()` create and release each namespace's NETLINK_RDMA socket.

## Control flow
`rdma_nl_init()` initializes one rwsem per RDMA netlink client. Callback tables are stored with release semantics and protected against unregister by the per-client rwsem. On receive, the code extracts client and op from `nlmsg_type`, checks bounds with `is_nl_msg_valid()`, takes the client read lock, autoloads `rdma-netlink-subsys-%u` once if no table exists, and dispatches the callback if present.

For most clients, `NLM_F_DUMP` selects `netlink_dump_start()` and regular requests call `.doit`. IWCM is still forced through dump handling for compatibility. LS is special because LS responses overload a netlink flag and because RDMA_NL_LS is allowed to receive kernel-initiated response messages without `NLM_F_REQUEST`.

## State and persistence
Global state is `rdma_nl_types[]`, one callback table pointer and rwsem per client. Per-net namespace state is the `NETLINK_RDMA` socket in `struct rdma_dev_net`. No durable state is stored.

## Dependencies and integration points
This file depends on Linux netlink core, network namespaces, RDMA net namespace helpers, `rdma/rdma_netlink.h` protocol definitions, module autoloading, and callbacks registered by IWCM, LS, NLDEV, and other RDMA netlink clients. NLDEV is the only client allowed outside `init_net` in this version.

## Risks
- The hard-coded `max_num_ops` table must be updated with new RDMA netlink clients; the `BUILD_BUG_ON` catches only client-count changes.
- Callback unregister waits for in-flight commands, but callback implementations must still manage their own object lifetimes.
- Permission is enforced at the callback-table flag level. New admin operations must set `RDMA_NL_ADMIN_PERM`.
- Non-init net namespace support is intentionally restricted; expanding it requires auditing callbacks for namespace-safe object lookup.
- LS and IWCM compatibility branches are easy to break if generic netlink dispatch is simplified.

## Test signals
- Module load/unload tests should verify `rdma_nl_exit()` does not warn about registered callback tables.
- Netlink fuzzing should cover invalid client/op values, missing callbacks, malformed headers, dump vs doit flags, ACK paths, and permission denial.
- Namespace tests should confirm NLDEV works outside init_net and other clients are rejected.
- Listener and multicast tests should verify `RDMA_NL_GROUP_NOTIFY` behavior with and without subscribers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/nldev.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/nldev.c

## Purpose
`nldev.c` implements the RDMA_NL_NLDEV netlink client, which is the main userspace control and introspection interface for RDMA devices. It reports device and port properties, dumps resource-tracker objects, exposes driver-specific details, controls RDMA counter modes and optional hardware counters, manages RDMA links and subdevices, reports character devices, emits monitor notifications, and configures FRMR pools.

## Important APIs, types, and functions
- Exported helpers include `rdma_nl_put_driver_string()`, `rdma_nl_put_driver_u32()`, `rdma_nl_put_driver_u32_hex()`, `rdma_nl_put_driver_u64()`, `rdma_nl_put_driver_u64_hex()`, `rdma_nl_get_privileged_qkey()`, `rdma_nl_stat_hwcounter_entry()`, `rdma_link_register()`, `rdma_link_unregister()`, and `rdma_nl_notify_event()`.
- `nldev_policy[]` defines validation for all NLDEV attributes, including device/port identifiers, resource IDs, statistics attributes, system settings, monitor event fields, and FRMR pool keys.
- `fill_dev_info()` and `fill_port_info()` construct device and port replies, including GUIDs, firmware, protocol, node type, DIM flag, port state, LID/SM LID/LMC, netdevice association, and capability flags.
- Resource fill helpers cover QP, raw QP, CM ID, CQ, raw CQ, MR, raw MR, PD, context, SRQ, raw SRQ, and counter entries.
- `res_get_common_doit()` and `res_get_common_dumpit()` implement the shared one-object and dump paths over RDMA restrack xarrays.
- Link management uses registered `struct rdma_link_ops` implementations through `nldev_newlink()` and `nldev_dellink()`.
- Statistics handlers include `nldev_stat_set_doit()`, `nldev_stat_del_doit()`, `nldev_stat_get_doit()`, `nldev_stat_get_dumpit()`, and `nldev_stat_get_counter_status_doit()`.
- FRMR pool handlers include `nldev_frmr_pools_get_dumpit()` and `nldev_frmr_pools_set_doit()`.
- `nldev_cb_table[]` maps all `RDMA_NLDEV_CMD_*` operations to doit/dump callbacks and admin-permission flags.

## Control flow
`nldev_init()` registers `nldev_cb_table` with the generic RDMA netlink dispatcher. GET commands parse identifiers, look up devices with `ib_device_get_by_index()` in the sender's net namespace, fill an skb, unicast the reply, and drop the device reference. Dump commands use netlink callback cursors in `cb->args[0]` to resume across devices, ports, resources, or FRMR pools.

Resource-specific commands either require a device-level resource ID or, for per-port resources such as QP and counters, a valid port. The common dump path opens a nested resource table, walks the restrack xarray under its lock, skips driver-detail-marked resources unless requested, takes a restrack reference before dropping the xarray lock, fills one nested entry, then resumes. Fill functions add common fields such as PID or kernel resource name and call optional driver hooks for extended or raw details.

Admin commands rename devices, move devices to another net namespace, toggle DIM, create/delete RDMA links, create/delete subdevices, change system netns and privileged QKey modes, bind/unbind QP counters, change counter auto mode, enable/disable optional hardware counters, adjust FRMR aging period, and pin FRMR pool handles. Monitor events build a compact NLDEV_CMD_MONITOR message and multicast it to `RDMA_NL_GROUP_NOTIFY`.

## State and persistence
The file owns a small amount of global state: `privileged_qkey`, the registered link-ops list protected by `link_ops_rwsem`, and the NLDEV callback table while registered. Most reported state comes from live RDMA devices, their restrack roots, counters, hw stats, FRMR pools, net namespace membership, and netdevices. System toggles such as privileged QKey mode and compatible-device netns mode remain kernel runtime state, not durable configuration.

## Dependencies and integration points
`nldev.c` integrates with the generic RDMA netlink dispatcher in `netlink.c`, RDMA device lookup and lifetime rules, restrack, CMA internals for CM ID reporting, uverbs context objects, RDMA counters, hardware stats, dynamic link providers such as RXE, character-device client info, FRMR pool management, netdevice association, and net namespaces. Userspace tools such as `rdma` from iproute2 consume this ABI.

## Risks
- Netlink ABI compatibility is critical. Attribute type, nesting, command, and permission changes can break userspace.
- Resource dumps walk live xarrays while objects are being created and destroyed. Missing restrack references or incorrect `-EAGAIN` handling can race or omit entries.
- Sensitive identifiers such as lkey/rkey and raw driver details are gated by `CAP_NET_ADMIN`; new fields must be audited for disclosure.
- Several handlers allocate reply skbs before performing mutable operations. Error cleanup must free skbs and release device/restrack/cdev references on every path.
- `stat_get_doit_qp()` uses static local mode/mask variables, which is unusual for a request handler and should be treated carefully under concurrency.
- Dynamic link deletion can unregister devices; handlers must not use device pointers after operations that consume references.
- Monitor error logging assumes netdevice lookup succeeds in some event cases; attach/rename failure paths should be tested with disappearing netdevices.

## Test signals
- Netlink ABI tests should cover every command in `nldev_cb_table` for required attributes, malformed attributes, permission checks, namespace lookup, and dump cursor resume.
- Resource tests should create QP, CQ, PD, MR, SRQ, CM ID, context, and counter objects, then verify both summary and detailed dumps, including driver-detail filtering.
- CAP_NET_ADMIN tests should check raw resource commands, lkey/rkey exposure, link/subdevice admin, system settings, stat mutation, and FRMR pool mutation.
- Counter tests should cover auto/manual QP counter binding, unbinding, optional hwcounter dynamic masks, default counter queries, and disabled-counter filtering.
- Monitor tests should subscribe to `RDMA_NL_GROUP_NOTIFY` and verify register, unregister, rename, netdev attach/detach, and netdev rename payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/nldev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/opa_smi.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/opa_smi.h

## Purpose
`opa_smi.h` declares Omni-Path Architecture SMI directed-route helpers and provides inline checks for whether an OPA SMP should be handled locally by a device's SMA/SM `process_mad` callback.

## Important APIs, types, and functions
- `opa_smi_handle_dr_smp_recv()` updates or validates an inbound OPA directed-route SMP according to switch/endport role, current port, and physical port count.
- `opa_smi_get_fwd_port()` returns the port to use when forwarding an OPA directed-route SMP.
- `opa_smi_check_forward_dr_smp()` classifies an OPA DR SMP as local, send, forward, or discard.
- `opa_smi_handle_dr_smp_send()` handles outgoing OPA DR SMP path updates and validation.
- `opa_smi_check_local_smp()` returns `IB_SMI_HANDLE` for outbound-direction DR SMPs that have reached the end of their directed route and can be passed to `device->ops.process_mad`.
- `opa_smi_check_local_returning_smp()` returns `IB_SMI_HANDLE` for returning DR SMPs whose hop pointer has reached zero and can be passed to the local SM.

## Control flow
The inline local checks are used by `mad.c` before deciding whether an OPA directed-route SMP should be sent on QP0, forwarded, discarded, or processed locally. They require a device `process_mad` callback and inspect OPA SMP direction, `hop_ptr`, and `hop_cnt`.

## State and persistence
The header owns no state. It reads fields from `struct opa_smp` and the RDMA device ops table. Any path mutation happens in the out-of-line helpers declared here.

## Dependencies and integration points
It depends on public IB and OPA SMI headers plus the local `smi.h` action enums. Its main consumer in this subset is `mad.c`, which uses it for OPA-specific DR SMP processing alongside classic IB SMI helpers.

## Risks
- The local-handle predicates encode OPA spec hop-pointer rules. Off-by-one changes can misroute management packets or prevent local SMA/SM handling.
- The checks require `device->ops.process_mad`; devices without that callback must discard local handling even if the path position matches.
- OPA and classic IB SMP structures are similar but not interchangeable; callers must only use these helpers on OPA SMPs.

## Test signals
- Directed-route OPA MAD tests should cover start, intermediate, local end, returning end, and discard cases.
- Build coverage should include OPA-capable RDMA configurations and classic IB-only configurations to catch include and type drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/opa_smi.h -->
