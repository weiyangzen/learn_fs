# sources/distributed-fs/ceph-client/net/rds/message.c

## Purpose
`message.c` implements allocation, reference counting, payload storage, extension header manipulation, zero-copy completion bookkeeping, user-copy helpers, and flush waiting for `struct rds_message`. It is the shared message object layer used by loopback, TCP, and IB transports.

## Important APIs, Types, and Functions
Public functions include `rds_message_alloc()`, `rds_message_alloc_sgs()`, `rds_message_map_pages()`, `rds_message_copy_from_user()`, `rds_message_inc_copy_to_user()`, `rds_message_addref()`, `rds_message_put()`, `rds_message_populate_header()`, `rds_message_add_extension()`, `rds_message_next_extension()`, `rds_message_add_rdma_dest_extension()`, `rds_message_wait()`, `rds_message_unmapped()`, and `rds_notify_msg_zcopy_purge()`. Zero-copy helpers manage `struct rds_msg_zcopy_info`, `struct rds_znotifier`, and socket zcookie queues.

## Control Flow
Messages are allocated with extra inline space for all scatterlist entries needed by data, RDMA, and atomic ops. `rds_message_alloc_sgs()` partitions that inline SG pool. Payload creation either copies user data into pages allocated by `rds_page_remainder_alloc()` or, for zero-copy, pins user pages with `iov_iter_get_pages2()` and records a notifier for completion cookies. `rds_message_map_pages()` builds a message over kernel page addresses and marks `RDS_MSG_PAGEVEC` so purge will not free those pages.

Header helpers initialize fixed fields, pack extension headers into the 16-byte extension area, and iterate extension headers by implied type length. RDMA destination cookies use the generic extension packing helper.

`rds_message_put()` drops a refcount and on final put verifies the message is off socket/connection lists, purges payload pages, zero-copy notifiers, RDMA/atomic operation state, and referenced MRs, then frees the message. Zero-copy completion records cookies into per-socket batches, wakes socket waiters, and handles early failure before a message is attached to a socket. `rds_message_wait()` blocks until the transport clears `RDS_MSG_MAPPED` via `rds_message_unmapped()`.

## State and Persistence
Message state persists while refcounted by socket queues, connection queues, transport work requests, or embedded incoming delivery. Payload pages are owned by the message except for pagevec messages and zero-copy pinned user pages. Zero-copy cookie state is persisted in the socket zcookie queue until collected by receive-side control messages.

## Dependencies and Integration Points
The file depends on `page.c` for small page-fragment allocation, `rdma.c` for RDMA/atomic cleanup, socket wakeups, Linux iterator/page pinning APIs, and checksum/extension constants from `rds.h`. Transports call addref/put and `rds_message_unmapped()` around DMA ownership. Receive code uses `rds_message_inc_copy_to_user()` for loopback messages.

## Risks
SG pool accounting must match all control-message extra-size calculations; otherwise later SG allocation fails or overwrites memory. Zero-copy paths must unaccount pinned pages on every error path. Extension header space is tiny and silently refuses additions by returning 0, so callers must handle dropped metadata. Final purge must not free pagevec pages. Refcount/list assertions can BUG on lifetime violations.

## Test Signals
Test copied and zero-copy sends, partial user-copy failures, SG pool exhaustion, extension packing/iteration near the 16-byte limit, message flush waiting, pagevec messages, and RDMA/atomic cleanup on final put. Check zcopy completion control messages and memory pin accounting.
