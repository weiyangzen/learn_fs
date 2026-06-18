
# sources/distributed-fs/ceph-client/include/trace/events/rxrpc.h

## Purpose
Defines the AF_RXRPC tracepoint catalog. The header gives ftrace, perf, BPF, and tracefs users a typed view of RxRPC local endpoint, peer, bundle, connection, call, skb, packet, ACK, retransmission, congestion-control, path-MTU, RACK/TLP, timer, abort, and RxGK rekey activity.

## Important APIs, Types, and Functions
The file is almost entirely trace metadata: large `EM`/`E_` enum tables, byte-sized enum declarations, `TRACE_DEFINE_ENUM()` exports, and `TRACE_EVENT()` declarations. Important enum tables include `rxrpc_abort_reasons`, `rxrpc_local_traces`, `rxrpc_peer_traces`, `rxrpc_bundle_traces`, `rxrpc_conn_traces`, `rxrpc_client_traces`, `rxrpc_call_traces`, `rxrpc_txqueue_traces`, `rxrpc_txdata_traces`, `rxrpc_receive_traces`, `rxrpc_recvmsg_traces`, `rxrpc_rtt_*_traces`, `rxrpc_timer_traces`, `rxrpc_propose_ack_*`, `rxrpc_ca_states`, `rxrpc_congest_changes`, packet and ACK-name tables, SACK, completion, request-ACK, txbuf, workqueue, PMTUD, RACK, and TLP tables. Major events include `rxrpc_local`, `rxrpc_peer`, `rxrpc_bundle`, `rxrpc_conn`, `rxrpc_client`, `rxrpc_call`, `rxrpc_skb`, `rxrpc_rx_packet`, `rxrpc_tx_packet`, `rxrpc_rx_ack`, `rxrpc_tx_ack`, `rxrpc_recvmsg`, `rxrpc_rtt_tx`, `rxrpc_rtt_rx`, `rxrpc_timer_*`, `rxrpc_congest`, `rxrpc_apply_acks`, `rxrpc_resend`, `rxrpc_rotate`, `rxrpc_req_ack`, `rxrpc_sack`, `rxrpc_pmtud_*`, `rxrpc_rack*`, `rxrpc_tlp_*`, and `rxrpc_rxgk_rekey`.

## Control Flow
RxRPC implementation code calls generated `trace_rxrpc_*()` helpers at lifecycle transitions and packet-processing points. Tracepoint control flow follows the protocol: endpoints and peers are referenced, client bundles and connections are allocated or reused, calls are attached, packets enter through receive paths, ACKs and DATA packets drive send-window rotation, RTT/congestion state is updated, timers are set or expire, retransmission and RACK/TLP logic marks losses, and abort/completion paths terminate calls. The header itself has no executable protocol logic, but each `TP_fast_assign` snapshots the relevant protocol fields before the formatted record reaches trace buffers.

## State and Persistence
No RxRPC protocol state is persisted by this header. State lives in the caller's RxRPC objects, socket buffers, timers, congestion structures, and security state; trace records persist only in tracing ring buffers. The enum/string mappings are compile-time trace ABI metadata and must stay consistent with values used by call sites. Dynamic fields copy packet, SACK, timing, serial, sequence, tx-window, and error information into trace records so later readers do not depend on object lifetime.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `linux/errqueue.h`, RxRPC internal types at call sites, and the kernel trace-event generator via `trace/define_trace.h`. Integrates with `net/rxrpc`, AFS over RxRPC, rxperf, RxKAD/RxGK security handling, UDP socket error reporting, congestion control, RACK/TLP loss recovery, PMTU discovery, and userspace trace tooling that consumes `events/rxrpc/*`.

## Risks
The biggest risk is trace ABI drift: renaming enum labels, changing event fields, or reordering values can break tooling that decodes RxRPC behavior. Tracepoints also dereference live protocol objects, so call sites must pass valid objects and copy variable-length data safely. Very hot packet paths can incur overhead when enabled, especially for verbose ACK, SACK, RTT, and retransmission events. The large enum tables are easy to update incompletely when adding new RxRPC states or reasons.

## Test Signals
Useful signals include building with `CREATE_TRACE_POINTS`, enabling each `events/rxrpc/*` tracepoint under AFS/rxperf traffic, packet loss and reordering tests that exercise retransmission/RACK/TLP, PMTU reduction tests, abort/security failure tests, trace-cmd/perf/BPF field decoding, and lockdep/KASAN runs while tracing hot receive and send paths.
