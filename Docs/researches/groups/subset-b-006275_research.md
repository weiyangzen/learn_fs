# subset-b-006275 Research

Grouped code research for selected SCTP state-machine construction and side-effect files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sm_make_chunk.c -->
# sources/distributed-fs/ceph-client/net/sctp/sm_make_chunk.c

## Purpose
`sm_make_chunk.c` is the SCTP state machine's chunk construction, parameter processing, cookie, ASCONF, PR-SCTP, and RE-CONFIG helper layer. It builds outbound SCTP control and data chunks, turns skbs into `struct sctp_chunk` objects, validates and applies INIT/INIT-ACK parameters, packs and unpacks state cookies, and processes extension-specific control chunks such as ASCONF and stream reset.

This file sits between state functions in `sm_statefuns.c`, association/transport management, authentication, address binding, and the outqueue. State functions decide what protocol action is needed; this file performs the low-level serialization and the association mutations required to make that action real.

## Important APIs, Types, And Functions
Core chunk allocation helpers are `_sctp_make_chunk()`, `sctp_make_control()`, `sctp_make_data()`, `sctp_make_idata()`, `sctp_chunkify()`, `sctp_addto_chunk()`, `sctp_user_addto_chunk()`, `sctp_chunk_hold()`, `sctp_chunk_put()`, and `sctp_chunk_free()`. They allocate an skb of padded chunk size, initialize `struct sctp_chunkhdr`, wrap it in `struct sctp_chunk`, attach ownership/destructor state for control chunks, and append payload bytes while maintaining `chunk_hdr->length` and `chunk_end`.

Handshake builders include `sctp_make_init()`, `sctp_make_init_ack()`, `sctp_make_cookie_echo()`, `sctp_make_cookie_ack()`, `sctp_pack_cookie()`, `sctp_unpack_cookie()`, `sctp_make_temp_asoc()`, `sctp_generate_tag()`, and `sctp_generate_tsn()`. Important SCTP data structures are `struct sctp_association`, `struct sctp_endpoint`, `struct sctp_inithdr`, `struct sctp_cookie_param`, `struct sctp_signed_cookie`, and `struct sctp_cookie`.

Common control chunk builders include `sctp_make_sack()`, `sctp_make_shutdown()`, `sctp_make_shutdown_ack()`, `sctp_make_shutdown_complete()`, `sctp_make_abort()`, `sctp_make_abort_no_data()`, `sctp_make_abort_user()`, `sctp_make_abort_violation()`, `sctp_make_violation_paramlen()`, `sctp_make_violation_max_retrans()`, `sctp_make_new_encap_port()`, `sctp_make_heartbeat()`, `sctp_make_heartbeat_ack()`, `sctp_make_pad()`, `sctp_make_op_error()`, and `sctp_make_auth()`.

INIT and parameter validation is handled by `sctp_verify_init()`, `sctp_verify_param()`, `sctp_verify_ext_param()`, `sctp_process_unk_param()`, `sctp_process_missing_param()`, `sctp_process_inv_mandatory()`, `sctp_process_inv_paramlength()`, `sctp_process_hn_param()`, `sctp_process_ext_param()`, `sctp_process_init()`, and `sctp_process_param()`.

Data and sequencing helpers are `sctp_make_datafrag_empty()`, `sctp_chunk_assign_ssn()`, and `sctp_chunk_assign_tsn()`. PR-SCTP helpers are `sctp_make_fwdtsn()` and `sctp_make_ifwdtsn()`.

ADD-IP/ASCONF helpers include `sctp_make_asconf()`, `sctp_make_asconf_update_ip()`, `sctp_make_asconf_set_prim()`, `sctp_make_asconf_ack()`, `sctp_add_asconf_response()`, `sctp_process_asconf_param()`, `sctp_verify_asconf()`, `sctp_process_asconf()`, `sctp_asconf_param_success()`, `sctp_get_asconf_response()`, and `sctp_process_asconf_ack()`.

RE-CONFIG/stream-reset helpers include `sctp_make_reconf()`, `sctp_make_strreset_req()`, `sctp_make_strreset_tsnreq()`, `sctp_make_strreset_addstrm()`, `sctp_make_strreset_resp()`, `sctp_make_strreset_tsnresp()`, and `sctp_verify_reconf()`.

