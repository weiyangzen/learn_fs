# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma_txreq.h

## Purpose
`sdma_txreq.h` defines the transport-neutral packet request container used by HFI1 SDMA producers. It provides the canonical fragment descriptor, request status codes, request flags, callback type, and `struct sdma_txreq` layout that verbs, user SDMA, IPOIB, and other callers embed at the start of their own request structures.

## Important APIs, Types, and Functions
- `NUM_DESC` sets the built-in descriptor capacity to 6, increased for AHG needs.
- `struct sdma_desc` stores two descriptor quadwords plus optional pinning context and a non-sleeping context release callback.
- Status constants `SDMA_TXREQ_S_OK`, `SDMA_TXREQ_S_SENDERROR`, `SDMA_TXREQ_S_ABORTED`, and `SDMA_TXREQ_S_SHUTDOWN` are passed to completion callbacks.
- Flags `SDMA_TXREQ_F_URGENT`, `SDMA_TXREQ_F_AHG_COPY`, `SDMA_TXREQ_F_USE_AHG`, and `SDMA_TXREQ_F_VIP` influence interrupt/head update behavior, AHG mode, and priority handling.
- `callback_t` is the completion callback signature.
- `struct sdma_txreq` tracks list linkage, descriptor storage, optional coalesce buffer, iowait owner, callback, packet and remaining length, descriptor counts/limits, next ring index, coalesce index, flags, and built-in descriptors.
- `sdma_txreq_built()` returns whether any descriptors have been built.

## Control Flow
Callers allocate a larger request object with `struct sdma_txreq` first, initialize it via helpers in `sdma.h`, add descriptors until `num_desc` is nonzero and `tlen` reaches zero, then submit it through `sdma.c`. During progress or abort, SDMA cleanup walks the descriptors, unmaps DMA mappings according to encoded mapping type, calls any pinning context release callback, frees coalesce/extended descriptor allocations, invokes the completion callback with one of the status values, and updates iowait state.

## State and Persistence Behavior
`struct sdma_txreq` is transient per-packet state. It can be queued on wait lists, flush lists, or the active tx ring. The descriptor pointer initially references the embedded `descs[]` array but may be replaced by an allocated larger array. `coalesce_buf` is allocated only for excessive fragment counts. `next_descq_idx` is set when submitted so progress can identify when the hardware head has passed the request. Nothing in this header is durable across request completion.

## Dependencies and Integration Points
The header depends on Linux list types and is included by `sdma.h`, which supplies initialization and descriptor manipulation helpers. Producers in verbs, user SDMA, IPOIB, and pinning code embed this type and attach subsystem-specific metadata after it. `sdma.c` is the primary consumer of private fields even though comments discourage direct external use.

## Risks and Edge Cases
The request structure is intentionally shared across multiple producers, so layout assumptions matter: the SDMA txreq must be first in enclosing structures when code casts between generic and producer-specific request types. Completion callbacks can run in interrupt, tasklet, or worker context and must not sleep. Pinning context release callbacks may also run in interrupt context. Mismanaging `tlen`, `num_desc`, or `desc_limit` can result in incomplete submission, descriptor overflow, or cleanup leaks. Flags must align with descriptor encoding logic in `sdma.h` and `sdma.c`.

## Test Signals
Tests should confirm callbacks receive correct status on success, abort, shutdown, and send error; descriptor extension preserves embedded descriptors; pinning context get/put balance is correct; `sdma_txreq_built()` distinguishes initialized-but-empty from built requests; and all producers can embed the struct without layout regressions.
