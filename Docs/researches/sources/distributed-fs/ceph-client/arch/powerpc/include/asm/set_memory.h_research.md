<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h

Purpose: Declares PowerPC page-attribute change helpers for kernel text/data mappings.

Important APIs/types/functions: `set_memory_ro/rw/nx/x/np/p/rox()`, `set_memory_attr()`, and attribute operation codes. Source-visible declarations include: #define _ASM_POWERPC_SET_MEMORY_H; #define SET_MEMORY_RO 0; #define SET_MEMORY_RW 1; #define SET_MEMORY_NX 2; #define SET_MEMORY_X 3; #define SET_MEMORY_NP 4 /* Set memory non present */; #define SET_MEMORY_P 5 /* Set memory present */; #define SET_MEMORY_ROX 6.

Control flow: callers request page count and virtual address changes; MMU backend updates PTEs and flushes as needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: changes persist in kernel page tables until reversed. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with module loader, BPF/JIT, rodata hardening, text patching, and memory hotplug.

Risks: incorrect permission transitions can leave executable writable mappings or make live code/data inaccessible. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 51 lines, 1446 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/set_memory.h -->
