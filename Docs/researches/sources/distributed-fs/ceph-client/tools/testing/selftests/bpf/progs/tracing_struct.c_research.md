# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct.c

## Purpose
This BTF tracing fixture validates struct and union arguments passed by value to fentry/fexit programs, including register extraction with `bpf_get_func_arg()` and return value capture. The source is 166 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_testmod_test_struct_arg_1`, `fexit/bpf_testmod_test_struct_arg_1`, `fentry/bpf_testmod_test_struct_arg_2`, `fexit/bpf_testmod_test_struct_arg_2`, `fentry/bpf_testmod_test_struct_arg_3`, `fexit/bpf_testmod_test_struct_arg_3`, `fentry/bpf_testmod_test_struct_arg_4`, `fexit/bpf_testmod_test_struct_arg_4`, `fentry/bpf_testmod_test_struct_arg_5`, `fexit/bpf_testmod_test_struct_arg_5`, `fentry/bpf_testmod_test_struct_arg_6`, `fexit/bpf_testmod_test_union_arg_1`, `fexit/bpf_testmod_test_union_arg_2`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG2`, `test_struct_arg_1`, `test_struct_arg_2`, `test_struct_arg_3`, `test_struct_arg_4`, `test_struct_arg_5`, `test_struct_arg_6`, `test_struct_arg_7`, `test_struct_arg_8`, `test_struct_arg_9`, `test_struct_arg_10`, `test_struct_arg_11`, `test_union_arg_1`, `test_union_arg_2`. BPF helpers and kfunc-style APIs referenced include `bpf_get_func_arg_cnt`, `bpf_get_func_arg`. Global observation/configuration variables include `long t1_a_a, t1_a_b, t1_b, t1_c, t1_ret, t1_nregs`, `__u64 t1_reg0, t1_reg1, t1_reg2, t1_reg3`, `long t2_a, t2_b_a, t2_b_b, t2_c, t2_ret`, `long t3_a, t3_b, t3_c_a, t3_c_b, t3_ret`, `long t4_a_a, t4_b, t4_c, t4_d, t4_e_a, t4_e_b, t4_ret`, `long t5_ret`, `int t6`, `long ut1_a_a, ut1_b, ut1_c`, `long ut2_a, ut2_b_a, ut2_b_b`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a tracing/LSM selftest program. The attachment section is part of the contract, and global variables form the observation surface used by the C harness after the traced kernel path runs. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 13 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
