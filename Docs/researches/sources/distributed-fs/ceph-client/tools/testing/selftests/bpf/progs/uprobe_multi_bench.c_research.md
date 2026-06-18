# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_bench.c

## Purpose
This benchmark fixture counts executions of a wildcard `uprobe.multi` attachment against the selftest binary for attach and trigger overhead measurement. The source is 15 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.multi/./uprobe_multi:uprobe_multi_func_*`. Map definitions are none visible. Important functions/subprograms are `uprobe_bench`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include `int count`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
