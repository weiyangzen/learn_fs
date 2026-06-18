<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.data.query`, `iter.s/cgroup`
- Important functions/callbacks: `cgroup_memcg_query`
- BPF helpers/kfunc-like calls: `bpf_core_enum_value`, `bpf_get_mem_cgroup`, `bpf_mem_cgroup_flush_stats`, `bpf_mem_cgroup_page_state`, `bpf_mem_cgroup_vm_events`, `bpf_put_mem_cgroup`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

No explicit BPF maps are declared; state is mostly hook context, kernel object fields, or transient stack variables. Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_core_read.h`, `cgroup_iter_memcg.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_core_enum_value`, `bpf_get_mem_cgroup`, `bpf_mem_cgroup_flush_stats`, `bpf_mem_cgroup_page_state`, `bpf_mem_cgroup_vm_events`, `bpf_put_mem_cgroup`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_iter_memcg.c -->
