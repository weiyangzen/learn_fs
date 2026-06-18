# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session.c

## Purpose
This uprobe.session fixture tracks wildcard function hits by function IP, uses `bpf_session_is_return()`, suppresses selected returns, and validates sleepable user memory copy. The source is 70 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.session//proc/self/exe:uprobe_multi_func_*`, `uprobe.session.s//proc/self/exe:uprobe_multi_func_*`. Map definitions are none visible. Important functions/subprograms are `uprobe_multi_check`, `uprobe`, `verify_sleepable_user_copy`, `uprobe_sleepable`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`, `bpf_get_func_ip`, `bpf_session_is_return`, `bpf_copy_from_user`, `bpf_strncmp`. Global observation/configuration variables include `__u64 uprobe_multi_func_1_addr = 0`, `__u64 uprobe_multi_func_2_addr = 0`, `__u64 uprobe_multi_func_3_addr = 0`, `__u64 uprobe_session_result[3] = {}`, `__u64 uprobe_multi_sleep_result = 0`, `int pid = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
