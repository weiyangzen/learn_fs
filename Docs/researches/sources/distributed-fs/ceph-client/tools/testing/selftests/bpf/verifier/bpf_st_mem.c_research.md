# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/bpf_st_mem.c

Purpose: validates immediate stores to stack memory, including nonzero values, zero initialization, variable-offset zero stores, and verbose sign formatting.

Important APIs/types/functions: uses `BPF_ST_MEM`, `BPF_ALU64_IMM` for variable offsets, `BPF_PROG_TYPE_SK_LOOKUP`, `BPF_SK_LOOKUP`, and `VERBOSE_ACCEPT`.

Control flow: tests store immediates into stack slots and exit. The variable-offset case builds a bounded variable pointer off `R10` before storing zero, relying on verifier rules that zero writes can initialize stack ranges. The sign test checks verbose verifier output for a negative immediate store.

State and persistence behavior: all state is verifier stack-slot initialization metadata. Zero stores are important because initialized stack state can influence later helper calls and pruning.

Dependencies and integration points: uses sk_lookup program type and attach type, with `.runs = -1` to avoid runtime execution where context is not material.

Risks: stack initialization tracking for immediate stores is foundational; regressions can either reject valid stack initialization or allow reads from uninitialized stack bytes.

Test signals: first three cases accept; sign case is `VERBOSE_ACCEPT` and checks the verbose log contains the expected stored value annotation.
