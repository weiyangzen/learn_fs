<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c

## Purpose

`libsrp.c` provides small SRP target-side utilities for the IBM virtual SCSI target module. It allocates DMA-coherent SRP IU receive buffers, manages a FIFO-backed pool of IU entries, parses SRP data descriptor formats, maps Target Core scatterlists, and drives target-specific RDMA callbacks for direct and indirect SRP data movement.

## Important APIs and Functions

- `srp_target_alloc()` initializes `struct srp_target`, allocates a ring of coherent SRP buffers, creates an IU entry FIFO, and stores the target in device driver data.
- `srp_target_free()` tears down the ring and IU pool.
- `srp_iu_get()` and `srp_iu_put()` pop/push `struct iu_entry` pointers through a locked `kfifo`.
- `srp_transfer_data()` chooses the active SRP descriptor direction and format, locates the direct or indirect descriptor in `srp_cmd::add_data`, and calls the supplied `srp_rdma_t` callback.
- `srp_data_length()` returns the data length encoded in a direct or indirect descriptor.
- `srp_get_desc_table()` returns the command data direction and encoded data length for Target Core submission.
- Internal helpers include `srp_iu_pool_alloc()`, `srp_ring_alloc()`, `srp_direct_data()`, `srp_indirect_data()`, and `data_out_desc_size()`.

## Control Flow

Allocation first creates an array of `struct srp_buf *`, then allocates each `struct srp_buf` and its coherent buffer. The IU pool is a separate array of `struct iu_entry` objects plus a FIFO of pointers to free entries; each entry is pre-associated with one SRP buffer.

For data transfer, `srp_transfer_data()` exits early when Target Core has no data SG entries, calculates the additional CDB-aligned offset, adjusts for data-out descriptors when handling data-in, and dispatches based on `SRP_NO_DATA_DESC`, `SRP_DATA_DESC_DIRECT`, or `SRP_DATA_DESC_INDIRECT`. Direct descriptors use one memory descriptor. Indirect descriptors either use the embedded descriptor list or, when the table is external and `ext_desc`/`dma_map` allow it, allocate coherent memory, copy the external descriptor table from the client through the RDMA callback, then transfer data.

## State and Persistence

All state is in memory: `srp_target` owns the ring, FIFO, device pointer, and optional caller data; each `iu_entry` records its target, remote token, flags, buffer, and IU length. No state persists beyond target allocation/free.

## Dependencies and Integration Points

The implementation uses Linux `kfifo`, DMA coherent allocation, scatterlist DMA mapping, and `<scsi/srp.h>` descriptor definitions. It includes `ibmvscsi_tgt.h` because the RDMA callback type operates on `struct ibmvscsis_cmd`. The target driver supplies `ibmvscsis_rdma()` as the concrete RDMA function.

## Risks and Edge Cases

- `srp_ring_free()` assumes all ring entries were allocated; it is safe for normal teardown but not a partial ring unless the caller follows the allocation error path.
- Data transfer uses `DMA_BIDIRECTIONAL` for SG mapping regardless of final direction, which is conservative but may hide direction-specific bugs.
- External indirect descriptor handling allocates coherent memory sized by the client-provided table descriptor length; callers must validate protocol limits before reaching this path.
- `srp_get_desc_table()` infers a single direction by checking data-in before data-out. Mixed bidirectional descriptors are not represented as true bidirectional Target Core operations.
- Pointer arithmetic depends on `srp_cmd::add_data` being byte-addressable; the file enforces this with `BUILD_BUG_ON()`.

## Test Signals

Unit-style tests should cover pool exhaustion/reuse, partial allocation failure, direct read/write descriptors, embedded indirect descriptors, external indirect descriptor copy, invalid descriptor formats, zero-SG commands, and descriptor lengths that do not match command data lengths. Integration tests should observe `ibmvscsis_rdma()` calls split according to SRP descriptor count and SG list shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/libsrp.c -->
