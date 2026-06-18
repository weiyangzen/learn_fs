<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c

Purpose: Inline-BTF kptr exchange test with local root types and object dropping. The file has 49 source lines and 1004 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `__btf_root`. Maps: `none declared in this file`. Types: `bin_data`. BPF helpers/kfuncs/macros used as calls: `bpf_obj_drop`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kptr_xchg_inline.c -->
