# Research: subset-b-006811

Grouped research for work item `subset-b-006811`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c

Purpose: Exercises BPF netfilter defragmentation visibility by detecting IPv4 and IPv6 fragment headers from skb dynptr slices. The file has 100 source lines and 1967 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `netfilter:defrag`. Local functions/subprograms: `is_frag_v4, is_frag_v6, handle_v4, handle_v6, defrag`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_dynptr_from_skb, bpf_dynptr_slice, bpf_ntohs`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `netfilter:defrag`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of netfilter:defrag; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/irq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/irq.c

Purpose: Verifier matrix for `bpf_local_irq_save/restore` and IRQ-safe resource spin locks, including stack flag tracking, nesting, sleepability, and out-of-order restore rejection. The file has 567 source lines and 12575 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?tc:irq_save_bad_arg, ?tc:irq_restore_bad_arg, ?tc:irq_restore_missing_2, ?tc:irq_restore_missing_3, ?tc:irq_restore_missing_3_minus_2, ?tc:irq_restore_missing_1_subprog, ?tc:irq_restore_missing_2_subprog, ?tc:irq_restore_missing_3_subprog, ?tc:irq_restore_missing_3_minus_2_subprog, ?tc:irq_balance, ?tc:irq_balance_n, ?tc:irq_balance_subprog; plus 19 more`. Local functions/subprograms: `irq_save_bad_arg, irq_restore_bad_arg, irq_restore_missing_2, irq_restore_missing_3, irq_restore_missing_3_minus_2, irq_restore_missing_1_subprog, irq_restore_missing_2_subprog, irq_restore_missing_3_subprog, irq_restore_missing_3_minus_2_subprog, irq_balance, irq_balance_n, irq_balance_subprog, irq_sleepable_helper, irq_sleepable_kfunc; plus 19 more`. Maps: `none declared in this file`. Types: `bpf_res_spin_lock, bpf_res_spin_lock`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_copy_from_user_str, bpf_iter_num_new, bpf_local_irq_restore, bpf_local_irq_save, bpf_obj_drop, bpf_obj_new, bpf_printk, bpf_res_spin_lock_irqsave, bpf_res_spin_unlock_irqrestore`. Verifier messages asserted here: `arg#0 doesn't point to an irq flag on stack, arg#0 doesn't point to an irq flag on stack, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region; plus 19 more`.

Control flow: Entry points are BPF programs in `?tc:irq_save_bad_arg, ?tc:irq_restore_bad_arg, ?tc:irq_restore_missing_2, ?tc:irq_restore_missing_3, ?tc:irq_restore_missing_3_minus_2, ?tc:irq_restore_missing_1_subprog, ?tc:irq_restore_missing_2_subprog, ?tc:irq_restore_missing_3_subprog; plus 23 more`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; critical sections protect intrusive container or resource-spin-lock state; helper-mediated memory reads avoid direct unsafe kernel/user access; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: void bpf_local_irq_save(unsigned long *) __weak __ksym, void bpf_local_irq_restore(unsigned long *) __weak __ksym, int bpf_copy_from_user_str(void *dst, u32 dst__sz, const void *unsafe_ptr__ign, u64 flags) __weak __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics; reference/kptr ownership mistakes can leak references or allow use-after-drop patterns; memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `arg#0 doesn't point to an irq flag on stack, arg#0 doesn't point to an irq flag on stack, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region, BPF_EXIT instruction in main prog cannot be used inside bpf_local_irq_save-ed region; plus 23 more`; successful attachment/execution of ?tc:irq_save_bad_arg, ?tc:irq_restore_bad_arg, ?tc:irq_restore_missing_2, ?tc:irq_restore_missing_3, ?tc:irq_restore_missing_3_minus_2, ?tc:irq_restore_missing_1_subprog; plus 25 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/irq.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters.c

Purpose: Large open-coded numeric iterator verifier suite covering safe loops, unsafe loop widening, iterator lifetime, stack precision, callback equivalence, and macro wrappers. The file has 2070 source lines and 43490 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp:iter_err_unsafe_c_loop, ?raw_tp:iter_err_unsafe_asm_loop, raw_tp:iter_while_loop, raw_tp:iter_while_loop_auto_cleanup, raw_tp:iter_for_loop, raw_tp:iter_bpf_for_each_macro, raw_tp:iter_bpf_for_macro, raw_tp:iter_pragma_unroll_loop, raw_tp:iter_manual_unroll_loop, raw_tp:iter_multiple_sequential_loops, raw_tp:iter_limit_cond_break_loop, raw_tp:iter_obfuscate_counter; plus 17 more`. Local functions/subprograms: `iter_err_unsafe_c_loop, iter_err_unsafe_asm_loop, iter_while_loop, iter_while_loop_auto_cleanup, iter_for_loop, iter_bpf_for_each_macro, iter_bpf_for_macro, iter_pragma_unroll_loop, iter_manual_unroll_loop, iter_multiple_sequential_loops, iter_limit_cond_break_loop, iter_obfuscate_counter, iter_search_loop, iter_array_fill; plus 19 more`. Maps: `amap, hash_map`. Types: `bpf_iter_num`. BPF helpers/kfuncs/macros used as calls: `bpf_for, bpf_for_each, bpf_get_current_comm, bpf_get_current_pid_tgid, bpf_get_prandom_u32, bpf_iter_num_destroy, bpf_iter_num_new, bpf_iter_num_next, bpf_loop, bpf_map_lookup_elem, bpf_printk, bpf_probe_read_kernel, bpf_probe_read_user, bpf_repeat`. Verifier messages asserted here: `math between map_value pointer and register with unbounded min value is not allowed, unbounded memory access, invalid mem access 'scalar', invalid mem access 'map_value_or_null', invalid mem access 'map_value_or_null', R1 type=scalar expected=fp, math between fp pointer and register with unbounded, math between fp pointer and register with unbounded; plus 9 more`.

Control flow: Entry points are BPF programs in `?raw_tp:iter_err_unsafe_c_loop, ?raw_tp:iter_err_unsafe_asm_loop, raw_tp:iter_while_loop, raw_tp:iter_while_loop_auto_cleanup, raw_tp:iter_for_loop, raw_tp:iter_bpf_for_each_macro, raw_tp:iter_bpf_for_macro, raw_tp:iter_pragma_unroll_loop; plus 21 more`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `amap, hash_map` and in globals emitted into BPF data sections. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics; memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `math between map_value pointer and register with unbounded min value is not allowed, unbounded memory access, invalid mem access 'scalar', invalid mem access 'map_value_or_null'; plus 13 more`; successful attachment/execution of ?raw_tp:iter_err_unsafe_c_loop, ?raw_tp:iter_err_unsafe_asm_loop, raw_tp:iter_while_loop, raw_tp:iter_while_loop_auto_cleanup, raw_tp:iter_for_loop, raw_tp:iter_bpf_for_each_macro; plus 23 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c

Purpose: Sleepable BPF iterator program that walks cgroup subsystems under RCU and validates css/cgroup iterator lifetime handling. The file has 76 source lines and 1921 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `bpf_cgroup_release, bpf_rcu_read_lock, bpf_rcu_read_unlock, iter_css_for_each`. Maps: `none declared in this file`. Types: `cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_task_btf, bpf_rcu_read_lock, bpf_rcu_read_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c

