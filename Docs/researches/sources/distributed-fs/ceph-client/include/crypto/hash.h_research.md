# sources/distributed-fs/ceph-client/include/crypto/hash.h

Purpose: kernel crypto API definitions for asynchronous hash (`ahash`) and synchronous hash (`shash`) algorithms and requests.

Important APIs/types/functions: `CRYPTO_AHASH_REQ_VIRT`, `struct hash_alg_common`, `struct ahash_request`, `struct ahash_alg`, `struct shash_desc`, `struct shash_alg`, `struct crypto_ahash`, `struct crypto_shash`, stack/clone allocation macros, allocation/free/clone/has helpers, digest/block/state/request size getters, flag helpers, setkey/init/update/final/finup/digest/export/import functions, request setters for SG and virtual buffers, and shash descriptor helpers.

Control flow: ahash callers allocate a tfm and request, set callback and data buffers, then call init/update/final/finup/digest or export/import state. shash callers allocate a tfm, provide a descriptor, and call init/update/final or one-shot digest. Some inline final/update helpers reduce to `finup` with zero data or null output.

State and persistence: tfms store algorithm context; requests/descriptors store transient operation state plus implementation-private context. Export/import APIs persist intermediate hash state in caller buffers. Sensitive request/descriptor memory is zeroized by free/zero helpers.

Dependencies and integration points: foundational for all kernel hash/HMAC/KDF users, DRBG, signatures, integrity, and crypto engine wrappers. Depends on scatterlists, slab, string, and core crypto APIs.

Risks: request flags include private virtual-buffer bits that callback setters must preserve. Stack request macros require conservative maximum sizes. Export/import state sizes must match algorithm state. Callers must allocate digest buffers of the advertised digest size.

Test signals: ahash and shash crypto manager vectors, SG and virtual-buffer request tests, keyed hash setkey tests, export/import resume tests, async callback/backlog tests, stack request coverage, and zeroization checks.
