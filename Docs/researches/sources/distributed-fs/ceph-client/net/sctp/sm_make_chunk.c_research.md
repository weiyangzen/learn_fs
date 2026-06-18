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
