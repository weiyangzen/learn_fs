# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irqflags.h

Purpose: local interrupt enable/disable/save/restore over Hexagon VM calls.

Important APIs/types/functions: functions: `arch_local_save_flags`, `arch_local_irq_save`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_irq_restore`; macros: `_ASM_IRQFLAGS_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/hexagon_vm.h`, `linux/types.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
