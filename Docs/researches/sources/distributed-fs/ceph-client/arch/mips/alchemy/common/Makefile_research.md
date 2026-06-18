# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/Makefile

## Purpose
`arch/mips/alchemy/common/Makefile` defines the always-built common support objects for Alchemy Au1xx0/Au1300 SoCs. It collects firmware/PROM, timer, clock, platform-device, power, GPIO, setup, sleep, DMA, descriptor DMA, voltage-scaling, IRQ, and USB control code into the Alchemy platform build.

## Important APIs, Types, And Variables
The only build variable is `obj-y`, which appends `prom.o time.o clock.o platform.o power.o gpiolib.o setup.o sleeper.o dma.o dbdma.o vss.o irq.o usb.o`.

## Control Flow
When the Alchemy platform directory is included by Kbuild, every listed object is linked into the kernel for Alchemy builds. Runtime initialization order is then controlled by each object's initcall level and architecture hook names, not by this Makefile.

## State And Persistence
There is no direct runtime state. The persistent effect is object inclusion: the Alchemy kernel image always contains common PROM parsing, clock registration, platform-device population, sleep support, DMA frameworks, GPIO, IRQ, and USB control support.

## Dependencies And Integration Points
It depends on the Alchemy platform being selected by the surrounding architecture build. The listed objects provide functions consumed across the architecture: `prom_init()`, `plat_mem_setup()`, `arch_init_irq()`, `au_sleep()`, DMA exports, clock framework registration, and platform devices. Board files rely on these common objects for GPIO, UART, PCI, Ethernet, and reboot behavior.

## Risks
Because all objects are unconditional for Alchemy builds, code inside each file must self-filter by CPU type when hardware is not present. Removing an object can cause missing architecture hooks or unresolved exports; adding a heavyweight object unconditionally can affect every Alchemy board. Initcall dependencies are implicit and need to remain compatible with board setup, PCI scanning, and driver probing.

## Test Signals
Build any `MIPS_ALCHEMY` configuration and inspect that all listed common objects compile. Boot smoke tests should show clocks, IRQs, GPIO, UARTs, and board devices initializing in expected order. Linker failures for architecture hooks or exported Alchemy helpers usually point to this Makefile or object-list regressions.
