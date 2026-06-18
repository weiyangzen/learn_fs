<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c

Purpose: JIT/runtime probe-memory path test using acquired kfunc objects and kptr exchange/release. The file has 60 source lines and 1061 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:test_jit_probe_mem`. Local functions/subprograms: `test_jit_probe_mem`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_release, bpf_kptr_xchg`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:test_jit_probe_mem`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:test_jit_probe_mem; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jit_probe_mem.c -->
