# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgtable.h

Purpose: Hexagon page-table bit layout, protection helpers, and swap encoding.

Important APIs/types/functions: functions: `set_pte`, `pmd_clear`, `pte_clear`, `pmd_none`, `pmd_present`, `pmd_bad`, `pte_none`, `pte_present`, `pte_mkold`, `pte_mkyoung`, `pte_mkclean`, `pte_mkdirty`, `pte_young`, `pte_dirty`, `pte_modify`, `pte_wrprotect`, `pte_mkwrite_novma`, `pte_mkexec`; macros: `_ASM_PGTABLE_H`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXECUTE`, `_PAGE_USER`, `_PAGE_PRESENT`, `_PAGE_DIRTY`, `_PAGE_ACCESSED`, `_PAGE_VALID`, `_PAGE_SWP_EXCLUSIVE`, `PGDIR_SHIFT`, `PTRS_PER_PGD`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/page.h`, `asm-generic/pgtable-nopmd.h`, `asm/vm_mmu.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.
