<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c

Purpose: Basic EBB cycles event test. It verifies that a cycles event can generate EBBs and increment state.

Important APIs and types: Defines `cycles()` and `main()`; uses `event_init_named`, `event_leader_ebb_init`, `setup_ebb_handler`, `ebb_global_enable`, and `core_busy_loop`.

Control flow: `cycles()` skips without EBB support, configures a cycles event excluding kernel/hypervisor/idle, enables counting, seeds PMC1, runs the busy loop until EBBs arrive, disables/freezes, dumps state, and checks count > 0.

State and persistence: Uses shared `ebb_state`; perf event fd is local.

Dependencies and integration points: Depends on `ebb.h`, perf events, and POWER8+ EBB support.

Risks: If counters are frozen or sample period unsuitable, no EBB arrives. Environment PMU restrictions can cause skips/failures.

Test signals: Pass is at least one counted EBB with sane state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_test.c -->
