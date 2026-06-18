<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c

Purpose: Shared runtime library for EBB selftests. It manages handler setup, EBB reset, PMU register access, event initialization, child workload coordination, tracing, and diagnostics.

Important APIs and types: Exports `ebb_hook`, `reset_ebb`, `ebb_check_mmcr0`, `ebb_check_count`, `standard_ebb_callee`, `setup_ebb_handler`, dump/clear helpers, `count_pmc`, `ebb_event_enable`, freeze/global enable controls, `ebb_is_supported`, event init helpers, `ebb_child`, `catch_sigill`, `write_pmc`, `read_pmc`, and constructor `ebb_init`.

Control flow: Tests call event init/setup helpers, install `ebb_handler` into EBBHR, enable global EBB state, run loops until PMCs overflow, and handlers call `standard_ebb_callee` or custom callees to count/reset PMCs. The constructor initializes trace buffers and SIGTERM diagnostics.

State and persistence: Global `ebb_state`, `sample_period`, `ebb_user_func`, trace buffer, and signal handlers persist for the process lifetime. Hardware PMU SPRs are modified and reset during tests.

Dependencies and integration points: Depends on `ebb.h`, `trace.h`, PMU event helpers, powerpc SPR macros, pipe synchronization from `lib.c`, and assembly `ebb_handler`/`core_busy_loop`.

Risks: High-risk shared code: wrong reset ordering can leave PMCs frozen or EBB disabled, and direct SPR access is privileged/CPU-feature sensitive. Global state means tests must clean up before exit.

Test signals: All EBB test binaries exercise this file; state dumps and EBB counts are primary diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.c -->
