# sources/distributed-fs/ceph-client/arch/arm/include/asm/mman.h

## Purpose
Adds ARM-specific mmap policy support on top of UAPI mman definitions, currently exposing whether write-execute denial is supported by the CPU architecture.

## Important APIs, Types, And Functions
Key declarations include static inline bool arch_memory_deny_write_exec_supported(void). Important macros/constants include __ASM_MMAN_H__, arch_memory_deny_write_exec_supported. It depends directly on #include <asm/system_info.h>, #include <uapi/asm/mman.h>.

## Control Flow
The inline helper gates memory-deny-write-exec support on cpu_architecture() >= ARMv6.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/system_info.h>, #include <uapi/asm/mman.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
