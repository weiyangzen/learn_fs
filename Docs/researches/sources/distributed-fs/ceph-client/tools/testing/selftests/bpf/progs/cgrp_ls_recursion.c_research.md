<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `fentry/bpf_local_storage_update`, `tp_btf/sys_enter`
- Maps: `map_a`, `map_b`
- Important functions/callbacks: `__on_update`, `BPF_PROG`, `__on_enter`, `on_update`, `on_enter`
- BPF helpers/kfunc-like calls: `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`
- Mutable globals/test result fields: `target_hid`, `is_cgroup1`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map_a`, `map_b` Globals are used as userspace-visible configuration/results: `target_hid`, `is_cgroup1` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `target_hid`, `is_cgroup1` to confirm the exercised path ran. Map contents/counts for `map_a`, `map_b` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_recursion.c -->
