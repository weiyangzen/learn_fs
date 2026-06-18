<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c

## Purpose

Negative verifier suite for per-CPU allocated objects and kptrs, covering invalid drops, type mismatches, scalar misuse, and illegal stores to referenced per-CPU kptrs.

## Important APIs, Types, and Functions

Attach sections: .maps, ?fentry/bpf_fentry_test1, ?fentry.s/bpf_fentry_test1, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_this_cpu_ptr. Important structs/types visible in this file: val_t, val2_t, val_with_ptr_t, val_with_rb_root_t, val_600b_t, elem. Includes: bpf_experimental.h, bpf_misc.h.

Verifier/test annotations present: __failure, __msg("store to referenced kptr disallowed"), __msg("invalid kptr access, R2 type=percpu_ptr_val2_t expected=ptr_val_t"), __msg("R1 type=scalar expected=percpu_ptr_, percpu_rcu_ptr_, percpu_trusted_ptr_"), __msg("arg#0 expected for bpf_percpu_obj_drop()"), __msg("arg#0 expected for bpf_obj_drop()"), __msg("bpf_percpu_obj_new type ID argument must be of a struct of scalars"), __msg("bpf_percpu_obj_new type ID argument must not contain special fields"), and 1 more. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long b, char b[600], long sum, long ret, int index, which the harness may initialize, mutate, or read back through the BPF object data maps. Allocated BPF objects, refcounted pointers, or kptr exchanges introduce explicit ownership that must be dropped, transferred, or rejected by the verifier.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

This is intentionally verifier-sensitive; expected error strings are part of the test contract and can change with verifier diagnostics.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, ?fentry/bpf_fentry_test1, ?fentry.s/bpf_fentry_test1, license` programs, helper coverage for `bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_percpu_obj_drop, bpf_percpu_obj_new, bpf_this_cpu_ptr`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/percpu_alloc_fail.c -->
