# sources/distributed-fs/ceph-client/include/crypto/chacha20poly1305.h

Purpose: direct ChaCha20-Poly1305 and XChaCha20-Poly1305 AEAD helper declarations.

Important APIs/types/functions: nonce/key/tag length enum, buffer encrypt/decrypt helpers, XChaCha variants, and in-place scatterlist encrypt/decrypt helpers.

Control flow: encrypt writes ciphertext and tag; decrypt authenticates and returns `bool` success before plaintext should be trusted. SG helpers operate in place over scatterlists.

State and persistence: no persistent state in header; keys/nonces are caller-owned and transient.

Dependencies and integration points: depends on scatterlists and is used by direct library AEAD consumers outside the generic AEAD request API.

Risks: nonce uniqueness is mandatory. Decrypt return value is `__must_check`; ignoring it can accept forged plaintext. Source length must account for tag placement expected by implementation.

Test signals: RFC8439 and XChaCha vectors, forged tag rejection, SG in-place vectors, empty AAD/plaintext cases, and nonce-size validation at call sites.
