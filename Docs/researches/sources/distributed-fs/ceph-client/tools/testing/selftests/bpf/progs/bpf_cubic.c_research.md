<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c

## Purpose

Large BPF CUBIC congestion-control implementation adapted from kernel TCP CUBIC for struct_ops selftests.

## Important APIs, Types, and Functions

- BPF sections: `license`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`
- Important functions/callbacks: `bictcp_reset`, `div64_u64`, `fls64`, `bictcp_clock_us`, `bictcp_hystart_reset`, `BPF_PROG`, `cubic_root`, `bictcp_update`, `hystart_ack_delay`, `hystart_update`, `bpf_cubic_init`, `bpf_cubic_cwnd_event_tx_start`, `bpf_cubic_cong_avoid`, `bpf_cubic_recalc_ssthresh`, `bpf_cubic_state`, `bpf_cubic_acked`, `bpf_cubic_undo_cwnd`
- BPF helpers/kfunc-like calls: `bpf_setsockopt`
- Mutable globals/test result fields: `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called` TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_tracing.h`, `errno.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance. Helper availability and license restrictions matter for `bpf_setsockopt`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nodelay_init_reject`, `nodelay_cwnd_event_tx_start_reject`, `bpf_cubic_acked_called` to confirm the exercised path ran. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_cubic.c -->
