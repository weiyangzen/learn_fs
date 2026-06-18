# sources/distributed-fs/ceph-client/include/crypto/internal/skcipher.h

Purpose: defines private skcipher/lskcipher registration, template, spawn, request-context, fallback, and scatterwalk helpers for symmetric-key ciphers.

Important APIs, types, and flow: instance structs overlay crypto instances with `skcipher_alg` or `lskcipher_alg`; spawn structs bind templates to inner algorithms. `struct skcipher_walk` tracks SG or virtual source/destination traversal, IV handling, remaining byte counts, temporary pages/buffers, block size, stride, and alignment. APIs register algorithms and instances, grab/drop/spawn children, set request size including DMA padding, initialize/advance skcipher walks for normal and AEAD-backed operations, abort walks, expose contexts, test algorithm self-test status, and allocate simple cipher-mode instances around block ciphers or lskciphers.

State and persistence: state lives in transform contexts, request contexts, walk buffers, and template instance contexts. Exportable cipher mode state is handled by public APIs; no persistent storage exists.

Dependencies and integration: depends on `crypto/algapi.h`, internal single-block cipher helpers, public skcipher API, scatterwalk, AEAD request integration, and templates implementing modes such as CBC/CTR/XTS.

Risks and test signals: high-risk areas include SG traversal, IV/state carry between chunks, alignment buffers, request-size flags, and lskcipher/skcipher interop. Signals include skcipher manager tests, SG fragmentation and unaligned buffers, export/import continuation, AEAD-walk callers, simple-template instance creation, and DMA hardware-driver tests.
