# sources/distributed-fs/ceph-client/include/crypto/skcipher.h

Purpose: exposes the public symmetric-key cipher API for asynchronous skcipher, synchronous skcipher, and lightweight lskcipher algorithms.

Important APIs, types, and flow: flags describe continuation/final state. `struct skcipher_request` carries cryptlen, IV, source/destination SGs, base request, and private context. `struct skcipher_alg_common`, `skcipher_alg`, and `lskcipher_alg` describe algorithm metadata and operations including setkey, encrypt/decrypt, export/import, and state size. Helpers allocate/free transforms, query names, IV/block/chunk/state/alignment/key sizes, set flags and keys, execute encrypt/decrypt, export/import mode state, perform lskcipher linear-buffer operations, allocate/free/zero requests, set callbacks, and set crypt buffers.

State and persistence: transform contexts store keys and mode state; request contexts and IV buffers are caller-owned. Export/import serializes runtime continuation state to caller buffers but no filesystem persistence exists.

Dependencies and integration: central to block/stream mode crypto, AF_ALG, dm-crypt/fs encryption users, and hardware drivers. Internal helpers in `internal/skcipher.h` implement registration and SG walking.

Risks and test signals: risks include IV reuse, request/transform mismatch, SG length errors, sync vs async allocation misuse, export/import state truncation, and lskcipher continuation flag errors. Signals include crypto manager skcipher tests, SG fragmentation, in-place/out-of-place operations, export/import continuation, zero-length and non-block-multiple handling per mode, and hardware async completion tests.
