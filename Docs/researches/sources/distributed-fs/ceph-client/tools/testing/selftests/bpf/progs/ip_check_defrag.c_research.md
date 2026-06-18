<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c

Purpose: Exercises BPF netfilter defragmentation visibility by detecting IPv4 and IPv6 fragment headers from skb dynptr slices. The file has 100 source lines and 1967 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `netfilter:defrag`. Local functions/subprograms: `is_frag_v4, is_frag_v6, handle_v4, handle_v6, defrag`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_dynptr_from_skb, bpf_dynptr_slice, bpf_ntohs`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `netfilter:defrag`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of netfilter:defrag; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ip_check_defrag.c -->
