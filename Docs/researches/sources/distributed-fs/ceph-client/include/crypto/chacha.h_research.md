# sources/distributed-fs/ceph-client/include/crypto/chacha.h

Purpose: common ChaCha/XChaCha stream cipher constants, state setup, block, HChaCha, and encryption helpers.

Important APIs/types/functions: IV/key/block size macros, `struct chacha_state`, `chacha_block_generic`, `chacha20_block`, `hchacha_block_generic`, `hchacha_block`, constants enum, `chacha_init_consts`, `chacha_init`, `chacha_crypt`, `chacha20_crypt`, and `chacha_zeroize_state`.

Control flow: initialize constants/key/counter/nonce into state, generate blocks with a selected round count, XOR keystream with input in `chacha_crypt`, and zeroize state when done.

State and persistence: `chacha_state` stores the mutable 16-word state including counter and nonce; encryption advances counter in implementation.

Dependencies and integration points: used by ChaCha20, XChaCha, and ChaCha20-Poly1305 code; depends on unaligned little-endian access and string zeroization.

Risks: nonce/counter reuse with the same key is catastrophic. Round-count variants must be chosen intentionally. State contains key material and should be zeroized.

Test signals: RFC7539 ChaCha20 vectors, XChaCha/HChaCha vectors, split encryption tests, counter rollover tests, and zeroization checks.
