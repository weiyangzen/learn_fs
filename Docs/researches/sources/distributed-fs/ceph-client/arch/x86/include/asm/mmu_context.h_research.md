# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu_context.h

## Purpose
Implements x86 address-space context lifecycle helpers: LDT management, LAM duplication, pkey duplication, context ID allocation, `switch_mm` declarations, and temporary-mm APIs.

## Important APIs, Types, And Functions
Defines optional `struct ldt_struct`, `init_new_context_ldt()`, `ldt_dup_context()`, `destroy_context_ldt()`, `load_mm_ldt()`, `switch_ldt()`, `mm_lam_cr3_mask()`, `dup_lam()`, `mm_untag_mask()`, `mm_reset_untag_mask()`, `arch_pgtable_dma_compat()`, `init_new_context()`, `destroy_context()`, `switch_mm()`, `switch_mm_irqs_off()`, `activate_mm`, `deactivate_mm`, `arch_dup_pkeys()`, `arch_dup_mmap()`, `arch_exit_mmap()`, `is_64bit_mm()`, `is_notrack_mm()`, `set_notrack_mm()`, `arch_vma_access_permitted()`, `__get_current_cr3_fast()`, `use_temporary_mm()`, and `unuse_temporary_mm()`.

## Control Flow
`init_new_context()` initializes the context lock, allocates a monotonic `ctx_id`, clears `tlb_gen`, initializes pkey defaults, global ASID, LAM untag mask, and LDT state. Fork duplication copies pkeys and LAM state then duplicates LDT. Exit tears down paravirt and LDT state. Context switch callers use `switch_mm_irqs_off()` and architecture-specific deactivate cleanup for GS/FS and shadow stacks.

## State And Persistence
State persists per `mm_struct`: context ID, TLB generation, LDT, LAM, pkeys, global ASID, and VDSO metadata. Temporary mm switching changes CPU CR3 state temporarily, not durable storage.

## Dependencies And Integration Points
Depends on pkeys, TLB flush tracing, paravirt, debug registers, GS segment, descriptors, LAM, shadow stacks, and generic mmu context. It integrates with scheduler context switching, fork/exec, `modify_ldt`, PKRU enforcement, DMA/SVA compatibility, and kernel temporary mapping code.

## Risks And Edge Cases
LAM masks are read locklessly during switch, so `READ_ONCE` semantics matter. LDT alias mappings are PTI-sensitive. Pkey enforcement only applies to current non-foreign VMAs. Context IDs must be monotonic and global ASID lifetime must match mm lifetime.

## Test Signals
Fork/exec stress, modify_ldt tests, LAM and pkey selftests, context-switch TLB tests, temporary-mm users, shadow-stack builds, and paravirt/Xen builds provide coverage.
