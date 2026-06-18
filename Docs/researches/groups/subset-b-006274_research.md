# Research: subset-b-006274

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/input.c -->
# sources/distributed-fs/ceph-client/net/sctp/input.c

## Purpose
`input.c` is the SCTP ingress and lookup core. It is the handoff from IPv4/IPv6 protocol receive callbacks into SCTP association state, and it also owns endpoint hashing, transport rhashtable lookup, out-of-the-blue packet filtering, backlog requeueing, and common ICMP/ICMPv6 error validation. The code turns an `sk_buff` into an `sctp_chunk`, finds the right `struct sctp_association` or listening/control `struct sctp_endpoint`, and queues work into the receiver inqueue under the socket lock.

## Important APIs, Types, And Functions
Main entry points are `sctp_rcv()`, `sctp_backlog_rcv()`, `sctp_err_lookup()`, `sctp_err_finish()`, `sctp_v4_err()`, `sctp_udp_v4_err()`, `sctp_hash_endpoint()`, `sctp_unhash_endpoint()`, `sctp_transport_hashtable_init()`, `sctp_hash_transport()`, `sctp_unhash_transport()`, `sctp_addrs_lookup_transport()`, `sctp_epaddr_lookup_transport()`, and `sctp_has_association()`. Internal lookup helpers include `__sctp_rcv_lookup_endpoint()`, `__sctp_lookup_association()`, `__sctp_rcv_init_lookup()`, `__sctp_rcv_asconf_lookup()`, `__sctp_rcv_walk_lookup()`, and `__sctp_rcv_lookup_harder()`.

Key state lives in `sctp_ep_hashtable`, `sctp_transport_hashtable`, per-endpoint bind lists, per-transport rhashtable nodes, and skb control blocks (`SCTP_INPUT_CB`). The file relies on AF-specific operations supplied by `protocol.c` and `ipv6.c` for address extraction, validation, interface indexes, and address-parameter conversion.

## Control Flow
`sctp_rcv()` rejects non-host packets, undersized packets, bad CRCs, non-unicast addresses, policy failures, socket-filtered packets, and chunks that cannot be allocated. It linearizes when checksum work needs contiguous bytes, pulls the SCTP common header, selects the AF table from the IP version, constructs source/destination `union sctp_addr` values, and looks up an association by local address, peer address, port, net namespace, and device binding. If no association is found, it falls back to endpoint lookup; if only the control endpoint is found, `sctp_rcv_ootb()` scans all chunks and silently discards OOTB ABORT, SHUTDOWN COMPLETE, malformed chunks, or bundled non-leading INIT.

When a chunk is accepted, `sctp_rcv()` locks the target socket, handles races where an association migrated to a new socket, then either queues the skb to the socket backlog or calls `sctp_inq_push()` immediately. `sctp_backlog_rcv()` later revalidates receiver liveness and may move a backlogged skb to a new socket if peeloff/accept migration changed `rcvr->sk`.

Association lookup is two-stage. The fast path uses the transport rhashtable keyed by net namespace, local port, and peer address, then validates bound device and local bind address. The harder path inspects INIT/INIT-ACK address parameters and AUTH/ASCONF chunk sequences so multihomed associations and ADD-IP traffic can be matched even when the packet source address is not yet a known transport.

## State And Persistence
There is no disk persistence. Runtime persistence is entirely in hash table membership, transport/endpoint reference counts, socket backlog holds, and association timers/statistics. Backlog insertion takes a transport or endpoint hold so state cannot disappear while the skb waits. Transport rhashtable entries are skipped for temporary associations and removed when transports are torn down.

## Dependencies And Integration Points
This file sits between `net_protocol`/`inet6_protocol` handlers and SCTP state-machine processing. It integrates with XFRM policy, socket filters, reuseport selection, L3 master device matching, rhashtable, SCTP AF operations, ICMP modules, UDP tunneling error callbacks, and SCTP MIB counters. It calls out to `sctp_inq_push()` for state-machine delivery and `sctp_retransmit()` for PMTU-driven retransmission.

## Risks
The major risks are reference-count and lock ordering mistakes across softirq receive, socket backlog processing, and socket migration. Lookup hardening must not walk beyond skb bounds while inspecting INIT/ASCONF parameters. OOTB filtering must preserve RFC behavior: dropping dangerous packets without suppressing packets that need state-machine responses. Error handling must validate verification tags before acting on ICMP, or spoofed ICMP could corrupt PMTU, abort associations, or report false socket errors.

