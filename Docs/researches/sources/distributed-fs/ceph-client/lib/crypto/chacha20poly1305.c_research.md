# sources/distributed-fs/ceph-client/lib/crypto/chacha20poly1305.c

## Purpose
ChaCha20-Poly1305 and XChaCha20-Poly1305 AEAD construction, including linear-buffer and in-place scatterlist APIs.

## Important APIs, Types, And Functions
Exports `chacha20poly1305_encrypt()`, `xchacha20poly1305_encrypt()`, `chacha20poly1305_decrypt()`, `xchacha20poly1305_decrypt()`, `chacha20poly1305_encrypt_sg_inplace()`, and `chacha20poly1305_decrypt_sg_inplace()`. Internal helpers include `chacha_load_key()`, `xchacha_init()`, `__chacha20poly1305_encrypt()`, `__chacha20poly1305_decrypt()`, and `chacha20poly1305_crypt_sg_inplace()`.

## Control Flow
Encryption derives the one-time Poly1305 key from ChaCha block 0, authenticates associated data with padding, encrypts plaintext with ChaCha20, authenticates ciphertext with padding and length block, then writes the tag. Decryption authenticates associated data and ciphertext before decrypting on tag match. XChaCha first derives a subkey with HChaCha over the first 16 nonce bytes and builds a 96-bit nonce from the final 8 bytes. Scatterlist mode walks pages atomically, handles partial ChaCha blocks across segments, and stores or verifies the tag at the end of the scatterlist.

## State, Persistence, And Dependencies
All state is per call: `chacha_state`, `poly1305_desc_ctx`, scatterlist iterator, and temporary union. Secret key words, IVs, tags, and stream buffers are explicitly zeroed where held in local unions or states. It depends on ChaCha, Poly1305, zero page padding, scatterlist helpers, unaligned loads, and constant-time `crypto_memneq`.

## Integration Points
Provides exported AEAD helpers used by kernel protocols needing compact crypto-lib primitives without the full crypto API request layer.

## Risks
Nonce reuse with a key is catastrophic and must be prevented by callers. Scatterlist mode has complex tag placement logic when the tag crosses segment boundaries. `src_len > INT_MAX` is rejected for SG mode. Decryption must never release plaintext before tag verification; linear mode satisfies this by decrypting only after `crypto_memneq` succeeds.

## Test Signals
RFC8439 vectors, XChaCha vectors, tampered tag tests, associated-data padding lengths, plaintext lengths around 0/15/16/64, in-place SG layouts with tag split across segments, and nonce/key zeroization checks are strong signals.
