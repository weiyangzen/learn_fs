<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h

Purpose: SunOS-compatible framebuffer ioctl and mmap-offset ABI for SPARC framebuffer devices.

Important APIs and control flow: defines framebuffer type IDs, `struct fbtype`, color-map and cursor structures, generic FBIO ioctls, WID allocation/list structures, Creator/FFB ioctls, cg14/MDI configuration and map offsets, and Leo CLUT/map constants. Drivers use these to translate legacy Sun framebuffer applications to Linux device operations.

State, dependencies, and risks: state includes framebuffer geometry, color maps, cursor image/position, WID allocations, CLUTs, video enable state, and mmap region selection. Dependencies include user-pointer annotations, SPARC ioctl encoding, and framebuffer drivers for cg/leo/ffb/creator-class devices. Risks are pointer-size compatibility, unsupported ioctls that must still preserve numeric ABI, mappable offset collisions, and stale hardware-specific constants. Test signals are `FBIOGTYPE`/`FBIOGATTR`, color-map set/get, cursor operations, legacy X server startup, and mmap of documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/fbio.h -->
