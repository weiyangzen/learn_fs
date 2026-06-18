## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/head_64.S

### Purpose
`compressed/head_64.S` implements both 32-bit and 64-bit entry paths for a 64-bit compressed kernel. It verifies long mode, builds early page tables, handles SEV setup, transitions to long mode when needed, relocates the decompressor, configures IDT and identity maps, calls `extract_kernel()`, and jumps to the decompressed kernel.

### Important APIs, Types, And Functions
Major symbols are `startup_32`, `startup_64`, `.Lrelocated`, `.Lno_longmode`, `verify_cpu`, `gdt64`, `gdt`, `boot_idt_desc`, `boot_idt`, `boot_stack`, `pgtable`, and `top_pgtable`. It calls `startup32_load_idt`, `get_sev_encryption_bit`, `startup32_check_sev_cbit`, `load_stage1_idt`, `sev_enable`, `configure_5level_paging`, `load_stage2_idt`, `initialize_identity_maps`, and `extract_kernel`.

### Control Flow
The 32-bit entry computes the runtime base, loads a GDT, sets segments and stack, installs SEV-ES IDT if configured, verifies long-mode CPU support, selects a decompression target, builds initial 4 GiB page tables with optional SEV C-bit mask, enables PAE and long mode, verifies C-bit correctness, and far-returns into `startup_64`. The 64-bit entry handles direct 64-bit bootloader entry, sets segments and stack, installs a GDT with a 32-bit code segment, preserves `boot_params` in `%r15`, loads stage-1 IDT, enables SEV handling, normalizes CR4, configures 5-level paging via trampoline if needed, relocates the compressed image backward, reloads GDT, jumps to relocated code, clears BSS, loads stage-2 IDT, initializes identity maps, calls `extract_kernel`, and jumps to the returned entry with `%rsi` restored to boot params.

### State, Persistence, And Dependencies
State spans page tables, GDT/IDT, boot stack, relocated image, SEV status globals, CR0/CR3/CR4/EFER, and preserved boot params. Dependencies include x86 boot ABI entry offsets, page table constants, SEV/TDX support objects, 5-level paging helpers, and compressed C runtime.

### Integration Points
This is the first compressed-kernel code for x86_64 regardless of 32-bit or 64-bit bootloader entry. It coordinates with `ident_map_64.c`, `idt_64.c`, `mem_encrypt.S`, SEV code, and `misc.c`.

### Risks
Mode transition ordering is extremely fragile: CPUID in encrypted guests needs handlers, CR4.LA57 cannot be changed directly in long mode, page-table encryption bits must be correct before memory access, and relocation must not overwrite live code. ABI entry offsets `0` and `0x200` are immutable.

### Test Signals
Boot via 32-bit and 64-bit entry, relocatable and fixed kernels, 4-level and 5-level paging, SEV/SEV-ES/SEV-SNP guests, KASLR on/off, and load addresses above 4 GiB.
