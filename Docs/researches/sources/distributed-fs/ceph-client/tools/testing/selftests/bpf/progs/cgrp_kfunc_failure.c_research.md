<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `kretprobe/cgroup_destroy_locked`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`, `tp_btf/cgroup_mkdir`
- Important functions/callbacks: `BPF_PROG`, `cgrp_kfunc_acquire_untrusted`, `cgrp_kfunc_acquire_no_null_check`, `cgrp_kfunc_acquire_fp`, `cgrp_kfunc_acquire_unsafe_kretprobe`, `cgrp_kfunc_acquire_trusted_walked`, `cgrp_kfunc_acquire_null`, `cgrp_kfunc_acquire_unreleased`, `cgrp_kfunc_xchg_unreleased`, `cgrp_kfunc_rcu_get_release`, `cgrp_kfunc_release_untrusted`, `cgrp_kfunc_release_fp`, `cgrp_kfunc_release_null`, `cgrp_kfunc_release_unacquired`
- BPF helpers/kfunc-like calls: `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`, `cgrp_kfunc_common.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_kfunc_failure.c -->
