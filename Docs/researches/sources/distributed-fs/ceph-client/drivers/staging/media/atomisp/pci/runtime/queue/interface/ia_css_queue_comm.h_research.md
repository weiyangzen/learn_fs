# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue_comm.h

Purpose: common queue constants and remote descriptor ABI.

Important definitions: queue locations (`HOST`, `SP`, `ISP`), queue types (`LOCAL`, `REMOTE`), `IA_CSS_MIN_ELEM_COUNT`, `IA_CSS_DMA_XFER_MASK`, and `ia_css_queue_remote_t` with descriptor/element addresses, location, and processor id.

Control flow/state: no logic. The remote descriptor tells queue operations where and how to access circular-buffer metadata/items.

Dependencies/integration: uses circular-buffer types and is consumed by queue init/access, event queues, and SP/host shared queues.

Risks: location/type constants are macros rather than enums for compactness, so invalid values can reach runtime. Minimum element count reflects DMA alignment and must match SP-side queue layout.

Test signals: ABI layout compatibility, remote init for each supported location, ISP location returning unsupported in access layer, and alignment assumptions for DDR queues.
