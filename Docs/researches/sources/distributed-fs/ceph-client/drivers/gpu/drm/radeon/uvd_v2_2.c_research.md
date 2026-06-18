# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v2_2.c

## Purpose

`uvd_v2_2.c` provides UVD 2.2 generation-specific fence, semaphore, and firmware memory-controller programming. It reuses older UVD support where needed and adds chip-ID reporting for firmware across RV7xx, Evergreen, Northern Islands, and early Southern Islands families.

## Important APIs, Types, and Functions

- `uvd_v2_2_fence_emit()` writes context ID, lower/upper fence address bits, fence sequence, and trap command into the UVD ring.
- `uvd_v2_2_semaphore_emit()` emits wait/signal commands through `UVD_SEMA_ADDR_LOW/HIGH` and `UVD_SEMA_CMD`.
- `uvd_v2_2_resume()` handles firmware/heap/stack/session cache range setup, address extension registers, and `UVD_VCPU_CHIP_ID`.

## Control Flow

Resume delegates RV770 to `uvd_v1_0_resume()` because that ASIC uses V1 memory-controller semantics. For other supported families it calls `radeon_uvd_resume()`, programs the three VCPU cache ranges, writes high address bits, maps `rdev->family` to a firmware chip ID, writes it to `UVD_VCPU_CHIP_ID`, and returns `-EINVAL` for unsupported families.

## State and Persistence Behavior

The function persists VCPU cache offsets/sizes and firmware chip ID in hardware registers. Fence and semaphore functions only append commands to the ring; completion state is observed by generic fence/semaphore infrastructure.

## Dependencies and Integration Points

- Uses `radeon_uvd_resume()` and UVD buffer fields from the Radeon device.
- Depends on `uvd_v1_0_resume()` compatibility, family enums, `PACKET0`, ring writing, and `rv770d.h` UVD register definitions.
- Supplies generation-specific callbacks to Radeon ASIC tables.

## Risks and Edge Cases

- Unsupported family values fail resume with `-EINVAL`; ASIC dispatch must only bind this implementation to listed families.
- Semaphore address encoding shifts by 3 and 23 with 20-bit masks; invalid alignment or address range assumptions could break synchronization.
- Cache size calculation includes firmware size plus 4 bytes, which must match the firmware image format expected by this generation.

## Test Signals

- Resume tests should verify correct chip IDs for each supported family and RV770 fallback to V1 resume.
- Fence tests should verify the emitted command sequence writes both low and upper fence address bits.
- Semaphore tests should verify wait and signal command encodings and address shifts.
