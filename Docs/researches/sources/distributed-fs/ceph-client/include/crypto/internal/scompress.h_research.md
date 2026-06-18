# sources/distributed-fs/ceph-client/include/crypto/internal/scompress.h

Purpose: defines the internal synchronous compression API and its shared relationship with asynchronous compression.

Important APIs, types, and flow: `struct crypto_scomp` wraps a crypto transform; `struct scomp_alg` supplies synchronous `compress`/`decompress` callbacks that operate on linear buffers and optional stream context, owns `crypto_acomp_streams`, and shares common compression metadata. Helpers cast transforms/algorithms, free transforms, call algorithm callbacks, and register/unregister one or multiple synchronous compression algorithms.

State and persistence: state is per transform plus per-CPU stream contexts. No persistence exists.

Dependencies and integration: includes internal acomp definitions and the generic crypto transform API. Synchronous compression algorithms can be exposed as async wrappers through shared stream support.

Risks and test signals: destination length is caller-provided and updated by algorithms, so bounds handling is central. Signals include scomp known-answer compression/decompression tests, stream allocation failure tests, concurrent per-CPU use, and async fallback integration tests.
