<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c

## Purpose

Counts cgroup skb traffic in cgroup local storage and per-CPU cgroup storage, using a small next-counter helper to update packet and byte totals with timestamps.

## Important APIs, Types, and Functions

Attach sections: .maps, cgroup/skb, license. Map types: BPF_MAP_TYPE_CGROUP_STORAGE, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE. Important local functions/programs: bpf_nextcnt. Helper and kfunc calls: bpf_get_local_storage, bpf_ktime_get_ns, bpf_nextcnt. Important structs/types visible in this file: none. Includes: linux/bpf.h, linux/version.h, bpf/bpf_helpers.h, netcnt_common.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `bpf_nextcnt`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_CGROUP_STORAGE, BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, cgroup/skb, license` programs, helper coverage for `bpf_get_local_storage, bpf_ktime_get_ns, bpf_nextcnt`, and stable behavior of `bpf_nextcnt` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/netcnt_prog.c -->
