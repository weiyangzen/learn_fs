# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/junk_insn.c

Purpose: confirms the verifier rejects malformed or unknown raw instruction encodings.

Important APIs/types/functions: uses `BPF_RAW_INSN` with opcode `0`, invalid `BPF_LDX` reserved fields, opcode `-1`, and `0x7f`.

Control flow: every test emits one malformed instruction followed by exit. Structural validation must reject before execution.

State and persistence behavior: no state beyond instruction decoder validation.

Dependencies and integration points: generic verifier selftest fragment.

Risks: accepting junk opcodes creates undefined interpreter/JIT behavior and can compromise verifier assumptions.

Test signals: all reject with `unknown opcode 00`, `BPF_LDX uses reserved fields`, `unknown opcode ff`, or `BPF_ALU uses reserved fields`.
