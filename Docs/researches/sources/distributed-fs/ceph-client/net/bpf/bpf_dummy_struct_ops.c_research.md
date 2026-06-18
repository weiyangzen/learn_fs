<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c -->
# sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c

Purpose: provides a dummy BPF struct-ops target used by BPF selftests to validate struct-ops verifier behavior, trampoline preparation, nullable pointer handling, sleepable restrictions, and test-run invocation.

Important APIs, types, and functions: exports `bpf_struct_ops_test_run` for test execution against `bpf_dummy_ops`. `struct bpf_dummy_ops_test_args` holds up to `MAX_BPF_FUNC_ARGS` raw user arguments plus a copied `bpf_dummy_ops_state`. `dummy_ops_init_args`, `dummy_ops_copy_args`, and `dummy_ops_call_op` marshal user state into a generated trampoline call. `check_test_run_args` inspects the attached function prototype and verifier context arg metadata to reject NULL for non-nullable pointer arguments. `bpf_dummy_ops_btf_struct_access` permits verifier writes only to `bpf_dummy_ops_state`. `bpf_dummy_ops_check_member` limits sleepable programs to the `test_sleepable` member.

Control flow: late init registers `bpf_bpf_dummy_ops`. A test run first verifies the program is attached to the dummy ops BTF type, copies exactly the number of u64 arguments implied by the attach function prototype, checks nullable pointer rules, creates a temporary `bpf_tramp_link`, increments the program reference, asks `bpf_struct_ops_prepare_trampoline` for an executable image, protects it, calls the selected op through the trampoline, copies the possibly modified state back to userspace, and writes the return value. Cleanup frees args, trampoline image, link, and tlink array on all paths.

State and persistence: global `bpf_dummy_ops_btf` caches the BTF pointer passed by struct-ops registration. Runtime test state is per-call and temporary. Registration state persists for the module lifetime through `register_bpf_struct_ops`.

Dependencies and integration points: depends on BPF verifier internals, BTF type lookup, BPF link and trampoline APIs, CFI offset handling, and the generated CFI stub instance `__bpf_bpf_dummy_ops`. It is built only with BPF syscall and JIT support.

Risks: argument marshalling is ABI-sensitive because it calls a variadic function pointer through a trampoline. Nullable pointer enforcement depends on correct BTF arg offsets and verifier `ctx_arg_info`. Missing cleanup would leak BPF program refs or executable trampoline memory. Sleepable acceptance must stay aligned with struct-ops verifier expectations.

Test signals: BPF selftests for dummy struct ops, nullable and non-nullable context arguments, writes to `bpf_dummy_ops_state`, sleepable member acceptance/rejection, and test-run return/state copyback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bpf/bpf_dummy_struct_ops.c -->
