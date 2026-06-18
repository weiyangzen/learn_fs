# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx_reg.h

## Purpose
Defines MB862xx/MB86297 framebuffer, display, capture, I2C, host, DRAM controller, and interrupt register offsets and bit constants.

## Important APIs, Types, and Functions
- Base offsets such as `MB862XX_MMIO_BASE`, `MB862XX_DISP_BASE`, and Carmine-specific register windows.
- Display controller registers such as `GC_DCM1`, `GC_L0M`, `GC_HDB_HDP`, `GC_VTR`, palette, cursor, layer, and capture registers.
- I2C register and bit definitions such as `GC_I2C_BCR`, `I2C_START`, `I2C_REPEATED_START`, `I2C_BER`, and `I2C_LRB`.
- Carmine DRAM initialization constants and clock/interrupt constants.

## Control Flow
No executable control flow. The main driver, I2C adapter, and acceleration code use these constants to address hardware registers through `inreg()` and `outreg()`.

## State and Persistence
No state in the header. The defined registers represent persistent device hardware state when written by driver code.

## Dependencies and Integration Points
Included by all MB862xx implementation files. It is the shared hardware contract for platform/PCI setup, display programming, capture layer controls, I2C transfers, and interrupt handling.

## Risks
Incorrect offsets or masks can corrupt unrelated hardware blocks. Some constants are board-specific evaluation-board values, especially Carmine DRAM timings. The header combines multiple chip generations, so call sites must select offsets based on `par->type` and mapped base windows correctly.

## Test Signals
Build tests ensure all MB862xx sources agree on names. Runtime signals include correct chip identification, successful display timing programming, working I2C, stable capture layer setup, and interrupt acknowledge behavior on both CoralP/Lime and Carmine paths.
