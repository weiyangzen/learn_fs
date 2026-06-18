# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.c

## Purpose
`amdgpu_dm_crtc.c` implements AMDGPU Display Manager CRTC lifecycle, vblank/vupdate IRQ control, panel self-refresh coordination, idle optimization work, DM CRTC atomic state management, CRTC property hooks, atomic validation, and CRTC initialization with primary/cursor planes and color-management capabilities.

## Important APIs, Types, And Functions
Public functions include `amdgpu_dm_crtc_handle_vblank`, `amdgpu_dm_crtc_modeset_required`, `amdgpu_dm_crtc_vrr_active_irq`, `amdgpu_dm_crtc_set_vupdate_irq`, `amdgpu_dm_crtc_vrr_active`, `amdgpu_dm_crtc_set_panel_sr_feature`, `amdgpu_dm_is_headless`, `idle_create_workqueue`, `amdgpu_dm_crtc_enable_vblank`, `amdgpu_dm_crtc_disable_vblank`, and `amdgpu_dm_crtc_init`. Static helpers handle idle polling, deferred vblank control, vblank IRQ get/put, state destroy/duplicate/reset, debugfs late registration, optional AMD private regamma property set/get, active-plane counting, helper atomic checks, and ISM defaults.

## Control Flow
Vblank handling notifies DRM and sends pending cursor-only events under the DRM event lock. Vblank enable validates that the CRTC is configured, restores vblank counters when IPS/self-refresh may have hidden interrupts, enables vupdate IRQs for active VRR, gets CRTC/pageflip/vline0 IRQs, and queues deferred work to update active vblank counts and ISM idle state. Atomic check updates active plane counts, requires a primary plane when enabling the CRTC, restricts async flips to fast updates, pulls in the primary plane for VRR handling, and validates DC streams.

## State And Persistence
The file manages runtime DRM object state and retained DC stream references. `amdgpu_dm_crtc_duplicate_state` retains streams and copies VRR/color/CRC/ABM/cursor fields; destroy releases the stream. The idle workqueue tracks `enable` and `running`; vblank deferred work retains a stream until work completion. CRTC initialization records `acrtc` in `adev->mode_info.crtcs`, initializes ISM state, cursor limits, IDs, and DRM color-management sizes.

## Dependencies And Integration Points
It depends on DRM vblank and atomic helpers, AMDGPU IRQ APIs, DC interrupt/stream validation/idle APIs, PSR and Replay helpers, plane initialization, debugfs setup, ISM tracing/events, CRC secure-display activation checks, and color-management constants from `amdgpu_dm.h`. Its CRTC funcs wire in the CRC callbacks declared by `amdgpu_dm_crc.h`.

## Risks
Risks include unbalanced IRQ get/put sequences if later IRQ enablement fails, deferred vblank work running after stream teardown without correct retain/release, event-lock races around cursor-only events, relying on `base.enabled` for vblank enable rejection, async flip classification depending on `update_type`, legacy userspace breakage if primary-plane requirements change, self-refresh enabling while CRC/VRR/replay constraints are stale, and failure paths in CRTC init that may need cleanup if plane initialization partially succeeds.

## Test Signals
Signals include vblank counter/event correctness, cursor-only commits delivering events, VRR enabling vupdate IRQs only when needed, async flip rejection for non-fast updates, CRTC enable rejected without a primary plane, PSR/Replay entry/exit around vblank enable/disable and CRC windows, suspend/resume with IPS vblank restore, DC stream retain/release leak checks, debugfs CRTC registration, and boot/modeset coverage across DCE/DCN/DCN4.01 color-capability differences.
