# sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h

### Purpose
`memory.h` defines ARM64 virtual/physical memory layout constants, translation helpers, KASLR/KASAN layout values, linear-map bounds, phys/virt conversion macros, and memory tagging/top-byte rules.

### Important APIs, Types, And Functions
Key items include `VA_BITS`, `PAGE_OFFSET`, `MODULES_VADDR`, `VMALLOC_START/END`, `VMEMMAP_START`, `KIMAGE_VADDR`, `PHYS_OFFSET`, `PHYS_MASK`, `__pa()`, `__va()`, `virt_to_phys()`, `phys_to_virt()`, `virt_addr_valid()`, `__is_lm_address()`, `lm_alias()`, `untagged_addr()`, memory limit declarations, and KASAN/MTE/TBI-aware address helpers.

### Control Flow
Most behavior is macro/inline expansion. Boot code establishes layout variables such as `memstart_addr`; later MM, DMA, and page-table code use the conversion helpers continuously.

### State, Persistence, And Dependencies
State includes boot-initialized physical offset/memory-limit globals and address-space constants. It depends on page definitions, compiler attributes, KASAN/MTE options, sparsemem, and kernel VA size configuration.

### Integration Points
This is foundational for all ARM64 kernel memory access, including page cache, network buffers, block I/O, DMA, KVM, and Ceph client data paths.

### Risks
Address conversion bugs cause memory corruption. Tagged-address handling must match MTE/TBI and userspace ABI. Layout constants must not overlap modules, vmalloc, vmemmap, fixmap, or kernel image regions.

### Test Signals
Boot page-size/VA-size/KASAN/MTE combinations; run memory hotplug, sparsemem, DMA, KASAN, and high-memory stress; validate `/proc/vmallocinfo` and page-owner diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/memory.h -->
