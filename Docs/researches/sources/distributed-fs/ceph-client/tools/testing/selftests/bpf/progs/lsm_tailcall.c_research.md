<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c

Purpose: LSM tail-call test using a prog-array jump table across file and kernfs hooks. The file has 35 source lines and 685 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry`. Local functions/subprograms: `lsm_file_permission_prog, lsm_kernfs_init_security_prog, lsm_kernfs_init_security_entry`. Maps: `jmp_table`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_tail_call_static`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `jmp_table` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of lsm/file_permission:lsm_file_permission_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_prog, lsm/kernfs_init_security:lsm_kernfs_init_security_entry; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_tailcall.c -->
