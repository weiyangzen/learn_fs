# sources/distributed-fs/ceph-client/crypto/ahash.c

Purpose: implements the asynchronous hash (`ahash`) front end, including scatterlist hash walking, shash-backed ahash transforms, key handling, block-only buffering, virtual-buffer fallback, export/import, transform cloning, registration, and one-shot digest helpers.

Important APIs, types, and functions: exported APIs include `crypto_hash_walk_first()`, `crypto_hash_walk_done()`, `shash_ahash_update()`, `shash_ahash_finup()`, `shash_ahash_digest()`, `crypto_ahash_setkey()`, `crypto_ahash_init()`, `crypto_ahash_update()`, `crypto_ahash_finup()`, `crypto_ahash_digest()`, export/import variants, `crypto_alloc_ahash()`, `crypto_clone_ahash()`, registration helpers, `ahash_request_free()`, and `crypto_hash_digest()`.

Control flow and behavior: transforms can either wrap a shash algorithm or use a native ahash algorithm. Native ahash requests reject queued async stack requests, enforce `NEED_KEY`, and may route virtual-buffer requests through a fallback transform using exported/imported state. Block-only algorithms buffer trailing partial blocks in request context and adjust SG chains before update/finup. Default `finup` composes update plus final through saved callbacks.

State and persistence: transform state records `using_shash`, reqsize, statesize, optional fallback tfm, and key-needed flags. Request context stores shash descriptors, block-only tail buffers, saved callbacks/data, and temporary chained SG entries. Export/import serializes algorithm state for cloning, continuation, and fallback transitions.

Dependencies and integration points: depends on scatterwalk, shash front end, hash common helpers, generic crypto registry, proc/netlink reporting, and consumers such as HMAC, AF_ALG hash, IPsec, fs integrity, and signature code. It shares fallback and spawn infrastructure with `algapi.c`.

Risks and correctness concerns: block-only buffering changes `req->src` and `req->nbytes` and must restore them even across async completion. Fallback requires state sizes bounded by `HASH_MAX_STATESIZE` and algorithms with export_core support. Clone behavior differs for keyed and unkeyed algorithms. Import validation must reject corrupt buffered-length values.

Test signals: shash-backed and native ahash vectors, update/finup/digest equivalence, virtual-buffer fallback, block-only algorithms with all tail lengths, export/import/clone continuation, keyed hash `-ENOKEY`, async completion ordering, stack request rejection, and AF_ALG hash accept-state cloning.