## Test Signals
Useful signals include SCTP over IPv4 and UDP encapsulation receive, checksum failures incrementing `SCTP_MIB_CHECKSUMERRORS`, OOTB ABORT/SHUTDOWN COMPLETE discard, INIT/INIT-ACK lookup by embedded address parameters, AUTH plus ASCONF lookup, reuseport endpoint selection, bound-device/L3 master filtering, socket-owned backlog paths, peeloff migration while packets are queued, ICMP frag-needed PMTU updates, ICMP protocol-unreachable abort events, and rhashtable duplicate transport rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/inqueue.c -->
# sources/distributed-fs/ceph-client/net/sctp/inqueue.c

## Purpose
`inqueue.c` implements the SCTP receive inqueue abstraction. It accepts packet-level `struct sctp_chunk` objects produced by `sctp_rcv()` and exposes chunk-level iteration to the SCTP state-machine top-half handler. The important job is splitting bundled SCTP packets and SCTP GSO frag-list packets into individual chunks while preserving enough skb/control-block context for later processing.

## Important APIs, Types, And Functions
The external API is small: `sctp_inq_init()`, `sctp_inq_free()`, `sctp_inq_push()`, `sctp_inq_peek()`, `sctp_inq_pop()`, and `sctp_inq_set_th_handler()`. State is in `struct sctp_inq`: `in_chunk_list` for queued packet chunks, `in_progress` for the packet currently being walked, and `immediate` for the handler callback. Important per-chunk flags maintained here are `singleton`, `end_of_packet`, `pdiscard`, `data_accepted`, `auth`, `has_asconf`, `chunk_hdr`, `chunk_end`, and `head_skb`.

## Control Flow
`sctp_inq_push()` drops chunks whose receiver was already marked dead, appends live chunks to `in_chunk_list`, updates association input packet stats, and directly invokes the configured work callback. Despite the `work_struct` shape, this path is synchronous at a known lock-safe point.

`sctp_inq_pop()` first completes any prior `in_progress` packet. If the previous chunk ended a packet, hit a parse-discard condition, or was a singleton, it advances through GSO `frag_list`/`next` skb chains or frees the packet chunk. If more chunks remain in the same skb, it advances `skb->data` to the prior padded `chunk_end`. When pulling a new packet, it handles SCTP GSO cover-letter skbs, saves RPS hash to the association socket, copies input control block data from a GSO head skb to fragment skbs, then initializes per-chunk parse flags.

For every popped chunk it sets `chunk_hdr`, computes padded `chunk_end`, pulls the chunk header, invalidates `subh`, and classifies the chunk as bundled, end-of-packet, or malformed. Malformed chunk lengths are not immediately freed here; `pdiscard` lets the state machine account and discard consistently.

## State And Persistence
The inqueue is volatile per endpoint/association receive state. It owns queued packet chunks until they are popped or freed. `sctp_inq_chunk_free()` restores `chunk->skb` to `head_skb` before freeing so GSO-owned resources are released from the correct head.

## Dependencies And Integration Points
This file depends on skbuff layout helpers, SCTP chunk allocation/freeing, `sctp_list_dequeue()`, SCTP state-machine callback wiring, and per-association stats. It is called from `input.c` receive/backlog paths and consumed by the state machine configured through `sctp_inq_set_th_handler()`.

## Risks
The high-risk logic is skb pointer movement across bundled chunks and GSO fragment lists. Incorrect `chunk_end` or `skb_pull()` arithmetic can desynchronize parsing, while freeing the wrong skb in GSO mode can leak or double-free. The direct callback model assumes caller lock context is correct; changing it to scheduled work would affect locking and object lifetime.

## Test Signals
Test with single-chunk packets, multi-chunk bundles, malformed short chunk lengths, padded chunk boundaries, SCTP GSO skbs with frag lists, cover-letter GSO skbs, dead receiver drops, queue free with active `in_progress`, and state-machine handler invocation ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/inqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ipv6.c -->
# sources/distributed-fs/ceph-client/net/sctp/ipv6.c

## Purpose
`ipv6.c` provides SCTP's IPv6 address-family and protocol-family implementation. It mirrors IPv4 support in `protocol.c` but handles IPv6 route lookup, address validation, link-local scope IDs, v4-mapped address behavior for dual-stack sockets, ICMPv6 errors, UDP encapsulation, proc address dumping, and registration with the IPv6 protocol and socket layers.

