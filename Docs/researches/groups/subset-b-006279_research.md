# Research: subset-b-006279

Grouped source-tree-aligned research for the requested SCTP stream/transport receive path, net shaper, and SMC build metadata files. Each section preserves the source path in its title and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream.c

## Purpose
Implements SCTP stream allocation, stream extension lifecycle, stream reset/reconfiguration request send paths, and inbound RE-CONFIG parameter processing. It owns the association stream counters, per-stream sequence reset state, and the mechanics that move queued chunks when stream counts shrink or grow.

## Important APIs, Types, And Functions
Exports `sctp_stream_init`, `sctp_stream_init_ext`, `sctp_stream_free`, `sctp_stream_clear`, `sctp_stream_update`, `sctp_send_reset_streams`, `sctp_send_reset_assoc`, `sctp_send_add_streams`, and the `sctp_process_strreset_*` handlers. Key state lives in `struct sctp_stream`, `struct sctp_association`, `struct sctp_stream_out_ext`, and RE-CONFIG parameter structs such as `sctp_strreset_outreq`, `sctp_strreset_inreq`, `sctp_strreset_tsnreq`, and `sctp_strreset_addstrm`.

## Control Flow
Initialization preallocates genradix-backed incoming/outgoing stream arrays, sets outgoing stream state to open, and selects the interleave operations table. Shrink/update paths first unschedule all scheduler queues, fail queued chunks for removed outgoing stream ids, migrate extensions, and reschedule survivors. Local reset/add requests validate peer capabilities, outstanding reset state, stream bounds, and chunk-size limits before creating RE-CONFIG chunks and closing affected outgoing streams until responses arrive. Inbound reset handlers enforce request sequence windows, replay cached results for duplicate requests, update stream mids/ssns or TSN maps, create ULP notifications, and return response chunks. Response handling looks up the original request in `asoc->strreset_chunk`, applies success/failure side effects, reopens streams, emits notifications, and drops the reconf timer/reference when all outstanding parameters complete.

## State And Persistence
All state is in-memory per association: stream counts, genradix arrays, per-stream `mid`/`mid_uo`, incoming `mid`, stream open/closed state, `strreset_inseq`, `strreset_outseq`, `strreset_outstanding`, cached `strreset_result[]`, and held `strreset_chunk`. No durable persistence exists. Correctness depends on holding chunk/transport references while timers are active.

## Dependencies And Integration Points
Integrates with SCTP schedulers (`stream_sched.h`), output queue chunk lists, RE-CONFIG chunk builders, state-machine primitive `sctp_primitive_RECONF`, TSN map helpers, ULP event factories, reconf timers on transports, and PR-SCTP accounting.

## Risks
High-risk areas are off-by-one stream bounds, failing to restore stream state after send failure, mismatched `strreset_outstanding` accounting for combined requests, timer/reference leaks around `strreset_chunk`, and shrinking outgoing streams while chunks or scheduler extension state still exist.

## Test Signals
Exercise full and per-stream outgoing/incoming reset, duplicate/out-of-window RE-CONFIG requests, reset while outqueue is non-empty, association TSN reset, add-stream success/failure rollback, scheduler switching around stream count changes, and notification flags for denied/failed/performed responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_interleave.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream_interleave.c

## Purpose
Implements SCTP message interleaving support for I-DATA and I-FORWARD-TSN while preserving the legacy DATA/FORWARD-TSN operations table. It provides the `struct sctp_stream_interleave` callbacks used by transmit numbering, receive validation, ULP event reassembly/order delivery, PR-SCTP skipping, reneging, and partial-delivery aborts.

## Important APIs, Types, And Functions
The exported entry point is `sctp_stream_interleave_init`. Important internal callbacks include `sctp_make_idatafrag_empty`, `sctp_chunk_assign_mid`, `sctp_validate_data`, `sctp_validate_idata`, `sctp_ulpevent_idata`, `sctp_generate_iftsn`, `sctp_validate_iftsn`, `sctp_report_iftsn`, and `sctp_handle_iftsn`. Key state is in `struct sctp_stream_in` (`mid`, `mid_uo`, `fsn`, `fsn_uo`, partial-delivery flags), `struct sctp_ulpq` (`reasm`, `reasm_uo`, `lobby`), and skip records.

