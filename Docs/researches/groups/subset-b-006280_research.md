# subset-b-006280 Research

Grouped code research for the Ceph client copy of Linux SMC socket, CLC handshake, CDC flow-control, and close-state code. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/af_smc.c -->
# sources/distributed-fs/ceph-client/net/smc/af_smc.c

## Purpose
`af_smc.c` implements the `PF_SMC` socket family for Shared Memory Communications over RDMA (`SMC-R`) and ISM/direct memory (`SMC-D`). It presents TCP-like stream socket operations while creating an internal TCP CLC socket for connection establishment, address handling, socket options, and fallback. The file owns socket allocation, bind/connect/listen/accept/send/receive/poll/shutdown/ioctl/splice behavior, client and server CLC handshake orchestration, fallback to TCP, link-group creation serialization, per-net initialization, workqueues, protocol registration, and module lifecycle.

## Important APIs, Types, And Functions
Externally visible socket operations include `smc_release()`, `smc_bind()`, `smc_connect()`, `smc_accept()`, `smc_getname()`, `smc_poll()`, `smc_ioctl()`, `smc_listen()`, `smc_shutdown()`, `smc_setsockopt()`, `smc_getsockopt()`, `smc_sendmsg()`, `smc_recvmsg()`, and `smc_splice_read()`. Creation and core helpers include `smc_sk_init()`, `smc_create_clcsk()`, `smc_hash_sk()`, `smc_unhash_sk()`, `smc_release_cb()`, and `smc_fill_gid_list()`. Handshake paths center on `__smc_connect()`, `smc_connect_rdma()`, `smc_connect_ism()`, `smc_listen_work()`, `smc_listen_find_device()`, and the RDMA/ISM finder helpers. It defines `smc_proto`, `smc_proto6`, `smc_sock_ops`, `smc_sock_family_ops`, SMC hash tables, and the `smc_tcp_ls_wq`, `smc_hs_wq`, and `smc_close_wq` workqueues.

## Control Flow
Socket creation allocates `struct smc_sock`, initializes the SMC state as `SMC_INIT`, creates a kernel TCP CLC socket, and registers the SMC sock in the protocol hash. `connect()` first delegates TCP connection establishment to the CLC socket with `tcp_sk(...)->syn_smc = 1`; once TCP reaches established state, `__smc_connect()` checks peer SMC capability, IPsec exclusion, VLAN state, and local RDMA/ISM resources, sends a CLC proposal, receives an accept, then creates either SMC-R or SMC-D resources before sending confirm. Nonblocking connects run the same path in `smc_connect_work()`.

`listen()` installs CLC data-ready and TCP `syn_recv_sock` hooks, starts TCP listen, and marks the SMC socket `SMC_LISTEN`. Accepted TCP children are drained by `smc_tcp_listen_work()`, wrapped in new `smc_sock` objects, and processed by `smc_listen_work()`. The server path receives proposal, validates version/features, selects SMC-D v2, SMC-D v1, SMC-R v2, or SMC-R v1 in preference order, sends accept, receives confirm, finalizes RDMA if needed, then enqueues the child for user `accept()`. If negotiation cannot proceed but TCP remains usable, `smc_switch_to_fallback()` rewires file ownership and CLC callbacks so the SMC socket behaves as TCP.

## State And Persistence
Persistent socket state lives in `struct smc_sock`: embedded `struct sock`, internal `clcsock`, saved TCP callbacks, `struct smc_connection`, listen parent, accept queue, work items, fallback flags/reason, peer diagnosis, queued handshake count, copied AF ops, deferred-accept value, and release mutex. Link-group creation is serialized by global client/server mutexes. Runtime state transitions use `SMC_INIT`, `SMC_ACTIVE`, `SMC_LISTEN`, close states, and `SMC_CLOSED`. Per-net SMC sysctls, stats, fallback counters, PNET state, and handshake limitation flags are initialized by pernet operations.

