<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c

## Purpose

Uses an fmod_ret hook on update_socket_protocol to turn socket protocol selection into IPPROTO_MPTCP for the target PID, providing the minimal BPF side of the mptcpify selftest.

## Important APIs, Types, and Functions

Attach sections: license, fmod_ret/update_socket_protocol. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_get_current_pid_tgid. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf_tracing_net.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int pid, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, fmod_ret/update_socket_protocol` programs, helper coverage for `bpf_get_current_pid_tgid`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcpify.c -->