Purpose: LSM and cgroup iterator programs that combine current-task cgroup acquisition with css-task iteration and cgroup iterator output. The file has 103 source lines and 2182 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer`. Local functions/subprograms: `bpf_cgroup_release, BPF_PROG, cgroup_id, cgroup_id_printer, BPF_PROG`. Maps: `none declared in this file`. Types: `cgroup, cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_acquire, bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_task_btf`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_state_safety.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_state_safety.c

Purpose: Verifier safety suite for open-coded iterator state creation, destruction, corruption, stack reuse, and leak detection. The file has 427 source lines and 8640 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:create_and_destroy, ?raw_tp:create_and_forget_to_destroy_fail, ?raw_tp:destroy_without_creating_fail, ?raw_tp:compromise_iter_w_direct_write_fail, ?raw_tp:compromise_iter_w_direct_write_and_skip_destroy_fail, ?raw_tp:compromise_iter_w_helper_write_fail, ?raw_tp:valid_stack_reuse, ?raw_tp:double_create_fail, ?raw_tp:double_destroy_fail, ?raw_tp:next_without_new_fail, ?raw_tp:next_after_destroy_fail; plus 2 more`. Local functions/subprograms: `force_clang_to_emit_btf_for_externs, create_and_destroy, create_and_forget_to_destroy_fail, destroy_without_creating_fail, compromise_iter_w_direct_write_fail, compromise_iter_w_direct_write_and_skip_destroy_fail, compromise_iter_w_helper_write_fail, leak_iter_from_subprog_fail, valid_stack_reuse, double_create_fail, double_destroy_fail, next_without_new_fail, next_after_destroy_fail, stacksafe_should_not_conflate_stack_spill_and_iter`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_iter_num_new, bpf_probe_read_kernel, bpf_repeat`. Verifier messages asserted here: `fp-8=iter_num(ref_id=1,state=active,depth=0), Unreleased reference id=1, expected an initialized iter_num as arg #0, expected an initialized iter_num as arg #0, Unreleased reference id=1, expected an initialized iter_num as arg #0, returning from callee:, Unreleased reference id=1; plus 7 more`.

Control flow: Entry points are BPF programs in `?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:create_and_destroy, ?raw_tp:create_and_forget_to_destroy_fail, ?raw_tp:destroy_without_creating_fail, ?raw_tp:compromise_iter_w_direct_write_fail, ?raw_tp:compromise_iter_w_direct_write_and_skip_destroy_fail, ?raw_tp:compromise_iter_w_helper_write_fail, ?raw_tp:valid_stack_reuse; plus 6 more`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; helper-mediated memory reads avoid direct unsafe kernel/user access; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics; memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `fp-8=iter_num(ref_id=1,state=active,depth=0), Unreleased reference id=1, expected an initialized iter_num as arg #0, expected an initialized iter_num as arg #0; plus 11 more`; successful attachment/execution of ?raw_tp:force_clang_to_emit_btf_for_externs, ?raw_tp:create_and_destroy, ?raw_tp:create_and_forget_to_destroy_fail, ?raw_tp:destroy_without_creating_fail, ?raw_tp:compromise_iter_w_direct_write_fail, ?raw_tp:compromise_iter_w_direct_write_and_skip_destroy_fail; plus 8 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_state_safety.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task.c

Purpose: Task iterator program that walks tasks from a current-task seed while holding an explicit BPF RCU read-side section. The file has 52 source lines and 1333 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `bpf_rcu_read_lock, bpf_rcu_read_unlock, iter_task_for_each_sleep`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_for_each, bpf_get_current_task_btf, bpf_rcu_read_lock, bpf_rcu_read_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c

Purpose: Negative verifier cases for task/css/css-task iterators used without required RCU protection or in disallowed program types. The file has 106 source lines and 2577 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `bpf_cgroup_release, bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `none declared in this file`. Types: `cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_cgroup_id, bpf_rcu_read_lock, bpf_rcu_read_unlock`. Verifier messages asserted here: `kernel func bpf_iter_task_new requires RCU critical section protection, kernel func bpf_iter_css_new requires RCU critical section protection, expected an RCU CS when using bpf_iter_task_next, expected an RCU CS when using bpf_iter_css_next, css_task_iter is only allowed in bpf_lsm, bpf_iter and sleepable progs`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `kernel func bpf_iter_task_new requires RCU critical section protection, kernel func bpf_iter_css_new requires RCU critical section protection, expected an RCU CS when using bpf_iter_task_next, expected an RCU CS when using bpf_iter_css_next; plus 1 more`; compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c

Purpose: Task VMA iterator smoke test over the current task's VMAs with a deliberately unlikely branch to keep verifier state live. The file has 44 source lines and 828 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:iter_task_vma_for_each`. Local functions/subprograms: `iter_task_vma_for_each`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_cmp_unlikely, bpf_for_each, bpf_get_current_task_btf`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:iter_task_vma_for_each`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of raw_tp/sys_enter:iter_task_vma_for_each; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod.c

