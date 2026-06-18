<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h

Purpose: public JR backend API for CAAM clients that submit descriptors directly to job rings.

Important APIs and control flow: declares `caam_jr_alloc()` to obtain a least-used JR device, `caam_jr_free()` to release the reference, and `caam_jr_enqueue()` to submit a DMA-mappable job descriptor with completion callback and caller context.

State and persistence behavior: no state in the header. The implementation increments/decrements per-JR `tfm_count` and uses the JR software/hardware rings in `jr.c`.

Dependencies and integration points: included by RNG, PRNG, key generation, and algorithm modules. It is the boundary between descriptor construction code and the hardware ring transport.

Risks and test signals: risks are callers forgetting `caam_jr_free()`, assuming `caam_jr_enqueue()` returns zero rather than `-EINPROGRESS` on success, and descriptors/data not being DMA-safe. Test signals are balanced alloc/free counts, correct callback invocation with original descriptor/context, and error handling for no JR, full ring, or descriptor DMA mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h -->
