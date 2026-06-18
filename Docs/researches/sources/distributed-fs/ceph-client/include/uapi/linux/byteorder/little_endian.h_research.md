
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h

## Purpose
Defines UAPI byte-order conversion macros for little-endian architectures. It marks the host as little-endian and maps CPU/native, little-endian, big-endian, and network-order conversions to identity casts or byte swaps.

## APIs, Control Flow, and State
The header defines `__LITTLE_ENDIAN`, `__LITTLE_ENDIAN_BITFIELD`, includes `stddef`, `types`, and `swab`, and exports the same constant, value, pointer, and in-place conversion families as the big-endian variant. On little-endian CPUs, little-endian conversions are identity casts, while big-endian/network conversions use swab helpers. It has no runtime state and no function control flow; conversion behavior is selected by preprocessor inclusion.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width/endian types and swab helpers. Integration points are broad: socket protocols, disk formats, device descriptors, ioctl payloads, and user tools that include kernel UAPI headers. Risks include side effects in macro arguments, incorrect bitfield assumptions when a UAPI struct uses `__LITTLE_ENDIAN_BITFIELD`, poor test coverage on big-endian peers, and accidentally using host-order values where an explicit `__be*`/`__le*` conversion is required. Test signals include sparse endian checking, cross-endian protocol/file-image tests, and build coverage for user programs including this header outside the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/byteorder/little_endian.h -->