## Dependencies And Integration Points
The file integrates with TCP internals, inet/IPv6 socket ops, generic netlink, BPF handshake control, SMC CLC/CDC/LLC/TX/RX/close/core/stat modules, RDMA device discovery, ISM devices, PNET resource selection, sysctls, tracepoints, and pernet namespace state. It exports protocol structs used by SMC inet integration and uses TCP CLC socket operations for fallback, name lookup, socket options, and unsupported data paths.

## Risks And Edge Cases
The highest-risk areas are lifetime and callback ordering around fallback, listen hooks, nonblocking connect cancellation, accepted but not user-accepted sockets, and workqueue-delayed close/connect/listen paths. Handshake failure codes must distinguish fatal errors from TCP fallback reasons. RDMA first-contact paths must register buffers, exchange LLC confirmation, and unwind link groups without leaking or terminating a shared group incorrectly. Accept backlog and handshake backlog interact through `queued_smc_hs`. Socket option handling can trigger fallback for unsupported TCP fast-open options, while cork/nodelay options flush SMC TX state.

## Test Signals
Useful signals include SMC-R and SMC-D loop/connect/listen/accept tests, nonblocking connect and poll readiness, TCP fallback when peer lacks SMC capability, IPsec fallback, no-device fallback, CLC decline handling, backlog and handshake-limitation behavior, TCP fast-open option rejection/fallback, deferred accept for SMC and fallback children, close of listening sockets with queued children, splice/ioctl/poll parity with TCP, module load/unload, pernet namespace creation/destruction, and lockdep/KASAN/KCSAN coverage across callback replacement and work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/af_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc.h -->
# sources/distributed-fs/ceph-client/net/smc/smc.h

## Purpose
`smc.h` is the socket-facing internal contract for the SMC subsystem. It defines SMC protocol versions, release level, protocol numbers, socket states, feature flags, CDC flag and cursor host representations, the central `struct smc_connection`, the `struct smc_sock` socket container, exported socket operation prototypes, callback helpers, byte-order helpers, IPsec detection, workqueue declarations, and accept/fallback utility prototypes.

## Important APIs, Types, And Functions
Important types include `enum smc_state`, `enum smc_supplemental_features`, `struct smc_wr_rx_hdr`, `struct smc_cdc_conn_state_flags`, `struct smc_cdc_producer_flags`, `union smc_host_cursor`, `struct smc_host_cdc_msg`, `enum smc_urg_state`, `struct smc_connection`, and `struct smc_sock`. Inline helpers include `smc_sk()`, `smc_init_saved_callbacks()`, `smc_clcsock_user_data()`, `smc_clcsock_user_data_rcu()`, `smc_clcsock_replace_cb()`, `smc_clcsock_restore_cb()`, `hton24()`, `ntoh24()`, `using_ipsec()`, and `smc_sock_set_flag()`. The header declares the socket operation functions implemented in `af_smc.c` and workqueue globals used by close, handshake, and TX/CDC logic.

## Control Flow
The header has little standalone execution, but it shapes the subsystem control flow. `struct smc_sock` is allocated as the protocol object and wraps a TCP CLC socket plus SMC connection state. Socket operations use `smc_sk()` to move from `struct sock` to the container. TCP callback replacement stores originals in `smc_sock` fields and restores them with the inline helpers during fallback or listen teardown. CDC receive and transmit paths update `struct smc_connection` cursors and flags, while close paths interpret `enum smc_state` values to progress active and passive shutdown.

## State And Persistence
`struct smc_connection` persists link-group membership, selected RDMA link, local alert token, peer RMB metadata, send/RMB buffer descriptors, cursor state for local TX/RX CDC messages, send-buffer and peer-buffer space counters, CDC sequence numbers, pending WR counters, TX retry work, urgent-data state, receive byte counters, close/abort work, SMC-D receive tasklet, peer token, and killed/freed/out-of-sync flags. `struct smc_sock` persists CLC socket pointer, saved callbacks, listen parent and accept queue, handshake work, fallback flags, peer diagnosis, and release locking. These fields are shared by socket operations, CDC/TX/RX, close, and core link-group code.

