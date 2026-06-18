# sources/distributed-fs/ceph-client/arch/x86/mm/pgprot.c

## Purpose
`pgprot.c` maps Linux VMA permission flags to x86 page-protection encodings and applies memory-encryption and protection-key bits where needed.

## Important APIs, Types, and Functions
The file owns the `protection_map[16]` table, marked `__ro_after_init`, indexed by `VM_READ`, `VM_WRITE`, `VM_EXEC`, and `VM_SHARED`. Public functions are `add_encrypt_protection_map()` and exported `vm_get_page_prot()`.

## Control Flow and State
`add_encrypt_protection_map()` mutates every table entry with `pgprot_encrypted()` during encryption setup. `vm_get_page_prot()` selects the table entry for a VMA flag combination, folds in Intel memory-protection-key bits from `VM_PKEY_BIT0..3` when configured, applies `__sme_set()`, masks present entries with `__supported_pte_mask`, and returns the final `pgprot_t`.

## State and Persistence
The protection map persists after init and becomes read-only. Returned protections are not stored here; they are consumed by generic MM when creating PTEs for VMAs. Encryption setup permanently changes the baseline table for the running kernel.

## Dependencies and Integration Points
It depends on x86 page-protection constants, SME memory encryption helpers, optional Intel pkeys, and generic MM `vm_get_page_prot()` callers such as mmap, mprotect, and fault handling.

## Risks and Test Signals
Risks include unsupported bits escaping into present PTEs, wrong copy-vs-shared mappings for writeable private VMAs, and pkey bit mismatches between `vm_flags` and PTE encoding. Test signals are mmap/mprotect permission tests, pkey tests, SME encrypted memory boot/runtime tests, and W^X checks for executable mappings.
