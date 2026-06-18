# sources/distributed-fs/ceph-client/net/sctp/sm_sideeffect.c

## Purpose
`sm_sideeffect.c` is the execution engine for SCTP state-machine side effects. State functions return a disposition and a command sequence; this file interprets those commands to mutate associations, start and stop timers, generate replies, retransmit chunks, deliver data and notifications to ULP, update transport liveness, and free associations.

It also defines timer callbacks that re-enter the SCTP state machine for retransmission, initialization, shutdown, heartbeat, SACK delay, RE-CONFIG, probe, autoclose, and ICMP protocol-unreachable events. In practice, `sctp_do_sm()` in this file is the central dispatcher for chunk events, timeout events, primitive events, and other SCTP events.

## Important APIs, Types, And Functions
The main public entry point is `sctp_do_sm()`. It looks up a state function with `sctp_sm_lookup_event()`, initializes `struct sctp_cmd_seq`, runs the state function, and passes the resulting disposition and commands to `sctp_side_effects()`.

The command interpreter is `sctp_cmd_interpreter()`. It consumes `struct sctp_cmd` entries from `struct sctp_cmd_seq` and handles verbs such as `SCTP_CMD_NEW_ASOC`, `SCTP_CMD_DELETE_TCB`, `SCTP_CMD_NEW_STATE`, `SCTP_CMD_REPLY`, `SCTP_CMD_SEND_PKT`, `SCTP_CMD_GEN_SACK`, `SCTP_CMD_PROCESS_SACK`, `SCTP_CMD_GEN_INIT_ACK`, `SCTP_CMD_GEN_COOKIE_ECHO`, `SCTP_CMD_GEN_SHUTDOWN`, timer start/restart/stop commands, retransmission commands, ECN commands, transport heartbeat and strike commands, ULP delivery commands, ASCONF cleanup, AUTH key setup, and message enqueueing.

Timer entry points are `sctp_generate_t3_rtx_event()`, `sctp_generate_heartbeat_event()`, `sctp_generate_proto_unreach_event()`, `sctp_generate_reconf_event()`, `sctp_generate_probe_event()`, and the association-timer wrappers for T1 cookie, T1 init, T2 shutdown, T4 RTO, T5 shutdown guard, SACK, and autoclose. The global `sctp_timer_events[]` table maps association timer indexes to timer callbacks.

Transport and protocol helpers include `sctp_do_ecn_ce_work()`, `sctp_do_ecn_ecne_work()`, `sctp_do_ecn_cwr_work()`, `sctp_gen_sack()`, `sctp_do_8_2_transport_strike()`, `sctp_cmd_transport_on()`, `sctp_cmd_hb_timers_start()`, `sctp_cmd_hb_timers_stop()`, `sctp_cmd_t3_rtx_timers_stop()`, `sctp_cmd_setup_t2()`, `sctp_cmd_setup_t4()`, and `sctp_cmd_t1_timer_update()`.

Association/ULP helpers include `sctp_cmd_init_failed()`, `sctp_cmd_assoc_failed()`, `sctp_cmd_process_init()`, `sctp_cmd_process_sack()`, `sctp_cmd_new_state()`, `sctp_cmd_delete_tcb()`, `sctp_cmd_process_operr()`, `sctp_cmd_del_non_primary()`, `sctp_cmd_set_sk_err()`, `sctp_cmd_assoc_change()`, `sctp_cmd_peer_no_auth()`, `sctp_cmd_adaptation_ind()`, and `sctp_cmd_send_msg()`.

## Control Flow
Normal event flow begins in `sctp_do_sm()`. The function receives an event type, subtype, current association state, endpoint, association, and event argument. It finds the matching state-function table entry, initializes a command sequence, invokes the state function, then calls `sctp_side_effects()` to execute the commands and interpret the final disposition. Debug macros log pre-state-function, post-state-function, and post-side-effect state.

