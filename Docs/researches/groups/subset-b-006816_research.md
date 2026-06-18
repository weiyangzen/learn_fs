# subset-b-006816 research

Grouped BPF selftest research. Each source section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim_reject.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim_reject.c

## Purpose
This timer test verifies map-in-map ownership rules for `struct bpf_timer`: a timer value obtained from one inner hash map is deliberately initialized against a different inner map, so callback setup and start should be rejected and surfaced through `err` bits. The source is 74 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_fentry_test1`. Map definitions are `inner_htab`, `outer_arr`. Important functions/subprograms are `timer_cb`, `BPF_PROG`, `test1`. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`. Global observation/configuration variables include `__u64 err`, `__u64 ok`, `__u64 cnt`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim_reject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_deadlock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_deadlock.c

## Purpose
This timer regression test arms the same BPF timer from an `hrtimer_start` BTF tracepoint while `bpf_timer_start()` is already in progress, exercising lock ordering that previously could deadlock. The source is 70 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `tp_btf/hrtimer_start`, `syscall`. Map definitions are `timer_map`. Important functions/subprograms are `timer_cb`, `BPF_PROG`, `start_timer`, `tp_hrtimer_start`. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_timer_start`, `bpf_timer_init`, `bpf_timer_set_callback`. Global observation/configuration variables include `volatile int in_timer_start`, `volatile int tp_called`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a tracing/LSM selftest program. The attachment section is part of the contract, and global variables form the observation surface used by the C harness after the traced kernel path runs. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_deadlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_delete_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_delete_race.c

## Purpose
This race test repeatedly starts a timer while another syscall program deletes the sole map element, relying on KASAN or runtime checks to catch callback use-after-free of the map value. The source is 66 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`. Map definitions are `timer_map`. Important functions/subprograms are `timer_cb`, `start_timer`, `delete_elem`. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_map_delete_elem`. Global observation/configuration variables include `long cb_cnt`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF timer selftest where map value lifetime, callback registration, and hrtimer integration are the important kernel interfaces. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_delete_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_kallsyms.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_kallsyms.c

## Purpose
This token/kallsyms fixture exposes an XDP entry that calls a weak subprogram symbol, letting user-space token tests validate symbol visibility and loading behavior without packet parsing. The source is 19 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `xdp`. Map definitions are none visible. Important functions/subprograms are `token_ksym_subprog`, `xdp_main`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_lsm.c

## Purpose
This LSM fixture hooks `bpf_token_capable` and `bpf_token_cmd` and gates rejection by PID plus global flags, providing controllable policy denial for BPF token selftests. The source is 32 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `lsm/bpf_token_capable`, `lsm/bpf_token_cmd`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG`, `token_capable`, `token_cmd`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`. Global observation/configuration variables include `int my_pid`, `int reject_capable`, `int reject_cmd`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a tracing/LSM selftest program. The attachment section is part of the contract, and global variables form the observation surface used by the C harness after the traced kernel path runs. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/token_lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_dummy_st_ops.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_dummy_st_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_printk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_printk.c

## Purpose
This program tests `bpf_trace_printk()` return behavior for normal ASCII, UTF-8 format strings, and an invalid non-ASCII format specifier attached to `sys_nanosleep` fentry. The source is 32 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are none visible. Map definitions are none visible. Important functions/subprograms are `sys_enter`. BPF helpers and kfunc-style APIs referenced include `bpf_trace_printk`. Global observation/configuration variables include `int trace_printk_ret = 0`, `int trace_printk_ran = 0`, `int trace_printk_invalid_spec_ret = 0`, `int trace_printk_utf8_ret = 0`, `int trace_printk_utf8_ran = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 0 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_vprintk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_vprintk.c

