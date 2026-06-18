# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.h

This header declares the common bus interface used by b43 core code. `enum b43_bus_type` contains BCMA and/or SSB variants depending on configuration, and `struct b43_bus_dev` stores the native bus pointer, power/enable/read/write/block-I/O callbacks, flush-write flag, Linux device and DMA device, IRQ, board/chip/core metadata, and SPROM pointer.

Inline helpers identify PCI, PCMCIA, and SDIO host types by checking the configured bus type and native bus fields. The header also declares BCMA/SSB initializer functions and drvdata get/set helpers.

Runtime state is the `b43_bus_dev` instance created during bus-specific probe. It integrates with DMA, PHY, board-quirk, LED, and core setup code. Main risks are conditional enum differences across builds, misuse of the native union without checking `bus_type`, and stale `dma_dev` or `bus_sprom` pointers. Test signals are builds for BCMA-only, SSB-only, combined configs, host-type helper correctness, and vtable register I/O.
