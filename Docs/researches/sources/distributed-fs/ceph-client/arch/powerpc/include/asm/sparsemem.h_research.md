<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h

Purpose: Sets PowerPC sparsemem section sizing and hotplug NUMA helpers.

Important APIs/types/functions: `SECTION_SIZE_BITS`, optional `MAX_PHYSMEM_BITS`, `remove_section_mapping()`, `memory_add_physaddr_to_nid()`, and `hot_add_scn_to_nid()`. Source-visible declarations include: #define _ASM_POWERPC_SPARSEMEM_H 1; #define SECTION_SIZE_BITS 24; extern int remove_section_mapping(unsigned long start, unsigned long end);; extern int memory_add_physaddr_to_nid(u64 start);; #define memory_add_physaddr_to_nid memory_add_physaddr_to_nid; extern int hot_add_scn_to_nid(unsigned long scn_addr);; static inline int hot_add_scn_to_nid(unsigned long scn_addr).

Control flow: memory hotplug code maps physical sections to nodes and tears down section mappings. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: memory section/node mappings persist in sparsemem metadata. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with memory hotplug, NUMA, memblock, and sparsemem core.

Risks: section-size constants shape the memmap ABI and hotplug helpers must match firmware topology. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sparsemem.h -->
