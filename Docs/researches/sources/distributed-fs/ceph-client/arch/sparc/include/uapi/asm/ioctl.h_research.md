<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h

Purpose: Defines SPARC ioctl number encoding.

Important APIs and control flow: `_IOC` packs direction, type, number, and size using SPARC's overlapping DIR/SIZE layout to preserve nonzero `_IOC_NONE` while retaining a 14-bit decoded size. `_IO`, `_IOR`, `_IOW`, `_IOWR`, and decoder macros are used by drivers and UAPI headers. Legacy `IOC_IN`, `IOC_OUT`, and size masks support PCMCIA/sound-style consumers.

State, dependencies, and risks: state is ABI numbering for every SPARC ioctl. Dependencies are compiler `sizeof` and driver decoder usage. Risks are command-number collisions, incorrect size decoding for `_IOC_NONE`, and cross-architecture assumptions in shared drivers. Test signals are ioctl number compile assertions, strace/driver decoding, and compat ioctl dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ioctl.h -->
