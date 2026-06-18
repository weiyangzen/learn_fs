<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c

Purpose: Counts failed store-conditional operations with PMU events. It validates marked and unmarked `stcx.` failure event behavior.

Important APIs and types: Defines `setup_event`, `do_count_loop`, `determine_overhead`, constants `PM_MRK_STCX_FAIL`/`PM_STCX_FAIL`, `test_body`, `count_ll_sc`, and `main()`. Calls `thirty_two_instruction_loop_with_ll_sc`.

Control flow: The test configures PMU events, runs a deterministic loop containing load-linked/store-conditional sequences against a target, reads counters, subtracts overhead, and checks expected failure counts.

State and persistence: State is local perf events and the LL/SC target memory word.

Dependencies and integration points: Depends on perf events, PMU event codes, `event.h`, `lib.h`, and the assembly loop implementation.

Risks: Event encodings can vary by CPU generation; marked-event behavior can be privilege/filter sensitive.

Test signals: Pass confirms PMU event codes count failed `stcx.` sequences as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/count_stcx_fail.c -->
