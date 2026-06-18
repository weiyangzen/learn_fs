# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/zc3xx-reg.h

## Purpose
`zc3xx-reg.h` is a register-name header for the ZC030x/ZC3xx GSPCA driver family. It maps numeric bridge register addresses to descriptive `ZC3XX_R...` macros so large register scripts and control code in `zc3xx.c` can use named addresses for frame size, sensor interface, I2C, exposure, gain, color matrix, gamma, sharpness, dead-pixel, and EEPROM operations.

The header has no executable logic. Its value is documentation and compile-time indirection: the same numeric register map can be shared across many sensor tables and mode paths without repeating raw hex addresses.

## Important APIs, Types, and Data
The file defines preprocessor macros only. The aliases are grouped by hardware function:

- System and operating registers: `ZC3XX_R000_SYSTEMCONTROL`, `ZC3XX_R001_SYSTEMOPERATING`.
- Picture size and clocking: `R002` through `R006`, plus JPEG clock/control `R008`.
- Frame retrieval/status: last acquisition time, monitor resolution, timestamps, frame lost, auto-adjust FPS, last frame state, and data counter.
- Stream/sensor control: CMOS sensor select, video status, and video control function.
- Sync and target size: horizontal sync registers and target picture-size bytes.
- Audio status registers.
- Sensor interface and bridge I2C: blanking, reset/gain/exposure address registers, I2C device address, command/status/address/value/read/write-ack registers.
- Windowing and sensor geometry: window start/width/height and first X/Y aliases.
- Exposure and gain: analog and digital gain, max/min gain, exposure time, black level, exposure limits, antiflicker registers.
- Auto exposure/white balance: AWB/AE status and freeze/unfreeze registers.
- Color statistics, RGB matrix, RGB gamma, luminance gamma, sharpness, dead pixel, and EEPROM registers.

## Control Flow
There is no runtime control flow in this header. The macros are consumed by C initializers and register-write functions in the companion ZC3xx driver. A typical path is a table entry in `zc3xx.c` using `{0xa0, value, ZC3XX_R...}` and a later table interpreter issuing the actual USB bridge write.

## State and Persistence
The header owns no state. It describes hardware state locations. Persistent behavior is determined by the C driver code that writes or reads these addresses. The macros themselves do not allocate memory, store device data, or change runtime behavior except through compile-time substitution.

## Dependencies and Integration Points
The header is GPL-2.0-only and is intended for inclusion by the ZC3xx GSPCA source. The comments say the register aliases came from an older zc0302 driver. The `rg` scan of this tree shows the macros are heavily used by `sources/distributed-fs/ceph-client/drivers/media/usb/gspca/zc3xx.c`, especially in sensor initialization tables and control paths.

This file sits at a hardware abstraction boundary: it does not hide register programming behind functions, but it gives names to addresses so the table-heavy driver remains reviewable.

## Risks and Edge Cases
Incorrect macro values would silently program the wrong bridge register wherever the alias is used. Since many uses occur in large static tables, a wrong alias can create broad camera regressions that are hard to trace.

The header contains a few spelling/uncertainty artifacts such as `COMPABILITYMODE` and `What is this ?` comments for `YTARGET`/`RESETLVL`. These should not be renamed casually because existing code may depend on the macro names.

The color matrix comment appears to contain channel-index inconsistencies in prose, so the numeric aliases should be trusted more than the explanatory formula unless hardware documentation confirms it.

Because the file has no include guard in the researched snapshot, it relies on normal include discipline or idempotent macro definitions. Multiple inclusion with identical definitions is usually harmless in C preprocessing but can produce redefinition warnings if values diverge.

## Test Signals
The primary test signal is successful compilation of `zc3xx.c` and any other includers. Functional test signals require hardware: correct stream start, frame size/windowing, I2C sensor access, exposure/gain/AWB changes, gamma/color behavior, sharpness, dead-pixel mode, and EEPROM access in the ZC3xx driver.

Static validation should check that every `ZC3XX_R...` macro used by `zc3xx.c` is defined and that no duplicate address aliases are accidental outside intentional high/low byte groupings. Hardware regression tests should focus on mode tables and controls that use the highest-risk register groups: I2C, exposure/gain, windowing, antiflicker, and color matrix/gamma.
