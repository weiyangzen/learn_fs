# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_imm64.c

Purpose: validates 64-bit immediate-load instruction pair encoding, reserved-field handling, missing second halves, and malformed second-half immediates.

Important APIs/types/functions: uses `BPF_LD_IMM64`, raw full immediate macros, and verifier diagnostics for `BPF_LD_IMM64` reserved fields and invalid instruction sequencing.

Control flow: accepted tests load constants into registers and exit or compare expected values. Negative tests mutate the second instruction, reserved source/destination/off fields, or pair structure so the verifier rejects the malformed immediate load.

State and persistence behavior: register-only state. The important invariant is that a 64-bit immediate load is a two-instruction unit with constrained metadata in both slots.

Dependencies and integration points: generic verifier instruction-decoder tests.

Risks: accepting malformed `ld_imm64` pairs can desynchronize verifier instruction walking and JIT decoding.

Test signals: mixture of accepts and rejects; key diagnostic for the final case is `invalid bpf_ld_imm64 insn` when the second immediate is not zero where required.