Purpose: BPF test module iterator and kfunc trust/RCU contract tests for task, VMA, numeric, and custom return-pointer kfuncs. The file has 172 source lines and 3951 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:iter_next_trusted, raw_tp/sys_enter:iter_next_trusted_or_null, raw_tp/sys_enter:iter_next_rcu, raw_tp/sys_enter:iter_next_rcu_or_null, raw_tp/sys_enter:iter_next_rcu_not_trusted`. Local functions/subprograms: `iter_next_trusted, iter_next_trusted_or_null, iter_next_rcu, iter_next_rcu_or_null, iter_next_rcu_not_trusted, iter_next_ptr_mem_not_trusted, iter_ret_rcu_test_protected, iter_ret_rcu_test_type, iter_ret_rcu_test_protected_nostruct, iter_ret_rcu_test_type_nostruct`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_iter_num_destroy, bpf_iter_num_new, bpf_iter_num_next, bpf_iter_task_destroy, bpf_iter_task_new, bpf_iter_task_next, bpf_iter_task_vma_destroy, bpf_iter_task_vma_new, bpf_iter_task_vma_next, bpf_kfunc_rcu_task_test, bpf_kfunc_ret_rcu_test, bpf_kfunc_ret_rcu_test_nostruct, bpf_kfunc_trusted_num_test, bpf_kfunc_trusted_task_test, bpf_kfunc_trusted_vma_test, bpf_rcu_read_lock, bpf_rcu_read_unlock; plus 1 more`. Verifier messages asserted here: `Possibly NULL pointer passed to trusted arg0, Possibly NULL pointer passed to trusted arg0, R1 must be referenced or trusted, R1 cannot write into rdonly_mem, kernel func bpf_kfunc_ret_rcu_test requires RCU critical section protection, R1 type=rcu_ptr_or_null_ expected=, kernel func bpf_kfunc_ret_rcu_test_nostruct requires RCU critical section protection, R1 type=rdonly_rcu_mem_or_null expected=`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:iter_next_trusted, raw_tp/sys_enter:iter_next_trusted_or_null, raw_tp/sys_enter:iter_next_rcu, raw_tp/sys_enter:iter_next_rcu_or_null, raw_tp/sys_enter:iter_next_rcu_not_trusted`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; test kfunc calls validate argument typing, reference ownership, and module resolution; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; the `bpf_testmod` kernel module and its exported test kfuncs. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `Possibly NULL pointer passed to trusted arg0, Possibly NULL pointer passed to trusted arg0, R1 must be referenced or trusted, R1 cannot write into rdonly_mem; plus 4 more`; successful attachment/execution of raw_tp/sys_enter:iter_next_trusted, raw_tp/sys_enter:iter_next_trusted_or_null, raw_tp/sys_enter:iter_next_rcu, raw_tp/sys_enter:iter_next_rcu_or_null, raw_tp/sys_enter:iter_next_rcu_not_trusted; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod_seq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod_seq.c

Purpose: Custom `bpf_iter_testmod_seq` iterator tests for normal sums, truncation, helper getter ordering, and drained-state validation. The file has 130 source lines and 2962 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:testmod_seq_empty, raw_tp/sys_enter:testmod_seq_full, raw_tp/sys_enter:testmod_seq_truncated, ?raw_tp:testmod_seq_getter_before_bad, ?raw_tp:testmod_seq_getter_after_bad, ?socket:testmod_seq_getter_good`. Local functions/subprograms: `testmod_seq_empty, testmod_seq_full, testmod_seq_truncated, testmod_seq_getter_before_bad, testmod_seq_getter_after_bad, testmod_seq_getter_good`. Maps: `none declared in this file`. Types: `bpf_iter_testmod_seq`. BPF helpers/kfuncs/macros used as calls: `bpf_for_each, bpf_iter_testmod_seq_destroy, bpf_iter_testmod_seq_new, bpf_iter_testmod_seq_next, bpf_iter_testmod_seq_value`. Verifier messages asserted here: `fp-16=iter_testmod_seq(ref_id=1,state=active,depth=0), fp-16=iter_testmod_seq(ref_id=1,state=drained,depth=0), call bpf_iter_testmod_seq_destroy, fp-16=iter_testmod_seq(ref_id=1,state=active,depth=0), fp-16=iter_testmod_seq(ref_id=1,state=drained,depth=0), call bpf_iter_testmod_seq_destroy, fp-16=iter_testmod_seq(ref_id=1,state=active,depth=0), fp-16=iter_testmod_seq(ref_id=1,state=drained,depth=0); plus 3 more`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:testmod_seq_empty, raw_tp/sys_enter:testmod_seq_full, raw_tp/sys_enter:testmod_seq_truncated, ?raw_tp:testmod_seq_getter_before_bad, ?raw_tp:testmod_seq_getter_after_bad, ?socket:testmod_seq_getter_good`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_iter_testmod_seq_new(struct bpf_iter_testmod_seq *it, s64 value, int cnt) __ksym, s64 *bpf_iter_testmod_seq_next(struct bpf_iter_testmod_seq *it) __ksym, s64 bpf_iter_testmod_seq_value(int blah, struct bpf_iter_testmod_seq *it) __ksym, void bpf_iter_testmod_seq_destroy(struct bpf_iter_testmod_seq *it) __ksym; the `bpf_testmod` kernel module and its exported test kfuncs. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: libbpf verifier annotations __failure, __retval(1000000), __success; expected verifier diagnostics such as `fp-16=iter_testmod_seq(ref_id=1,state=active,depth=0), fp-16=iter_testmod_seq(ref_id=1,state=drained,depth=0), call bpf_iter_testmod_seq_destroy, fp-16=iter_testmod_seq(ref_id=1,state=active,depth=0); plus 7 more`; successful attachment/execution of raw_tp/sys_enter:testmod_seq_empty, raw_tp/sys_enter:testmod_seq_full, raw_tp/sys_enter:testmod_seq_truncated, ?raw_tp:testmod_seq_getter_before_bad, ?raw_tp:testmod_seq_getter_after_bad, ?socket:testmod_seq_getter_good; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_testmod_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c

Purpose: Regression test that prevents equality-branch inference from treating a map lookup result as non-NULL unsafely. The file has 47 source lines and 1174 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp:jeq_infer_not_null_ptr_to_btfid`. Local functions/subprograms: `jeq_infer_not_null_ptr_to_btfid`. Maps: `m_hash`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem`. Verifier messages asserted here: `R8 invalid mem access 'map_value_or_null`.

Control flow: Entry points are BPF programs in `?raw_tp:jeq_infer_not_null_ptr_to_btfid`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `m_hash` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `R8 invalid mem access 'map_value_or_null`; successful attachment/execution of ?raw_tp:jeq_infer_not_null_ptr_to_btfid; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c

Purpose: JIT/runtime probe-memory path test using acquired kfunc objects and kptr exchange/release. The file has 60 source lines and 1061 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:test_jit_probe_mem`. Local functions/subprograms: `test_jit_probe_mem`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_release, bpf_kptr_xchg`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:test_jit_probe_mem`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:test_jit_probe_mem; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c

Purpose: Tracepoint/fentry/fexit skb test that reads skb/net_device metadata and emits perf samples during free and eth-type paths. The file has 154 source lines and 3654 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `perf_buf_map`. Types: `callback_head, dev_ifalias, net_device, sk_buff, meta`. BPF helpers/kfuncs/macros used as calls: `bpf_htons, bpf_printk, bpf_probe_read_kernel, bpf_skb_output`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `perf_buf_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_destructive.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_destructive.c

Purpose: Minimal program that invokes a destructive test kfunc from TC to exercise destructive kfunc gating. The file has 14 source lines and 267 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:kfunc_destructive_test`. Local functions/subprograms: `kfunc_destructive_test`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_destructive`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:kfunc_destructive_test`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:kfunc_destructive_test; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_destructive.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_race.c

Purpose: Small module-kfunc attachment used to reproduce kfunc lookup/race behavior while loading test modules. The file has 14 source lines and 273 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:kfunc_call_fail`. Local functions/subprograms: `kfunc_call_fail`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_testmod_test_mod_kfunc`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:kfunc_call_fail`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; the `bpf_testmod` kernel module and its exported test kfuncs. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:kfunc_call_fail; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_race.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c

Purpose: Subprogram kfunc-call test that mixes socket context conversion, per-CPU ksym lookup, and test kfunc calls. The file has 38 source lines and 758 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:kfunc_call_test1`. Local functions/subprograms: `kfunc_call_test1`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_smp_processor_id, bpf_kfunc_call_test1, bpf_kfunc_call_test3, bpf_per_cpu_ptr, bpf_sk_fullsock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:kfunc_call_test1`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: const int bpf_prog_active __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:kfunc_call_test1; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c

Purpose: Tests kfuncs with implicit `struct bpf_prog_aux` arguments and verifies that implementation symbols cannot be called directly. The file has 42 source lines and 1115 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl`. Local functions/subprograms: `test_kfunc_implicit_arg, test_kfunc_implicit_arg_impl_illegal, test_kfunc_implicit_arg_legacy, test_kfunc_implicit_arg_legacy_impl`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_implicit_arg, bpf_kfunc_implicit_arg_impl, bpf_kfunc_implicit_arg_legacy, bpf_kfunc_implicit_arg_legacy_impl`. Verifier messages asserted here: `cannot find address for kernel function bpf_kfunc_implicit_arg_impl`.

Control flow: Entry points are BPF programs in `syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_kfunc_implicit_arg(int a) __weak __ksym, int bpf_kfunc_implicit_arg_impl(int a, struct bpf_prog_aux *aux) __weak __ksym, int bpf_kfunc_implicit_arg_legacy(int a, int b) __weak __ksym, int bpf_kfunc_implicit_arg_legacy_impl(int a, int b, struct bpf_prog_aux *aux) __weak __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes.

Test signals: libbpf verifier annotations __failure, __retval(11), __retval(5), __retval(7); expected verifier diagnostics such as `cannot find address for kernel function bpf_kfunc_implicit_arg_impl`; successful attachment/execution of syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c

Purpose: Classifier programs that call kfuncs from differently ordered test modules to validate module kfunc resolution. The file has 31 source lines and 618 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `classifier:call_kfunc_xy, classifier:call_kfunc_yx`. Local functions/subprograms: `call_kfunc_xy, call_kfunc_yx`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_test_modorder_retx, bpf_test_modorder_rety`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `classifier:call_kfunc_xy, classifier:call_kfunc_yx`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_test_modorder_retx(void) __ksym, int bpf_test_modorder_rety(void) __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of classifier:call_kfunc_xy, classifier:call_kfunc_yx; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c

