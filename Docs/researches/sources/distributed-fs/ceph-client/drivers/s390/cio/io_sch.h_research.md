# sources/distributed-fs/ceph-client/drivers/s390/cio/io_sch.h

Purpose: defines private data structures for I/O subchannels, internal CCW requests, sense-id buffers, and CCW-device private state.

Important APIs/types/functions: `struct io_subchannel_private` stores the active ORB, child CCW device pointer, channel-program options, and subchannel DMA area. `struct ccw_request` is the reusable internal request descriptor with timeout/retry/path/check/filter/callback fields. `struct senseid`, `struct ccw_device_dma_area`, and `struct ccw_device_private` define the shared memory/state layout used by device FSM, ID, PGID, status, QDIO, CMF, and todo code. Inline helpers get/set subchannel private data and child device.

Control flow: no executable flow beyond inline accessors, but the structures determine how internal requests are started and completed, how SENSE ID/PGID/IRB data is shared, and how state flags drive the FSM.

State and persistence behavior: all state is in memory and either tied to subchannel device data or a CCW device. DMA areas hold architecture-visible channel-program data below the required addressing limits.

Dependencies and integration points: includes CSS, ORB, CCW device UAPI, IRQ class definitions, and is a central private contract for `device_fsm.c`, `device_id.c`, `device_pgid.c`, `device_status.c`, `device_ops.c`, QDIO, and I/O subchannel code.

Risks and test signals: bitfield packing, DMA alignment, and flag semantics are ABI-sensitive within the driver. Tests should indirectly validate every state flag transition, internal request cancellation/retry, fake IRB delivery, QDIO data ownership, DMA pool lifetime, and subchannel private-data lifetime.
