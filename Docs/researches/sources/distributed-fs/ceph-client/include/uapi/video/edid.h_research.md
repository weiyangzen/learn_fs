<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/edid.h -->
# sources/distributed-fs/ceph-client/include/uapi/video/edid.h

Purpose: provides the minimal UAPI EDID block wrapper used by legacy framebuffer/video interfaces.

Important APIs and types: `struct edid_info` contains a single 128-byte `dummy` array representing one base EDID block.

Control flow: drivers or legacy ioctls can pass a raw 128-byte EDID block through this struct without interpreting it in the header.

State and persistence: no state is stored. The bytes represent display-provided configuration data read at runtime from monitor firmware.

Dependencies and integration points: this UAPI header is included by the kernel wrapper `include/video/edid.h` and old framebuffer paths that need a stable EDID container.

Risks and test signals: risks are mainly legacy ABI expectations and the fixed single-block size not covering extension blocks. Test compile inclusion from userspace/kernel wrappers and EDID read paths that still expose `edid_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/video/edid.h -->
