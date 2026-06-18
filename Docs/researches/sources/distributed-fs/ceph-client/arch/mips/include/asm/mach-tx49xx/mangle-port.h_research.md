# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/mangle-port.h

Purpose: TX49xx port and memory I/O byte-order policy. It tells generic I/O accessors how to swizzle addresses and byte-swap port values.

Important APIs/types/functions: `__swizzle_addr_{b,w,l,q}` are identity mappings. `ioswabb` and `__mem_ioswabb` return byte values unchanged. `ioswabw`, `ioswabl`, and `ioswabq` convert little-endian port values with `le16_to_cpu`, `le32_to_cpu`, and `le64_to_cpu`; memory forms for word/long/quad are identity.

Control flow, state, and persistence: Pure macro transformations, no state. The control behavior is compile-time substitution in generic `in*`, `out*`, and memory I/O helpers.

Dependencies and integration: Depends on Linux endian helpers and sparse `__force` casts. It integrates with MIPS `io.h` and board drivers expecting little-endian PCI/port data.

Risks and test signals: Wrong endian policy corrupts device register values only on affected access widths. Test by exercising PCI/IDE/network register access on TX49xx and comparing raw register dumps against expected little-endian device specifications.
