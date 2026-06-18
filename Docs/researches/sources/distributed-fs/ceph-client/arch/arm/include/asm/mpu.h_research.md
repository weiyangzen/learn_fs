# sources/distributed-fs/ceph-client/arch/arm/include/asm/mpu.h

## Purpose
Defines PMSA/MPU register bit layouts, memory attributes, region descriptors, and setup hooks for ARM NoMMU/MPU systems.

## Important APIs, Types, And Functions
Key declarations include struct mpu_rgn {; struct mpu_rgn_info {; unsigned int used;; struct mpu_rgn rgns[MPU_MAX_REGIONS];; extern struct mpu_rgn_info mpu_rgn_info;; extern void __init pmsav7_adjust_lowmem_bounds(void);. Important macros/constants include __ARM_MPU_H, MPUIR_nU, MPUIR_DREGION, MPUIR_IREGION, MPUIR_DREGION_SZMASK, MPUIR_IREGION_SZMASK, MMFR0_PMSA, MMFR0_PMSAv7, MMFR0_PMSAv8, PMSAv7_RSR_SZ.

## Control Flow
Early architecture setup detects PMSAv7 or PMSAv8, adjusts lowmem bounds, fills mpu_rgn_info, and programs region base/limit/access attributes.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
