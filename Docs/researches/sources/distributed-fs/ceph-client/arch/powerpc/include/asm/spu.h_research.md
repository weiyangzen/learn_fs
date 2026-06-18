<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h

Purpose: Main kernel interface for Cell Broadband Engine Synergistic Processing Units and spufs.

Important APIs/types/functions: MFC command/event constants, `struct spu`, `struct cbe_spu_info`, SPU callbacks, runqueue/context declarations, syscall/coredump hooks, and SPU MMU helpers. Source-visible declarations include: #define _SPU_H; #define LS_SIZE (256 * 1024); #define LS_ADDR_MASK (LS_SIZE - 1); #define MFC_PUT_CMD 0x20; #define MFC_PUTS_CMD 0x28; #define MFC_PUTR_CMD 0x30; #define MFC_PUTF_CMD 0x22; #define MFC_PUTB_CMD 0x21.

Control flow: platform code discovers SPUs, spufs binds contexts to SPUs, interrupt callbacks handle mailbox/MFC/stop events, and MM code flushes SPU SLBs. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: persistent SPU device objects track local store, MM association, interrupts, callbacks, runqueue state, owner PIDs, and utilization stats. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/workqueue.h>, #include <linux/device.h>, #include <linux/mutex.h>, #include <asm/reg.h>, #include <asm/copro.h>. Integrated with Cell platform setup, spufs, scheduler, coredumps, MMU/SLB handling, IRQ affinity, and coprocessor support.

Risks: hardware register ordering, context-switch flags, and callback lifetimes are hard to test without Cell hardware. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 679 lines, 23975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu.h -->
