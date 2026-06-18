# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_failure.c

## Purpose
This collection declares optional fentry/fexit programs for sensitive or unsupported kernel functions, so the user-space test can verify attach-time rejection paths. The source is 32 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?fentry/bpf_spin_lock`, `?fentry/bpf_spin_unlock`, `?fentry/__rcu_read_lock`, `?fexit/do_exit`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG`, `test_spin_lock`, `test_spin_unlock`, `tracing_deny`, `fexit_noreturns`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 4 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
