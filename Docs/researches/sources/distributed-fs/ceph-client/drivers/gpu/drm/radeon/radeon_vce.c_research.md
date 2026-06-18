<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c

## Purpose
`radeon_vce.c` manages the Video Coding Engine encoder block. It loads and validates supported VCE firmware versions, allocates firmware/heap BOs, tracks encoding session handles, validates VCE command streams, emits VCE-specific ring packets, and provides ring/IB tests.

## Important APIs, types, and functions
Lifecycle functions are `radeon_vce_init`, `radeon_vce_fini`, `radeon_vce_suspend`, and `radeon_vce_resume`. Runtime power/session helpers are `radeon_vce_note_usage`, `radeon_vce_idle_work_handler`, and `radeon_vce_free_handles`. Test/session IB helpers are `radeon_vce_get_create_msg` and `radeon_vce_get_destroy_msg`. CS validation uses `radeon_vce_cs_parse`, `radeon_vce_validate_handle`, and `radeon_vce_cs_reloc`. Ring integration uses `radeon_vce_semaphore_emit`, `radeon_vce_ib_execute`, `radeon_vce_fence_emit`, `radeon_vce_ring_test`, and `radeon_vce_ib_test`.

## Control flow
Init selects Tahiti or Bonaire firmware by family, loads the blob, scans it for firmware and feedback version strings, rejects unsupported firmware versions, allocates/pins a VRAM VCPU BO sized by VCE generation, and clears handle slots. Resume maps the BO, zeroes it, and either calls the v1.0 firmware loader or copies the firmware directly. Suspend refuses to proceed if encoding sessions are active. Command parsing walks length-prefixed VCE commands, requires a session command before meaningful work, allocates or validates session handles, requires a create command for newly allocated handles, patches/validates relocations for encode/context/bitstream/feedback buffers, forbids commands after destroy, and frees handles on destroy or error after allocation.

## State, dependencies, and integration points
State resides in `rdev->vce`: firmware pointer/version, feedback version, VCPU BO/GPU address, atomic handles, owning DRM files, image sizes, and idle work. It depends on Radeon BO, IB, fence, ring, semaphore, PM/DPM, firmware, ASIC VCE helpers, and command-submission parser structures. It integrates with ring tests and `radeon_test.c` through dummy create/destroy messages.

## Risks and test signals
Risks include fragile firmware string scanning, unsupported active-session suspend, handle collisions, buffer-size under-validation, wrong endian packet emission, and clock gating while fences remain. Test signals include firmware version logs, parser rejection of malformed IBs, VCE ring pointer movement, create/destroy IB fence completion, encoder workload success, and handle cleanup on file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vce.c -->
