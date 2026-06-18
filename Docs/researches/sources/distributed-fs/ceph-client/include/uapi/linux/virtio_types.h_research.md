<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h

Purpose: defines the bitwise-tagged virtio scalar integer types used in device structures whose endian interpretation differs between legacy and modern virtio.

Important APIs and types: `__virtio16`, `__virtio32`, and `__virtio64` are bitwise typedefs over unsigned integer widths. Comments define their contract: native-endian for legacy devices and little-endian for standards-compliant devices.

Control flow, state, and persistence: no control flow or state; these types annotate wire-format fields to force explicit conversion at use sites.

Dependencies and integration points: depends on Linux fixed-width types and sparse bitwise annotations; included by virtio ring and device-specific ABI headers.

Risks and test signals: risks include silently treating virtio fields as host endian, sparse warning suppression, and mixing `__le*` with `__virtio*` in shared structs. Test with sparse, big-endian builds, legacy vs modern device negotiation, and compile users of all virtio UAPI headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/virtio_types.h -->
