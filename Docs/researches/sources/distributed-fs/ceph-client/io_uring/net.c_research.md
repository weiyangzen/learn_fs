<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.c -->
# sources/distributed-fs/ceph-client/io_uring/net.c

## Purpose
`net.c` implements io_uring network opcodes: shutdown, send/sendmsg, recv/recvmsg, multishot and bundled send/recv, zero-copy send notifications, zero-copy receive handoff, accept, socket creation, connect, bind, listen, BPF socket filter population, and network async-data cleanup. It is the main bridge between io_uring request semantics and socket APIs.

## Important APIs, Types, and Functions
- Per-op command payloads include `io_shutdown`, `io_accept`, `io_socket`, `io_connect`, `io_bind`, `io_listen`, `io_sr_msg`, and `io_recvzc`.
- Prep/issue pairs include `io_shutdown_prep()`/`io_shutdown()`, `io_sendmsg_prep()`/`io_sendmsg()`/`io_send()`, `io_recvmsg_prep()`/`io_recvmsg()`/`io_recv()`, `io_recvzc_prep()`/`io_recvzc()`, `io_send_zc_prep()`/`io_sendmsg_zc()`, `io_accept_prep()`/`io_accept()`, `io_socket_prep()`/`io_socket()`, `io_connect_prep()`/`io_connect()`, `io_bind_prep()`/`io_bind()`, and `io_listen_prep()`/`io_listen()`.
- `io_msg_alloc_async()`, `io_net_import_vec()`, `io_msg_copy_hdr()`, and compat helpers import and cache msghdr/iovec state.
- `io_recv_finish()` and `io_send_finish()` centralize CQE flags, buffer commitment, multishot retry, bundle continuation, and final result setting.
- `io_send_zc_cleanup()`, `io_sendrecv_fail()`, and `io_netmsg_cache_free()` handle cleanup/failure for async network data and zero-copy notifications.
- `io_socket_bpf_populate()` fills BPF filter context for socket operations.

## Control Flow
Send prep allocates `io_async_msghdr`, reads length/flags/message flags, records buffer group for buffer-select requests, handles bundle mode, marks NOWAIT on `MSG_DONTWAIT`, sets compat CMSG flags, then imports either a raw buffer, a fixed registered buffer, a vector, or a userspace msghdr. Send issue checks socket type, honors `POLL_FIRST`, applies nonblocking flags, optionally selects provided buffers, calls `sock_sendmsg()` or `__sys_sendmsg_sock()`, handles `MSG_WAITALL` short sends by accumulating `done_io` and returning retry, commits selected buffers, posts bundle CQEs with `IORING_CQE_F_MORE`, recycles async msg data, and completes.

Recv prep mirrors send but validates recv-specific flags, requires buffer selection for multishot, rejects `MSG_WAITALL` for multishot, supports per-shot and total byte limits for `IORING_OP_RECV`, and imports destination buffers or msghdrs. Recv issue selects provided buffers when needed, prepares multishot recvmsg output headers, calls `sock_recvmsg()` or `__sys_recvmsg_sock()`, handles partial `MSG_WAITALL`, converts `-ERESTARTSYS`, recycles buffers on no data/retry, and delegates to `io_recv_finish()`. Finish computes `SOCK_NONEMPTY`, buffer CQE flags, bundle accumulation, multishot CQE posting, fairness-limited immediate retries, and `IOU_REQUEUE` when a multishot loop exceeds `MULTISHOT_MAX_RETRY`.

Zero-copy send prep allocates a notification request with `io_alloc_notif()`, chooses notification user_data, rejects CQE skip, sets `MSG_ZEROCOPY`, imports normal or fixed buffers, configures `sg_from_iter`, and accounts memory for non-fixed iterators. Issue verifies socket zero-copy support, imports fixed buffers lazily if needed, assigns the notification ubuf, sends, flushes notification immediately unless running unlocked in io-wq, sets the request result with `IORING_CQE_F_MORE`, and relies on notification completion for the final notification CQE.

Accept/socket operations optionally install files into fixed-file tables. Accept supports multishot, poll-first, don't-wait, normal fd allocation, fixed slot allocation, and `SOCK_NONEMPTY` CQE flags. Socket creation supports normal or fixed-file install and BPF context population. Connect stores sockaddr in async data, tracks in-progress state, retries `-EINPROGRESS`/`-EAGAIN`/first `-ECONNABORTED` under nonblocking issue, and reads `sock_error()` for completion after poll. Bind/listen are straightforward wrappers around kernel socket helpers after prep-time address/backlog validation.

## State and Persistence Behavior
Network requests persist mutable state across retries in the request command area: `done_io`, message flags, selected buffer group, multishot counters/limits, current buffer pointer/length, control pointer, notification request, connect progress flags, and fixed-file slot/nofile limits. `req->async_data` stores `io_async_msghdr` and can be recycled into `ctx->netmsg_cache` when issue occurs under the ring lock. Cached vectors may be retained up to `IO_VEC_CACHE_SOFT_CAP`; larger vectors are freed.

Provided buffers interact with request flags `REQ_F_BUFFER_SELECT`, `REQ_F_BUFFER_RING`, `REQ_F_BUFFERS_COMMIT`, `REQ_F_BL_EMPTY`, `REQ_F_BL_NO_RECYCLE`, `REQ_F_APOLL_MULTISHOT`, and `REQ_F_MULTISHOT`. Zero-copy send creates a secondary notification request whose completion state persists until skb ubuf references drain.

## Dependencies and Integration Points
This module depends on core io_uring request/completion APIs, `kbuf` buffer selection, registered resources/fixed buffers, filetable fixed fd install, allocation cache, zero-copy notification support from `notif.c`, zcrx receive support, compat msghdr helpers, socket syscalls/helpers, skb zero-copy APIs, BPF filter context types, and opdef registration. It is compiled behind `CONFIG_NET` entries in `opdef.c`; `net.h` provides stubs for non-NET builds where needed.

## Risks and Edge Cases
- Multishot and bundle paths are stateful and must avoid monopolizing CPU; `MULTISHOT_MAX_RETRY` forces requeue after repeated immediate completions.
- Buffer-selected sends/receives must commit or recycle buffers on every retry/error path to avoid leaks or double use.
- `MSG_WAITALL` partial transfers accumulate `done_io`; final failures may complete with partial byte counts instead of errors.
- Recvmsg multishot writes a header plus sockaddr/control payload into the selected buffer; size calculation and copy-to-user faults must stop the multishot safely.
- Zero-copy send has two CQE streams: the send result and notification CQE. Cleanup must flush the notification on cancellation/failure and preserve `IORING_CQE_F_MORE`.
- Fixed-buffer zero-copy import is deferred until issue for some paths and uses the notification request for resource ownership.
- Accept/socket fixed-file installs must handle failure after file allocation without leaking fds/files.
- Connect has protocol-specific in-progress behavior and must interpret `-EBADFD`/`-EISCONN` through `sock_error()`.

## Test Signals
Tests should cover send/sendmsg/recv/recvmsg raw and vectored forms, compat msghdrs, fixed buffers, buffer selection, bundles, multishot receive limits, `POLL_FIRST`, NOWAIT and `MSG_DONTWAIT`, `MSG_WAITALL` partials, CQE `SOCK_NONEMPTY`/`MORE`/buffer flags, zero-copy send notification success/copy fallback/accounting, zcrx multishot receive, accept multishot normal/fixed fds, socket fixed install, connect retry and socket error completion, bind/listen validation, cleanup on cancellation, and non-CONFIG_NET fallback via opcode support checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.c -->
