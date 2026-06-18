# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vce.h

## Purpose

`amdgpu_vce.h` declares the shared VCE encoder state and public helper APIs for legacy AMD video encode blocks. It is consumed by VCE hardware IP implementations, command submission, file cleanup, power management, and ring setup code.

## Important Types And APIs

The header defines `AMDGPU_MAX_VCE_HANDLES` as 16, the firmware offset, harvest flags for two VCE blocks, and a firmware version helper constant. `struct amdgpu_vce` holds the VCPU BO and addresses, optional saved BO pointer, firmware and feedback versions, per-session atomic handles, per-session owning `drm_file`, per-session image size, delayed idle work, idle mutex, firmware pointer, VCE rings, IRQ source, harvest config, scheduler entity, soft reset state, ring count, keyselect, and a GART node.

Exports cover early firmware init, software init/fini, scheduler entity init, suspend/resume, file-close handle cleanup, non-VM and VM command stream parsing, IB/fence ring emission, ring/IB tests, begin/end power-use hooks, ring sizing helpers, and priority mapping.

## Control Flow And Integration

The common flow is firmware load in early init, VCPU BO allocation in software init, ring/entity setup, CS parser enforcement during submissions, idle power management around ring use, and teardown on software fini. Handle ownership spans submissions, so close cleanup and parser rollback are key integration points.

Dependencies include `amdgpu_device`, `amdgpu_ring`, `amdgpu_job`, `amdgpu_cs_parser`, dma-fence, firmware, DRM file ownership, and power management. Several functions are implemented in `amdgpu_vce.c`; sizing helpers may be provided by IP-version-specific code.

## State, Risks, And Tests

State is per-device and mostly in-memory/GPU-BO backed. Risks include stale handles, mismatched ring counts, use of VCE APIs when firmware is absent, suspend attempts with live sessions, and incorrect image size state driving reloc validation. Test signals should cover init/fini idempotence, ring count boundaries, handle ownership isolation, parser entry points, and firmware/BO absent cases.
