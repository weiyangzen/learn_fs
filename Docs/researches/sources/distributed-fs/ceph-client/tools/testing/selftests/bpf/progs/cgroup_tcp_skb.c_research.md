<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`, `cgroup_skb/egress`, `cgroup_skb/ingress`
- Important functions/callbacks: `needed_tcp_pkt`, `egress_accept`, `ingress_accept`, `egress_connect`, `ingress_connect`, `egress_close_remote`, `ingress_close_remote`, `egress_close_local`, `ingress_close_local`, `server_egress`, `server_ingress`, `server_egress_srv`, `server_ingress_srv`, `client_egress_srv`, `client_ingress_srv`, `client_egress`, `client_ingress`
- BPF helpers/kfunc-like calls: `bpf_htons`, `bpf_skb_load_bytes`
- Mutable globals/test result fields: `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/if_ether.h`, `linux/in.h`, `linux/in6.h`, `linux/ipv6.h`, `linux/tcp.h`, `sys/types.h`, `sys/socket.h`, `cgroup_tcp_skb.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_htons`, `bpf_skb_load_bytes`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g_sock_port`, `g_sock_state`, `g_unexpected`, `g_packet_count` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_tcp_skb.c -->
