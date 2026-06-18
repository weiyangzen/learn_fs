<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h

Purpose: public interface for the legacy CAAM/QI backend used by QI-aware CAAM crypto algorithms.

Important APIs and control flow: defines `CAAM_QI_MEMCACHE_SIZE`, exported `caam_congested`, callback type `caam_qi_cbk`, operation enum, opaque request/context relationship, `struct caam_drv_ctx` holding preheader/shared descriptor, request/response FQs, refcount, CPU, operation type, and device, and `struct caam_drv_req` holding a two-entry QMan S/G table, context, callback, and app context. Prototypes expose context init/update/release, enqueue, busy check, backend init, and QI cache allocation/free.

State and persistence behavior: no header state, but it describes the state allocated by `qi.c`. Request structures are caller-owned and must remain valid until callback; contexts persist for a crypto transform/session.

Dependencies and integration points: depends on QMan types, crypto alignment, CAAM descriptor constants, and descriptor construction helpers. Used by `caamalg_qi` style algorithms to submit frame-based CAAM work.

Risks and test signals: risks include callers mis-sizing/initializing `fd_sgt`, using requests after completion, failing to release contexts, mismatch between comment saying 256B and actual `CAAM_QI_MEMCACHE_SIZE` 768, and relying on global congestion for backpressure. Test signals include enqueue/completion callbacks with correct app context, context update preserving in-flight requests, cache allocation alignment, and busy/backpressure behavior under congestion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h -->
