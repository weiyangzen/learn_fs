# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.h

## Purpose
`iris_ctrls.h` declares the V4L2 control initialization and firmware property setter interface used by platform capability tables and stream setup.

## Important APIs, Types, And Functions
The header exports `iris_ctrls_init()`, `iris_session_init_caps()`, all named cap setter callbacks, and `iris_set_properties()`. These functions are referenced by platform data through `struct platform_inst_fw_cap.set`, by streamon paths, and by V4L2 control handling.

## Control Flow
Platform data associates firmware capability IDs with setter functions declared here. During session setup, `iris_set_properties()` sends fixed HFI config params and then invokes capability setters. During `S_CTRL`, `iris_op_s_ctrl()` may invoke the same callbacks dynamically.

## State And Persistence Behavior
The declarations mutate `inst->fw_caps[]`, `inst->hfi_rc_type`, stream/session HFI properties, and sometimes current format-derived values. The header does not own state directly.

## Dependencies And Integration Points
It includes `iris_platform_common.h` for capability types and forward-declares `iris_core` and `iris_inst`. It is an integration point between platform capability descriptions, controls, and HFI command generation.

## Risks And Test Signals
The public setter surface is broad and generation-sensitive. Build tests should catch stale declarations when platform tables change; runtime tests should validate that every callback referenced in platform data has the expected payload type for the active HFI generation.
