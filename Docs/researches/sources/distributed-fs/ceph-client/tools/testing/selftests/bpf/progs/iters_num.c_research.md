<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_num.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_num.c

Purpose: Runtime numeric iterator tests over empty, negative, positive, huge, and element-count-limited ranges. The file has 243 source lines and 4285 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:num_empty_zero, raw_tp/sys_enter:num_empty_int_min, raw_tp/sys_enter:num_empty_int_max, raw_tp/sys_enter:num_empty_minus_one, raw_tp/sys_enter:num_simple_sum, raw_tp/sys_enter:num_neg_sum, raw_tp/sys_enter:num_very_neg_sum, raw_tp/sys_enter:num_very_big_sum, raw_tp/sys_enter:num_neg_pos_sum, raw_tp/sys_enter:num_invalid_range, raw_tp/sys_enter:num_max_range, raw_tp/sys_enter:num_e2big_range; plus 3 more`. Local functions/subprograms: `num_empty_zero, num_empty_int_min, num_empty_int_max, num_empty_minus_one, num_simple_sum, num_neg_sum, num_very_neg_sum, num_very_big_sum, num_neg_pos_sum, num_invalid_range, num_max_range, num_e2big_range, num_succ_elem_cnt, num_overfetched_elem_cnt; plus 1 more`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_for, bpf_iter_num_destroy, bpf_iter_num_new, bpf_iter_num_next`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:num_empty_zero, raw_tp/sys_enter:num_empty_int_min, raw_tp/sys_enter:num_empty_int_max, raw_tp/sys_enter:num_empty_minus_one, raw_tp/sys_enter:num_simple_sum, raw_tp/sys_enter:num_neg_sum, raw_tp/sys_enter:num_very_neg_sum, raw_tp/sys_enter:num_very_big_sum; plus 7 more`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of raw_tp/sys_enter:num_empty_zero, raw_tp/sys_enter:num_empty_int_min, raw_tp/sys_enter:num_empty_int_max, raw_tp/sys_enter:num_empty_minus_one, raw_tp/sys_enter:num_simple_sum, raw_tp/sys_enter:num_neg_sum; plus 9 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_num.c -->
