# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mem-layout.h

Purpose: Hexagon virtual-memory layout constants and fixmap ranges.

Important APIs/types/functions: types: `fixed_addresses`; macros: `_ASM_HEXAGON_MEM_LAYOUT_H`, `PAGE_OFFSET`, `PHYS_OFFSET`, `PHYS_PFN_OFFSET`, `ARCH_PFN_OFFSET`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `MIN_KERNEL_SEG`, `VMALLOC_START`, `VMALLOC_OFFSET`, `FIXADDR_TOP`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/const.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
