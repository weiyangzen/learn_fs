# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.h

Purpose: declares the software I2C fallback engine state, default timing constants, constructor, command submitter, and acquisition function.

Important APIs and types: constants set the default 50 kHz software I2C speed, 10 start retries, and 3000-unit timeout delay. `struct dce_i2c_sw` stores the current DDC, DC context, calculated clock delay, and selected speed. `dce_i2c_sw_construct()` initializes the context, `dce_i2c_engine_acquire_sw()` opens the DDC pins for bit-banging, and `dce_i2c_submit_command_sw()` executes a full `struct i2c_command`.

Control flow and integration: included by the top-level I2C facade and software backend. The software engine is usually stack-allocated by `dce_i2c_submit_command()` after hardware acquisition fails, then acquired and submitted through these declarations.

State and persistence: no external persistence. The active DDC pointer exists only while the software engine owns GPIO pins; the C file clears it during release.

Dependencies and risks: relies on `struct ddc`, `struct dc_context`, `struct resource_pool`, and `struct i2c_command` definitions from surrounding DC headers. Timing constants are hardware/protocol sensitive and should be validated with slow or clock-stretching sinks. Test signals are successful fallback EDID reads, repeated-start transactions, and clean DDC release after failures.
