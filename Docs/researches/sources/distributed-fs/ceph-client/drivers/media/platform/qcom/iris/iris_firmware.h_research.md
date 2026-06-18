# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.h

## Purpose
`iris_firmware.h` declares the core firmware lifecycle functions used by the Iris core and power-management paths.

## Important APIs, Types, And Functions
The exported API is `iris_fw_load(struct iris_core *core)`, `iris_fw_unload(struct iris_core *core)`, and `iris_set_hw_state(struct iris_core *core, bool resume)`.

## Control Flow
`iris_core_init()` calls `iris_fw_load()` during boot; `iris_core_deinit()` calls `iris_fw_unload()` during teardown. Runtime suspend/resume uses `iris_set_hw_state()` to inform the remote subsystem state before power transitions.

## State And Persistence Behavior
The API affects PAS authenticated firmware state, reserved memory content, TZ video memory protection, and remote subsystem state. The header owns no direct state.

## Dependencies And Integration Points
The header forward-declares `struct iris_core` and is included by core and HFI common code. Its implementation depends on Qualcomm firmware/SCM infrastructure.

## Risks And Test Signals
Callers must sequence firmware load only after required memory and power resources are available and unload only after sessions/queues are inactive. Suspend/resume and init/deinit tests are the main validation signals.
