<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h

## Purpose

Shared inline helper for nested-trust tests; it deliberately calls cpumask helpers through a nested pointer expression so success and failure files can exercise verifier trust propagation.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: bpf_cpumask_test_cpu. Helper and kfunc calls: bpf_cpumask_first_zero, bpf_cpumask_test_cpu. Important structs/types visible in this file: none. Includes: stdbool.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_cpumask_test_cpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `bpf_cpumask_first_zero, bpf_cpumask_test_cpu`, and stable behavior of `bpf_cpumask_test_cpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/nested_trust_common.h -->
