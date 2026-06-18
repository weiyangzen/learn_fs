<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c

## Purpose

Build-variant wrapper around pyperf.h that changes stack depth, unroll strategy, bpf_loop/iterator usage, or subprogram/global-function layout for verifier and compiler coverage.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: pyperf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/pyperf_global.c -->
