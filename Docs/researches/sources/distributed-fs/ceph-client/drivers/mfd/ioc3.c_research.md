# sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c

Purpose: SGI IOC3 PCI MFD driver. It configures the IOC3 multifunction ASIC, demultiplexes internal interrupts through an IRQ domain, and creates platform children for Ethernet, serial, keyboard, one-wire, RTC, and LEDs depending on subsystem ID.

Important APIs/types/functions: `ioc3_mfd_probe()`, `ioc3_setup()`, `ioc3_irq_domain_setup()`, `ioc3_irq_handler()`, per-subsystem setup functions, `ioc3_infos`, and `struct ioc3_priv_data`.

Control flow: probe enables PCI, sets latency and DMA mask, maps BAR0, clears interrupts, reads PCI subsystem ID, selects a board-specific setup routine, optionally creates an IRQ domain/chained handler, and adds child devices. Remove clears IRQs, removes MFD children/domain, unmaps BAR, and disables PCI.

State and persistence: tracks mapped IOC3 registers, PCI device, IRQ domain, and chained parent IRQ. Hardware IRQ enables/status and GPIO mode registers are programmed during setup.

Dependencies and integration: depends on SGI IOC3 register definitions, PCI bridge `map_irq`, Linux IRQ domains, MFD core, and child drivers such as `ioc3-serial8250`, `ioc3-eth`, `ioc3-kbd`, RTC drivers, `sgi_w1`, and `ip30-leds`.

Risks: board-specific wiring determines interrupt mapping and child composition. Error paths attempt to free IRQ/domain resources and must match setup state. Serial setup changes UART mode and waits for hardware. Only the first pending internal IRQ is handled per chained entry.

Test signals: boot on IP27/IP30/MENET/CAD DUO variants, child resource offsets, chained IRQ delivery for serial/kbd, Ethernet IRQ passthrough, RTC probing, and bind/unbind resource cleanup.