## Dependencies And Integration Points
`smc.h` includes Linux socket/sock/genetlink types and `smc_ib.h`, and is included across nearly all SMC modules. It integrates with TCP callback user-data conventions, optional XFRM/IPsec policy checks, netlink handshake-limit commands, SMC core link groups, RDMA link/buffer descriptors, SMC-D tasklet handling, and generic socket flags.

## Risks And Edge Cases
The header encodes wire-adjacent bitfield layout for CDC flags, so endian definitions must stay aligned with protocol expectations. Cursor copying uses atomic64 where available and a connection spinlock otherwise; mixed use can produce corrupt flow control. `struct smc_connection` lifetime is tied to async work, tasklets, and link-group cleanup, making field ownership and state transitions sensitive. TCP callback save/restore helpers only save once, so nested replacement must preserve ordering.

## Test Signals
Primary signals are build coverage across IPv4, IPv6, XFRM enabled/disabled, and architectures with or without `ATOMIC64_INIT`; runtime close-state, urgent-data, fallback-callback, and CDC cursor tests; static assertions or protocol tests for bitfield and 24-bit conversion layout; and lockdep/KCSAN coverage around cursor and callback state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_cdc.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_cdc.c

## Purpose
`smc_cdc.c` implements Connection Data Control processing for SMC. CDC messages carry producer and consumer cursors, flow-control flags, urgent-data indications, close/abort bits, and failover validation state. The file handles CDC send completion, CDC send construction for SMC-R and SMC-D, pending WR accounting, receive-side cursor updates, wakeups, close scheduling, failover validation, SMC-D tasklet receive, and registration of the CDC work-request receive handler.

## Important APIs, Types, And Functions
Public functions include `smc_cdc_get_free_slot()`, `smc_cdc_msg_send()`, `smcr_cdc_msg_send_validation()`, `smc_cdc_get_slot_and_msg_send()`, `smc_cdc_wait_pend_tx_wr()`, `smcd_cdc_msg_send()`, `smcd_cdc_rx_init()`, and `smc_cdc_init()`. Key internal helpers are `smc_cdc_tx_handler()`, `smc_cdc_add_pending_send()`, `smcr_cdc_get_slot_and_msg_send()`, `smc_cdc_handle_urg_data_arrival()`, `smc_cdc_msg_validate()`, `smc_cdc_msg_recv_action()`, `smc_cdc_msg_recv()`, `smcd_cdc_rx_tsklet()`, and `smc_cdc_rx_handler()`.

## Control Flow
On SMC-R transmit, callers obtain a WR slot with `smc_cdc_get_free_slot()`, fill it through `smc_cdc_msg_send()`, increment `cdc_pend_tx_wr`, and post it via `smc_wr_tx_send()`. Completion enters `smc_cdc_tx_handler()`, which advances confirmed TX cursors, frees local send-buffer space, records completed CDC sequence, decrements pending WRs, wakes waiters, and triggers pending TX if the last CDC completed. SMC-D bypasses WR slots: `smcd_cdc_msg_send()` writes a CDC header into peer DMB memory and updates local confirmed receive cursor and local send-buffer space unless nocopy DMB requires waiting for peer consumption.

Receive starts from `smc_cdc_rx_handler()` for SMC-R work completions or `smcd_cdc_rx_tsklet()` for SMC-D DMB notifications. The handler validates length/type, finds the connection by alert token in the link group, drops stale sequence numbers, handles failover validation, then calls `smc_cdc_msg_recv_action()`. That action imports peer cursors, increases peer RMB space when the peer consumes data, increases local `bytes_to_rcv` when the peer produces data, handles urgent data, wakes readers/writers, schedules TX when consumer updates request more sends, marks reset on peer abort, and queues close work for close or send-done flags.

