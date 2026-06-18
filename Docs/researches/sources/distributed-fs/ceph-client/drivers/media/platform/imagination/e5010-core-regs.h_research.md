# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-core-regs.h

## Purpose
Register map for the Imagination/Jasper E5010 JPEG encoder core. It defines offsets, masks, and shifts for core identity, interrupts, clock/reset, input control, MMU control, image size, buffer base addresses, output size, quantization tables, CRC, and total core byte size.

## Important APIs, Types, and Functions
Notable offsets include `JASPER_INTERRUPT_MASK_OFFSET`, `JASPER_INTERRUPT_STATUS_OFFSET`, `JASPER_RESET_OFFSET`, `JASPER_CORE_CTRL_OFFSET`, `JASPER_STATUS_OFFSET`, `JASPER_INPUT_CTRL0/1_OFFSET`, `JASPER_IMAGE_SIZE_OFFSET`, input/output base registers, output size/max size registers, luma/chroma quantization table offsets, CRC registers, and `JASPER_CORE_BYTE_SIZE`.

## Control Flow
No code flow. Hardware helper functions use these constants for read-modify-write and busy-polled register programming.

## State and Persistence
Represents volatile MMIO register layout only. The hardware stores programmed state while powered.

## Dependencies and Integration Points
Included by `e5010-jpeg-enc-hw.h` and used by `e5010-jpeg-enc-hw.c`. It pairs with `e5010-mmu-regs.h` for MMU control.

## Risks
Mask/shift mismatches can corrupt unrelated register fields. Address registers use alignment masks that must match DMA address requirements. Quantization table offsets must match the 64-entry table packing used by the driver.

## Test Signals
Hardware encode smoke tests, interrupt enable/status/clear tests, max-size overflow IRQ tests, QP table quality changes, and register trace comparison against vendor documentation.
