<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c

Purpose: Positive list front/back peek test that exercises non-removing access under spin lock. The file has 114 source lines and 2310 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `syscall:list_peek`. Local functions/subprograms: `list_peek`. Maps: `none declared in this file`. Types: `node_data`. BPF helpers/kfuncs/macros used as calls: `bpf_jiffies64, bpf_list_back, bpf_list_front, bpf_list_push_back, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `syscall:list_peek`. Control flow is centered on critical sections protect intrusive container or resource-spin-lock state.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: libbpf verifier annotations __failure, __retval(0); successful attachment/execution of syscall:list_peek; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list_peek.c -->
