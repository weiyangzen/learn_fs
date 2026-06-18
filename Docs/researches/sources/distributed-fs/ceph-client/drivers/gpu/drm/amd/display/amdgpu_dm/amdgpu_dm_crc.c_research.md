# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.c

## Purpose
`amdgpu_dm_crc.c` implements DRM CRTC CRC capture for AMD display pipes and, when secure display is enabled, ROI/window CRC handling used by secure-display workflows. It parses debugfs CRC source names, configures DC stream CRC generation and dithering, manages vblank references, reads CRC values on IRQ, and coordinates secure-display ROI updates with DMUB/DC and PSP TA work.

## Important APIs, Types, And Functions
Public functions include `amdgpu_dm_crtc_get_crc_sources`, `amdgpu_dm_crtc_verify_crc_source`, `amdgpu_dm_crtc_configure_crc_source`, `amdgpu_dm_crtc_set_crc_source`, `amdgpu_dm_crtc_handle_crc_irq`, and secure-display functions `amdgpu_dm_crc_window_is_activated`, `amdgpu_dm_crtc_handle_crc_window_irq`, and `amdgpu_dm_crtc_secure_display_create_contexts`. Helpers parse sources, classify CRTC vs DPRX sources, decide dithering, sort connectors into secure-display PHY IDs, map MST ports by RAD/LCT, reset CRC windows, notify PSP TA, and forward ROI windows to DC/DMUB.

## Control Flow
Setting a CRC source takes the CRTC modeset lock, waits for outstanding hardware commits, resolves DP AUX for DPRX capture when needed, obtains or releases a vblank reference, resets secure-display windows, calls DC CRC configuration, starts/stops DP AUX CRC when applicable, updates `acrtc->dm_irq_params.crc_src`, resets skip count, and initializes secure-display PHY mapping for legacy mode. IRQ handling skips the first two frames after enabling, then reads DC stream CRC and submits DRM CRC entries.

## State And Persistence
Runtime state lives in `amdgpu_crtc.dm_irq_params`, `dm_crtc_state.crc_skip_count`, secure-display CRTC contexts, and the display manager secure-display context. Work items persist across IRQs until flushed or device teardown. No state is persisted to disk; CRC values are emitted through DRM debugfs/readback and secure-display paths.

## Dependencies And Integration Points
The file depends on DRM CRTC/vblank/DP AUX CRC APIs, AMD DC stream CRC/dither/dynamic-expansion calls, AMDGPU IRQ and reset state, PSR/Replay disable hooks, secure-display PSP TA APIs, connector/MST topology state, and `dc_lock`/event/mode-config synchronization. It integrates with `amdgpu_dm_crtc.c` vblank IRQ enablement and secure-display vline0 interrupt handling.

## Risks
Risks include lock-order regressions among CRTC mutex, commit lock, event lock, mode-config mutex, `dc_lock`, and PSP mutex; vblank reference leaks on partial enable failures; secure-display PHY mapping staleness after hotplug; MST RAD sorting mistakes; CRC window updates racing with IRQ reads; first-frame skip assumptions hiding hardware readiness issues; and PSR/Replay interactions if CRC is enabled or disabled around panel self-refresh transitions.

## Test Signals
Signals include debugfs CRC source enumeration, invalid source rejection, enabling/disabling CRTC CRC with correct vblank reference counts, DPRX CRC on DP/eDP and rejection on non-DP connectors, dither variants changing DC dither configuration, first two CRC frames skipped, PSR/Replay disabled while CRC is active, secure-display ROI updates producing CRC/frame counters, MST secure-display mapping stability, and suspend/hotplug/reset tests while CRC capture is active.