Purpose: Iterator and open-coded iterator programs for kmem_cache discovery, name matching, and map-based result collection. The file has 109 source lines and 2315 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter`. Local functions/subprograms: `slab_info_collector, BPF_PROG, open_coded_iter`. Maps: `slab_hash, slab_result`. Types: `kmem_cache_result`. BPF helpers/kfuncs/macros used as calls: `bpf_for_each, bpf_get_current_task, bpf_get_kmem_cache, bpf_map_lookup_elem, bpf_map_update_elem, bpf_probe_read_kernel_str, bpf_strncmp`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `slab_hash, slab_result` and in globals emitted into BPF data sections. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: struct kmem_cache *bpf_get_kmem_cache(u64 addr) __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi.c

Purpose: Kprobe.multi/kretprobe.multi functional tests for wildcard attachment, manual IP lists, attach cookies, and module symbols. The file has 163 source lines and 4382 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_tes??:test_kprobe, kretprobe.multi/bpf_fentry_test*:test_kretprobe, kprobe.multi:test_kprobe_manual, kretprobe.multi:test_kretprobe_manual, kprobe.multi:test_kprobe_testmod, kretprobe.multi:test_kretprobe_testmod`. Local functions/subprograms: `kprobe_multi_check, BPF_PROG, test_kprobe, test_kretprobe, test_kprobe_manual, test_kretprobe_manual, kprobe_multi_testmod_check, test_kprobe_testmod, test_kretprobe_testmod`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_attach_cookie, bpf_get_current_pid_tgid, bpf_get_func_ip`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_tes??:test_kprobe, kretprobe.multi/bpf_fentry_test*:test_kretprobe, kprobe.multi:test_kprobe_manual, kretprobe.multi:test_kretprobe_manual, kprobe.multi:test_kprobe_testmod, kretprobe.multi:test_kretprobe_testmod`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: const void bpf_fentry_test1 __ksym, const void bpf_fentry_test2 __ksym, const void bpf_fentry_test3 __ksym, const void bpf_fentry_test4 __ksym, const void bpf_fentry_test5 __ksym, const void bpf_fentry_test6 __ksym; plus 5 more; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_tes??:test_kprobe, kretprobe.multi/bpf_fentry_test*:test_kretprobe, kprobe.multi:test_kprobe_manual, kretprobe.multi:test_kretprobe_manual, kprobe.multi:test_kprobe_testmod; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c

Purpose: Empty-pattern kprobe.multi object used by user-space tests to validate attach rejection/edge behavior. The file has 13 source lines and 238 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.multi/:test_kprobe_empty`. Local functions/subprograms: `test_kprobe_empty`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe.multi/:test_kprobe_empty`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe.multi/:test_kprobe_empty; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_override.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_override.c

Purpose: Return-override tests for kprobe.multi and regular kprobe using `bpf_override_return` on selected PIDs. The file has 29 source lines and 505 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.multi:test_override, kprobe:test_kprobe_override`. Local functions/subprograms: `test_override, test_kprobe_override`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_override_return`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe.multi:test_override, kprobe:test_kprobe_override`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe.multi:test_override, kprobe:test_kprobe_override; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_override.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c

Purpose: Kprobe session tests that distinguish entry/return phases and verify function IP matching across wildcard and symbol attaches. The file has 89 source lines and 1986 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms`. Local functions/subprograms: `session_check, BPF_PROG, test_kprobe, test_kprobe_syms`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_get_func_ip, bpf_program__attach_kprobe_multi_opts`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: const void bpf_fentry_test1 __ksym, const void bpf_fentry_test2 __ksym, const void bpf_fentry_test3 __ksym, const void bpf_fentry_test4 __ksym, const void bpf_fentry_test5 __ksym, const void bpf_fentry_test6 __ksym; plus 2 more; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session_cookie.c

Purpose: Kprobe session cookie tests validating `bpf_session_cookie()` and `bpf_session_is_return()` for multiple programs. The file has 58 source lines and 1155 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test1:test_kprobe_1, kprobe.session/bpf_fentry_test1:test_kprobe_2, kprobe.session/bpf_fentry_test1:test_kprobe_3`. Local functions/subprograms: `BPF_PROG, check_cookie, test_kprobe_1, test_kprobe_2, test_kprobe_3`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_session_cookie, bpf_session_is_return`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test1:test_kprobe_1, kprobe.session/bpf_fentry_test1:test_kprobe_2, kprobe.session/bpf_fentry_test1:test_kprobe_3`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test1:test_kprobe_1, kprobe.session/bpf_fentry_test1:test_kprobe_2, kprobe.session/bpf_fentry_test1:test_kprobe_3; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session_cookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c

Purpose: Sleepable kprobe.multi test proving sleepable helpers are accepted only on sleepable attachments. The file has 26 source lines and 422 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG`. Local functions/subprograms: `handle_kprobe_multi_sleepable, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c

Purpose: Verifier return-value range tests for kprobe.session programs, including valid 0/1 and invalid 2 return values. The file has 32 source lines and 582 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2`. Local functions/subprograms: `kprobe_session_return_0, kprobe_session_return_1, kprobe_session_return_2`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `At program exit the register R0 has smin=2 smax=2 should have been in [0, 1]`.

Control flow: Entry points are BPF programs in `kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2`. Control flow is centered on annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: libbpf verifier annotations __failure, __success; expected verifier diagnostics such as `At program exit the register R0 has smin=2 smax=2 should have been in [0, 1]`; successful attachment/execution of kprobe.session:kprobe_session_return_0, kprobe.session:kprobe_session_return_1, kprobe.session:kprobe_session_return_2; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_verifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c

Purpose: Verifier tests around writing kprobe and kprobe.multi context memory, including freplace/fentry combinations. The file has 42 source lines and 607 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG`. Local functions/subprograms: `kprobe_write_ctx, kprobe_multi_write_ctx, kprobe_dummy, freplace_kprobe, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c

Purpose: Inline-BTF kptr exchange test with local root types and object dropping. The file has 49 source lines and 1004 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `__btf_root`. Maps: `none declared in this file`. Types: `bin_data`. BPF helpers/kfuncs/macros used as calls: `bpf_obj_drop`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c

Purpose: Per-CPU ksym access race reproducer using a test-module percpu symbol and `bpf_this_cpu_ptr`. The file has 14 source lines and 283 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:ksym_fail`. Local functions/subprograms: `ksym_fail`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_this_cpu_ptr`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:ksym_fail`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_testmod_ksym_percpu __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:ksym_fail; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c

Purpose: One half of a linked-object test where subprograms and kfunc-like helpers reference functions defined in another object. The file has 98 source lines and 2581 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `set_output_val1, set_output_ctx1, BPF_PROG, kfunc_gen1`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_cast_to_kern_ctx, bpf_core_type_size, bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `?raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int set_output_val2(int x). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of ?raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs2.c

Purpose: Second half of the linked-function test, mirroring cross-object calls and kernel-context casting. The file has 98 source lines and 2634 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `set_output_val2, set_output_ctx2, BPF_PROG, kfunc_gen2`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_cast_to_kern_ctx, bpf_core_type_size, bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `?raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int set_output_val1(int x). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of ?raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c

