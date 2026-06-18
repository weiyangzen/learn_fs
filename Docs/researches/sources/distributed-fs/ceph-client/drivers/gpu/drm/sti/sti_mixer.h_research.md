# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.h

Purpose: Defines the STI mixer object and its programming interface for CRTC and plane flush code.

Important APIs/types: `struct sti_mixer` embeds `struct drm_crtc`, register base, device pointer, mixer id, and status. `to_sti_mixer()` converts a CRTC pointer to the containing mixer. Public functions create mixers, set plane status/depth, configure active video area, set background status, and initialize debugfs. `STI_MIXER_MAIN` and `STI_MIXER_AUX` identify the two compositor paths.

Control/state: `enum sti_mixer_status` tracks CRTC lifecycle readiness and deferred disabling. `GAM_MIXER_NB_DEPTH_LEVEL` fixes z-order slots to six programmable levels.

Dependencies/integration: Includes DRM CRTC/debugfs/file headers and `sti_plane.h`. Used by compositor construction, CRTC lifecycle, TVOUT path selection, GDP/HQVDP debug messages, and output bridge clock-parent decisions.

Risks/test signals: The embedded CRTC layout is a core ABI inside this driver. Any change to ids/status must be validated through modeset and output path selection tests.