## Important APIs, Types, And Functions
Public registration hooks are `sctp_v6_pf_init()`, `sctp_v6_pf_exit()`, `sctp_v6_protosw_init()`, `sctp_v6_protosw_exit()`, `sctp_v6_add_protocol()`, `sctp_v6_del_protocol()`, and UDP error entry `sctp_udp_v6_err()`. The core AF/PF tables are `sctp_af_inet6` and `sctp_pf_inet6`.

Important helpers include `sctp_inet6addr_event()`, `sctp_v6_err()`, `sctp_v6_err_handle()`, `sctp_v6_xmit()`, `sctp_v6_get_dst()`, `sctp_v6_get_saddr()`, `sctp_v6_copy_addrlist()`, `sctp_v6_from_skb()`, `sctp_v6_from_addr_param()`, `sctp_v6_cmp_addr()`, `sctp_v6_available()`, `sctp_v6_addr_valid()`, `sctp_v6_addr_to_user()`, `sctp_inet6_bind_verify()`, `sctp_inet6_send_verify()`, and `sctp_getname()`.

## Control Flow
IPv6 address notifier events add/remove `sctp_sockaddr_entry` records from the per-net local address list under `local_addr_lock`, mark entries invalid before RCU removal, and enqueue ASCONF address-management events through `sctp_addr_wq_mgmt()`. Receive registration uses `sctp6_rcv()`, which clears encapsulation metadata and delegates to common `sctp_rcv()`.

ICMPv6 handling resets skb headers to the embedded SCTP packet, calls common `sctp_err_lookup()` for verification-tag validation and association lookup, then maps packet-too-big to PMTU updates, unknown-next-header to proto-unreachable handling, redirects to route redirect handling, and other ICMPv6 errors to socket hard/soft errors.

Transmit uses `sctp_v6_xmit()`. It applies DSCP overrides, ECN marking, PMTUD `ignore_df`, and either calls `ip6_xmit()` for native SCTP or wraps SCTP in UDP with `udp_tunnel6_xmit_skb()` when both local and remote encapsulation ports are set. Route selection in `sctp_v6_get_dst()` prefers a route-selected source address that is in the association bind list; if that fails, it walks bound IPv6 source addresses by scope and prefix match, taking link-local scope and flowlabel options into account.

## State And Persistence
IPv6 state is in static AF/PF tables, protosw registrations, the IPv6 address notifier, route/dst caches on transports, and per-net local address entries. No data is persisted outside memory. Socket-visible behavior persists through socket options such as `IPV6_V6ONLY`, `SCTP_I_WANT_MAPPED_V4_ADDR`, IPv6 tx options, flowlabel settings, DSCP, PMTUD flags, and UDP encapsulation ports.

## Dependencies And Integration Points
The file integrates with IPv6 core protocol registration, `inet6_register_protosw()`, `proto_register(&sctpv6_prot)`, IPv6 address notifiers, route lookup, flow labels, extension options, ICMPv6, UDP tunnels, dual-stack SCTP socket operations, and common SCTP input/output helpers. It also consumes the IPv4 AF table when translating v4-mapped addresses.

## Risks
Subtle risks include v4-mapped address policy mismatches, link-local addresses without scope IDs, route source selection outside the association bind list, stale dst cookies, ICMPv6 spoofing if common validation is bypassed, UDP-encapsulation checksum/GSO metadata mistakes, and notifier races with RCU readers of the local address list.

## Test Signals
Exercise native IPv6 SCTP, dual-stack sockets with and without `IPV6_V6ONLY`, v4-mapped address conversion, link-local bind/send validation with scope IDs, IPv6 address add/delete notifier updates, ASCONF auto-address queueing, ICMPv6 packet-too-big PMTU changes, unknown-next-header abort behavior, UDP-encapsulated IPv6 SCTP, flowlabel use, proc address formatting, and protosw/protocol register-unregister failure rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/objcnt.c -->
# sources/distributed-fs/ceph-client/net/sctp/objcnt.c

## Purpose
`objcnt.c` implements debug object counters for SCTP allocations. It exposes counters for key SCTP object classes through procfs so developers can spot leaks, unexpected object growth, or lifetime imbalance during testing.

