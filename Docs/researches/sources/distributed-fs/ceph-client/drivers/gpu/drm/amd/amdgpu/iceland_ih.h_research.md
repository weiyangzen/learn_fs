# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.h

## Purpose
`iceland_ih.h` declares the Iceland/VI interrupt-handler IP block.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_ip_block_version iceland_ih_ip_block;`, which points device/IP setup code to the implementation in `iceland_ih.c`.

## Control Flow, State, Integration, And Risks
The header has no executable code or state. It depends on the AMDGPU IP block type definition being available to consumers. Build/link coverage catches symbol drift; runtime validation is successful VI IH probe, interrupt ring initialization, and IRQ delivery.
