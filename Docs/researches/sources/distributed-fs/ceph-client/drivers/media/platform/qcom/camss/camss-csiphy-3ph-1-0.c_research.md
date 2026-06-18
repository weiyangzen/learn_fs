
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c

## Purpose
Implements the 3-phase CSIPHY hardware operation table used by the common CAMSS CSIPHY subdev code. It knows the register layout, reset/interrupt sequence, lane mask calculation, settle-count programming, and SoC-specific lane register tables for gen1 and gen2 PHY blocks.

## Important APIs, Types, and Functions
`struct csiphy_lane_regs` encodes register address, data, optional delay, and parameter type. Large tables cover SDM845, SC8280XP, SM8250/7280, QCM2290/SM6150, SM8550, SM8650, SA8775P/SM8300, and X1E80100. The exported contract is `csiphy_ops_3ph_1_0`, filling `get_lane_mask`, `hw_version_read`, `reset`, `lanes_enable`, `lanes_disable`, `isr`, and `init`. Key helpers are `csiphy_settle_cnt_calc()`, `csiphy_gen1_config_lanes()`, `csiphy_gen2_config_lanes()`, `csiphy_is_gen2()`, and `csiphy_init()`.

## Control Flow
`csiphy_init()` allocates `csiphy->regs`, chooses the SoC table, and sets common register offsets. Power-on in `camss-csiphy.c` calls `reset()` and version read. Stream-on calls `get_lane_mask()` and `lanes_enable()`: it computes settle count from link frequency and timer clock, powers common control bits, programs either gen1 per-lane registers or the selected gen2 table, skips DNP/skew-cal entries, and disables/masks PHY interrupts. The ISR mirrors status bytes into clear registers, pulses common clear, and resets clear registers.

## State and Persistence
State is volatile hardware state plus the devm-owned `csiphy_device_regs` pointer. No persistent storage exists. Register ordering relies on relaxed I/O with explicit barriers in higher-level stream setup and in selected paths.

## Dependencies and Integration Points
Depends on `camss.h` SoC version IDs, `camss-csiphy.h`, Linux I/O and delay primitives, and the common CSIPHY subdev code. It integrates via resource tables that select `csiphy_ops_3ph_1_0`.

## Risks and Test Signals
Risks are table accuracy, lane-position interpretation, settle-count overflow/underflow, incomplete skew-cal support, and SoC offset mismatches. Test signals include a readable HW version, no reset/IRQ storms, correct lane enable masks for 1-4 data lanes, successful streams across supported link frequencies, and stable capture on each SoC table.