## Control Flow
Chunk construction starts in `_sctp_make_chunk()`. It computes the padded chunk allocation size, rejects chunks larger than `SCTP_MAX_CHUNK_LEN`, allocates an skb, writes the chunk header, wraps it with `sctp_chunkify()`, and marks `chunk->auth` when `sctp_auth_send_cid()` says the chunk type must be authenticated. `sctp_make_control()` adds control ownership via `sctp_control_set_owner_w()`, which pins the active shared key for authenticated chunks and installs `sctp_control_release_owner()` as the skb destructor.

Handshake flow builds INIT or INIT-ACK chunks from association state. `sctp_make_init()` serializes fixed INIT fields, local bind addresses, supported address types, ECN/PR-SCTP, supported extensions, adaptation indication, interleaving, ADD-IP, RE-CONFIG, and AUTH parameters. `sctp_make_init_ack()` mirrors this for a peer-validated association, packs a signed state cookie containing the association cookie state plus the peer INIT and raw local addresses, and includes only capabilities accepted from the peer. COOKIE-ECHO and COOKIE-ACK helpers then complete the four-way SCTP association setup.

Cookie unpack flow validates COOKIE-ECHO before recreating an association. `sctp_unpack_cookie()` checks the cookie length and padding, verifies HMAC-SHA256 when cookie authentication is enabled, compares vtag and ports with the packet header, checks expiration unless this is an init-collision/lost-COOKIE-ACK case, allocates a fresh association, restores cookie state, restores bind addresses from the cookie, initializes TSN and ADD-IP/RE-CONFIG serials, and leaves INIT processing to later side effects.

INIT validation flow first checks mandatory fixed fields and minimum advertised receive window, then walks parameters to detect malformed TLVs and required state-cookie presence for INIT-ACK. Each variable parameter is then verified by `sctp_verify_param()`, which enforces feature gates and length rules for ADD-IP, AUTH, PR-SCTP, host-name, and supported-extension parameters. Unknown parameters are handled according to the SCTP high-bit action policy, optionally accumulating ERROR chunks.

INIT processing flow mutates the association. `sctp_process_init()` adds the source address as the initial active peer transport, processes embedded address/capability parameters, requires that the packet source match a valid advertised or implicit address, disables incomplete AUTH capability, blocks ADD-IP without AUTH unless the net namespace allows backward compatibility, removes `SCTP_UNKNOWN` transports, stores peer fixed INIT fields, clamps stream counts to peer limits, initializes TSN tracking and stream state, updates fragmentation point, assigns an association id for non-temporary associations, and initializes the peer ADD-IP serial.

SACK flow snapshots the peer TSN map into cumulative TSN, gap acknowledgement blocks, and duplicate TSNs. `sctp_make_sack()` writes advertised receive window from `asoc->a_rwnd`, targets the last data transport, increments duplicate-chunk statistics, and advances `peer.sack_generation`, resetting transport generations on wrap.

ASCONF flow has separate outbound, inbound, and acknowledgement paths. Outbound builders create an ASCONF with a serial, an address parameter, and one or more add/delete/set-primary TLVs. Inbound `sctp_verify_asconf()` enforces address-parameter ordering and TLV lengths before `sctp_process_asconf()` applies each request, accumulates ASCONF-ACK responses only after the first failure, increments `peer.addip_serial`, and caches ACK chunks for retransmission. `sctp_process_asconf_ack()` walks the cached last ASCONF, maps responses by correlation id, applies successful local address changes, disables unsupported ADD-IP parameter types, handles resource-shortage retry signals, and frees `addip_last_asconf`.

RE-CONFIG flow serializes stream-reset and add-stream requests into one RE-CONFIG chunk, with request sequence numbers derived from `strreset_outseq` and response sequence numbers from `strreset_inseq`. `sctp_verify_reconf()` limits a RE-CONFIG chunk to at most three parameters and enforces valid combinations and exact/minimum lengths for reset requests, responses, TSN reset, and add-stream operations.

## State And Persistence
All state is in kernel runtime objects; nothing is persisted outside socket, endpoint, association, transport, skb, and ULP queue lifetimes. The file mutates association fields such as `peer.cookie`, `peer.cookie_len`, `peer.ecn_capable`, `peer.prsctp_capable`, `peer.auth_capable`, `peer.asconf_capable`, `peer.reconf_capable`, `peer.intl_capable`, `peer.peer_random`, `peer.peer_hmacs`, `peer.peer_chunks`, `peer.rwnd`, `peer.i.*`, `peer.tsn_map`, `peer.addip_serial`, `peer.sack_generation`, `next_tsn`, `ctsn_ack_point`, `adv_peer_ack_point`, `addip_serial`, `strreset_outseq`, `strreset_inseq`, `asconf_ack_list`, `addip_last_asconf`, `asconf_addr_del_pending`, `new_transport`, and bind-address state.

