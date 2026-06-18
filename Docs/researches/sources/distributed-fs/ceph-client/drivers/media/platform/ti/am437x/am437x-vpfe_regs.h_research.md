# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe_regs.h

## Purpose
Defines AM437x VPFE/CCDC register offsets and bit fields used by the capture driver.

## Important APIs, Types, And Functions
Offsets cover PCR, SYNMODE, timing/window registers, SDRAM address, clamp/black compensation, ALAW, BT.656 interface, CCDCFG, DMA control, sysconfig, config, and IRQ registers. Bit masks and shifts describe polarity, frame format, data size, pixel format, write enable, low-pass filter, ALAW, black clamp/compensation, latch behavior, line offsets, interlaced/progressive memory offsets, input data widths, BT.656 flags, interrupt bits, DMA overflow, and CONFIG enable/standby fields.

## Control Flow
No executable flow. The implementation uses these constants when restoring defaults, configuring raw/YCrCb capture, setting windows/stride, programming SDRAM addresses, enabling/disabling CCDC, and acknowledging interrupts.

## State And Persistence
The header describes mutable hardware register state; it stores no data itself.

## Dependencies And Integration Points
Consumed by `am437x-vpfe.h` and `am437x-vpfe.c`. It encodes the ABI between the driver and AM437x image sensor interface hardware.

## Risks
Incorrect masks or alignment constants can corrupt capture geometry, DMA stride, interrupt acknowledgement, or pixel packing. The driver relies on `VPFE_HSIZE_OFF_MASK`/32-byte alignment and `VPFE_REG_END` for context storage, so register-table changes must keep those users in sync.

## Test Signals
Hardware capture with known patterns, interrupt count behavior, stride alignment checks, DMA overflow reporting, raw and YCbCr mode validation, and suspend/resume context tests provide coverage beyond compilation.
