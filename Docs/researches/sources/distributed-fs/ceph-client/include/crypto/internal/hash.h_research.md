# sources/distributed-fs/ceph-client/include/crypto/internal/hash.h

Purpose: defines private async and synchronous hash registration, template, spawn, walk, fallback, keying, export/import, and context helpers.

Important APIs, types, and flow: algorithm flags describe block-only behavior, nonzero final requirements, multi-block finup support, and core-export support. `struct crypto_hash_walk` tracks SG traversal for ahash operations. `ahash_instance` and `shash_instance` overlay crypto instances with hash algorithms; spawn helpers bind templates to inner ahash or shash algorithms. Registration APIs publish ahash/shash algorithms and instances. Helpers detect whether algorithms have or need keys, bridge shash operations through ahash request wrappers, set statesize/reqsize including DMA padding, allocate fallback stack requests (`HASH_FBREQ_ON_STACK`), enqueue/dequeue requests, expose transform/request contexts, and export/import core state without partial-block buffers.

State and persistence: state is per transform, per request/descriptor, queued request, or exported caller buffer. Hash state can be serialized through export/import for runtime continuation, but there is no filesystem persistence.

Dependencies and integration: depends on public hash API, crypto queue/spawn/template infrastructure, scatterlists, fallback transforms, and crypto self-tests. Hash algorithms, HMAC/KDF code, and templates use these contracts.

Risks and test signals: state-size math, partial-block removal in core export, keyed-hash enforcement, fallback flag propagation, and DMA alignment are subtle. Signals include ahash/shash self-tests, HMAC with missing keys, export/import continuation tests, SG and virtual request paths, fallback-stack request tests, and template unload/reload.
