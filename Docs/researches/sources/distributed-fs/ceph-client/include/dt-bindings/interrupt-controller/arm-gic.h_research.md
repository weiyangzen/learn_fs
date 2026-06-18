<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h

## Purpose
This common header defines ARM GIC interrupt specifier constants for SPI/PPI and extended SPI/PPI interrupt types, plus CPU target mask helpers.

## Important APIs, types, and functions
The API includes `GIC_SPI`, `GIC_PPI`, `GIC_ESPI`, `GIC_EPPI`, `GIC_CPU_MASK_RAW(x)`, and `GIC_CPU_MASK_SIMPLE(num)`. It also imports generic trigger flags from `irq.h`.

## Control flow
DTS interrupt specifiers reference these macros in the interrupt-controller cell format. The preprocessed cells are interpreted by GIC irqchip drivers while mapping interrupts.

## State and persistence
There is no state. The constants are stable DT binding ABI shared by many ARM platforms.

## Dependencies and integration points
It integrates with ARM GICv2/GICv3/GICv4 bindings, platform DTS interrupt descriptions, and the generic IRQ trigger flag header. CPU masks are relevant for PPI affinity encodings in older GIC bindings.

## Risks and test signals
Risks include wrong cell type selection, invalid CPU masks, and mixing extended interrupt types with controllers that do not support them. Test signals include `dtbs_check`, interrupt-controller probe, timer/PPI delivery, SPI device interrupts, and affinity handling on SMP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h -->
