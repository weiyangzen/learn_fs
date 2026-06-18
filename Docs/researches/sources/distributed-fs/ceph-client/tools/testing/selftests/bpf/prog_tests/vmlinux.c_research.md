# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vmlinux.c

## Purpose

Smoke test that BPF programs compiled against `vmlinux.h` can attach to several tracing mechanisms and observe a nanosleep trigger. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_vmlinux__open_and_load()`, `test_vmlinux__attach()`, `syscall(__NR_nanosleep)`, and BSS flags for tracepoint, raw tracepoint, tp_btf, kprobe, and fentry handlers.

## Control Flow

Load and attach the skeleton, call `nanosleep()` with a distinctive nanosecond value, then assert each BSS flag was set by its corresponding BPF program.

## State and Persistence Behavior

Only skeleton BSS flags persist during the test; no file or kernel state is retained after skeleton destruction.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

The test depends on availability of all tracing attach mechanisms and the nanosleep path on the running kernel.

## Test Signals

All of `tp_called`, `raw_tp_called`, `tp_btf_called`, `kprobe_called`, and `fentry_called` must be true.
