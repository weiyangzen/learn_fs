<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h

## Purpose
Defines Xtensa IRQ numbering constants and declares IRQ-domain mapping helpers.

## Important APIs, Types, And Functions
Defines `PLATFORM_NR_IRQS`, `XTENSA_NR_IRQS`, `NR_IRQS`, `XTENSA_PIC_LINUX_IRQ`, `irq_canonicalize`, and declares `migrate_irqs`, `xtensa_irq_domain_xlate`, `xtensa_irq_map`, `xtensa_map_ext_irq`, and `xtensa_get_ext_irq_no`.

## Control Flow
No inline runtime flow except identity `irq_canonicalize`. IRQ-domain code elsewhere uses the declarations to translate interrupt specifiers and map internal/external IRQs.

## State And Persistence
No owned state. IRQ domains and mappings are maintained by interrupt-controller code.

## Dependencies And Integration Points
Depends on variant interrupt count, platform extra IRQ count, Linux IRQ domains, and SMP migration support.

## Risks And Edge Cases
IRQ numbering reserves Linux IRQ 0 by offsetting hardware IRQs by one. Platform IRQ count must match external controller wiring. Device-tree translation must map internal/external IRQ cells correctly.

## Test Signals
Boot with device tree IRQ mappings, inspect `/proc/interrupts`, exercise external IRQ devices, and CPU hotplug IRQ migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/irq.h -->
