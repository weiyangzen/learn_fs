# sources/distributed-fs/ceph-client/arch/arm/include/asm/sync_bitops.h

## Purpose
Includes synchronized atomic bit operation definitions for ARM.

## Important APIs, Types, And Functions
Key declarations include int _sync_test_and_set_bit(int nr, volatile unsigned long * p);; int _sync_test_and_clear_bit(int nr, volatile unsigned long * p);; int _sync_test_and_change_bit(int nr, volatile unsigned long * p);. Important macros/constants include __ASM_SYNC_BITOPS_H__, sync_set_bit(nr,, sync_clear_bit(nr,, sync_change_bit(nr,, sync_test_bit(nr,, sync_test_and_set_bit(nr,, sync_test_and_clear_bit(nr,, sync_test_and_change_bit(nr,, arch_sync_cmpxchg(ptr,. It depends directly on #include <asm/bitops.h>.

## Control Flow
Callers needing ordered bit operations use these wrappers rather than relaxed non-atomic bit helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/bitops.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