## Important APIs, Types, And Functions
The file declares counters with `SCTP_DBG_OBJCNT()` for `sock`, `ep`, `transport`, `assoc`, `bind_addr`, `bind_bucket`, `chunk`, `addr`, `datamsg`, and `keys`. It builds `sctp_dbg_objcnt[]` with `SCTP_DBG_OBJCNT_ENTRY()` records and exposes them through seq operations: `sctp_objcnt_seq_start()`, `sctp_objcnt_seq_next()`, `sctp_objcnt_seq_stop()`, and `sctp_objcnt_seq_show()`. The integration entry point is `sctp_dbg_objcnt_init(struct net *net)`.

## Control Flow
During per-net SCTP defaults initialization, `sctp_dbg_objcnt_init()` creates `/proc/net/sctp/sctp_dbg_objcnt` below the namespace's SCTP proc directory. Reads iterate by `loff_t` index over `sctp_dbg_objcnt[]`; each row prints a label and `atomic_read()` of the backing counter. There is no custom open/release logic beyond `proc_create_seq()`.

## State And Persistence
Counter state is global atomic in-memory state, incremented and decremented by macros used in other SCTP files. The proc entry is per net namespace, but the counters themselves are not per-net in this file. Values reset only when the module is unloaded or the kernel restarts.

## Dependencies And Integration Points
This depends on SCTP debug counter macros and procfs support initialized by `proc.c`/`protocol.c`. It is useful only when object allocation/free paths elsewhere consistently call the increment/decrement macros.

## Risks
Because counters are global while proc entries are per-net, readers should not interpret the values as namespace-local. Missing instrumentation in an allocation path creates false confidence. Counter imbalance is a diagnostic signal but not proof of a leak unless object lifetime and delayed RCU frees are also considered.

## Test Signals
Read `/proc/net/sctp/sctp_dbg_objcnt` after module init, after opening/closing SCTP sockets, after creating and tearing down associations, after chunk-heavy sends, and after namespace teardown. Counts should return to baseline after grace periods and no row should disappear or read out of bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/objcnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/offload.c -->
# sources/distributed-fs/ceph-client/net/sctp/offload.c

## Purpose
`offload.c` registers SCTP Generic Segmentation Offload support for IPv4 and IPv6. It handles segmentation of SCTP GSO skbs and checksum preparation when hardware cannot compute SCTP CRC32c.

## Important APIs, Types, And Functions
The main initialization entry is `sctp_offload_init()`. Static integration tables are `sctp_offload` and `sctp6_offload`, both with `.callbacks.gso_segment = sctp_gso_segment`. Helpers are `sctp_gso_segment()` and `sctp_gso_make_checksum()`.

## Control Flow
`sctp_offload_init()` registers IPv4 offload first with `inet_add_offload()` and IPv6 offload next with `inet6_add_offload()`, rolling back IPv4 registration if IPv6 registration fails. `sctp_gso_segment()` rejects non-SCTP-GSO skbs, ensures the SCTP common header is pullable, temporarily pulls it before segmentation decisions, and then either accepts robust hardware GSO by recalculating `gso_segs` from the head/frags or calls `skb_segment()` with checksum-capable features.

After software segmentation, if `NETIF_F_SCTP_CRC` is unavailable, it walks produced segments and fills SCTP checksums for `CHECKSUM_PARTIAL` skbs using `sctp_gso_make_checksum()`. That helper resets checksum mode, primes GSO checksum metadata for potential UDP tunneling checksums, and computes CRC from the SCTP transport offset.

## State And Persistence
The file owns only static offload registration structures. Runtime state is per-skb segmentation metadata such as `gso_type`, `gso_segs`, `ip_summed`, `csum_not_inet`, and SCTP checksum fields. Nothing is persisted.

## Dependencies And Integration Points
It integrates with the networking offload framework, IPv4/IPv6 inet offload registries, skbuff GSO helpers, SCTP checksum code, and the output path that marks large SCTP packets as `SKB_GSO_SCTP` or UDP tunnel GSO.

## Risks
Checksum correctness is the central risk. SCTP uses CRC32c rather than the standard Internet checksum, and UDP-encapsulated SCTP also needs correct outer checksum metadata. Incorrect header pulling or `gso_segs` accounting can cause malformed segmentation, bad statistics, or device-driver offload failures. Rollback on init failure must remain paired so SCTP is not partially registered.

## Test Signals
Test native SCTP GSO over IPv4 and IPv6, devices with and without `NETIF_F_SCTP_CRC`, software fallback segmentation, UDP-encapsulated SCTP GSO, cloned/nonlinear skbs, robust GSO paths that return `NULL`, and module init paths where IPv6 offload registration fails after IPv4 succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/output.c -->
# sources/distributed-fs/ceph-client/net/sctp/output.c

