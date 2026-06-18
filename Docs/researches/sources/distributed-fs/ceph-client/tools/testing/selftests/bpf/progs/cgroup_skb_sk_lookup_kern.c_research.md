<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup_skb/ingress`
- Important functions/callbacks: `set_ip`, `set_tuple`, `is_allowed_peer_cg`, `ingress_lookup`
- BPF helpers/kfunc-like calls: `bpf_htons`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_cgroup_id`, `bpf_sk_lookup_tcp`, `bpf_sk_release`, `bpf_skb_ancestor_cgroup_id`, `bpf_skb_cgroup_id`, `bpf_skb_load_bytes`
- Mutable globals/test result fields: `g_serv_port`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `g_serv_port` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/if_ether.h`, `linux/in.h`, `linux/in6.h`, `linux/ipv6.h`, `linux/tcp.h`, `sys/types.h`, `sys/socket.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_htons`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_cgroup_id`, `bpf_sk_lookup_tcp`, `bpf_sk_release`, `bpf_skb_ancestor_cgroup_id`, `bpf_skb_cgroup_id`, `bpf_skb_load_bytes`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `g_serv_port` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_sk_lookup_kern.c -->
