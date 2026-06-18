
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h

## Purpose
Defines UAPI byte-order conversion macros for big-endian architectures. It marks the host as big-endian and maps CPU/native, little-endian, big-endian, and network-order conversions to either identity casts or byte-swapping helpers.

## APIs, Control Flow, and State
The header defines `__BIG_ENDIAN`, `__BIG_ENDIAN_BITFIELD`, includes `stddef`, `types`, and `swab`, and exports constant, value, pointer, and in-place conversion macros such as `__constant_htonl`, `__constant_cpu_to_le32`, `__cpu_to_be64`, `__le32_to_cpu`, `__cpu_to_le32p`, and `__cpu_to_be32s`. On a big-endian CPU, big-endian/network conversions are identity casts, while little-endian conversions call `___constant_swab*`, `__swab*`, pointer swab, or in-place swab. There is no runtime state; the "control flow" is compile-time selection by including the architecture's byteorder header.

## Dependencies, Integration, Risks, and Tests
Depends on endian-qualified Linux types and swab helpers. Integration points include every UAPI structure with fixed wire/disk endianness, especially filesystems, networking, storage, and ioctl structs containing `__le*` or `__be*`. Risks include including the wrong endian header for the target architecture, losing sparse `__force` type checking through casts, evaluating macro arguments with side effects, and mismatched bitfield layout in headers that key on `__BIG_ENDIAN_BITFIELD`. Test signals include cross-compilation for big-endian architectures, sparse endian warnings, protocol/filesystem round trips, and layout tests for bitfield-bearing UAPI structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/big_endian.h -->
