<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h

## Purpose

Data-contract header for profiler.inc.h, defining event payload limits, metadata structures, cgroup/file/kill/exec/fork payload layouts, and function-stat identifiers.

## Important APIs, Types, and Functions

Attach sections: none. Map types: none. Important local functions/programs: none. Helper and kfunc calls: none. Important structs/types visible in this file: ancestors_data_t, var_metadata_t, cgroup_data_t, var_sysctl_data_t, var_kill_data_t, var_exec_data_t, var_fork_data_t, var_filemod_data_t, profiler_config_struct, bpf_func_stats_data, bpf_func_stats_ctx. Includes: none.

## Control Flow and Data Flow

The file is loaded by the BPF selftest harness through libbpf, which turns the `SEC()` declarations into attachable BPF programs or maps. Runtime control starts from the listed attach sections, then follows the local helper/subprogram calls into map lookups, kfunc/helper invocations, socket or kernel object reads, and final return codes. For header or wrapper-style files, control is provided by the including C file and this file contributes shared inline logic, constants, data contracts, or macro-selected variants.

## State and Persistence Behavior

Global data variables include int cgroup_full_path_root_pos, char payload[MAX_SYSCTL_PAYLOAD_LEN], int kill_sig, char payload[MAX_KILL_PAYLOAD_LEN], char payload[MAX_EXEC_PAYLOAD_LEN], char payload[MAX_METADATA_PAYLOAD_LEN], char payload[MAX_FILEMOD_PAYLOAD_LEN], bool fetch_cgroups_from_bpf, bool use_variable_buffers, bool read_environ_from_exec, and 1 more, which the harness may initialize, mutate, or read back through the BPF object data maps.

## Dependencies and Integration Points

Depends on libbpf SEC/BTF skeleton generation, Linux BPF verifier, vmlinux/BTF types. It integrates with `tools/testing/selftests/bpf` user-space tests, generated skeletons, kernel BTF/CO-RE relocation, and the specific attach hooks named above. The file is source-tree-aligned with other BPF selftest programs rather than production Ceph client code; its value is regression coverage for kernel BPF behavior used by networking, tracing, cgroup, LSM, memory-allocation, and verifier subsystems.

## Risks and Edge Cases

Program size, loop unrolling, compiler version, and stack depth are significant risk points for verifier acceptance.

## Test Signals

.
For this file specifically, useful signals include presence of `none` programs, helper coverage for `none`, and stable behavior of `none` under the owning selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/profiler.h -->
