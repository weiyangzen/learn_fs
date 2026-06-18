<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c

## Purpose
Provides common x86 hibernation header, image integrity checks, relocated restore-code setup, and SMT resume handling.

## Important APIs, Types, And Functions
`pfn_is_nosave()` identifies nosave pages. `struct restore_data_record` stores magic, restore jump addresses, CR3, and E820 checksum. `arch_hibernation_header_save/restore()` serialize and validate this data. `relocate_restore_code()` copies `core_restore_code` to a safe executable page. `arch_resume_nosmt()` rescans hlt-sleeping SMT siblings.

## Control Flow
Save writes architecture header values, masking PCID bits from CR3. Restore verifies magic and E820 CRC before accepting jump/CR3 values. Resume allocates a safe page, copies restore code, clears NX on the page mapping, flushes TLBs, and later bitness-specific code jumps into `restore_image()`.

## State And Persistence
Global visible symbols carry restore jump address, physical jump address, restore CR3, temporary page-table address, and relocated restore-code address between C and assembly. The hibernation image persists the header on disk/swap.

## Dependencies And Integration Points
Depends on hibernation core, E820 firmware table, safe-page allocator, page-table APIs, TLB flush, bitness-specific hibernate code, and CPU hotplug SMT helpers.

## Risks And Edge Cases
E820 changes between hibernate and resume reject the image. Executability changes must handle leaf mappings at several levels. PCID bits in CR3 must be cleared to avoid illegal CR4/CR3 transitions.

## Test Signals
Successful hibernate image save/restore, rejection of mismatched headers/maps, and SMT sibling recovery after resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c -->
