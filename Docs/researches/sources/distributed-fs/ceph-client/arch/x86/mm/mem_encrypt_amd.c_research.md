# sources/distributed-fs/ceph-client/arch/x86/mm/mem_encrypt_amd.c

## Purpose
This file implements AMD-specific memory encryption mechanics for SME, SEV, SEV-ES, and SEV-SNP: early encrypt/decrypt operations, page-table C-bit transitions, SNP RMP state changes, hypervisor notifications, boot-data mapping, and decrypted memory cleanup.

## Important APIs, Types, and Functions
- Globals `sme_me_mask`, `sev_status`, and `sev_check_data` live in `.data` for very early boot and are exported or PIC-aliased.
- `sme_early_encrypt()` and `sme_early_decrypt()` call `__sme_early_enc_dec()` for early in-place content conversion.
- `early_set_memory_decrypted()` and `early_set_memory_encrypted()` alter early direct-map page encryption attributes.
- `prepare_pte_enc()` and `set_pte_enc_mask()` support later encryption attribute changes by computing PFN/protection state and updating PTEs.
- `sme_early_init()` installs encryption masks, protection-map changes, SNP/SEV hooks, and feature-specific boot workarounds.
- `sme_map_bootdata()` and `sme_unmap_bootdata()` map or unmap boot params and command line under SME.
- `mem_encrypt_free_decrypted_mem()` re-encrypts and frees unused decrypted BSS pages.

## Control Flow and State
Early encryption maps source and destination aliases with encrypted/decrypted protections, copies through a cache-line-safe temporary buffer, and for SNP transitions pages shared/private around copies. Large page attribute changes may split mappings through `kernel_physical_mapping_change()` before updating PTE/PMD/PUD entries and flushing TLBs. `sme_early_init()` propagates the C-bit into early PMD flags and supported PTE masks, registers guest encryption hooks, disables parallel bring-up for SEV-ES, disables IA32 emulation for SEV, and suppresses unsafe ROM/table scans for SNP.

## Dependencies and Integration Points
The file depends on early memremap encrypted/decrypted variants, SNP RMP helpers, set-memory/CPA, TLB/cache flushes, boot parameters, x86 platform hooks, SEV GHCB/SNP helpers, and `mm_internal.h` direct-map splitting. It feeds generic `set_memory_encrypted/decrypted()` through platform hooks and affects kexec, AP bring-up, DMI/MP parsing, and device DMA.

## Risks
Encryption attribute transitions require cache flushes, TLB flushes, RMP state ordering, and sometimes hypervisor notifications. Wrong ordering can corrupt memory, trigger SNP validation faults, or expose private data as shared. Early boot code runs before normal allocators and must use limited fixmap slots. SEV-ES and SNP workarounds are security-sensitive and platform-specific.

## Test Signals
Relevant tests include SME bare-metal boot, SEV/SEV-ES/SEV-SNP guest boot, encrypted/decrypted `set_memory_*()` transitions, kexec, AP bring-up, IA32 syscall attempts in SEV guests, ROM/DMI probing under SNP, and freeing unused decrypted ranges without warnings.
