# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/map_range.c

Purpose: Provides the early PI page-table range mapper used for idmaps, kernel maps, FDT maps, and temporary LPA2 remaps before the normal mm subsystem is available.

Important APIs: `map_range()` recursively creates block/page mappings at the requested translation level, allocating lower-level tables from a caller-provided physical pointer. `create_init_idmap()` builds the initial idmap over text and data ranges and returns the end of used page-table memory.

Control flow: `map_range()` aligns start and physical address, advances to the relevant table entry, chooses block/page descriptor bits unless clearing mappings, recurses when alignment or level requires finer mappings, optionally uses contiguous PTE attributes, and writes descriptors directly. `create_init_idmap()` maps `_stext` to `__initdata_begin` RX and `__initdata_begin` to `_end` RW, applying a caller-supplied clear mask.

Dependencies and integration: called by `head.S` through PI aliases and by `pi/map_kernel.c`. It depends on arm64 page table descriptor definitions, early linker symbols, strict alignment flags, and MMU-off physical pointer assumptions.

Risks and test signals: risks are table allocation overrun, wrong contiguous-bit boundaries, clearing live mappings without TLB handling by caller, and descriptor bits invalid under LPA2 unless masked. Test early boot with all page sizes and levels, LPA2, KASLR relocation, FDT mapping, and page table debug instrumentation.
