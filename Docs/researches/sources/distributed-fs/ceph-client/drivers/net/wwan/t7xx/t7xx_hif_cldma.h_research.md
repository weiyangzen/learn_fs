# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_cldma.h

Purpose: declares high-level CLDMA HIF structures and APIs used by t7xx modem control and port layers.

Important APIs/types: `enum cldma_id` distinguishes MD and AP CLDMA instances. `struct cldma_gpd` defines the DMA descriptor layout with flags, allowed/data lengths, next pointer, and data pointer. `struct cldma_request` binds one GPD, DMA address, SKB, mapped buffer, and list node. `struct cldma_ring` owns request lists and packet size. `struct cldma_queue` tracks queue direction, ring pointers, budget, locks, workqueue, waitqueue, and RX callback. `struct cldma_ctrl` owns all queues, rings, active bitmaps, DMA pool, PM entity, and hardware info.

Control flow and state: public functions allocate/init/exit CLDMA, switch queue configuration, start/stop/reset, send SKBs, and clear queues. Queue state is shared between HIF workers, interrupt handlers, PM callbacks, and port proxy users.

Dependencies and integration points: includes low-level CLDMA definitions, PCI device types, DMA pool, SKBs, workqueues, and t7xx PCI state. It is consumed by modem ops and port proxy layers.

Risks and test signals: descriptor layout and queue pointer invariants are critical. Tests should cover both CLDMA instances, all queues, shared/dedicated configs, TX send API return codes, reset cleanup, and build compatibility across PM/debug configs.
