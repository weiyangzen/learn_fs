# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c

### Purpose
`dpaa2-qdma.c` implements the DMAengine driver for NXP Layerscape DPAA2 QDMA, using DPDMAI objects on the Freescale Management Complex bus and DPIO queue notifications. It primarily exposes DMA memcpy capability through DPAA2 frame descriptors, frame lists, and source/destination descriptors.

### Important APIs, Types, And Functions
Key DMAengine operations are `dpaa2_qdma_alloc_chan_resources()`, `dpaa2_qdma_free_chan_resources()`, `dpaa2_qdma_prep_memcpy()`, and `dpaa2_qdma_issue_pending()`. Descriptor helpers include `dpaa2_qdma_request_desc()`, `dpaa2_qdma_populate_fd()`, `dpaa2_qdma_populate_first_framel()`, `dpaa2_qdma_populate_frames()`, `dpaa2_qdma_free_desc()`, and `dpaa2_dpdmai_free_comp()`. Device setup and teardown are handled by `dpaa2_qdma_probe()`, `dpaa2_qdma_setup()`, `dpaa2_qdma_dpio_setup()`, `dpaa2_dpdmai_bind()`, `dpaa2_qdma_fqdan_cb()`, `dpaa2_qdma_remove()`, and `dpaa2_qdma_shutdown()`.

### Control Flow, State, And Persistence
Probe allocates private state, detects whether an IOMMU domain is present to decide BMT handling, allocates an MC portal, opens and validates the DPDMAI object, fetches RX/TX FQIDs, registers DPIO notification contexts and stores, binds RX queues to DPIO destinations, enables the DPDMAI, creates eight virtual DMA channels, and registers the DMAengine device. Per channel resource allocation creates DMA pools for frame descriptors, frame lists, and source/destination descriptors. A memcpy prepare path allocates or reuses a completion object, fills a frame descriptor pointing at a three-entry frame list, and returns a virtual DMA descriptor. Issue-pending removes the next virtual descriptor, places it on `comp_used`, and enqueues the frame descriptor to the TX FQID. FQDAN callbacks pull response frames, match completions by frame-list address, complete cookies, and rearm notifications.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on `virt-dma`, DPDMAI MC commands, DPIO enqueue/pull/rearm services, DPAA2 frame descriptor helpers, DMA pools, IOMMU domain detection, and SoC matching for the LX2160 write-transaction workaround. Integration points include the MC bus object type `"dpdmai"`, DPIO notification routing, DMAengine clients, and shutdown-time DPDMAI destroy. Risks include global `smmu_disable` shared across devices, completion matching by descriptor address, queue-lock and vchan-lock ordering, missing cleanup of in-flight hardware work during remove, version checks that reject newer minor revisions, and error enqueue paths that silently recycle descriptors without completing cookies. Test signals include MC probe deferral, DPDMAI version mismatch handling, IOMMU and no-IOMMU operation, memcpy completion callbacks, queue errors in FD status, descriptor reuse, remove/shutdown paths, and LX2160 coherent-write fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpaa2-qdma.c -->
