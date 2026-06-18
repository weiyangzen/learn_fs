<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`
- Maps: `cgroup_storage`
- Important functions/callbacks: `egress`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`
- Mutable globals/test result fields: `invocations`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage` Globals are used as userspace-visible configuration/results: `invocations` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `linux/bpf.h`, `linux/ip.h`, `linux/udp.h`, `bpf/bpf_helpers.h`, `progs/cg_storage_multi.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `invocations` to confirm the exercised path ran. Map contents/counts for `cgroup_storage` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cg_storage_multi_egress_only.c -->
