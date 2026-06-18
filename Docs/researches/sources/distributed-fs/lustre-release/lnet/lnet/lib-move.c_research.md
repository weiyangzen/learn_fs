# sources/distributed-fs/lustre-release/lnet/lnet/lib-move.c

## Purpose

`lib-move.c` is LNet's data movement core. It sends and receives LNet messages, chooses local and peer NIs, enforces NI/peer/router credits, parses incoming PUT/GET/REPLY/ACK traffic, handles routed forwarding, tracks response timeouts, drives resend and recovery queues, and exposes public `LNetPut()`, `LNetGet()`, `LNetDist()`, `lnet_parse()`, and related helpers.

The file is the integration point where MDs, MEs, portals, peers, routes, NIs, health, CPT locality, LND callbacks, test failure injection, and monitor-thread recovery converge.

## Important APIs, Types, and Functions

- `struct lnet_send_data` carries pathway-selection state: chosen local NI, destination/gateway peer NIs, final destination, peer objects, source/destination/router NIDs, CPTs, message, and send-case flags.
- Stats helpers `lnet_incr_stats()`, `lnet_sum_stats()`, and `lnet_usr_translate_stats()` maintain per-element send/receive/drop counters by message type.
- Failure injection uses `lnet_fail_nid()` and `fail_peer()` with `the_lnet.ln_test_peers`.
- Buffer helpers `lnet_iov_nob()`, `lnet_kiov_nob()`, `lnet_extract_kiov()`, and `lnet_copy_kiov2iter()` support vector length, subrange extraction, and page-vector copying into kernel iterators.
- LND boundary helpers `lnet_ni_recv()`, `lnet_prep_send()`, `lnet_ni_send()`, and `lnet_ni_eager_recv()` call `lnd_recv`, `lnd_send`, and `lnd_eager_recv`.
- Credit functions `lnet_post_send_locked()`, `lnet_return_tx_credits_locked()`, `lnet_post_routed_recv_locked()`, and `lnet_return_rx_credits_locked()` manage NI, peer, peer-router, and router-buffer credits and delayed queues.
- Path selection is centered on `lnet_select_pathway()`, `lnet_handle_send_case_locked()`, `lnet_get_best_ni()`, `lnet_select_peer_ni()`, `lnet_handle_find_routed_path()`, and the source/destination/MR/NMR case handlers.
- Monitor and recovery code includes `lnet_monitor_thread()`, `lnet_monitor_thr_start()`, `lnet_monitor_thr_stop()`, response tracker helpers, resend queues, local/peer NI recovery, and `lnet_mt_event_handler()`.
- Incoming parse path includes `lnet_parse()`, `lnet_parse_forward_locked()`, `lnet_parse_local()`, `lnet_parse_put()`, `lnet_parse_get()`, `lnet_parse_reply()`, and `lnet_parse_ack()`.
- Public operations are `LNetPut()`, `LNetGet()`, optimized GET reply helpers `lnet_create_reply_msg()` and `lnet_set_reply_msg_len()`, and distance API `LNetDist()`.

## Control Flow

The send flow starts with an upper layer preparing a message through `LNetPut()` or `LNetGet()`. Those functions allocate a message, validate and attach a free-floating MD, fill the wire header, build the local send event, optionally attach a response tracker, and call `lnet_send()`. `lnet_send()` marks the message sending, delegates to `lnet_select_pathway()`, and if credits are immediately available calls `lnet_ni_send()`.

`lnet_select_pathway()` locks a current CPT, derives an MD locality CPT from the first backing page, creates or finds the destination peer NI, optionally initiates peer discovery, classifies the send as source-specified or source-any, local or remote, MR or NMR, response or request, then dispatches to a case handler. Case handlers either use an explicit local NI, prefer a stable source NI for non-MR peers, search local peer nets before routes for MR peers, or find a route/gateway through `lnet_handle_find_routed_path()`. Final send setup in `lnet_handle_send()` updates round-robin sequence numbers, may switch CPT locks after computing the selected NI CPT, commits the message, sets source/destination wire NIDs, records response-tracker next hop, and posts send credits.

Transmit credit posting first checks deadline and peer aliveness for routed messages, aborts if the MD was unlinked, then consumes peer TX credits and NI TX credits. If either credit pool goes negative, the message is queued on the peer or NI delayed queue. Delay rules can also queue a message. Credit return wakes the next delayed message and carefully switches CPT locks if the queued message belongs to another CPT.

The receive flow enters `lnet_parse()` from an LND with a header, source NID, private LND state, and RDMA flag. It validates message type and payload size, updates router liveness for reserved GET pings, rejects bad destination/routing cases, applies failure/drop rules, allocates and initializes a message, finds the sender peer NI, marks sender status/aliveness, commits the receive message, and either forwards it through router-buffer credit posting or parses it locally. Local parsing matches PUT/GET traffic against portal MDs, attaches reply/ack MDs by wire handle, calls `lnet_ni_recv()` to pull payload, or sends a REPLY for GET.

