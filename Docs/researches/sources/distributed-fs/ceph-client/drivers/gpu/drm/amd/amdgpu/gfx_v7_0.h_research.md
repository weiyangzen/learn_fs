# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.h

Purpose: this header exposes the GFX7 AMDGPU IP block descriptors used by CIK device discovery and declares the CIK MQD commit helper associated with GFX7 compute queue programming.

Important APIs and types: it declares `gfx_v7_1_ip_block`, `gfx_v7_2_ip_block`, and `gfx_v7_3_ip_block` as `struct amdgpu_ip_block_version` instances, forward-declares `struct amdgpu_device` and `struct cik_mqd`, and declares `int gfx_v7_0_mqd_commit(struct amdgpu_device *adev, struct cik_mqd *mqd)`. The IP block descriptors are consumed by ASIC setup code to add the correct GFX IP version while sharing the implementation in `gfx_v7_0.c`.

Control flow: include guards make the declarations available to CIK setup and any GFX7-adjacent code without pulling in the full AMDGPU or CIK MQD definitions. Device initialization code can reference the declared IP block descriptors and pass them to AMDGPU IP block registration. The MQD commit declaration describes a helper that programs HQD/MQD registers from a prepared CIK MQD, though in the current C file the implementation is private to that translation unit.

State and persistence: the header itself owns no state. It publishes access to const IP block descriptors and a helper signature that operates on caller-owned `amdgpu_device` and `cik_mqd` state. The actual persistent state lives in the GFX7 implementation and in the device's IP block list, ring/MQD BOs, and hardware queue registers.

Dependencies and integration points: consumers need compatible definitions of `struct amdgpu_ip_block_version`, `struct amdgpu_device`, and `struct cik_mqd` from AMDGPU and CIK headers. `cik.c` references the IP block descriptors during ASIC-specific IP block assembly for GFX 7.1, 7.2, and 7.3 devices. The MQD helper declaration implies potential integration with compute queue programming or KFD/KGD code, but the current implementation in `gfx_v7_0.c` is `static` and only called internally.

Risks and edge cases: the declared MQD commit helper does not currently match external linkage in the C implementation, creating a stale or misleading public declaration if any other file tries to call it. Changes to descriptor names or IP version declarations can break CIK device registration. Because the header uses forward declarations, signature drift in the real structures will be caught only at implementation or call sites that include full definitions.

Test signals: compile coverage that includes `cik.c` and `gfx_v7_0.c` is the primary signal. Link coverage should confirm the three IP block descriptors resolve. A targeted check should verify no external call site relies on `gfx_v7_0_mqd_commit` while it remains static, or else the declaration and implementation linkage must be reconciled.
