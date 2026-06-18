<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c

## Purpose
Implements the Linux NVMe over Fabrics TCP host transport. It registers the `tcp` fabrics transport, creates and reconnects controllers, maps blk-mq requests to NVMe/TCP command and data PDUs, owns socket callback integration, supports header/data digests, and optionally negotiates TLS PSKs before the NVMe/TCP initial connection exchange.

## Important APIs, Types, And Functions
Core state lives in `struct nvme_tcp_ctrl`, `struct nvme_tcp_queue`, and `struct nvme_tcp_request`. The important blk-mq hooks are `nvme_tcp_queue_rq()`, `nvme_tcp_commit_rqs()`, `nvme_tcp_timeout()`, `nvme_tcp_poll()`, `nvme_tcp_init_request()`, and hctx init functions. Transport lifecycle is driven by `nvme_tcp_create_ctrl()`, `nvme_tcp_setup_ctrl()`, `nvme_tcp_configure_admin_queue()`, `nvme_tcp_configure_io_queues()`, `nvme_tcp_start_queue()`, teardown helpers, reset/reconnect work, and `nvme_tcp_transport`. Send and receive state machines are centered on `nvme_tcp_try_send()`, `nvme_tcp_try_recv()`, `nvme_tcp_recv_skb()`, `nvme_tcp_recv_pdu()`, `nvme_tcp_recv_data()`, and digest helpers.

## Control Flow
Controller creation parses fabrics options, prevents duplicate connects unless allowed, allocates queues, initializes the common NVMe controller, then configures the admin queue and I/O queues. Queue allocation creates a kernel TCP socket, binds source address/interface when requested, sets TCP options, optionally starts TLS, performs the NVMe/TCP ICReq/ICResp negotiation, and later installs socket callbacks before sending fabrics connect commands. Requests enter from blk-mq, are encoded as command PDUs with transport SGL descriptors, queued through an llist/list pair, and drained by `nvme_tcp_io_work()`. Writes may send inline data, R2T-driven H2C data PDUs, and optional data digests. Reads parse C2H data PDUs into request iterators and complete either via response CQEs or DATA_SUCCESS. Socket state changes and protocol errors trigger reset/reconnect recovery.

## State And Persistence
No media state is persisted here; the file maintains live transport state only. Controller state includes queue arrays, tag sets, address options, reconnect counters, TLS PSK id, and work items. Queue state tracks socket callbacks, CPU affinity, flags for allocated/live/polling, PDU receive offsets, digest CRCs, pending requests, and the current send request. Request state tracks PDU bytes sent, data iterator position, R2T offsets, NVMe status, and digest bytes. Across reconnects, queues and tag sets are torn down and rebuilt while the common NVMe controller state machine moves through CONNECTING, LIVE, RESETTING, and deletion states.

## Dependencies And Integration Points
Integrates with NVMe core/fabrics helpers, blk-mq, kernel sockets/TCP, TLS handshake/keyring APIs, CRC32C, busy-poll, workqueues, memory reclaim controls, and transport registration. It relies on `nvme.h` and `fabrics.h` for command setup, controller state, fabrics connect/register operations, authentication, queue mapping, and namespace request completion.

## Risks
High-risk areas are socket lifetime and callback replacement, because error recovery, teardown, TLS, and reconnect can race with data-ready/write-space callbacks. Send/receive state must handle partial socket I/O, digest mismatch, R2T protocol violations, inline data completion, and CQE lookup failures without double completion. Memory reclaim windows use `memalloc_noreclaim_save()` and `memalloc_noio_save()` to avoid block I/O recursion during send and socket release. TLS secure concatenation has careful PSK revocation and admin-queue restart rules. Global queue CPU accounting is best effort and must be decremented exactly when queues stop.

## Test Signals
Useful coverage includes normal connect/disconnect, reconnect after TCP close, controller reset, duplicate connect rejection, IPv4/IPv6 source binding, host interface binding, header/data digest success and failure, TLS static PSK and secure concatenation, R2T writes larger than inline capsule size, read DATA_SUCCESS completion, blk-mq timeout handling, busy-poll queues, and module unload with live controllers. Kernel signals include absence of request double-completion, lockdep splats on socket locks, stuck socket wmem warnings, and stale TLS key ids after reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c -->
