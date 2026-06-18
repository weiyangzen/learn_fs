# sources/distributed-fs/ceph-client/crypto/pcbc.c

Purpose: implements the Propagating Cipher Block Chaining (`pcbc`) skcipher template over simple block ciphers.

Important APIs and functions: `crypto_pcbc_encrypt()`, `crypto_pcbc_decrypt()`, and their segment/in-place helpers perform the mode. `crypto_pcbc_create()` allocates a simple skcipher instance and installs the PCBC encrypt/decrypt callbacks.

Control flow: instance creation delegates most child setup to `skcipher_alloc_instance_simple()`. Encryption walks the request virtually. For each block, encryption xors plaintext into IV, encrypts to ciphertext, then sets the next IV to plaintext xor ciphertext. The in-place path saves plaintext in a stack buffer before overwriting. Decryption decrypts the ciphertext block, xors IV to produce plaintext, then sets the next IV to plaintext xor ciphertext.

State and persistence: mode state is request-local in the walk IV. The child cipher is stored by the simple skcipher instance infrastructure. No state persists outside tfm/request lifetimes.

Dependencies and integration points: depends on internal cipher and skcipher helpers, `crypto_xor()`, `crypto_xor_cpy()`, and the crypto template registry. It imports `CRYPTO_INTERNAL` because it uses simple cipher internals.

Risks: PCBC is an old mode with limited modern use and should not be selected for new protocols without a compatibility requirement. The stack temporary uses `MAX_CIPHER_BLOCKSIZE`, so child block sizes must fit crypto API expectations. In-place handling is separate and must preserve the original ciphertext/plaintext for IV propagation.

Test signals: encrypt/decrypt round trips for in-place and separate buffers, multi-SG walks, non-block-multiple rejection by skcipher walk, IV update behavior, and template lookup `pcbc(cipher)`.