## State And Persistence
CDC state persists in `struct smc_connection`: `local_tx_ctrl`, `local_rx_ctrl`, `tx_curs_sent`, `tx_curs_fin`, `local_tx_ctrl_fin`, `rx_curs_confirmed`, `peer_rmbe_space`, `sndbuf_space`, `bytes_to_rcv`, `tx_cdc_seq`, `tx_cdc_seq_fin`, `cdc_pend_tx_wr`, `cdc_pend_tx_wq`, urgent fields, `out_of_sync`, and `tx_in_release_sock`. Pending send-private state is stored in `struct smc_cdc_tx_pend` until completion.

## Dependencies And Integration Points
The file depends on SMC WR posting and receive-handler registration, TX pending logic, RX wakeups, close workqueue handling, SMC-D ISM write and nocopy capability, link-group connection lookup, socket wait queues, and RDMA completion status. It is the flow-control bridge between `smc_tx.c`, `smc_rx.c`, `smc_close.c`, and lower SMC-R/SMC-D transports.

## Risks And Edge Cases
Pending WR counters must stay balanced on post failures, killed connections, and failover validation sends. Cursor import rejects backwards movement but must tolerate wrap semantics. SMC-D nocopy changes when send-buffer space is released, relying on peer consumer updates. `sock_owned_by_user()` paths defer TX to `release_cb()` to avoid socket-lock recursion. Out-of-sync failover validation schedules abort work and changes the connection link under `send_lock`.

## Test Signals
High-value tests include CDC sequence wrap and stale-message drops, peer consumer updates freeing send space, producer updates waking readers, `cons_curs_upd_req` causing TX, urgent-data inline and out-of-band behavior, peer done/closed/abort close scheduling, killed connection send failure, SMC-D nocopy and non-nocopy send-space release, failover validation handling, pending WR wait wakeups, and KCSAN/lockdep coverage around cursor and `send_lock` updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_cdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_cdc.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_cdc.h

## Purpose
`smc_cdc.h` defines CDC wire-format messages, SMC-D CDC layout, cursor conversion helpers, cursor arithmetic, close-state predicates, pending-send metadata, and CDC function prototypes. It is the shared contract between transmit, receive, close, SMC-R WR handling, and SMC-D memory notification paths.

## Important APIs, Types, And Functions
The header defines `SMC_CDC_MSG_TYPE`, `union smc_cdc_cursor`, `struct smc_cdc_msg`, `union smcd_cdc_cursor`, `struct smcd_cdc_msg`, and `struct smc_cdc_tx_pend`. Inline helpers include `smc_cdc_rxed_any_close()`, `smc_cdc_rxed_any_close_or_senddone()`, `smc_curs_add()`, `smc_curs_copy()`, `smc_curs_copy_net()`, `smcd_curs_copy()`, `smc_curs_diff()`, `smc_curs_comp()`, `smc_curs_diff_large()`, `smc_host_cursor_to_cdc()`, `smc_host_msg_to_cdc()`, `smc_cdc_cursor_to_host()`, `smcr_cdc_msg_to_host()`, `smcd_cdc_msg_to_host()`, and `smc_cdc_msg_to_host()`.

## Control Flow
Transmit code stages host-order CDC state in `conn->local_tx_ctrl`, then `smc_host_msg_to_cdc()` snapshots the producer and consumer cursors and converts fields to network order before posting an SMC-R WR. Receive code uses `smc_cdc_msg_to_host()` to choose SMC-R or SMC-D conversion, then imports cursor movement into `conn->local_rx_ctrl`. Cursor helpers calculate ring-buffer deltas for send-buffer space, peer RMB space, received data, and splice/urgent positioning. Close code uses the inline predicates to decide whether peer close, peer abort, or send-done flags have arrived.

