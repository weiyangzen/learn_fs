<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h

Purpose: Implements the legacy PowerPC simple spinlock and rwlock primitives.

Important APIs/types/functions: lock token selection, `arch_spin_*`, `arch_read_*`, `arch_write_*`, paravirt yield hooks, ticketless wait loops, and memory-barrier usage. Source-visible declarations include: #define _ASM_POWERPC_SIMPLE_SPINLOCK_H; #define LOCK_TOKEN (*(u32 *)(&get_paca()->lock_token)); #define LOCK_TOKEN (*(u32 *)(&get_paca()->paca_index)); #define LOCK_TOKEN 1; static inline int arch_spin_is_locked(arch_spinlock_t *lock); static inline unsigned long __arch_spin_trylock(arch_spinlock_t *lock); static inline int arch_spin_trylock(arch_spinlock_t *lock); static inline void splpar_spin_yield(arch_spinlock_t *lock) {}.

Control flow: trylock uses atomic load/store reservation, lock paths spin with optional SPLPAR yield, and unlock stores zero with release ordering. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: lock word state is caller-owned and may encode CPU/PACA tokens. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/irqflags.h>, #include <linux/kcsan-checks.h>, #include <asm/paravirt.h>, #include <asm/paca.h>, #include <asm/synch.h>, #include <asm/ppc-opcode.h>. Integrated with locking core, paravirt/splpar yield, paca, low-level synchronization, and irq-safe sections.

Risks: barrier placement and token ownership are concurrency-critical; regressions deadlock under SMP or virtualized contention. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 268 lines, 6242 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/simple_spinlock.h -->
