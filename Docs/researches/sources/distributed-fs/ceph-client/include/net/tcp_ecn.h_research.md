# sources/distributed-fs/ceph-client/include/net/tcp_ecn.h

## Purpose

`tcp_ecn.h` centralizes TCP ECN negotiation and feedback helpers, including classic RFC3168 ECN and Accurate ECN (AccECN). It is used by TCP input/output paths to decide what flags to put on SYN/SYN-ACK/data ACKs, how to validate feedback from peers and middleboxes, and how to maintain per-connection ECN counters in `struct tcp_sock`.

## Important APIs, types, and functions

The public configuration enums are `enum tcp_ecn_mode` and `enum tcp_accecn_option`. Important helpers include `tcp_ecn_send_syn()`, `tcp_ecn_rcv_syn()`, `tcp_ecn_send_synack()`, `tcp_ecn_make_synack()`, `tcp_ecn_rcv_synack()`, `tcp_ecn_rcv_ecn_echo()`, `tcp_ecn_queue_cwr()`, `tcp_ecn_accept_cwr()`, `tcp_accecn_set_ace()`, `tcp_ecn_received_counters()`, `tcp_accecn_option_init()`, `tcp_update_ecn_bytes()`, and `tcp_accecn_option_beacon_check()`. The Accurate ECN helpers encode/decode the ACE field from TCP `AE/CWR/ECE` bits and map 24-bit option counters to ECT(0), ECT(1), and CE byte counters.

## Control flow

Outbound active opens call `tcp_ecn_send_syn()` to consult `sysctl_tcp_ecn`, congestion-control requirements, BPF congestion-control ECN needs, and route ECN feature hints. If AccECN is requested, it sets `TCPHDR_AE`, enters pending mode, and records the transmitted SYN ECN codepoint. Passive opens call `tcp_ecn_rcv_syn()` to downgrade to classic ECN or accept AccECN based on the ACE bits and received IP ECN field. SYN-ACK construction uses `tcp_accecn_reflector_flags()` or classic ECE, while SYN-ACK reception selects disabled, RFC3168, or AccECN mode from the returned ACE field and fallback policy. After negotiation, receive paths call `tcp_ecn_received_counters()` to update CE packet counters, byte counters, ACK urgency, and AccECN option demand; transmit paths call `tcp_accecn_set_ace()` to reflect pending CE counts.

## State and persistence behavior

The header mutates transient connection state in `struct tcp_sock`: `ecn_flags`, `syn_ect_snt`, `syn_ect_rcv`, `received_ce`, `received_ce_pending`, `received_ecn_bytes[]`, `delivered_ecn_bytes[]`, `accecn_minlen`, `accecn_opt_demand`, `saw_accecn_opt`, `accecn_fail_mode`, timestamps, and previous ECN field tracking. It also sets ACK scheduling bits in `inet_connection_sock`. No persistent storage is owned here; state lasts for the TCP connection and is initialized/reset through helpers such as `tcp_accecn_init_counters()`.

## Dependencies and integration points

It depends on TCP core structures, SKB control blocks, `inet_ecn.h`, bitfield helpers, sysctls under `sock_net(sk)->ipv4`, congestion-control hooks, BPF congestion-control hooks, route features, and TCP option parsing. It integrates with handshake creation, SYN cookie validation (`cookie_accecn_ok()`), ACK generation, CWR handling, receive counter accounting, and option emission policy.

## Risks and test signals

Risks include invalid ACE interpretation during handshake fallback, wrong ECN transition validation after middlebox remarking, 24-bit counter wrap mistakes, off-by-one indexing into ECN byte arrays, excessive or missing ACK forcing on ECN edges, and accidentally setting CWR in AccECN mode. Tests should exercise active/passive opens for all `sysctl_tcp_ecn` modes, AccECN downgrade to RFC3168 and disabled, CE-on-SYN/SYN-ACK accounting, option zeroing detection, 24-bit counter wrap, CWR demand/withdrawal, and builds with congestion-control/BPF ECN requirements.
