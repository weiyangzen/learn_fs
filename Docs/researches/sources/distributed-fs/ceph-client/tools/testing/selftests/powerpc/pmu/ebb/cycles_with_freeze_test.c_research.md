<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c

Purpose: Tests EBB behavior while PMCs are deliberately frozen and unfrozen. It checks that no EBBs are counted during freeze windows.

Important APIs and types: Defines global `counters_frozen`, `ebbs_while_frozen`, custom `ebb_callee`, `cycles_with_freeze()`, and `main()`.

Control flow: The test configures a cycles EBB event, alternates `ebb_freeze_pmcs`/`ebb_unfreeze_pmcs` while running busy loops, and the handler records if an EBB arrives while the frozen flag is set.

State and persistence: Shared globals record freeze state and unexpected EBBs; `ebb_state` records normal counts.

Dependencies and integration points: Depends on MMCR0 freeze behavior, EBB handler reset, and perf setup helpers.

Risks: Races around the software `counters_frozen` flag and hardware freeze transition can produce edge-sensitive failures.

Test signals: Pass means freeze suppresses PMU progress/EBB delivery during the tested windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_freeze_test.c -->