## State And Persistence
The header itself owns no storage, but its data layouts directly persist in connection fields and on the wire. SMC-R CDC messages are network-byte-order WR payloads with token/sequence/cursors. SMC-D CDC messages are embedded in DMB memory with compact producer/consumer cursor unions carrying flags. `struct smc_cdc_tx_pend` persists per posted CDC WR until completion, carrying the connection pointer, sent cursor, producer cursor snapshot, and control sequence.

## Dependencies And Integration Points
`smc_cdc.h` includes `smc.h`, `smc_core.h`, and `smc_wr.h`, binding CDC to connection state, link groups, and work-request APIs. It is consumed by CDC implementation, TX/RX cursor accounting, close handling, and SMC-D receive initialization.

## Risks And Edge Cases
Cursor arithmetic is protocol-critical. The helpers assume the caller supplies correct buffer sizes and that deltas do not exceed ring capacity except in the explicit large-diff helper. Atomic cursor copying must remain consistent across host and network cursor unions. `smc_cdc_cursor_to_host()` intentionally ignores backwards cursor movement to prevent stale control messages from corrupting state. Any layout change must preserve wire format, alignment, and WR size constraints enforced in `smc_cdc.c`.

## Test Signals
Useful signals include unit-style cursor arithmetic tests for wrap, backwards movement, full-buffer deltas, and large wrap cases; byte-order/layout checks for SMC-R and SMC-D CDC messages; integration tests for close predicate behavior; and cross-architecture builds for endian bitfields and atomic64/no-atomic64 cursor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_cdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_clc.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_clc.c

## Purpose
`smc_clc.c` implements CLC, the TCP in-band handshake protocol used before SMC-R/SMC-D data transfer. It manages user and system EID negotiation, netlink EID/SEID operations, CLC message validation, IP prefix construction and matching, CLC receive framing, DECLINE/PROPOSAL/ACCEPT/CONFIRM construction, v2 feature negotiation, hostname initialization, and cleanup of the EID table.

## Important APIs, Types, And Functions
Public functions include `smc_clc_ueid_count()`, `smc_nl_add_ueid()`, `smc_nl_remove_ueid()`, `smc_nl_flush_ueid()`, `smc_nl_dump_ueid()`, `smc_nl_dump_seid()`, `smc_nl_enable_seid()`, `smc_nl_disable_seid()`, `smc_clc_match_eid()`, `smc_clc_prfx_match()`, `smc_clc_wait_msg()`, `smc_clc_send_decline()`, `smc_clc_send_proposal()`, `smc_clc_send_confirm()`, `smc_clc_send_accept()`, `smc_clc_srv_v2x_features_validate()`, `smc_clc_clnt_v2x_features_validate()`, `smc_clc_v2x_features_confirm_check()`, `smc_clc_get_hostname()`, `smc_clc_init()`, and `smc_clc_exit()`. Internal helpers validate UEIDs, validate message headers/lengths/trailers, build first-contact extensions, and fill SMC-R/SMC-D accept-confirm payloads.

## Control Flow
EID control flows through a global locked table. Netlink add validates a 32-byte UEID, rejects duplicates and over-capacity, and appends it. Remove and flush delete entries; on s390, removing the last UEID re-enables system EID use. During handshake, `smc_clc_send_proposal()` builds an iovec containing the base proposal, optional SMC-D v1 data, optional IP prefix data, optional v2 extension with UEIDs and SMC-R RoCE GID, optional SMC-D v2 extension with system EID and GID/CHID pairs, and trailer, then sends it over the CLC socket.

`smc_clc_wait_msg()` peeks the CLC header from the TCP stream to determine exact message length, receives that many bytes without consuming following data, validates eyecatcher/type/length/trailer, drains any extra proposal bytes beyond the caller buffer, and returns either success, peer-decline reason, or socket/protocol error. Accept and confirm share `smc_clc_send_confirm_accept()`, which selects SMC-D or SMC-R formatting, inserts first-contact extension data when required, and sends the assembled iovec. Feature validation compares release, max connections, max links, and feature masks across proposal, accept, and confirm.

