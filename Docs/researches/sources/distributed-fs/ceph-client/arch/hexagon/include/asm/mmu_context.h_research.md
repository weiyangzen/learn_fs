# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu_context.h

Purpose: Hexagon mm activation and context-switch hooks.

Important APIs/types/functions: functions: `switch_mm`, `activate_mm`; types: `task_struct`; macros: `_ASM_MMU_CONTEXT_H`, `activate_mm`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/mm_types.h`, `asm/setup.h`, `asm/page.h`, `asm/pgalloc.h`, `asm/mem-layout.h`, `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
