# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.c

Purpose: this file implements allocation, initialization, cleanup, and free operations for vNIC completion queues used by SNIC.

Important APIs, types, and functions: `svnic_cq_alloc()` binds a `vnic_cq` to an MMIO CQ control resource and allocates a coherent descriptor ring. `svnic_cq_init()` programs ring base, size, color, head/tail, interrupt enable, CQ entry enable, interrupt offset, and optional message address. `svnic_cq_clean()` resets software consumer state, hardware head/tail/color, and clears descriptors. `svnic_cq_free()` frees the descriptor ring and clears the control pointer.

Control flow: probe resource allocation calls `svnic_cq_alloc()` for WQ ACK CQs and firmware CQs, then `svnic_cq_init()`. Cleanup and remove call `svnic_cq_clean()` and `svnic_cq_free()`.

State and persistence: runtime state includes `vnic_cq.index`, `vdev`, MMIO `ctrl`, DMA ring, `to_clean`, and `last_color`. No persistent state exists.

Dependencies and integration: depends on vNIC resource discovery for CQ controls, coherent DMA ring helpers from `vnic_dev.c`, and service loops in `vnic_cq.h`/`vnic_cq_fw.h`.

Risks: register programming order and color initialization must match hardware expectations. `writeq()` is provided by `vnic_dev.h` if the architecture lacks it. Cleanup clears descriptors while hardware should already be disabled or quiesced.

Test signals: allocate/init/free under fault injection, CQ wraparound, interrupt offset validation, and cleanup after active completions.
