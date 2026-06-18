# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jit.c

Purpose: runtime-oriented verifier/JIT regression tests for shifts, 32-bit moves around `ldimm64`, multiplication/division, signed jumps, and jump padding.

Important APIs/types/functions: uses ALU shift/mul/div instructions, `BPF_LD_IMM64`, signed jump predicates, long jump sequences, subprogram calls, and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: early tests compute expected return value `2` for lsh/rsh/arsh, mov32, multiply, divide, and signed compare cases. Torturous jump tests use large immediate and conditional jump layouts, including a subprogram variant, to catch JIT offset and padding mistakes.

State and persistence behavior: state is register-only runtime state. The verifier accepts these programs; the JIT or interpreter must preserve exact arithmetic and branch behavior.

Dependencies and integration points: included in verifier tests but primarily probes JIT code generation. Some cases set `.prog_type = BPF_PROG_TYPE_SCHED_CLS`.

Risks: architecture JITs can miscompile edge-case shifts, division, or branch padding even when verifier acceptance is correct.

Test signals: all entries accept with specific `.retval` values, mostly `2`, with jump padding cases returning `1`, `2`, or `3`.
