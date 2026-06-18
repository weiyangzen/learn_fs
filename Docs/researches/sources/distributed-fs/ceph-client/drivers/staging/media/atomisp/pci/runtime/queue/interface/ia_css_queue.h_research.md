# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/queue/interface/ia_css_queue.h

Purpose: public queue abstraction for local host queues and remote queues in host/SP/ISP memory.

Important types/APIs: `ia_css_queue_local`, opaque `ia_css_queue_t`, init for local/remote queues, uninit, enqueue/dequeue, empty/full checks, used/free space, peek, and size query.

Control flow/state: local queues wrap host circular-buffer descriptors/elements. Remote queues store location/proc/address metadata and use `queue_access` to load/store descriptors and items during each operation.

Dependencies/integration: `ia_css_queue_comm.h`, `queue_access.h`, platform/type support, and circular-buffer helpers. Eventq and buffer queues rely on this API.

Risks: remote operations are not atomic across descriptor load, item access, and descriptor store; external synchronization or single-producer/single-consumer assumptions matter. The header exposes implementation internals by including `../src/queue_access.h`.

Test signals: local queue wraparound, remote SP/HOST queue enqueue/dequeue, full/empty errors, peek boundary, and size/free/used consistency.
