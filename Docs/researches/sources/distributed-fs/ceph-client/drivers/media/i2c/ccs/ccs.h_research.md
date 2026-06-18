# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs.h

## Purpose
`ccs.h` is the central private header for the CCS/SMIA sensor driver. It collects common constants, hardware configuration structures, module identity structures, media-bus format descriptors, subdevice wrappers, and the main `struct ccs_sensor`.

## Important APIs, Types, and Functions
Key constants include SMIA/SMIAPP version/profile values, reset delays, default I2C addresses, pad indices, and stream ID. `CCS_LIM()` and `CCS_LIM_AT()` wrap cached capability access. Important structs are `ccs_flash_strobe_parms`, `ccs_hwconfig`, `ccs_module_ident`, `ccs_module_info`, `ccs_csi_data_format`, `ccs_binning_subtype`, `ccs_subdev`, and `ccs_sensor`. It declares `ccs_replace_limit()` and `ccs_get_limit()`.

## Control Flow
The header implements no control flow, but its macros and structs shape the whole driver. `to_ccs_subdev()` and `to_ccs_sensor()` convert V4L2 subdev pointers back to driver state. Identity macros such as `CCS_IDENT_LQ()` initialize the module ID table used during probe.

## State and Persistence Behavior
`struct ccs_sensor` owns nearly all per-device runtime state: mutex, subdevices, hardware config, regulators/clock/GPIO/regmap handles, cached limits, parsed static data, frame format offsets, streaming flag, initialization flags, identity/quirk pointer, PLL state, valid link-frequency masks, and V4L2 control pointers. This is in-memory only and is destroyed on remove or probe failure.

## Dependencies and Integration Points
It includes V4L2 controls/subdev APIs, regmap, mutexes, generated CCS data/limit/register headers, quirk/register-access interfaces, PLL definitions, and legacy SMIAPP register definitions. It is included by all CCS driver implementation files in this subset.

## Risks and Edge Cases
The main state struct is shared across subdevices and protected by `sensor->mutex` except for V4L2 control internals as documented. Optional pointers such as `scaler`, `strobe_setup`, controls, static-data arrays, and GPIOs require null checks. Cached limit access depends on `ccs-core.c` initializing `ccs_limit_offsets[]` and `sensor->ccs_limits` before use.

## Test Signals
Compile coverage should catch structure/API drift across all CCS files. Runtime validation should exercise devices with and without scaler, static-data firmware, alternate I2C address, flash strobe, quirks, all control families, and all media graph subdevices.
