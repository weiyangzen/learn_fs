# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.h

## Purpose
Declares TI CSC register offsets, bit masks/shifts, bypass bit, state structure, and exported helper prototypes.

## Important APIs, Types, and Functions
Defines registers `CSC_CSC00` through `CSC_CSC05`, coefficient field masks/shifts for A/B/C/D terms, `CSC_BYPASS`, and `struct csc_data`. Public prototypes mirror `csc.c`: dump, bypass, coefficient setup, and create.

## Control Flow
No executable control flow. The register layout controls how callers allocate/register shadow payload space and how `csc_set_coeff()` packs coefficients.

## State and Persistence
`struct csc_data` holds the MMIO mapping, resource, and platform device pointer. Hardware register state is external and volatile.

## Dependencies and Integration Points
Consumed by `csc.c` and VPE/VIP users that need CSC register programming. Requires V4L2 format types for the `csc_set_coeff()` prototype through includer context.

## Risks and Edge Cases
Mask/shift mistakes would corrupt color conversion. `CSC_BYPASS` shares register 5 with D coefficients, so callers must preserve register payload ordering.

## Test Signals
Build all users, inspect generated register payloads for known CSC matrices, confirm bypass bit placement, and verify MMIO dump offsets match hardware documentation.
