<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c

## Purpose

Search-oriented rbtree test that builds two trees over refcounted nodes, traverses root/left/right links, removes nodes, and checks lock requirements for search helpers.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: less0, less1, rbtree_search. Helper and kfunc calls: bpf_jiffies64, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, bpf_rbtree_root, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock. Important structs/types visible in this file: node_data. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h, bpf_experimental.h.

Verifier/test annotations present: __retval(0), __failure. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `less0` and related routines such as `less1, rbtree_search`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int key0, int key1, int zero, long lookup_key, __u64 jiffies, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics. Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_jiffies64, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_rbtree_left, bpf_rbtree_remove, bpf_rbtree_right, bpf_rbtree_root, and 3 more`, and stable behavior of `less0, less1, rbtree_search` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/rbtree_search.c -->
