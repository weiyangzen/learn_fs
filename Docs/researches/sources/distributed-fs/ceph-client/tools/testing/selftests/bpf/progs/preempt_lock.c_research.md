<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c

## Purpose

Verifier test matrix for bpf_preempt_disable/enable and guard-preempt regions, covering missing enables, subprogram balancing, and forbidden sleepable helpers or kfuncs while preemption is disabled.

## Important APIs, Types, and Functions

Attach sections: ?tc, ?syscall, license. Map types: none. Important local functions/programs: preempt_lock_missing_1, preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable, preempt_enable, preempt_lock_missing_1_subprog, preempt_lock_missing_2_subprog, preempt_lock_missing_2_minus_1_subprog, preempt_balance_subprog, preempt_sleepable_helper, preempt_sleepable_kfunc, preempt_global_subprog_test, preempt_global_sleepable_helper_subprog, and 2 more. Helper and kfunc calls: bpf_copy_from_user, bpf_copy_from_user_str, bpf_guard_preempt, bpf_preempt_disable, bpf_preempt_enable, bpf_printk. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __failure, __msg("BPF_EXIT instruction in main prog cannot be used inside bpf_preempt_disable-ed region"), __success, __msg("sleepable helper bpf_copy_from_user#"), __msg("kernel func bpf_copy_from_user_str is sleepable within non-preemptible region"), __msg("sleepable global function"). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `preempt_lock_missing_1` and related routines such as `preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include u32 data, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `?tc, ?syscall, license` programs, helper coverage for `bpf_copy_from_user, bpf_copy_from_user_str, bpf_guard_preempt, bpf_preempt_disable, bpf_preempt_enable, bpf_printk`, and stable behavior of `preempt_lock_missing_1, preempt_lock_missing_2, preempt_lock_missing_3, preempt_lock_missing_3_minus_2, preempt_disable, preempt_enable, and 10 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempt_lock.c -->
