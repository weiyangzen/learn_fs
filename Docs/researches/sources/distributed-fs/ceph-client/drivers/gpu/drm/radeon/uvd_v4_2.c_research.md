# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v4_2.c

## Purpose

`uvd_v4_2.c` implements UVD 4.2 firmware memory-controller resume programming. It handles the newer firmware-header layout, programs VCPU cache ranges, writes high address extension registers, and passes the maximum handle count to firmware when needed.

## Important APIs, Types, and Functions

- `uvd_v4_2_resume()` is the sole entry point. It computes firmware start address with an optional `0x200` header skip, writes cache offsets/sizes for firmware, heap, and stack/session memory, writes `UVD_LMI_ADDR_EXT` and `UVD_LMI_EXT40_ADDR`, and optionally writes `UVD_GP_SCRATCH4`.

## Control Flow

Resume derives the firmware cache base from `rdev->uvd.gpu_addr`, skipping the header only when `rdev->uvd.fw_header_present` is true. It then lays out heap and stack/session regions contiguously after the firmware region and writes high address bits separately. New-header firmware receives `max_handles` through scratch register 4.

## State and Persistence Behavior

The function persists firmware buffer layout and max handle count in UVD hardware registers. It assumes generic UVD resume/firmware upload has already established `rdev->uvd.gpu_addr`, `rdev->uvd_fw`, and `rdev->uvd.max_handles`.

## Dependencies and Integration Points

- Depends on Radeon UVD state and `cikd.h` register definitions.
- Used by ASIC resume paths for UVD 4.2 generation chips.

## Risks and Edge Cases

- The firmware size calculation still uses `uvd_fw->size + 4` even when the programmed start skips a 0x200-byte header; buffer layout must account for the header convention exactly.
- No call to `radeon_uvd_resume()` appears in this function, so caller sequencing must perform generic firmware resume before invoking it.
- Address extension registers are derived from the BO base, while cache offset0 may be header-skipped; this must match hardware semantics for upper bits.

## Test Signals

- Resume tests should cover both header-present and legacy firmware images and confirm offset0 differs by 0x200 >> 3 only for new firmware.
- Firmware boot tests should confirm `UVD_GP_SCRATCH4` is programmed with `max_handles` when the header is present.
