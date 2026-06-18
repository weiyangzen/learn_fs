<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S

Purpose: Linker script for the s390 boot/decompressor image. It fixes boot section layout, embeds compressed vmlinux and metadata, defines decompressor symbols, stores relocation tables, and asserts that forbidden dynamic relocation/linkage sections remain absent.

Important APIs/types/functions: Defines output format/architecture, entry `startup`, sections `.ipldata`, `.head.text`, `.parmarea`, `.text`, `.rodata`, exception table, `.got`, notes, `.data`, `BOOT_DATA`, `BOOT_DATA_PRESERVED`, decompressor `.bss` and stacks, `.vmlinux.info`, `.decompressor.syms`, `_decompressor_end`, `.vmlinux.relocs`, `.rodata.compressed`, `.sb.trailer`, and discard/assertion sections.

Control flow: Link-time only. The script positions the IPL header/startup areas, collects boot code/data, records metadata consumed by `startup.c` and `printk.c`, aligns compressed or uncompressed payload placement, adds a secure-boot trailer, and rejects unexpected PLT or dynamic relocation content.

State and persistence: Produces linker symbols such as `_stack_start/_end`, `_dump_info_stack_start/_end`, `_vmlinux_info`, `_decompressor_syms_start/_end`, `_decompressor_end`, `__vmlinux_relocs_64_start/_end`, `_compressed_start/_end`, and `_end`.

Dependencies and integration points: Consumed by `startup.c`, `printk.c`, `pgm_check.c`, decompressor entry assembly, vmlinux info generation, secure boot tooling, and relocation adjustment logic.

Risks: Section order and alignment are ABI-like. The `.vmlinux.info` layout must match `struct vmlinux_info`; relocation sections must be available until after KASLR relocation; `.sb.trailer` must not overwrite compressed data. Assertions guard against runtime relocations that the decompressor cannot process.

Test signals: Linker map inspection, booting compressed and uncompressed kernels, secure boot trailer validation, relocation table bounds checks, and build failures when unexpected `.plt` or `.rela.dyn` content appears.

Source read size: 173 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmlinux.lds.S -->
