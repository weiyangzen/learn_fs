# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_vkms.h

Purpose: Declares the vmwgfx VKMS/vblank/CRC interface used by STDU and display-unit code.

Important APIs/types: Device init/cleanup, modeset/vblank lock helpers, vblank timestamp/enable/disable callbacks, CRTC lifecycle/atomic hooks, CRC source functions, and `vmw_vkms_set_crc_surface()`.

Control flow: Device code initializes VKMS once, each CRTC initializes per-DU state, and DRM callback tables route vblank/CRC/atomic events through these functions. STDU atomic flush updates the CRC surface and calls VKMS flush.

State/persistence: No state is declared here; implementation state lives in `struct vmw_private` and per-display-unit VKMS fields.

Dependencies/integration: DRM CRTC/atomic declarations, vmwgfx private/surface types, hrtimer types, `vmwgfx_vkms.c`, and `vmwgfx_stdu.c`.

Risks/test signals: Callback signature drift, lock/unlock protocol misuse, display builds with VKMS hooks, vblank/CRC registration, and atomic modeset lock pairing.
