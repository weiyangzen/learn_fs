<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c

## Purpose

Positive string kfunc test table comparing expected return values for strcmp, strcasecmp, strlen, strchr, strstr, strspn, and related bounded variants.

## Important APIs, Types, and Functions

Attach sections: syscall, license. Map types: none. Important local functions/programs: none. Helper and kfunc calls: bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, bpf_strncasestr, bpf_strnchr, bpf_strnlen, bpf_strnstr, bpf_strrchr, bpf_strspn, bpf_strstr. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf_misc.h, errno.h.

Verifier/test annotations present: __success, __retval(retval). These annotations are part of the executable selftest contract, not comments for documentation only.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

load-time verifier annotations should match the embedded __success/__failure/__retval/__msg expectations; the declared attach sections should load and attach in the owning selftest.
For this file specifically, useful signals include presence of `syscall, license` programs, helper coverage for `bpf_strcasecmp, bpf_strcasestr, bpf_strchr, bpf_strchrnul, bpf_strcmp, bpf_strcspn, bpf_strlen, bpf_strncasecmp, and 7 more`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/string_kfuncs_success.c -->
