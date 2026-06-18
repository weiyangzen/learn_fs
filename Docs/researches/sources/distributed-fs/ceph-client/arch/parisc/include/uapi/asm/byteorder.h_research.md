<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h

Source read size: 7 lines, 194 bytes.

Purpose: declares PA-RISC userspace byte order as big-endian. Important API: includes `linux/byteorder/big_endian.h`. Control flow: none beyond preprocessing. State and persistence: compile-time ABI contract. Dependencies and integration points: used by networking, filesystem, and binary interface headers. Risks: any accidental little-endian assumption corrupts userspace protocol and structure interpretation. Test signals: headers_install, endian conversion compile tests, network packet tests, and filesystem image interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/byteorder.h -->
