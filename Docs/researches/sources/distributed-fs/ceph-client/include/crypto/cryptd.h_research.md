# sources/distributed-fs/ceph-client/include/crypto/cryptd.h

Purpose: software async crypto daemon wrapper interface for AEAD algorithms.

Important APIs/types/functions: `struct cryptd_aead`, `__cryptd_aead_cast`, `cryptd_alloc_aead`, `cryptd_aead_child`, `cryptd_aead_queued`, and `cryptd_free_aead`.

Control flow: callers allocate a cryptd AEAD wrapper for a child algorithm, submit through normal AEAD APIs, query whether work is queued without CPU migration, and free wrapper state.

State and persistence: wrapper embeds `crypto_aead` base and maintains child/queue state in implementation.

Dependencies and integration points: depends on AEAD API; integrates with cryptd worker threads to provide asynchronous behavior for synchronous algorithms.

Risks: `cryptd_aead_queued()` requires CPU stability, so callers must disable migration or otherwise satisfy that condition. Child lifetime must track wrapper lifetime.

Test signals: async completion tests, child algorithm passthrough vectors, CPU migration/queue tests, and wrapper free under pending work checks.
