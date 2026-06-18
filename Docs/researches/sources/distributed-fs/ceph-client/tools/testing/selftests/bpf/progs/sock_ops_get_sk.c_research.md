<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c

## Purpose

Sockops context fixture exercising direct access to sk fields in multiple sockops programs.

## Important APIs, Types, and Functions

Attach sections: sockops, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Global data variables include int bug_detected, int null_seen, int field_bug_detected, int field_null_seen, int diff_reg_bug_detected, int diff_reg_null_seen, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `sockops, license` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_ops_get_sk.c -->
