# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.h

## Purpose
Declares the E5010 hardware helper API used by the V4L2 driver and includes the core/MMU register maps.

## Important APIs, Types, and Functions
Prototypes cover IRQ enable/status/clear, clock gating, CRC, input source and geometry, luma/chroma/output DMA addresses, output size, strides, subsampling, chroma order, quantization table writes, reset, output max size, encode start, and MMU bypass.

## Control Flow
No implementation flow. It defines the call surface used by probe/init, mem2mem job programming, IRQ handling, and error reset.

## State and Persistence
No software state. Functions operate on caller-provided `void __iomem *` bases and hardware state.

## Dependencies and Integration Points
Includes `e5010-core-regs.h` and `e5010-mmu-regs.h`. Used by `e5010-jpeg-enc.c` and implemented by `e5010-jpeg-enc-hw.c`.

## Risks
Prototype/base naming uses `core_offset` but actual values are MMIO bases; misuse with wrong base region would program invalid registers. Header lacks include guards for Linux types itself and relies on includers or included register headers for `u32`, `bool`, and `struct device`.

## Test Signals
Compile coverage for both implementation and main driver, plus runtime tests for every declared helper via encode, IRQ, reset, and quality-control paths.
