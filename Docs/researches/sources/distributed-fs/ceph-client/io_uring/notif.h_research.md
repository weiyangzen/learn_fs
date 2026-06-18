<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.h -->
# sources/distributed-fs/ceph-client/io_uring/notif.h

## Purpose
`notif.h` declares io_uring zero-copy notification data structures and helpers used by network send paths.

## Important APIs, Types, and Functions
- `IO_NOTIF_UBUF_FLAGS` defines skb ubuf flags for managed zero-copy fragments and orphan behavior.
- `IO_NOTIF_SPLICE_BATCH` defines a batching constant for notification-related splice behavior.
- `struct io_notif_data` stores file, ubuf info, linked notification pointers, accounted pages, and zero-copy report state.
- `io_alloc_notif()` allocates notification requests.
- `io_tx_ubuf_complete()` is the ubuf completion callback.
- `io_notif_to_data()` converts a notification request to its embedded data.
- `io_notif_flush()` forces completion of a notification under `uring_lock`.
- `io_notif_account_mem()` accounts pages against the ring user for non-fixed zero-copy send buffers.

## Control Flow
Zero-copy send prep allocates a notification and optionally calls `io_notif_account_mem()` for the send length. Send issue attaches `io_notif_to_data(notif)->uarg` to the socket message. Cleanup or successful in-ring issue calls `io_notif_flush()` when immediate flushing is required.

## State and Persistence Behavior
`account_pages` accumulates page-accounting charge until completion. `zc_report`, `zc_used`, and `zc_copied` determine notification result flags. `next` and `head` implement linked notification chains.

## Dependencies and Integration Points
It includes net/uio/socket headers and `rsrc.h` for memory accounting. It is used by `net.c` and implemented by `notif.c`.

## Risks and Edge Cases
- `io_notif_account_mem()` estimates pages as `(len >> PAGE_SHIFT) + 2`; callers must pass the same notification that will later unaccount.
- `io_notif_flush()` assumes `uring_lock` is held and invokes the same completion callback path used by networking.

## Test Signals
Tests should verify memory accounting failure paths, flush behavior, report flag propagation, and linked notification completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.h -->
