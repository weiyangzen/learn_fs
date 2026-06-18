<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h

## Purpose
Small compatibility include that pulls OMAP1 hardware and IRQ definitions together while noting that `linux/soc/ti/omap1-soc.h` can replace it once drivers are fixed.

## Important APIs, Types, and Functions
No new symbols. It includes `hardware.h`, `irqs.h`, and `asm/irq.h`.

## Control Flow
No runtime flow. It is an include aggregation point.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Provides transitive access to hardware and IRQ constants for many mach-omap1 files.

## Risks
Because it is a broad include, removing or changing it can expose hidden include-order dependencies. It also perpetuates legacy local header coupling.

## Test Signals
Compile all mach-omap1 users after any include cleanup and check that CPU predicates, IRQ constants, and register definitions remain visible where needed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/soc.h -->
