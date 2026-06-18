<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h

Purpose: Declares the early debug console function-pointer interface.

Important APIs/types/functions: `udbg_putc`, `udbg_flush`, `udbg_getc`, `udbg_getc_poll`, early init helpers, and simple put/get wrappers. Source-visible declarations include: #define _ASM_POWERPC_UDBG_H; extern void (*udbg_putc)(char c);; extern void (*udbg_flush)(void);; extern int (*udbg_getc)(void);; extern int (*udbg_getc_poll)(void);; struct device_node;.

Control flow: early platform code installs backend callbacks and printk/debug paths emit characters before full console registration. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global function pointers persist until replaced or unused after console handoff. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/init.h>. Integrated with early boot console, xmon, firmware consoles, serial/RTAS/OPAL debug backends.

Risks: callbacks may run very early or in crash paths, so they must avoid sleeping and invalid mappings. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 56 lines, 1736 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/udbg.h -->
