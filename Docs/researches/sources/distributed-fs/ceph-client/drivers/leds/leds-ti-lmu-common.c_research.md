# sources/distributed-fs/ceph-client/drivers/leds/leds-ti-lmu-common.c

Purpose: shared helper library for TI LMU LED drivers. It exports brightness, ramp, and firmware-property helpers used by chip-specific LMU LED drivers.

Important APIs, types, and functions: `ti_lmu_common_set_brightness()` writes 8-bit or 11-bit brightness using `ti_lmu_bank` register metadata. `ti_lmu_common_set_ramp()` converts configured ramp-up/down microseconds into packed register nibbles. `ti_lmu_common_get_ramp_params()` reads `ramp-up-us` and `ramp-down-us`. `ti_lmu_common_get_brt_res()` reads `ti,brightness-resolution` from device or child fwnode and clamps it to supported max.

Control flow: callers populate a `struct ti_lmu_bank` with regmap and register addresses, then call exported helpers during probe or LED callbacks. Brightness updates write LSB bits first for 11-bit mode, then the MSB register. Ramp conversion chooses the nearest entry from a fixed 16-value table.

State and persistence: no private state; all state is held by caller-owned `ti_lmu_bank` and hardware registers. The helper mutates ramp and max-brightness fields based on firmware properties.

Dependencies and integration points: regmap through `linux/leds-ti-lmu-common.h`, fwnode/property APIs, and exported GPL symbols.

Risks and test signals: test 8-bit versus 11-bit register writes, ramp table boundaries and nearest-neighbor behavior, missing property warnings, invalid brightness resolution clamping, and callers passing complete register metadata.
