<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c

## Purpose

Large positive and mixed verifier suite for refcounted allocated nodes shared across rbtree, list, array kptr, and percpu hash map ownership paths.

## Important APIs, Types, and Functions

Attach sections: .maps, tc, license. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_HASH. Important local functions/programs: less, less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree, __read_from_list, __read_from_unstash, rbtree_refcounted_node_ref_escapes, rbtree_refcounted_node_ref_escapes_owning_input, __stash_map_empty_xchg, rbtree_wrong_owner_remove_fail_a1, rbtree_wrong_owner_remove_fail_b, rbtree_wrong_owner_remove_fail_a2, BPF_PROG, and 4 more. Helper and kfunc calls: bpf_kptr_xchg, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_probe_read_kernel, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, map_value, node_acquire. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __success, __retval(579), __retval(-1), __retval(84). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERCPU_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long key, long list_data, long data, long res, long val, int idx, u32 refcount, int key, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, tc, license` programs, helper coverage for `bpf_kptr_xchg, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_probe_read_kernel, and 8 more`, and stable behavior of `less, less_a, __insert_in_tree_and_list, __stash_map_insert_tree, __read_from_tree, __read_from_list, and 12 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr.c -->
