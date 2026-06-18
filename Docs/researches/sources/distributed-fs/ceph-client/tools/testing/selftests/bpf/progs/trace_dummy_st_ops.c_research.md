# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_dummy_st_ops.c

## Purpose
This tracing fixture attaches to a dummy struct-ops fentry point, reads a pointer argument and the pointed state with `bpf_probe_read_kernel()`, and records the observed value. The source is 21 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/test_1`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG`, `fentry_test_1`. BPF helpers and kfunc-style APIs referenced include `bpf_probe_read_kernel`. Global observation/configuration variables include `int val = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a tracing/LSM selftest program. The attachment section is part of the contract, and global variables form the observation surface used by the C harness after the traced kernel path runs. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