## Purpose
`output.c` implements packet-level SCTP output assembly. It owns `struct sctp_packet` initialization, chunk bundling decisions, DATA accounting when chunks are appended, AUTH/SACK/PAD opportunistic bundling, GSO packet packing, checksum setup, and final transmission through AF-specific `sctp_xmit` callbacks.

## Important APIs, Types, And Functions
External APIs include `sctp_packet_init()`, `sctp_packet_config()`, `sctp_packet_free()`, `sctp_packet_append_chunk()`, `sctp_packet_transmit_chunk()`, and `sctp_packet_transmit()`. Core helpers are `sctp_packet_reset()`, `sctp_packet_bundle_auth()`, `sctp_packet_bundle_sack()`, `sctp_packet_bundle_pad()`, `__sctp_packet_append_chunk()`, `sctp_packet_can_append_data()`, `sctp_packet_append_data()`, `sctp_packet_will_fit()`, `sctp_packet_pack()`, and `sctp_packet_gso_append()`.

## Control Flow
`sctp_packet_config()` prepares a transport packet for a flush cycle: it sets the verification tag, path MTU, header overhead, route cache, PMTU synchronization, optional prepended ECNE chunk, socket dst caps, and GSO max size. `sctp_packet_append_chunk()` first applies DATA-specific congestion/window/Nagle checks, then may prepend AUTH and pending SACK chunks before appending the requested chunk. `__sctp_packet_append_chunk()` updates packet flags and, for DATA/I-DATA, assigns TSN and stream sequence numbers, marks RTT measurement candidates, and accounts flight size, outstanding bytes, and peer rwnd.

`sctp_packet_transmit_chunk()` flushes a packet when appending hits PMTU/GSO limits, unless a COOKIE-ECHO packet must remain constrained. `sctp_packet_transmit()` allocates the outgoing head skb, writes the SCTP common header, verifies a dst exists, packs chunks into one skb or a GSO frag list, starts autoclose if DATA was sent, applies ECN capability, updates association packet stats, and calls the transport AF `sctp_xmit()` function. Cleanup frees unsent non-DATA control chunks and resets the packet object.

## State And Persistence
State is in-memory and per packet/transport/association. DATA append mutates transport `flight_size`, association `outstanding_bytes`, peer rwnd, TSN counters, stream sched numbering, chunk `sent_at`, `sent_count`, and RTT flags. Packet flags such as `has_data`, `has_sack`, `has_auth`, `has_cookie_echo`, and `ipfragok` live only for a flush cycle.

## Dependencies And Integration Points
This file depends on chunk constructors from the state machine, SCTP auth, SACK generation, stream scheduler callbacks, PMTU/path state in transports, skbuff allocation/accounting, AF-specific xmit from `protocol.c`/`ipv6.c`, device GSO capabilities, xfrm dst checks, and SCTP MIB/stat counters.

## Risks
The major risks are accounting chunks as in flight before final xmit, mismatched AUTH key bundling, bad PMTU/GSO split decisions, incorrect CRC offload selection, freeing control chunks while preserving DATA chunks for retransmission, and Nagle/rwnd/cwnd checks that can stall or overrun transmission. GSO packing must preserve AUTH HMAC placement and recalculate HMAC after chunks are copied.

## Test Signals
Exercise DATA sends under rwnd full, cwnd full, Nagle delay, no-delay, PMTU-full, GSO-enabled, GSO-disabled, AUTH-required, pending SACK bundling, COOKIE-ECHO bundling, heartbeat PLPMTUD PAD chunks, UDP encapsulation, xfrm routes, missing dst, autoclose timer start, and checksum paths with and without SCTP CRC offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/outqueue.c -->
# sources/distributed-fs/ceph-client/net/sctp/outqueue.c

## Purpose
`outqueue.c` implements association-level outbound queueing, retransmission, SACK processing, congestion interactions, and PR-SCTP abandonment/forward-TSN generation. It is the bridge between state-machine/user chunks and packet assembly in `output.c`.

