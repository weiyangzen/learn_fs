<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/goldfish.h -->
# sources/distributed-fs/ceph-client/include/linux/goldfish.h

Purpose: Provides helper functions for Goldfish virtual platform drivers to write host pointers or DMA addresses into split 32-bit MMIO registers.

Important APIs/types/functions: `gf_ioread32` and `gf_iowrite32` default to `ioread32`/`iowrite32` unless overridden. `gf_write_ptr()` writes lower 32 bits of a kernel pointer and, on 64-bit kernels, upper bits. `gf_write_dma_addr()` writes lower bits of a `dma_addr_t` and upper bits when DMA addresses are 64-bit.

Control flow: A driver passes low/high MMIO register addresses; helpers split the pointer/address and issue MMIO writes in low-then-high order.

State and persistence behavior: No kernel state is stored; effects persist in device MMIO registers according to virtual hardware behavior.

Dependencies and integration points: Depends on kernel bit helpers, types, and MMIO accessors. Used by Goldfish emulator device drivers.

Risks: Register ordering must match device specification. Pointer writes expose kernel virtual addresses to the virtual device and should be used only where the platform expects them. High register is untouched on 32-bit pointer/DMA configurations.

Test signals: Goldfish driver tests on 32-bit and 64-bit configurations, MMIO write tracing for low/high register values, and DMA address width build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/goldfish.h -->
