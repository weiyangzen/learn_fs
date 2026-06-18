<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h

Purpose: Defines low-level PowerPC thread-info layout, flags, stack sizing, and syscall-work masks.

Important APIs/types/functions: `THREAD_SIZE`, `THREAD_ALIGN`, `struct thread_info`, `INIT_THREAD_INFO`, TIF bits, local flags, and work-mask macros. Source-visible declarations include: #define _ASM_POWERPC_THREAD_INFO_H; #define MIN_THREAD_SHIFT (CONFIG_THREAD_SHIFT + 1); #define MIN_THREAD_SHIFT CONFIG_THREAD_SHIFT; #define THREAD_SHIFT PAGE_SHIFT; #define THREAD_SHIFT MIN_THREAD_SHIFT; #define THREAD_SIZE (1 << THREAD_SHIFT); #define THREAD_ALIGN_SHIFT (THREAD_SHIFT + 1); #define THREAD_ALIGN_SHIFT THREAD_SHIFT.

Control flow: entry assembly and scheduler test flags to decide syscall tracing, signal delivery, reschedule, restore, and mitigation work. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: thread_info persists at the task stack/thread base and is read by assembly. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/asm-const.h>, #include <asm/page.h>, #include <linux/cache.h>, #include <asm/processor.h>, #include <asm/accounting.h>, #include <asm/ppc_asm.h>. Integrated with entry/exit assembly, scheduler, signal, seccomp, livepatch, KVM, and stack allocation.

Risks: flag numbers and struct offsets are assembly ABI; changing them requires offset regeneration and entry-path tests. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 238 lines, 7798 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/thread_info.h -->
