# sources/distributed-fs/ceph-client/net/bluetooth/ecdh_helper.c

## Purpose
This file wraps the kernel KPP/ECDH crypto API for Bluetooth LE Secure Connections key generation and shared-secret computation, including Bluetooth-required endian conversion.

## Important APIs, Types, And Functions
Exported helpers are `compute_ecdh_secret()`, `set_ecdh_privkey()`, `generate_ecdh_public_key()`, and `generate_ecdh_keys()`. `swap_digits()` reverses and byte-swaps 64-bit limbs between Bluetooth little-endian key format and crypto API representation.

## Control Flow
`set_ecdh_privkey()` optionally converts a provided 32-byte private key, encodes an ECDH key blob, and calls `crypto_kpp_set_secret()`, generating a private key when input is NULL. `generate_ecdh_public_key()` submits a KPP public-key request, waits for completion, then converts the 64-byte X/Y point back to Bluetooth little-endian order. `compute_ecdh_secret()` converts peer public key coordinates, submits a shared-secret request, waits, converts the 32-byte secret back, and clears sensitive temporary buffers. `generate_ecdh_keys()` sets/generates a private key then computes the public key.

## State, Persistence, And Dependencies
The caller owns the `struct crypto_kpp *tfm` and key material buffers. This file allocates temporary buffers and KPP requests per call and uses `DECLARE_CRYPTO_WAIT` for asynchronous completion. No state persists beyond the crypto transform's secret.

## Integration Points
SMP/Secure Connections code calls these helpers after allocating an ECDH KPP transform. Kconfig `BT` selects `CRYPTO_ECDH`, and `BT_SELFTEST_ECDH` can exercise these helpers.

## Risks
The code casts byte buffers to `u64 *` in `swap_digits()`, so alignment assumptions should be considered on strict-alignment architectures even though kernel allocations are aligned and caller arrays may be stack or struct fields. Sensitive buffers are cleared with `kfree_sensitive()`, but the public-key temporary buffer is freed normally. Incorrect endian conversion would silently break pairing interoperability.

## Test Signals
Signals include known-answer ECDH selftests, generated public keys accepted by peer SMP, shared secrets matching test vectors, allocation-failure injection returning `-ENOMEM`, crypto request errors propagating, and KMSAN/KASAN coverage of key-buffer access.
