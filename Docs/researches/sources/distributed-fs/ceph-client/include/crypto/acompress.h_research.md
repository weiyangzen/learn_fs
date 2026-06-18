# sources/distributed-fs/ceph-client/include/crypto/acompress.h

Purpose: asynchronous compression API front-end for kernel crypto algorithms of type `CRYPTO_ALG_TYPE_ACOMPRESS`.

Important APIs/types/functions: request flags for virtual/DMA/non-DMA buffers, `struct acomp_req_chain`, `struct acomp_req`, `struct crypto_acomp`, `struct comp_alg_common`, `crypto_alloc_acomp`, `crypto_alloc_acomp_node`, `crypto_free_acomp`, `crypto_has_acomp`, request alloc/free/clone/on-stack helpers, source/destination setters for SG, DMA virtual, non-DMA virtual, and folios, plus `crypto_acomp_compress` and `crypto_acomp_decompress`.

Control flow: callers allocate a `crypto_acomp`, allocate or stack-initialize an `acomp_req`, configure callback and source/destination buffers, then dispatch compress/decompress. Setter helpers maintain private request flags so implementations can distinguish SG from virtual and DMA-safe from non-DMA buffers.

State and persistence: tfm state includes algorithm callbacks and request context size. Requests hold transient buffer pointers, lengths, callback data, and private chained SG/folio state. Requests are zeroized on free unless stack-allocated.

Dependencies and integration points: depends on core crypto request APIs, scatterlists, folios, slab, atomics, and allocation hooks. Used by compression users that need async hardware or software fallback support.

Risks: private flags must be preserved when callbacks are set; otherwise buffer interpretation can be corrupted. DMA safety flags must match actual memory. `dlen` is both capacity and produced length, so callers must inspect it after completion.

Test signals: async compression/decompression vectors, SG/virtual/folio buffer coverage, DMA/non-DMA fallback tests, request clone/on-stack tests, and memory zeroization checks.