## Important APIs, Types, And Functions
Primary APIs are `sctp_outq_init()`, `sctp_outq_teardown()`, `sctp_outq_free()`, `sctp_outq_tail()`, `sctp_outq_uncork()`, `sctp_retransmit_mark()`, `sctp_retransmit()`, `sctp_outq_sack()`, `sctp_outq_is_empty()`, `sctp_prsctp_prune()`, and `sctp_generate_fwdtsn()`. Important helpers include `sctp_outq_head_data()`, `sctp_outq_tail_data()`, `sctp_outq_dequeue_data()`, `sctp_insert_list()`, `__sctp_outq_flush_rtx()`, `sctp_outq_flush_ctrl()`, `sctp_outq_flush_rtx()`, `sctp_outq_flush_data()`, `sctp_outq_flush_transports()`, `sctp_check_transmitted()`, `sctp_mark_missing()`, and `sctp_acked()`.

## Control Flow
DATA chunks are queued through the stream scheduler and `out_chunk_list`; control chunks are queued separately and counted as outbound control. Unless corked, `sctp_outq_tail()` immediately flushes. Flush sends control first, respecting SCTP bundling rules that INIT, INIT ACK, and SHUTDOWN COMPLETE are singleton packets. Response chunks may force one-packet behavior; ASCONF source-address restrictions can stop DATA flushing until address reconfiguration completes.

Retransmission starts with `sctp_retransmit()`, which adjusts counters and congestion state based on reason (T3 timeout, fast retransmit, PMTUD, T1), moves eligible transmitted chunks to the sorted retransmit queue with `sctp_retransmit_mark()`, possibly generates FWD-TSN, and flushes for timeout-style retransmits. `__sctp_outq_flush_rtx()` sends at most one packet for timeout/fast retransmit and moves retransmitted chunks back to the chosen transport's transmitted list.

SACK processing in `sctp_outq_sack()` validates cumulative TSN progress, updates CACC state, runs retransmit and per-transport transmitted queues through `sctp_check_transmitted()`, advances `ctsn_ack_point`, marks missing chunks for fast retransmit, recomputes unacknowledged DATA, frees cumulatively acked chunks, updates rwnd, and generates PR-SCTP FWD-TSN when abandoned chunks advance `adv_peer_ack_point`.

## State And Persistence
The outqueue persists association send state in memory: unsent DATA, control chunks, retransmit queue, sacked queue, abandoned queue, outstanding bytes, cork/fast retransmit flags, per-transport transmitted lists, flight sizes, T3 timers, cwnd/ssthresh, rwnd, TSN missing reports, PR-SCTP removable counters, and stream scheduler queues. No disk persistence exists.

## Dependencies And Integration Points
It integrates with `output.c` packet assembly, transport congestion helpers, stream scheduler ops, PR-SCTP policies, SCTP timers, state-machine chunk constructors, trace events, association peer path management, and SACK/FWD-TSN wire formats.

## Risks
Accounting is the hardest risk: bytes must move exactly once between unsent, outstanding, retransmit, sacked, and abandoned states. Reneged SACKs, ASCONF-deleted transports, migrated DATA, zero-window probing, and PR-SCTP abandonment all create edge cases. Fast retransmit marking depends on gap-block interpretation and CACC skip rules; errors can cause spurious retransmits or data stalls. Freeing chunks during teardown must notify send-failure paths without touching already freed stream scheduler state.

## Test Signals
Use tests for normal DATA/SACK progression, gap ACK fast retransmit after three missing reports, reneged gap ACKs, T3 timeout retransmission, PMTU retransmission, COOKIE-ECHO bundling limits, zero-window probe SACKs, PR-SCTP priority pruning of sent/unsent data, FWD-TSN generation, ASCONF source restrictions, stream-closed requeueing, cork/uncork, multi-homed path switch/CACC behavior, and teardown with chunks in every queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/outqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/primitive.c -->
# sources/distributed-fs/ceph-client/net/sctp/primitive.c

## Purpose
`primitive.c` implements SCTP upper-layer protocol primitives as thin wrappers into the SCTP state machine. These functions correspond to SCTP service primitives such as associate, shutdown, abort, send, heartbeat request, ASCONF, and reconf.

## Important APIs, Types, And Functions
The file defines `DECLARE_PRIMITIVE(name)`, which generates `sctp_primitive_ASSOCIATE()`, `sctp_primitive_SHUTDOWN()`, `sctp_primitive_ABORT()`, `sctp_primitive_SEND()`, `sctp_primitive_REQUESTHEARTBEAT()`, `sctp_primitive_ASCONF()`, and `sctp_primitive_RECONF()`. Each takes `struct net *net`, optional `struct sctp_association *asoc`, and a primitive-specific `void *arg`.

