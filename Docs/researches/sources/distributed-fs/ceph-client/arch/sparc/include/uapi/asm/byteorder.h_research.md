<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h

Purpose: Declares SPARC user ABI byte order.

Important APIs and control flow: includes `linux/byteorder/big_endian.h`, making SPARC UAPI consumers use big-endian integer conversion definitions.

State, dependencies, and risks: no runtime state. Dependencies are generic byteorder headers. Risks are ABI/data corruption if endian assumptions diverge from compiler target, particularly for network, filesystem, and ioctl structures. Test signals are endian macro compile tests and cross-built userspace using kernel headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/byteorder.h -->
