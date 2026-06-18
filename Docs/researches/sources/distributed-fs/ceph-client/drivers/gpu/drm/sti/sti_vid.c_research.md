# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.c

Purpose: Implements the VID mixer-side video layer programmed when the HQVDP plane is committed. It controls viewport registers, masking, color conversion matrices, PSI defaults, and debugfs.

Important APIs/functions: `sti_vid_create()` allocates `struct sti_vid`, records id/register base, and calls `sti_vid_init()`. `sti_vid_commit()` unmasks the VID layer, aligns destination dimensions to even values, converts destination coordinates through VTG helpers, writes viewport origin/stop, and selects BT.709 or BT.601 YCbCr-to-RGB coefficients based on source height. `sti_vid_disable()` masks the layer. `vid_debugfs_init()` exposes register state.

Control flow: The compositor creates VID before planes. During CRTC atomic flush, when an updated plane has descriptor `STI_HQVDP_0`, CRTC calls `sti_vid_commit(compo->vid[0], p->state)` after enabling plane depth/status. Disabling HQVDP causes `sti_vid_disable()`.

State/persistence: `struct sti_vid` stores device, register base, and id. Hardware registers persist viewport, coefficients, alpha, PSI, and ignore-mask state.

Dependencies/integration: Uses DRM plane state, VTG coordinate conversion, HQVDP plane descriptor via CRTC, and mixer enable masks.

Risks/test signals: Colorimetry selection by source height is a coarse heuristic. VID assumes one HQVDP/VID pair at `vid[0]`. Test HQVDP commits at SD/HD heights, viewport alignment, disable mask, debugfs coefficient dump, and mixer interaction.
