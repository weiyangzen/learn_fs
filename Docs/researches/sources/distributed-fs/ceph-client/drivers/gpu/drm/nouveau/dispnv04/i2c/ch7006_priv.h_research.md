<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h

## Purpose
This private header defines CH7006 driver state, TV norm/mode structures, register constants, bitfield helpers, module parameter declarations, and function prototypes shared by the CH7006 driver and mode calculation files.

## Important APIs, Types, and Functions
Important types are `fixed`, `enum ch7006_tv_norm`, `struct ch7006_tv_norm_info`, `struct ch7006_mode`, `struct ch7006_state`, and `struct ch7006_priv`. It defines `to_ch7006_priv`, logging macros, bitfield macros `bitf`, `bitfs`, `setbitf`, `unbitf`, interpolation and fixed rounding helpers, register load/save macros, hardware constants `CH7006_FREQ0`, `CH7006_MAXN`, `CH7006_MAXM`, and register/field definitions through `CH7006_VERSION_ID`.

## Control Flow
The header has no standalone flow, but its macros implement all register field packing/unpacking used by `ch7006_mode.c`. `interpolate` maps 0-100 user property values around a midpoint, and `round_fixed` converts 32.32 fixed-point values.

## State and Persistence Behavior
`struct ch7006_priv` owns the persistent per-encoder software state: configuration parameters, current mode pointer, register shadows, saved hardware state, DRM scale property, TV properties, chip version, and last DPMS state. `struct ch7006_state` mirrors the hardware register space.

## Dependencies and Integration Points
It includes DRM probe helpers and public Nouveau I2C encoder/CH7006 parameter headers. It is internal to the CH7006 module and feeds the external TV path in `tvnv04.c` through callback registration.

## Risks
The bitfield macros use the same `high:low` preprocessor idiom as Nouveau register headers and are easy to misuse. The register array is sized to `0x26`; new register constants beyond that would overrun if added carelessly. Property defaults and module parameters must remain consistent with DRM TV property ranges.

## Test Signals
Compile coverage for every macro use, mode-set tests that exercise all register fields, static analysis for register-index bounds, module parameter parsing, and save/load round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h -->