The monitor thread waits for LNet start then loops once per second while running. It checks routers, resends queued messages, expires response trackers at half transaction-timeout cadence, pings local and peer NIs in recovery queues, emits rate-controlled health console updates, and queues ping-buffer updates. Stop transitions the monitor to stopping/shutdown, flushes ping-buffer work, wakes the thread, waits on a semaphore, then cleans response trackers, recovery queues, and resend queues.

## State and Persistence Behavior

All state is in-memory kernel state. Messages carry pointers to attached MDs, TX/RX NIs, peer NIs, router buffers, private LND state, response/recovery flags, deadlines, retry counts, original source/router NID parameters, and event fields. MD refcounts and NI/peer refcounts keep objects alive across unlock/send/receive/finalize boundaries.

Credit state is distributed across `struct lnet_tx_queue`, `struct lnet_peer_ni`, router buffer pools, and peer router queues. Negative credit counts represent blocked queues and are paired with non-empty delayed lists. Return paths restore credits and schedule queued work.

Response tracking attaches `struct lnet_rsp_tracker` to an MD and per-CPT monitor queue. Receipt invalidates the handle for later cleanup. Expiry unlinks the MD, increments timeout counters, and penalizes the next-hop peer health. If the monitor cannot look up an MD that still has a valid tracker, it moves the tracker to a zombie queue until final MD detach or shutdown cleanup.

Recovery queues hold local NIs and peer NIs with extra refs. Recovery sends reserved-portal GET pings using temporary MDs and event metadata. On send/reply/unlink events, the handler updates pending/failed flags and health.

## Dependencies and Integration Points

`lib-move.c` depends on almost every LNet subsystem: peer tables, route tables, router checker, portal matching, MD/ME resource handles, message allocation/finalization, NI health/status, ping buffers, discovery, dynamic configuration sequence checks, delay/drop rules, libcfs failpoints, and per-CPT locks/counters. It calls LND operations `lnd_send`, `lnd_recv`, `lnd_eager_recv`, and optional `lnd_get_dev_prio`.

It integrates upward with public LNet consumers through `LNetPut()`, `LNetGet()`, `LNetDist()`, event handlers, ACK/REPLY/PUT/GET semantics, and MD callbacks. It integrates downward with LNDs through header parse/receive/send callbacks and optimized RDMA GET reply helpers.

## Risks and Edge Cases

- Locking is complex: code moves among `lnet_net_lock(cpt)`, `lnet_res_lock(cpt)`, NI locks, peer locks, and spinlocks, sometimes dropping locks around LND callbacks and reacquiring possibly different CPT locks.
- Credit invariants rely on negative counts matching non-empty queues. Imbalance can stall sends/receives or overrun router buffers.
- Path selection combines health, selection priority, direct DMA device priority, NUMA distance, available credits, and round-robin sequence numbers. Small changes can alter routing fairness or locality.
- Peer discovery can replace peer ownership and queue the message for discovery, so callers must treat `LNET_DC_WAIT` as non-final and not touch freed message state.
- Response tracker lifetime crosses MD unlink, monitor expiry, and shutdown paths. Zombie tracker handling exists because MD lookup can fail while the tracker is still logically attached.
- `lnet_check_message_drop()` enforces deadlines only for non-routing originators; routers intentionally forward beyond upper-layer deadlines.
- Incoming `lnet_parse()` must always call back into `lnd_recv()` for accepted packets, even drops, so LND resources are released.
- Routed receive uses eager receive when available before credits exist; LNDs without eager receive mark ready-delay and queue.
- Recovery intentionally drops NI/peer refs before sending pings to avoid deadlocks with deletion, then looks objects up again; races with user deletion are expected.
- Public `LNetPut()` and `LNetGet()` return success once the operation is queued/sent; completion and many failures are asynchronous events.

## Test Signals

High-value tests include send-path selection for every source/local/remote/MR/NMR/response case; route comparison by UDSP preference, priority, hops, gateway health, queue length, credits, and sequence; NI selection by fatal flag, health, selection priority, GPU device priority, NUMA distance, credits, and round robin; credit exhaustion and wakeup for peer TX, NI TX, peer router, and router-buffer pools; MD unlink races canceling sends; deadline and peer-dead drops; peer discovery queuing; failure/drop/delay rule injection; incoming parse validation for bad payloads, bad destinations, disabled routing, asymmetrical routes, local PUT/GET/REPLY/ACK matching, truncation, ACK disable, and optimized RDMA GET; delayed PUT drop/resume; response tracker attach/update/expire/zombie cleanup; monitor start/stop cleanup; local and peer NI recovery state transitions; `LNetPut()`/`LNetGet()` invalid MD and allocation failures; and `LNetDist()` local, same-net, routed, namespace-priority, and unreachable cases.