## Purpose
This program tests `__bpf_vprintk()` formatting with many arguments, basic `bpf_printk()`, and the error path for `bpf_trace_vprintk()` with NULL data. The source is 34 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are none visible. Map definitions are none visible. Important functions/subprograms are `sys_enter`. BPF helpers and kfunc-style APIs referenced include `bpf_printk`, `bpf_trace_vprintk`. Global observation/configuration variables include `int null_data_vprintk_ret = 0`, `int trace_vprintk_ret = 0`, `int trace_vprintk_ran = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 0 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trace_vprintk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_failure.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct_many_args.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tracing_struct_many_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trigger_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trigger_bench.c

## Purpose
This benchmark program supplies comparable handlers for uprobe, kprobe, fentry/fexit, tracepoint, raw tracepoint, fmod_ret, USDT, and multi-attach paths, optionally collecting user/kernel stack traces. The source is 190 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?uprobe`, `?uprobe.multi`, `?raw_tp`, `?kprobe/bpf_get_numa_node_id`, `?kretprobe/bpf_get_numa_node_id`, `?kprobe.multi/bpf_get_numa_node_id`, `?kretprobe.multi/bpf_get_numa_node_id`, `?fentry/bpf_get_numa_node_id`, `?fexit/bpf_get_numa_node_id`, `?fmod_ret/bpf_modify_return_test_tp`, `?tp/bpf_test_run/bpf_trigger_tp`, `?raw_tp/bpf_trigger_tp`, `?usdt`. Map definitions are `stack_heap`. Important functions/subprograms are `inc_counter`, `do_stacktrace`, `handle`, `bench_trigger_uprobe`, `bench_trigger_uprobe_multi`, `trigger_kernel_count`, `trigger_driver`, `trigger_driver_kfunc`, `bench_trigger_kprobe`, `bench_trigger_kretprobe`, `bench_trigger_kprobe_multi`, `bench_kprobe_multi_empty`, `bench_trigger_kretprobe_multi`, `bench_kretprobe_multi_empty`, `bench_trigger_fentry`, `bench_trigger_fexit`, `bench_trigger_fmodret`, `bench_trigger_tp`, plus 2 more. BPF helpers and kfunc-style APIs referenced include `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_get_stack`, `bpf_get_numa_node_id`, `bpf_modify_return_test_tp`. Global observation/configuration variables include `volatile const int stacktrace`, `const volatile int batch_iters = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 17 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/trigger_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/twfw.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/twfw.c

## Purpose
This cgroup skb verifier regression models a tiered firewall lookup where a bounded `seqnum < 64` must prove that `seqnum / 64` indexes the one-word mask safely. The source is 58 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `cgroup_skb/ingress`. Map definitions are none visible. Important functions/subprograms are `twfw_verifier`. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a cgroup hook selftest. Return values and context access rules are observable through socket or skb operations driven by the user-space harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/twfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/type_cast.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/type_cast.c

## Purpose
This kfunc/CO-RE fixture exercises `bpf_cast_to_kern_ctx()` and `bpf_core_cast()` from XDP, TC, BTF tracepoint, and raw tracepoint contexts to validate trusted-kernel-context typing. The source is 79 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?xdp`, `?tc`, `?tp_btf/sys_enter`, `?tracepoint/syscalls/sys_enter_nanosleep`. Map definitions are `enter_id`. Important functions/subprograms are `md_xdp`, `md_skb`, `BPF_PROG`, `kctx_u64`, `untrusted_ptr`. BPF helpers and kfunc-style APIs referenced include `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_get_current_task_btf`, `bpf_task_storage_get`. Global observation/configuration variables include `int ifindex, ingress_ifindex`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/type_cast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/udp_limit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/udp_limit.c

## Purpose
This cgroup socket program limits concurrently accepted UDP socket creations, tags sockets with sk_storage, and confirms release hooks are not called for rejected create operations. The source is 59 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `cgroup/sock_create`, `cgroup/sock_release`. Map definitions are `sk_map`. Important functions/subprograms are `sock`, `sock_release`. BPF helpers and kfunc-style APIs referenced include `bpf_sk_storage_get`. Global observation/configuration variables include `int invocations = 0, in_use = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a cgroup hook selftest. Return values and context access rules are observable through socket or skb operations driven by the user-space harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/udp_limit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uninit_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uninit_stack.c

## Purpose
This verifier fixture reads fixed and variable stack slots before initialization and passes uninitialized stack memory to a helper to verify stack-state diagnostics and `STACK_MISC` marking. The source is 89 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are `dummy`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 3 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present. Expected verifier diagnostics include `fp-104=mmmmmmmm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uninit_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/unsupported_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/unsupported_ops.c

## Purpose
This struct_ops verifier test wires a BPF program into an unsupported member of `bpf_testmod_ops`, expecting load-time rejection of that member. The source is 22 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `struct_ops/unsupported_ops`. Map definitions are none visible. Important functions/subprograms are `BPF_PROG`, `unsupported_ops`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present. Expected verifier diagnostics include `attach to unsupported member unsupported_ops of struct bpf_testmod_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/unsupported_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/update_map_in_htab.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/update_map_in_htab.c

## Purpose
This map-definition fixture declares hash-of-maps variants with and without preallocation so user-space can test updating inner-map entries in both outer hash modes. The source is 30 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are none visible. Map definitions are `inner_map`, `outer_htab_map`, `outer_alloc_htab_map`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 0 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/update_map_in_htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi.c

## Purpose
This comprehensive uprobe.multi fixture records function-IP and attach-cookie matches for entry and return probes, sleepable user-copy behavior, PID filtering, and USDT PID filtering. The source is 143 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.multi//proc/self/exe:uprobe_multi_func_*`, `uretprobe.multi//proc/self/exe:uprobe_multi_func_*`, `uprobe.multi.s//proc/self/exe:uprobe_multi_func_*`, `uretprobe.multi.s//proc/self/exe:uprobe_multi_func_*`, `usdt`. Map definitions are none visible. Important functions/subprograms are `verify_sleepable_user_copy`, `uprobe_multi_check`, `uprobe`, `uretprobe`, `uprobe_sleep`, `uretprobe_sleep`, `uprobe_extra`, `usdt_pid`, `usdt_extra`. BPF helpers and kfunc-style APIs referenced include `bpf_copy_from_user`, `bpf_strncmp`, `bpf_get_current_pid_tgid`, `bpf_get_attach_cookie`, `bpf_get_func_ip`. Global observation/configuration variables include `__u64 uprobe_multi_func_1_addr = 0`, `__u64 uprobe_multi_func_2_addr = 0`, `__u64 uprobe_multi_func_3_addr = 0`, `__u64 uprobe_multi_func_1_result = 0`, `__u64 uprobe_multi_func_2_result = 0`, `__u64 uprobe_multi_func_3_result = 0`, `__u64 uretprobe_multi_func_1_result = 0`, `__u64 uretprobe_multi_func_2_result = 0`, `__u64 uretprobe_multi_func_3_result = 0`, `__u64 uprobe_multi_sleep_result = 0`, `int pid = 0`, `int child_pid = 0`, plus 7 more.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_bench.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_consumers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_consumers.c

