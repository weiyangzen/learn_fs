<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c

## Purpose

Socket iterator batch test for TCP/UDP sockets that writes loopback reuse data and can destroy sockets matching iterator criteria.

## Important APIs, Types, and Functions

Attach sections: iter/tcp, iter/udp, license. Map types: none. Important local functions/programs: ipv6_addr_loopback, ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse. Helper and kfunc calls: bpf_core_cast, bpf_get_socket_cookie, bpf_htonl, bpf_ntohl, bpf_seq_write, bpf_sock_destroy. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf/bpf_endian.h, bpf_tracing_net.h, bpf_kfuncs.h, test_jhash.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `ipv6_addr_loopback` and related routines such as `ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include volatile const __u16 ports[2], __u64 sock_cookie, int idx, volatile const __u64 destroy_cookie, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `iter/tcp, iter/udp, license` programs, helper coverage for `bpf_core_cast, bpf_get_socket_cookie, bpf_htonl, bpf_ntohl, bpf_seq_write, bpf_sock_destroy`, and stable behavior of `ipv6_addr_loopback, ipv4_addr_loopback, iter_tcp_soreuse, iter_tcp_destroy, iter_udp_soreuse` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_iter_batch.c -->
