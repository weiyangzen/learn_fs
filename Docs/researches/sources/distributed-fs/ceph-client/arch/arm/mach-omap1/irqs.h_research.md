<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h

## Purpose
Defines the legacy Linux IRQ number map for OMAP1510, OMAP1610, and OMAP7xx interrupt handler banks, including cascaded GPIO and MPUIO ranges.

## Important APIs, Types, and Functions
Exports `INT_*` macros, `IH2_BASE`, `IH_GPIO_BASE`, `IH_MPUIO_BASE`, `OMAP_IRQ_END`, `OMAP_IRQ_BIT()`, and optional `FIQ_START`.

## Control Flow
No runtime flow. The macros are consumed at compile time by platform-device resource tables, IRQ controller setup, PM wake masks, timers, serial, I2C, MMC, DMA, and USB code.

## State and Persistence Behavior
No state; it is the shared interrupt numbering contract for OMAP1.

## Dependencies and Integration Points
Depends on `NR_IRQS_LEGACY`. Integrates with `irq.c` legacy domain allocation, platform resources, and board files.

## Risks
Macro collisions or off-by-one cascade offsets cause drivers to request the wrong IRQ. The header mixes variants, so callers must choose CPU-specific names carefully.

## Test Signals
Compile all OMAP1 variant configs and boot hardware smoke tests for core device IRQs. Static checks should verify platform resources use variant-appropriate interrupt names.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/irqs.h -->
