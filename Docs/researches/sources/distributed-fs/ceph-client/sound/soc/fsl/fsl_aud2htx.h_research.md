# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_aud2htx.h

## Purpose
`fsl_aud2htx.h` defines the AUD2HTX register map, bitfields, FIFO/DMA constants, supported audio formats, and private driver state used by `fsl_aud2htx.c`.

## Important APIs, Types, and Definitions
- `FSL_AUD2HTX_FORMATS` allows S24_LE, S32_LE, and IEC958 subframe little-endian playback.
- Register offsets cover control, extended control, write FIFO register, status, nonmasked IRQ flags, masked IRQ flags, and IRQ masks.
- Bit macros define block enable, DMA enable, DMA threshold selector, low/high watermark fields, and interrupt mask bits.
- FIFO constants set depth and both watermarks to 0x10, with DMA maxburst 0x10.
- `struct fsl_aud2htx` contains platform device, regmap, bus clock, and DMAengine DAI metadata.

## Control Flow and Usage
The header has no direct control flow. The C file uses register and field macros to initialize regmap, configure watermarks/interrupt masks, toggle trigger enable bits, and fill DMA parameters for writes to `AUD2HTX_WR`.

## State and Persistence
State is represented by hardware registers and the private structure. Regmap cache in the C file preserves register settings across runtime suspend.

## Dependencies and Integration Points
It assumes includers provide ASoC/DMAengine, regmap, clk, and platform-device type definitions. The format mask and DMA constants are part of the driver contract exposed through the DAI and DMAengine PCM registration.

## Risks and Edge Cases
- Field macros use raw shifts and masks; callers must pass values within hardware width.
- Watermark constants equal half FIFO depth; changing them affects DMA request behavior and underrun/overrun margin.
- The private struct contains RX DMA metadata although current DAI support is playback-only.

## Test Signals
- Compile-time use catches missing type includes from C files.
- Register write traces should show expected low/high watermark fields and IRQ mask bits.
