<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c

## Purpose

Positive verifier companion for nested trusted-pointer propagation through task and socket-storage paths, proving that accepted trusted sources can be passed to cpumask helpers.

## Important APIs, Types, and Functions

Attach sections: license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe. Map types: BPF_MAP_TYPE_SK_STORAGE. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cpumask_first_zero, bpf_cpumask_test_cpu, bpf_sk_storage_get. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf_misc.h, nested_trust_common.h.

Verifier/test annotations present: __success. These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_SK_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, tp_btf/task_newtask, tp_btf/tcp_probe` programs, helper coverage for `bpf_cpumask_first_zero, bpf_cpumask_test_cpu, bpf_sk_storage_get`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_success.c -->
