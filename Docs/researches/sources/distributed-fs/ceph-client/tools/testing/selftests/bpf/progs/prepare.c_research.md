<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c

## Purpose

Small fixture defining array and ringbuf maps plus a cgroup skb program, used by loader-side prepare tests to validate object/map setup.

## Important APIs, Types, and Functions

Attach sections: license, .maps, cgroup_skb/egress. Map types: BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_RINGBUF. Important local functions/programs: program. Helper and kfunc calls: none. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_helpers.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `program`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_RINGBUF for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include int err, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

The main risk is drift between BPF helper/kfunc verifier rules and the user-space selftest expectations.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, cgroup_skb/egress` programs, helper coverage for `none`, and stable behavior of `program` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/prepare.c -->
