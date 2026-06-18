<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c

## Purpose

bpf_strncmp correctness and verifier fixture, including valid comparisons plus bad size, writable target, and non-NUL-terminated cases.

## Important APIs, Types, and Functions

Attach sections: license, ?tp/syscalls/sys_enter_nanosleep. Map types: none. Important local functions/programs: do_strncmp, strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target. Helper and kfunc calls: bpf_get_current_pid_tgid, bpf_strncmp. Important structs/types visible in this file: none. Includes: stdbool.h, linux/types.h, linux/bpf.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `do_strncmp` and related routines such as `strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include const char target[STRNCMP_STR_SZ], char str[STRNCMP_STR_SZ], int cmp_ret, int target_pid, const char no_str_target[STRNCMP_STR_SZ], char writable_target[STRNCMP_STR_SZ], which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, ?tp/syscalls/sys_enter_nanosleep` programs, helper coverage for `bpf_get_current_pid_tgid, bpf_strncmp`, and stable behavior of `do_strncmp, strncmp_bad_not_const_str_size, strncmp_bad_writable_target, strncmp_bad_not_null_term_target` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strncmp_test.c -->
