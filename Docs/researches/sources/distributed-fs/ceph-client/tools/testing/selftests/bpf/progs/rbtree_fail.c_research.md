<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c

## Purpose

Negative rbtree verifier suite covering missing locks, unreleased references, double insertion, unchecked remove results, escaped release-on-unlock references, and illegal callback calls.

## Important APIs, Types, and Functions

Attach sections: ?tc, license. Map types: none. Important local functions/programs: less, rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node, rbtree_api_remove_no_drop, rbtree_api_add_to_multiple_trees, rbtree_api_use_unchecked_remove_retval, rbtree_api_add_release_unlock_escape, rbtree_api_first_release_unlock_escape, less__bad_fn_call_add, less__bad_fn_call_remove, less__bad_fn_call_first_unlock_after, add_with_cb, and 3 more. Helper and kfunc calls: bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("bpf_spin_lock at off=16 must be held for bpf_rb_root"), __retval(0), __msg("Unreleased reference id=3 alloc_insn={{[0-9]+}}"), __msg("arg#1 expected pointer to allocated object"), __msg("Possibly NULL pointer passed to trusted arg1"), __msg("bpf_rbtree_remove can only take non-owning or refcounted bpf_rb_node pointer"), __msg("rbtree_remove not allowed in rbtree cb"), and 1 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include long key, long data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, license` programs, helper coverage for `bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_first, bpf_rbtree_remove, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less, rbtree_api_nolock_add, rbtree_api_nolock_remove, rbtree_api_nolock_first, rbtree_api_remove_unadded_node, rbtree_api_remove_no_drop, and 11 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_fail.c -->