Purpose: Positive intrusive BPF linked-list tests over map, inner-map, global, nested, and array-backed list heads. The file has 421 source lines and 8340 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple, tc:inner_map_list_push_pop_multiple, tc:global_list_push_pop_multiple, tc:map_list_in_list, tc:inner_map_list_in_list, tc:global_list_in_list`. Local functions/subprograms: `list_push_pop, list_push_pop_multiple, list_in_list, test_list_push_pop, test_list_push_pop_multiple, test_list_in_list, map_list_push_pop, inner_map_list_push_pop, global_list_push_pop, global_list_push_pop_nested, global_list_array_push_pop, map_list_push_pop_multiple, inner_map_list_push_pop_multiple, global_list_push_pop_multiple; plus 3 more`. Maps: `none declared in this file`. Types: `head_nested_inner, head_nested`. BPF helpers/kfuncs/macros used as calls: `bpf_list_pop_back, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple, tc:inner_map_list_push_pop_multiple, tc:global_list_push_pop_multiple; plus 3 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple; plus 5 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.h

Purpose: Shared list/map type definitions for linked-list selftests, including nested list nodes and map-of-maps declarations. The file has 57 source lines and 1166 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `none declared in this file`. Maps: `map_of_maps`. Types: `bar, foo, map_value, array_map, array_map, array_map`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: This header has no runtime persistence; it defines shared structs, inline helpers, or map declarations consumed by companion BPF object files.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_fail.c

Purpose: Large negative verifier suite for BPF list/node ownership, locking, direct access, map compatibility, and pointer offsets. The file has 612 source lines and 13139 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?kprobe/xyz:map_compat_kprobe, ?kretprobe/xyz:map_compat_kretprobe, ?tracepoint/xyz:map_compat_tp, ?perf_event:map_compat_perf, ?raw_tp/xyz:map_compat_raw_tp, ?raw_tp.w/xyz:map_compat_raw_tp_w, ?tc:obj_type_id_oor, ?tc:obj_new_no_composite, ?tc:obj_new_no_struct, ?tc:obj_drop_non_zero_off, ?tc:new_null_ret, ?tc:obj_new_acq; plus 24 more`. Local functions/subprograms: `map_compat_kprobe, map_compat_kretprobe, map_compat_tp, map_compat_perf, map_compat_raw_tp, map_compat_raw_tp_w, obj_type_id_oor, obj_new_no_composite, obj_new_no_struct, obj_drop_non_zero_off, new_null_ret, obj_new_acq, use_after_drop, ptr_walk_scalar; plus 25 more`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_core_type_id_local, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_obj_new_impl, bpf_spin_lock, bpf_spin_unlock, bpf_this_cpu_ptr`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `?kprobe/xyz:map_compat_kprobe, ?kretprobe/xyz:map_compat_kretprobe, ?tracepoint/xyz:map_compat_tp, ?perf_event:map_compat_perf, ?raw_tp/xyz:map_compat_raw_tp, ?raw_tp.w/xyz:map_compat_raw_tp_w, ?tc:obj_type_id_oor, ?tc:obj_new_no_composite; plus 28 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of ?kprobe/xyz:map_compat_kprobe, ?kretprobe/xyz:map_compat_kretprobe, ?tracepoint/xyz:map_compat_tp, ?perf_event:map_compat_perf, ?raw_tp/xyz:map_compat_raw_tp, ?raw_tp.w/xyz:map_compat_raw_tp_w; plus 30 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c

Purpose: Positive list front/back peek test that exercises non-removing access under spin lock. The file has 114 source lines and 2310 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `syscall:list_peek`. Local functions/subprograms: `list_peek`. Maps: `none declared in this file`. Types: `node_data`. BPF helpers/kfuncs/macros used as calls: `bpf_jiffies64, bpf_list_back, bpf_list_front, bpf_list_push_back, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `syscall:list_peek`. Control flow is centered on critical sections protect intrusive container or resource-spin-lock state.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: libbpf verifier annotations __failure, __retval(0); successful attachment/execution of syscall:list_peek; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps1.c

