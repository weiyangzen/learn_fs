# sources/distributed-fs/ceph-client/drivers/soc/qcom/ramp_controller.c

## Purpose

`ramp_controller.c` programs the Qualcomm Ramp Controller on MSM8976-class hardware. The controller handles hardware-managed ramp-up/down behavior after SoC-specific SID configuration is written.

## Important APIs, Types, and Functions

`struct qcom_ramp_controller_desc` stores SoC-specific register sequences for DFS, link, LMH, enable, disable, counts, and command-register offset. `struct qcom_ramp_controller` stores the regmap and selected descriptor. Core helpers are `rc_wait_for_update()`, `rc_set_cfg_update()`, `rc_write_cfg()`, `rc_ramp_ctrl_enable()`, and `qcom_ramp_controller_start()`. Probe/remove perform MMIO regmap setup and start/disable sequences.

## Control Flow

Probe maps MMIO, allocates state, fetches OF match data, initializes a 32-bit regmap, stores drvdata, and calls `qcom_ramp_controller_start()`. Start writes LMH SIDs, DFS SIDs, link SIDs, then enables ramp control. Each config write waits for controller readiness, writes a reg sequence, and triggers config updates from the last SID downward. Remove writes the disable sequence and logs if it fails.

## State and Persistence Behavior

Driver state is devm-managed. Hardware state persists in ramp-controller registers after probe; the driver has no runtime management beyond disabling on remove. There is no software cache of current register values.

## Dependencies and Integration Points

The driver depends on platform MMIO, regmap, OF match data, initcall ordering, and hard-coded MSM8976 register sequences. It suppresses bind attrs, implying dynamic unbind/rebind is not intended as a normal control path.

## Risks and Edge Cases

`rc_set_cfg_update()` writes `ce` with `regmap_set_bits()`, which treats `ce` as a bitmask, not an arbitrary field value; this matches only if configuration-entry numbers are bit positions or low bits intended by hardware. The ack computation uses `FIELD_PREP(RC_CFG_ACK, BIT(ce))`; large `ce` values could overflow the 16-bit ack field, though current constants fit. Remove cannot recover from a failed disable sequence. Adding SoCs requires exact sequence counts and register limits.

## Test Signals

Tests should include successful probe register trace, timeout in readiness and ACK polling, failed regmap writes, remove disable sequence, invalid/missing match data, and hardware readback that confirms each SID update and final enable state.
