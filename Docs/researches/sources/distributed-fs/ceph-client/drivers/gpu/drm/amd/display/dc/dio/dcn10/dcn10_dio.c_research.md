# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.c

Purpose: Implements the small DCN10 DIO block-level memory power control object.

Important APIs/types/functions: `dcn10_dio_construct()` initializes a `struct dcn10_dio` with context, function table, and register metadata. `dcn10_dio_mem_pwr_ctrl()` writes `DIO_MEM_PWR_CTRL` and optionally forces I2C light sleep.

Control flow: Memory power control first writes `0` to `DIO_MEM_PWR_CTRL`, described as powering AFMT HDMI memory, then sets `I2C_LIGHT_SLEEP_FORCE` when requested. Constructor only stores pointers and function table.

State/persistence: Software state is register metadata and context. Hardware state is the DIO memory power control register and I2C light-sleep bit.

Dependencies/integration: Implements `struct dio_funcs` from `dio.h`; uses DC register helper macros.

Risks: The function name takes `enable_i2c_light_sleep` but always clears the whole register first, so callers must account for collateral bit resets. There is no read-modify preservation of unrelated fields.

Test signals: Register write traces for both `enable_i2c_light_sleep=false` and `true`, plus constructor/function-table smoke coverage.
