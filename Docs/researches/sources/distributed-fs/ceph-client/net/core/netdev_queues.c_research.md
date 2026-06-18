<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_queues.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_queues.c

## Purpose
Shared queue utility code for DMA-device selection, queue-creation eligibility, queue-lease eligibility, and queue-busy checks used by the netdev generic-netlink queue control plane and memory-provider setup.

## APIs, Types, and Functions
`netdev_queue_get_dma_dev()` returns the DMA device for an RX or TX queue, following RX queue leases from virtual to physical devices when needed. `netdev_can_create_queue()` validates that a device is virtual and implements `ndo_queue_create`. `netdev_can_lease_queue()` validates that a lease source is a present physical device with queue management ops. `netdev_queue_busy()` rejects queues already used by AF_XDP, RX queue leasing, or a memory provider.

## Control Flow, State, and Persistence
The helpers are read-only except for extack messages. DMA-device lookup requires the caller to hold the netdev ops lock, handles leased RX queues by locking the physical device, and falls back to `dev->dev.parent` when the driver lacks `ndo_queue_get_dma_dev`.

## Dependencies and Integration
Depends on `netdev_queue_mgmt_ops`, RX queue lease helpers from `netdev_rx_queue.c`, AF_XDP `xsk_get_pool_from_qid()`, and device DMA mask validation. It feeds dmabuf binding, queue creation, and zero-copy memory-provider paths.

## Risks and Test Signals
Risks include returning NULL for devices with missing DMA masks, incorrect virtual/physical classification through `dev.parent`, and stale busy checks if future users can attach to TX queues. Test signals are AF_XDP rejection, leased RX queue rejection, memory-provider rejection, virtual-device queue creation acceptance, and leased RX DMA lookup returning the physical queue DMA device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_queues.c -->
