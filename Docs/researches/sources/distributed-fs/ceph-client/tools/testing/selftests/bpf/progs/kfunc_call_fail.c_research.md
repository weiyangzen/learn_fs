<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_fail.c

Purpose: Negative kfunc-call verifier cases for syscall contexts, NULL handling, memory lifetime, constant lengths, and pointer type mismatches. The file has 161 source lines and 3225 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?syscall:kfunc_syscall_test_fail, ?syscall:kfunc_syscall_test_null_fail, ?tc:kfunc_call_test_get_mem_fail_rdonly, ?tc:kfunc_call_test_get_mem_fail_use_after_free, ?tc:kfunc_call_test_get_mem_fail_oob, ?tc:kfunc_call_test_get_mem_fail_not_const, ?tc:kfunc_call_test_mem_acquire_fail, ?tc:kfunc_call_test_pointer_arg_type_mismatch`. Local functions/subprograms: `kfunc_syscall_test_fail, kfunc_syscall_test_null_fail, kfunc_call_test_get_mem_fail_rdonly, kfunc_call_test_get_mem_fail_use_after_free, kfunc_call_test_get_mem_fail_oob, kfunc_call_test_get_mem_fail_not_const, kfunc_call_test_mem_acquire_fail, kfunc_call_test_pointer_arg_type_mismatch`. Maps: `none declared in this file`. Types: `syscall_test_args`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_int_mem_release, bpf_kfunc_call_test_acq_rdonly_mem, bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_get_rdonly_mem, bpf_kfunc_call_test_get_rdwr_mem, bpf_kfunc_call_test_mem_len_pass1, bpf_kfunc_call_test_pass_ctx, bpf_kfunc_call_test_release`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `?syscall:kfunc_syscall_test_fail, ?syscall:kfunc_syscall_test_null_fail, ?tc:kfunc_call_test_get_mem_fail_rdonly, ?tc:kfunc_call_test_get_mem_fail_use_after_free, ?tc:kfunc_call_test_get_mem_fail_oob, ?tc:kfunc_call_test_get_mem_fail_not_const, ?tc:kfunc_call_test_mem_acquire_fail, ?tc:kfunc_call_test_pointer_arg_type_mismatch`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of ?syscall:kfunc_syscall_test_fail, ?syscall:kfunc_syscall_test_null_fail, ?tc:kfunc_call_test_get_mem_fail_rdonly, ?tc:kfunc_call_test_get_mem_fail_use_after_free, ?tc:kfunc_call_test_get_mem_fail_oob, ?tc:kfunc_call_test_get_mem_fail_not_const; plus 2 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_fail.c -->