## Purpose
This fixture attaches multiple consumers to normal uprobe.multi and session uprobe paths and records which consumers ran, including a session handler that suppresses return probing. The source is 39 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.multi`, `uprobe.session`. Map definitions are none visible. Important functions/subprograms are `uprobe_0`, `uprobe_1`, `uprobe_2`, `uprobe_3`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include `__u64 uprobe_result[4]`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 4 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_consumers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_pid_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_pid_filter.c

## Purpose
This program backs PID-filter tests by maintaining per-probe hit/miss counters for three expected PIDs. The source is 40 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.multi`. Map definitions are none visible. Important functions/subprograms are `update_pid`, `uprobe_multi_0`, `uprobe_multi_1`, `uprobe_multi_2`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`. Global observation/configuration variables include `__u32 pids[3]`, `__u32 test[3][2]`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_pid_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_cookie.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_recursive.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_recursive.c

## Purpose
This recursive session test stores entry cookies and checks return cookies across nested calls, using return values to decide which invocations get return probes. The source is 43 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.session//proc/self/exe:uprobe_session_recursive`. Map definitions are none visible. Important functions/subprograms are `check_cookie`, `uprobe_recursive`. BPF helpers and kfunc-style APIs referenced include `bpf_session_cookie`, `bpf_session_is_return`, `bpf_get_current_pid_tgid`. Global observation/configuration variables include `int pid = 0`, `int idx_entry = 0`, `int idx_return = 0`, `__u64 test_uprobe_cookie_entry[6]`, `__u64 test_uprobe_cookie_return[3]`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_recursive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_single.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_single.c

## Purpose
This single-symbol session test attaches three consumers to one function and verifies only the selected consumer allows the return-side session. The source is 44 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.session//proc/self/exe:uprobe_multi_func_1`. Map definitions are none visible. Important functions/subprograms are `uprobe_multi_check`, `uprobe_0`, `uprobe_1`, `uprobe_2`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`. Global observation/configuration variables include `__u64 uprobe_session_result[3] = {}`, `int pid = 0`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_session_single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_usdt.c

## Purpose
This minimal USDT fixture increments a counter on each probe hit and is used to validate multi-uprobe USDT attachment plumbing. The source is 16 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `usdt`. Map definitions are none visible. Important functions/subprograms are `usdt0`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include `int count`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_usdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_verifier.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_verifier.c

## Purpose
This verifier test checks the legal return-value range for `uprobe.session` programs: 0 and 1 are accepted, while 2 is rejected. The source is 31 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe.session`. Map definitions are none visible. Important functions/subprograms are `uprobe_sesison_return_0`, `uprobe_sesison_return_1`, `uprobe_sesison_return_2`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 3 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present. Expected verifier diagnostics include `At program exit the register R0 has smin=2 smax=2 should have been in [0, 1]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_multi_verifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall.c

## Purpose
This uprobe fixture copies the incoming `pt_regs` into global storage, letting user-space compare the register snapshot for syscall-oriented probe paths. The source is 15 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe`. Map definitions are none visible. Important functions/subprograms are `probe`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include `struct pt_regs regs`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall_executed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall_executed.c

## Purpose
This execution fixture increments one shared counter from uprobe, uretprobe, multi-uprobe, multi-uretprobe, session uprobe, and USDT handlers after PID filtering. The source is 73 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `uprobe`, `uretprobe`, `uprobe.multi`, `uretprobe.multi`, `uprobe.session`, `usdt`. Map definitions are none visible. Important functions/subprograms are `BPF_UPROBE`, `BPF_URETPROBE`, `test_uprobe_multi`, `test_uretprobe_multi`, `test_uprobe_session`, `test_usdt`, `test_uprobe`, `test_uretprobe`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`. Global observation/configuration variables include `struct pt_regs regs`, `int executed = 0`, `int pid`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It integrates with the user-space uprobe/USDT selftest harness. User space sets globals such as PIDs, target addresses, cookies, or expected counters, attaches the declared sections to functions in `/proc/self/exe`, triggers the target functions, and reads globals back from the BPF object. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 6 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uprobe_syscall_executed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_failure.c

