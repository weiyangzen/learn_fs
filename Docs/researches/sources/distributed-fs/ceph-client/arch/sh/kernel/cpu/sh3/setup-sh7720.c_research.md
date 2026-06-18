# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7720.c

## Purpose
`setup-sh7720.c` supports SH7720 and SH7721. It registers RTC, two SCIFs, OHCI USB host, SH UDC gadget, CMT, TMU, and a SoC-specific interrupt controller.

## Important APIs, Types, And Functions
Key devices are `rtc_device`, `scif0_device`, `scif1_device`, `usb_ohci_device`, `usbf_device`, `cmt_device`, and `tmu0_device`. INTC data includes `vectors`, `prio_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7720", ...)`. Hooks are `sh7720_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
Early boot registers SCIF, CMT, and TMU only. Normal `arch_initcall` registers the full list including RTC and USB devices. IRQ setup registers SH7720 INTC and then common SH3 external IRQ setup.

## State And Persistence
Static platform resources describe MMIO, IRQs, DMA masks, and RTC capabilities. Runtime state is held by bound USB, timer, RTC, and serial drivers.

## Dependencies And Integration Points
It uses `sh7720_sci_port_ops`, `usb_ohci_pdata`, `sh_timer_config`, `evt2irq()`, `sh_intc`, `asm/rtc.h`, and common SH3 IRQ setup. USB host/gadget drivers depend on the resources here.

## Risks
USB host/gadget share adjacent address space and separate IRQs; resource mistakes can cause probe conflicts. `CONFIG_CPU_SUBTYPE_SH7720` conditionally includes an SSL vector, so SH7721 builds need separate coverage. CMT uses an unusual low physical address resource.

## Test Signals
Early console and timer boot, OHCI enumeration, gadget controller probe, RTC operation, and `/proc/interrupts` entries for CMT/TMU/USB/SCIF validate integration.
