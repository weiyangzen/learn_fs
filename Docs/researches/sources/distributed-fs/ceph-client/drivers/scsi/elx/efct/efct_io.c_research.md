# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_io.c

## Purpose
`efct_io.c` manages the software SCSI IO pool used above the HW XRI pool. It preallocates `struct efct_io` objects, response DMA buffers, and SGL arrays, hands IOs to the SCSI target path, returns them to a freelist, and finds active target IOs by FC exchange IDs for ABTS/TMF handling.

## Important APIs, Types, and Functions
`struct efct_io_pool` contains the owning `struct efct`, a spinlock, a fixed array of up to `EFCT_NUM_SCSI_IOS`, and a freelist. Public functions are `efct_io_pool_create`, `efct_io_pool_free`, `efct_io_pool_allocated`, `efct_io_pool_io_alloc`, `efct_io_pool_io_free`, and `efct_io_find_tgt_io`.

## Control Flow
Pool creation allocates the pool, initializes its freelist/lock, then loops over `EFCT_NUM_SCSI_IOS`, allocating one `struct efct_io`, a coherent response buffer sized for FCP response plus sense data, and a software SGL array sized by HW capability. Each IO is tagged by index and added to the freelist. Allocation removes the first freelist entry under lock, resets per-command fields, assigns EFCT context, and increments active/total allocation counters. Freeing removes any associated HW IO after the software IO is returned to the freelist and updates active/free counters. `efct_io_find_tgt_io` scans a node's active IO list for matching OX_ID and optional RX_ID and takes a kref before returning.

## State and Persistence Behavior
The IO pool is volatile memory owned by `efct->xport->io_pool`. Per-IO response DMA and SGL allocations persist across individual commands until pool free. Per-command fields are reset on allocation, while the allocated buffers and tag/index remain stable. Active IO membership is not managed by this file except through `efct_io_find_tgt_io`; SCSI allocation/free add/remove active node list entries.

## Dependencies and Integration Points
This file depends on `efct_hw_io_free` for returning associated HW exchanges, Linux DMA coherent allocation, spinlocks, and node active IO lists. It is created by `efct_xport_attach`, used by `efct_scsi_io_alloc` and abort helper allocation, and freed by xport shutdown.

## Risks
Partial pool creation can silently create fewer than `EFCT_NUM_SCSI_IOS` IOs if `kzalloc_obj` fails, but callers may assume the configured pool size. A failed SGL allocation calls `efct_io_pool_free`, which expects prior DMA fields to be valid. Returning the software IO to the freelist before freeing the associated HIO creates a window where the IO object is visible as free while HW cleanup is still happening, although the lock protects list state. `efct_io_find_tgt_io` relies on active list and kref discipline from `efct_scsi.c`.

## Test Signals
Validate pool creation/free under allocation failures, DMA buffer lifetime, allocation/free counter symmetry, HIO release on software IO free, ABTS lookup by OX_ID and wildcard/specific RX_ID, and behavior when pool exhaustion occurs.
