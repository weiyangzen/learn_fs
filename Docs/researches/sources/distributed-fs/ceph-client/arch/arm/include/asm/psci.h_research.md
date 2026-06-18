# sources/distributed-fs/ceph-client/arch/arm/include/asm/psci.h

## Purpose
Declares ARM PSCI firmware integration used for CPU power, suspend, and system reset/off operations.

## Important APIs, Types, And Functions
Key declarations include extern const struct smp_operations psci_smp_ops;; static inline bool psci_smp_available(void) { return false; }. Important macros/constants include __ASM_ARM_PSCI_H.

## Control Flow
Platform setup detects PSCI conduit and function IDs, then SMP and power-management paths invoke firmware through SMC/HVC wrappers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
