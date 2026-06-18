<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c

## Purpose

Benchmark comparing hand-written string comparison with bpf_strncmp helper on syscall tracepoints.

## Important APIs, Types, and Functions

Attach sections: license, tp/syscalls/sys_enter_getpgid. Map types: none. Important local functions/programs: local_strncmp, strncmp_no_helper, strncmp_helper. Helper and kfunc calls: bpf_strncmp. Important structs/types visible in this file: none. Includes: linux/types.h, linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `local_strncmp` and related routines such as `strncmp_no_helper, strncmp_helper`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include const char target[STRNCMP_STR_SZ], long hits, char str[STRNCMP_STR_SZ], int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, tp/syscalls/sys_enter_getpgid` programs, helper coverage for `bpf_strncmp`, and stable behavior of `local_strncmp, strncmp_no_helper, strncmp_helper` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_bench.c -->
