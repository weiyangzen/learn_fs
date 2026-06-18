<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c

## Purpose

Implements allocation and cleanup of PVRDMA User Access Region indexes used for doorbell pages.

## Important APIs, Types, And Functions

`pvrdma_uar_table_init()` initializes an ID bitmap sized by `dev->dsr->caps.max_uar`, reserves index 0 for the driver/device, and requires a power-of-two table. `pvrdma_uar_alloc()` finds a free bit, sets it, returns an index and PFN. `pvrdma_uar_free()` clears the bit and updates allocation cursors. `pvrdma_uar_table_cleanup()` frees the bitmap.

## Control Flow

Probe initializes the table after capabilities are available. Ucontext allocation obtains a UAR index and passes its PFN to the device through a create-ucontext command. Ucontext deallocation destroys the context and frees the UAR index.

## State And Persistence Behavior

State lives in `dev->uar_table.tbl`: bitmap, `last`, `top`, `max`, `mask`, and lock. UAR allocation persists for the lifetime of a user context. PFNs are derived from the UAR PCI resource start plus allocated index.

## Dependencies And Integration Points

Depends on Linux bitmap helpers, PCI resource addresses, and PVRDMA ucontext code.

## Risks And Edge Cases

`max_uar` must be a power of two. The `top`/mask logic produces wrapped index generations; consumers must agree on how much of `uar->index` is a raw table index versus generation. Index 0 is reserved and must not be handed to userspace.

## Test Signals

Test power-of-two rejection, full-table `-ENOMEM`, reserve index 0, reuse after free, PFN computation, and concurrent allocation/free under the spinlock.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_doorbell.c -->
