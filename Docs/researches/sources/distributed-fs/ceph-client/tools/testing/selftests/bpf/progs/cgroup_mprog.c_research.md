<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`, `cgroup/getsockopt`
- Important functions/callbacks: `getsockopt_1`, `getsockopt_2`, `getsockopt_3`, `getsockopt_4`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_mprog.c -->
