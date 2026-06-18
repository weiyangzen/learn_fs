<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c

## Purpose

BTF negative test proving bpf_rbtree_add rejects a node/container type that does not match the root __contains declaration.

## Important APIs, Types, and Functions

Attach sections: tc, license. Map types: none. Important local functions/programs: less2, rbtree_api_add__add_wrong_type. Helper and kfunc calls: bpf_obj_new, bpf_rbtree_add, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data, node_data2. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less2` and related routines such as `rbtree_api_add__add_wrong_type`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int key, int data, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `tc, license` programs, helper coverage for `bpf_obj_new, bpf_rbtree_add, bpf_spin_lock, bpf_spin_unlock`, and stable behavior of `less2, rbtree_api_add__add_wrong_type` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_btf_fail__add_wrong_type.c -->
