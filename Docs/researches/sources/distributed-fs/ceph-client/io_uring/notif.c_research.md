<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.c -->
# sources/distributed-fs/ceph-client/io_uring/notif.c

## Purpose
`notif.c` implements io_uring zero-copy send notification requests. It creates notification `io_kiocb`s, exposes `ubuf_info_ops` for skb zero-copy completion/linking, aggregates linked notifications, accounts/unaccounts pinned memory, and completes notification CQEs through task_work when skb references drain.

## Important APIs, Types, and Functions
- `io_alloc_notif()` allocates and initializes a notification request with NOP opcode and `ubuf_info`.
- `io_tx_ubuf_complete()` is the skb zero-copy completion callback.
- `io_link_skb()` links compatible io_uring notification ubufs on the same skb.
- `io_notif_tw_complete()` finishes one or a linked list of notifications under `uring_lock`.
- Static `io_ubuf_ops` provides `.complete` and `.link_skb` to networking.

## Control Flow
Zero-copy send prep calls `io_alloc_notif()` under `uring_lock`. The function pulls a request from the normal request cache, initializes core fields, consumes a task reference, clears resource nodes, initializes `io_notif_data`, configures ubuf flags/ops, and sets refcount to one.

When the networking stack completes skb zero-copy, `io_tx_ubuf_complete()` updates report fields for zero-copy used/copied status, decrements the ubuf refcount, and returns until it reaches zero. If the notification is linked to a head, it recursively completes the head. Otherwise it queues task_work on the notification request, lazily waking only when no `next` notifications are linked. `io_notif_tw_complete()` walks the linked notification chain, sets `IORING_NOTIF_USAGE_ZC_COPIED` when reporting requires it, unaccounts pages, and delegates each notification to normal request completion.

`io_link_skb()` either attaches a fresh io_uring ubuf to an skb or links another notification into an existing io_uring notification chain if contexts/task contexts match and the chain is not already merged.

## State and Persistence Behavior
Notification state lives in `struct io_notif_data` embedded in a request command area: file pointer, ubuf info, linked-list pointers, page accounting, report flags, and zero-copy used/copied booleans. The ubuf refcount controls lifetime. Linked notifications share a head ubuf reference and complete in a single task_work chain.

## Dependencies and Integration Points
This module integrates with `net.c` zero-copy send paths, skb zero-copy APIs, io_uring request allocation/completion/task_work, resource memory accounting, and notification helpers declared in `notif.h`.

## Risks and Edge Cases
- Notification completion can be linked recursively; context and task context mismatches are rejected to keep task_work completion valid.
- Memory accounting must be unaccounted exactly once when notification completes.
- Reported `ZC_COPIED` status depends on both success and whether the stack actually used zero-copy.
- Cleanup paths must flush notifications when sends fail or are canceled before skb completion.

## Test Signals
Tests should cover successful zero-copy notification CQEs, copied fallback reporting, linked skb notifications, memory accounting/unaccounting, cancellation cleanup via flush, io-wq cleanup ordering, and context mismatch rejection in `link_skb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/notif.c -->
