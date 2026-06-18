# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/ring.c

Purpose: endpoint ring cache and ring-pointer management for command, channel, and event rings. It maps host ring context into local state, caches host descriptors, appends event elements to host rings, updates read pointers, and raises moderated IRQs for event rings.

Important APIs: `mhi_ep_ring_init()`, `mhi_ep_ring_start()`, `mhi_ep_ring_reset()`, `mhi_ep_ring_addr2offset()`, `mhi_ep_update_wr_offset()`, `mhi_ep_ring_add_element()`, and `mhi_ep_ring_inc_index()`. Internal caching copies host descriptors through controller `read_sync()` and writes event elements through `write_sync()`.

Control flow: ring start reads `rlen`, `rbase`, `rp`, and `wp` from host context, computes offsets, records event MSI vector/intmod, allocates a descriptor cache, and caches descriptors up to host write pointer. Channel/command rings refresh their cached descriptors when doorbells arrive. Adding an event checks free space, writes a ring element to the host event ring, increments the local read offset, and writes the new `rp` back to the context. Event-ring delayed work raises the configured IRQ vector.

State and persistence: `struct mhi_ep_ring` stores ring size/base, read/write offsets, descriptor cache, event moderation work, IRQ pending flag, and started state. Host ring contexts persist in shared memory; cache is freed on reset.

Dependencies and integration: depends on controller read/write sync transport callbacks, MMIO doorbell reads, endpoint main event/command/channel processing, and delayed work.

Risks: wraparound cache copying and free-space calculation are protocol-critical. `mhi_ep_ring_add_element()` supports one element at a time only. Event ring start does not cache descriptors. Test signals include wraparound descriptor reads, empty/full event ring behavior, rp/wp updates, event interrupt moderation/cancel, reset cancellation of delayed work, and transport callback failures.
