# sources/distributed-fs/ceph-client/net/qrtr/tun.c

## Purpose
`tun.c` exposes a `/dev/qrtr-tun` misc device that lets userspace implement or test QRTR endpoints by reading outgoing QRTR frames and writing inbound QRTR frames.

## Important APIs, Types, And Functions
The per-open state is `struct qrtr_tun`, containing a QRTR endpoint, skb queue, and read waitqueue. File operations are `qrtr_tun_open()`, `qrtr_tun_read_iter()`, `qrtr_tun_write_iter()`, `qrtr_tun_poll()`, and `qrtr_tun_release()`. Endpoint transmit callback is `qrtr_tun_send()`.

## Control Flow
Open allocates per-file state, initializes queue/waitqueue, sets endpoint `xmit`, stores private data, and registers the endpoint. When QRTR sends to the endpoint, `qrtr_tun_send()` queues the skb and wakes readers. Reads block until an skb is available unless nonblocking, copy up to the user iov length, and free the skb. Writes allocate a kernel buffer of the user-provided length, copy data from userspace, pass it to `qrtr_endpoint_post()`, free the buffer, and return either the posted length or the QRTR error. Poll reports readable when the queue is non-empty. Release unregisters endpoint, purges queued skbs, and frees state.

## State And Persistence
Each open file has an independent endpoint and queue. State is volatile and ends on close.

## Dependencies And Integration Points
The file integrates with miscdevice registration, poll/read/write iter APIs, QRTR endpoint APIs, skb queues, waitqueues, and usercopy helpers.

## Risks
Read truncates silently to the user buffer length without preserving the remainder because it frees the skb. Large writes up to `KMALLOC_MAX_SIZE` may pressure memory. Release does not explicitly wake blocked readers after unregister; normal file teardown handles close paths, but concurrent blocking I/O deserves attention. Written data must already be a valid aligned QRTR packet.

## Test Signals
Coverage should include open/register failure, blocking and nonblocking reads, poll readiness, short-buffer reads, invalid/zero/oversized writes, valid write injection, and close with queued packets.
