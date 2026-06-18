<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h

**Purpose:** Provides MIPS-optimized IP checksum operations unless `CONFIG_GENERIC_CSUM` is selected.

**Important APIs/types/functions:** Declares `csum_partial`, user copy/checksum helpers, `csum_fold`, `ip_fast_csum`, `csum_tcpudp_nofold`, `ip_compute_csum`, and `csum_ipv6_magic`.

**Control flow:** User copy helpers validate access and call assembly helpers. Inline checksum functions perform one's-complement carry folding and use inline assembly for IPv6 pseudo-header summing.

**State, dependencies, integration:** Used by networking stack and user copy paths. Depends on endian config, 32/64-bit arithmetic, and uaccess.

**Risks and test signals:** Carry handling and endian shifts are easy to break. Test IPv4/IPv6 checksum vectors, odd-length fragments, user access failure returning zero, 32/64-bit builds, and little/big endian.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h -->
