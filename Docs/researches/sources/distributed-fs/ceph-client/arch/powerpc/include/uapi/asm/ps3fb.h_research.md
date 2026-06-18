<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h

Purpose: Defines PlayStation 3 framebuffer ioctl ABI.

Important APIs/types/functions: `PS3FB_IOCTL_*`, fallback `FBIO_WAITFORVSYNC`, and `struct ps3fb_ioctl_res`.

Control flow: Userspace framebuffer tools issue ioctls to set/get mode, get screen info, enable/disable special operation, request flip, and wait for vsync.

State and persistence: Framebuffer mode and flip state live in the ps3fb driver/hardware; the struct reports resolution, offset, and frame count.

Dependencies and integration points: Depends on Linux ioctl/types and the PS3 framebuffer driver.

Risks: Ioctl numbers and struct layout are ABI. Mode changes can disrupt console/display users.

Test signals: ps3fb ioctl smoke tests, mode set/get tests, vsync wait, and headers compile checks.

Source read size: 33 lines, 1110 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ps3fb.h -->
