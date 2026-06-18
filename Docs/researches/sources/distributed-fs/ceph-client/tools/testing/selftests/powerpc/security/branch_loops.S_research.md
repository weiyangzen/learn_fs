# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/branch_loops.S

Purpose: provides branch-prediction workload loops for the Spectre v2 mitigation measurement test.

Important APIs/types/functions: exports `pattern_cache_loop` and `indirect_branch_loop` with `FUNC_START/FUNC_END`. `ITER_SHIFT` controls loop length, and `jump_table` drives pattern-cache transitions.

Control flow: `pattern_cache_loop` cycles through eight aligned state labels using a computed count-register branch, creating a predictable but indirect branch pattern. `indirect_branch_loop` repeatedly branches through CTR to a local aligned label. Both loops run for `1 << 31` iterations unless interrupted by completion.

State and persistence behavior: no persistent state; only GPR/CTR state during execution. The data jump table is read-only for test purposes.

Dependencies and integration points: consumed by `spectre_v2.c` and built only for 64-bit powerpc by the security Makefile.

Risks and test signals: PMU test quality depends on these loops generating stable branch prediction counts. Changes to alignment or loop length can alter thresholds in `spectre_v2.c`.
