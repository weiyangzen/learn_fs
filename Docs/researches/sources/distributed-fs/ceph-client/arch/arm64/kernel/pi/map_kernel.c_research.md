# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_kernel.c

Purpose: Builds the early kernel virtual mapping, handles relocation/KASLR, feature override parsing, LPA2/idmap remapping, optional dynamic SCS patching, BTI/PAC text permissions, and final swapper page table installation.

Important APIs and state: `early_map_kernel()` is called from `head.S`. Helpers include `map_kernel()`, `map_segment()`, `unmap_segment()`, `remap_idmap_for_lpa2()`, `map_fdt()`, and `ng_mappings_allowed()`. It uses linker symbols for text/rodata/init/data ranges and PI globals such as `arm64_use_ng_mappings`.

Control flow: the FDT is mapped, BSS and initial page tables are cleared, feature overrides are parsed, VA bits/root level are adjusted for LVA/LPA2 hardware, KASLR seed is folded with physical low bits, LPA2 idmap descriptors are remapped if needed, then segments are mapped. A two-pass mapping is used for relocation or dynamic SCS: text is first writable, relocation/SCS patching runs, text is unmapped, TLBs are invalidated, and text is remapped with final executable permissions before copying the root table to `swapper_pg_dir`.

Dependencies and integration: depends on PI `map_range()`, relocation and SCS PI helpers, libfdt, cpufeature probes, TCR/TTBR manipulation, linker aliases, KASLR early seed, Cavium erratum handling for non-global mappings, and `head.S` handoff.

Risks and test signals: risks are wrong permissions during two-pass mapping, TLB conflicts when remapping text, FDT overlap with kernel image, LPA2 descriptor bit reinterpretation, dynamic SCS with PAC/BTI, and KASLR/KPTI non-global mapping errata. Test relocatable and non-relocatable boots, BTI/PAC/SCS combinations, `rodata=off`, LPA2/LVA hardware, KASLR seed, KPTI, and early page table dumps.
