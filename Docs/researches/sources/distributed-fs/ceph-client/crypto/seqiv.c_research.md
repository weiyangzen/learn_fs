# sources/distributed-fs/ceph-client/crypto/seqiv.c

Purpose: implements the `seqiv` AEAD IV generator template, which derives an 8-byte IV from a sequence number xor a salt and stores that IV in the message.

Important APIs and functions: `seqiv_aead_encrypt()`, `seqiv_aead_decrypt()`, completion helpers, and `seqiv_aead_create()` implement the template. It uses `struct aead_geniv_ctx` from geniv infrastructure and child AEAD requests stored in request context.

Control flow: creation uses `aead_geniv_alloc()` and accepts only children with `ivsize == sizeof(u64)`. Encryption requires at least 8 bytes of cryptlen, copies source to destination for out-of-place requests, handles unaligned IV memory by duplicating it, xors the caller-provided sequence value with the salt, writes the resulting IV into the destination after associated data, and invokes the child AEAD with associated data length increased by 8. Decryption extracts the stored IV from source, increases associated data length by 8, and calls the child.

State and persistence: salt and child tfm persist in the geniv tfm context. Per-request duplicated IV memory is freed in completion and copied back to `req->iv` after successful async encryption.

Dependencies and integration points: depends on `crypto/internal/geniv.h`, AEAD API, `memcpy_sglist()`, and `scatterwalk_map_and_copy()`. Useful for CTR-like AEAD constructions needing sequence-derived nonces.

Risks: nonce uniqueness depends on callers supplying non-repeating sequence values and appropriate salt. The implementation hardcodes an 8-byte IV. Unaligned IV handling changes completion callback/data and must preserve caller completion semantics.

Test signals: AEAD encrypt/decrypt with in-place and out-of-place SGs, unaligned `req->iv`, too-short cryptlen failures, async child completion, IV copyback, and salt xor correctness.