## Purpose
This uptr verifier file asserts that user-pointer fields in task storage cannot be overwritten, used as kptrs, dereferenced without NULL checks, or trusted after object allocation. The source is 105 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?syscall`. Map definitions are `datamap`. Important functions/subprograms are `uptr_write`, `uptr_write_nested`, `uptr_no_null_check`, `uptr_kptr_xchg`, `uptr_obj_new`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_task_btf`, `bpf_task_storage_get`, `bpf_kptr_xchg`, `bpf_obj_new`, `bpf_obj_drop`. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 5 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present. Expected verifier diagnostics include `store to uptr disallowed`, `R1 invalid mem access 'mem_or_null'`, `doesn't point to kptr`, `invalid mem access 'scalar'`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_map_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_map_failure.c

## Purpose
This map-definition fixture declares task-storage value types with unsupported or malformed uptr layouts so map creation/loading tests can reject them. The source is 27 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are none visible. Map definitions are `large_uptr_map`, `empty_uptr_map`, `kstruct_uptr_map`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 0 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_map_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_update_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_update_failure.c

## Purpose
This load-only task-storage program reads a user pointer under a spin lock and updates a user struct field, covering accepted uptr use with locking and NULL checks. The source is 42 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`. Map definitions are `datamap`. Important functions/subprograms are `not_used`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_task_btf`, `bpf_task_storage_get`, `bpf_spin_lock`, `bpf_spin_unlock`. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 1 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uptr_update_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uretprobe_stack.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/uretprobe_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_fail.c

## Purpose
This verifier suite intentionally misuses user-ringbuf callback dynptrs, context pointers, release helpers, return values, and reinitialization to assert precise rejection messages. The source is 245 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?raw_tp`. Map definitions are `user_ringbuf`, `ringbuf`. Important functions/subprograms are `bad_access1`, `user_ringbuf_callback_bad_access1`, `bad_access2`, `user_ringbuf_callback_bad_access2`, `write_forbidden`, `user_ringbuf_callback_write_forbidden`, `null_context_write`, `user_ringbuf_callback_null_context_write`, `null_context_read`, `user_ringbuf_callback_null_context_read`, `try_discard_dynptr`, `user_ringbuf_callback_discard_dynptr`, `try_submit_dynptr`, `user_ringbuf_callback_submit_dynptr`, `invalid_drain_callback_return`, `user_ringbuf_callback_invalid_return`, `try_reinit_dynptr_mem`, `try_reinit_dynptr_ringbuf`, plus 5 more. BPF helpers and kfunc-style APIs referenced include `bpf_dynptr_data`, `bpf_printk`, `bpf_user_ringbuf_drain`, `bpf_ringbuf_discard_dynptr`, `bpf_ringbuf_submit_dynptr`, `bpf_dynptr_from_mem`, `bpf_ringbuf_reserve_dynptr`. Global observation/configuration variables include none visible.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 11 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present. Expected verifier diagnostics include `negative offset dynptr_ptr ptr`, `dereference of modified dynptr_ptr ptr`, `invalid mem access 'dynptr_ptr'`, `invalid mem access 'scalar'`, `cannot release unowned const bpf_dynptr`, `At callback return the register R0 has `, `Dynptr has to be an uninitialized dynptr`, `dereference of modified dynptr_ptr ptr R1 off=16384 disallowed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_success.c

## Purpose
This success suite drains a user ring buffer through dynptr reads and direct data access, runs a bidirectional protocol with a kernel ring buffer, and validates epoll-visible drain behavior. The source is 212 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are none visible. Map definitions are `user_ringbuf`, `kernel_ringbuf`. Important functions/subprograms are `is_test_process`, `record_sample`, `handle_sample_msg`, `read_protocol_msg`, `publish_next_kern_msg`, `publish_kern_messages`, `test_user_ringbuf_protocol`, `test_user_ringbuf`, `do_nothing_cb`, `test_user_ringbuf_epoll`. BPF helpers and kfunc-style APIs referenced include `bpf_get_current_pid_tgid`, `bpf_dynptr_read`, `bpf_printk`, `bpf_dynptr_data`, `bpf_ringbuf_reserve`, `bpf_ringbuf_discard`, `bpf_ringbuf_submit`, `bpf_loop`, `bpf_user_ringbuf_drain`. Global observation/configuration variables include `int pid, err, val`, `int read = 0`, `__u64 kern_mutated = 0`, `__u64 user_mutated = 0`, `__u64 expected_user_mutated = 0`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 0 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/user_ringbuf_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_align.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_align.c

