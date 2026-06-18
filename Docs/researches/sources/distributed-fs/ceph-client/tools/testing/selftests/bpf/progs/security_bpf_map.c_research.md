<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c

## Purpose

Security hook fixture that observes or overrides security_bpf_map decisions and uses side maps to coordinate with fentry test programs.

## Important APIs, Types, and Functions

Attach sections: license, .maps, fmod_ret/security_bpf_map, fentry/bpf_fentry_test1. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_map_lookup_elem, bpf_map_update_elem. Important structs/types visible in this file: map. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG` and related routines such as `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include __u32 key, __u32 val1, __u32 val2, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, fmod_ret/security_bpf_map, fentry/bpf_fentry_test1` programs, helper coverage for `bpf_map_lookup_elem, bpf_map_update_elem`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/security_bpf_map.c -->
