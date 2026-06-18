# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.c

Purpose: Provides common STI plane helpers shared by GDP, HQVDP, cursor, and mixer/CRTC code.

Important APIs/functions: `sti_plane_to_str()` maps plane descriptors to readable names. `sti_plane_update_fps()` tracks frame and field counters over a 3-second interval, formats FPS/FIPS strings from the active framebuffer, and optionally logs them. `sti_plane_init_property()` attaches zpos properties and emits debug mapping. Internal helpers choose default zpos: primary 0, overlay 1, cursor 7, with mutable zpos for primary/overlay and immutable cursor zpos.

Control flow: Plane implementations call `sti_plane_update_fps()` after hardware updates or field events. The top-level driver debugfs toggles `fps_info.output`; the CRTC flush uses `plane->status` but this file only defines common property and accounting helpers.

State/persistence: FPS counters, timestamps, output flag, and formatted strings live in `struct sti_fps_info` embedded in each `struct sti_plane`.

Dependencies/integration: Uses DRM blend/zpos properties, framebuffer format metadata, GEM DMA includes, and local plane enums. Debugfs FPS reporting in `sti_drv.c` reads the strings maintained here.

Risks/test signals: FPS formatting casts fourcc to a char string and depends on framebuffer state remaining valid. Test zpos property ranges, cursor immutable zpos, FPS enable bitmask, field-rate reporting for interlaced HQVDP, and no-FB transitions.
