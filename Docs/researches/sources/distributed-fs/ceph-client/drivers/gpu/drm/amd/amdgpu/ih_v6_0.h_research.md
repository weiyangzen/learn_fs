# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_0.h

## Purpose
`ih_v6_0.h` is the public declaration point for the IH v6.0 amdgpu IP block.

## Important APIs, Types, And Functions
It declares `extern const struct amdgpu_ip_block_version ih_v6_0_ip_block;`. The type itself is defined by the amdgpu IP framework and instantiated in `ih_v6_0.c`.

## Control Flow
There is no control flow in the header. Consumers include it so board/IP discovery code can reference the v6.0 IH block and register its lifecycle callbacks.

## State And Persistence
The header owns no state. The declared object represents static driver metadata for IH major 6 minor 0 revision 0.

## Dependencies And Integration Points
The header assumes `struct amdgpu_ip_block_version` is visible or forward-resolvable at include sites. It integrates `ih_v6_0.c` with amdgpu IP block tables.

## Risks
Risk is limited to declaration drift: if the implementation symbol name or IP block version changes without updating this header, build or link failures follow.

## Test Signals
Build coverage is the main test signal. Runtime coverage comes indirectly from devices selecting `ih_v6_0_ip_block`.
