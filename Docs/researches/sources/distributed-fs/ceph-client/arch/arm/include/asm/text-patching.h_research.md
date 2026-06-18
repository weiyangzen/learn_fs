# sources/distributed-fs/ceph-client/arch/arm/include/asm/text-patching.h

## Purpose
Declares ARM kernel text patching helpers for modifying instructions at runtime.

## Important APIs, Types, And Functions
Key declarations include void patch_text(void *addr, unsigned int insn);; void __patch_text_real(void *addr, unsigned int insn, bool remap);; static inline void __patch_text(void *addr, unsigned int insn); static inline void __patch_text_early(void *addr, unsigned int insn). Important macros/constants include _ARM_KERNEL_PATCH_H.

## Control Flow
Alternatives, probes, and mitigation code patch instruction words with cache/TLB synchronization so CPUs execute the new text safely.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
