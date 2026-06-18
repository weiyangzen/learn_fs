## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_summary.sh

Purpose: validates `perf trace` summary modes, including BPF and cgroup summaries.
Important function: `test_perf_trace`.
Control flow: requires perf trace and root, runs process and system-wide summary variants (`-s`, `-S`, summary-mode thread/total), then if BPF support is present runs BPF summary variants including cgroup mode. Each invocation checks for at least three summary rows matching open/read/close with percentages.
State and persistence: one temp output file is removed.
Dependencies and integration: syscall tracing, summary aggregation, optional libbpf/BPF summary support.
Risks: expected syscalls for `true` can vary by libc/kernel; system-wide mode uses `--no-bpf-summary` until BPF gate.
Test signals: count of matching summary rows equals three for each mode.
