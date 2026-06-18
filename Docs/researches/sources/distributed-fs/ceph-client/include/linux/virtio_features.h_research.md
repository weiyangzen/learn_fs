# sources/distributed-fs/ceph-client/include/linux/virtio_features.h

## Purpose
This header defines fixed-size virtio feature bit arrays and helper operations for testing, setting, clearing, copying, and comparing feature sets.

## Important APIs, types, and functions
Important definitions are `VIRTIO_FEATURES_U64S`, `VIRTIO_FEATURES_BITS`, `VIRTIO_BIT()`, `VIRTIO_U64()`, `VIRTIO_DECLARE_FEATURES()`, and helpers `virtio_features_chk_bit()`, test/set/clear/zero/from_u64/equal/copy/andnot.

## Control flow, state, and persistence
Helpers operate on two-u64 arrays representing the supported feature namespace. Constant out-of-range feature bits trigger build errors; dynamic out-of-range bits warn and return false/no-op. State belongs to caller feature arrays and is runtime negotiation state.

## Dependencies and integration points
It depends on bits, bug, and string helpers. It integrates virtio core, transports, vDPA, and any code manipulating feature sets beyond the lower 64 bits.

## Risks and test signals
Risks include assuming only one u64 of features, out-of-range feature indexes, and copying arrays with the wrong size. Tests should cover boundary bits, dynamic invalid bits, equality/copy/andnot, and `VIRTIO_DECLARE_FEATURES()` layout.
