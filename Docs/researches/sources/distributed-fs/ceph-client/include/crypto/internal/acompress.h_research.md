# sources/distributed-fs/ceph-client/include/crypto/internal/acompress.h

Purpose: defines the internal asynchronous compression algorithm contract and helper machinery for compression transforms that may operate on scatterlists, virtual buffers, or per-CPU synchronous fallback streams.

Important APIs, types, and flow: `struct acomp_alg` supplies `compress`, `decompress`, optional transform `init`/`exit`, and common compression algorithm metadata shared with synchronous compression. `struct crypto_acomp_streams` owns per-CPU stream contexts, allocation/free callbacks, a work item, and a CPU mask of requested streams. `struct acomp_walk` abstracts either virtual source/destination pointers or scatter walks. Request helpers expose transform/request contexts, detect request buffer modes (`*_isvirt`, `*_isnondma`, `*_issg`), allocate/free streams, lock per-CPU streams with BH-disabled spinlocks, walk virtual buffers, and initialize fallback requests on stack with `ACOMP_FBREQ_ON_STACK`.

State and persistence: state is transform-local context plus per-CPU compression stream contexts guarded by spinlocks. Walk state is transient per request; no persistent storage is used.

Dependencies and integration: includes public `crypto/acompress.h`, `crypto/algapi.h`, scatterwalk helpers, workqueues, cpumasks, and synchronous compression fallback definitions. Registration functions (`crypto_register_acomp*`) attach implementations to the crypto API registry.

Risks and test signals: risks include mixing virtual/scatterlist/NON-DMA flags incorrectly, per-CPU stream locking bugs in softirq context, fallback request flag loss, and destination-length accounting. Signals include acomp self-tests across SG and virtual buffers, compression/decompression with small and oversized outputs, CPU hotplug or preemption-heavy runs, and fallback path coverage.
