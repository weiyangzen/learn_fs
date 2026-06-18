<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c

## Purpose

Tracing selftest for module lifetime races around BPF programs, fexit hooks, and widened race windows.

## Important APIs, Types, and Functions

- BPF sections: `fmod_ret.s/bpf_fentry_test1`, `fexit/do_init_module`, `fexit/btf_try_get_module`, `license`
- Important functions/callbacks: `check_thread_id`, `BPF_PROG`, `widen_race`, `fexit_init_module`, `fexit_module_get`
- BPF helpers/kfunc-like calls: `bpf_copy_from_user`, `bpf_get_current_task_btf`, `bpf_prog_widen_race`
- Mutable globals/test result fields: `bpf_blocking`, `res_try_get_module`

## Control Flow and Data Flow

Tracing hooks filter for the selftest thread, widen selected race windows, and record whether module lookup/release paths were reached while a BPF program remains attached.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `bpf_blocking`, `res_try_get_module`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_copy_from_user`, `bpf_get_current_task_btf`, `bpf_prog_widen_race`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `bpf_blocking`, `res_try_get_module` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_mod_race.c -->
