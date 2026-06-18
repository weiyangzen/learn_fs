# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.c

Purpose: Implements low-level mixer register programming for main/aux composition: background color/area, active video area, plane enable masks, z-order depth, and debugfs state.

Important APIs/functions: `sti_mixer_create()` allocates `struct sti_mixer` and records id/register base. `sti_mixer_active_video_area()` writes active video and background bounds from DRM mode via VTG coordinate helpers, sets the module-param background color, and enables background. `sti_mixer_set_plane_depth()` maps STI plane descriptors to crossbar depth ids and updates `GAM_MIXER_CRB` using normalized zpos. `sti_mixer_set_plane_status()` maps plane descriptors to `GAM_MIXER_CTL` masks and enables/disables layers. `sti_mixer_debugfs_init()` exposes register dumps for main/aux mixers.

Control flow: CRTC mode set programs active/background geometry; CRTC atomic flush calls depth then status for updated planes and status false for disabling planes. Cursor depth is immutable/no-op.

State/persistence: Mixer has only dev, register base, id, embedded CRTC, and status. Background color is a writable module parameter `bkgcolor`.

Dependencies/integration: Uses DRM debugfs, local plane descriptors/status, VTG coordinate conversion, and CRTC ownership through `to_sti_mixer`.

Risks/test signals: Depth update searches existing plane assignment but can operate with an uninitialized `mask` if the plane id is not found before the loop completes; this path deserves review. Test zpos changes, layer enable/disable, background color parameter, active area for multiple modes, and mixer debugfs CRB/CTL decoding.
