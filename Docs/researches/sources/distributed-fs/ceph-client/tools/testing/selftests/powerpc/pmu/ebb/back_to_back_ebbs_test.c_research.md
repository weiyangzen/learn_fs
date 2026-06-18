<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c

Purpose: Tests delivery of many EBBs back-to-back without losing handler state. It forces repeated PMC overflows.

Important APIs and types: Defines `NUMBER_OF_EBBS`, custom `ebb_callee`, `back_to_back_ebbs`, and `main()`.

Control flow: The test sets an EBB handler that counts and resets overflows, configures a cycles event, repeatedly drives the busy loop until the target EBB count is reached, then disables/freezes PMCs and validates counts.

State and persistence: Uses global `ebb_state` and `sample_period` from `ebb.c`; perf event fd is local.

Dependencies and integration points: Depends on `ebb.h`, perf events, and `core_busy_loop`.

Risks: Very small sample periods can expose timing races; handler reset ordering is critical.

Test signals: Pass means repeated adjacent overflows are delivered and accounted without spurious loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/back_to_back_ebbs_test.c -->
