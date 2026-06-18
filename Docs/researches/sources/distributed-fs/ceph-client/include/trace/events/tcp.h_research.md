# sources/distributed-fs/ceph-client/include/trace/events/tcp.h

Purpose: Defines the `tcp` trace system for TCP packet loss, resets, socket lifetime, receive-window growth, retransmission, congestion state, TCP probe telemetry, MD5/AO authentication failures, and sequence-number-extension updates.

Important APIs/types/functions: Exports tracepoints including `tcp_retransmit_skb`, `tcp_send_reset`, `tcp_receive_reset`, `tcp_destroy_sock`, `tcp_rcv_space_adjust`, `tcp_rcvbuf_grow`, `tcp_retransmit_synack`, `tcp_sendmsg_locked`, `tcp_probe`, `tcp_bad_csum`, `tcp_cong_state_set`, `tcp_hash_*`, and `tcp_ao_*`. It declares reusable event classes `tcp_event_sk`, `tcp_event_skb`, `tcp_hash_event`, `tcp_ao_event`, `tcp_ao_event_sk`, and `tcp_ao_event_sne`, plus `DECLARE_TRACE(tcp_cwnd_reduction)`. It uses `DEFINE_RST_REASON` to register reset-reason enum names.

Control flow: Callers in TCP fast paths invoke generated `trace_tcp_*` helpers; TP assignment snapshots `sock`, `sk_buff`, TCP/IPv4/IPv6 tuple, ports, sequence numbers, window metrics, congestion state, reset reason, and AO key/MAC context into ring-buffer records. Conditional AO events are only compiled with `CONFIG_TCP_AO`.

State/persistence: The file owns no TCP state; it serializes volatile socket and packet fields into ftrace/perf buffers. Trace output depends on lifetime-safe dereferences of live `sock`, request-sock, and skb objects.

Dependencies/integration: Includes TCP, IPv6, socket-diagnostic, reset-reason, and net probe common helpers; consumed by kernel TCP implementation and user tooling under tracefs/perf/BPF.

Risks: Tracepoint ABI field names and enum string mappings are user-visible. Misreading IPv4/IPv6 address families, AO optional data, or reset reasons would break diagnostics or cause unsafe dereferences on hot paths.

Test signals: Build with tracing, IPv6, and TCP_AO variants; enable `tcp:*` events while running retransmit/reset/AO failure scenarios and confirm stable formatted tuples and no lockdep/KASAN issues.
