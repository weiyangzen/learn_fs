# sources/distributed-fs/ceph-client/crypto/rsa-pkcs1pad.c

Purpose: implements the `pkcs1pad(rsa)` akcipher template for RSAES-PKCS1-v1_5 style public-key encryption padding and unpadding.

Important APIs, types, and functions: `struct pkcs1pad_ctx` stores the child RSA tfm and key size. `struct pkcs1pad_request` stores temporary SGs, buffers, and child request. Key setup functions call `rsa_set_key()`. Main paths are `pkcs1pad_encrypt()`, `pkcs1pad_encrypt_complete()`, `pkcs1pad_decrypt()`, and `pkcs1pad_decrypt_complete()`.

Control flow: instance creation accepts only a child whose base name is `rsa`, then registers `pkcs1pad(rsa-driver)`. Encryption checks key size, maximum source length `key_size - 11`, and destination size. It builds an encoded block beginning with `0x02`, random nonzero padding bytes, a zero separator, and plaintext, then invokes child RSA encrypt. Completion left-pads the child result to the full modulus size if needed. Decryption requires ciphertext length equal to key size, runs child RSA decrypt into a temporary buffer, checks the `0x00 0x02 PS 0x00` structure and minimum padding length, then copies plaintext to the caller buffer or reports needed size.

State and persistence: child tfm and key size persist per transform. Per-request buffers are allocated and freed, with decrypted buffers wiped via `kfree_sensitive()`.

Dependencies and integration points: depends on akcipher internals, RSA helpers, scatterlists, and random nonzero padding. Registered by `rsa.c` through `rsa_pkcs1pad_tmpl`.

Risks: PKCS#1 v1.5 encryption padding has known oracle risks if error behavior is exposed to attackers. The unpadding path branches on malformed structure and is not a full side-channel hardened protocol defense. Random padding must be nonzero. Asynchronous cleanup must free temp buffers exactly once.

Test signals: RSA encryption/decryption vectors, too-long plaintext, short destination `-EOVERFLOW`, malformed padding rejection, async child completion, leading-zero modulus output normalization, and template name validation.
