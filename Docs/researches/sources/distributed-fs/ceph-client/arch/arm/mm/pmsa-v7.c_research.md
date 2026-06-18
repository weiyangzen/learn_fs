# sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v7.c

## Purpose
This file programs ARM PMSAv7 MPU regions for no-MMU systems. It translates memblock RAM and optional XIP ROM into power-of-two MPU regions with subregion masks, truncating usable RAM when hardware region limits cannot cover the requested memory.

## Important APIs, Types, and Functions
`struct region` records base, size, and disabled subregions. `try_split_region()` finds the smallest aligned power-of-two MPU region that can cover a range and uses subregions when possible. `allocate_region()` decomposes a range into up to `MPU_MAX_REGIONS` regions. `pmsav7_adjust_lowmem_bounds()` probes min region order and max region count, reserves slots for background/vectors/XIP, converts the first contiguous memblock RAM range into MPU regions, and removes unsupported tail memory. `pmsav7_setup()` programs background, XIP, RAM, and vector regions.

Low-level helpers write CP15 MPU registers or Cortex-M SCB memory-mapped registers: region number, base, size, access-control, and optional instruction-side equivalents. `mpu_setup_region()` performs barriers, optional cache flush, register writes, and records values in `mpu_rgn_info`.

## Control Flow
Early memory-bound adjustment probes hardware limits, rejects non-contiguous first RAM, ignores later RAM banks, and computes a region plan. Later `pmsav7_setup()` programs regions in priority order: background strongly ordered no-execute, optional XIP ROM, RAM normal RW, and exception vectors. Any setup error panics.

## State and Persistence Behavior
The file uses `__initdata` arrays for planning and stores the final runtime MPU register image in global `mpu_rgn_info`, used by secondary/resume paths. It mutates memblock by removing unsupported memory. Hardware MPU state persists until reset or later MPU reprogramming.

## Dependencies and Integration Points
It is called from `nommu.c` based on `MMFR0.PMSA`. It depends on CP15/MPUIR, V7-M SCB definitions, memblock, cache flushing, `vectors_base`, XIP section symbols, and MPU constants from `asm/mpu.h`.

## Risks
MPU region sizing is constrained and easy to get wrong: base/size alignment, minimum region order, subregion granularity, and fixed slot reservations all affect usable memory. Removing later memblock ranges while iterating must remain broad and intentional. Incorrect region attributes can make RAM uncached, make vectors user-accessible, or permit execution from device/background regions.

## Test Signals
Boot PMSAv7 no-MMU boards with varied RAM sizes, non-power-of-two memory, XIP kernels, V7-M and non-V7-M targets, and separate I/D MPU maps. Confirm log messages for truncation and region independence, inspect `mpu_rgn_info`, and run memory, exception, DMA/cache, and executable-code tests.
