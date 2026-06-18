<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha.c -->
# sources/distributed-fs/ceph-client/crypto/chacha.c

## Purpose

`chacha.c` registers Crypto API skcipher wrappers for ChaCha20, XChaCha20, and XChaCha12 using the shared ChaCha library implementation.

## Important APIs, Types, and Flow

`struct chacha_ctx` stores eight 32-bit key words and the number of rounds. `chacha_setkey()` requires a 32-byte key, loads little-endian words, and records 20 or 12 rounds. `chacha_stream_xor()` initializes a `chacha_state` from the key and IV, walks the skcipher request with `skcipher_walk_virt()`, rounds non-final chunks down to `CHACHA_BLOCK_SIZE`, and calls `chacha_crypt()` to XOR keystream with input.

`crypto_chacha_crypt()` uses the request IV directly. `crypto_xchacha_crypt()` derives a subkey with HChaCha over the first 128 nonce bits, then builds a standard 16-byte ChaCha IV from stream position and remaining nonce bits before calling the shared stream XOR routine.

## State, Dependencies, and Integration

State is per-transform key words and round count. Dependencies are `crypto/chacha.h`, internal skcipher APIs, unaligned little-endian helpers, and skcipher walking. Registered algorithms are `chacha20`, `xchacha20`, and `xchacha12` with driver names ending in `-lib`.

## Risks and Test Signals

Risks include IV layout, XChaCha subkey derivation, block-boundary walking, and round-count selection. Test signals are ChaCha20/XChaCha known-answer vectors, split scatterlist requests, unaligned data, zero-length input, and encrypt/decrypt identity because stream cipher encryption and decryption are identical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha.c -->
