# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-enet.c

Purpose: BCM63xx platform-device registration for the `enet` hardware block.

Important APIs and functions: exported/init functions include register_shared. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `enet`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, linux/export.h, bcm63xx_dev_enet.h, bcm63xx_io.h, bcm63xx_regs.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `enet` block.
