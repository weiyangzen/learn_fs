<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c

## Purpose

Socket destroy test that records target cookies, finds sockets from connect/iterator contexts, and calls bpf_sock_destroy on matching TCP/UDP IPv6 sockets.

## Important APIs, Types, and Functions

Attach sections: .maps, cgroup/connect6, iter/tcp, iter/udp, license. Map types: BPF_MAP_TYPE_ARRAY. Important local functions/programs: bpf_sock_destroy, sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client, iter_udp6_server. Helper and kfunc calls: bpf_get_socket_cookie, bpf_map_lookup_elem, bpf_map_update_elem, bpf_skc_to_tcp6_sock, bpf_sock_destroy. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h, bpf/bpf_endian.h, bpf_tracing_net.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_sock_destroy` and related routines such as `sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u64 sock_cookie, int key, __u32 keyc, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, cgroup/connect6, iter/tcp, iter/udp, license` programs, helper coverage for `bpf_get_socket_cookie, bpf_map_lookup_elem, bpf_map_update_elem, bpf_skc_to_tcp6_sock, bpf_sock_destroy`, and stable behavior of `bpf_sock_destroy, sock_connect, iter_tcp6_client, iter_tcp6_server, iter_udp6_client, iter_udp6_server` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/sock_destroy_prog.c -->
