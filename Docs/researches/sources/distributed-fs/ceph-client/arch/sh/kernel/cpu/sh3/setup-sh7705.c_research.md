# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh7705.c

## Purpose
`setup-sh7705.c` registers SH7705 interrupt vectors and platform devices for two SCIF ports, TMU, and RTC.

## Important APIs, Types, And Functions
Important data includes `vectors`, `prio_registers`, `DECLARE_INTC_DESC(intc_desc, "sh7705", ...)`, `scif0_device`, `scif1_device`, `rtc_device`, `tmu0_device`, and setup hooks `sh7705_devices_setup()`, `plat_early_device_setup()`, and `plat_irq_setup()`.

## Control Flow
`arch_initcall` registers full platform devices. Early boot registers SCIF and TMU devices. `plat_irq_setup()` registers the subtype INTC descriptor and then calls common `plat_irq_setup_sh3()` for external IRQ pins.

## State And Persistence
The file contributes static resources and interrupt descriptors. Runtime hardware state is owned by the INTC, serial, TMU, and RTC drivers.

## Dependencies And Integration Points
It uses `sh770x_sci_port_ops`, `evt2irq()` event conversion, `sh-tmu-sh3`, `sh-rtc`, and the common SH3 interrupt-pin helper.

## Risks
SCIF device IDs and MMIO addresses are not numerically ordered by hardware naming, so driver aliases and console parameters must match. RTC resource bounds are small and IORESOURCE_IO-specific.

## Test Signals
Successful early console, TMU clockevent registration, RTC probe, and PINT/SCIF interrupt counts validate setup.
