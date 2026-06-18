<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h

## Purpose

Large reusable BPF profiler implementation covering kill, exec, fork, sysctl, file modification, cgroup metadata, filtering maps, perf output, and per-function stats.

## Important APIs, Types, and Functions

Attach sections: .maps, kprobe/proc_sys_write, tracepoint/syscalls/sys_enter_kill, raw_tracepoint/sched_process_exit, raw_tracepoint/sched_process_exec, kretprobe/do_file_open, kprobe/vfs_link, kprobe/vfs_symlink, raw_tracepoint/sched_process_fork, license. Map types: BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERF_EVENT_ARRAY. Important local functions/programs: IS_ERR, get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors, get_var_kill_data, trace_var_sys_kill, bpf_stats_enter, bpf_stats_exit, bpf_stats_pre_submit_var_perf_event, is_ancestor_in_allowed_inodes, is_dentry_allowed_for_filemod, tracepoint__syscalls__sys_enter_kill, raw_tracepoint__sched_process_exit, and 4 more. Helper and kfunc calls: bpf_cmp_likely, bpf_cmp_unlikely, bpf_core_enum_value, bpf_core_field_exists, bpf_core_read_str, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_current_uid_gid, bpf_get_smp_processor_id, bpf_ktime_get_ns, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem, bpf_nop_mov, bpf_perf_event_output, bpf_probe_read_kernel, bpf_probe_read_kernel_str, bpf_stats_enter, and 2 more. Important structs/types visible in this file: var_kill_data_arr_t, kernfs_iattrs___52, kernfs_node___52. Includes: vmlinux.h, bpf/bpf_core_read.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, profiler.h, err.h, bpf_experimental.h, bpf_compiler.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `IS_ERR` and related routines such as `get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERF_EVENT_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include u32 ino, u32 generation, u64 id, int cgrp_id, int subsys_id, u64 uid_gid, int zero, u32 spid, int index, u64 delta_sec, and 16 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, perf-event output userspace reader. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases. Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, kprobe/proc_sys_write, tracepoint/syscalls/sys_enter_kill, raw_tracepoint/sched_process_exit, raw_tracepoint/sched_process_exec, kretprobe/do_file_open, and 4 more` programs, helper coverage for `bpf_cmp_likely, bpf_cmp_unlikely, bpf_core_enum_value, bpf_core_field_exists, bpf_core_read_str, bpf_get_current_pid_tgid, bpf_get_current_task, bpf_get_current_uid_gid, and 12 more`, and stable behavior of `IS_ERR, get_userspace_pid, is_init_process, get_var_spid_index, populate_ancestors, get_var_kill_data, and 12 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.inc.h -->
