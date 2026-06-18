# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/ld_dw.c

Purpose: stress-tests 64-bit immediate load handling through randomized/generated `ld_dw` instruction streams.

Important APIs/types/functions: uses empty `.insns` filled by `bpf_fill_rand_ld_dw`, scheduler classifier program type, and expected `.retval` values.

Control flow: five tests delegate instruction generation to the fill helper, then execute XOR-style semi-random immediate-load sequences that return known values.

State and persistence behavior: register-only runtime state. The verifier must accept the generated `ld_imm64` pairs and the JIT/interpreter must preserve exact 64-bit constants.

Dependencies and integration points: depends on harness fill helper `bpf_fill_rand_ld_dw`; not standalone.

Risks: immediate-pair encoding or JIT relocation bugs can corrupt high/low halves of constants.

Test signals: all accept with return values `4090`, `2047`, `511`, `5`, and `1000000 - 6`.
