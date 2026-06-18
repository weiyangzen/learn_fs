# sources/distributed-fs/ceph-client/include/linux/fsl/netc_global.h

Purpose: provides tiny common MMIO read/write wrappers for NXP NETC code.

Important APIs and functions: `netc_read()` calls `ioread32()` and `netc_write()` calls `iowrite32()` on a supplied `void __iomem *` register address.

Control flow and state: drivers call these helpers when accessing NETC registers. The header owns no state and imposes little-endian/native 32-bit MMIO semantics through the selected accessors.

Dependencies and integration points: depends on Linux I/O accessors and is shared by NETC networking support.

Risks and test signals: risks are mostly endian/register-width assumptions and lack of barriers beyond normal MMIO accessor semantics. Tests should cover register access on supported NETC platforms and compile coverage for consumers.
