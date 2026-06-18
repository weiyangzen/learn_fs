<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h

Purpose: User ABI for `/dev/openprom`, compatible with SunOS/Solaris and BSD openprom interfaces.

Important APIs and control flow: `struct openpromio` carries variable-length property buffers for SunOS-style OPROM ioctls such as get/set option, next property, child/next node, property lookup, console info, framebuffer name, boot args, and Linux extensions for selecting nodes by id, PCI tuple, or path. `struct opiocdesc` supports BSD-style property operations using user pointers.

State, dependencies, and risks: state is PROM/device-tree navigation cursor and firmware properties. Dependencies include Linux ioctl encoding, user-pointer handling, and PROM access drivers. Risks include buffer-size trust, pointer-size compat, exposing firmware mutation, and exact SunOS numeric compatibility. Test signals are property enumeration, path-to-node lookup, boot-args retrieval, console flag retrieval, and compat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/openpromio.h -->