## Purpose
This verifier suite focuses on scalar alignment and tnum propagation, packet pointer arithmetic, variable offsets, subtraction, multiplication, and rejection of impossible packet offsets. The source is 581 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `tc`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 11 success markers and 1 failure markers across 12 loadable sections. Expected verifier diagnostics include `0: R1=ctx() R10=fp0`, `0: {{.*}} R3=2`, `1: {{.*}} R3=4`, `2: {{.*}} R3=8`, `3: {{.*}} R3=16`, `4: {{.*}} R3=32`, `0: {{.*}}R3=1`, `1: {{.*}}R3=2`, plus 84 more.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_align.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_and.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_and.c

## Purpose
This verifier suite covers bitwise AND range tracking for negative values, invalid range checks, and preservation of known subregister information. The source is 113 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are `map_hash_48b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 2 success markers and 4 failure markers across 3 loadable sections. Test descriptions include `invalid and of negative number`, `invalid range check`, `check known subreg with unknown reg`. Expected verifier diagnostics include `R0 max value is outside of the allowed memory range`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_and.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena.c

## Purpose
This arena suite exercises `BPF_MAP_TYPE_ARENA`, arena globals, pointer casts, iterator contexts, aliasing, direct stores, and trusted/untrusted arena pointer checks. The source is 610 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`, `syscall`, `iter.s/bpf_map`. Map definitions are `arena`. Important functions/subprograms are `basic_alloc1_nosleep`, `basic_alloc1`, `basic_alloc2_nosleep`, `basic_alloc2`, `basic_alloc3_nosleep`, `basic_alloc3`, `basic_reserve1_nosleep`, `basic_reserve1`, `basic_reserve2_nosleep`, `basic_reserve2`, `reserve_twice_nosleep`, `reserve_twice`, `reserve_invalid_region_nosleep`, `reserve_invalid_region`, `iter_maps1`, `iter_maps2`, `iter_maps3`, `arena_kfuncs_under_bpf_lock`, plus 5 more. BPF helpers and kfunc-style APIs referenced include `bpf_arena_alloc_pages`, `bpf_arena_free_pages`, `bpf_arena_reserve_pages`, `bpf_spin_lock`, `bpf_spin_unlock`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 21 success markers and 2 failure markers across 23 loadable sections. Expected verifier diagnostics include `expected pointer to STRUCT bpf_map`, `untrusted_ptr_bpf_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals1.c

## Purpose
This arena-globals file validates generated arena-backed global data access and initialization across syscall programs. The source is 87 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`. Map definitions are `arena`. Important functions/subprograms are `check_reserve1`, `check_relocation`. BPF helpers and kfunc-style APIs referenced include `bpf_arena_reserve_pages`. Global observation/configuration variables include `volatile char __arena global_data[GLOBAL_PAGES][PAGE_SIZE]`.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 2 success markers and 0 failure markers across 2 loadable sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals2.c

## Purpose
This companion arena-globals file covers a second global layout so skeleton/linking tests can validate multiple arena global objects. The source is 49 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`. Map definitions are `arena`. Important functions/subprograms are `check_reserve2`. BPF helpers and kfunc-style APIs referenced include `bpf_arena_reserve_pages`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 1 success markers and 0 failure markers across 1 loadable sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_globals2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_large.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_large.c

## Purpose
This large-arena suite stresses arena allocation and access patterns over large offsets and object sizes, including socket and syscall program contexts. The source is 316 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`, `socket`. Map definitions are `arena`. Important functions/subprograms are `big_alloc1`, `access_reserved`, `request_partially_reserved`, `free_reserved`, `alloc_pages`, `big_alloc2`, `big_alloc3`. BPF helpers and kfunc-style APIs referenced include `bpf_arena_alloc_pages`, `bpf_arena_free_pages`, `bpf_arena_reserve_pages`, `bpf_for`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 6 success markers and 0 failure markers across 6 loadable sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_arena_large.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_array_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_array_access.c

## Purpose
This array-map verifier suite covers constant, register, variable, signed, read-only, write-only, per-CPU, elided lookup, and stack-key access paths for array values. The source is 731 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`, `tc`. Map definitions are `map_array_ro`, `map_array_wo`, `map_array_pcpu`, `map_array`, `map_hash_48b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_probe_read_user`, `bpf_get_prandom_u32`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 15 success markers and 28 failure markers across 29 loadable sections. Test descriptions include `valid map access into an array with a constant`, `valid map access into an array with a register`, `valid map access into an array with a variable`, `valid map access into an array with a signed variable`, `invalid map access into an array with a constant`, `invalid map access into an array with a register`, `invalid map access into an array with a variable`, `invalid map access into an array with no floor check`, `invalid map access into an array with a invalid max check`, `valid read map access into a read-only array 1`, plus 17 more. Expected verifier diagnostics include `R0 leaks addr`, `invalid access to map value, value_size=48 off=48 size=8`, `R0 min value is outside of the allowed memory range`, `R0 unbounded memory access, make sure to bounds check any such access`, `R0 unbounded memory access`, `invalid access to map value, value_size=48 off=44 size=8`, `R0 pointer += pointer`, `write into map forbidden`, plus 5 more.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_array_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_async_cb_context.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_async_cb_context.c

## Purpose
This async-callback suite checks context inheritance for timer, workqueue, and task-work callbacks, especially sleepable helper availability in non-sleepable and sleepable roots. The source is 181 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_fentry_test1`, `lsm.s/file_open`. Map definitions are `timer_map`, `wq_map`, `task_work_map`. Important functions/subprograms are `timer_cb`, `timer_non_sleepable_prog`, `timer_sleepable_prog`, `wq_cb`, `wq_non_sleepable_prog`, `wq_sleepable_prog`, `task_work_cb`, `task_work_non_sleepable_prog`, `task_work_sleepable_prog`. BPF helpers and kfunc-style APIs referenced include `bpf_copy_from_user`, `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_get_current_task_btf`, `bpf_task_work_schedule_resume`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 4 success markers and 2 failure markers across 6 loadable sections. Expected verifier diagnostics include `sleepable helper bpf_copy_from_user#{{[0-9]+}} in non-sleepable prog`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_async_cb_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_basic_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_basic_stack.c

