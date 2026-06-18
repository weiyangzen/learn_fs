# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_local.h

## Purpose

`nv_local.h` centralizes environment-specific hardware access macros for the NVIDIA fbdev driver. It wraps raw MMIO reads/writes, VGA MMIO accesses, DMA command-buffer emission, FIFO put/get handling, memory barriers, and little-endian bit reversal for monochrome image data. The source was read as a complete 114-line file.

## Important APIs, Types, and Functions

The key macros are `NV_WR08`, `NV_RD08`, `NV_WR16`, `NV_RD16`, `NV_WR32`, `NV_RD32`, `VGA_WR08`, `VGA_RD08`, `NVDmaNext`, `NVDmaStart`, `_NV_FENCE`, `WRITE_PUT`, `READ_GET`, and `reverse_order`. These are macro APIs, not functions, and are used throughout `nv_hw.c`, `nv_setup.c`, `nv_accel.c`, and `nvidia.c`.

## Control Flow

There is no standalone flow. Callers use these macros inline to perform register I/O or emit DMA words. `NVDmaStart` checks DMA free space, calls `NVDmaWait()` when needed, emits a method header, and decrements free space. `WRITE_PUT` fences, reads framebuffer memory as a flush, writes the FIFO put pointer, and issues a memory barrier.

## State and Persistence Behavior

The macros mutate caller-owned `struct nvidia_par` fields such as `dmaCurrent`, `dmaFree`, and hardware FIFO registers. The header itself stores no state. `reverse_order` conditionally mutates a 32-bit word in-place on little-endian hosts.

## Dependencies and Integration Points

The header depends on Linux raw I/O helpers, barriers, optional x86 port I/O for `_NV_FENCE`, and `linux/bitrev.h` on little-endian builds. It intentionally keeps low-level access code separate from the more generic NVIDIA hardware logic.

## Risks and Edge Cases

Because most APIs are macros, argument side effects and type assumptions matter. Raw MMIO access bypasses endian conversion except where explicitly handled. `NVDmaStart` depends on an external `NVDmaWait()` symbol and must only be used in contexts where that helper exists. Incorrect barriers or FIFO put/get conversion can lead to lost commands or GPU lockups.

## Test Signals

Compiler coverage across endian and non-x86 architectures, accelerated rendering stress, FIFO wraparound tests, and sparse/build warnings around `__iomem` pointer arithmetic are useful signals.
