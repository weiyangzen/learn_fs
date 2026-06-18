# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_io.h

Purpose: this header defines the per-I/O data structures used by the SCSI fast path and error-recovery paths. It describes how Linux SCSI commands are backed by fnic-owned scatter/gather descriptors, DMA addresses, remote-port state, completion waiters, and queue tags.

Important types and constants: `FNIC_DFLT_SG_DESC_CNT` is 32, `FNIC_MAX_SG_DESC_CNT` is 256, and `FNIC_SG_DESC_ALIGN` is 16. `struct host_sg_desc` is the hardware-facing scatter/gather descriptor containing little-endian address and length fields. `struct fnic_dflt_sgl_list` and `struct fnic_sgl_list` are slab/mempool allocation shapes for default and maximum SGL sizes. `enum fnic_sgl_list_type` selects the SGL cache. `enum fnic_ioreq_state` tracks command lifecycle: not initialized, command pending, ABTS pending, ABTS complete, and command complete.

Core structure: `struct fnic_io_req` links a `scsi_cmnd` to driver and firmware state. It records iport/tport pointers, SGL pointer plus original allocation pointer, DMA addresses for SGL and sense buffer, SGL count/type, an `io_completed` bit, remote FC port ID, start time, optional completions for abort and device reset, the blk-mq/fnic tag, and the SCSI command pointer.

Control flow and integration: `fnic_queuecommand()` allocates `fnic_io_req` from a mempool, fills SGL metadata, maps DMA, stores the object in both `fnic_priv(sc)->io_req` and the software copy-WQ tag table, then posts a copy-WQ descriptor. Completion handlers read and clear this object, unmap buffers through `fnic_release_ioreq_buf()`, and free it. Abort and device-reset paths reuse the same object to wait for firmware ITMF completions.

State and persistence: all state is per-command and volatile. The `start_time` supports latency histograms and EH diagnostics. `abts_done` and `dr_done` are stack completion pointers owned by EH callers and must be set/cleared under the copy-WQ lock.

Dependencies: the header depends on SCSI FC FCP definitions and `fnic_fdls.h` for iport/tport types. It is included by resource descriptor helpers, main initialization, FCS, ISR, and SCSI files.

Risks and test signals: risks center on lifetime and locking: stale `io_req` pointers, double completion, DMA unmap after failed mapping, and stack completion pointers surviving timeout paths. Tests should stress high queue depth, large SGL commands above 32 segments, abort races with normal completion, LUN reset with pending commands, host reset/unload with active I/O, and blk-mq tag reuse.
