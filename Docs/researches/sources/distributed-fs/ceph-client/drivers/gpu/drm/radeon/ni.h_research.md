# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni.h

## Purpose

`ni.h` is a small private header for Northern Islands Radeon support. It exposes only the NI/Cayman helpers that other Radeon source files need without publishing the full implementation details from `ni.c`.

## Important APIs

- `cayman_cp_int_cntl_setup(struct radeon_device *rdev, int ring, u32 cp_int_cntl)` selects a CP ring through `SRBM_GFX_CNTL` and programs `CP_INT_CNTL`.
- `cayman_vm_decode_fault(struct radeon_device *rdev, u32 status, u32 addr)` prints a human-readable VM fault for Cayman/TN memory-client IDs and protection bits.
- `cayman_gpu_check_soft_reset(struct radeon_device *rdev)` inspects GPU status registers and returns a Radeon reset mask.

The only type declaration is the forward declaration for `struct radeon_device`, keeping this header independent of the full Radeon device definition.

## Control Flow and Integration

This header is included by peer Radeon implementation files that need reset, CP interrupt, or VM fault decoding support. For example, `ni_dma.c` calls `cayman_gpu_check_soft_reset()` from DMA lockup detection. The implementation is in `ni.c`; this header just publishes the narrow cross-file contract.

## State, Dependencies, and Persistence

`ni.h` owns no state and performs no persistence. Its declarations imply dependence on Radeon device state and hardware MMIO side effects in the implementations. Consumers must include suitable Radeon headers for `u32` and the complete `struct radeon_device` where they call these functions.

## Risks and Test Signals

The main risk is ABI drift inside the driver: if function signatures or reset-mask semantics change in `ni.c` without updating this header and callers, build failures or incorrect lockup handling follow. Build coverage of all Radeon objects using this header is the primary test signal, with runtime confirmation from DMA/GFX lockup paths and VM fault logs.
