# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.h

Purpose: provides internal datagram queue and ioctl contracts shared by context, host, and datagram implementation files.

Important types/APIs: `VMCI_MAX_DELAYED_DG_HOST_QUEUE_SIZE` bounds delayed host callback backlog. `struct vmci_datagram_queue_entry` wraps an in-kernel queued datagram with list node and cached datagram size for spinlock-protected queue accounting. `struct vmci_datagram_snd_rcv_info` is the userspace send/receive ioctl payload. Internal prototypes are `vmci_datagram_dispatch()` and `vmci_datagram_invoke_guest_handler()`.

Control flow/integration: contexts store `vmci_datagram_queue_entry` nodes on per-context queues. Host ioctl code copies `vmci_datagram_snd_rcv_info` to and from userspace before calling dispatch/dequeue. Guest interrupt code calls the guest handler for datagrams read from the virtual device.

State/persistence: the queue entry is transient in-memory state and owns a pointer to a separately allocated datagram until dequeued or context destruction.

Risks: the header includes `vmci_context.h`, while context includes this header, so changes can aggravate include cycles. The ioctl struct uses raw user virtual addresses and must remain layout-compatible.

Test signals: structure-size compatibility, datagram queue entry lifetime under enqueue/dequeue/destroy, and ioctl send/receive buffer-size handling.
