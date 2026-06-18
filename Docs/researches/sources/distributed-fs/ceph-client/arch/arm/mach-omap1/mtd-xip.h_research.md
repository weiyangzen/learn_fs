<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h

## Purpose
Supplies OMAP1 architecture primitives for MTD execute-in-place delay and idle handling without relying on normal kernel services that may be unavailable while flash is busy.

## Important APIs, Types, and Functions
Defines `xip_omap_mpu_timer_regs_t`, `xip_omap_mpu_timer_read()`, `xip_irqpending()`, `xip_currtime()`, `xip_elapsed_since()`, and `xip_cpu_idle()`.

## Control Flow
XIP delay code reads MPU timer 0, computes elapsed time from the inverted down-counter, checks pending unmasked IH1 interrupts, and can idle the CPU with ARM CP15 wait-for-interrupt.

## State and Persistence Behavior
No persistent software state. It directly observes MPU timer and interrupt-controller hardware state through OMAP1 IO mappings.

## Dependencies and Integration Points
Included indirectly by `linux/mtd/xip.h`; depends on `hardware.h`, `omap1-io.h`, MPU timer register layout, and IH1 interrupt registers.

## Risks
The elapsed-time conversion is explicitly approximate and timer-frequency dependent. Because it is used in constrained XIP contexts, calling normal kernel APIs here would be unsafe; all macros must remain low-level.

## Test Signals
Build XIP-enabled OMAP1 kernels and run flash erase/program operations while confirming timer delays, interrupt pending detection, and idle wake behavior do not hang.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/mtd-xip.h -->
