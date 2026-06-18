<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `cgroup_skb/ingress`, `license`
- Important functions/callbacks: `direct_packet_access`
- Mutable globals/test result fields: `data_end`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `data_end` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `data_end` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_skb_direct_packet_access.c -->
