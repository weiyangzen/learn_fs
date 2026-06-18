<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/vctrl-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/vctrl-regulator.c

Purpose: Implements a virtual output regulator whose voltage is linearly derived from a separate control regulator, with optional over-voltage-protection-aware downward ramping.

Important APIs and types: `struct vctrl_data` stores the registered regulator, dynamic descriptor, enabled flag, OVP threshold, minimum slew-down rate, control/output ranges, discrete mapping table, and current selector. `vctrl_calc_ctrl_voltage()` and `_calc_output_voltage()` convert between output and control voltage ranges. Continuous and discrete regulator ops are split into `vctrl_ops_cont` and `vctrl_ops_non_cont`.

Control flow: Probe parses DT ranges and OVP settings, obtains the `"ctrl"` supply, chooses continuous operations if the control regulator is continuous or lacks a selector table, otherwise builds a sorted control-to-output selector table and precomputes safe downward selector steps. It then drops the early consumer handle and lets regulator core manage the supply through `supply_name = "ctrl"`.

State and persistence: The driver stores a software enabled flag and selector cache for discrete mode. Actual voltage state persists in the upstream control regulator. OVP lowering loops step through intermediate voltages and sleep according to configured slew rate.

Dependencies and integration points: Depends on DT properties `regulator-min-microvolt`, `regulator-max-microvolt`, `ctrl-voltage-range`, optional `ovp-threshold-percent`, and `min-slew-down-rate`; regulator coupler/internal APIs; and the upstream control regulator.

Risks: Discrete `vctrl_set_voltage_sel()` computes delay after updating `vctrl->sel`, making the difference expression use the same selector on both sides and likely sleeping for zero time. If the current control voltage is inside range but not exactly in the table, selector initialization may leave `sel` at zero. OVP config requires a nonzero slew rate.

Test signals: Continuous and discrete control regulators, voltage conversion endpoints, OVP downward stepping, rollback on upstream failures, invalid DT ranges, selector initialization from existing control voltage, and enable/disable software state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/vctrl-regulator.c -->
