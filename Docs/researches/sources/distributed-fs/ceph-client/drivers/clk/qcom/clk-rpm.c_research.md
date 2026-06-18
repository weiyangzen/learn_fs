# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpm.c

## Purpose
Implements the legacy Qualcomm RPM clock-controller provider used by older MSM/APQ/IPQ platforms where clock votes are sent directly to the RPM MFD. It exposes RPM-managed fabric, peripheral, PLL, and XO-buffer clocks to the common clock framework, translates prepare/unprepare and rate changes into active/sleep RPM votes, and registers per-SoC clock arrays selected by device-tree compatible strings.

## Important APIs, Types, And Functions
- `struct clk_rpm` is the per-clock state: RPM resource id, optional XO bit offset, active-only flag, cached rate, enabled state, branch-mode behavior, peer active/sleep clock, `clk_hw`, RPM handle, and containing `rpm_cc`.
- `struct rpm_cc` stores the clock table, number of clocks, aggregate XO-buffer bitfield, and XO-specific mutex.
- `clk_rpm_prepare`, `clk_rpm_unprepare`, and `clk_rpm_set_rate` compute aggregate votes across a normal and active-only peer, convert rate clocks to kHz, and use boolean votes for branch clocks.
- `clk_rpm_xo_prepare` and `clk_rpm_xo_unprepare` update the shared `QCOM_RPM_CXO_BUFFERS` bitfield using `QCOM_RPM_XO_MODE_ON` shifted by each buffer offset.
- `clk_rpm_handoff` sends `INT_MAX` active and sleep votes during probe to preserve already enabled RPM resources, except for PLL4 and CXO buffers.
- `rpm_clk_probe` retrieves the parent `struct qcom_rpm`, initializes every listed clock, registers the `clk_hw`s, and publishes the OF clock provider.

## Control Flow
The platform driver is registered at `core_initcall`. Probe reads the SoC descriptor from the match table, stores the parent RPM handle in each static `clk_rpm`, performs handoff writes, then registers all available clocks and `qcom_rpm_clk_hw_get`. Common-clock consumers later obtain a clock by binding index, set rates, and prepare or unprepare it. Prepare takes `rpm_clk_lock`, ignores zero-rate clocks, converts the local vote and the enabled peer vote into active/sleep votes, sends active first, then sleep, and marks the clock enabled on success. Unprepare recomputes the vote from only the enabled peer and clears `enabled` after both active and sleep writes succeed. Rate changes only send messages while the clock is already enabled, then cache the requested rate; RPM owns final rounding, so determine/recalc are intentionally pass-through/cached.

## State And Persistence
Driver state is mostly static per-clock objects plus runtime fields `rate`, `enabled`, `rpm`, `rpm_cc`, and the shared `xo_buffer_value`. Persistent hardware/firmware state is the active and sleep RPM vote for each resource id. Normal and active-only peers share a remote resource, so each operation recomputes the max aggregate vote rather than writing independent hardware state. XO buffers persist as bits in one RPM resource. No state is stored on disk.

## Dependencies And Integration Points
The file depends on the RPM MFD API `qcom_rpm_write`, RPM and clock dt-bindings, the Linux common clock framework, OF clock providers, and board-provided `pxo` or `cxo` parents. It integrates with older `qcom,rpmcc-*` nodes, downstream consumers using `qcom,rpmcc.h` clock indexes, and power-management firmware that interprets active/sleep resource votes.

## Risks And Edge Cases
Peer aggregation is subtle: disabling one side must leave the other side's vote intact, and branch resources must be reduced to 0/1 after aggregation. Sleep votes for active-only clocks must be zero or they can keep resources active through suspend. Failed sleep writes after an active write attempt a rollback to the peer active vote, but rollback failure is not separately reported. The static clock objects are reused by compatible tables, so probe lifetime assumes only one matching instance per system. XO-buffer writes require the separate `xo_lock` because several logical clocks share one remote bitfield.

## Test Signals
Useful signals include successful probe for msm8660/apq8064/ipq806x compatibles, valid OF lookup indexes and `-ENOENT` for sparse entries, active/sleep RPM messages matching max peer rates, active-only clocks dropping sleep votes to zero, branch clocks sending 0/1 values, XO buffers preserving unrelated bits, and no unintended clock drop during handoff or suspend/resume.
