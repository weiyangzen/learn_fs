# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/byteorder.h

Userspace byte-order selector for ARC. It includes big_endian or little_endian Linux byteorder headers based on __BIG_ENDIAN__. Control flow is compile-time for userspace and kernel UAPI consumers. State is none. Dependencies are compiler endian defines and Linux byteorder UAPI. Risks are toolchains that define endian macros differently, causing ABI misinterpretation. Test signals are headers_install and big/little endian userspace builds.
