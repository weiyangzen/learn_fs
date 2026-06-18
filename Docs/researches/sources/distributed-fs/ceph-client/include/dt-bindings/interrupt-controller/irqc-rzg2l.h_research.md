<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h

## Purpose
This binding header defines Renesas RZ/G2L family IRQC source IDs for NMI and IRQ0-IRQ7 lines.

## Important APIs, types, and functions
It exports `RZG2L_NMI` and `RZG2L_IRQ0` through `RZG2L_IRQ7`, with comments documenting that NMI maps to SPI0 and IRQ0-7 map to SPI1-8.

## Control flow
DTS files reference these constants in IRQC interrupt specifiers. The compiled numbers are translated by the RZ/G2L irqchip driver into GIC SPI routing and trigger configuration.

## State and persistence
No runtime state exists in the header. The mapping is persistent DT ABI.

## Dependencies and integration points
It integrates with Renesas RZ/G2L IRQC controller nodes, GIC parent interrupt routing, and board-level GPIO/peripheral interrupt declarations.

## Risks and test signals
Risks include off-by-one SPI mapping, using `RZG2L_NMI` for maskable IRQ semantics, and applying this map to an incompatible Renesas family. Test signals include DTS validation, NMI routing tests, IRQ0-7 edge/level tests, and irqdomain mapping traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h -->
