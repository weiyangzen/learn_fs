# sources/distributed-fs/ceph-client/net/ceph/auth_x_protocol.h

## Purpose
Defines CephX wire-protocol constants and packed message structures shared by the CephX backend.

## Important APIs, Types, and Functions
Constants include request opcodes `CEPHX_GET_AUTH_SESSION_KEY`, `CEPHX_GET_PRINCIPAL_SESSION_KEY`, `CEPHX_GET_ROTATING_KEY`, key usage numbers for auth connection secrets, ticket session keys, ticket blobs, authorizers, challenges, and replies, plus `CEPHX_ENC_MAGIC`. Packed structs describe ticket blobs, request/reply headers, server challenge, authenticate request, service ticket request, challenge proof blob, authorizer parts A and B, authorize challenge/reply, and encrypted bundle header.

## Control Flow
No code runs here. `auth_x.c` fills, encrypts, decrypts, and validates these layouts while constructing monitor and service auth messages.

## State and Persistence
No runtime state. The definitions are ABI contracts for on-wire message layout and must remain byte-stable.

## Dependencies and Integration Points
Used by `auth_x.c` and `auth_x.h`. The packed little-endian fields integrate with Ceph protocol encoders and monitor/service peers.

## Risks
Changing struct layout, packing, field order, or key usage constants would break interoperability. The comments distinguish client-auth, ticket, and service-authorizer encryption contexts; using the wrong usage value weakens or breaks authentication. `CEPHX_ENC_MAGIC` is a key validation signal after decryption.

## Test Signals
Wire-compatibility tests against userspace Ceph, decode/encode tests for every struct version, encrypted-header magic validation, and cross-version tests for Nautilus-era authenticate/service-ticket behavior.