## Control Flow
Every generated primitive builds an SCTP state-machine event with type `SCTP_EVENT_T_PRIMITIVE`, subtype `SCTP_ST_PRIMITIVE(SCTP_PRIMITIVE_name)`, current state from `asoc->state` or `SCTP_STATE_CLOSED`, endpoint from `asoc->ep` or `NULL`, and calls `sctp_do_sm()` with `GFP_KERNEL`. The real behavior is table-driven in the SCTP state machine; this file only normalizes primitive invocation and return of the state-machine error code.

## State And Persistence
This file owns no persistent state. State changes happen inside `sctp_do_sm()` actions: association creation, shutdown, abort, enqueueing DATA, heartbeat chunks, address reconfiguration, and stream reconfiguration. The wrapper observes association state only long enough to select the state-machine row.

## Dependencies And Integration Points
It depends on SCTP state-machine definitions in `net/sctp/sm.h` and is called by socket/ULP paths that need to initiate protocol actions. It is the narrow API boundary between user-facing socket operations and lower state-machine processing.

## Risks
Because wrappers are generated by macro, a wrong primitive name or subtype mapping would route user actions to the wrong state-machine event. The wrappers use `GFP_KERNEL`, so they are intended for sleepable user/process context rather than atomic receive paths. Passing `NULL` association is valid for some primitives only if the state-machine table expects closed-state endpoint-less handling.

## Test Signals
Validate each socket operation reaches the expected state-machine primitive, including connect/associate, graceful shutdown, abort with cause, sendmsg DATA, heartbeat request, ASCONF address changes, and RECONF stream reset. Error-path tests should cover invalid state transitions and `NULL` association calls where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/primitive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/proc.c -->
# sources/distributed-fs/ceph-client/net/sctp/proc.c

## Purpose
`proc.c` exposes SCTP observability under `/proc/net/sctp`. It publishes MIB counters, endpoint tables, association tables, and remote-address/transport information for each network namespace.

## Important APIs, Types, And Functions
The initialization API is `sctp_proc_init(struct net *net)`. Proc entries are `snmp`, `eps`, `assocs`, and `remaddr`. Key functions include `sctp_snmp_seq_show()`, `sctp_seq_dump_local_addrs()`, `sctp_seq_dump_remote_addrs()`, endpoint seq operations (`sctp_eps_seq_start/next/stop/show()`), transport rhashtable iterator operations (`sctp_transport_seq_start/next/stop()`), `sctp_assocs_seq_show()`, and `sctp_remaddr_seq_show()`. `struct sctp_ht_iter` embeds `seq_net_private` plus `rhashtable_iter`.

## Control Flow
`sctp_proc_init()` creates the namespace SCTP proc directory and then registers the four read-only files, removing the subtree if any creation fails. `snmp` folds per-CPU SCTP MIB fields into a local buffer and prints name/value rows from `sctp_snmp_list`.

`eps` iterates endpoint hash buckets by position, locks each bucket, filters sockets by seq file net namespace, and prints endpoint pointer, socket pointer, style, state, hash bucket, local port, UID, inode, and local addresses. `assocs` and `remaddr` iterate the transport rhashtable with hold/put discipline; associations are printed once per transport iterator entry, while `remaddr` prints every peer transport for the association visible from the current iterator transport.

Address dumping is AF-polymorphic: local and remote address printers use `sctp_get_af_specific()` and `af->seq_dump_addr()`, marking primary addresses with `*`.

## State And Persistence
Proc output is a live snapshot of in-memory SCTP counters, endpoint hash state, association state, transport lists, timers, socket buffers, and address lists. It does not store history. The proc directory exists per net namespace and is removed during SCTP per-net cleanup.

## Dependencies And Integration Points
This file depends on procfs, seq_file, SCTP MIB allocation, endpoint hash tables from `input.c`/`protocol.c`, transport rhashtable iterators, AF address dump callbacks, socket UID/inode helpers, and net namespace filtering.

## Risks
Iterator lifetime and locking are central. Endpoint iteration uses bucket read locks, while transport iteration must hold and release transports correctly around seq transitions. Association and transport lists are live and RCU-protected in places, so output can be approximate under concurrent changes. Pointer printing uses `%pK`, respecting kernel pointer exposure policy, but still exposes diagnostic topology.

## Test Signals
Check proc files in initial, active, and teardown states; verify per-net namespace filtering; compare SNMP counters with traffic; create multihomed associations and verify local/remote primary markers; read while associations are closing; test failure cleanup by forcing one proc entry creation to fail; and validate `remaddr` timer/state fields after heartbeat and path failure events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/protocol.c -->
# sources/distributed-fs/ceph-client/net/sctp/protocol.c

