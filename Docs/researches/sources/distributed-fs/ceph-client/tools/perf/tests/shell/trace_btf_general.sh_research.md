## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_general.sh

Purpose: tests general BTF-based argument augmentation in `perf trace`.
Important functions: `check_vmlinux`, `trace_config`, `trace_test_string`, `trace_test_buffer`, `trace_test_struct_btf`, and cleanup handlers.
Control flow: creates two temp files and a private perf config, disables display decorations, traces `mv` renameat string arguments, `echo` write buffer contents, and `sleep` clock_nanosleep struct arguments with `--force-btf`.
State and persistence: temp files and temp config are removed.
Dependencies and integration: perf trace, root, BTF vmlinux, syscall tracepoints, and configurable trace formatting.
Risks: regexes depend on exact argument formatting; cleanup trap is installed before cleanup function definition but resolves at runtime in shell.
Test signals: trace output includes decoded strings, buffer content, and timespec-like struct.
