<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h

Purpose: Collects PowerPC setup-time declarations for relocation, memory limits, panic timeout, and platform init hooks.

Important APIs/types/functions: progress printing, `memory_limit`, relocation helpers, `initmem_init()`, pSeries relocation-on-exception helpers, KASLR init, and `ARCH_PANIC_TIMEOUT`. Source-visible declarations include: #define _ASM_POWERPC_SETUP_H; extern void ppc_printk_progress(char *s, unsigned short hex);; extern unsigned long long memory_limit;; struct device_node;; extern unsigned long reloc_offset(void);; extern unsigned long add_reloc_offset(unsigned long);; extern void reloc_got2(unsigned long);; #define PTRRELOC(x) ((typeof(x)) add_reloc_offset((unsigned long)(x))).

Control flow: early boot uses relocation helpers before final mappings and later platform setup queries feature hooks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: boot globals such as memory limit and relocation offset persist into setup. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/setup.h>. Integrated with early boot, pSeries, KASLR, memblock, console progress, and platform firmware discovery.

Risks: relocation helpers are valid only during boot phases where GOT/data relocation assumptions hold. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 99 lines, 2935 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setup.h -->
