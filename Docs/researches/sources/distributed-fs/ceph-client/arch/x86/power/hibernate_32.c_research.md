<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c

## Purpose
Builds temporary 32-bit page tables needed to restore a hibernated image.

## Important APIs, Types, And Functions
`resume_pg_dir` stores the temporary PGD. Helpers allocate resume-safe PMD/PTE pages, map all low physical memory at `PAGE_OFFSET`, map the image kernel restore text at its original virtual address, and `swsusp_arch_resume()` orchestrates the transition.

## Control Flow
Resume allocates a safe PGD, initializes PAE entries if needed, maps `restore_jump_address` to `jump_address_phys`, builds a physical/direct mapping up to `max_low_pfn` using PSE large pages where possible, publishes `temp_pgt`, relocates restore code, and calls assembly `restore_image()`.

## State And Persistence
Temporary page tables live on safe pages and are referenced by `temp_pgt` for assembly. They exist only for the no-return restore phase.

## Dependencies And Integration Points
Depends on x86 32-bit paging, PAE/PSE support, safe-page allocator, common hibernate globals, and `hibernate_asm_32.S`.

## Risks And Edge Cases
Failure after the final no-recover point cannot unwind. PAE first-level initialization must point unused entries to the zero page. Incorrect text mapping prevents jumping into the restored image kernel.

## Test Signals
32-bit hibernate resume with and without PAE/PSE and correct no-memory error handling before `restore_image()` validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c -->
