# sources/distributed-fs/ceph-client/arch/x86/boot/startup/map_kernel.c

Purpose: performs early x86-64 kernel page-table fixups, identity mapping, LA57 propagation, and SME post-processing while running from early identity mappings.

Important APIs and state: exports `__startup_64(unsigned long p2v_offset, struct boot_params *bp)`. Helpers include `check_la57_support()` and `sme_postprocess_startup()`. It manipulates global early page tables, `phys_base`, `next_early_pgt`, `__pgtable_l5_enabled`, `pgdir_shift`, and `ptrs_per_p4d`.

Control flow: detects active LA57 via CR4, validates physical address and 2 MiB alignment, computes load delta and virtual text range, fixes top-level/kernel/fixmap page-table entries, builds identity mappings around the current physical location using early dynamic page tables, fixes or invalidates `level2_kernel_pgt` entries around the actual image, calls `sme_encrypt_kernel()`, changes `.bss..decrypted` mappings to decrypted/shared as needed, and returns the encryption mask for CR3 setup.

Dependencies and integration: called by `head_64.S` before virtual-address execution. Depends on RIP-relative addressing, early page-table globals, SME/SNP helpers, and linker symbols `_text`, `_end`, `__start_bss_decrypted`, and `__end_bss_decrypted`.

Risks and test signals: invalid mappings can allow speculative access to reserved memory or crash before diagnostics. Test relocatable kernels, 4-level/5-level paging, SME active/non-active, SNP page-state transitions for decrypted BSS, and kernels loaded at non-preferred but 2 MiB-aligned addresses.
