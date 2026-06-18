# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_reg.h

## Purpose
`et8ek8_reg.h` defines the data contract shared between the ET8EK8 sensor driver and the compiled register/mode tables in `et8ek8_mode.c`. It provides mode metadata, register sequence element formats, reglist type identifiers, and the external `meta_reglist` symbol.

## Important APIs, Types, and Data
- `struct et8ek8_mode` describes sensor array dimensions, active sensor window, output dimensions, output window, `pixel_clock`, `timeperframe`, `max_exp`, `bus_format`, and fixed-point `sensitivity`.
- Register entry type constants are `ET8EK8_REG_8BIT`, `ET8EK8_REG_16BIT`, `ET8EK8_REG_DELAY`, and `ET8EK8_REG_TERM`.
- `struct et8ek8_reg` carries a register operation type, 16-bit register offset, and up-to-32-bit value.
- Reglist type constants divide sensor lifecycle and feature lists: standby, power-on, resume, stream on/off, disabled, mode, lens-shading enable/disable, and auto-noise-reduction enable/disable.
- `struct et8ek8_reglist` combines a type, a mode descriptor, and a flexible `regs[]` array.
- `struct et8ek8_meta_reglist` carries a version string and a flexible table of reglist pointers; `meta_reglist` is declared `extern`.

## Control Flow
The header has no runtime logic. It shapes the consumer driver's control flow by defining the sentinel-based register walk (`ET8EK8_REG_TERM`) and the list classification (`ET8EK8_REGLIST_*`) that tells the driver whether a sequence is a mode, power-on sequence, stream transition, or feature toggle.

## State and Persistence
The structures are storage definitions for persistent compiled-in mode/register data. The header itself owns no device state. Values such as `timeperframe`, `max_exp`, and `sensitivity` become the initial truth used by V4L2 enumeration and control setup in the main driver.

## Dependencies and Integration Points
- Includes Linux I2C and V4L2 type headers plus `linux/types.h`.
- Forward-declares V4L2 media-bus structs for compatibility with the main ET8EK8 code.
- Integrated directly with `et8ek8_mode.c` through the `meta_reglist` declaration.
- The flexible-array layout requires static initializers to be defined carefully in C files.

## Risks
- This is a shared ABI within the driver; changing field order, type widths, constants, or sentinel values requires synchronized changes in every consumer and mode table.
- `struct et8ek8_reglist` and `struct et8ek8_meta_reglist` use flexible arrays; misuse with stack allocation or wrong terminators can cause memory overruns.
- `ET8EK8_MAX_LEN` bounds the version string; longer version text in a table initializer would be truncated or rejected depending on initializer form.
- The comment says "smia_reglist" although the symbols are ET8EK8, suggesting inherited code and a need for cautious semantic review.

## Test Signals
- Compile coverage should catch mismatched field names and initializer shape between mode table and header.
- Static analysis should focus on consumers walking `regs[]` and `reglist[]` sentinels.
- Runtime media enumeration should confirm `struct et8ek8_mode` fields produce coherent formats, frame sizes, and control ranges.