## State And Persistence
Persistent module state is `smc_hostname` and the global `smc_clc_eid_table` containing a rwlock, UEID list, UEID count, and SEID-enabled flag. Handshake-specific data persists only through CLC wire messages and the caller's `struct smc_init_info`: selected versions, negotiated EID, release number, feature mask, max connections/links, GID/CHID candidates, and routing data.

## Dependencies And Integration Points
The file integrates with generic netlink attributes, UTS hostname, TCP socket send/recv, IPv4/IPv6 address and prefix inspection, network device/dst lookup under RCU, SMC core initialization data, RDMA GID/MAC values, ISM system EID/GID/CHID helpers, SMC netlink family definitions, and version/feature constants from `smc.h` and `smc_clc.h`.

## Risks And Edge Cases
CLC parsing is security-sensitive because it handles peer-controlled lengths and offsets. Validation must reject malformed offsets, excessive IPv6 prefix counts, excessive UEIDs/GID entries, wrong accept lengths, and missing trailers. The proposal validator references SMC-D v2 extension sizing only when v2 data is present; offset helpers must prevent out-of-bounds access. `smc_clc_wait_msg()` temporarily overwrites CLC socket receive timeout and must restore it on every exit. SEID behavior differs on s390 versus other platforms.

## Test Signals
Useful tests include netlink add/remove/flush/dump UEID and SEID behavior, invalid UEID character and count rejection, proposal/accept/confirm/decline encode/decode length checks for v1/v2 SMC-R/SMC-D, malformed CLC fuzzing, TCP stream coalescing where extra bytes follow a CLC message, timeout and signal interruption in `smc_clc_wait_msg()`, IPv4/v4-mapped/IPv6 prefix match tests, feature negotiation for release/max-links/max-conns, and endian/layout tests for packed CLC structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_clc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_clc.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_clc.h

## Purpose
`smc_clc.h` defines the CLC wire protocol used for SMC negotiation over the internal TCP socket. It provides message type constants, SMC type encodings, wait timeouts, decline reason codes, packed v1/v2 proposal/accept/confirm/decline layouts, extension layouts for SMC-Dv2 and first contact, bounded proposal-area storage, offset helpers, type helpers, and CLC function prototypes.

## Important APIs, Types, And Functions
Important definitions include `SMC_CLC_PROPOSAL`, `SMC_CLC_ACCEPT`, `SMC_CLC_CONFIRM`, `SMC_CLC_DECLINE`, `SMC_TYPE_R`, `SMC_TYPE_D`, `SMC_TYPE_N`, `SMC_TYPE_B`, `CLC_WAIT_TIME`, and the `SMC_CLC_DECL_*` diagnosis codes. Core wire structs include `smc_clc_msg_hdr`, `smc_clc_msg_trail`, `smc_clc_msg_local`, `smc_clc_ipv6_prefix`, `smc_clc_v2_extension`, `smc_clc_msg_proposal`, `smc_clc_msg_proposal_area`, `smcr_clc_msg_accept_confirm`, `smcd_clc_msg_accept_confirm_common`, `smc_clc_first_contact_ext`, `smc_clc_first_contact_ext_v2x`, `smc_clc_fce_gid_ext`, `smc_clc_msg_accept_confirm`, `smc_clc_msg_decline`, and `smc_clc_msg_decline_v2`. Inline helpers locate variable proposal extensions and test indicated SMC types.

