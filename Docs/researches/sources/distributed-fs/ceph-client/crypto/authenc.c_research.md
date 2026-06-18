<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authenc.c -->
# sources/distributed-fs/ceph-client/crypto/authenc.c

## Purpose

`authenc.c` implements the `authenc(auth,enc)` AEAD template used by IPsec-style encrypt-then-authenticate constructions. It composes an ahash authentication algorithm with a skcipher encryption algorithm and exposes them as one AEAD transform.

## Important APIs, Types, and Flow

`crypto_authenc_extractkeys()` parses the `rtattr`-encoded combined key, validates the parameter payload, extracts the encryption-key length, and splits authentication and encryption keys. The template context stores ahash and skcipher spawns plus `reqoff`; each tfm stores allocated child transforms in `crypto_authenc_ctx`.

Encryption copies associated data when source and destination differ, encrypts the payload using the child skcipher over scatterlists advanced past `assoclen`, then computes a hash over `assoclen + cryptlen` bytes in the destination and appends the truncated auth tag. Decryption hashes `assoclen + cryptlen - authsize`, copies the supplied tag from the input, verifies with `crypto_memneq()`, and only then decrypts the ciphertext. Async callbacks preserve original request completion and suppress intermediate `-EINPROGRESS`/`-EBUSY` notifications where needed.

## State, Dependencies, and Integration

Persistent state is the child transform pair and derived request-size layout. Per-request scratch contains two small scatterlist arrays and a tail region containing two digest buffers plus child requests. It integrates with the crypto template system, scatterwalk helpers, `crypto/internal/aead.h`, ahash, skcipher, and the exported key-splitting helper used by `authencesn.c`.

## Risks and Test Signals

Risks include malformed key attributes, insufficient `reqoff` sizing, scatterlist forwarding mistakes, in-place versus out-of-place associated-data handling, and authentication-before-decryption ordering. Test signals are AEAD known-answer tests for valid tags, `-EBADMSG` on tag mismatch, async completion behavior, and key parsing failures for bad rtattrs or inconsistent lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authenc.c -->
