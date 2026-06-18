# sources/distributed-fs/ceph-client/arch/arm/include/asm/mcs_spinlock.h

## Purpose
Supplies ARM SMP hooks for generic MCS queued spinlocks using WFE/SEV-friendly acquire and release primitives.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_MCS_LOCK_H, arch_mcs_spin_lock_contended(lock), arch_mcs_spin_unlock_contended(lock). It depends directly on #include <asm/spinlock.h>.

## Control Flow
Waiters publish prior stores, sleep in WFE until the node lock byte becomes true with acquire ordering, and unlockers store-release then call dsb_sev to wake sleepers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/spinlock.h>.

## Risks And Edge Cases
Ordering and wakeup details are concurrency-critical; missing barriers or broken WFE/SEV alternatives can deadlock SMP systems or expose protected data before lock acquisition is complete.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
