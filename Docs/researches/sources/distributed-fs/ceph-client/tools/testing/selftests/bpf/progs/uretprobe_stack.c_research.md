# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uretprobe_stack.c

## Purpose
This stack fixture captures user stack traces at uprobe entries, uretprobe exits, recursive returns, and USDT probes for later comparison by the user-space harness. The source is 96 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe//proc/self/exe:target_1`, `uretprobe//proc/self/exe:target_1`, `uprobe//proc/self/exe:target_2`, `uprobe//proc/self/exe:target_3`, `uprobe//proc/self/exe:target_4`, `uretprobe//proc/self/exe:target_4`, `usdt//proc/self/exe:uretprobe_stack:target`. Map definitions are none visible. Important functions/subprograms are `BPF_UPROBE`, `BPF_URETPROBE`, `BPF_USDT`, `uprobe_1`, `uretprobe_1`, `uprobe_2`, `uprobe_3`, `uprobe_4`, `uretprobe_4`, `usdt_probe`. BPF helpers and kfunc-style APIs referenced include `bpf_get_stack`. Global observation/configuration variables include `__u64 entry_stack1[32], exit_stack1[32]`, `__u64 entry_stack1_recur[32], exit_stack1_recur[32]`, `__u64 entry_stack2[32]`, `__u64 entry_stack3[32]`, `__u64 entry_stack4[32], exit_stack4[32]`, `__u64 usdt_stack[32]`, `int entry1_len, exit1_len`, `int entry1_recur_len, exit1_recur_len`, `int entry2_len, exit2_len`, `int entry3_len, exit3_len`, `int entry4_len, exit4_len`, `int usdt_len`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 7 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
