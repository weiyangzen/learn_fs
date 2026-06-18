<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`, `cgroup_skb/egress`, `.maps`, `.maps`, `cgroup/sock_create`, `license`
- Maps: `cgroup_storage`, `cgroup_storage_oob`, `lru_map`
- Important functions/callbacks: `bpf_prog`, `trigger_oob`
- BPF helpers/kfunc-like calls: `bpf_get_local_storage`, `bpf_long_memcpy`, `bpf_map_update_elem`, `bpf_obj_memcpy`, `bpf_prog`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `cgroup_storage`, `cgroup_storage_oob`, `lru_map` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `linux/bpf.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_local_storage`, `bpf_long_memcpy`, `bpf_map_update_elem`, `bpf_obj_memcpy`, `bpf_prog`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `cgroup_storage`, `cgroup_storage_oob`, `lru_map` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_storage.c -->
