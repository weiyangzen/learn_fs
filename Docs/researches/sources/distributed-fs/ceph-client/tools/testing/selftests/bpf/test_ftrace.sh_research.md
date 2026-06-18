# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_ftrace.sh

## Research

This shell test checks ftrace interaction needed by BPF selftests, specifically that enabling fentry tracing on `bpf_fentry_test1` is visible in the trace pipe after triggering the test module path. It also behaves as an environment gate for missing tracefs or missing kernel support.

The script locates tracefs at `/sys/kernel/tracing`, skips with exit code `4` if unavailable, and checks whether `bpf_fentry_test1` appears in `available_filter_functions`. It installs a `trap` that disables tracing, clears the trace buffer, removes the ftrace filter, and removes `bpf_testmod`. The main flow loads `bpf_testmod`, writes `bpf_fentry_test1` into `set_ftrace_filter`, enables `function` tracing, triggers the module by reading `/sys/kernel/bpf_testmod`, disables tracing, and greps `trace` for `bpf_fentry_test1`. If the symbol is absent from the trace output, it prints a failure and returns nonzero.

State side effects are all kernel/debugfs scoped: loaded module state, ftrace current tracer, function filter, trace buffer contents, and the module sysfs read trigger. Dependencies include tracefs, ftrace function tracer support, root privileges, `modprobe`, and the `bpf_testmod` module exposing the sysfs trigger.

Risks are host configuration sensitivity, symbol name changes, concurrent tracing users, and cleanup races if another test manipulates the same ftrace files. Test signals are explicit skip output for unsupported environments and a successful grep of the trace buffer after the sysfs read trigger.