## Control Flow
`af_smc.c` and `smc_clc.c` use these layouts to build and parse the CLC state machine: client sends proposal, server sends accept, client sends confirm, or either side sends decline. Offset helpers such as `smc_clc_proposal_get_prefix()`, `smc_get_clc_msg_smcd()`, `smc_get_clc_v2_ext()`, `smc_get_clc_smcd_v2_ext()`, and `smc_get_clc_first_contact_ext()` let parsers navigate variable-length proposal and accept-confirm data while bounding offsets against `smc_clc_msg_proposal_area`.

## State And Persistence
The header owns no runtime storage, but its structs are serialized directly on the TCP CLC connection and copied into initialization/link-group state. The decline reason constants persist in fallback statistics and peer diagnosis fields. Negotiated EIDs, GIDs, CHIDs, release, max connections, max links, feature masks, first-contact hostnames, and SMC-D tokens originate from these wire structs.

## Dependencies And Integration Points
`smc_clc.h` includes RDMA verbs, public Linux SMC UAPI constants, `smc.h`, and SMC netlink definitions. It is consumed by socket handshake code, CLC encoding/decoding, SMC-R link setup, SMC-D device selection, netlink EID management, and feature negotiation.

## Risks And Edge Cases
Most structs are packed or aligned for external protocol compatibility. Bitfields depend on endian configuration, and variable-length extension offsets must remain consistent with `static_assert()` guarded fixed portions. Adding fields outside the tagged fixed groups would break offset calculations. The unioned accept/confirm layout reuses overlapping SMC-R and SMC-D data; callers must use `hdr.typev1` and `is_smcd` consistently.

## Test Signals
Signals include compile-time layout/static-assert coverage, protocol capture comparison for v1/v2 CLC messages, fuzz tests for extension offsets and counts, decline-code mapping tests, first-contact extension parsing, SMC type helper tests, and cross-endian build coverage for header bitfields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_clc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_close.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_close.c

## Purpose
`smc_close.c` implements normal and abnormal SMC socket shutdown. It releases internal TCP CLC sockets, cleans up unaccepted children, waits for prepared sends to leave the send buffer, sends CDC close/write-done/abort indicators, cancels pending close/TX work, handles active aborts, drives active close and shutdown-write state transitions, processes peer close/abort work, frees connections, and initializes close work items.

## Important APIs, Types, And Functions
Public functions are `smc_clcsock_release()`, `smc_close_wake_tx_prepared()`, `smc_close_abort()`, `smc_close_active_abort()`, `smc_close_active()`, `smc_close_shutdown_write()`, and `smc_close_init()`. Internal helpers include `smc_close_cleanup_listen()`, `smc_close_stream_wait()`, `smc_close_wr()`, `smc_close_final()`, `smc_close_cancel_work()`, `smc_close_sent_any_close()`, `smc_close_passive_abort_received()`, and `smc_close_passive_work()`.

## Control Flow
Active full close enters `smc_close_active()`. From `SMC_ACTIVE`, it waits up to linger or `SMC_MAX_STREAM_WAIT_TIMEOUT` for prepared TX data, flushes pending TX, cancels delayed TX work, sends final close CDC flags, moves to `SMC_PEERCLOSEWAIT1`, and shuts down the CLC TCP socket. Other states either confirm a peer close, finish after prior shutdown-write, wait for peer final close, or send an abort from `SMC_PROCESSABORT`. `smc_close_shutdown_write()` is the half-close path: from active it flushes data, sends `peer_done_writing`, and moves to `SMC_PEERCLOSEWAIT1`; from passive close it acknowledges write shutdown and moves to `SMC_APPCLOSEWAIT2`.

Passive close is scheduled by CDC receive into `conn.close_work`. `smc_close_passive_work()` locks the socket, interprets `peer_conn_abort`, `peer_conn_closed`, and `peer_done_writing`, transitions among active/passive close states, wakes readers and writers, and frees the SMC connection plus CLC socket when the socket is dead or detached. Active abort marks errors, aborts the TCP CLC socket, cancels close/TX work, drives states to `SMC_CLOSED`, and releases resources depending on whether passive close references remain.

