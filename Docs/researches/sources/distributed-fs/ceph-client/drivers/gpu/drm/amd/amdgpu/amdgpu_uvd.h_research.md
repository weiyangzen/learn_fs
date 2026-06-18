# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_uvd.h

## Purpose

`amdgpu_uvd.h` declares the shared data model and entry points for legacy UVD decode support. It defines firmware memory sizing, instance limits, harvest flags, per-instance resources, global UVD state, and the lifecycle/parser/test APIs consumed by UVD IP block implementations and common AMDGPU paths.

## Important Types And APIs

The header sets default and maximum decode handles (`10` and `40`), stack/heap/session sizes, firmware offset, and maximum UVD instances. `AMDGPU_UVD_FIRMWARE_SIZE(adev)` computes aligned firmware payload size from the common firmware header.

`struct amdgpu_uvd_inst` contains the VCPU BO, CPU/GPU addresses, saved BO copy, decode ring, encode rings associated with UVD-era blocks, IRQ source, and soft reset register state. `struct amdgpu_uvd` stores firmware pointer/version, max handles, number of encode rings and UVD instances, address-mode/context-buffer flags, per-instance array, per-handle owning DRM file and atomic handle value, scheduler entity, idle work, harvest config, decode image width, keyselect, and shared message IB BO.

Exported functions cover software init/fini, scheduler entity init, suspend/resume, kernel create/destroy messages, handle cleanup on file close, CS parsing, ring power begin/end hooks, IB testing, and active handle counting.

## Control Flow And Integration

The header supports the common lifecycle: firmware and BO allocation during software init, ring/entity setup by hardware IP code, CS parser use during job submission, per-file handle cleanup on close, suspend/resume preservation, and delayed idle power management. It integrates with `amdgpu_cs_parser`, `amdgpu_job`, `amdgpu_ring`, dma-fence, DRM file ownership, and AMDGPU firmware headers.

## State, Risks, And Tests

State is concentrated in `adev->uvd` and is reset/suspend sensitive. The handle arrays are per-device but owner-tagged by `drm_file`; tests must verify ownership isolation and cleanup. Risks are stale firmware pointers, wrong BO sizing after firmware format changes, harvested instance handling, mismatched max handle assumptions between firmware and driver, and parser/test callers using uninitialized rings.

Test signals include structure initialization defaults, harvested instance skip logic, handle count boundaries, firmware BO sizing, ring entity init only on the primary decode ring, and API behavior when firmware or VCPU BO is absent.
