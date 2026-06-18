# sources/distributed-fs/ceph-client/include/linux/vmw_vmci_api.h

## Purpose
`vmw_vmci_api.h` declares the public in-kernel VMware VMCI client API. It allows other kernel components, notably VMCI sockets/vsock support, to create datagram endpoints, doorbells, event subscriptions, and queue pairs over VMware's Virtual Machine Communication Interface.

## Important APIs, Types, and Functions
The header defines `VMCI_KERNEL_API_VERSION_*`, `vmci_device_shutdown_fn`, and `vmci_vsock_cb`. Datagram APIs include `vmci_datagram_create_handle()`, `vmci_datagram_create_handle_priv()`, `vmci_datagram_destroy_handle()`, and `vmci_datagram_send()`. Doorbell APIs include `vmci_doorbell_create()` and `vmci_doorbell_destroy()`. Context APIs include `vmci_get_context_id()`, `vmci_is_context_owner()`, `vmci_context_get_priv_flags()`, and `vmci_register_vsock_callback()`. Event APIs are `vmci_event_subscribe()` and `vmci_event_unsubscribe()`. Queue-pair APIs include `vmci_qpair_alloc()`, `vmci_qpair_detach()`, producer/consumer index readers, free-space/ready-byte queries, and vectorized enqueue/dequeue/peek operations.

## Control Flow
Clients create handles or queue pairs, provide callbacks for incoming datagrams or events, send datagrams to VMCI handles, and use queue-pair enqueue/dequeue calls for stream-like data exchange. Queue-pair operations return availability through shared producer/consumer indexes. Event subscribers receive callbacks by subscription ID, while doorbells provide lightweight notification channels.

## State and Persistence
State is held by the VMCI core in registered resources, queue-pair objects, event subscription tables, and doorbell handles. The API passes opaque handles and `struct vmci_qp *` references. There is no durable persistence; resources live until explicit detach/destroy, context teardown, or device shutdown.

## Dependencies and Integration Points
The header depends on Linux UID/GID types, VMCI definitions, `struct msghdr`, and callback types from `vmw_vmci_defs.h`. Integration points include VMware guest/host drivers, VMCI transport for vsock, event delivery, doorbell notification, and queue-pair backed data paths.

## Risks
Clients must destroy handles and detach queue pairs exactly once. Permission checks through context IDs, uid ownership, and privilege flags must be respected. Queue-pair size and peer flags must match the peer or allocation/attach fails. Datagram callbacks may run in constrained contexts depending on flags. Vector enqueue/dequeue modes must match user/kernel buffer expectations.

## Test Signals
Signals include VMCI device probe, context ID retrieval, datagram send/receive, doorbell notification, event subscribe/unsubscribe, queue-pair allocation and detach, producer/consumer index consistency, vsock traffic over VMCI, and negative tests for access, duplicate handles, and peer mismatch.
