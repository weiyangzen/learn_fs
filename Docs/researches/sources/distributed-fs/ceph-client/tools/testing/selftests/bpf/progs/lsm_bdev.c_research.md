<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c

Purpose: Block-device LSM test that stores verity device metadata and validates allocation/free/integrity hook behavior. The file has 97 source lines and 2586 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `verity_devices`. Types: `verity_info`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `verity_devices` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm.s/bdev_setintegrity:BPF_PROG, lsm/bdev_free_security:BPF_PROG, lsm.s/bdev_alloc_security:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_bdev.c -->