## Purpose
This stack suite validates stack bounds, uninitialized stack behavior for privileged/unprivileged loads, frame-pointer arithmetic, and misalignment rejection. The source is 100 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are `map_hash_8b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 4 success markers and 8 failure markers across 6 loadable sections. Test descriptions include `stack out of bounds`, `uninitialized stack1`, `uninitialized stack2`, `invalid fp arithmetic`, `non-invalid fp arithmetic`, `misaligned read from stack`. Expected verifier diagnostics include `invalid write to stack`, `stack depth 8`, `invalid read from stack`, `R1 subtraction from stack pointer`, `misaligned stack access`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_basic_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bitfield_write.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bitfield_write.c

## Purpose
This CO-RE suite writes and reads kernel-style bitfields to verify single, multiple, adjacent, and multibyte bitfield roundtrips. The source is 100 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `tc`. Map definitions are none visible. Important functions/subprograms are `single_field_roundtrip`, `multiple_field_roundtrip`, `adjacent_field_roundtrip`, `multibyte_field_roundtrip`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 4 success markers and 0 failure markers across 4 loadable sections. Test descriptions include `single CO-RE bitfield roundtrip`, `multiple CO-RE bitfield roundtrip`, `adjacent CO-RE bitfield roundtrip`, `multibyte CO-RE bitfield roundtrip`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bitfield_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bits_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bits_iter.c

## Purpose
This bits-iterator suite validates `bpf_iter_bits_*` lifetime, initialization, destroy requirements, word counts, NULL input, and copied bit masks. The source is 232 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `iter.s/cgroup`, `iter/cgroup`, `syscall`. Map definitions are none visible. Important functions/subprograms are `bpf_iter_bits_new`, `bpf_iter_bits_destroy`, `BPF_PROG`, `null_pointer`, `bits_copy`, `bits_memalloc`, `bit_index`, `bits_too_big`, `fewer_words`, `zero_words`, `huge_words`, `max_words`, `bad_words`, `no_destroy`, `next_uninit`, `destroy_uninit`. BPF helpers and kfunc-style APIs referenced include `bpf_iter_bits_new`, `bpf_iter_bits_next`, `bpf_iter_bits_destroy`, `bpf_for_each`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 10 success markers and 3 failure markers across 13 loadable sections. Test descriptions include `bits iter without destroy`, `uninitialized iter in ->next()`, `uninitialized iter in ->destroy()`, `null pointer`, `bits copy`, `bits memalloc`, `bit index`, `bits too big`, `fewer words`, `zero words`, plus 3 more. Expected verifier diagnostics include `Unreleased reference`, `expected an initialized iter_bits as arg #0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bits_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds.c

## Purpose
This large bounds suite covers pointer and scalar range deduction through arithmetic, truncation, shifts, sign extension, signed/unsigned comparisons, overflow, and verifier log precision. The source is 2187 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`, `tc`, `xdp`. Map definitions are `map_hash_8b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 68 success markers and 34 failure markers across 79 loadable sections. Test descriptions include `subtraction bounds (map value) variant 1`, `subtraction bounds (map value) variant 2`, `check subtraction on pointers for unpriv`, `bounds check based on zero-extended MOV`, `bounds check based on sign-extended MOV. test1`, `bounds check based on sign-extended MOV. test2`, `bounds check based on reg_off + var_off + insn_off. test1`, `bounds check based on reg_off + var_off + insn_off. test2`, `bounds check after truncation of non-boundary-crossing range`, `bounds check after truncation of boundary-crossing range (1)`, plus 67 more. Expected verifier diagnostics include `R0 max value is outside of the allowed memory range`, `R0 min value is negative, either use unsigned index or do a if (index >=0) check.`, `R1 has unknown scalar with mixed signed bounds`, `R9 pointer -= pointer prohibited`, `map_value pointer and 4294967295`, `R0 min value is outside of the allowed memory range`, `map_value pointer offset 1073741822 is not allowed`, `value 1073741823`, plus 41 more.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction.c