## State And Persistence
Close state is stored in `sk->sk_state`, `sk_shutdown`, `sk_err`, CDC transmit and receive connection-state flags, `conn.killed`, `wait_close_tx_prepared`, delayed TX work, close work, and CLC socket pointer protected by `clcsock_release_lock`. Listen cleanup drains `accept_q` and closes never-accepted SMC children. Socket references are deliberately held for passive close and workqueue paths, with `sock_put()` paired in state transitions.

## Dependencies And Integration Points
The file depends on `smc_tx_prepared_sends()`, `smc_tx_pending()`, CDC send helpers, close predicates from `smc_cdc.h`, connection freeing from SMC core, TCP abort/shutdown/release, socket wait queues, and the shared `smc_close_wq`. It is called from `af_smc.c` release/shutdown/listen cleanup and from CDC receive when peer close flags arrive.

## Risks And Edge Cases
The close state machine is reference-count sensitive. Some states represent postponed passive close and require exactly one `sock_put()`. Work cancellation temporarily releases the socket lock to avoid deadlocks. `smc_close_final()` sends abort instead of clean close if unread bytes remain. Linger and process-exiting paths alter wait duration. CLC socket release must handle listen children and avoid canceling the currently running listen work. Races with peer close can force the active path to restart its switch.

## Test Signals
Useful tests include active close with and without pending corked data, shutdown write followed by peer close, passive peer done-writing, passive peer closed, peer abort with unread data, simultaneous close, close while listen children are queued, release during nonblocking connect/listen work, linger timeout and signal interruption, abnormal link termination, CLC socket release races, and lockdep/refcount/KASAN coverage for close work cancellation and final `sock_put()` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_close.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_close.h

## Purpose
`smc_close.h` is the small public interface for SMC close handling. It declares timeout constants and the close/release/abort functions used by socket operations, CDC receive processing, and connection setup/teardown code.

## Important APIs, Types, And Functions
The header defines `SMC_MAX_STREAM_WAIT_TIMEOUT` as the default maximum wait for prepared stream data during close and `SMC_CLOSE_SOCK_PUT_DELAY` as a close-related delay constant. It declares `smc_close_wake_tx_prepared()`, `smc_close_active()`, `smc_close_shutdown_write()`, `smc_close_init()`, `smc_clcsock_release()`, `smc_close_abort()`, and `smc_close_active_abort()`.

## Control Flow
`af_smc.c` calls `smc_close_init()` during socket initialization, `smc_close_active()` from release and full shutdown paths, `smc_close_shutdown_write()` from `SHUT_WR`, `smc_close_active_abort()` during failed or aborted active setup, and `smc_clcsock_release()` during final cleanup. `smc_cdc.c` and TX logic use `smc_close_abort()` and `smc_close_wake_tx_prepared()` to signal close or unblock a close waiting for TX progress.

## State And Persistence
The header owns no storage. Its constants bound close wait behavior, while declared functions operate on persistent `struct smc_sock` and `struct smc_connection` state defined in `smc.h`: socket state, CLC socket pointer, CDC flags, close work, TX work, and pending TX indicators.

## Dependencies And Integration Points
`smc_close.h` includes workqueue support and `smc.h`, making it available to AF_SMC socket operations, CDC flow-control, TX send paths, and core cleanup paths. It is the compile-time boundary between close-state implementation and the rest of the SMC subsystem.

## Risks And Edge Cases
Because the header exposes only high-level close actions, callers must hold the correct socket lock and reference expectations required by `smc_close.c`. Misuse can cause double release of CLC sockets, missed wakeups for close waiting on prepared TX data, or unmatched passive-close references.

## Test Signals
Header-level signals are build coverage and correct linkage. Runtime signals come from the `smc_close.c` state-machine tests: active close, half close, abort, pending TX wakeup, CLC release, and workqueue cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_close.h -->
