## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_enum.sh

Purpose: tests BTF enum augmentation in `perf trace` for syscall and tracepoint arguments.
Important functions: `check_vmlinux`, `check_permissions`, `trace_landlock`, and `trace_non_syscall`.
Control flow: requires perf trace, root, and `/sys/kernel/btf/vmlinux`; traces `landlock_add_rule` using the `landlock` perf workload when available, then traces `timer:hrtimer_start --max-events=1` and expects enum names such as `LANDLOCK_RULE_*` and `HRTIMER_MODE_*`.
State and persistence: no temp files.
Dependencies and integration: BTF vmlinux, landlock workload/syscall, timer tracepoint, perf trace enum decoding.
Risks: landlock may be absent and is skipped to non-syscall path; permissions can skip.
Test signals: augmented enum names appear in trace output.
