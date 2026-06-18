<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c

Purpose: BPF LSM selftest programs for map access and sleepable helper behavior in mprotect and credential hooks. The file has 184 source lines and 4051 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `array, hash, lru_hash, percpu_array, percpu_hash, lru_percpu_hash, inner_map, outer_arr, outer_hash`. Types: `inner_map, outer_arr, outer_hash`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_get_current_pid_tgid, bpf_map_lookup_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `array, hash, lru_hash, percpu_array, percpu_hash, lru_percpu_hash, inner_map, outer_arr, outer_hash` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm/file_mprotect:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm.c -->
