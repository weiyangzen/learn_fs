<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `lsm.s/socket_connect`, `lsm/socket_connect`, `lsm/socket_connect`, `lsm.s/socket_connect`, `lsm.s/socket_connect`, `lsm/socket_connect`, `cgroup/sendmsg4`
- Important functions/callbacks: `read_xattr`, `BPF_PROG`, `trusted_cgroup_ptr_sleepable`, `trusted_cgroup_ptr_non_sleepable`, `use_css_iter_non_sleepable`, `use_css_iter_sleepable_missing_rcu_lock`, `use_css_iter_sleepable_with_rcu_lock`, `use_bpf_cgroup_ancestor`, `cgroup_skb`
- BPF helpers/kfunc-like calls: `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_read_xattr`, `bpf_cgroup_release`, `bpf_dynptr_from_mem`, `bpf_for_each`, `bpf_get_current_cgroup_id`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`
- Mutable globals/test result fields: `value[16]`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `value[16]` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`, `bpf_experimental.h`, `bpf_misc.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_read_xattr`, `bpf_cgroup_release`, `bpf_dynptr_from_mem`, `bpf_for_each`, `bpf_get_current_cgroup_id`, `bpf_rcu_read_lock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `value[16]` to confirm the exercised path ran. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_read_xattr.c -->
