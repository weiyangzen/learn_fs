<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c

## Purpose

Compact CUBIC-like TCP congestion-control struct_ops test that exercises callback registration and pacing/cwnd helper logic.

## Important APIs, Types, and Functions

- BPF sections: `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`, `license`
- Important functions/callbacks: `div64_u64`, `tcp_update_pacing_rate`, `tcp_cwnd_reduction`, `tcp_may_raise_cwnd`, `BPF_PROG`, `bpf_cubic_init`, `bpf_cubic_cwnd_event_tx_start`, `bpf_cubic_cong_control`, `bpf_cubic_recalc_ssthresh`, `bpf_cubic_state`, `bpf_cubic_acked`, `bpf_cubic_undo_cwnd`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance.

## Test Signals

Load/attach success and verifier log expectations are primary signals. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cc_cubic.c -->
