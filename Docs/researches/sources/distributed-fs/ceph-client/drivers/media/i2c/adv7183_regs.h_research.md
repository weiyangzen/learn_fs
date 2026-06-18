<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h

## Purpose
`adv7183_regs.h` provides symbolic register offsets for the ADV7183 decoder. It is a pure local header used by `adv7183.c` to make register scripts, log-status dumps, controls, routing, standard detection, and debug access readable.

## Important APIs, Types, and Functions
The file exports preprocessor constants only. Major groups include input/output and autodetect registers (`ADV7183_IN_CTRL`, `ADV7183_VD_SEL`, `ADV7183_OUT_CTRL`, `ADV7183_AUTO_DET_EN`), controls (`CONTRAST`, `BRIGHTNESS`, `HUE`, saturation/offset), status/identity registers, clamp/filter/gain/ADC registers, sync/window/VBI registers, and SD timing/saturation/drive-strength registers.

## Control Flow
There is no runtime control flow. The header is included before use by `adv7183.c`, and constants are compiled into register reads/writes.

## State and Persistence
The header has no state. Its values define the hardware state locations that the driver reads and writes.

## Dependencies and Integration Points
It depends only on inclusion from C code that already has kernel integer types available if needed. The integration point is the ADV7183 register map expected by `adv7183.c`; mismatched constants would directly misprogram the chip.

## Risks
- Constants are untyped macros, so invalid use is not compiler-constrained.
- The header does not define masks or bit shifts for most fields; callers encode magic values in the C file.
- No register access width metadata is present, but the driver assumes all offsets are byte-addressable SMBus byte registers.

## Test Signals
Validation is by compile coverage and hardware behavior: log-status register names should match the datasheet, init-script writes should land on intended offsets, and debug register access should read expected identity/status values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h -->
