<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c

Purpose: Cgroup LSM programs for socket create/bind/storage behavior, getsockopt/setsockopt mediation, and security-module config gates. The file has 193 source lines and 4319 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG`. Local functions/subprograms: `test_local_storage, real_create, BPF_PROG, BPF_PROG, real_bind, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `cgroup_storage`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_local_storage, bpf_getsockopt, bpf_probe_read_kernel, bpf_setsockopt`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `cgroup_storage` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: bool CONFIG_SECURITY_SELINUX __kconfig __weak, bool CONFIG_SECURITY_SMACK __kconfig __weak, bool CONFIG_SECURITY_APPARMOR __kconfig __weak; BPF LSM attachment support and relevant LSM hooks. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_post_create:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/socket_bind:BPF_PROG, lsm_cgroup/sk_alloc_security:BPF_PROG, lsm_cgroup/inet_csk_clone:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lsm_cgroup.c -->
