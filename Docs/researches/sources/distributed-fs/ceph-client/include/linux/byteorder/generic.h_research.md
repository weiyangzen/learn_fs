## sources/distributed-fs/ceph-client/include/linux/byteorder/generic.h

**Purpose:** This header maps architecture-provided byteorder primitives onto standard kernel conversion names.

**Important APIs/types/functions:** It aliases `cpu_to_le64`, `le64_to_cpu`, `cpu_to_le32`, `le32_to_cpu`, `cpu_to_le16`, `le16_to_cpu`, corresponding big-endian forms, pointer forms `*p`, and in-place forms `*s` to underlying `__cpu_to_*`, `__*_to_cpu`, and related architecture/UAPI macros.

**Control flow, state, persistence:** There is no runtime state. The macros are compile-time conversion entry points that may become swaps or no-ops depending on architecture endian.

**Dependencies/integration:** Intended to be included by `big_endian.h` or `little_endian.h` after architecture/UAPI byteorder primitives are defined. Used by on-disk, network, firmware, and MMIO protocol code.

**Risks and test signals:** Risks include using pointer conversion macros on unaligned data, missing architecture definitions, and mixing CPU/native values with annotated endian types. Test signals include sparse endian warnings, unaligned-access tests, filesystem/network protocol interoperability, and cross-endian build coverage.
