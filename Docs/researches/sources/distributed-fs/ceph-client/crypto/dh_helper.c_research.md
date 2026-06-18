# sources/distributed-fs/ceph-client/crypto/dh_helper.c

## Purpose
`dh_helper.c` serializes and deserializes DH key material for the KPP API. It packs a `struct kpp_secret` header plus key, modulus `p`, and generator `g` sizes and byte arrays into the buffer accepted by `dh_set_secret()`.

## Important APIs, Types, And Functions
- `crypto_dh_key_len()` returns total serialized length.
- `crypto_dh_encode_key()` writes secret header, three size fields, and key/p/g data into a caller-provided buffer.
- `__crypto_dh_decode_key()` parses the header and size fields and points `struct dh` members directly into the serialized buffer without allocation.
- `crypto_dh_decode_key()` adds generic safety checks: key and generator sizes must not exceed `p_size`, and `p` must not be all zeros.

## Control Flow
Encoding computes the expected end pointer and uses `dh_pack_data()` for each field. It fails if the buffer length is zero or if packing does not exactly fill the provided buffer. Decoding checks minimum size, secret type, expected length, then assigns internal pointers based on size offsets. The public decode wrapper performs additional driver-protection checks.

## State And Persistence
The helper does not allocate or persist state. Decoded pointers alias the caller's input buffer, so the buffer must remain valid through downstream use.

## Dependencies And Integration Points
It depends on `<crypto/dh.h>` and `<crypto/kpp.h>`. The base `dh` implementation uses `crypto_dh_decode_key()`; safe-prime template code uses `__crypto_dh_decode_key()` to permit key-only input with absent `p` and `g`.

## Risks And Edge Cases
The main edge is aliasing: decode does not copy data. The public decoder prevents common driver assumptions from being violated but does not verify primality or generator order. Size arithmetic is simple but relies on `secret.len == crypto_dh_key_len(params)` after sizes are read.

## Test Signals
Tests should cover exact-length encoding/decoding, zero-length buffers, wrong secret type, truncated buffers, key/g larger than p, all-zero p, and key-only safe-prime decode through the internal helper.
