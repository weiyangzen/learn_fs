# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/jset.c

Purpose: validates 64-bit `BPF_JSET` runtime behavior and verifier reasoning for known, unknown, and partially known bit masks.

Important APIs/types/functions: uses `BPF_JMP_REG(BPF_JSET)`, `BPF_JMP_IMM(BPF_JSET)`, direct packet fixture input, `BPF_FUNC_get_prandom_u32`, and socket-filter program type for verifier path tests.

Control flow: functional tests compare packet-loaded values against register and immediate masks, including bit 63, bit 31 sign extension, and missing-bit paths. Later tests use known constants, random values, and `OR`-forced partial constants to verify whether guarded invalid loads are unreachable or reachable.

State and persistence behavior: state is register bitmask knowledge. The verifier must refine tnum/range information after JSET enough to prove some paths safe while rejecting genuinely reachable invalid reads.

Dependencies and integration points: uses packet data fixtures and helper availability for socket filter tests.

Risks: incorrect sign-extension of immediate masks or overly aggressive pruning can either miscompile runtime checks or accept unsafe invalid reads.

Test signals: functional cases accept with `.retvals` over multiple `.data64` inputs; negative reasoning cases reject with `!read_ok`; half-known and range cases accept due to proven branch constraints.
