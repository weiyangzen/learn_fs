# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.h

## Purpose

`gfx_v8_0.h` is the public internal header for the AMDGPU GFX8 implementation. It exposes the GFX8 IP block descriptors and the MQD commit helper implemented in `gfx_v8_0.c` so other AMDGPU compilation units can register or program GFX8 hardware without including the large implementation file.

The header is intentionally small: it is a declaration boundary, not a policy or state owner.

## Important APIs, Types, and Symbols

- Include guard: `__GFX_V8_0_H__` prevents duplicate declarations.
- `extern const struct amdgpu_ip_block_version gfx_v8_0_ip_block;` declares the GFX IP block descriptor for GFX 8.0 hardware.
- `extern const struct amdgpu_ip_block_version gfx_v8_1_ip_block;` declares the GFX IP block descriptor for GFX 8.1 hardware, which currently uses the same implementation callback table as 8.0.
- Forward declarations: `struct amdgpu_device;` and `struct vi_mqd;` avoid pulling in full AMDGPU and VI MQD structure definitions for users that only need the function prototype.
- `int gfx_v8_0_mqd_commit(struct amdgpu_device *adev, struct vi_mqd *mqd);` exposes the helper that writes a prepared VI MQD/HQD register image into selected hardware queue registers.

## Control Flow

ASIC/IP selection code includes this header to reference `gfx_v8_0_ip_block` or `gfx_v8_1_ip_block` when building the device's IP block list. Once the AMDGPU core walks the selected IP block, the callback table in `gfx_v8_0.c` drives early init, software init, hardware init, suspend/resume, reset, and gating.

Queue setup code can call `gfx_v8_0_mqd_commit()` after selecting a MEC/pipe/queue with SRBM routing. The function expects the caller to provide an initialized `struct vi_mqd` and the correct hardware selection/serialization context; the header itself does not enforce those preconditions.

## State and Persistence Behavior

The header stores no state. The exported IP block descriptors are immutable `const` objects defined in `gfx_v8_0.c`. MQD contents are supplied by the caller and represent persistent queue state stored elsewhere, commonly in ring MQD BOs and backup buffers under `adev->gfx`.

## Dependencies and Integration Points

This header depends on users having declarations for `struct amdgpu_ip_block_version`, typically through AMDGPU internal headers included before or alongside it. It integrates with VI ASIC setup code, the AMDGPU IP block framework, and queue/MQD management paths that need direct access to the GFX8 MQD commit primitive.

The `vi_mqd` forward declaration ties the API to VI-generation MQD layout, so it is not a generation-neutral queue commit interface.

## Risks and Edge Cases

- `gfx_v8_0_mqd_commit()` is low-level and hardware-stateful. Calling it without selecting the intended ME/pipe/queue or without holding the relevant SRBM serialization can write an MQD into the wrong HQD.
- The header does not include the full type definitions. Callers must include the appropriate AMDGPU/VI headers when they need to allocate or inspect `struct vi_mqd`.
- The two exported IP block descriptors share implementation callbacks in the `.c` file; future GFX8.1 divergence would require either additional callbacks or careful branching in the shared implementation.

## Test and Validation Signals

- Build coverage should include all ASIC setup files that reference `gfx_v8_0_ip_block`, `gfx_v8_1_ip_block`, or `gfx_v8_0_mqd_commit()`.
- Queue tests should verify callers select the correct MEC/pipe/queue before invoking `gfx_v8_0_mqd_commit()`.
- IP discovery/probe tests should confirm GFX 8.0 and 8.1 devices register the intended descriptor and execute the `gfx_v8_0.c` lifecycle callbacks.
