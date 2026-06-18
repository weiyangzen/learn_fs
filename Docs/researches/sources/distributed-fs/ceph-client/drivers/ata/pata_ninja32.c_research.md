# sources/distributed-fs/ceph-client/drivers/ata/pata_ninja32.c

`pata_ninja32.c` supports Ninja32/CardBus-like PATA controllers with a custom BAR0 layout. It exposes one BMDMA libata port, uses 32-bit PIO transfers, and manually programs controller control/timing registers.

`ninja32_set_piomode()` writes static timing bytes for PIO0-4 to BAR0 offset `0x1f` and caches the programmed device in `ap->private_data`. `ninja32_dev_select()` resets timing to a safe value, performs standard device select, and reapplies target PIO timing when switching devices. `ninja32_program()` writes magic initialization constants for IRQ control, burst/setup, wait bits, and BMDMA control.

Probe allocates a one-port host, enables PCI, maps BAR0, sets DMA mask, enables bus mastering, assigns taskfile/control/BMDMA addresses at fixed offsets, sets PIO32 flags, runs `ninja32_program()`, and activates with shared `ata_bmdma_interrupt()`. Resume repeats controller programming after PCI resume.

State is limited to BAR0 registers and `ap->private_data`. Dependencies are PCI managed mapping, DMA mask setup, and libata BMDMA/SFF. Risks include undocumented initialization bytes, shared timing between devices, fixed 40-wire cable reporting, and no explicit remove-time IRQ disable. Tests should cover listed PCI IDs, PIO mode switching, device-select timing reload, 32-bit PIO transfer, DMA interrupts, resume, and remove/hot-unplug behavior.
