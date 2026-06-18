<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h

Purpose: Shared MPTCP helpers for list-head checks and conversion from MPTCP subflow context to TCP socket. The file has 43 source lines and 1244 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `list_is_head, mptcp_subflow_tcp_sock`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: This header has no runtime persistence; it defines shared structs, inline helpers, or map declarations consumed by companion BPF object files.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; MPTCP kernel types and socket helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mptcp_bpf.h -->
