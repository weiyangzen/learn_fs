# sources/distributed-fs/ceph-client/arch/arm/include/asm/therm.h

## Purpose
Declares ARM thermal or SoC-specific temperature support hook points when present.

## Important APIs, Types, And Functions
Key declarations include struct therm {; int hi;; int lo;. Important macros/constants include __ASM_THERM_H, CMD_SET_THERMOSTATE, CMD_GET_THERMOSTATE, CMD_GET_STATUS, CMD_GET_TEMPERATURE, CMD_SET_THERMOSTATE2, CMD_GET_THERMOSTATE2, CMD_GET_TEMPERATURE2, CMD_GET_FAN, CMD_SET_FAN.

## Control Flow
Platform thermal drivers can include this header for architecture-visible thermal integration.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
