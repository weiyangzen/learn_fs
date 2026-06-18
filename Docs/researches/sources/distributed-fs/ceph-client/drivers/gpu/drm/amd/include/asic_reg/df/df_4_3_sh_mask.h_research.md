# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_4_3_sh_mask.h

## Purpose
`df_4_3_sh_mask.h` defines one-bit shift and mask macros for the DF 4.3 hardware assert mask low/high registers. These fields let the driver determine whether RAS poison mode is consistently enabled or disabled.

## Important APIs, Types, And Functions
The file exports `HWAssertMsk0` through `HWAssertMsk31` shifts and masks for `DF_CS_UMC_AON0_HardwareAssertMaskLow`, plus the same field range for `DF_NCS_PG0_HardwareAssertMaskHigh`. Each field maps to a single bit in a 32-bit register.

## Control Flow
The header is declarative. `df_v4_3_query_ras_poison_mode()` uses `REG_GET_FIELD` to read `HWAssertMsk0` and `HWAssertMsk1` from the low register and `HWAssertMsk28` and `HWAssertMsk31` from the high register. If all four are set it returns true; if all are clear it returns false; otherwise it warns and returns false.

## State, Persistence, And Dependencies
The macros describe persistent hardware state but keep no software state. They depend on AMD register-helper expansion conventions and on `df_4_3_offset.h` for the actual register addresses.

## Integration Points
The direct consumer is `drivers/gpu/drm/amd/amdgpu/df_v4_3.c`, where the result is published through `amdgpu_df_funcs.query_ras_poison_mode`. The field naming is intentionally aligned with the DF 3.6 assert-mask macros, allowing similar RAS logic across generations.

## Risks
Generated bitfield repetition creates off-by-one risk. If `HWAssertMsk28` or `HWAssertMsk31` is wrong, the warning logic may report inconsistent poison settings even on healthy systems. If low-register bits 0 or 1 are wrong, poison mode may be inverted or always false.

## Test Signals
Useful tests include `REG_GET_FIELD` extraction checks for representative low/high values, RAS poison-mode tests covering all set, all clear, and mixed states, and cross-generation comparison against DF 3.6 masks for the same logical assert bits.
