<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c

## Purpose

Negative licensing fixture for TCP congestion-control struct_ops: it uses a non-GPL license to check helper/kfunc gating.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `BPF_PROG`, `nogpltcp_init`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance.

## Test Signals

Load/attach success and verifier log expectations are primary signals. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tcp_nogpl.c -->
