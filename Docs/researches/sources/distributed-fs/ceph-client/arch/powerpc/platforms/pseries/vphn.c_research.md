<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c

Purpose: converts virtual processor home node associativity data returned by the pSeries hypervisor into the standard `ibm,associativity` property cell format.

Important APIs/types/functions: `vphn_unpack_associativity()` decodes packed 16-bit/32-bit fields, and kernel-only `hcall_vphn()` invokes `H_HOME_NODE_ASSOCIATIVITY` and fills a `__be32` associativity buffer. Constants `VPHN_FIELD_UNUSED`, `VPHN_FIELD_MSB`, and `VPHN_FIELD_MASK` describe the packed field encoding.

Control flow: the unpacker first converts `plpar_hcall9()` long return registers to big-endian 64-bit slots, then walks the 16-bit field stream. A high-bit field encodes a 15-bit domain, a low-bit field starts a 31-bit domain completed by the next 16-bit field, and `0xffff` terminates the list. The output cell zero stores the number of associativity domains.

State and persistence: the file has no global mutable state. It transforms a bounded hypervisor return buffer into a caller-provided output buffer.

Dependencies and integration points: uses `asm/vphn.h` constants and `plpar_hcall9()` in kernel builds. The file is also included by a selftest and is intentionally usable from userspace for unpacking validation.

Risks: malformed field streams ending while `is_32bit` is true are not explicitly reported; the current contract trusts the hypervisor buffer shape. Endianness conversion is central because HCALL returns longs while the OF-style output expects big-endian cells.

Test signals: selftests for 15-bit values, 31-bit combined values, terminators, maximum buffer length, and HCALL success paths should validate both unpacking and the `hcall_vphn()` wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vphn.c -->