## Purpose
This file checks deduction from constants against context and pointer arithmetic, including accepted branches and rejected pointer/scalar subtraction cases. The source is 174 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 2 success markers and 11 failure markers across 10 loadable sections. Test descriptions include `check deducing bounds from const, 1`, `check deducing bounds from const, 2`, `check deducing bounds from const, 3`, `check deducing bounds from const, 4`, `check deducing bounds from const, 5`, `check deducing bounds from const, 6`, `check deducing bounds from const, 7`, `check deducing bounds from const, 8`, `check deducing bounds from const, 9`, `check deducing bounds from const, 10`. Expected verifier diagnostics include `R0 tried to subtract pointer from scalar`, `R1 has pointer with unsupported alu operation`, `R6 has pointer with unsupported alu operation`, `dereference of modified ctx ptr`, `negative offset ctx ptr R1 off=-1 disallowed`, `math between ctx pointer and register with unbounded min value is not allowed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction_non_const.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction_non_const.c

## Purpose
This file enumerates non-constant jump comparisons for 64-bit and 32-bit equality, inequality, unsigned, and signed relations, expecting successful verifier deduction. The source is 639 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 30 success markers and 0 failure markers across 30 loadable sections. Test descriptions include `check deducing bounds from non-const, jmp64, <non_const> == <const>, 1`, `check deducing bounds from non-const, jmp64, <non_const> == <const>, 2`, `check deducing bounds from non-const, jmp64, <non_const> != <const>, 1`, `check deducing bounds from non-const, jmp64, <non_const> != <const>, 2`, `check deducing bounds from non-const, jmp32, <non_const> == <const>, 1`, `check deducing bounds from non-const, jmp32, <non_const> == <const>, 2`, `check deducing bounds from non-const, jmp32, <non_const> != <const>, 1`, `check deducing bounds from non-const, jmp32, <non_const> != <const>, 2`, `check deducing bounds from non-const, jmp64, <const> > <non_const>, 1`, `check deducing bounds from non-const, jmp64, <const> > <non_const>, 2`, plus 20 more.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_deduction_non_const.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_mix_sign_unsign.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_mix_sign_unsign.c

## Purpose
This suite stresses mixed signed/unsigned bounds checks, documenting which branch patterns still leave unbounded negative minima and which prove safe access. The source is 554 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are `map_hash_8b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 6 success markers and 26 failure markers across 16 loadable sections. Test descriptions include `bounds checks mixing signed and unsigned, positive bounds`, `bounds checks mixing signed and unsigned`, `bounds checks mixing signed and unsigned, variant 2`, `bounds checks mixing signed and unsigned, variant 3`, `bounds checks mixing signed and unsigned, variant 4`, `bounds checks mixing signed and unsigned, variant 5`, `bounds checks mixing signed and unsigned, variant 6`, `bounds checks mixing signed and unsigned, variant 7`, `bounds checks mixing signed and unsigned, variant 8`, `bounds checks mixing signed and unsigned, variant 9`, plus 6 more. Expected verifier diagnostics include `unbounded min value`, `R4 min value is negative, either use unsigned`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bounds_mix_sign_unsign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_fastcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_fastcall.c

## Purpose
This architecture-sensitive suite validates BPF fastcall translation, stack-depth accounting, subprogram register invalidation, helper interactions, bpf_loop interactions, and kfunc cast handling. The source is 888 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `raw_tp`, `cgroup/getsockname_unix`. Map definitions are none visible. Important functions/subprograms are `kfunc_bpf_rdonly_cast`, `kfunc_root`. BPF helpers and kfunc-style APIs referenced include `bpf_loop_interaction1`, `bpf_loop_interaction2`, `bpf_core_type_id_kernel`, `bpf_cast_to_kern_ctx`, `bpf_rdonly_cast`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 28 success markers and 0 failure markers across 29 loadable sections. Expected verifier diagnostics include `stack depth 8`, `stack depth 16`, `stack depth 24`, `stack depth 32+0`, `stack depth 40+0`, `stack depth 512+0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_fastcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_get_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_get_stack.c

## Purpose
This suite validates that `bpf_get_stack()` and `bpf_get_task_stack()` return values are range-refined before use as map value offsets. The source is 124 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `tracepoint`, `iter/task`. Map definitions are `map_array_48b`, `map_hash_48b`. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 2 success markers and 0 failure markers across 2 loadable sections. Test descriptions include `bpf_get_stack return R0 within range`, `bpf_get_task_stack return R0 range is refined`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_get_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_trap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_trap.c

## Purpose
This trap suite ensures reachable compiler traps and `__bpf_trap()` calls fail verification while dead trap code is accepted. The source is 71 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are `bpf_builtin_trap_with_simple_c`, `bpf_trap_with_simple_c`. BPF helpers and kfunc-style APIs referenced include `bpf_builtin_trap_with_simple_c`, `bpf_trap_with_simple_c`, `bpf_trap_at_func_end`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 1 success markers and 4 failure markers across 5 loadable sections. Test descriptions include `__builtin_trap with simple c code`, `__bpf_trap with simple c code`, `__bpf_trap as the second-from-last insn`, `dead code __bpf_trap in the middle of code`, `reachable __bpf_trap in the middle of code`. Expected verifier diagnostics include `unexpected __bpf_trap() due to uninitialized variable?`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bpf_trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bswap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bswap.c

## Purpose
This byte-swap suite covers 16/32/64-bit endian conversions, CPU v4 ALU32 translation effects on register bounds, and reg-id reset after bswap. The source is 128 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are `dummy_test`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 8 success markers and 1 failure markers across 6 loadable sections. Test descriptions include `BSWAP, 16`, `BSWAP, 32`, `BSWAP, 64`, `BSWAP, reset reg id`, `cpuv4 is not supported by compiler or jit, use a dummy test`. Expected verifier diagnostics include `math between fp pointer and register with unbounded min value is not allowed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_bswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_ctx_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_ctx_access.c

