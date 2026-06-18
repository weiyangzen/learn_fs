## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/ident_map_64.c

### Purpose
`compressed/ident_map_64.c` builds and updates early identity mappings for x86_64 compressed boot, including fault-driven mapping expansion and encryption attribute changes for SEV/SNP.

### Important APIs, Types, And Functions
Exports include `kernel_add_identity_map()`, `initialize_identity_maps()`, `set_page_decrypted()`, `set_page_encrypted()`, `set_page_non_present()`, `do_boot_page_fault()`, and `do_boot_nmi_trap()`. Key state includes `pgt_data`, `top_level_pgt`, `physical_mask`, and `mapping_info`.

### Control Flow
`initialize_identity_maps()` initializes mapping callbacks, selects whether to append to existing boot page tables or allocate a new top-level table, maps the compressed image, boot params, command line, and setup_data chain, performs SEV/SNP preparation, loads CR3, and checks SNP features. `kernel_add_identity_map()` aligns ranges to PMD boundaries and delegates to generic identity mapping code. Page-attribute helpers ensure a mapped PTE exists, split large PMDs if needed, flush caches for encryption changes, update SNP RMP state, modify PTE flags, and reload CR3. `do_boot_page_fault()` validates the fault, rejects unexpected or GHCB faults, and identity maps the faulting 2 MiB range.

### State, Persistence, And Dependencies
State persists in early page tables under `_pgtable`, CR3, page-table allocation offsets, encryption mask handling, and `spurious_nmi_count`. Dependencies include `../../mm/ident_map.c`, low-level page table macros, SEV/SNP helpers, command-line pointer retrieval, setup_data traversal, and boot IDT handlers.

### Integration Points
`head_64.S` calls `initialize_identity_maps()` after loading the stage-2 IDT. SEV code calls page encryption helpers. `idt_handlers_64.S` routes page faults and NMIs into these handlers.

### Risks
Running out of `BOOT_PGT_SIZE` prevents required mappings and halts boot. Large-PMD splitting deliberately avoids a clear-then-flush sequence because the current code/stack may reside in the mapping. Encryption attribute changes must coordinate PTE flags, cache flushing, and SNP RMP transitions in the correct order.

### Test Signals
Boot with command line/setup_data above existing mappings, trigger early page faults, test SEV-SNP page shared/private transitions, exercise 5-level paging, and verify low page-table buffer warnings are absent.
