<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c

## Purpose

BPF implementation of DCTCP congestion-control callbacks, using socket storage and TCP helpers to validate struct_ops behavior.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `struct_ops`, `.struct_ops`, `.struct_ops`
- Maps: `sk_stg_map`
- Important functions/callbacks: `dctcp_reset`, `BPF_PROG`, `dctcp_react_to_loss`, `dctcp_ece_ack_cwr`, `dctcp_ece_ack_update`, `bpf_dctcp_init`, `bpf_dctcp_ssthresh`, `bpf_dctcp_update_alpha`, `bpf_dctcp_state`, `bpf_dctcp_cwnd_event`, `bpf_dctcp_cwnd_undo`, `bpf_dctcp_cong_avoid`
- BPF helpers/kfunc-like calls: `bpf_dctcp_init`, `bpf_getsockopt`, `bpf_setsockopt`, `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_tcp_send_ack`
- Mutable globals/test result fields: `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt`

## Control Flow and Data Flow

The kernel invokes registered `tcp_congestion_ops` struct_ops callbacks across TCP connection lifetime. The BPF code reads `struct sock`/`tcp_sock`, updates private congestion-control state or socket storage, calls TCP kfuncs/helpers, and returns cwnd/ssthresh decisions to TCP.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `sk_stg_map` Globals are used as userspace-visible configuration/results: `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt` TCP congestion-control state persists in `inet_csk_ca`, socket storage, or kernel TCP fields for the lifetime of each connection.

## Dependencies and Integration Points

Includes `bpf_tracing_net.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with BPF struct_ops `tcp_congestion_ops`, TCP kfuncs, `bpf_tracing_net.h`, and the TCP selftest harness.

## Risks and Edge Cases

Congestion-control callbacks run in TCP hot paths; incorrect cwnd math, ownership, or helper availability can affect connection behavior or verifier acceptance. Helper availability and license restrictions matter for `bpf_dctcp_init`, `bpf_getsockopt`, `bpf_setsockopt`, `bpf_sk_storage_delete`, `bpf_sk_storage_get`, `bpf_tcp_send_ack`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `cc_res[TCP_CA_NAME_MAX]`, `tcp_cdg_res`, `stg_result`, `ebusy_cnt` to confirm the exercised path ran. Map contents/counts for `sk_stg_map` provide state validation. TCP selftests should create connections using the named congestion-control ops and confirm callback counters, fallback behavior, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_dctcp.c -->
