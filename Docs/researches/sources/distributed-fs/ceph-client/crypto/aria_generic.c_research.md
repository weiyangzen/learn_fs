# sources/distributed-fs/ceph-client/crypto/aria_generic.c

Purpose: implements the generic ARIA block cipher provider for the Linux Crypto API, including key schedule generation, encryption, decryption, and exported helper functions used by architecture-specific or mode wrappers.

Important APIs/types/functions: `key_rc` contains ARIA round constants. `aria_set_encrypt_key()` derives encryption round keys from 128, 192, or 256 bit keys using ARIA substitution/diffusion helpers from `crypto/aria.h`. `aria_set_decrypt_key()` derives inverse round keys. `aria_set_key()` validates key length, initializes `struct aria_ctx`, and exports the setkey helper. `__aria_crypt()` is the common round function. `aria_encrypt()` and `aria_decrypt()` are exported raw helpers; `__aria_encrypt()` and `__aria_decrypt()` are Crypto API callbacks.

Control flow: module load registers `aria_alg`. Setkey computes rounds as `(key_len + 32) / 4`, fills `enc_key`, then builds `dec_key`. Encryption/decryption load four big-endian words, apply alternating odd/even subst-diff rounds, perform the final S-box/key transformation, and store big-endian output.

State and persistence: state is per-transform `struct aria_ctx`, including key length, round count, and round-key arrays. Constants and S-boxes are read-only. No persistence exists outside transform lifetime.

Dependencies and integration points: depends on `crypto/aria.h` for ARIA primitive helpers, S-boxes, context layout, and constants. Registers `"aria"` and `"aria-generic"` as a classic cipher algorithm.

Risks: key schedule layout is guarded by `BUILD_BUG_ON()` size checks, but any context-layout change must remain synchronized with callers and assembly alternatives. Table lookups may have side-channel implications. Wrong accepted key sizes or round counts would silently break standards compliance.

Test signals: RFC 5794 known-answer vectors for 128/192/256 bit keys, exported helper use from accelerated implementations, invalid key length rejection, module alias lookup, and encrypt/decrypt inverse tests.
