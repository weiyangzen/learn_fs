# sources/distributed-fs/ceph-client/crypto/ecdh_helper.c

## Purpose
`ecdh_helper.c` serializes and deserializes ECDH private-key material for the KPP API. The serialized form is a `struct kpp_secret`, a key-size field, and optional key bytes.

## Important APIs, Types, And Functions
- `crypto_ecdh_key_len()` returns serialized length.
- `crypto_ecdh_encode_key()` writes header, key size, and key bytes.
- `crypto_ecdh_decode_key()` parses the header, validates type and length, and points `params->key` into the original buffer.

## Control Flow
Encoding rejects a NULL buffer and requires the provided length to match `crypto_ecdh_key_len(params)`. Decoding rejects NULL/truncated buffers, wrong secret type, and inconsistent lengths. It does not allocate; it assigns the key pointer to the payload after the key-size field.

## State And Persistence
No state is retained. Decoded keys alias caller memory, so buffer lifetime must cover consumer parsing.

## Dependencies And Integration Points
The helper uses `<crypto/ecdh.h>` and `<crypto/kpp.h>` and is consumed by `ecdh_set_secret()` in `ecdh.c`.

## Risks And Edge Cases
The helper validates serialization but not curve-specific key size or scalar range; `ecdh.c` and `ecc.c` perform those checks. Empty key payload is valid and means "generate a private key" to `ecdh_set_secret()`.

## Test Signals
Tests should cover valid explicit keys, empty key generation requests, NULL buffer rejection, truncated secret headers, wrong secret type, and mismatched encoded length.
