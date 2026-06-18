# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-coremask.h

## Purpose
This header defines a bitmap type and minimal helpers for representing Octeon core sets, including sparse multi-node core numbering where node IDs create large gaps.

## Important APIs, Types, and Functions
`CVMX_MIPS_MAX_CORES` is 1024, `CVMX_COREMASK_ELTSZ` is 64, and `CVMX_COREMASK_BMPSZ` sizes the bitmap. `struct cvmx_coremask` contains `u64 coremask_bitmap[16]`. Inline helpers test a core bit (`cvmx_coremask_is_core_set`), copy masks (`cvmx_coremask_copy`), set the low 64 bits (`cvmx_coremask_set64`), and clear one core (`cvmx_coremask_clear_core`).

## Control Flow
Helpers compute word and bit indices from a core number and manipulate the bitmap. There is no iteration helper here; callers handle traversal or use the routines in boot and SMP setup.

## State and Persistence Behavior
The structure is plain in-memory state. It appears inside bootinfo as `ext_core_mask`, making its layout part of the bootloader ABI. Helper operations mutate only the supplied mask.

## Dependencies and Integration Points
It depends on kernel integer types, `bool`, and `memcpy` from included context. It integrates with `cvmx_bootinfo`, SMP core selection, multi-node initialization, and any role partitioning for shared Octeon binaries.

## Risks
The inline helpers do not bounds-check `core`; invalid or negative core numbers can index outside the bitmap. `cvmx_coremask_set64()` only initializes the low word, which is insufficient for CN78XX-style node 1+ core IDs. Callers must distinguish hardware CPUNum values from dense Linux CPU indices.

## Test Signals
Test sparse masks with core IDs 0-47, 128-175, and higher-node ranges. Verify bootinfo extended core masks select expected CPUs, invalid core IDs are filtered by callers, and low-64 compatibility paths still work on older systems.
