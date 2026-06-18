<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `.maps`
- Maps: `__cgrps_kfunc_map`
- Important functions/callbacks: `cgrps_kfunc_map_insert`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `__cgrps_kfunc_map` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `errno.h`, `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `__cgrps_kfunc_map` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_common.h -->
