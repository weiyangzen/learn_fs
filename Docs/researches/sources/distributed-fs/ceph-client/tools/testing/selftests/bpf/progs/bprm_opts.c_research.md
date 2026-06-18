<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c

## Purpose

LSM selftest using task local storage to set secure-exec behavior during binary execution.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`, `lsm/bprm_creds_for_exec`
- Maps: `secure_exec_task_map`
- Important functions/callbacks: `BPF_PROG`, `secure_exec`
- BPF helpers/kfunc-like calls: `bpf_bprm_opts_set`, `bpf_get_current_task_btf`, `bpf_task_storage_get`

## Control Flow and Data Flow

On `bprm_creds_for_exec`, the program fetches current-task storage, and if the stored flag is set, calls `bpf_bprm_opts_set` to request secure execution.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `secure_exec_task_map`

## Dependencies and Integration Points

Includes `linux/bpf.h`, `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_bprm_opts_set`, `bpf_get_current_task_btf`, `bpf_task_storage_get`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Map contents/counts for `secure_exec_task_map` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bprm_opts.c -->
