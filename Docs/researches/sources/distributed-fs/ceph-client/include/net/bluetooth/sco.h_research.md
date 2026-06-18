# sources/distributed-fs/ceph-client/include/net/bluetooth/sco.h

## Purpose
This header defines the minimal SCO Bluetooth socket ABI used for synchronous audio links. It provides the default SCO MTU, socket address format, and socket option payloads for MTU and connection metadata.

## Important APIs, Types, And Constants
- `SCO_DEFAULT_MTU` is the default payload size.
- `struct sockaddr_sco` carries the address family and peer Bluetooth address.
- `SCO_OPTIONS` with `struct sco_options` exposes the negotiated MTU.
- `SCO_CONNINFO` with `struct sco_conninfo` exposes HCI handle and remote class-of-device bytes.

## Control Flow And State
There is no executable flow here. SCO socket implementation code uses these records in bind/connect/getsockopt/setsockopt paths. A userspace socket addresses a peer with `sockaddr_sco`; once connected, getsockopt-style queries return MTU and HCI connection identity.

## State And Persistence Behavior
The header defines transient socket-visible state only. MTU, HCI handle, and device class are derived from the live SCO/HCI connection and are not persisted by this file.

## Dependencies And Integration Points
The file depends on `sa_family_t`, `bdaddr_t`, and fixed-width Linux integer aliases. It integrates with the Bluetooth SCO protocol implementation and HCI connection layer.

## Risks
- These structs are userspace ABI; field order and width must remain stable.
- SCO code must ensure `sco_conninfo` reflects a valid live HCI connection and does not expose stale handle data after disconnect.

## Test Signals
- SCO socket ABI tests should validate address sizes and `SCO_OPTIONS`/`SCO_CONNINFO` getsockopt payload lengths.
- Audio/SCO integration tests should cover default MTU, connect/disconnect, and HCI handle reporting.
