<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h

## Purpose
This small header defines MIPS GIC interrupt specifier type constants for shared and local interrupt sources.

## Important APIs, types, and functions
It includes generic `irq.h` flags and exports `GIC_SHARED` and `GIC_LOCAL`. There are no functions or data structures.

## Control flow
MIPS DTS interrupt specifiers use these constants to indicate whether an interrupt is a shared GIC source or a CPU-local source. The MIPS GIC irqchip consumes the resulting numeric cells during IRQ domain translation.

## State and persistence
The header is stateless. Its values persist in platform DTBs.

## Dependencies and integration points
It integrates with MIPS GIC interrupt-controller bindings, generic trigger flags, timer/per-CPU local interrupts, and shared device interrupts.

## Risks and test signals
Risks include mixing local and shared specifier formats and using generic ARM GIC constants by mistake. Test signals include DTS preprocessing, MIPS GIC probe, local timer interrupt delivery, and shared peripheral interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h -->
