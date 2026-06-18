# sources/distributed-fs/ceph-client/arch/arm/include/asm/virt.h

## Purpose
Defines ARM virtualization-mode detection, boot CPU mode synchronization, HVC stub call numbers, and hypervisor availability helpers.

## Important APIs, Types, And Functions
Key declarations include extern int __boot_cpu_mode;; static inline void sync_boot_mode(void); void hyp_mode_check(void);; static inline bool is_hyp_mode_available(void); static inline bool is_hyp_mode_mismatched(void); static inline bool is_kernel_in_hyp_mode(void). Important macros/constants include VIRT_H, BOOT_CPU_MODE_MISMATCH, __boot_cpu_mode, sync_boot_mode(), HVC_SET_VECTORS, HVC_SOFT_RESTART, HVC_STUB_ERR. It depends directly on #include <asm/ptrace.h>, #include <asm/cacheflush.h>.

## Control Flow
Boot code records whether CPUs entered in SVC or HYP mode, checks mismatches on secondary CPUs, and HYP stubs use HVC_SET_VECTORS or HVC_SOFT_RESTART.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/ptrace.h>, #include <asm/cacheflush.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
