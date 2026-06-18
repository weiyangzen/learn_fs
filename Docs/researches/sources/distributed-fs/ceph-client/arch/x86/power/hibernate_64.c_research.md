<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c

## Purpose
Builds temporary 64-bit page tables for hibernation restore, including five-level paging support.

## Important APIs, Types, And Functions
`set_up_temporary_text_mapping()` maps the image kernel entry virtual address to its physical page. `set_up_temporary_mappings()` allocates a fresh PGD, maps restore text, identity-maps all `pfn_mapped` ranges through `kernel_ident_mapping_init()`, and stores `temp_pgt`. `swsusp_arch_resume()` calls setup, relocation, and assembly restore.

## Control Flow
The code allocates safe pages for required page-table levels, filters page protections through the default kernel mask, installs a large executable PMD for restore text, creates direct identity mappings for every mapped physical range, relocates restore code, and enters `restore_image()`.

## State And Persistence
Temporary page tables and relocated restore code are safe-page state consumed during the no-return restore sequence.

## Dependencies And Integration Points
Depends on x86_64 page-table APIs, LA57 detection, `kernel_ident_mapping_init()`, common hibernation globals, and `hibernate_asm_64.S`.

## Risks And Edge Cases
Five-level paging requires an extra P4D page. Page protection must avoid unsupported bits. Mapping only the final text page assumes relocated code handles the switch until the last jump.

## Test Signals
64-bit hibernate resume under 4-level and 5-level paging, with KASLR/large mappings, validates the page-table setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c -->
