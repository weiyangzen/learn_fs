# sources/distributed-fs/ceph-client/arch/sh/mm/pmb.c

Purpose: implements SH Privileged Space Mapping Buffer management for large kernel/IO mappings, bootloader mapping synchronization, debugfs visibility, and resume restoration.

Important APIs and state: `struct pmb_entry`, `pmb_entry_list`, `pmb_map`, `pmb_bolt_mapping`, `pmb_remap_caller`, `pmb_unmap`, `pmb_init`, `__in_29bit_mode`, `pmb_debugfs_show`, early param `pmb=iomap`, and PM resume hooks.

Control flow: boot synchronizes software entries with valid hardware PMB entries, updates cache flags, links contiguous mappings, coalesces to larger page sizes, optionally resizes uncached mappings, logs entries, clears interrupt-mask control, and flushes TLBs. Runtime remap aligns large physical ranges, reserves vmalloc space, installs PMB entries, and unmaps linked entries as a group.

State and persistence: owns global PMB entry array/bitmap, hardware PMB address/data registers, mapping links, optional debugfs file, and resume restoration state.

Dependencies and integration: `ioremap.c` uses PMB for large mappings; `init.c` calls `pmb_init`; cache/TLB/uncached mapping code must stay coherent with PMB flags.

Risks: PMB operations must be performed uncached when required. Entry allocation/linking under locks is delicate, and partial mapping failures must unmap already-installed entries. Existing bootloader mappings outside valid RAM are invalidated.

Test signals: boot PMB logs/debugfs, `pmb=iomap` large ioremap tests, suspend/resume on PMB hardware, and cacheability validation for PMB mappings.
