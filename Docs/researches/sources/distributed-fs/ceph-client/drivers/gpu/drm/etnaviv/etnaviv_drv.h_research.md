# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_drv.h

## Purpose
Declares shared top-level etnaviv driver data structures, exported cross-file function prototypes, debug macros, and utility helpers.

## Important APIs, Types, and Functions
Defines `ETNAVIV_SOFTPIN_START_ADDRESS`, `struct etnaviv_file_private`, and `struct etnaviv_drm_private`. Declares GEM, PRIME, buffer, submit, validation, and debugfs functions. Inline helpers include `size_vstruct()` for overflow-safe variable-struct sizing and `etnaviv_timeout_to_jiffies()` for monotonic UAPI timeout conversion.

## Control Flow
No primary runtime flow; inline helpers are used by submit and wait paths. Timeout conversion returns zero for expired absolute monotonic deadlines.

## State and Persistence
Documents per-file context state, global driver-private state, active contexts xarray, GEM list, command buffer suballocator, global MMU, GPU array, and flop reset payload pointer.

## Dependencies and Integration Points
Included across the etnaviv driver. Depends on DRM GEM/UAPI headers, DRM scheduler, xarray, Linux time APIs, and etnaviv MMU/GPU forward declarations.

## Risks
The flexible submit sizing helper must be used consistently to avoid allocation overflow. Timeout semantics are absolute monotonic, so userspace and kernel must agree on clock domain.

## Test Signals
Build coverage, ioctl timeout tests, large submit allocation validation, and context lifecycle tests exercise this header’s contracts.
