# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/setup-sh7760.c

## Purpose
`setup-sh7760.c` describes SH7760 interrupts and platform devices for four serial ports and TMU.

## Important APIs, Types, And Functions
Important data includes `vectors`, interrupt `groups`, `mask_registers`, `prio_registers`, `intc_desc`, `intc_desc_irq`, SCIF0-2 platform devices, a SIM-as-SCI port, `tmu0_device`, `sh7760_devices_setup()`, `plat_early_device_setup()`, `plat_irq_setup_pins()`, and `plat_irq_setup()`.

## Control Flow
`arch_initcall` adds serial and timer devices. Early setup registers the same set for console/timer availability. Base IRQ setup registers `intc_desc`; board IRQ pin setup can enable IRLM in `INTC_ICR` and register `intc_desc_irq`.

## State And Persistence
The file registers static resources and writes interrupt-control mode bits. Runtime device state is owned by serial and timer drivers.

## Dependencies And Integration Points
It uses SH INTC, `sh-sci`, `sh-tmu`, raw I/O, and `evt2irq()`. The SIM card module is intentionally exposed as `PORT_SCI` with only base registers because the serial driver lacks SIM-specific support.

## Risks
The comment that MFI vector differs from the data sheet is a red flag for hardware validation. SIM resource sizing is deliberate; expanding it could break `regshift` calculation. Unsupported IRQ pin modes `BUG()`.

## Test Signals
Serial probes for SCIF0-2 and SIM/SCI, TMU tick behavior, IRQ delivery for grouped SCIF/SIM/MMCIF/DMABRG interrupts, and IRQ pin mode tests are key.
