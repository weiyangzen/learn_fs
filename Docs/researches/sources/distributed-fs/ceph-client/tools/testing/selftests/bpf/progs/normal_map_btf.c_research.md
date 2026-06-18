<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c

## Purpose

Validates that a normal array map value with BTF-described spin lock and list head can own allocated list nodes through bpf_obj_new and bpf_list_push_back.

## Important APIs, Types, and Functions

Attach sections: .maps, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: add_to_list_in_array. Helper and kfunc calls: bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, map_value. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `add_to_list_in_array`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u64 data, int pid, bool done, int zero, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, license` programs, helper coverage for `bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `add_to_list_in_array` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/normal_map_btf.c -->