`sctp_side_effects()` always runs the command interpreter first. It then converts dispositions into final effects: discard logs ignored events, nomem returns `-ENOMEM`, delete/abort clears the caller's association pointer, consume does no extra work, violation logs a rate-limited protocol violation, not-implemented warns, bug calls `BUG()`, and unknown dispositions are converted to an error with a one-time warning.

Timer callbacks lock the socket in BH context before re-entering the state machine. If userspace owns the socket, callbacks reschedule shortly later and hold the association or transport reference needed for the deferred callback. Association-scoped timers use `sctp_generate_timeout_event()`, which skips dead associations and passes the timeout id as the state-machine event argument. Transport timers pass the transport pointer. Every callback releases the reference held for the timer before returning.

SACK generation is delayed or forced by `sctp_gen_sack()`. It marks SACK needed for forced ACKs, disabled delayed ACKs, or out-of-order TSN maps. Otherwise it increments the delayed SACK counter, sets the SACK timer from the last data transport or association defaults, and restarts that timer. When a SACK is due, it snapshots `rwnd` into `a_rwnd`, builds a SACK, queues it as a reply, resets SACK counters, and stops the SACK timer.

The command interpreter is a single large switch. Association lifecycle commands register a new association with the endpoint, transition states, purge outqueues, or free the TCB. Reply and send commands cork the outqueue so multiple replies to one received packet are bundled, tail chunks to the outqueue, or transmit complete out-of-the-blue packets directly. At the end, the interpreter uncorks after a complete input packet or after locally corked non-chunk processing.

Handshake commands build INIT-ACK, process peer INIT data, build COOKIE-ECHO, choose alternate INIT transports, update init retry counters, restart T1 timers, retransmit COOKIE-ECHO bundled data, and report initialization failure. Association-failure commands generate ULP association-change notifications, optionally send a max-retrans protocol-violation abort, move the association to CLOSED, set outqueue error, and schedule TCB deletion.

Reliability commands mark TSNs, duplicate TSNs, FWD-TSNs, process inbound SACKs through the outqueue, synthesize a SACK header for cumulative TSN processing, mark RTO pending, retransmit for T1/T3 reasons, and update congestion state. ECN commands remember CE state, lower congestion window on newer ECNE, generate CWR, and clear `need_ecne` on CWR receipt.

Transport liveness commands implement RFC path failure behavior. Strikes increment association and transport error counts, move active transports to partially failed state after `pf_retrans`, mark paths down after `pathmaxrxt`, switch primary path after `ps_retrans`, and back off RTO. HEARTBEAT ACK handling clears error counters and `hb_sent`, marks inactive/unconfirmed/PF transports up, confirms dst cache, updates RTO from heartbeat timestamp, restarts heartbeat timers, and triggers immediate retransmission when a single unconfirmed path becomes confirmed.

ULP commands deliver data chunks, enqueue notifications, start partial delivery, renege queued events, report remote errors, generate association-change/adaptation/AUTH notifications, and clear `data_ready_signalled` after command processing. ASCONF and RE-CONFIG commands set T4 timers, stop ASCONF on unsupported ERROR reports, purge ASCONF queues, and update probe timers.

## State And Persistence
All state is runtime kernel state. This file mutates association state (`asoc->state`, init counters, timeout values, `overall_error_count`, `shutdown_last_sent_to`, `peer.sack_needed`, `peer.sack_cnt`, `a_rwnd`, ECN fields, peer init tag, outqueue error/corking, ASCONF queues, stream ULP queues), transport state (`error_count`, `state`, `hb_sent`, `rto`, `rto_pending`, timers, dst confirmation, init send count), socket state (`sk_err`, `sk_shutdown`, TCP-style `sk_state`, state-change wakeups), and endpoint association membership.

Timer reference ownership is a central persistence rule. Starting a timer takes an association or transport reference when the timer was not already pending; stopping a timer drops it when deletion succeeds; callbacks drop the reference they were invoked with. Rescheduling a busy-socket timer takes a new reference only if `mod_timer()` reports the timer was not pending.

