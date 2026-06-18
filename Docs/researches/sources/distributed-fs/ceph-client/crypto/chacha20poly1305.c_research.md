<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c -->
# sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c

## Purpose

`chacha20poly1305.c` implements RFC7539 ChaCha20-Poly1305 AEAD templates, including `rfc7539` with 12-byte IVs and `rfc7539esp` with 8-byte packet IVs plus a salt stored in the key.

## Important APIs, Types, and Flow

The template instance stores a skcipher spawn and salt length. Each tfm stores the child ChaCha skcipher and flexible salt. `chachapoly_setkey()` requires `CHACHA_KEY_SIZE + saltlen`, stores the salt suffix, and sets the child ChaCha key. `chacha_iv()` builds the 16-byte ChaCha IV as little-endian initial block counter, salt, and request IV bytes.

Encryption sets `rctx->cryptlen` to plaintext length, encrypts payload with counter 1, derives the Poly1305 key by ChaCha block counter 0, hashes AAD and ciphertext with Poly1305 padding plus 64-bit length trailer, and writes the tag to the destination scatterwalk. Decryption derives the Poly1305 key first, hashes AAD and ciphertext, verifies the tag from the input, then decrypts with counter 1. Async continuations clear MAY_SLEEP after callback entry and complete only terminal statuses.

## State, Dependencies, and Integration

State is per-tfm child skcipher and optional ESP salt; per-request state stores scratch scatterlists, Poly1305 one-time key, calculated tag, lengths, flags, and embedded skcipher request. Dependencies include internal AEAD/skcipher/hash headers, `crypto/chacha.h`, `crypto/poly1305.h`, scatterwalk, and ZERO_PAGE padding.

## Risks and Test Signals

Risks include salt/key length mismatch, ESP AAD adjustment, tag verification ordering, scatterwalk tag placement, zero-length plaintext, and async continuation status. Test signals are RFC7539 and ESP vectors, invalid authsize, bad tag `-EBADMSG`, associated-data-only messages, in-place/out-of-place operation, and child ChaCha algorithm validation during template creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c -->