## Control Flow
Transmit fragments receive MID and FSN values across every chunk in a datamsg, with unordered messages using the unordered MID counter. Receive validation rejects DATA or I-DATA with already skipped ordered sequence numbers. Ordered I-DATA is sorted by stream/MID/FSN in `reasm`, reassembled when a complete sequence or partial-delivery threshold is reached, then held in `lobby` until the next expected MID. Unordered I-DATA uses `reasm_uo` and separate partial-delivery state. I-FORWARD-TSN generation coalesces abandoned chunks into up to ten skip entries and queues a control chunk. I-FORWARD-TSN receive advances the TSN map, flushes fragments up to the forwarded TSN, aborts partial delivery when required, and skips ordered MID dependencies to release lobby data.

## State And Persistence
All state is volatile per association/stream. The selected interleave ops pointer switches between legacy DATA and I-DATA behavior based on peer `intl_capable`. Receive queues own skb-backed ULP events until delivery or flush.

## Dependencies And Integration Points
Relies on `ulpqueue.c` for common ULP queueing and reassembled skb construction, `ulpevent.c` for receive events and partial-delivery notifications, `tsnmap.c` for cumulative TSN advancement, outqueue abandoned lists for PR-SCTP, and socket receive queues for ULP delivery.

## Risks
The main risks are ordering bugs in stream/MID/FSN sorted queues, partial-delivery state not being cleared on skips, incorrect unordered MID handling, I-FORWARD-TSN skip coalescing truncation, skb queue ownership mistakes, and inconsistent behavior between legacy DATA and I-DATA paths.

## Test Signals
Cover fragmented ordered and unordered I-DATA, partial delivery with and without EOR, interleaved streams, skipped ordered MIDs via I-FORWARD-TSN, reneging under receive memory pressure, duplicate or stale MID validation, and fallback to legacy callbacks when `intl_capable` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_interleave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream_sched.c

## Purpose
Defines the common SCTP stream scheduler API and the built-in FCFS scheduler. It owns scheduler registration, scheduler switching, per-stream scheduler value get/set, and common dequeue bookkeeping for all scheduler implementations.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_register`, `sctp_sched_ops_init`, `sctp_sched_set_sched`, `sctp_sched_get_sched`, `sctp_sched_set_value`, `sctp_sched_get_value`, `sctp_sched_dequeue_done`, `sctp_sched_dequeue_common`, `sctp_sched_init_sid`, and `sctp_sched_ops_from_stream`. The central interface is `struct sctp_sched_ops`.

## Control Flow
`sctp_sched_ops_init` registers FCFS, PRIO, RR, FC, and WFQ implementations in a static table. Scheduler switching frees old scheduler state, initializes the new scheduler and existing stream extensions, then re-enqueues one representative datamsg per queued message. FCFS itself dequeues either the current unfinished message stream or the first chunk in the global outqueue. `sctp_sched_dequeue_done` preserves `stream.out_curr` for multi-fragment messages when the peer lacks interleaving, ensuring one message is completed before scheduler fairness can pick another stream.

## State And Persistence
State is in-memory per association outqueue and per stream extension. `outqueue.sched` points to the active ops table; `stream.out_curr` pins a partially dequeued datamsg.

## Dependencies And Integration Points
Integrates with `sctp_outq`, datamsg chunk lists, stream extension allocation in `stream.c`, and all concrete schedulers. Socket options or association setup call the set/get APIs.

## Risks
Risks include scheduler switch rollback leaving stale extension fields, incorrect `out_curr` handling breaking message atomicity when ndata is unavailable, missing stream extension allocation before scheduler value set, and outqueue length mismatch if common dequeue is bypassed.

## Test Signals
Switch schedulers with queued data, send fragmented messages with and without peer interleaving, set/get scheduler values on valid and invalid stream ids, inject init failures during scheduler switch, and assert `out_qlen` and chunk list membership after dequeue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_fc.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream_sched_fc.c

## Purpose
Implements Fair Capacity (`SCTP_SS_FC`) and Weighted Fair Queueing (`SCTP_SS_WFQ`) schedulers from RFC 8260 sections 3.5 and 3.6. Both use a per-stream cumulative length metric; WFQ adds configurable stream weights.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_fc_init` and `sctp_sched_ops_wfq_init`. Important helpers are `sctp_sched_fc_init`, `sctp_sched_fc_init_sid`, `sctp_sched_fc_sched`, `sctp_sched_fc_enqueue`, `sctp_sched_fc_dequeue`, and `sctp_sched_fc_dequeue_done`. Per-stream state lives in `sctp_stream_out_ext.fc_list`, `fc_length`, and `fc_weight`; global ordering is `stream->fc_list`.

