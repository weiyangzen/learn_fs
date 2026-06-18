<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c

## Purpose
`client-buffers.c` manages per-client ISHTP RX and TX ring buffers plus IO request block recycling. It is the allocation/free/recycle layer used by ISHTP clients after connection setup.

## Important APIs, Types, and Functions
RX APIs are `ishtp_cl_alloc_rx_ring`, `ishtp_cl_free_rx_ring`, `ishtp_io_rb_init`, `ishtp_io_rb_alloc_buf`, `ishtp_cl_io_rb_recycle`, and `ishtp_cl_rx_get_rb`. TX APIs are `ishtp_cl_alloc_tx_ring` and `ishtp_cl_free_tx_ring`. `ishtp_io_rb_free` frees a standalone request block.

## Control Flow
RX ring allocation uses the firmware client maximum message length, creates `rx_ring_size` request blocks, allocates each data buffer, and appends them to `free_rb_list` under `free_list_spinlock`. TX allocation creates `tx_ring_size` transmit ring entries, allocates send buffers of the same max message length, appends them to `tx_free_list`, and increments `tx_ring_free_size`. Failure paths call the corresponding free function to unwind partial allocation.

RX free drains both free and in-process lists under their spinlocks, freeing data buffers and request blocks. TX free drains both free and active TX lists. Recycling returns an RX block to the free list and, if the client has no outgoing flow-control credits, calls `ishtp_cl_read_start` to notify firmware that receive capacity is available. `ishtp_cl_rx_get_rb` removes the first in-process RX block for client event callbacks.

## State and Persistence Behavior
Ring entries persist for the connection lifetime and are freed on disconnect/reset/remove. List membership tracks ownership: free RX, in-process RX, free TX, and active TX. Spinlocks protect list mutation and `tx_ring_free_size`.

## Dependencies and Integration Points
The file depends on `client.h` definitions for `struct ishtp_cl`, request block types, lists, spinlocks, and flow-control helper `ishtp_cl_read_start`. It is called from ISHTP client connection setup and reset cleanup.

## Risks and Edge Cases
Max message length comes from firmware properties; a bogus large value can drive memory pressure. `ishtp_cl_io_rb_recycle` appends without checking whether the block is already on a list, so double recycle would corrupt lists. Free paths assume no concurrent users remain; reset/remove ordering must cancel callbacks first. Flow-control restart during recycle can fail and returns the error to the caller, but many callbacks may ignore it.

## Test Signals
Test allocation failure unwind, normal RX event recycle, flow-control restart when credits are exhausted, reset cleanup with in-process buffers, TX free-size accounting, and concurrency under high-rate sensor reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client-buffers.c -->
