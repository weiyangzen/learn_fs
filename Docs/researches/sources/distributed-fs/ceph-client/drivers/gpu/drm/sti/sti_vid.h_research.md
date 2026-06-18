# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.h

Purpose: Declares the VID layer object and public operations used by compositor and CRTC code.

Important APIs/types: `struct sti_vid` stores device, register base, and id. `sti_vid_create()` constructs and initializes a VID block. `sti_vid_commit()` programs VID viewport/color conversion from a DRM plane state. `sti_vid_disable()` masks the VID layer. `vid_debugfs_init()` registers debugfs dumps.

Control/state: The VID block is not a DRM plane itself; it is a hardware companion to the HQVDP DRM plane and is driven from CRTC flush based on plane descriptor.

Dependencies/integration: Forward declarations are implicit from included build context; implementation depends on DRM plane state and DRM minor. Used by compositor setup and CRTC atomic flush.

Risks/test signals: Header lacks explicit forward declarations for some referenced structs, relying on include order in users. Build coverage and HQVDP display tests validate the interface.