## Control Flow
Initialization creates a global fair-capacity list and initializes each stream extension with length zero and weight one. Enqueue schedules the stream that owns the datamsg if not already present, ordered by normalized `fc_length / weight`. Dequeue selects `out_curr` when pinned, otherwise the first stream in the fair list, then removes the chunk from global and stream lists. After dequeue, the stream's length increases by the sent skb length, large counters are normalized before overflow, empty streams are unscheduled, and non-empty streams are repositioned by weighted normalized length.

## State And Persistence
All scheduler state is volatile per association. WFQ weight is persisted only in the stream extension while the association exists.

## Dependencies And Integration Points
Uses the common scheduler helpers in `stream_sched.c`, the outqueue datamsg layout, and `SCTP_SO(stream, sid)->ext` allocated by stream code.

## Risks
Risk centers on weighted comparison overflow, list insertion around the sentinel when the list is empty, counter normalization changing relative fairness, and maintaining identical behavior for FC and WFQ except for non-default weights.

## Test Signals
Send mixed-size messages across streams, verify WFQ weight changes affect order, test counter normalization near `U32_MAX`, unschedule empty streams, and switch into/out of FC/WFQ with already queued chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_fc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_prio.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream_sched_prio.c

## Purpose
Implements SCTP priority stream scheduling. Streams are grouped by priority, priority groups are served in ascending priority order, and streams within a priority are round-robined.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_prio_init`. Important helpers include `sctp_sched_prio_get_head`, `sctp_sched_prio_set`, `sctp_sched_prio_sched`, `sctp_sched_prio_unsched`, `sctp_sched_prio_dequeue`, and `sctp_sched_prio_dequeue_done`. `struct sctp_stream_priorities` holds a priority group, active stream list, next stream pointer, and reference count.

## Control Flow
Each stream extension references a priority head. Setting a priority allocates or reuses a head, unschedules the stream if active, switches the reference, then reschedules it if needed. Enqueue schedules the stream into its priority group's active list and schedules the group into the global `prio_list` if this is its first active stream. Dequeue chooses the current pinned stream or the first scheduled priority group's next stream. Completion advances the group's round-robin pointer and unschedules streams that have no queued data.

## State And Persistence
Priority heads and per-stream references live for the association only. Reference counts free unused priority groups when streams change priority or are freed.

## Dependencies And Integration Points
Uses stream scheduler common helpers, stream extensions, outqueue datamsg queues, and priority values set via scheduler socket options.

## Risks
Risks include reference leaks or premature frees of priority heads, invalid next pointers when unscheduling the current stream, preserving sorted priority-group order, and ensuring scheduler switch cleanup clears extension scheduler fields.

## Test Signals
Set multiple streams to the same and different priorities, change priority while queued, dequeue fragmented messages, empty the last stream in a priority group, switch schedulers, and validate priority head refcounts with stream free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_prio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_rr.c -->
# sources/distributed-fs/ceph-client/net/sctp/stream_sched_rr.c

## Purpose
Implements round-robin stream scheduling for SCTP outgoing streams. It keeps a circular list of streams with pending chunks and chooses the next stream after each completed datamsg.

## Important APIs, Types, And Functions
Exports `sctp_sched_ops_rr_init`. Internal helpers are `sctp_sched_rr_init`, `sctp_sched_rr_init_sid`, `sctp_sched_rr_sched`, `sctp_sched_rr_unsched`, `sctp_sched_rr_next_stream`, `sctp_sched_rr_enqueue`, `sctp_sched_rr_dequeue`, and `sctp_sched_rr_dequeue_done`.

## Control Flow
Initialization creates `stream->rr_list` and clears `rr_next`. Enqueue inserts a stream extension once into the active list and initializes `rr_next` when the first stream becomes active. Dequeue uses `stream.out_curr` if a non-interleavable message is in progress, otherwise `rr_next`. Dequeue completion advances `rr_next` and removes the stream when its per-stream outq is empty.

## State And Persistence
State is in-memory only: `stream->rr_list`, `stream->rr_next`, and each extension's `rr_list` membership.

## Dependencies And Integration Points
Depends on stream extension allocation, common scheduler dequeue/list helpers, and outqueue chunk placement onto per-stream queues.

## Risks
The empty-list path is sensitive: advancing before removing the last stream must leave `rr_next` null. Other risks are duplicate list insertion, stale list nodes after scheduler switch, and fairness disruption when `out_curr` pins fragmented messages.

## Test Signals
Exercise one-stream, two-stream, and many-stream queues; enqueue duplicate datamsgs on an active stream; drain the last stream; switch schedulers; and compare order with/without fragmented messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/stream_sched_rr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sysctl.c -->
# sources/distributed-fs/ceph-client/net/sctp/sysctl.c

## Purpose
Registers global and per-network-namespace SCTP sysctls and implements custom handlers for coupled or side-effectful settings such as RTO bounds, authentication, UDP encapsulation port, HMAC algorithm, and PLPMTUD probe interval.

## Important APIs, Types, And Functions
Exports `sctp_sysctl_net_register`, `sctp_sysctl_net_unregister`, `sctp_sysctl_register`, and `sctp_sysctl_unregister`. Custom handlers include `proc_sctp_do_hmac_alg`, `proc_sctp_do_rto_min`, `proc_sctp_do_rto_max`, `proc_sctp_do_alpha_beta`, `proc_sctp_do_auth`, `proc_sctp_do_udp_port`, and `proc_sctp_do_probe_interval`.

## Control Flow
Static tables define global memory sysctls and per-net SCTP settings. Per-net registration duplicates `sctp_net_table`, rebases each `.data` pointer from `init_net.sctp` to the target net namespace, then patches coupled min/max `.extra*` pointers. Custom write handlers parse into temporary variables, validate ranges or strings, and only commit on success. Auth writes also update the control socket endpoint. UDP port writes serialize under `sctp_sysctl_mutex`, stop/start the UDP encapsulation socket, roll back to zero on start failure, and update the control socket cached port.

## State And Persistence
Sysctl values persist only in kernel memory per net namespace or global variables. Registration stores a table header in `net->sctp.sysctl_header`; unregister frees the duplicated table.

## Dependencies And Integration Points
Integrates with Linux sysctl infrastructure, SCTP per-net defaults, control sockets, UDP encapsulation helpers, and optional L3 master-device support.

## Risks
Important risks are incorrect pointer rebasing for netns tables, broken coupling between `rto_min` and `rto_max` or `pf_retrans` and `ps_retrans`, racing UDP socket restart, accepting invalid HMAC strings, and failing to update control socket state after sysctl writes.

## Test Signals
Read/write every custom sysctl in separate net namespaces, validate invalid range rejection, toggle auth and UDP port while associations exist, test UDP bind failure rollback, and confirm unregister frees duplicated tables without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/transport.c -->
# sources/distributed-fs/ceph-client/net/sctp/transport.c

## Purpose
Defines lifecycle, routing, timers, PMTU/PLPMTUD, RTO estimation, congestion-window control, and reference management for an SCTP transport representing one remote peer address.

## Important APIs, Types, And Functions
Exports constructors/destructors and state updates including `sctp_transport_new`, `sctp_transport_free`, `sctp_transport_set_owner`, timer reset helpers, `sctp_transport_pmtu`, `sctp_transport_pl_send`, `sctp_transport_pl_recv`, `sctp_transport_update_pmtu`, `sctp_transport_route`, `sctp_transport_hold`, `sctp_transport_put`, `sctp_transport_update_rto`, `sctp_transport_raise_cwnd`, `sctp_transport_lower_cwnd`, `sctp_transport_burst_limited`, `sctp_transport_reset`, `sctp_transport_immediate_rtx`, and dst helpers.

## Control Flow
Initialization copies the peer address, sets defaults from netns SCTP sysctls, initializes timers/lists, nonce, and refcount. Free marks the transport dead, deletes active timers while dropping their held references, and releases the final reference; destruction frees packets, association refs, dst, and memory through RCU. Routing refreshes dst/source address and PMTU. PLPMTUD tracks BASE, ERROR, SEARCH, and COMPLETE states on probe send/receive and packet-too-big signals. RTO updates follow SCTP smoothing rules with sysctl alpha/beta divisors and min/max clamps. Congestion control raises cwnd in slow start or avoidance, lowers it on T3, fast retransmit, ECNE, or inactivity, and enforces max-burst temporarily.

## State And Persistence
Transport state is entirely in-memory: timers, refcount, dst, source/peer addresses, RTO/RTT variables, cwnd/ssthresh/flight size, path error counters, heartbeat/reconf/probe state, and PLPMTUD search fields.

## Dependencies And Integration Points
Integrates with association lifecycle, SCTP timers/state machine event generators, routing address-family hooks, dst cache, SCTP outqueue retransmit, netns sysctls, and congestion/PMTU sync back to the association.

## Risks
High-risk areas are timer reference leaks, freeing while RCU readers hold transport pointers, incorrect PLPMTUD state transitions after black-hole detection, cwnd math under fast recovery, stale dst usage, and RTO changes when `rto_pending` is not set.

## Test Signals
Test timer start/delete/free races, route refresh after obsolete dst, PMTU too-low and PLPMTUD packet-too-big paths, RTO first and subsequent RTT samples, cwnd transitions for each lower reason, burst limiting/reset, and immediate retransmit timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/tsnmap.c -->
# sources/distributed-fs/ceph-client/net/sctp/tsnmap.c

## Purpose
Maintains the receive-side Transmission Sequence Number map used to detect duplicates, track gaps, compute cumulative TSN ACK point, produce SACK gap-ack blocks, skip abandoned TSNs, and renege received TSNs under memory pressure.

## Important APIs, Types, And Functions
Exports `sctp_tsnmap_init`, `sctp_tsnmap_free`, `sctp_tsnmap_check`, `sctp_tsnmap_mark`, `sctp_tsnmap_skip`, `sctp_tsnmap_pending`, `sctp_tsnmap_renege`, and `sctp_tsnmap_num_gabs`. Internal helpers are `sctp_tsnmap_update`, `sctp_tsnmap_find_gap_ack`, iterator helpers, and `sctp_tsnmap_grow`.

## Control Flow
Initialization allocates a bitmap, sets `base_tsn`, cumulative ack to initial minus one, and clears duplicate count. Check rejects old or out-of-window TSNs and detects bitmap duplicates. Mark either fast-advances the no-gap case or grows the bitmap, sets the bit, updates `max_tsn_seen`, and shifts away contiguous received bits. Skip advances base and cumulative ack through a forwarded TSN and shifts or clears the bitmap. Gap ack generation iterates over set bit runs past the cumulative ack point. Renege clears a bit so SACK generation can report it missing again.

## State And Persistence
The map is an in-memory bitmap plus counters in `struct sctp_tsnmap`: `len`, `base_tsn`, `cumulative_tsn_ack_point`, `max_tsn_seen`, and duplicate count.

## Dependencies And Integration Points
Used by ULP event creation after receive memory admission, SACK generation, FORWARD-TSN/I-FORWARD-TSN handling, stream reset TSN reset paths, and reneging in `ulpqueue.c`.

## Risks
Risks include wrap-aware TSN comparison mistakes, bitmap length measured in bits but allocated in bytes, growth failure causing receive drops, gap-ack off-by-one relative to cumulative ack, and renege clearing invalid bits.

## Test Signals
Cover sequential receives, gap creation/fill, duplicate old/current TSNs, TSN wraparound comparisons, bitmap growth near `SCTP_TSN_MAP_SIZE`, skip beyond current map, SACK gap block limits, and renege/pending counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/tsnmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ulpevent.c -->
# sources/distributed-fs/ceph-client/net/sctp/ulpevent.c

## Purpose
Creates, owns, accounts, and frees skb-backed SCTP ULP events delivered to sockets. It covers notifications, received DATA messages, ancillary receive info, association ownership, receive-window accounting, and event queue purging.

## Important APIs, Types, And Functions
Important exported constructors include `sctp_ulpevent_make_assoc_change`, `sctp_ulpevent_make_remote_error`, send-failed variants, shutdown/adaptation/auth/sender-dry events, stream reset/change/association reset events, `sctp_ulpevent_make_rcvmsg`, and `sctp_ulpevent_make_pdapi`. Other APIs include `sctp_ulpevent_notify_peer_addr_change`, read helpers for `SCTP_SNDRCV`, `SCTP_RCVINFO`, `SCTP_NXTINFO`, `sctp_ulpevent_free`, and `sctp_queue_purge_ulpevents`.

## Control Flow
Notification constructors allocate or clone skbs, prepend the notification struct, fill RFC-defined fields, hold the association, and set association ids. Receive-message construction checks socket or association rmem policy, schedules receive memory, clones the chunk skb, marks the TSN map, trims padding, holds the source chunk, charges rwnd recursively across fragments, and records stream/TSN flags. Read helpers emit cmsgs for application recvmsg. Free paths distinguish notifications from data: notifications drop owner refs, data increases rwnd, puts held chunks recursively, releases owner refs, then frees skbs.

## State And Persistence
Events are transient skb control-block objects. They hold association references and data receive memory accounting until delivered or purged; there is no durable state.

## Dependencies And Integration Points
Integrates with socket receive queues, SCTP association refcount/rwnd accounting, TSN map marking, chunk references, address-family user address conversion, ULP queue delivery, and RFC6458 ancillary data.

## Risks
High-risk areas are skb clone/copy length calculations, failing to undo memory admission on later failures, recursive fragment owner accounting, releasing chunk references exactly once, and filtering disabled notifications after allocation.

## Test Signals
Exercise each notification constructor, receive data with padding and skb fragments, memory-pressure failure before and after TSN marking, ancillary cmsg output, disabled subscription filtering through ULP queue paths, and purge/free accounting for mixed notification/data queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ulpevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ulpqueue.c -->
# sources/distributed-fs/ceph-client/net/sctp/ulpqueue.c

## Purpose
Implements the legacy SCTP upper-layer protocol queue for DATA chunks: receive event creation, TSN-based fragment reassembly, SSN ordering, socket receive/lobby delivery, partial delivery, reneging, FORWARD-TSN skipping, and queue flushing.

## Important APIs, Types, And Functions
Exports `sctp_ulpq_init`, `sctp_ulpq_flush`, `sctp_ulpq_free`, `sctp_ulpq_tail_data`, `sctp_clear_pd`, `sctp_ulpq_tail_event`, `sctp_make_reassembled_event`, `sctp_ulpq_reasm_flushtsn`, `sctp_ulpq_skip`, `sctp_ulpq_renege_list`, `sctp_ulpq_partial_delivery`, `sctp_ulpq_renege`, and `sctp_ulpq_abort_pd`. Key queues are `reasm`, `reasm_uo`, `lobby`, socket `sk_receive_queue`, and socket `pd_lobby`.

## Control Flow
Incoming DATA becomes an ULP event, then fragmented messages are sorted by TSN in `reasm` until complete or partial-delivery thresholds are met. Complete messages are ordered by stream/SSN in `lobby` unless unordered. `sctp_ulpq_tail_event` chooses socket receive queue or partial-delivery lobby depending on socket/association PD state and fragment-interleave setting, then signals `sk_data_ready`. Partial delivery retrieves the first contiguous fragment run when allowed and sets association/socket PD mode. Renege frees received-but-undelivered events above cumulative TSN, clears TSN map bits, and retries chunk admission. FORWARD-TSN flushes stale fragments and skips SSNs to release newly ordered lobby data.

## State And Persistence
State is volatile in `struct sctp_ulpq`, socket `pd_mode`, and skb queues. Receive-window and TSN map updates are coupled to event ownership.

## Dependencies And Integration Points
Works with `ulpevent.c` for event allocation/free/accounting, `tsnmap.c` for cumulative TSN and renege behavior, stream SSN helpers, socket receive queues, and stream-interleave callbacks that reuse reassembly helpers.

## Risks
Risks include skb frag_list manipulation during reassembly, partial-delivery deadlocks when lobbies are not drained, reneging below cumulative ack, wrong queue selection under fragment interleave, and ordering bugs after SSN skip.

## Test Signals
Test fragmented complete and partial messages, unordered delivery, receive shutdown filtering, simultaneous associations in partial delivery, FORWARD-TSN skip/reap, memory-pressure reneging, cloned skb reassembly, and aborting partial delivery with notification enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ulpqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/Makefile -->
# sources/distributed-fs/ceph-client/net/shaper/Makefile

## Purpose
Builds the generic net shaper infrastructure into the kernel networking core by compiling `shaper.o` and generated netlink glue `shaper_nl_gen.o`.

## Important APIs, Types, And Functions
There are no C APIs in this Makefile. The key build declaration is `obj-y += shaper.o shaper_nl_gen.o`, making the infrastructure built-in rather than conditional on a visible Kconfig symbol in this directory.

## Control Flow
Kbuild includes both the hand-written shaper implementation and generated YNL netlink family implementation whenever this directory participates in the network build.

## State And Persistence
No runtime state. It controls object inclusion in the built kernel.

## Dependencies And Integration Points
Depends on Kbuild traversal from the parent networking Makefile. It integrates generated code with the hand-written implementation, so missing either object breaks `net_shaper_nl_family` registration or operation callbacks.

## Risks
Risks are build-only: unconditional inclusion can expose missing dependencies on headers or symbols, and generated/hand-written files must remain in sync with `Documentation/netlink/specs/net_shaper.yaml`.

## Test Signals
Build-test networking configurations, confirm both objects appear in the link, and run netlink family registration tests to catch missing generated callback symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper.c -->
# sources/distributed-fs/ceph-client/net/shaper/shaper.c

## Purpose
Implements the generic net shaper netlink API backend for network devices. It manages per-device shaper hierarchies, validates user attributes against driver capabilities, handles get/dump/set/delete/group/capability operations, and coordinates tentative software state with driver callbacks.

## Important APIs, Types, And Functions
Externally used functions include netlink callbacks declared in `shaper_nl_gen.h`, `net_shaper_flush_netdev`, and `net_shaper_set_real_num_tx_queues`. Core types are `struct net_shaper_hierarchy` with an xarray, `struct net_shaper_nl_ctx`, `struct net_shaper_binding`, `struct net_shaper`, and `struct net_shaper_ops`. Key helpers include handle/index conversion, context setup/cleanup, `net_shaper_lookup`, `net_shaper_hierarchy_setup`, `net_shaper_pre_insert`, `net_shaper_commit`, `net_shaper_rollback`, parsers, validators, `__net_shaper_delete`, and `__net_shaper_group`.

## Control Flow
Pre-doit hooks resolve and reference a netdev, and write operations take the netdev instance lock. Handles encode scope and id into xarray indexes; entries are inserted tentatively without `NET_SHAPER_VALID`, configured in the driver, then committed with a memory barrier and VALID mark. Gets and dumps run under RCU and expose only valid entries. Set parses incremental attributes, validates capability flags and queue ids, disallows creating new node shapers, pre-inserts, calls `ops->set`, and commits or rolls back. Delete reparents child leaves when deleting a node, invokes driver delete, erases xarray entries, and recursively removes empty parents. Group parses a node plus leaves, allocates ids for new nodes, validates nesting and duplicate leaves, calls `ops->group`, commits node/leaves, cleans old empty nodes best-effort, and replies with the node handle. Capability commands report driver-supported flags by scope. Flush and queue-count shrink remove per-device hierarchy state.

## State And Persistence
State is per-netdevice, in-memory, and pointed to by `dev->net_shaper_hierarchy`. The xarray stores `struct net_shaper` entries and uses `NET_SHAPER_VALID` to separate tentative from visible state. No durable persistence exists.

## Dependencies And Integration Points
Depends on generic netlink, generated YNL ops, netdevice lifetime/ref tracking, netdev locks, RCU, xarray allocation, driver-provided `net_shaper_ops`, and UAPI attributes from `linux/net_shaper.h`.

## Risks
High-risk areas are tentative insertion rollback, parent/leaf count consistency, reparenting on node delete, RCU visibility and memory barriers, netdev unregister races, generated policy drift, and best-effort cleanup after successful grouping leaving stale empty nodes if driver delete fails.

## Test Signals
Netlink tests should cover get before set, set unsupported attrs/metrics, queue id bounds, dump while deleting, node id auto-allocation, group with duplicate leaves, reparenting and empty-node cleanup, driver callback failures and rollback, netdev unregister flush, and `real_num_tx_queues` shrink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.c -->
# sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.c

## Purpose
Auto-generated YNL generic-netlink source for the net shaper family. It defines attribute validation policies, split operation tables, and the `net_shaper_nl_family` descriptor that binds netlink commands to hand-written callbacks in `shaper.c`.

## Important APIs, Types, And Functions
Exports `net_shaper_handle_nl_policy`, `net_shaper_leaf_info_nl_policy`, and `net_shaper_nl_family`. The ops table maps `NET_SHAPER_CMD_GET`, `SET`, `DELETE`, `GROUP`, and `CAP_GET` doit/dump variants to `net_shaper_nl_*` callbacks.

## Control Flow
Netlink core uses the policy arrays to validate top-level and nested attributes before invoking callbacks. Do commands run pre/doit/post hooks; dump commands run start/dumpit/done hooks. Administrative permission is required for set, delete, and group. The family is namespace-aware and allows parallel operations, relying on the hand-written callbacks to acquire device references and locks.

## State And Persistence
No mutable runtime state beyond the registered family descriptor. Policies and ops are static const data.

## Dependencies And Integration Points
Generated from `Documentation/netlink/specs/net_shaper.yaml`, includes `uapi/linux/net_shaper.h`, and requires all callback prototypes from `shaper_nl_gen.h` to be implemented by `shaper.c`.

## Risks
Manual edits would be overwritten. Drift between YAML, UAPI enums, policies, and hand-written parser expectations can admit invalid messages or reject valid ones. `parallel_ops = true` increases reliance on correct per-device locking in callbacks.

## Test Signals
Regenerate with `tools/net/ynl/ynl-regen.sh`, compile-check callback symbol coverage, run YAML/YNL netlink selftests for policy validation, and fuzz nested handle/leaves attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.h -->
# sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.h

## Purpose
Auto-generated header for the net shaper generic-netlink family. It exposes generated policies, family descriptor, max handle id, and callback prototypes shared between generated netlink glue and the hand-written implementation.

## Important APIs, Types, And Functions
Declares `NET_SHAPER_MAX_HANDLE_ID`, policy arrays, pre/post doit and dump hooks, operation handlers for get/set/delete/group/capability commands, and `extern struct genl_family net_shaper_nl_family`.

## Control Flow
Included by both generated and hand-written shaper code. The generated source consumes callback prototypes; `shaper.c` implements them and registers the family at subsystem init.

## State And Persistence
No runtime state. It is compile-time interface glue derived from the YAML spec.

## Dependencies And Integration Points
Depends on generic netlink headers and `uapi/linux/net_shaper.h`. It must stay synchronized with `shaper_nl_gen.c`, the YAML spec, and `shaper.c`.

## Risks
Risks are interface drift, stale `NET_SHAPER_MAX_HANDLE_ID` relative to handle packing in `shaper.c`, and callback signature mismatch after netlink spec regeneration.

## Test Signals
Regeneration diff review, compile with `W=1`, validate handle id boundary tests, and ensure every declared callback has exactly one implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/Kconfig -->
# sources/distributed-fs/ceph-client/net/smc/Kconfig

## Purpose
Defines configuration options for the SMC socket protocol family, SMC diagnostic monitoring, and an eBPF hook for SMC handshake control.

## Important APIs, Types, And Functions
Configuration symbols are `CONFIG_SMC`, `CONFIG_SMC_DIAG`, and `CONFIG_SMC_HS_CTRL_BPF`. `SMC` is tristate and depends on `INET`, `INFINIBAND`, and `DIBS`; diagnostics depend on `SMC`; handshake BPF depends on `SMC`, `BPF_JIT`, and `BPF_SYSCALL` and defaults to enabled.

## Control Flow
Kconfig dependency resolution determines which SMC objects are built by the Makefile. Enabling base SMC permits the socket family implementation; enabling diagnostics adds netlink/socket monitoring; enabling handshake BPF compiles the BPF hook integration.

## State And Persistence
No runtime state directly. Selected symbols persist in kernel build configuration and control compiled feature surface.

## Dependencies And Integration Points
Integrates SMC with the INET stack, InfiniBand/RDMA support, diagnostic tooling such as `smcss`, and kernel BPF infrastructure.

## Risks
The visible typo in the help text ("filtring") is documentation-only. Functional risks include dependency churn making SMC unavailable unexpectedly, default-on BPF hook widening build/test matrix, and mismatch between Kconfig symbols and Makefile object lists.

## Test Signals
Run randconfig/allmodconfig build coverage across dependencies, verify SMC is hidden when prerequisites are absent, ensure `SMC_DIAG` cannot build without `SMC`, and compile with BPF prerequisites toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/Makefile -->
# sources/distributed-fs/ceph-client/net/smc/Makefile

## Purpose
Defines Kbuild object composition for the SMC protocol implementation, optional diagnostics, sysctl support, and optional handshake BPF integration.

## Important APIs, Types, And Functions
Build targets include `obj-$(CONFIG_SMC) += smc.o`, `obj-$(CONFIG_SMC_DIAG) += smc_diag.o`, and composite `smc-y` object lists covering AF_SMC, pnet, RDMA/ISM, CLC, core, work requests, LLC, CDC, TX/RX, close, netlink, stats, tracepoints, and inet integration. Conditional additions are `smc-$(CONFIG_SYSCTL) += smc_sysctl.o` and `smc-$(CONFIG_SMC_HS_CTRL_BPF) += smc_hs_bpf.o`.

## Control Flow
Kbuild links all `smc-y` members into the `smc.o` composite when `CONFIG_SMC` is enabled. Diagnostic support builds separately as `smc_diag.o`. Include path `ccflags-y += -I$(src)` lets local generated or sibling headers be included consistently.

## State And Persistence
No runtime state. It defines build-time module/built-in composition.

## Dependencies And Integration Points
Tied directly to symbols from `Kconfig` and to source files implementing the SMC stack. Parent networking Makefiles consume this directory's objects.

## Risks
Risks are missing an object when new SMC subsystems are added, stale conditional symbols, incorrect include assumptions, and link failures if `Kconfig` permits combinations not reflected here.

## Test Signals
Build `CONFIG_SMC=y/m`, `CONFIG_SMC_DIAG=y/m`, with and without `CONFIG_SYSCTL`, and with BPF handshake support enabled/disabled; inspect resulting module symbols and run modpost for unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/Makefile -->