Outqueue corking is also stateful. The interpreter may cork locally while queueing replies or messages, and must uncork before switching associations, deleting a TCB, forcing primary retransmission, discarding a packet, or finishing a packet event. Incorrect cork handling would change packet bundling and retransmission timing.

## Dependencies And Integration Points
This file depends on SCTP state tables (`sctp_sm_lookup_event()`), state-function command production, chunk builders from `sm_make_chunk.c`, association and endpoint registration/freeing, outqueue scheduling and retransmission, packet transmit helpers, TSN maps, stream scheduler/ULP queue callbacks, transport congestion/RTO/timer helpers, socket locking, Linux timer APIs, and ULP event constructors.

External integration points include `endpointola.c` and `associola.c` chunk input paths, `primitive.c` user-triggered primitive events, transport timers initialized by association setup, stream reset and ASCONF paths in state functions, socket wait queues and `sk_state_change()`, and SCTP sysctl/net namespace policy such as partial-failure behavior.

## Risks And Edge Cases
The interpreter's behavior depends on command order. State functions often enqueue commands assuming earlier commands set up association state, corking, timers, or chunks for later commands. Reordering commands, adding commands that can fail in the middle, or changing when the interpreter uncorks can produce extra packets, lost replies, leaked chunks, or use-after-free on associations.

Timer handling is concurrency-sensitive. Callbacks run under BH socket locking, handle busy sockets by short rescheduling, and manually balance association/transport references. Missing a hold or put around `mod_timer()`, `timer_reduce()`, or `timer_delete()` can leak references or free an object while a timer can still fire.

Transport strike logic is subtle because heartbeat and non-heartbeat failures affect `overall_error_count` differently, partially failed paths have separate thresholds, and RTO backoff skips the first heartbeat send until an outstanding heartbeat is actually missed. Changing these rules can cause premature association failure or delayed path failover.

Failure handling inside `sctp_cmd_interpreter()` drains remaining `SCTP_CMD_REPLY` chunks when an error occurs, but other command object types may have ownership rules elsewhere. Any new command that allocates resources must define cleanup behavior for mid-sequence errors.

Association deletion is conditional for TCP-style listening sockets so accept can still pick up a non-temporary association. Incorrectly freeing or retaining TCBs here can break one-to-one socket accept/connect semantics.

`sctp_cmd_process_operr()` loops while `chunk->chunk_end > chunk->skb->data` but relies on remote-error event construction and skb parsing state to advance over causes. Any change to remote-error parsing must preserve progress or this loop could repeatedly inspect the same error cause.

## Test Signals
Useful coverage includes SCTP selftests for association establishment, COOKIE-ECHO retransmission, shutdown, abort, path failover, heartbeat confirmation, delayed SACK behavior, PR-SCTP FWD-TSN, ASCONF, AUTH notifications, and RE-CONFIG timeouts.

Timer and concurrency tests should exercise busy-socket rescheduling, timer start/restart/stop reference balancing, T3 retransmission, T1 init/cookie backoff across multiple transports, T2 shutdown transport choice, T4 ASCONF timeout, heartbeat/probe timers, SACK timer cancellation, and autoclose.

Interpreter tests should validate command sequences for new association registration, state transitions, ULP delivery, reply bundling and uncorking at end-of-packet, mid-sequence allocation failure cleanup, INIT/association failure notifications, `sk_err` behavior for one-to-one sockets, and TCB retention for listening sockets.

Runtime signals include dynamic debug for `sctp_do_sm()` transitions, tracepoints around timers and retransmission, packet captures confirming bundled replies and correct CWR/SACK/SHUTDOWN timing, lockdep for socket/timer paths, fault injection for chunk and notification allocation failures, and KASAN/KCSAN while running multi-homed SCTP failover and ASCONF workloads.
