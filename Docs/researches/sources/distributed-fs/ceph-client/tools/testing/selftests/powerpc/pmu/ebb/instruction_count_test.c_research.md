<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c

Purpose: EBB variant of deterministic instruction counting. It verifies PMU instruction counts collected via EBB overflows.

Important APIs and types: Defines `do_count_loop`, `determine_overhead`, custom `pmc4_ebb_callee`, `instruction_count`, and `main()`. Calls `thirty_two_instruction_loop`.

Control flow: The test measures overhead, configures an instruction-counting EBB event, runs fixed-size loops, handles PMC4 overflows in the custom callee, and checks accumulated counts against expected instruction totals.

State and persistence: Uses shared `ebb_state`, local event state, and measured overhead values.

Dependencies and integration points: Depends on `ebb.h`, `loop.S`, perf instruction events, and PMU counter routing to PMC4.

Risks: Instruction count tolerance depends on exact assembly loop and handler overhead. PMU event placement must match the custom handler.

Test signals: Pass shows EBB-based instruction counting is accurate enough for deterministic loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/instruction_count_test.c -->
