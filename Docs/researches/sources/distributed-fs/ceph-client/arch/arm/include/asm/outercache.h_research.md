# sources/distributed-fs/ceph-client/arch/arm/include/asm/outercache.h

## Purpose
Defines the outer-cache operation dispatch table and inline wrappers used by ARM platforms with external L2 caches.

## Important APIs, Types, And Functions
Key declarations include struct l2x0_regs;; struct outer_cache_fns {; void (*inv_range)(unsigned long, unsigned long);; void (*clean_range)(unsigned long, unsigned long);; void (*flush_range)(unsigned long, unsigned long);; void (*flush_all)(void);. Important macros/constants include __ASM_OUTERCACHE_H. It depends directly on #include <linux/types.h>.

## Control Flow
If CONFIG_OUTER_CACHE is enabled, wrappers call registered outer_cache callbacks for range invalidate/clean/flush, all-cache flush, disable, resume, secure writes, and L2x0 configuration; otherwise they compile to no-ops.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
