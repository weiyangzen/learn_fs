<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_looping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_looping.c

Purpose: Focused verifier tests for `bpf_repeat`/iterator looping corner cases, including NULL checks, access size, and stack-depth widening. The file has 217 source lines and 4147 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:consume_first_item_only, ?raw_tp:missing_null_check_fail, ?raw_tp:wrong_sized_read_fail, ?raw_tp:simplest_loop`. Local functions/subprograms: `force_clang_to_emit_btf_for_externs, consume_first_item_only, missing_null_check_fail, wrong_sized_read_fail, simplest_loop, iterator_with_diff_stack_depth`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_repeat`. Verifier messages asserted here: `R0 invalid mem access 'scalar', invalid access to memory, mem_size=4 off=0 size=8, R0 min value is outside of the allowed memory range`.

Control flow: Entry points are BPF programs in `?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:consume_first_item_only, ?raw_tp:missing_null_check_fail, ?raw_tp:wrong_sized_read_fail, ?raw_tp:simplest_loop`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `R0 invalid mem access 'scalar', invalid access to memory, mem_size=4 off=0 size=8, R0 min value is outside of the allowed memory range`; successful attachment/execution of ?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:consume_first_item_only, ?raw_tp:missing_null_check_fail, ?raw_tp:wrong_sized_read_fail, ?raw_tp:simplest_loop; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_looping.c -->
