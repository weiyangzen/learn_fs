# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.h

## Purpose

`tonga_ih.h` is the public declaration header for the Tonga interrupt handler IP block. It exposes `tonga_ih_ip_block` so AMDGPU ASIC setup code can include the VI/Tonga IH implementation in the device IP block list.

## Important APIs, Control Flow, And State

The only API is `extern const struct amdgpu_ip_block_version tonga_ih_ip_block;`. The header has no executable logic and defines no state. Runtime behavior is implemented in `tonga_ih.c`, where the block installs IH function callbacks, allocates interrupt rings, programs IH registers, and manages suspend/resume and soft reset.

## Dependencies, Risks, And Test Signals

Consumers need AMDGPU IP block type definitions visible through normal include ordering. The risk is configuration-level: selecting this IP block for incompatible hardware would program the wrong IH register model. Compile coverage and probe/interrupt tests on Tonga/VI hardware validate the declaration.
