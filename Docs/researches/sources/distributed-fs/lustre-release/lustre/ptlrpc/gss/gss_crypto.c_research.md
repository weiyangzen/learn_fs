# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.c

Purpose: provides common crypto and parsing helpers for GSS mechanisms, including keyblock transform setup, serialized field extraction, scatterlist construction, hashing over mixed message/page data, padding, and raw-object encryption.

Important APIs/types/functions: `gss_keyblock_init/free/dup()` manage `rawobj_t` keys and `crypto_sync_skcipher` transforms. `gss_get_bytes()`, `gss_get_rawobj()`, and `gss_get_keyblock()` parse user-space serialized contexts. `gss_setup_sgtable()` maps kmalloc or vmalloc buffers into a scatter-gather table; `gss_teardown_sgtable()` frees multi-entry tables. `gss_crypt_generic()` encrypts/decrypts a contiguous buffer in place. `gss_digest_hash()` and `gss_digest_hash_compat()` update an ahash over raw objects, bio_vec pages, and optional headers. `gss_add_padding()` PKCS-style pads with byte value equal to padding length. `gss_crypt_rawobjs()` encrypts/decrypts a sequence of raw objects into one output object.

Control flow: mechanisms import keys, initialize transforms, build scatterlists for either direct buffers or pages, then drive synchronous kernel crypto requests. Hash helpers process message rawobjs first, then bulk vectors, then headers; the compat variant hashes only header length for the optional header.

State/persistence: keyblocks own allocated key bytes and optional crypto transforms. Parsing helpers allocate raw object buffers. No persistent state.

Dependencies/integration: uses Linux crypto skcipher/ahash APIs, Lustre OBD allocation macros, `bio_vec`, vmalloc/page helpers, and LNet crypto wrappers.

Risks/test signals: transform setkey failure leaves allocated transforms unless callers free; buffer length must match block size; sgtable setup must handle vmalloc buffers and zero lengths correctly. Tests should cover malformed serialized lengths and overflow checks, empty raw objects, vmalloc and kmalloc hashing, block-aligned and unaligned encryption inputs, padding bounds, multi-object encryption, and cleanup after crypto errors.
