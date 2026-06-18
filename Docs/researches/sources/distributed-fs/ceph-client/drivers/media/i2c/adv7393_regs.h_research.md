<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h

## Purpose
`adv7393_regs.h` supplies ADV7393 register offsets, defaults, bit masks, output presets, SD timing constants, and control ranges for `adv7393.c`.

## Important APIs, Types, and Functions
- `struct adv7393_std_info` describes the SD standard bits, FSC value, and V4L2 standard ID.
- Register macros cover power/mode/DAC/soft-reset, HD mode, SD mode, SD timing, FSC, CGMS/WSS, hue, and brightness registers.
- Bit masks cover input mode, RGB/YUV output selection, SD brightness/WSS split, soft reset, HD timing/sync/filter controls, SD standard/filter/pedestal/square-pixel/pixel-valid controls, DAC output 1, and control min/max/defaults.

## Control Flow
No executable control flow is present. Constants are expanded into the ADV7393 driver's initialization and update paths.

## State and Persistence
The header has no state; default macros seed `adv7393_state` register shadows and hardware initialization.

## Dependencies and Integration Points
The header is local to the I2C media driver and assumes V4L2 standard ID types are available from the including source. It is coupled to the register semantics in `adv7393.c`.

## Risks
- Untyped macros and magic masks can be combined incorrectly by callers.
- Definitions for HD modes are mostly unused by the current C driver, increasing drift risk.
- Register defaults are a behavior contract; changing them affects probe-time hardware state.

## Test Signals
Compile coverage, register dump comparison after initialization, FSC register byte values for each standard, and checks that SD mode register 2 pedestal/DAC bits match output and standard selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h -->
