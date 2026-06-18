# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.c

## Purpose
Hardware access layer for the E5010 JPEG encoder. It wraps MMIO register field writes, busy polling, reset, MMU bypass, interrupt control/status/clear, clock/CRC/input setup, DMA base addresses, image dimensions, strides, quantization tables, output size, and encode start.

## Important APIs, Types, and Functions
`write_reg_field()` performs masked writes; `write_reg_field_not_busy()` waits for `JASPER_BUSY` to clear before programming most fields. Exported helper functions include `e5010_reset()`, `e5010_hw_bypass_mmu()`, interrupt enable/status/clear helpers, clock gating and CRC toggles, input source/address/subsampling/chroma-order setters, stride and image size setters, `e5010_hw_set_output_max_size()`, `e5010_hw_set_qpvalue()`, `e5010_hw_get_output_size()`, and `e5010_hw_encode_start()`.

## Control Flow
The main driver initializes the device by bypassing the MMU, configuring clocking/CRC/input source, and enabling IRQs. For each job it programs addresses, dimensions, strides, subsampling, chroma order, max output size, then starts encoding. On busy-programming errors it resets the core/MMU.

## State and Persistence
State is hardware MMIO state. No software state is kept except stack temporaries.

## Dependencies and Integration Points
Depends on Linux `io.h`, `iopoll.h`, device logging, `e5010-core-regs.h`, and `e5010-mmu-regs.h`. Called exclusively by the V4L2 E5010 driver.

## Risks
Busy polling uses atomic polling with a 50 ms timeout; long hardware operations may fail configuration. `e5010_hw_enable_manual_clock_gating()` ignores its `enable` argument and always writes 0, likely intentional for disabling but surprising. Address setters pass shift 0 with masks that encode alignment bits, so callers must already provide appropriately aligned DMA addresses.

## Test Signals
Register programming traces, reset timeout injection, output address error IRQ, picture done IRQ, quality-control QP table updates, MMU bypass verification, and encode start/complete tests.
