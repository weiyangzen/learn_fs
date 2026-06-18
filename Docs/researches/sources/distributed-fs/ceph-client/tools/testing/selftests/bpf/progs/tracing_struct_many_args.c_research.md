# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct_many_args.c

## Purpose
This companion fixture stresses BTF tracing argument marshalling after many scalar and pointer arguments, where structs may move between registers and stack slots. The source is 95 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_testmod_test_struct_arg_7`, `fexit/bpf_testmod_test_struct_arg_7`, `fentry/bpf_testmod_test_struct_arg_8`, `fexit/bpf_testmod_test_struct_arg_8`, `fentry/bpf_testmod_test_struct_arg_9`, `fexit/bpf_testmod_test_struct_arg_9`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG2`, `test_struct_many_args_1`, `test_struct_many_args_2`, `test_struct_many_args_3`, `test_struct_many_args_4`, `test_struct_many_args_5`, `test_struct_many_args_6`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include `long t7_a, t7_b, t7_c, t7_d, t7_e, t7_f_a, t7_f_b, t7_ret`, `long t8_a, t8_b, t8_c, t8_d, t8_e, t8_f_a, t8_f_b, t8_g, t8_ret`, `long t9_a, t9_b, t9_c, t9_d, t9_e, t9_f, t9_g, t9_h_a, t9_h_b, t9_h_c, t9_h_d, t9_i, t9_ret`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a tracing/LSM selftest program. The attachment section is part of the contract, and global variables form the observation surface used by the C harness after the traced kernel path runs. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 6 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
