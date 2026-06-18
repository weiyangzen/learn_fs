<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/init.c

## Purpose
`init.c` allocates, relocates, protects, and publishes the x86 real-mode trampoline blob used for secondary CPU startup, real-mode restart, and ACPI wakeup paths.

## Important APIs, types, and functions
Key symbols are `real_mode_header`, `trampoline_cr4_features`, `trampoline_pgd_entry`, `load_trampoline_pgtable()`, `reserve_real_mode()`, `init_real_mode()`, and the early initcall `do_init_real_mode()`. `sme_sev_setup_real_mode()` adjusts the trampoline for SME/SEV-ES.

## Control flow
Early boot reserves low memory below 1 MiB, copies `real_mode_blob`, applies 16-bit segment and 32-bit linear relocations from `real_mode_relocs`, then fills `struct trampoline_header`. On 64-bit it prepares EFER, CR4, the trampoline lock, and a trampoline PGD that identity maps the low stub and imports kernel mappings. Later `set_real_mode_permissions()` marks the blob NX/RO except executable text.

## State and persistence behavior
Persistent state is the allocated low-memory real-mode area referenced by `real_mode_header`, the trampoline PGD entry, trampoline lock/header fields, and CR4 feature pointer used by CPU bring-up. SME hosts decrypt the trampoline pages.

## Dependencies and integration points
It depends on memblock allocation, page attribute APIs, CR3/CR4/TLB helpers, `asm/realmode.h`, SEV-ES AP jump-table setup, embedded data from `rmpiggy.S`, and the platform `x86_platform.realmode_init()` hook.

## Risks and edge cases
Low-memory allocation failure prevents SMP trampoline use. Relocation ordering is critical because the trampoline header is dereferenced only after relocation. PCID must be cleared before switching to the trampoline page table, and stale global TLB entries are explicitly flushed. SME/SEV setup is sensitive to encrypted/decrypted memory state.

## Test signals
Boot tests with SMP CPU bring-up, kexec/reboot paths, ACPI S3 resume, SME/SEV-ES guests/hosts, and page-permission debugging are the main signals. A missing low-memory reservation or bad signature/relocation should fail early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/init.c -->
