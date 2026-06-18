<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h

## Purpose
This minimal header reserves the SPARC hardware IRQ include path.

## Important APIs, Types, and Functions
It currently provides only the include guard and no declarations.

## Control Flow
Generic code can include `<asm/hw_irq.h>` without pulling additional SPARC definitions.

## State and Persistence Behavior
No runtime or build state is defined.

## Dependencies and Integration Points
It integrates with generic IRQ code that expects an architecture `hw_irq.h` header.

## Risks
The main risk is accidental addition of declarations that conflict with generic IRQ handling.

## Test Signals
Full SPARC builds with IRQ-related configs enabled ensure the empty header remains sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/hw_irq.h -->
