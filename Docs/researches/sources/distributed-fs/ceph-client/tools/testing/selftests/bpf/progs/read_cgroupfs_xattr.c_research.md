<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c

## Purpose

Sleepable LSM file_open program that resolves the current cgroup, iterates/read cgroupfs xattrs via dynptr, and records matching xattr results.

## Important APIs, Types, and Functions

Attach sections: license, lsm.s/file_open. Map types: none. Important local functions/programs: BPF_PROG. Helper and kfunc calls: bpf_cgroup_from_id, bpf_cgroup_read_xattr, bpf_cgroup_release, bpf_dynptr_from_mem, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_pid_tgid, bpf_rcu_read_lock, bpf_rcu_read_unlock, bpf_strncmp. Important structs/types visible in this file: none. Includes: vmlinux.h, bpf/bpf_tracing.h, bpf/bpf_helpers.h, bpf/bpf_core_read.h, bpf_experimental.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `BPF_PROG`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Global data variables include char xattr_value[64], bool found_value_a, bool found_value_b, u64 cgrp_id, int ret, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, experimental BPF object/list/rbtree APIs, test kfuncs or kernel kfunc allowlists. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Lock, preemption, or RCU lifetime balance is the main safety risk; missing unlock/drop paths should fail or be asserted by user space. Pointer reads depend on kernel/user layout, CO-RE relocation, and bounded copies; truncation and NULL checks are important edge cases.

## Test Signals

the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, lsm.s/file_open` programs, helper coverage for `bpf_cgroup_from_id, bpf_cgroup_read_xattr, bpf_cgroup_release, bpf_dynptr_from_mem, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_pid_tgid, bpf_rcu_read_lock, and 2 more`, and stable behavior of `BPF_PROG` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/read_cgroupfs_xattr.c -->
