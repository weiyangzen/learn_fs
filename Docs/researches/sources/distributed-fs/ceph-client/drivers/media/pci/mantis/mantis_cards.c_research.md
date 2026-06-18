# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_cards.c

- Purpose: PCI entry point for the Mantis DVB bridge driver; binds supported TwinHan/TechniSat/TerraTec subsystem IDs to board-specific frontend configurations and coordinates all subsystem setup.
- Important APIs/types/functions: module parameter `verbose`, `mantis_irq_handler()`, `mantis_pci_probe()`, `mantis_pci_remove()`, `mantis_pci_table`, and `mantis_pci_driver`.
- Control flow: Probe allocates `struct mantis_pci`, installs the board IRQ callback, initializes PCI/MMIO, routes TS to HIF, registers I2C, reads EEPROM MAC, allocates DMA, registers DVB, input, and UART. Remove unwinds in reverse. The ISR acknowledges MMIO interrupt status, schedules DMA bottom-half work for RISC interrupts, wakes I2C/HIF waits, and schedules UART/HIF work.
- State and persistence: Runtime state lives in `struct mantis_pci`: interrupt masks/status, work items, DVB objects, I2C adapter, DMA buffers, CA state, and rc-core device. No disk persistence; EEPROM MAC is read but not copied into `mac_address` here.
- Dependencies and integration points: Integrates Linux PCI, IRQ, workqueue, rc-core, DVB demux/frontend/net, board configs from `mantis_vp*`, and local PCI/I2C/DMA/DVB/UART/input/CA modules.
- Risks: Shared IRQ handling depends on correct mask/status acknowledgement; IRQ0 assumes `mantis_ca` exists when CAM support is active; teardown must cancel work before freeing MMIO-backed state; `devs` monotonically increments and is not decremented.
- Test signals: Build with all referenced frontend modules; probe/remove on supported PCI IDs; exercise DMA demux, I2C frontend attach, IR UART IRQ, and CAM insert/remove interrupts while checking for lost IRQs or use-after-free on unload.
