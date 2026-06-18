# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic.c

Purpose: minimal verifier sanity tests for program termination and initialized return register requirements.

Important APIs/types/functions: uses empty `.insns`, `BPF_EXIT_INSN`, and `BPF_ALU64_REG(BPF_MOV, ...)`.

Control flow: one test has no instructions, one exits without initializing `R0`, and one ends with a non-exit instruction.

State and persistence behavior: no runtime state persists. The file validates initial verifier state for `R0` and final-instruction structural checks.

Dependencies and integration points: consumed by the generic verifier selftest table.

Risks: these tiny cases catch broad verifier acceptance regressions that would otherwise allow malformed programs.

Test signals: all reject, with diagnostics `last insn is not an exit or jmp`, `R0 !read_ok`, and `not an exit`.
