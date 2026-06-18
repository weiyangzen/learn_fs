# sources/distributed-fs/ceph-client/include/linux/virtio_byteorder.h

## Purpose
This header provides virtio-specific endian conversion helpers for legacy and modern device fields.

## Important APIs, types, and functions
Important helpers are `virtio_legacy_is_little_endian()`, `__virtio16_to_cpu()`, `__cpu_to_virtio16()`, `__virtio32_to_cpu()`, `__cpu_to_virtio32()`, `__virtio64_to_cpu()`, and `__cpu_to_virtio64()`.

## Control flow, state, and persistence
Helpers branch on a runtime `little_endian` boolean or compile-time native endian for legacy devices. There is no state or persistence.

## Dependencies and integration points
It depends on virtio UAPI integer typedefs and CPU endian helpers. It integrates with virtio config-space and ring/data-structure accessors.

## Risks and test signals
Risks include using legacy host-endian rules for modern little-endian devices or vice versa. Tests should cover big-endian and little-endian builds, legacy and VERSION_1 devices, and 16/32/64-bit conversion round trips.
