<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `syscall`
- Important functions/callbacks: `is_test_kfunc_task`, `BPF_PROG`, `test_cgrp_from_id_ns`, `test_cgrp_acquire_release_argument`, `test_cgrp_acquire_leave_in_map`, `test_cgrp_xchg_release`, `test_cgrp_get_release`, `test_cgrp_get_ancestors`, `test_cgrp_from_id`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `cgrp_kfunc_common.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_success.c -->
