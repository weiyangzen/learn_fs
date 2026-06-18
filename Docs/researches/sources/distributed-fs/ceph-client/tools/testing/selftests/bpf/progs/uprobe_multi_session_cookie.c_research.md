# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_cookie.c

## Purpose
This session-cookie test writes a per-invocation cookie on entry and verifies the same value on the corresponding return for three target functions. The source is 47 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.session//proc/self/exe:uprobe_multi_func_1`, `uprobe.session//proc/self/exe:uprobe_multi_func_2`, `uprobe.session//proc/self/exe:uprobe_multi_func_3`. Map definitions are none visible. Important functions/subprograms are `check_cookie`, `uprobe_1`, `uprobe_2`, `uprobe_3`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`, `bpf_session_cookie`, `bpf_session_is_return`. Global observation/configuration variables include `int pid = 0`, `__u64 test_uprobe_1_result = 0`, `__u64 test_uprobe_2_result = 0`, `__u64 test_uprobe_3_result = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 3 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
