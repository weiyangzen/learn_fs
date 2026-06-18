# sources/distributed-fs/ceph-client/drivers/clk/qcom/common.h

## Purpose
Declares the shared Qualcomm clock-controller data structures, constants, and helper APIs implemented by `common.c` and consumed by SoC-specific qcom clock drivers. It defines the descriptor contract that lets generated-style controller files register clocks, resets, GDSCs, interconnect clocks, RPM runtime behavior, and optional preconfiguration data through one common probe path.

## Important APIs, Types, And Functions
- PLL FSM constants define bit positions and masks for bias count, lock count, FSM enable, and FSM reset fields used by `qcom_pll_set_fsm_mode`.
- `struct qcom_icc_hws_data` links an interconnect master/slave pair to a clock id in the descriptor clock table.
- `struct qcom_cc_driver_data` supplies optional alpha PLLs to configure, CBCRs to force-enable, DFS RCG descriptors, and a driver-specific register-configuration callback.
- `struct qcom_cc_desc` is the top-level controller descriptor: regmap config, regmap clocks, resets, GDSCs, standalone `clk_hw`s, interconnect hardware data, RPM runtime flag, and driver-data pointer.
- `struct parent_map` maps logical parent sources to hardware mux config values.
- The header exports frequency lookup, parent lookup, board/sleep clock registration, regmap mapping, and common probe helpers.

## Control Flow
There is no executable control flow in the header. SoC-specific drivers fill static instances of `qcom_cc_desc` and optional `qcom_cc_driver_data`, then call `qcom_cc_probe`, `qcom_cc_probe_by_index`, or `qcom_cc_really_probe`. Clock implementation files call frequency and parent helpers from their rate and mux operations.

## State And Persistence
The header itself stores no runtime state. Its structures describe state owned by controller drivers and `common.c`: clock arrays, reset maps, GDSC lists, interconnect data, and optional initialization hooks. Hardware persistence is indirect through the consumers of these declarations.

## Dependencies And Integration Points
It forward-declares key kernel and qcom types instead of including all implementation headers. It integrates SoC clock-controller files with regmap, platform devices, reset maps, GDSCs, alpha PLLs, RCG DFS data, common-clock hardware, and optional interconnect clock support.

## Risks And Edge Cases
Descriptor arrays must align with dt-binding indexes, and counts must match the actual array sizes. `icc_hws[*].clk_id` must reference a registered clock. Setting `use_rpm` changes runtime-PM behavior in common probe. Missing `driver_data` is valid, but partially filled PLL data is not. Because this header forward-declares several structs, implementation files must include the concrete subsystem headers before dereferencing fields.

## Test Signals
Useful signals are build coverage across many qcomcc drivers, static analysis for descriptor count/index mismatches, probe success for descriptors with and without GDSCs/resets/interconnect clocks, and compile-time detection when new fields require updated initializers.
