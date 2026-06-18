# sources/distributed-fs/ceph-client/drivers/dma/xilinx/Makefile

## Purpose
This Makefile selects the Xilinx DMA-family objects built for the kernel based on Kconfig symbols. It is a build integration file, not runtime code.

## Important Entries
The file maps `CONFIG_XILINX_DMA` to `xilinx_dma.o`, `CONFIG_XILINX_XDMA` to `xdma.o`, `CONFIG_XILINX_ZYNQMP_DMA` to `zynqmp_dma.o`, and `CONFIG_XILINX_ZYNQMP_DPDMA` to `xilinx_dpdma.o`. The SPDX tag is `GPL-2.0-only`.

## Control Flow and State
There is no runtime control flow or persistent state. Kbuild evaluates the `obj-$(CONFIG_...)` assignments and includes the matching objects in the driver build.

## Dependencies and Integration Points
The integration point is the kernel Kbuild system and the corresponding Kconfig symbols. The `xdma.o` entry is the build hook for `sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c`.

## Risks and Test Signals
The main risk is configuration drift: if a source file is renamed, split, or gated by a different symbol, this Makefile must stay synchronized. Test signals are simple: build with each Xilinx DMA config enabled individually and together, and confirm the intended object files are compiled.
