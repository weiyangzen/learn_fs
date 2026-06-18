<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h

Purpose: this local UAPI copy provides Linux fixed-width and endian-tagged type aliases for tools.

Important APIs/types: it includes `asm-generic/int-ll64.h`, defines `__bitwise`, endian typedefs (`__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`), checksum types (`__sum16`, `__wsum`), and 8-byte aligned aliases (`__aligned_u64`, `__aligned_be64`, `__aligned_le64`) when not assembling.

Control flow: no runtime flow; it is a compile-time foundation for UAPI structs.

State and persistence: no state. Layout and alignment choices influence all ABI structs that include these types.

Dependencies/integration: consumed by most headers in this subset, especially networking, perf, statx, namespace, and userfaultfd headers.

Risks and test signals: risks are compiler compatibility and alignment differences across architectures. Test by compiling representative UAPI structs and checking size/alignment against kernel expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/types.h -->
