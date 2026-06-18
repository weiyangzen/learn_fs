<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authencesn.c -->
# sources/distributed-fs/ceph-client/crypto/authencesn.c

## Purpose

`authencesn.c` implements `authencesn(auth,enc)`, an IPsec AEAD template for extended sequence numbers. It is derived from `authenc` but rearranges high-order ESN bits so the authentication input matches IPsec ESN layout while the packet-associated data remains in normal order.

## Important APIs, Types, and Flow

The template context stores ahash and skcipher spawns; the tfm context stores `reqoff` plus allocated child transforms. `crypto_authenc_esn_setkey()` reuses `crypto_authenc_extractkeys()`, sets both child keys, and clears the temporary key structure. `crypto_authenc_esn_setauthsize()` rejects nonzero authentication sizes below four bytes.

Encryption requires at least eight bytes of associated data. It encrypts payload scatterlists after `assoclen`, then `crypto_authenc_esn_genicv()` moves the high-order ESN bits from the start of associated data to the end of authenticated text, hashes the adjusted stream, restores the bytes, and writes the tag after ciphertext. Decryption copies the supplied tag, performs the same ESN rearrangement for hashing, verifies with `crypto_memneq()`, restores or copies associated data, then decrypts payload.

## State, Dependencies, and Integration

State is per-tfm child ahash/skcipher handles plus per-request scratch scatterlists and digest buffers. The implementation depends on scatterwalk map/copy, `memcpy_sglist()`, ahash and skcipher internals, and the `authenc` key format. It integrates with IPsec users that need ESN-aware AEAD names and request semantics.

## Risks and Test Signals

The main risks are ESN byte shuffling offsets, in-place versus out-of-place copy differences, zero-authsize bypass behavior, `assoclen < 8` rejection, and tag placement after adjusted ciphertext length. Tests should cover ESN AAD lengths, 8/12/16-byte tags, tag mismatch, no-auth mode, asynchronous hash/encrypt completion, and source/destination aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authencesn.c -->
