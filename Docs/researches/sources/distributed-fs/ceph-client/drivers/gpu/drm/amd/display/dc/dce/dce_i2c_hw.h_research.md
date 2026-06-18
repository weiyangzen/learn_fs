# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h

Purpose: defines hardware I2C status/action enums, timing/buffer constants, register/mask/shift metadata, transaction data, hardware-engine state, constructors, and public hardware submit/acquire functions.

Important APIs and types: enums describe I2C arbitration/status, operation results, and DCE transaction actions including normal and MOT reads/writes plus DP/DPCD actions. Constants define setup limits, buffer sizes, default speeds, reset lengths, and timeout clocks. `I2C_HW_ENGINE_COMMON_REG_LIST*()` and mask-list macros provide generation-specific register metadata. `struct i2c_request_transaction_data` is the internal request descriptor. `struct dce_i2c_hw` stores DDC pointer, transaction/buffer counters, frequency/defaults, engine id, setup/reset parameters, context, and register metadata. Public functions construct generation variants, submit hardware commands, and acquire an engine.

Control flow and integration: resource builders allocate one `dce_i2c_hw` per DDC-capable line and initialize it with this header's constructors. `dce_i2c.c` acquires and submits through the public functions. The header also shares `i2c_request_transaction_data` with the software backend for common request action/status meanings.

State and persistence: in-memory state persists across command submissions in the resource pool; hardware register state is managed by `dce_i2c_hw.c`. The `engine_keep_power_up_count` influences whether the engine is disabled during release.

Dependencies and risks: depends on generated register names, `struct ddc`, `struct resource_pool`, and DC context definitions from included compile units. Risks are enum value compatibility with hardware register encodings, optional DCN memory-power/clock-enable fields, and buffer-size differences by generation. Test signals include constructor defaults per ASIC, compile coverage for DCN30/DCN35/DCN401 mask lists, and acquisition/submission behavior under hardware contention.
