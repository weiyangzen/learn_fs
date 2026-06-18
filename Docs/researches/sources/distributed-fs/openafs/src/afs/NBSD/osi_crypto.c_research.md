## sources/distributed-fs/openafs/src/afs/NBSD/osi_crypto.c

Purpose: NetBSD kernel random-byte provider for OpenAFS.

Important API: `osi_readRandom(void *data, afs_size_t len)`.

Control flow: for NetBSD 7.0 and newer (`AFS_NBSD70_ENV`), asserts the requested length is within `CPRNG_MAX_LEN` and calls `cprng_strong(kern_cprng, data, len, 0)`. Older NetBSD builds include random-device private headers and call `rnd_extract_data(data, len, RND_EXTRACT_ANY)`. The function returns 0 unconditionally after filling the buffer.

Dependencies and integration: depends on NetBSD kernel CPRNG or rnd APIs. It integrates with OpenAFS code paths needing random material, such as identifiers, crypto-adjacent tokens, or cache/protocol randomness supplied through OSI.

State and persistence: no OpenAFS-owned state. Entropy and generator state are owned by the NetBSD kernel.

Risks: the newer path asserts instead of gracefully splitting requests larger than `CPRNG_MAX_LEN`; callers must respect the maximum. The older `rnd_extract_data` path uses `RND_EXTRACT_ANY`, so randomness quality follows old NetBSD random semantics. Errors are not propagated because neither branch returns failure here.

Test signals: compile on pre-7 and 7+ NetBSD, request boundary tests around `CPRNG_MAX_LEN`, nonzero/random-looking output, and consumers that expect a zero return code.
