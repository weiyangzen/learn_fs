# sources/distributed-fs/ceph-client/net/ceph/crypto.h

## Purpose
Declares libceph crypto key structures, size limits, cryptographic helper APIs, armor helpers, and crypto module init/shutdown hooks.

## Important APIs, Types, and Functions
Constants are `CEPH_MAX_KEY_LEN` and `CEPH_MAX_CON_SECRET_LEN`. `struct ceph_crypto_key` stores key type, creation time, length, key bytes, and either an AES skcipher transform or AES256-KRB5 HMAC/KRB5 transform state. Declared functions cover key prepare/clone/decode/unarmor/destroy, `ceph_crypt()`, buffer offset/length helpers, `ceph_hmac_sha256()`, `ceph_crypto_init()`, `ceph_crypto_shutdown()`, `ceph_armor()`, and `ceph_unarmor()`.

## Control Flow
No executable flow. The header defines contracts implemented by `crypto.c` and `armor.c`, and consumed by auth and common option parsing.

## State and Persistence
The declared key struct owns sensitive heap state and crypto transforms when instantiated. Callers are responsible for zero-initializing before decode/clone and for `ceph_crypto_key_destroy()` cleanup.

## Dependencies and Integration Points
Depends on SHA-2 helper types, Ceph type definitions, and `struct ceph_buffer`. Included by auth-none/CephX/common crypto users.

## Risks
The KRB5 transform array has three slots, so all usage arrays must fit. Increasing `CEPH_MAX_KEY_LEN` or connection secret length affects protocol validation and stack/user buffers. The union means cleanup must branch on key type correctly.

## Test Signals
Compile all crypto users, static checks for usage array sizes, key lifecycle tests for each key type, and ABI review when changing struct fields or constants.
