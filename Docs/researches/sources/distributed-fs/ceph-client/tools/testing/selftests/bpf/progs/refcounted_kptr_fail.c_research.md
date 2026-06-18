<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c

## Purpose

Negative companion for refcounted kptr ownership, covering leaked acquired references, maybe-NULL trusted args, and forbidden function calls while holding locks.

## Important APIs, Types, and Functions

Attach sections: ?tc, license. Map types: none. Important local functions/programs: less, rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG. Helper and kfunc calls: bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_acquire. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("Unreleased reference id=4 alloc_insn={{[0-9]+}}"), __msg("Possibly NULL pointer passed to trusted arg0"), __msg("Unreleased reference id=3 alloc_insn={{[0-9]+}}"), __msg("function calls are not allowed while holding a lock"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less` and related routines such as `rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include long key, long data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, license` programs, helper coverage for `bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less, rbtree_refcounted_node_ref_escapes, refcount_acquire_maybe_null, rbtree_refcounted_node_ref_escapes_owning_input, BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/refcounted_kptr_fail.c -->
