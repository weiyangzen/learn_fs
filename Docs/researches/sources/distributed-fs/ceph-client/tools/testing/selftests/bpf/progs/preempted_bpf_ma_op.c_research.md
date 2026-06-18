<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c

## Purpose

Stress test for BPF memory allocator map operations under preemption by repeatedly deleting, allocating, and exchanging kptr array entries from fentry programs.

## Important APIs, Types, and Functions

Attach sections: .maps, license, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, fentry/bpf_fentry_test4. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: del_array, add_array, del_then_add_array, BPF_PROG2. Helper and kfunc calls: bpf_kptr_xchg, bpf_loop, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new. Important structs/types visible in this file: bin_data, map_value. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `del_array` and related routines such as `add_array, del_then_add_array, BPF_PROG2`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include char data[256], bool nomem_err, int i, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, license, fentry/bpf_fentry_test1, fentry/bpf_fentry_test2, fentry/bpf_fentry_test3, fentry/bpf_fentry_test4` programs, helper coverage for `bpf_kptr_xchg, bpf_loop, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new`, and stable behavior of `del_array, add_array, del_then_add_array, BPF_PROG2` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/preempted_bpf_ma_op.c -->