Purpose: Cross-object map-linking test with one object declaring an extern map supplied by its companion. The file has 83 source lines and 1851 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG`. Maps: `map1`. Types: `my_key, my_value`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `map1` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: map2_t map2 SEC(".maps"). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c

Purpose: Companion map-linking object that supplies/uses maps across linked BPF objects. The file has 77 source lines and 1735 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG`. Maps: `map1, map2`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `map1, map2` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: struct {
	__uint(max_entries, 16). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c

Purpose: Cross-object global variable and weak kconfig/ksym resolution test. The file has 55 source lines and 1382 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int LINUX_KERNEL_VERSION __kconfig, bool CONFIG_BPF_SYSCALL __kconfig __weak, const void bpf_link_fops __ksym __weak, int input_bss2, int input_data2, const int input_rodata2. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars2.c

Purpose: Companion linked-variable test that resolves the opposite object's globals and strong kernel symbols. The file has 56 source lines and 1383 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int LINUX_KERNEL_VERSION __kconfig, bool CONFIG_BPF_SYSCALL __kconfig, const void __start_BTF __ksym, int input_bss1, int input_data1, const int input_rodata1. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c

Purpose: Fentry/fexit trampoline attachment smoke test for a function that can be affected by livepatch-style trampolines. The file has 31 source lines and 537 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c

Purpose: Cgroup skb program that validates `bpf_skb_load_bytes_relative` for network-header-relative packet reads. The file has 49 source lines and 1003 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:load_bytes_relative`. Local functions/subprograms: `load_bytes_relative`. Maps: `test_result`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_update_elem, bpf_skb_load_bytes_relative`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:load_bytes_relative`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `test_result` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:load_bytes_relative; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c

Purpose: Positive local kptr stash tests for rb-tree nodes, local roots, refcounted nodes, and map-stored kptr exchange. The file has 286 source lines and 5686 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash, tc:stash_refcounted_node`. Local functions/subprograms: `less, create_and_stash, stash_rb_nodes, stash_plain, stash_local_with_root, unstash_rb_node, stash_test_ref_kfunc, refcount_acquire_without_unstash, stash_refcounted_node`. Maps: `refcounted_node_stash, some_nodes`. Types: `plain_local, node_data, refcounted_node, stash, plain_local, local_with_root, map_value, node_data, refcounted_node`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash, tc:stash_refcounted_node`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: Persistent state is held in BPF maps `refcounted_node_stash, some_nodes` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c

Purpose: Negative local kptr stash cases for type mismatch and non-zero-offset release. The file has 86 source lines and 1843 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:stash_rb_nodes, tc:drop_rb_node_off`. Local functions/subprograms: `stash_rb_nodes, drop_rb_node_off`. Maps: `some_nodes`. Types: `node_data, map_value, node_data2, node_data`. BPF helpers/kfuncs/macros used as calls: `bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new`. Verifier messages asserted here: `invalid kptr access, R2 type=ptr_node_data2 expected=ptr_node_data, R1 must have zero offset when passed to release func`.

Control flow: Entry points are BPF programs in `tc:stash_rb_nodes, tc:drop_rb_node_off`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `some_nodes` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `invalid kptr access, R2 type=ptr_node_data2 expected=ptr_node_data, R1 must have zero offset when passed to release func`; successful attachment/execution of tc:stash_rb_nodes, tc:drop_rb_node_off; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c

Purpose: LSM programs exercising inode, socket, and task local storage get/delete paths across sleepable and non-sleepable hooks. The file has 214 source lines and 5083 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `inode_storage_map, sk_storage_map, sk_storage_map2, task_storage_map, task_storage_map2`. Types: `local_storage`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_inode_storage_delete, bpf_inode_storage_get, bpf_sk_storage_delete, bpf_sk_storage_get, bpf_task_storage_delete, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `inode_storage_map, sk_storage_map, sk_storage_map2, task_storage_map, task_storage_map2` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c

Purpose: Benchmark helper programs for map-in-map local-storage lookup loops and randomized task-storage access. The file has 105 source lines and 2324 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `do_lookup, loop, get_local`. Maps: `array_of_local_storage_maps, array_of_hash_maps`. Types: `loop_ctx`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_loop, bpf_map_lookup_elem, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `array_of_local_storage_maps, array_of_hash_maps` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c

Purpose: RCU Tasks Trace benchmark probes that create/delete task local storage and timestamp grace-period phases. The file has 68 source lines and 1424 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp`. Local functions/subprograms: `get_local, pregp_step, postgp`. Maps: `task_storage`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_ktime_get_ns, bpf_task_storage_delete, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `task_storage` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop1.c

Purpose: Bounded nested-loop verifier test attached to raw kfree_skb tracepoint. The file has 25 source lines and 443 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tracepoint/kfree_skb:nested_loops`. Local functions/subprograms: `nested_loops`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tracepoint/kfree_skb:nested_loops`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tracepoint/kfree_skb:nested_loops; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c

Purpose: While-true loop verifier test with an explicit internal break bound. The file has 25 source lines and 395 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tracepoint/consume_skb:while_true`. Local functions/subprograms: `while_true`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tracepoint/consume_skb:while_true`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tracepoint/consume_skb:while_true; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop3.c

Purpose: Alternate while-true loop verifier test over a smaller bound. The file has 19 source lines and 377 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tracepoint/consume_skb:while_true`. Local functions/subprograms: `while_true`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tracepoint/consume_skb:while_true`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tracepoint/consume_skb:while_true; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop4.c

Purpose: Socket program that explores nested branch/loop combinations for verifier state handling. The file has 21 source lines and 371 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `socket:combinations`. Local functions/subprograms: `combinations`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `socket:combinations`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of socket:combinations; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop5.c

Purpose: Socket while-loop verifier test with controlled increments and termination. The file has 32 source lines and 449 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `socket:while_true`. Local functions/subprograms: `while_true`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `socket:while_true`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of socket:while_true; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c

Purpose: Kprobe program that reads virtqueue scatter-gather arguments with bounded loops and kernel memory reads. The file has 96 source lines and 2110 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe/virtqueue_add_sgs:BPF_KPROBE`. Local functions/subprograms: `BPF_KPROBE`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_probe_read_kernel`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe/virtqueue_add_sgs:BPF_KPROBE`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of kprobe/virtqueue_add_sgs:BPF_KPROBE; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie.h

Purpose: Shared longest-prefix-match trie key definition for LPM trie map selftests. The file has 31 source lines and 534 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `none declared in this file`. Maps: `none declared in this file`. Types: `trie_key`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: This header has no runtime persistence; it defines shared structs, inline helpers, or map declarations consumed by companion BPF object files.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; LPM trie map implementation. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c

Purpose: LPM trie benchmark program measuring lookup/insert/update/delete loop costs and deferred map-free timing. The file has 231 source lines and 4565 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, generate_key, noop, baseline, lookup, insert, update, delete, BPF_PROG`. Maps: `trie_map`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_prandom_u32, bpf_ktime_get_ns, bpf_loop, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem, bpf_printk, bpf_strncmp`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `trie_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; LPM trie map implementation. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_map.c

Purpose: Standalone LPM trie map declaration used by map-free and benchmark selftests. The file has 20 source lines and 407 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `none declared in this file`. Maps: `trie_free_map`. Types: `trie_key`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `trie_free_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; LPM trie map implementation. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c

Purpose: LRU hash map regression program that updates/deletes across fentry hooks while tracking current task identity. The file has 50 source lines and 1007 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep`. Local functions/subprograms: `printk, nanosleep`. Maps: `lru_map`. Types: `map_value`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_ktime_get_ns, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `lru_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c

Purpose: BPF LSM selftest programs for map access and sleepable helper behavior in mprotect and credential hooks. The file has 184 source lines and 4051 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `array, hash, lru_hash, percpu_array, percpu_hash, lru_percpu_hash, inner_map, outer_arr, outer_hash`. Types: `inner_map, outer_arr, outer_hash`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_get_current_pid_tgid, bpf_map_lookup_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `array, hash, lru_hash, percpu_array, percpu_hash, lru_percpu_hash, inner_map, outer_arr, outer_hash` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c

Purpose: Block-device LSM test that stores verity device metadata and validates allocation/free/integrity hook behavior. The file has 97 source lines and 2586 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `verity_devices`. Types: `verity_info`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `verity_devices` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c

Purpose: Cgroup LSM programs for socket create/bind/storage behavior, getsockopt/setsockopt mediation, and security-module config gates. The file has 193 source lines and 4319 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG`. Local functions/subprograms: `test_local_storage, real_create, BPF_PROG, BPF_PROG, real_bind, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `cgroup_storage`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_local_storage, bpf_getsockopt, bpf_probe_read_kernel, bpf_setsockopt`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `cgroup_storage` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: bool CONFIG_SECURITY_SELINUX __kconfig __weak, bool CONFIG_SECURITY_SMACK __kconfig __weak, bool CONFIG_SECURITY_APPARMOR __kconfig __weak; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup_nonvoid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup_nonvoid.c

Purpose: Negative or edge LSM cgroup program for a non-void hook return contract. The file has 15 source lines and 347 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm_cgroup/inet_csk_clone:BPF_PROG`. Local functions/subprograms: `BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm_cgroup/inet_csk_clone:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of lsm_cgroup/inet_csk_clone:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup_nonvoid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c

Purpose: LSM tail-call test using a prog-array jump table across file and kernfs hooks. The file has 35 source lines and 685 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry`. Local functions/subprograms: `lsm_file_permission_prog, lsm_kernfs_init_security_prog, lsm_kernfs_init_security_entry`. Maps: `jmp_table`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_tail_call_static`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `jmp_table` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lwt_misc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lwt_misc.c

Purpose: Lightweight tunnel transmit verifier test for missing destination context with `bpf_lwt_push_encap`. The file has 23 source lines and 424 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lwt_xmit:test_missing_dst`. Local functions/subprograms: `test_missing_dst`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_lwt_push_encap`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lwt_xmit:test_missing_dst`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: libbpf verifier annotations __retval(0), __success; successful attachment/execution of lwt_xmit:test_missing_dst; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lwt_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_excl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_excl.c

Purpose: Map exclusive-access test with paired programs that should and should not update a restricted map. The file has 35 source lines and 706 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `should_have_access, should_not_have_access`. Maps: `excl_map`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `excl_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_excl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c

Purpose: Map-in-map BTF test that pushes allocated list nodes into an inner array map protected by spin lock. The file has 74 source lines and 1453 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `add_to_list_in_inner_array`. Maps: `inner_array, outer_array`. Types: `node_data, map_value, inner_array_type`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: Persistent state is held in BPF maps `inner_array, outer_array` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr.c

Purpose: Comprehensive positive kptr map/local-storage test for referenced/unreferenced kptrs, per-CPU maps, map-in-map, and local storage. The file has 559 source lines and 12922 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:test_map_kptr, tp_btf/cgroup_mkdir:BPF_PROG, lsm/inode_unlink:BPF_PROG, lsm/inode_unlink:BPF_PROG, tc:test_sk_map_kptr, tc:test_map_in_map_kptr, tc:test_map_kptr_ref1, tc:test_map_kptr_ref2, tc:test_map_kptr_ref3, syscall:count_ref, syscall:test_ls_map_kptr_ref1, syscall:test_ls_map_kptr_ref2; plus 1 more`. Local functions/subprograms: `test_kptr_unref, test_kptr_ref, test_kptr, test_map_kptr, BPF_PROG, BPF_PROG, BPF_PROG, test_sk_map_kptr, test_map_in_map_kptr, test_map_kptr_ref_pre, test_map_kptr_ref_post, test_map_kptr_ref1, test_map_kptr_ref2, test_map_kptr_ref3; plus 4 more`. Maps: `array_map, pcpu_array_map, hash_map, pcpu_hash_map, hash_malloc_map, pcpu_hash_malloc_map, lru_hash_map, lru_pcpu_hash_map, cgrp_ls_map, task_ls_map, inode_ls_map, sk_ls_map; plus 1 more`. Types: `map_value, array_map, pcpu_array_map, hash_map, pcpu_hash_map, hash_malloc_map, pcpu_hash_malloc_map, lru_hash_map, lru_pcpu_hash_map, cgrp_ls_map; plus 3 more`. BPF helpers/kfuncs/macros used as calls: `bpf_cgrp_storage_get, bpf_get_current_task_btf, bpf_inode_storage_get, bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_ref, bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_map_lookup_percpu_elem, bpf_map_update_elem, bpf_sk_storage_get, bpf_task_storage_delete, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:test_map_kptr, tp_btf/cgroup_mkdir:BPF_PROG, lsm/inode_unlink:BPF_PROG, lsm/inode_unlink:BPF_PROG, tc:test_sk_map_kptr, tc:test_map_in_map_kptr, tc:test_map_kptr_ref1, tc:test_map_kptr_ref2; plus 5 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: Persistent state is held in BPF maps `array_map, pcpu_array_map, hash_map, pcpu_hash_map, hash_malloc_map, pcpu_hash_malloc_map, lru_hash_map, lru_pcpu_hash_map, cgrp_ls_map, task_ls_map; plus 3 more` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:test_map_kptr, tp_btf/cgroup_mkdir:BPF_PROG, lsm/inode_unlink:BPF_PROG, lsm/inode_unlink:BPF_PROG, tc:test_sk_map_kptr, tc:test_map_in_map_kptr; plus 7 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_fail.c

Purpose: Negative verifier suite for kptr access size, alignment, offsets, trusted/untrusted type rules, helper indirection, and reference state. The file has 404 source lines and 7966 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?tc:size_not_bpf_dw, ?tc:non_const_var_off, ?tc:non_const_var_off_kptr_xchg, ?tc:misaligned_access_write, ?tc:misaligned_access_read, ?tc:reject_var_off_store, ?tc:reject_bad_type_match, ?tc:marked_as_untrusted_or_null, ?tc:correct_btf_id_check_size, ?tc:inherit_untrusted_on_walk, ?tc:reject_kptr_xchg_on_unref, ?tc:mark_ref_as_untrusted_or_null; plus 9 more`. Local functions/subprograms: `size_not_bpf_dw, non_const_var_off, non_const_var_off_kptr_xchg, misaligned_access_write, misaligned_access_read, reject_var_off_store, reject_bad_type_match, marked_as_untrusted_or_null, correct_btf_id_check_size, inherit_untrusted_on_walk, reject_kptr_xchg_on_unref, mark_ref_as_untrusted_or_null, reject_untrusted_store_to_ref, reject_untrusted_xchg; plus 8 more`. Maps: `array_map`. Types: `map_value, array_map`. BPF helpers/kfuncs/macros used as calls: `bpf_core_type_size, bpf_get_current_comm, bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_this_cpu_ptr`. Verifier messages asserted here: `kptr access size must be BPF_DW, kptr access cannot have variable offset, R1 doesn't have constant offset. kptr has to be, kptr access misaligned expected=8 off=7, kptr access misaligned expected=8 off=1, variable untrusted_ptr_ access var_off=(0x0; 0x1e0), invalid kptr access, R1 type=untrusted_ptr_prog_test_ref_kfunc, R1 type=untrusted_ptr_or_null_ expected=percpu_ptr_; plus 13 more`.

Control flow: Entry points are BPF programs in `?tc:size_not_bpf_dw, ?tc:non_const_var_off, ?tc:non_const_var_off_kptr_xchg, ?tc:misaligned_access_write, ?tc:misaligned_access_read, ?tc:reject_var_off_store, ?tc:reject_bad_type_match, ?tc:marked_as_untrusted_or_null; plus 13 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `array_map` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `kptr access size must be BPF_DW, kptr access cannot have variable offset, R1 doesn't have constant offset. kptr has to be, kptr access misaligned expected=8 off=7; plus 17 more`; successful attachment/execution of ?tc:size_not_bpf_dw, ?tc:non_const_var_off, ?tc:non_const_var_off_kptr_xchg, ?tc:misaligned_access_write, ?tc:misaligned_access_read, ?tc:reject_var_off_store; plus 15 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c

Purpose: Race/leak regression tests for map kptr deletion and map-free paths across hash, percpu hash, and sk storage maps. The file has 198 source lines and 4036 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG, syscall:count_ref`. Local functions/subprograms: `test_htab_leak, fill_percpu_kptr, test_percpu_htab_leak, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, count_ref`. Maps: `race_hash_map, race_percpu_hash_map, race_sk_ls_map`. Types: `map_value`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_lookup_percpu_elem, bpf_map_update_elem, bpf_sk_storage_delete, bpf_sk_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG, syscall:count_ref`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: Persistent state is held in BPF maps `race_hash_map, race_percpu_hash_map, race_sk_ls_map` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c

Purpose: BPF map iterator program that emits per-map element-count statistics with `bpf_map_sum_elem_count`. The file has 25 source lines and 528 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `iter/bpf_map:dump_bpf_map`. Local functions/subprograms: `dump_bpf_map`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_sum_elem_count`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `iter/bpf_map:dump_bpf_map`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of iter/bpf_map:dump_bpf_map; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c

Purpose: Kernel `struct bpf_map` pointer introspection test covering many map implementations and their type-specific fields. The file has 721 source lines and 17590 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:cg_skb`. Local functions/subprograms: `check_bpf_map_fields, check_bpf_map_ptr, check, check_default, check_hash, check_array, check_prog_array, check_perf_event_array, check_percpu_hash, check_percpu_array, check_stack_trace, check_cgroup_array, check_lru_hash, check_lru_percpu_hash; plus 17 more`. Maps: `m_hash, m_array, m_prog_array, m_perf_event_array, m_percpu_hash, m_percpu_array, m_stack_trace, m_cgroup_array, m_lru_hash, m_lru_percpu_hash, m_lpm_trie, inner_map; plus 15 more`. Types: `bpf_map_type, bpf_map, bpf_htab, bpf_array, bpf_stack_map, lpm_trie, lpm_key, inner_map, bpf_dtab, bpf_stab; plus 9 more`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem, bpf_map_sum_elem_count, bpf_map_update_elem, bpf_ringbuf_discard, bpf_ringbuf_reserve`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:cg_skb`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `m_hash, m_array, m_prog_array, m_perf_event_array, m_percpu_hash, m_percpu_array, m_stack_trace, m_cgroup_array, m_lru_hash, m_lru_percpu_hash; plus 17 more` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:cg_skb; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mem_rdonly_untrusted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mem_rdonly_untrusted.c

Purpose: Verifier suite for readonly untrusted memory returned by `bpf_rdonly_cast`, including read, write, atomic, helper, and kfunc constraints. The file has 230 source lines and 4116 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tp_btf/sys_enter:btf_id_to_ptr_mem, socket:ldx_is_ok_bad_addr, socket:ldx_is_ok_good_addr, socket:offset_not_tracked, socket:stx_not_ok, socket:atomic_not_ok, socket:atomic_rmw_not_ok, socket:kfunc_param_not_ok, socket:mixed_mem_type, socket:diff_size_access, socket:misaligned_access, socket:null_check`. Local functions/subprograms: `btf_id_to_ptr_mem, ldx_is_ok_bad_addr, ldx_is_ok_good_addr, offset_not_tracked, stx_not_ok, atomic_not_ok, atomic_rmw_not_ok, kfunc_param_not_ok, helper_param_not_ok, mixed_mem_type, combine, diff_size_access, misaligned_access, null_check`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_core_enum_value_exists, bpf_core_field_offset, bpf_core_type_id_kernel, bpf_for, bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_kfunc_trusted_num_test, bpf_rdonly_cast`. Verifier messages asserted here: `r8 = *(u64 *)(r7 +0)          ; R7=ptr_nameidata(imm={{[0-9]+}}) R8=rdonly_untrusted_mem(sz=0), r9 = *(u8 *)(r8 +0)           ; R8=rdonly_untrusted_mem(sz=0) R9=scalar, cannot write into rdonly_untrusted_mem, cannot write into rdonly_untrusted_mem, cannot write into rdonly_untrusted_mem, invalid access to memory, mem_size=0 off=0 size=4, R1 min value is outside of the allowed memory range, R1 type=rdonly_untrusted_mem expected=`.

Control flow: Entry points are BPF programs in `tp_btf/sys_enter:btf_id_to_ptr_mem, socket:ldx_is_ok_bad_addr, socket:ldx_is_ok_good_addr, socket:offset_not_tracked, socket:stx_not_ok, socket:atomic_not_ok, socket:atomic_rmw_not_ok, socket:kfunc_param_not_ok; plus 4 more`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; test kfunc calls validate argument typing, reference ownership, and module resolution; helper-mediated memory reads avoid direct unsafe kernel/user access; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: libbpf verifier annotations __failure, __retval(0), __retval(0x88442211), __retval(0x99553322), __retval(1), __success; expected verifier diagnostics such as `r8 = *(u64 *)(r7 +0)          ; R7=ptr_nameidata(imm={{[0-9]+}}) R8=rdonly_untrusted_mem(sz=0), r9 = *(u8 *)(r8 +0)           ; R8=rdonly_untrusted_mem(sz=0) R9=scalar, cannot write into rdonly_untrusted_mem, cannot write into rdonly_untrusted_mem; plus 4 more`; successful attachment/execution of tp_btf/sys_enter:btf_id_to_ptr_mem, socket:ldx_is_ok_bad_addr, socket:ldx_is_ok_good_addr, socket:offset_not_tracked, socket:stx_not_ok, socket:atomic_not_ok; plus 6 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mem_rdonly_untrusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_unused.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_unused.c

Purpose: Minimal cgroup skb program carrying metadata that is intentionally unused by generated skeleton tests. The file has 16 source lines and 321 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:prog`. Local functions/subprograms: `prog`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:prog`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:prog; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_unused.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_used.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_used.c

Purpose: Minimal cgroup skb program with metadata that is referenced by generated skeleton tests. The file has 16 source lines and 342 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:prog`. Local functions/subprograms: `prog`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:prog`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:prog; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/metadata_used.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe.c

Purpose: Missed-kprobe accounting test with fentry plus nested kprobe/kfunc-common invocations. The file has 31 source lines and 554 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2`. Local functions/subprograms: `BPF_PROG, test1, test2`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_common_test`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c

Purpose: Recursion/missed-probe test across kprobe.multi, kprobe.session, and regular kprobe attachments. The file has 55 source lines and 906 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5, kprobe.session/bpf_kfunc_common_test:test6`. Local functions/subprograms: `BPF_PROG, test1, test2, test3, test4, test5, test6`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_common_test`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5, kprobe.session/bpf_kfunc_common_test:test6`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c

Purpose: Tracepoint recursion test that combines fentry, kprobe, and tracepoint printk hooks. The file has 42 source lines and 673 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4`. Local functions/subprograms: `BPF_PROG, test1, test2, test3, test4`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_printk`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c

Purpose: Map-in-map mmapable inner-array access test for list/map layout constraints. The file has 58 source lines and 1196 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `add_to_list_in_inner_array`. Maps: `inner_array, outer_map`. Types: `inner_array_type`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_map_lookup_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `inner_array, outer_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/modify_return.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/modify_return.c

Purpose: Fentry/fmod_ret/fexit ordering test for functions whose return value can be modified by BPF. The file has 103 source lines and 2435 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, fmod_ret/bpf_modify_return_test:BPF_PROG, fexit/bpf_modify_return_test:BPF_PROG, fentry/bpf_modify_return_test2:BPF_PROG, fmod_ret/bpf_modify_return_test2:BPF_PROG, fexit/bpf_modify_return_test2:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, fmod_ret/bpf_modify_return_test:BPF_PROG, fexit/bpf_modify_return_test:BPF_PROG, fentry/bpf_modify_return_test2:BPF_PROG, fmod_ret/bpf_modify_return_test2:BPF_PROG, fexit/bpf_modify_return_test2:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, fmod_ret/bpf_modify_return_test:BPF_PROG, fexit/bpf_modify_return_test:BPF_PROG, fentry/bpf_modify_return_test2:BPF_PROG, fmod_ret/bpf_modify_return_test2:BPF_PROG, fexit/bpf_modify_return_test2:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/modify_return.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h

Purpose: Shared MPTCP helpers for list-head checks and conversion from MPTCP subflow context to TCP socket. The file has 43 source lines and 1244 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `list_is_head, mptcp_subflow_tcp_sock`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: This header has no runtime persistence; it defines shared structs, inline helpers, or map declarations consumed by companion BPF object files.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c

Purpose: MPTCP socket-storage and sockops/fentry test for MPTCP/TCP socket BTF conversions. The file has 89 source lines and 1894 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG`. Local functions/subprograms: `_sockops, BPF_PROG`. Maps: `socket_storage_map`. Types: `mptcp_storage`. BPF helpers/kfuncs/macros used as calls: `bpf_core_field_exists, bpf_sk_storage_get, bpf_skc_to_mptcp_sock, bpf_skc_to_tcp_sock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `socket_storage_map` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of sockops:_sockops, fentry/mptcp_pm_new_connection:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c

Purpose: MPTCP sockmap test that injects accepted sockets into a sockmap and redirects stream verdict traffic. The file has 44 source lines and 943 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect`. Local functions/subprograms: `mptcp_sockmap_inject, mptcp_sockmap_redirect`. Maps: `sock_map`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_sk_redirect_map, bpf_sock_map_update`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `sock_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of sockops:mptcp_sockmap_inject, sk_skb/stream_verdict:mptcp_sockmap_redirect; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_sockmap.c -->
