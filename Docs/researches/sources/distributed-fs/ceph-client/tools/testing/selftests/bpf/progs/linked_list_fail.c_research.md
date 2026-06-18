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
