# sources/distributed-fs/ceph-client/arch/arm/include/asm/tcm.h

## Purpose
Declares tightly coupled memory section markers, allocation helpers, and copy routines for ARM TCM support.

## Important APIs, Types, And Functions
Key declarations include void *tcm_alloc(size_t len);; void tcm_free(void *addr, size_t len);; void __init tcm_init(void);; static inline void tcm_init(void). Important macros/constants include __ASMARM_TCM_H, __tcmdata, __tcmconst, __tcmfunc, __tcmlocalfunc. It depends directly on #include <linux/compiler.h>.

## Control Flow
Boot/linker code maps ITCM/DTCM sections at fixed virtual addresses and platform code can allocate or copy data into TCM.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
