<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h

## Purpose

BPF selftest support source in the kernel selftests BPF program tree.

## Important APIs, Types, and Functions

- Important functions/callbacks: `before`, `tcp_in_slow_start`, `tcp_is_cwnd_limited`
- BPF helpers/kfunc-like calls: `bpf_jiffies64`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_jiffies64`.

## Test Signals

Load/attach success and verifier log expectations are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_tracing_net.h -->
