# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-smd-rpm.c

## Purpose
Provides Qualcomm RPM clock controllers over the SMD RPM transport. It defines many reusable RPM clock templates and SoC-specific binding tables, sends active/sleep SMD RPM votes for rate and branch clocks, enables RPM-side clock scaling, and bootstraps interconnect-related RPM clocks until the interconnect driver takes ownership.

## Important APIs, Types, And Functions
- `struct clk_smd_rpm` stores RPM resource type, key, resource id, active-only flag, enabled/branch flags, peer pointer, common-clock hardware, and cached rate.
- `struct rpm_smd_clk_desc` contains the public clock table plus an interconnect clock list, count, and `scaling_before_handover` quirk.
- The `DEFINE_CLK_SMD_RPM*` macros build paired normal and active-only clocks for rate resources, branch resources, XO buffers, pin-control variants, bus clocks, and QDSS state resources.
- `clk_smd_rpm_prepare`, `clk_smd_rpm_unprepare`, and `clk_smd_rpm_set_rate` aggregate peer votes and write active/sleep requests with `qcom_rpm_smd_write`.
- `clk_smd_rpm_handoff` votes `INT_MAX` for rate clocks or 1 for branch clocks in both active and sleep sets before registration.
- `clk_smd_rpm_enable_scaling` writes `QCOM_RPM_SMD_KEY_ENABLE` to the misc scaling resource for both sleep and active states.
- `rpm_smd_clk_probe` performs handoff, enables scaling in the correct order, registers clocks, registers the OF provider, and creates the `icc_smd_rpm` platform device.

## Control Flow
Probe stores the parent `struct qcom_smd_rpm` in the global `rpmcc_smd_rpm`, selects a descriptor by compatible, optionally enables scaling before handoff, sends handoff votes for all exposed clocks and any interconnect bootstrap clocks, enables scaling after handoff for the normal case, registers each common-clock object, adds the OF clock provider, and then registers an `icc_smd_rpm` child device. Runtime prepare mirrors the legacy direct-RPM logic: under `rpm_smd_clk_lock`, it converts the local clock and enabled peer into active/sleep votes, reduces branch resources to boolean values, writes active first and sleep second, and marks enabled. Unprepare leaves only the peer vote in place. Set-rate sends new aggregate votes only for an enabled clock and then updates the cached rate.

## State And Persistence
The transport handle is global, while each static clock object tracks `enabled` and cached `rate`. Persistent firmware state consists of SMD RPM active and sleep votes keyed by resource type, id, and request key. Normal and active-only peers share one remote resource and are aggregated in software. Interconnect handoff clocks are not registered as regular consumer clocks here; they are temporarily voted to avoid premature gating before the interconnect framework initializes.

## Dependencies And Integration Points
The file depends on `linux/soc/qcom/smd-rpm.h`, RPM SMD request layout, RPM clock dt-bindings, common clock framework, OF providers, and platform-device creation. It integrates with many `qcom,rpmcc-*` compatibles from MSM8909 through SM6375/QCM2290, with RPM-managed NoC/BIMC clocks, XO buffer clocks, QDSS, CE/IPA/HWKM/PKA/QPIC resources, and the `icc_smd_rpm` interconnect driver.

## Risks And Edge Cases
Ordering around scaling and handoff is platform-specific; `msm8974` enables scaling first while most platforms do it after handoff. Branch and rate clocks use different RPM keys and value semantics, so a wrong macro or table entry can vote the wrong resource. Active-only peers must not hold sleep votes. The global RPM pointer and static objects assume a single RPM SMD clock-controller instance. Interconnect bootstrap clocks must match the later ICC topology or buses can be under-voted during driver ordering gaps. Provider lookup returns `-ENOENT` for sparse table entries, so bindings and tables must stay aligned.

## Test Signals
Signals include correct probe and clock registration for each compatible, RPM SMD writes with expected resource type/id/key/value, scaling writes in active and sleep sets, branch votes as 0/1, rate votes in kHz, active-only sleep votes of zero, successful creation and cleanup of `icc_smd_rpm`, valid sparse-index errors, and stable bus/interconnect clocks during early boot before ICC handover.
