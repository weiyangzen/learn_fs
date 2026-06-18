# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7786.c

Purpose: implements SH7786 platform setup for serial, timers, DMA, USB EHCI/OHCI, complex interrupt distribution, optional SCIF1 IRQ demux, and USB PHY initialization.

Important APIs, types, and functions: `sh7786_usb_setup()` performs USB register initialization and PHY/PLL polling. `sh7786_devices_setup()` runs USB setup, optionally replaces SCIF1 resources with demuxed IRQs using `intc_irq_lookup()`, registers early devices, then normal devices. `plat_early_device_setup()`, `plat_irq_setup()`, `plat_irq_setup_pins()`, and `plat_mem_setup()` provide platform hooks.

Control flow: early devices include SCIF0-5 and TMU0-3. Normal devices include DMA0 and USB host controllers. The main INTC descriptor maps internal sources including WDT, TMUs, DMAC, HUDI, HPB, SCIF, Ethernet, PCIe, USB, I2C, display, SSI, HAC, FLCTL, HSPI, GPIO, thermal, and inter-CPU interrupts. IRQ pin setup supports IRQ/IRL 3210 and 7654 modes. SCIF1 starts with a single IRQ, but after the main INTC is registered the device setup can install separate ERI/RXI/TXI/BRI IRQ resources.

State and persistence: USB setup writes persistent initial values to USBINIT registers and controls PHY/PLL bits. `sh7786_intc_desc` includes SMP balancing distribution registers. Platform device metadata can be mutated for SCIF1 demuxing. `plat_mem_setup()` is empty.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-dma-engine`, `sh_ehci`, `ohci-platform`, INTC SMP balancing, PFC/board external pins, and USB PHY hardware.

Risks: USB setup has a busy wait without timeout reporting if PLL never locks. SCIF1 demux depends on `intc_irq_lookup()` after descriptor registration. SMP interrupt distribution register masks must match CPU count. Re-registering early devices in `sh7786_devices_setup()` can conflict if call ordering changes.

Test signals: USB EHCI/OHCI enumeration and PHY lock log, SCIF1 interrupt demux behavior, TMU0-3 interrupts, DMA transfer tests, Ethernet/PCIe/USB interrupt delivery, SMP IPI distribution, and external IRQ/IRL mode tests.
