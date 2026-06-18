# sources/distributed-fs/ceph-client/arch/arm/include/asm/tls.h

## Purpose
Defines ARM TLS register access, user helper page conventions, and thread TLS save/restore hooks.

## Important APIs, Types, And Functions
Key declarations include static inline void set_tls(unsigned long val); struct thread_info *thread;; static inline unsigned long get_tpuser(void); unsigned long reg = 0;; static inline void set_tpuser(unsigned long val); static inline void flush_tls(void). Important macros/constants include __ASMARM_TLS_H, tls_emu, has_tls_reg, defer_tls_reg_update, switch_tls, tls_emu, has_tls_reg, defer_tls_reg_update, switch_tls, tls_emu. Assembly macros include .macro switch_tls_none, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_v6k, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_v6, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_software, base, tp, tpuser, tmp1, tmp2. It depends directly on #include <linux/compiler.h>, #include <asm/thread_info.h>, #include <asm/asm-offsets.h>, #include <asm/smp_plat.h>.

## Control Flow
Context-switch and exec paths update per-task tp_value slots and write CP15/thread pointer state for EABI/OABI userland.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>, #include <asm/thread_info.h>, #include <asm/asm-offsets.h>, #include <asm/smp_plat.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
