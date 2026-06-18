# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_loopback.c

## Purpose
This file implements the local loopback vsock transport using virtio-vsock common transport operations. It registers a `VSOCK_TRANSPORT_F_LOCAL` transport that reports CID `VMADDR_CID_LOCAL` and feeds transmitted packets back into the virtio-vsock receive path.

## Important APIs, types, and functions
`struct vsock_loopback` stores the workqueue, packet queue, and worker. `vsock_loopback_get_local_cid()` returns the local CID. `vsock_loopback_send_pkt()` queues an skb with `virtio_vsock_skb_queue_tail()` and schedules worker processing. `vsock_loopback_cancel_pkt()` purges queued packets for a socket. The `loopback_transport` object wires AF_VSOCK transport callbacks to `virtio_transport_*` helpers and its `send_pkt` method to `vsock_loopback_send_pkt()`.

`vsock_loopback_work()` splices the packet queue into a local queue, marks bytes as sent with `virtio_transport_consume_skb_sent(skb, false)`, delivers tap visibility, and calls `virtio_transport_recv_pkt()` using the skb socket namespace. Module init allocates the workqueue and registers with vsock core; exit unregisters, flushes work, purges queued skbs, and destroys the workqueue.

## Control flow
Send is asynchronous: enqueue skb, queue work, then the worker drains all queued packets. The worker owns receiver delivery and skb lifetime transfer. Cancellation purges outstanding queue entries for a closing socket. Init and exit pair transport registration with workqueue lifetime.

## State and persistence
All state is global module memory in `the_vsock_loopback`: one workqueue and one skb queue. There is no durable persistence. Queue locking uses the skb queue spinlock and bottom-half-safe operations.

## Dependencies and integration points
The file depends on virtio-vsock common APIs and vsock core registration. It exposes loopback support to AF_VSOCK users and advertises `MODULE_ALIAS_NETPROTO(PF_VSOCK)`. It integrates with BPF through `read_skb = virtio_transport_read_skb` and allows message zero-copy.

## Risks
Packet lifetime is delicate because the worker decrements unsent bytes without freeing the skb, leaving the receiver path to free it. Exit must unregister before purging to prevent new sends. Namespace delivery uses `sock_net(skb->sk)`, so skb socket association must remain valid.

## Test signals
Use local CID stream, seqpacket, and datagram traffic; cancellation during close; module unload with queued packets; tap visibility; zero-copy capability checks; and concurrent send stress.