`sctp_pack_cookie()` copies selected association cookie state and the original INIT into an on-wire state cookie. `sctp_unpack_cookie()` treats that signed cookie as the source of truth for recreating a server-side association after COOKIE-ECHO. AUTH control chunks also hold references to active shared keys until skb destruction, and the destructor can enqueue an AUTH key-free notification when a deactivated key's final use is released.

## Dependencies And Integration Points
The file depends on Linux skb allocation/manipulation, random number generation, endian helpers, HMAC-SHA256, IPv4/IPv6 address-family helpers, LSM hooks through `security_sctp_bind_connect()`, SCTP association/endpoint/transport APIs, bind-address APIs, stream scheduler APIs, TSN maps, AUTH helpers, outqueue behavior, and ULP event delivery.

Primary callers are SCTP state functions and side-effect handlers. `sm_statefuns.c` asks this file to build replies, aborts, INIT-ACKs, ASCONF-ACKs, FWD-TSNs, and RE-CONFIG responses. `sm_sideeffect.c` invokes INIT processing and chunk builders from command execution. `stream.c` uses stream reset builders. Association setup in `associola.c`, input paths, primitive calls, and endpoint receive processing all rely on these helpers to keep wire serialization and association mutation consistent.

## Risks And Edge Cases
Chunk sizing is critical. Several helpers intentionally assume the caller reserved enough tailroom and use `skb_put()` or `sctp_addto_chunk()` after computing lengths. Wrong `paylen`, missing padding, or an incorrect parameter length can corrupt chunk length accounting or trigger skb bounds failures.

Handshake and cookie logic is security-sensitive. Cookie HMAC coverage, vtag/port comparison, cookie lifetime checks, and source-address validation are all required to avoid accepting forged or stale association state. Timestamp-based stale-cookie checks intentionally trade a small false-expiration risk for lower per-packet timestamp overhead.

Parameter handling must preserve SCTP's unknown-parameter action semantics. Incorrectly treating a `skip` parameter as fatal, or failing to stop on a `discard` parameter, can break interoperability. AUTH and ADD-IP negotiation has a specific security coupling: ADD-IP is disabled if the peer advertises ASCONF without usable AUTH unless the namespace compatibility knob allows it.

Address reconfiguration touches transport lists while timers and retransmission logic can be active. ASCONF delete-all and delete-source rules protect against removing the last or current source address, but bugs in wildcard address handling, primary-path selection, or cached ASCONF cleanup can leave stale transports, stale dst caches, or unbalanced chunk references.

Stream-reset validation is intentionally strict about parameter order and count. Relaxing those checks can expose downstream stream code to malformed parameter combinations; over-tightening them can reject valid paired out/in reset and add-stream requests.

## Test Signals
Strong tests include SCTP handshake tests for INIT/INIT-ACK capability negotiation, COOKIE-ECHO with valid, stale, malformed, bad-HMAC, bad-vtag, and bad-port cookies, and multi-homed INIT address validation with IPv4, IPv6, v6-only, and source-address mismatch cases.

Protocol parser tests should cover unknown parameter action bits, invalid mandatory parameters, invalid parameter lengths, missing state cookie in INIT-ACK, AUTH random/HMAC/chunks validation, ADD-IP-without-AUTH gating, host-name abort behavior, and extension negotiation for ECN, PR-SCTP, AUTH, ASCONF, RE-CONFIG, and I-DATA.

Chunk builder tests should assert wire lengths, padding, flags, network-byte-order fields, transport selection for replies, AUTH ownership/key release, SACK gap/duplicate serialization, ABORT/ERROR cause payloads, HEARTBEAT nonce and probe fields, FWD-TSN skip lists, and RE-CONFIG parameter order.

Integration signals are lksctp selftests, packetdrill-style SCTP traces, KASAN/KMSAN/UBSAN runs against malformed TLVs, lockdep under ASCONF and timer activity, fault-injection of allocation failures, and interoperability tests against peers exercising multihoming, PR-SCTP, AUTH, ADD-IP, and stream reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sm_make_chunk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sm_sideeffect.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/sm_sideeffect.c -->
