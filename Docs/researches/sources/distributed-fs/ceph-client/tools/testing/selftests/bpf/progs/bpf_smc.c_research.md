<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c

## Purpose

SMC protocol selftest that redirects eligible TCP sockets to SMC and registers BPF struct_ops handshake policy callbacks.

## Important APIs, Types, and Functions

- BPF sections: `license`, `fentry/smc_release`, `fentry/smc_switch_to_fallback`, `.maps`, `fmod_ret/update_socket_protocol`, `struct_ops`, `struct_ops`, `.struct_ops`
- Maps: `smc_policy_ip`
- Important functions/callbacks: `BPF_PROG`, `smc_check`, `bpf_smc_release`, `bpf_smc_switch_to_fallback`, `smc_run`, `bpf_smc_set_tcp_option_cond`, `bpf_smc_set_tcp_option`
- BPF helpers/kfunc-like calls: `bpf_core_field_exists`, `bpf_get_current_task_btf`, `bpf_map_lookup_elem`
- Mutable globals/test result fields: `smc_cnt`, `fallback_cnt`, `default_ip_strat_value`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `smc_policy_ip` Globals are used as userspace-visible configuration/results: `smc_cnt`, `fallback_cnt`, `default_ip_strat_value`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf_tracing_net.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_core_field_exists`, `bpf_get_current_task_btf`, `bpf_map_lookup_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `smc_cnt`, `fallback_cnt`, `default_ip_strat_value` to confirm the exercised path ran. Map contents/counts for `smc_policy_ip` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_smc.c -->
