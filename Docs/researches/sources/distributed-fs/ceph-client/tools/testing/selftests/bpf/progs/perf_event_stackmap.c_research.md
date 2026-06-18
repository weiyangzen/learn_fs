<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c

## Purpose

Perf-event program that samples stack IDs and raw stacks into stack-trace/per-CPU maps, used to validate stack helpers from perf_event context.

## Important APIs, Types, and Functions

Attach sections: .maps, perf_event, license. Map types: BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_STACK_TRACE. Important local functions/programs: oncpu. Helper and kfunc calls: bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `oncpu`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_PERCPU_ARRAY, BPF_MAP_TYPE_STACK_TRACE for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include long stackid_kernel, long stackid_user, long stack_kernel, long stack_user, __u32 key, long val, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `.maps, perf_event, license` programs, helper coverage for `bpf_get_stack, bpf_get_stackid, bpf_map_lookup_elem`, and stable behavior of `oncpu` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/perf_event_stackmap.c -->
