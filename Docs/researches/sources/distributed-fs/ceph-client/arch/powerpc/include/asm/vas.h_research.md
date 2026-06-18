<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h

Purpose: Declares the Virtual Accelerator Switchboard window and coprocessor request interface.

Important APIs/types/functions: VAS FIFO/threshold constants, window status flags, `struct vas_window`, `struct vas_tx_win_attr`, `struct coprocessor_request_block`, field helper macros, open/close/paste/IRQ APIs. Source-visible declarations include: #define _ASM_POWERPC_VAS_H; #define VAS_RX_FIFO_SIZE_MIN (1 << 10) /* 1KB */; #define VAS_RX_FIFO_SIZE_MAX (8 << 20) /* 8MB */; #define VAS_THRESH_DISABLED 0; #define VAS_THRESH_FIFO_GT_HALF_FULL 1; #define VAS_THRESH_FIFO_GT_QTR_FULL 2; #define VAS_THRESH_FIFO_GT_EIGHTH_FULL 3; #define VAS_WIN_ACTIVE 0x0 /* Used in platform independent */.

Control flow: drivers open RX/TX windows, configure FIFO/credit/interrupt attributes, paste CRBs to submit work, and close or migrate windows. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: window objects, FIFO mappings, credits, IRQs, and attached mm/context state persist while devices use VAS. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sched/mm.h>, #include <linux/mmu_context.h>, #include <asm/icswx.h>, #include <uapi/asm/vas-api.h>. Integrated with NX/GZIP/crypto acceleration, user VAS API, hypervisor hcalls, IRQs, and mm context handling.

Risks: credit accounting, window migration, and user-mapped paste addresses are concurrency and security sensitive. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 294 lines, 8100 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vas.h -->
