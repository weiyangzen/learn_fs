# sources/distributed-fs/ceph-client/include/net/tls_toe.h

## Purpose

`tls_toe.h` defines the registration and socket hook contract for inline TLS TCP offload engine devices. It is separate from the kTLS netdevice offload structures and focuses on TOE-style listen/hash/unhash integration.

## Important APIs, types, and functions

The main type is `struct tls_toe_device`, containing a device name, global device list node, optional `feature`, `hash`, and `unhash` callbacks, a `release` callback, and a `kref`. Public functions are `tls_toe_bypass()`, `tls_toe_hash()`, `tls_toe_unhash()`, `tls_toe_register_device()`, and `tls_toe_unregister_device()`.

## Control flow

Inline TLS devices register a `tls_toe_device`. Socket hash/listen setup can call the device `hash` callback to program listen state and choose TOE behavior; socket teardown calls `unhash`; bypass logic can decide that a socket should avoid TOE handling. Unregistration drops the device from the list and releases references through the provided `kref` callback.

## State and persistence behavior

Device state persists in registered `tls_toe_device` objects and their reference counts. Per-socket state is external to this header and owned by the inline TLS driver/socket integration.

## Dependencies and integration points

It depends on list and kref primitives and forward-declares `struct sock`. It integrates with inline TLS drivers, TCP listen/hash lifecycle, and module registration.

## Risks and test signals

Risks include unregistering while sockets still hold references, nullable callback handling, device-name collisions, and incomplete cleanup of listen state. Tests should cover register/unregister, hash/unhash ordering, bypass behavior, refcount release, and concurrent socket close during device removal.
