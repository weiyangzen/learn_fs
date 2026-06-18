# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_speed.sh

Purpose: helper that writes PCIe thermal cooling states and checks that each state maps to the expected `current_link_speed` string.

Important data/functions: `PCIELINKSPEED` maps speed-state indices to strings from 2.5 through 64.0 GT/s PCIe. `set_state()` writes `cur_state`, sleeps one second, reads link speed, computes `expected_linkspeed=maxstate-state`, and records failure on mismatch. `cleanup_skip()` restores the old state and exits with kselftest skip code.

Control flow: reads `oldstate` and `maxstate`, installs an EXIT trap that restores state as skip on unexpected termination, then iterates from `maxstate` down to `oldstate`. After normal completion it clears the trap, prints `[PASS]` or `[FAIL]`, and exits with accumulated status.

State and persistence: mutates `$coolingdev/cur_state` and restores the original state only on trapped skip/error path. During successful runs the final state is `oldstate` because the loop descends to it.

Dependencies/integration: requires writable thermal cooling sysfs state files and readable PCI `current_link_speed`. It is called by `set_pcie_cooling_state.sh`.

Risks: assumes link-speed strings exactly match the array, and that one second is enough for hardware to settle. Array indexing fails conceptually if `max_state - state` exceeds known speeds.

Test signals: mismatch lines name expected and actual speeds; final line is `set_pcie_speed [PASS]` or `[FAIL]`; exit code is zero or one.
