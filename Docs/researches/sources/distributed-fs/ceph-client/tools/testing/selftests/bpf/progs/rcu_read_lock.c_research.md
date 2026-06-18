<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c

## Purpose

Comprehensive verifier matrix for explicit bpf_rcu_read_lock/unlock, task/cgroup/key kfunc usage, sleepable versus non-sleepable contexts, subprogram balance, and RCU pointer trust.

## Important APIs, Types, and Functions

Attach sections: license, .maps, ?lsm.s/bpf. Map types: BPF_MAP_TYPE_TASK_STORAGE. Important local functions/programs: bpf_key_put, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id, task_succ, no_lock, two_regions, non_sleepable_1, non_sleepable_2, task_acquire, miss_lock, miss_unlock, non_sleepable_rcu_mismatch, and 23 more. Helper and kfunc calls: bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_get_current_cgroup_id, bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_key_put, bpf_lookup_user_key, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_acquire, bpf_task_pt_regs, bpf_task_release, bpf_task_storage_get. Important structs/types visible in this file: bpf_key, task_struct. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_tracing_net.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_key_put` and related routines such as `bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_TASK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __s32 key_serial, long init_val, __u32 value, volatile int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, ?lsm.s/bpf` programs, helper coverage for `bpf_copy_from_user, bpf_copy_from_user_str, bpf_copy_from_user_task, bpf_get_current_cgroup_id, bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_key_put, bpf_lookup_user_key, and 6 more`, and stable behavior of `bpf_key_put, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_task_release, get_cgroup_id, task_succ, and 31 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rcu_read_lock.c -->
