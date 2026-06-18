# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_testmod-events.h

## Research

This trace event header defines the tracepoints exported by `bpf_testmod`. It uses the Linux tracepoint framework pattern with `TRACE_SYSTEM bpf_testmod`, guarded declarations, and a final `trace/define_trace.h` include.

The main event is `TRACE_EVENT(bpf_testmod_test_read)`, which records current task PID, command, read offset, and length from `struct bpf_testmod_test_read_ctx`. It also declares bare tracepoints for write, nullable-argument testing, raw tracepoint null-argument testing, writable tracepoint testing, and fentry helper tracepoints `bpf_testmod_fentry_test1` and `bpf_testmod_fentry_test2`. `BPF_TESTMOD_DECLARE_TRACE` adapts to kernels with `DECLARE_TRACE_WRITABLE`, otherwise falling back to normal `DECLARE_TRACE`.

There is no independent control flow; including `CREATE_TRACE_POINTS` before this header in `bpf_testmod.c` instantiates the tracepoints. Runtime state is kernel tracepoint registration and event metadata. Dependencies include `linux/tracepoint.h`, `bpf_testmod.h`, and generated trace definitions.

Integration points are BPF raw tracepoint, tracepoint, fentry/fexit, nullable annotation, and writable tracepoint selftests. Risks are tracepoint prototype drift, writable tracepoint availability differences, and BTF/nullability annotation changes. Test signals include successful module build/load, tracepoint attach success, correct context field values, and writable tracepoint mutation behavior.
