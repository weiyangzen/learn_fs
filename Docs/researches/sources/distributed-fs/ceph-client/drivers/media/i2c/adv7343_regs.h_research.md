<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h

## Purpose
`adv7343_regs.h` defines the ADV7343 encoder register offsets, reset/default values, bit masks, SD/HD mode constants, output power presets, and V4L2 control ranges used by `adv7343.c`.

## Important APIs, Types, and Functions
- `struct adv7343_std_info` binds an encoder SD standard value, FSC value, and V4L2 standard ID.
- Register macros cover power, mode select, mode register 0, DAC level, soft reset, HD mode registers, SD mode registers, FSC registers, CGMS/WSS, hue, and brightness.
- Bit masks define input mode, RGB/YUV output, soft reset, HD standards/sync/gamma/filter controls, SD standard/filter/pedestal/pixel-valid controls, and DAC disable bits.
- Control range macros define brightness, hue, and gain min/max/default values.

## Control Flow
There is no runtime code. The C driver consumes these constants to assemble init sequences and bitfield updates.

## State and Persistence
The header has no state. Default-value macros seed the driver's register shadows and initialization table, indirectly determining hardware state after probe.

## Dependencies and Integration Points
It expects V4L2 standard types to be visible through the including C file. It is tightly coupled to `adv7343.c` and the public platform data header.

## Risks
- Duplicate `ADV7343_SD_MODE_REG8_DEFAULT` definitions can hide accidental divergence.
- Untyped masks invite incorrect `&` versus `|` use in callers.
- Some HD constants are defined even though the driver path mostly programs SD output, so unused definitions may drift from datasheet expectations.

## Test Signals
Compile coverage plus hardware register dumps after probe are the main signals. Compare the init table and standard/output transitions against datasheet defaults, especially power-mode, SD mode 1/2, and FSC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h -->
