# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq_params.h

## Purpose
`amdgpu_dm_irq_params.h` defines the per-CRTC Display Manager IRQ parameter bundle used by vblank, pageflip, VRR/FreeSync, PSR/Replay, CRC, and secure-display paths.

## Important APIs, types, and functions
The central type is `struct dm_irq_params`, containing `last_flip_vblank`, `vrr_params`, active `stream`, `active_planes`, `allow_sr_entry`, `freesync_config`, debugfs CRC source and polynomial mode fields, and optional secure-display CRC window parameters plus `crc_window_activated`.

## Control flow
The header has no executable logic. Runtime code stores this struct in `struct amdgpu_crtc` and updates it from IRQ, debugfs, CRC, FreeSync, and PSR/Replay paths.

## State and persistence behavior
The struct is runtime-only CRTC state. It tracks active stream and interrupt-related parameters and is reset with driver/CRTC state.

## Dependencies and integration points
It includes `amdgpu_dm_crc.h` and integrates CRTC IRQ handling with DC stream state, FreeSync config, debugfs pipe CRC controls, and optional secure-display CRC windows.

## Risks and edge cases
The `stream` pointer must only be used while the owning CRTC state is valid. CRC fields are config-gated, so callers need matching guards. Secure-display window updates share state with IRQ/debugfs contexts and require correct locking.

## Test signals
Compile with and without debugfs/secure-display configs, pipe CRC tests, secure CRC window tests, VRR/vblank behavior, pageflip tracking, and PSR/Replay self-refresh checks validate this header.
