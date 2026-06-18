# sources/distributed-fs/ceph-client/arch/arm/include/asm/prom.h

## Purpose
Provides ARM Open Firmware/devicetree boot integration declarations.

## Important APIs, Types, And Functions
Key declarations include extern const struct machine_desc *setup_machine_fdt(void *dt_virt);; extern void __init arm_dt_init_cpu_maps(void);; static inline const struct machine_desc *setup_machine_fdt(void *dt_virt); static inline void arm_dt_init_cpu_maps(void) { }. Important macros/constants include __ASMARM_PROM_H.

## Control Flow
Early boot code calls the declared DT setup helpers to parse machine data and pass it into platform discovery.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
