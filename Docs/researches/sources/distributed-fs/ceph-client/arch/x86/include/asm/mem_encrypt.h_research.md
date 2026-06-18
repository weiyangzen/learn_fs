# sources/distributed-fs/ceph-client/arch/x86/include/asm/mem_encrypt.h

## Purpose
Declares AMD SME/SEV memory encryption setup interfaces, early encrypt/decrypt helpers, decrypted BSS section annotations, and physical-address masking helpers.

## Important APIs, Types, And Functions
Exports `mem_encrypt_init()`, `mem_encrypt_setup_arch()`, `sme_encrypt_execute()`, `sme_early_encrypt()`, `sme_early_decrypt()`, `sme_map_bootdata()`, `sme_unmap_bootdata()`, `sme_early_init()`, `sme_encrypt_kernel()`, `sme_enable()`, `early_set_memory_decrypted()`, `early_set_memory_encrypted()`, `early_set_mem_enc_dec_hypercall()`, `mem_encrypt_free_decrypted_mem()`, `sev_es_init_vc_handling()`, `sme_get_me_mask()`, `add_encrypt_protection_map()`, `__sme_pa()`, and `__sme_pa_nodebug()`. State symbols are `sme_me_mask` and `sev_status`.

## Control Flow
Early boot discovers encryption support, sets the SME mask, encrypts or decrypts kernel regions, maps boot data with correct attributes, and initializes SEV-ES VC handling. Non-enabled configs compile to stubs and zero masks.

## State And Persistence
State is boot-time and global: encryption mask, SEV status, decrypted BSS ranges, and page attribute changes. It persists for the lifetime of the booted kernel but not across reboot.

## Dependencies And Integration Points
Depends on confidential-computing platform helpers, boot parameters, page-table physical address conversion, and AMD memory-encryption code. It integrates with early boot, kernel relocation/encryption, SEV-ES exception handling, and hypercall-assisted attribute changes.

## Risks And Edge Cases
Incorrect mask use in CR3 or page-table addresses can corrupt address translation. Early decrypted/encrypted transitions run before normal allocators and are hard to recover from. Stubs must preserve callers across non-AMD or disabled builds.

## Test Signals
Boot tests on SME, SEV, SEV-ES, and non-encrypted systems; kexec/suspend smoke tests; and early page attribute validation are key signals.
