<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h

Purpose: defines legacy Radeon framebuffer ioctl constants for querying MMIO, framebuffer, and AGP aperture regions.

Important APIs and types: ioctl constants such as `FBIO_RADEON_GET_MIRROR`, `FBIO_RADEON_SET_MIRROR`, `FBIO_RADEON_GET_MMON`, and aperture/MMIO query values expose old radeonfb control hooks.

Control flow: legacy userspace opens a framebuffer device and issues Radeon-specific ioctls to query or change display/memory aperture behavior. Actual behavior is implemented by the radeonfb driver.

State and persistence: display mirror and aperture mappings are runtime device state; no persistent state is defined here.

Dependencies and integration points: integrates with fbdev, old Radeon hardware support, mmap users, and legacy display utilities.

Risks and test signals: risks include stale ABI for uncommon hardware, unsafe MMIO exposure, and conflicts with DRM/KMS drivers. Test only on radeonfb configurations: ioctl query/set behavior, mmap bounds, and coexistence exclusion with DRM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/radeonfb.h -->
