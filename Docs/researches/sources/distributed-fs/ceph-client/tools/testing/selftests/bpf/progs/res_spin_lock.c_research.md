<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c

## Purpose

Positive resilient spin-lock tests for map-value and global locks, lock ordering, same-lock try behavior, and held-lock capacity.

## Important APIs, Types, and Functions

Attach sections: .maps, .data.A, .data.B, tc, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: res_spin_lock_test, res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max. Helper and kfunc calls: bpf_ktime_get_ns, bpf_map_lookup_elem, bpf_res_spin_lock, bpf_res_spin_unlock. Important structs/types visible in this file: arr_elem, bpf_res_spin_lock. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `res_spin_lock_test` and related routines such as `res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int r, int err, int ret, int key, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, .data.A, .data.B, tc, license` programs, helper coverage for `bpf_ktime_get_ns, bpf_map_lookup_elem, bpf_res_spin_lock, bpf_res_spin_unlock`, and stable behavior of `res_spin_lock_test, res_spin_lock_test_AB, res_spin_lock_test_BA, res_spin_lock_test_held_lock_max` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/res_spin_lock.c -->
