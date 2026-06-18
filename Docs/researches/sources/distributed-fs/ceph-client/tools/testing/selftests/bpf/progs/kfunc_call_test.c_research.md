<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test.c

Purpose: Positive kfunc-call coverage for scalar arguments, acquired references, syscall kfuncs, memory-return kfuncs, and testmod context objects. The file has 316 source lines and 6698 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:kfunc_call_test5, tc:kfunc_call_test4, tc:kfunc_call_test2, tc:kfunc_call_test1, tc:kfunc_call_test_ref_btf_id, tc:kfunc_call_test_pass, syscall:kfunc_syscall_test, syscall:kfunc_syscall_test_null, tc:kfunc_call_test_get_mem, tc:kfunc_call_test_static_unused_arg, tc:kfunc_call_ctx`. Local functions/subprograms: `kfunc_call_test5, kfunc_call_test4, kfunc_call_test2, kfunc_call_test1, kfunc_call_test_ref_btf_id, kfunc_call_test_pass, kfunc_syscall_test, kfunc_syscall_test_null, kfunc_call_test_get_mem, kfunc_call_test_static_unused_arg, kfunc_call_ctx`. Maps: `ctx_map`. Types: `syscall_test_args, ctx_val`. BPF helpers/kfuncs/macros used as calls: `bpf_get_prandom_u32, bpf_kfunc_call_test1, bpf_kfunc_call_test2, bpf_kfunc_call_test4, bpf_kfunc_call_test5, bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_get_rdonly_mem, bpf_kfunc_call_test_get_rdwr_mem, bpf_kfunc_call_test_mem_len_fail2, bpf_kfunc_call_test_mem_len_pass1, bpf_kfunc_call_test_pass1, bpf_kfunc_call_test_pass2, bpf_kfunc_call_test_pass_ctx, bpf_kfunc_call_test_release, bpf_kfunc_call_test_static_unused_arg, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_sk_fullsock; plus 2 more`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:kfunc_call_test5, tc:kfunc_call_test4, tc:kfunc_call_test2, tc:kfunc_call_test1, tc:kfunc_call_test_ref_btf_id, tc:kfunc_call_test_pass, syscall:kfunc_syscall_test, syscall:kfunc_syscall_test_null; plus 3 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: Persistent state is held in BPF maps `ctx_map` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; the `bpf_testmod` kernel module and its exported test kfuncs. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:kfunc_call_test5, tc:kfunc_call_test4, tc:kfunc_call_test2, tc:kfunc_call_test1, tc:kfunc_call_test_ref_btf_id, tc:kfunc_call_test_pass; plus 5 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test.c -->
