# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.h

## Purpose

This header exposes the GFX11 IP block descriptor and one cross-file helper for the GFX index mutex. It is the public interface used by nearby AMDGPU code, including the GFX11.0.3 RAS helper, to reference GFX11 lifecycle registration and coordinate access to CP indexed reset/register state.

## Important APIs, Types, And Data

- `extern const struct amdgpu_ip_block_version gfx_v11_0_ip_block;` exports the GFX11 IP block descriptor implemented in `gfx_v11_0.c`.
- `int gfx_v11_0_request_gfx_index_mutex(struct amdgpu_device *adev, bool req);` requests or releases the hardware `CP_GFX_INDEX_MUTEX` using the GFX11 implementation's polling protocol.
- The declaration depends on `struct amdgpu_device` and `bool` being available to includers through kernel/AMDGPU headers.

## Control Flow

The header has no executable flow, but it exposes a function used by reset-related code. The implementation writes `CP_GFX_INDEX_MUTEX`, waits for ownership or release, and returns `0` or `-EINVAL` on timeout.

## State And Persistence

No state is stored in this header. The mutex helper manipulates hardware state in the GFX CP block and is used to serialize reset-sensitive operations.

## Dependencies And Integration Points

- Included by `gfx_v11_0.c` for its own declarations and by `gfx_v11_0_3.c` for GFX11.0.3 RAS integration.
- Ties consumers to AMDGPU core types and GFX11 register semantics without exposing register constants in the header.

## Risks

- External users of `gfx_v11_0_request_gfx_index_mutex` must pair request/release calls correctly or they may block firmware/driver indexed access.
- Because the header does not document locking requirements, callers must know from implementation context that reset paths also use `adev->gfx.reset_sem_mutex`.

## Test Signals

- Build coverage should catch declaration/definition mismatches.
- Reset-path tests should verify that request and release both succeed and that timeout handling does not leave the hardware mutex held.
