<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c

## Purpose

cgroup sendmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields and including deny variants for policy tests.

## Important APIs, Types, and Functions

Attach sections: cgroup/sendmsg6, license. Map types: none. Important local functions/programs: sendmsg_v6_prog, sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog. Helper and kfunc calls: bpf_htonl, bpf_htons. Important structs/types visible in this file: none. Includes: linux/stddef.h, linux/bpf.h, sys/socket.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_sockopt_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sendmsg_v6_prog` and related routines such as `sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

The file has little or no persistent BPF map state; observable state is primarily return values, verifier acceptance/rejection, emitted events, or kernel side effects in the attach context.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/sendmsg6, license` programs, helper coverage for `bpf_htonl, bpf_htons`, and stable behavior of `sendmsg_v6_prog, sendmsg_v6_v4mapped_prog, sendmsg_v6_wildcard_prog, sendmsg_v6_preserve_dst_prog, sendmsg_v6_deny_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sendmsg6_prog.c -->
