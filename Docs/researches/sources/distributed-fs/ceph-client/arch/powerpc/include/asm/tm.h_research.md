<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h

Purpose: Declares kernel transactional-memory save, reclaim, and restore hooks.

Important APIs/types/functions: `tm_reclaim()`, `tm_reclaim_current()`, `tm_recheckpoint()`, `tm_save_sprs()`, `tm_restore_sprs()`, and `tm_suspend_disabled`. Source-visible declarations include: extern void tm_reclaim(struct thread_struct *thread,; extern void tm_reclaim_current(uint8_t cause);; extern void tm_recheckpoint(struct thread_struct *thread);; extern void tm_save_sprs(struct thread_struct *thread);; extern void tm_restore_sprs(struct thread_struct *thread);; extern bool tm_suspend_disabled;.

Control flow: context switch, signal, ptrace, and exception code reclaim or recheckpoint transactional state around user/kernel transitions. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: transactional checkpointed registers persist in `thread_struct` and hardware TM SPRs. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/tm.h>. Integrated with POWER transactional memory, signal handling, context switch, ptrace, and suspend/CPU feature code.

Risks: ordering mistakes can expose checkpointed state or corrupt transactions during signals and context switches. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 22 lines, 626 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tm.h -->
