# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_lib.c

Purpose: allocates and frees NITROX software resources shared by crypto algorithms and hardware queue submission, including command rings and DMA-backed crypto contexts.

Important APIs and control flow: `nitrox_common_sw_init()` creates the context DMA pool, packet input queues, and AQM queues; cleanup reverses this. `nitrox_cmdq_init()` allocates aligned coherent queue memory, initializes locks/lists/work, counters, and indices. Packet input and AQM queue allocation assign CSR doorbell/completion addresses and instruction sizes. `crypto_alloc_context()` allocates a metadata wrapper and DMA pool object, stores DMA addresses in both wrapper and embedded `ctx_hdr`, and returns a context handle; `crypto_free_context()` releases it.

State and persistence: state is coherent command ring memory, `struct nitrox_cmdq` arrays, DMA pool objects, response/backlog lists, and per-context DMA handles. These resources persist for the device lifetime or crypto transform lifetime.

Dependencies and integration points: depends on DMA coherent allocation, DMA pools, NUMA node allocation, `nitrox_req.h` command sizes, `nitrox_csr.h` offsets, and request-manager backlog work.

Risks and test signals: risks include `nitrox_common_sw_init()` continuing to allocate AQM queues even after packet queue allocation failed unless error flow is read carefully, contexts allocated with GFP_KERNEL only, queue memory alignment relying on pointer arithmetic from DMA address alignment, and pending response/backlog lists needing to be empty before cleanup. Test signals include queue DMA alignment, successful HAL ring programming from allocated addresses, context pool allocation/free under crypto self-tests, and cleanup after partial allocation failure.
