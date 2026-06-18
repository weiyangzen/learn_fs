# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_instr.c

Purpose: covers ordinary ALU, shift, move, and endian instruction semantics, especially 32-bit zero-extension and shift-by-zero behavior.

Important APIs/types/functions: uses ALU macros such as `BPF_ALU64_IMM`, `BPF_ALU64_REG`, `BPF_ALU32_REG`, `BPF_MOV32_IMM`, `BPF_LD_IMM64`, and a raw invalid `BPF_ALU64 | BPF_END | BPF_TO_BE` encoding.

Control flow: accepted tests compute fixed return values for add/sub/mul, XOR zero-extension, arithmetic right shifts, and zero-distance left/right/arithmetic shifts with immediate and register shift counts. Negative coverage rejects an invalid 64-bit endian opcode. Final move tests confirm `mov64 src == dst` and `src != dst` acceptance in scheduler classifier programs.

State and persistence behavior: no persistent state. Tests are register-dataflow checks, with `.retval` values acting as runtime proofs for arithmetic semantics.

Dependencies and integration points: consumed by the verifier test harness; some cases specify `BPF_PROG_TYPE_SCHED_CLS`.

Risks: ALU verifier range tracking and JIT lowering frequently share implementation paths; regressions can show up as wrong return values rather than verifier rejection.

Test signals: mostly `ACCEPT` with expected `.retval`; the invalid endian case rejects with `unknown opcode df`.
