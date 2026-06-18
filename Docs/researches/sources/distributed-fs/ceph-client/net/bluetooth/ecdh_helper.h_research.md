# sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.h

## Purpose
This header declares Bluetooth ECDH helper functions built on the kernel KPP crypto API.

## Important APIs, Types, And Functions
It declares `compute_ecdh_secret()`, `set_ecdh_privkey()`, `generate_ecdh_public_key()`, and `generate_ecdh_keys()`, all operating on `struct crypto_kpp` and fixed-size Bluetooth P-256 key buffers.

## Control Flow
There is no executable control flow. The declarations define the SMP-facing crypto helper contract.

## State, Persistence, And Dependencies
The header depends on `<crypto/kpp.h>` and Linux integer types. State is carried by the caller's crypto transform and buffers.

## Integration Points
Bluetooth SMP and selftest code include this header to perform LE Secure Connections ECDH operations without duplicating KPP request plumbing.

## Risks
The API exposes fixed-size arrays by pointer convention; callers must provide correctly sized 32-byte private/secret and 64-byte public-key buffers. The header has no include guard, so duplicate inclusion relies on declarations being identical and harmless.

## Test Signals
Compile tests should catch signature drift. Runtime signals come from SMP pairing and ECDH selftests using the helper functions.
