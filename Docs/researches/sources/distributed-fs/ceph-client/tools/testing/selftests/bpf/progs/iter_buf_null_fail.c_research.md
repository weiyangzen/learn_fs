<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iter_buf_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iter_buf_null_fail.c

Purpose: Negative and positive verifier coverage for iterator context buffers where `ctx->meta->seq` can be NULL. The file has 40 source lines and 835 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `iter/bpf_map_elem:iter_buf_null_deref, iter/bpf_map_elem:iter_buf_null_check_ok`. Local functions/subprograms: `iter_buf_null_deref, iter_buf_null_check_ok`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `invalid mem access`.

Control flow: Entry points are BPF programs in `iter/bpf_map_elem:iter_buf_null_deref, iter/bpf_map_elem:iter_buf_null_check_ok`. Control flow is centered on annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `invalid mem access`; successful attachment/execution of iter/bpf_map_elem:iter_buf_null_deref, iter/bpf_map_elem:iter_buf_null_check_ok; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iter_buf_null_fail.c -->
