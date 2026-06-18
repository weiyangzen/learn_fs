<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c

## Purpose
`radeon_uvd.c` manages the Unified Video Decoder block: firmware selection/loading, decoder BO allocation, session handle tracking, command-stream validation, dummy messages for tests, runtime clock/power usage, and UPLL divider calculation.

## Important APIs, types, and functions
Lifecycle APIs are `radeon_uvd_init`, `radeon_uvd_fini`, `radeon_uvd_suspend`, and `radeon_uvd_resume`. Session cleanup uses `radeon_uvd_free_handles`; placement constraints use `radeon_uvd_force_into_uvd_segment`. CS validation is centered on `radeon_uvd_cs_parse`, with helpers `radeon_uvd_cs_reg`, `radeon_uvd_cs_reloc`, `radeon_uvd_cs_msg`, `radeon_uvd_cs_msg_decode`, and `radeon_uvd_validate_codec`. Test/message helpers include `radeon_uvd_get_create_msg`, `radeon_uvd_get_destroy_msg`, and `radeon_uvd_send_msg`. Power helpers are `radeon_uvd_note_usage`, `radeon_uvd_idle_work_handler`, `radeon_uvd_calc_upll_dividers`, and `radeon_uvd_send_upll_ctlreq`.

## Control flow
Init chooses firmware by ASIC family, tries newer Bonaire firmware before legacy fallback, validates new-style headers, sets max handle count based on firmware version, allocates/pins/maps a VRAM VCPU BO sized for firmware, stack, heap, and sessions, and clears handle arrays. Resume copies firmware into the BO and zeroes the remaining working area. Suspend and file-close cleanup destroy active handles by sending destroy messages and waiting on fences. CS parsing requires 16-dword IB alignment and relocation chunks, accepts only selected packet/register writes, requires a message command before other commands, validates handle ownership, codec support, DPB/image sizes, buffer bounds, and 256MB segment restrictions.

## State, dependencies, and integration points
Persistent state is in `rdev->uvd`: firmware pointer, header flag, max handles, VCPU BO CPU/GPU addresses, atomic handles, owning DRM files, image sizes, and delayed idle work. It integrates with BO/GEM, command submission, relocation validation, UVD ring scheduling, fences, PM/DPM clocks, firmware loading, and test code.

## Risks and test signals
Risks include firmware fallback mistakes, handle leaks/collisions, accepting malformed decode messages, relocation buffers crossing 256MB boundaries, insufficient DPB checks, and clock-off while work is pending. Signals include UVD firmware version logs, CS parser rejections, UVD IB/ring tests, decode workload success, handle cleanup on file close/suspend, fence completion, and idle clock-down behavior after one second of inactivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_uvd.c -->
