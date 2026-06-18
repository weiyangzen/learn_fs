<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c

## Purpose

cgroup recvmsg address-rewrite fixture for IPv4, IPv6, or Unix sockets, mutating destination address fields or Unix path and returning allow/deny status.

## Important APIs, Types, and Functions

Attach sections: cgroup/recvmsg_unix, license. Map types: none. Important local functions/programs: recvmsg_unix_prog. Helper and kfunc calls: bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path. Important structs/types visible in this file: none. Includes: vmlinux.h, string.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_kfuncs.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `recvmsg_unix_prog`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include __u32 unaddrlen, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `cgroup/recvmsg_unix, license` programs, helper coverage for `bpf_cast_to_kern_ctx, bpf_core_cast, bpf_sock_addr_set_sun_path`, and stable behavior of `recvmsg_unix_prog` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/recvmsg_unix_prog.c -->
