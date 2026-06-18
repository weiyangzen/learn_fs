# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_mmu.h

Purpose: Hexagon VM MMU PDE/PTE encoding constants.

Important APIs/types/functions: macros: `_ASM_VM_MMU_H`, `__HVM_PDE_S`, `__HVM_PDE_S_4KB`, `__HVM_PDE_S_16KB`, `__HVM_PDE_S_64KB`, `__HVM_PDE_S_256KB`, `__HVM_PDE_S_1MB`, `__HVM_PDE_S_4MB`, `__HVM_PDE_S_16MB`, `__HVM_PDE_S_INVALID`, `__HVM_PDE_PTMASK_4KB`, `__HVM_PDE_PTMASK_16KB`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.
