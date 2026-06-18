## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_bpf_filter.sh

Purpose: validates `perf record --filter` sample filtering implemented via BPF.
Important functions: `test_bpf_filter_priv`, `test_bpf_filter_basic`, `test_bpf_filter_fail`, `test_bpf_filter_group`, `test_bpf_filter_multi`, and `test_bpf_filter_cgroup`.
Control flow: first probes privilege/support, then records filtered task-clock/page-fault samples, checks forbidden filters produce required sample-type diagnostics, validates multiple filters, and verifies cgroup filtering with `--all-cgroups`.
State and persistence: one temp perf.data file is reused and cleaned.
Dependencies and integration: needs BPF filter support, perf record/script/report, cgroup sample support, and sometimes root or setup-filter pinning.
Risks: kernel 6.2 is explicitly treated as unsupported for one IP filter path; address filters assume kernel addresses have `ffffffff` prefix.
Test signals: absence of filtered-out kernel IPs, expected `PERF_SAMPLE_*` diagnostics, task-clock period thresholds, and root cgroup 100% report.