## Purpose
`protocol.c` initializes and tears down SCTP protocol support and provides the IPv4 AF/PF implementation. It owns global caches, hash tables, per-net defaults, local address tracking, IPv4 routing/transmit helpers, UDP tunneling sockets, AF/PF registration, socket protocol registration, and module init/exit.

## Important APIs, Types, And Functions
Important exported or cross-file APIs include `sctp_copy_local_addr_list()`, `sctp_addr_wq_mgmt()`, `sctp_udp_sock_start()`, `sctp_udp_sock_stop()`, `sctp_register_af()`, `sctp_get_af_specific()`, `sctp_get_pf_specific()`, and `sctp_register_pf()`. Static initialization functions include `sctp_defaults_init()`, `sctp_defaults_exit()`, `sctp_ctrlsock_init()`, `sctp_ctrlsock_exit()`, and module-level `sctp_init()`/`sctp_exit()`.

The IPv4 AF/PF tables are `sctp_af_inet` and `sctp_pf_inet`, with helpers for address copy/parse/compare/scope, bind/send verification, route lookup, source address selection, ECN, skb msgname construction, and `sctp_v4_xmit()`. Socket registrations include `sctp_seqpacket_protosw`, `sctp_stream_protosw`, `sctp_protocol`, and `inet_seqpacket_ops`.

## Control Flow
Module init creates bind-bucket and chunk slab caches, initializes global counters and association IDR, computes memory sysctls, allocates endpoint and bind-port hash tables, initializes the transport rhashtable, registers global sysctls, registers IPv4/IPv6 AF/PF tables and stream scheduler ops, registers per-net default setup, registers IPv4/IPv6 socket protosw entries, creates per-net control sockets, registers IPv4/IPv6 protocol handlers, and finally registers SCTP offload. Each failure label unwinds the subset already initialized.

Per-net defaults set SCTP timers, retransmit limits, feature defaults (ADDIP, PR-SCTP, RECONF, AUTH, ECN, UDP encapsulation, scope policy, L3 master accept), sysctls, MIBs, proc entries, debug object counters, local address list, ASCONF address wait queue, and address wait timer. Exit frees address queues/lists, proc subtree, MIBs, and sysctls.

IPv4 address notifiers maintain `net->sctp.local_addr_list` under RCU and queue ASCONF notifications. The address wait timer batches add/delete events and invokes `sctp_asconf_mgmt()` for auto-ASCONF sockets bound to all addresses. `sctp_v4_get_dst()` performs route lookup and verifies/selects a source address from the association bind list; `sctp_v4_xmit()` sends either native SCTP with `__ip_queue_xmit()` or UDP-encapsulated SCTP with `udp_tunnel_xmit_skb()`.

## State And Persistence
Persistent runtime state includes global SCTP caches, hash tables, AF/PF function pointers, per-net defaults/sysctls, local address lists, address wait queues, control sockets, UDP tunnel sockets, MIBs, and module parameter `sctp_checksum_disable` exposed as `no_checksums`. All state is in memory and removed on net namespace exit or module unload.

## Dependencies And Integration Points
The file integrates with IPv4/IPv6 core protocol registries, socket protosw, `struct proto` definitions from socket code, sysctl, procfs, net namespaces, inet address notifiers, route lookup, UDP tunnel helpers, SCTP input/output, stream scheduler registration, slab/percpu allocation, and SCTP offload registration.

## Risks
Initialization ordering is fragile because many later pieces assume AF/PF tables, hash tables, per-net fields, and control sockets exist. Unwind labels must stay paired with successful init steps. Address notifier and ASCONF queue logic must handle add/delete flapping and IPv6 DAD delays without leaking entries. Route/source selection must not choose an address outside the bind list unless explicitly allowed. The `no_checksums` parameter is dangerous for real networks because it disables SCTP checksum verification/computation.

## Test Signals
Test module load/unload, IPv4 and IPv6 socket creation for `SOCK_SEQPACKET` and `SOCK_STREAM`, per-net namespace init/exit, sysctl defaults, proc creation, local address list population, address add/delete ASCONF batching, UDP tunnel socket start/stop, IPv4 PMTU/ECN/DSCP transmit behavior, source address selection from multihomed bind lists, failure injection at each init step, and `no_checksums` behavior on receive/transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sctp/protocol.c -->
