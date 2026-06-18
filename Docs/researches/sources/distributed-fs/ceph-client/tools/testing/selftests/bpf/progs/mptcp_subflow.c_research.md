<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c

## Purpose

Tests MPTCP subflow socket operations by counting subflows per MPTCP token, setting SO_MARK by subflow order, applying congestion control on the second subflow, and validating those properties from a cgroup getsockopt program.

## Important APIs, Types, and Functions

Attach sections: license, .maps, sockops, cgroup/getsockopt. Map types: BPF_MAP_TYPE_HASH. Important local functions/programs: mptcp_subflow, _check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow. Helper and kfunc calls: bpf_core_cast, bpf_get_current_pid_tgid, bpf_map_lookup_elem, bpf_map_update_elem, bpf_setsockopt, bpf_skc_to_mptcp_sock. Important structs/types visible in this file: none. Includes: bpf_tracing_net.h, mptcp_bpf.h.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

The main data flow centers on `mptcp_subflow` and related routines such as `_check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow`, with BPF helper results checked before dereference or used deliberately to exercise verifier rejection paths.

## State and Persistence Behavior

Persistent state is held in BPF maps of type BPF_MAP_TYPE_HASH for the lifetime of the loaded object or until the user-space test deletes/updates entries. Global data variables include char cc[TCP_CA_NAME_MAX], int pid, __u32 init, int err, int i, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types, networking and cgroup/sockops attach points. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Network tests are sensitive to attach context, protocol family, socket state, namespace, and kernel helper allowlists.

## Test Signals

user-space checks should inspect map contents or storage side effects; the declared attach sections should load and attach in the owning selftest; return values/counters from the named BPF programs should match selftest assertions.
For this file specifically, useful signals include presence of `license, .maps, sockops, cgroup/getsockopt` programs, helper coverage for `bpf_core_cast, bpf_get_current_pid_tgid, bpf_map_lookup_elem, bpf_map_update_elem, bpf_setsockopt, bpf_skc_to_mptcp_sock`, and stable behavior of `mptcp_subflow, _check_getsockopt_subflow_mark, _check_getsockopt_subflow_cc, _getsockopt_subflow` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_subflow.c -->
