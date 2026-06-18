<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c

## Purpose

Cgroup/BPF selftest program covering cgroup hooks, cgroup storage, local storage, cgroup iterators, cgroup kfunc references, or socket packet validation.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `.maps`, `tp_btf/cgroup_attach_task`, `fentry/bpf_rstat_flush`, `iter.s/cgroup`
- Maps: `percpu_attach_counters`, `attach_counters`
- Important functions/callbacks: `create_percpu_attach_counter`, `create_attach_counter`, `BPF_PROG`, `counter`, `flusher`, `dumper`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_lookup_percpu_elem`, `bpf_map_update_elem`

## Control Flow and Data Flow

Control enters from cgroup, tracepoint, iterator, LSM, or fentry hooks. Programs read hook context, socket/cgroup/task objects, sometimes allocate/acquire cgroup references, update maps/local storage/globals, and return pass/fail or hook-specific status.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `percpu_attach_counters`, `attach_counters` Cgroup/local/task/sk storage persists per owning object and must be released or overwritten according to helper ownership rules.

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`. Integrates with cgroup hook attachment, cgroup storage/local-storage maps, cgroup kfuncs, socket/cgroup iterators, and userspace selftest drivers.

## Risks and Edge Cases

Cgroup refcount/local-storage tests are ownership-sensitive; missing release, invalid RCU lifetime, or wrong hook return values are the main failure modes. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_map_lookup_percpu_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `percpu_attach_counters`, `attach_counters` provide state validation. Cgroup selftests should drive the hook with controlled sockets/cgroups and verify storage, retval, packet-count, or refcount observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgroup_hierarchical_stats.c -->
