## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_selftests.c

## Purpose
Provides optional ethtool offline self-tests for TSNEP gate control and taprio offload behavior. The tests exercise gate-control enable timeout handling, static schedules, schedule changes, and cycle-time-extension edge cases.

## Important APIs, Types, and Functions
Exports `tsnep_ethtool_get_test_count`, `tsnep_ethtool_get_test_strings`, and `tsnep_ethtool_self_test` when `CONFIG_TSNEP_SELFTESTS` is enabled. Internal test helpers include `enable_gc_timeout`, `gc_delayed_enable`, `tsnep_test_gc_enable`, `delay_base_time`, `get_gate_state`, `get_operation`, `check_gate`, `enable_check_taprio`, `disable_taprio`, `run_taprio`, `tsnep_test_taprio`, `tsnep_test_taprio_change`, and `tsnep_test_taprio_extension`.

## Control Flow and State
Online tests are reported as skipped/successful without touching hardware. Offline tests directly program gate-control registers or call `tsnep_tc_setup` with synthetic `tc_taprio_qopt_offload` schedules, then repeatedly compare hardware gate state, next gate state, and change time against the driver's `adapter->gcl` software model. Failures set `ETH_TEST_FL_FAILED` and a per-test nonzero result. Each taprio test destroys the qdisc on failure paths to reset hardware state.

## Dependencies and Integration Points
Depends on `tsnep_tc.c` taprio programming, `tsnep_get_system_time`, `net/pkt_sched.h`, TSNEP gate-control MMIO registers, and ethtool self-test integration through `tsnep_ethtool.c`/`tsnep.h`.

## Risks and Test Signals
Risks include destructive offline behavior while traffic is active, timing sensitivity from `ndelay`, long runtime due to many schedule checks, and false failures if system time or gate-control hardware is paused or virtualized. These tests themselves are the main signal for taprio regressions; run `ethtool -t <dev> offline` on hardware with `gate_control` detected, including repeated runs after link up/down and after taprio qdisc changes.
