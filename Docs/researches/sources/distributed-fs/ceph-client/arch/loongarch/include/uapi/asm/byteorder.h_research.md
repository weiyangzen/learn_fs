<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h

Purpose: declares LoongArch UAPI byte order.
Important APIs and types: includes little-endian byteorder definitions.
Control flow: compile-time only; userspace and kernel headers use it for endian conversions.
State and persistence: fixes ABI endian assumptions for structures shared with userspace.
Dependencies and integration: consumed by libc, kernel UAPI structures, networking/filesystem tools, and BPF headers.
Risks and test signals: wrong endian selection corrupts ABI interpretation. Signals include headers_check and userspace cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/byteorder.h -->
