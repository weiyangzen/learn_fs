<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c

## Purpose

Broad sockopt selftest program for LSM cgroup socket creation, cgroup getsockopt, and sockops callbacks across SOL_SOCKET, IP, IPv6, TCP, bind-to-device, MSS, and saved SYN options.

## Important APIs, Types, and Functions

Attach sections: lsm_cgroup/socket_post_create, cgroup/getsockopt, sockops, license. Map types: none. Important local functions/programs: sk_is_tcp, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, bpf_test_tcp_sockopt, bpf_test_sockopt, binddev_test, test_tcp_maxseg, test_tcp_saved_syn, BPF_PROG, _getsockopt, skops_sockopt. Helper and kfunc calls: bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_setsockopt, bpf_skc_to_tcp_sock, bpf_strncmp, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, bpf_test_socket_sockopt, bpf_test_sockopt, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_tcp_sockopt. Important structs/types visible in this file: sockopt_test, loop_ctx. Includes: vmlinux.h, bpf_tracing_net.h, bpf/bpf_core_read.h, bpf/bpf_helpers.h, bpf/bpf_tracing.h, bpf_misc.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `sk_is_tcp` and related routines such as `bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include int nr_listen, int nr_passive, int nr_active, int nr_connect, int nr_binddev, int nr_socket_post_create, int nr_fin_wait1, int opt, int new, int restore, and 8 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `lsm_cgroup/socket_post_create, cgroup/getsockopt, sockops, license` programs, helper coverage for `bpf_core_cast, bpf_getsockopt, bpf_loop, bpf_setsockopt, bpf_skc_to_tcp_sock, bpf_strncmp, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, and 5 more`, and stable behavior of `sk_is_tcp, bpf_test_sockopt_flip, bpf_test_sockopt_int, bpf_test_socket_sockopt, bpf_test_ip_sockopt, bpf_test_ipv6_sockopt, and 8 more` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/setget_sockopt.c -->
