# sources/distributed-fs/ceph-client/arch/arm/include/asm/v7m.h

## Purpose
Defines ARMv7-M system-control, exception, cache, MPU register offsets, exception-return bits, and restart hook declarations.

## Important APIs, Types, And Functions
Key declarations include enum reboot_mode;; void armv7m_restart(enum reboot_mode mode, const char *cmd);. Important macros/constants include V7M_SCS_ICTR, V7M_SCS_ICTR_INTLINESNUM_MASK, BASEADDR_V7M_SCB, V7M_SCB_CPUID, V7M_SCB_ICSR, V7M_SCB_ICSR_PENDSVSET, V7M_SCB_ICSR_PENDSVCLR, V7M_SCB_ICSR_RETTOBASE, V7M_SCB_ICSR_VECTACTIVE, V7M_SCB_VTOR.

## Control Flow
v7-M boot and exception code programs SCB/MPU/cache registers and uses armv7m_restart for system reset.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
