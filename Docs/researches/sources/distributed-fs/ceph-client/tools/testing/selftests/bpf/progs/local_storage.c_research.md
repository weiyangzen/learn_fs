<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c

Purpose: LSM programs exercising inode, socket, and task local storage get/delete paths across sleepable and non-sleepable hooks. The file has 214 source lines and 5083 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `inode_storage_map, sk_storage_map, sk_storage_map2, task_storage_map, task_storage_map2`. Types: `local_storage`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_get_current_task_btf, bpf_inode_storage_delete, bpf_inode_storage_get, bpf_sk_storage_delete, bpf_sk_storage_get, bpf_task_storage_delete, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `inode_storage_map, sk_storage_map, sk_storage_map2, task_storage_map, task_storage_map2` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of lsm/inode_unlink:BPF_PROG, lsm.s/inode_rename:BPF_PROG, lsm.s/socket_bind:BPF_PROG, lsm.s/socket_post_create:BPF_PROG, lsm.s/bprm_committed_creds:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage.c -->
