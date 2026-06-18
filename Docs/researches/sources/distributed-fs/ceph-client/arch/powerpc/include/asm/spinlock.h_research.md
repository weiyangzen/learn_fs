<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h

Purpose: Selects the configured PowerPC spinlock implementation and supplies the post-lock memory barrier.

Important APIs/types/functions: queued spin/rwlock includes when enabled, simple spinlock fallback, `smp_mb__after_spinlock()`, and `pv_spinlocks_init()`. Source-visible declarations include: #define __ASM_SPINLOCK_H; #define smp_mb__after_spinlock() smp_mb(); static inline void pv_spinlocks_init(void) { }.

Control flow: generic locking includes this header to bind arch lock operations. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state lives in selected lock types. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/qspinlock.h>, #include <asm/qrwlock.h>, #include <asm/simple_spinlock.h>. Integrated with locking core, qspinlock, qrwlock, paravirt, and simple spinlock code.

Risks: backend selection must keep type and operation headers consistent across configs. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 21 lines, 474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spinlock.h -->
