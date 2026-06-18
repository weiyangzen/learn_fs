# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7757.c

Purpose: provides SH7757 platform setup for SCIF, TMU, SPI/RSPI, four DMA engines, USB host controllers, interrupt descriptors, and a small URAM memory node.

Important APIs, types, and functions: `sh7757_devices_setup()` registers all devices; `plat_early_device_setup()` registers SCIF2-4 and TMU0 early; `plat_irq_setup()` registers the main `intc_desc`; `plat_irq_setup_pins()` supports IRQ7654/3210 and IRL7654/3210 modes with optional masking; `plat_mem_setup()` registers URAM with `setup_bootmem_node()`.

Control flow: platform resources describe three SCIF ports, TMU0, SPI0/1, RSPI, EHCI/OHCI, and DMA0-3. DMA tables provide separate slave configs and pdata per engine. Default IRQ setup masks external IRQ/IRL lines and registers core vectors; board pin setup selects extra descriptors for external pins.

State and persistence: static DMA, device, and interrupt metadata persists after registration. `plat_mem_setup()` adds node 1 for `0xe55f0000-0xe5610000`. INTC mask/prio registers and DMA controller state are hardware-backed.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh_spi`, `rspi`, `sh-dma-engine`, `sh_ehci`, `ohci-platform`, SH PFC for pin modes, and the INTC core.

Risks: the four DMA engines share some IRQs and use `IORESOURCE_IRQ_SHAREABLE`, making interrupt routing sensitive. External IRQ mode selection writes ICR0 bits directly. URAM node bounds are fixed and must not overlap RAM maps.

Test signals: test DMA clients across each engine, SPI and RSPI transfers, EHCI/OHCI enumeration, early console/timers, all external IRQ/IRL pin modes, and memory node registration.
