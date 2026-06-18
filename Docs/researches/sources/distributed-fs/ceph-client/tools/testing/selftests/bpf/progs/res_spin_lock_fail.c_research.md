<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c

## Purpose

Negative resilient spin-lock matrix for bad arguments, AA deadlock, mismatched unlocks, IRQ-save pairing errors, out-of-order unlock, and invalid lock offsets.

## Important APIs, Types, and Functions

Attach sections: .maps, .data.A, .data.B, ?tc, .data.OO1, .data.OO2, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: res_spin_lock_arg, res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2, res_spin_lock_irq_mismatch_1, res_spin_lock_irq_mismatch_2, res_spin_lock_ooo, res_spin_lock_ooo_irq, res_spin_lock_ooo_unlock, res_spin_lock_bad_off, res_spin_lock_var_off, res_spin_lock_no_lock_map, res_spin_lock_no_lock_kptr. Helper and kfunc calls: bpf_assert_range, bpf_core_cast, bpf_local_irq_save, bpf_map_lookup_elem, bpf_obj_new, bpf_res_spin_lock, bpf_res_spin_lock_irqsave, bpf_res_spin_unlock, bpf_res_spin_unlock_irqrestore, bpf_throw. Important structs/types visible in this file: arr_elem, bpf_spin_lock, bpf_res_spin_lock. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __failure, __msg("point to map value or allocated object"), __msg("AA deadlock detected"), __msg("unlock of different lock"), __success, __msg("bpf_res_spin_unlock cannot be out of order"), __msg("off 1 doesn't point to 'struct bpf_res_spin_lock' that is at 0"), __msg("R1 doesn't have constant offset. bpf_res_spin_lock has to be at the constant offset"), and 2 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `res_spin_lock_arg` and related routines such as `res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long value, u64 val, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, .data.A, .data.B, ?tc, .data.OO1, .data.OO2, and 1 more` programs, helper coverage for `bpf_assert_range, bpf_core_cast, bpf_local_irq_save, bpf_map_lookup_elem, bpf_obj_new, bpf_res_spin_lock, bpf_res_spin_lock_irqsave, bpf_res_spin_unlock, and 2 more`, and stable behavior of `res_spin_lock_arg, res_spin_lock_AA, res_spin_lock_cond_AA, res_spin_lock_mismatch_1, res_spin_lock_mismatch_2, res_spin_lock_irq_mismatch_1, and 8 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock_fail.c -->
