## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_bpf_metadata.sh

Purpose: verifies perf records BPF program metadata for BPF sample filters.
Important function: `test_bpf_metadata`.
Control flow: skips if `libbpf-strings` feature is unavailable, records a task-clock sample filter `ip > 0`, then parses `perf script --show-bpf-events` to find `PERF_RECORD_BPF_METADATA` for `perf_sample_filter` and a `perf_version` entry matching `perf version`.
State and persistence: temp perf.data is removed.
Dependencies and integration: BPF sample filter infrastructure, metadata strings compiled into perf BPF programs, and perf script BPF event display.
Risks: awk parser depends on current `perf script` formatting and entry indentation.
Test signals: metadata event contains current perf version string.
