# sources/distributed-fs/ceph-client/arch/arm/include/asm/spectre.h

## Purpose
Declares ARM Spectre mitigation selection, branch predictor hardening, and firmware workaround interfaces.

## Important APIs, Types, And Functions
Key declarations include enum {; enum {; enum {; void spectre_v2_update_state(unsigned int state, unsigned int methods);; static inline void spectre_v2_update_state(unsigned int state,; unsigned int methods). Important macros/constants include __ASM_SPECTRE_H.

## Control Flow
CPU bring-up and alternative patching choose mitigation callbacks; exception/user-copy paths use the resulting barriers or branch predictor sequences.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
