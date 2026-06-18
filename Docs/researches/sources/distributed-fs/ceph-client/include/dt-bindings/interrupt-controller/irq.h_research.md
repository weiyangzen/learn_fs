<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h

## Purpose
This common header defines generic interrupt trigger and polarity flag constants used by many device-tree interrupt bindings.

## Important APIs, types, and functions
It exports `IRQ_TYPE_NONE`, `IRQ_TYPE_EDGE_RISING`, `IRQ_TYPE_EDGE_FALLING`, `IRQ_TYPE_EDGE_BOTH`, `IRQ_TYPE_LEVEL_HIGH`, and `IRQ_TYPE_LEVEL_LOW`. There are no functions or structures.

## Control flow
Other binding headers and DTS files include this header, then place the numeric flags in interrupt specifier cells. IRQ domain code later translates the values into Linux IRQ trigger type flags.

## State and persistence
The file has no state. Its values are fundamental DT ABI and must remain unchanged.

## Dependencies and integration points
It is a dependency for controller-specific headers such as ARM GIC, Apple AIC, and MIPS GIC. It integrates with irqdomain translation, interrupt-controller schemas, and every DTS interrupt specifier using standard flags.

## Risks and test signals
Risks include combining level and edge values incorrectly, assuming `IRQ_TYPE_NONE` selects a default edge, or changing constants that are globally ABI-stable. Test signals include `dtbs_check`, interrupt trigger configuration in `/proc/interrupts`/debugfs, and hardware tests for rising, falling, both-edge, high-level, and low-level interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h -->
