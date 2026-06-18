# File Research: sources/cow-pools/bcachefs-tools/include/crypto/chacha.h

Purpose: kernel-style ChaCha20 constants and helper wrappers backed by libsodium.

Key contents:
- Defines ChaCha IV/key/block/state sizes and state word counts.
- Defines ChaCha constant words and `struct chacha_state`.
- `chacha_init_consts()` and `chacha_init()` initialize state from key and IV.
- `chacha20_crypt()` calls `crypto_stream_chacha20_xor_ic()` from libsodium.
- `chacha_zeroize_state()` clears state with `memzero_explicit()`.

Important interactions:
- Provides the kernel crypto API shape expected by bcachefs code while using libsodium in tools builds.
- Assumes libsodium call succeeds, enforced with `BUG_ON(ret)`.
