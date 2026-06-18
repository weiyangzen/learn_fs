# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ctx.h

Purpose: this header defines amdgpu context and context-manager structures plus the APIs used by command submission, waits, scheduling, and file teardown.

Important APIs/types: `AMDGPU_MAX_ENTITY_NUM` caps per-HW-IP entity slots. `struct amdgpu_ctx_entity` stores the hardware IP, next sequence number, DRM scheduler entity, and flexible array of recent fences. `struct amdgpu_ctx` stores refcounting, ring lock, reset/query counters, priority, stable pstate, guilty flag, preamble state, VM generation, RAS counters, manager pointer, and entity table. `struct amdgpu_ctx_mgr` stores the device pointer, context IDR lock, IDR, and per-HW-IP time counters. The header declares context lookup/refcount, entity lookup, fence add/get, priority validation/override, ioctl, previous-fence wait, manager lifecycle, and usage APIs.

Control flow and integration: CS code obtains contexts and scheduler entities through this API, stores submission fences, and waits for previous fences. DRM ioctl dispatch calls `amdgpu_ctx_ioctl()`. File lifecycle code initializes, flushes, and finalizes the manager. Diagnostics can call usage accounting.

State and persistence: all structures are per-process/per-device in memory. Fence arrays retain only a bounded recent history sized by `amdgpu_sched_jobs`; old fences intentionally become unavailable.

Dependencies: the header depends on ktime/types, `amdgpu_ring.h`, DRM file/device forward declarations, dma-fence, kref, IDR, mutex, and scheduler entity definitions pulled through included amdgpu headers.

Risks: structure fields are tightly coupled to `amdgpu_ctx.c` cleanup and CS assumptions. The flexible fence array requires allocation with enough elements. Any change to entity counts affects userspace-visible ring validation and scheduler selection.

Test signals: compile coverage across CS, KMS file lifecycle, and scheduler code; runtime CS/wait ioctl tests; and memory-safety checks around context refcounting and manager finalization.