## Purpose
This BTF context access suite accepts full-width pointer argument reads and rejects too-small reads for pointer arguments in fentry contexts. The source is 80 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_modify_return_test`, `fentry/bpf_fentry_test9`, `fentry/bpf_fentry_test10`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 3 success markers and 3 failure markers across 6 loadable sections. Test descriptions include `btf_ctx_access accept`, `btf_ctx_access u32 pointer accept`, `btf_ctx_access u32 pointer reject u32`, `btf_ctx_access u32 pointer reject u16`, `btf_ctx_access u32 pointer reject u8`, `btf_ctx_access const void pointer accept`. Expected verifier diagnostics include `size 4 must be 8`, `size 2 must be 8`, `size 1 must be 8`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_ctx_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_unreliable_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_unreliable_prog.c

## Purpose
This kprobe verifier fixture exercises log output for programs with unreliable BTF context typing while still loading successfully. The source is 20 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `kprobe`. Map definitions are none visible. Important functions/subprograms are `btf_unreliable_kprobe`. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 1 success markers and 0 failure markers across 1 loadable sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_btf_unreliable_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cfg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cfg.c

## Purpose
This control-flow suite covers unreachable instructions, out-of-range jumps, static back edges, verifier loop detection, and one accepted bounded conditional loop. The source is 162 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `socket`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 1 success markers and 15 failure markers across 10 loadable sections. Test descriptions include `unreachable`, `unreachable2`, `out of range jump`, `out of range jump2`, `loop (back-edge)`, `loop2 (back-edge)`, `conditional loop`, `conditional loop (2)`, `unconditional loop after conditional jump`. Expected verifier diagnostics include `unreachable`, `jump out of range`, `unreachable insn 1`, `back-edge`, `unreachable insn 4`, `infinite loop detected`, `back-edge from insn 10 to 11`, `back-edge from insn 3 to 2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_inv_retcode.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_inv_retcode.c

## Purpose
This cgroup socket return-code suite verifies that the final `R0` value is constrained to the accepted [0, 1] range. The source is 89 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `cgroup/sock`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 2 success markers and 5 failure markers across 7 loadable sections. Test descriptions include `bpf_exit with invalid return code. test1`, `bpf_exit with invalid return code. test2`, `bpf_exit with invalid return code. test3`, `bpf_exit with invalid return code. test4`, `bpf_exit with invalid return code. test5`, `bpf_exit with invalid return code. test6`, `bpf_exit with invalid return code. test7`. Expected verifier diagnostics include `smin=0 smax=4294967295 should have been in [0, 1]`, `smin=0 smax=3 should have been in [0, 1]`, `smin=2 smax=2 should have been in [0, 1]`, `R0 is not a known value (ctx)`, `R0 has unknown scalar value should have been in [0, 1]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_inv_retcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_skb.c

## Purpose
This cgroup skb suite validates direct packet reads, permitted return codes, and rejected context-field accesses or writes for `BPF_PROG_TYPE_CGROUP_SKB`. The source is 227 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `cgroup/skb`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 10 success markers and 10 failure markers across 10 loadable sections. Test descriptions include `direct packet read test#1 for CGROUP_SKB`, `direct packet read test#2 for CGROUP_SKB`, `direct packet read test#3 for CGROUP_SKB`, `direct packet read test#4 for CGROUP_SKB`, `invalid access of tc_classid for CGROUP_SKB`, `invalid access of data_meta for CGROUP_SKB`, `invalid access of flow_keys for CGROUP_SKB`, `invalid write access to napi_id for CGROUP_SKB`, `write tstamp from CGROUP_SKB`, `read tstamp from CGROUP_SKB`. Expected verifier diagnostics include `invalid bpf_context access off=76 size=4`, `invalid bpf_context access`, `invalid bpf_context access off=152 size=8`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_skb.c -->
