<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c

## Purpose

Exercises per-CPU object allocation through array maps and cgroup local storage, including this-CPU and arbitrary-CPU access under RCU and kptr exchange cleanup.

## Important APIs, Types, and Functions

Attach sections: .maps, ?fentry/bpf_fentry_test1, ?fentry/bpf_fentry_test2, ?fentry/bpf_fentry_test3, ?fentry/bpf_fentry_test4, ?fentry.s/bpf_fentry_test1, cgroup_skb/egress, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE. Important local functions/programs: bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, cgroup_egress. Helper and kfunc calls: bpf_for, bpf_get_current_pid_tgid, bpf_get_local_storage, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_map_update_elem, bpf_per_cpu_ptr, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_this_cpu_ptr. Important structs/types visible in this file: val_t, elem. Includes: bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_rcu_read_lock` and related routines such as `bpf_rcu_read_unlock, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long sum, int index, int my_pid, u64 value, int key, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, ?fentry/bpf_fentry_test1, ?fentry/bpf_fentry_test2, ?fentry/bpf_fentry_test3, ?fentry/bpf_fentry_test4, ?fentry.s/bpf_fentry_test1, and 2 more` programs, helper coverage for `bpf_for, bpf_get_current_pid_tgid, bpf_get_local_storage, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_map_update_elem, bpf_per_cpu_ptr, bpf_percpu_obj_drop, and 4 more`, and stable behavior of `bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, cgroup_egress` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_array.c -->
