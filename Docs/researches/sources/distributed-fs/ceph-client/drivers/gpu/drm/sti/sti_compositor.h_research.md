# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.h

Purpose: Defines the public compositor data structures shared by the STI DRM compositor, CRTC, mixer, GDP, VID, and VTG code.

Important APIs/types: `enum sti_compositor_subdev_type` classifies mixer, GDP, VID, and cursor subdevices. `struct sti_compositor_subdev_descriptor` records type, logical id, and register offset. `struct sti_compositor_data` carries the hardware descriptor table, bounded by `MAX_SUBDEV`. `struct sti_compositor` stores device context, register base, clocks, resets, mixer/VID/VTG pointers, and VTG vblank notifier blocks. `sti_compositor_debugfs_init()` is exported to CRTC late registration.

Control/state: The header makes the compositor the shared persistence object for display pipeline construction. `STI_MAX_MIXER` and `STI_MAX_VID` fix array bounds to two mixers and one VID for this generation. `WAIT_NEXT_VSYNC_MS` is a timing constant consumed by display synchronization code in this driver family.

Dependencies/integration: Includes kernel clock/reset-facing types and local `sti_mixer.h`/`sti_plane.h`. It is included by the compositor, CRTC, GDP, HQVDP, cursor, and VID paths to locate common resources.

Risks/test signals: Descriptor bounds must match platform data; adding hardware blocks requires keeping `MAX_SUBDEV`, array limits, and descriptor initialization consistent. Compile-time coverage and KMS enumeration are the primary signals.
