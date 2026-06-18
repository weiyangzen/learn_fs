# sources/distributed-fs/ceph-client/net/core/datagram.c

## Purpose
This file provides generic networking-core helpers for datagram-style socket receive, peek, copy, checksum, zerocopy scatter-gather construction, and poll behavior. It centralizes common logic used by protocols such as UDP, raw sockets, packet sockets, Appletalk/IPX-style datagram users, and sequenced-packet sockets that share skb receive-queue semantics.

## Important APIs, Types, and Functions
Receive-side helpers include `connection_based()`, `receiver_wake_function()`, `__skb_wait_for_more_packets()`, `skb_set_peeked()`, `__skb_try_recv_from_queue()`, `__skb_try_recv_datagram()`, `__skb_recv_datagram()`, `skb_recv_datagram()`, `skb_free_datagram()`, `__sk_queue_drop_skb()`, and `skb_kill_datagram()`. These operate on `struct sock`, `struct sk_buff_head`, and `struct sk_buff`, handling `MSG_PEEK`, offsets, blocking waits, socket errors, shutdown, and busy polling.

Copy helpers are centered on `__skb_datagram_iter()`, which walks skb head data, page frags, and nested frag skbs into an `iov_iter`. Public wrappers include `skb_copy_datagram_iter()`, `skb_copy_and_crc32c_datagram_iter()` under `CONFIG_NET_CRC32C`, `skb_copy_datagram_from_iter()`, `skb_copy_datagram_from_iter_full()`, and checksum-aware `skb_copy_and_csum_datagram_msg()`.

Zerocopy send construction is handled by `zerocopy_fill_skb_from_iter()`, `zerocopy_fill_skb_from_devmem()`, `__zerocopy_sg_from_iter()`, and `zerocopy_sg_from_iter()`. These pin or reference pages/netmem from user iterators or devmem dma-buf bindings and append them as skb fragments while updating skb length, data length, truesize, and socket write memory accounting.

Poll APIs are `datagram_poll_queue()` and `datagram_poll()`, returning `__poll_t` masks for errors, receive readiness, shutdown/hangup, connection state, and write availability.

## Control Flow
`__skb_recv_datagram()` computes the receive timeout from socket flags, repeatedly calls `__skb_try_recv_datagram()`, and sleeps in `__skb_wait_for_more_packets()` while the queue has not advanced and the timeout allows. `__skb_try_recv_datagram()` first reports pending socket errors, locks the queue, delegates selection to `__skb_try_recv_from_queue()`, unlocks, optionally busy-polls if the queue did not advance, and returns `-EAGAIN` when no skb is ready.

`__skb_try_recv_from_queue()` walks the skb queue. For normal receives it unlinks the first eligible skb. For `MSG_PEEK`, it may maintain a byte offset across already-peeked skbs, clones shared zero-length skbs before setting `skb->peeked`, increments the skb user count, and leaves the skb queued. `__sk_queue_drop_skb()` and `skb_kill_datagram()` handle the follow-up case where a peeked skb needs to be removed if it is still queued.

`__skb_datagram_iter()` copies out in three stages: linear skb head, page fragments, then nested frag-list skbs recursively. It uses callback indirection so plain copy, CRC32C update, and checksum update can share traversal. On short copy or malformed length it reverts the iterator to its starting position and returns `-EFAULT` unless the caller allows a nonfault short copy at end of iterator.

`skb_copy_datagram_from_iter()` mirrors the traversal in the opposite direction, copying from an iterator into linear data, page frags, and nested fragments. The `_full` variant saves and restores iterator state on failure. `skb_copy_and_csum_datagram_msg()` either validates the existing checksum before plain copy when the destination is short, or copies and computes the checksum in one pass, reverting the iterator if the checksum fails.

Zerocopy filling first copies any linear head bytes when needed, then gathers pages from the iterator or resolves devmem offsets from a dma-buf binding. It coalesces adjacent compound-page fragments where possible, enforces `MAX_SKB_FRAGS`, advances the iterator, and charges the resulting truesize either to stream socket write memory or to the skb socket write allocation.

`datagram_poll_queue()` registers the caller in the socket wait queue, reports errors and error queue state, maps receive shutdown to readable/RDHUP events, reports custom receive-queue non-emptiness, handles connection-based close/SYN_SENT state, and reports writability via `sock_writeable()` or sets async nospace.

## State and Persistence
The file manipulates transient socket receive queues, skb reference counts, skb `peeked` state, queue links, iterator positions, checksum accumulators, skb fragment arrays, skb length/truesize fields, and socket memory counters. It does not persist state beyond socket/skb lifetime, but its helpers are responsible for preserving invariants across blocking waits, peeking, iterator rollback, zerocopy page references, and socket shutdown transitions.

## Dependencies and Integration Points
Dependencies include core socket APIs, skbuff internals, wait queues, poll/epoll flags, busy-poll support, iov_iter, checksum and CRC helpers, page-frag mapping, highmem local mapping, tracepoint `trace_skb_copy_datagram_iovec`, netdevice checksum fault reporting, and optional devmem dma-buf support from `devmem.h`. Exported symbols integrate with protocol receive paths, protocol send paths that build skb frags from userspace, and generic socket file poll operations.

## Risks
Important risks include races between `MSG_PEEK` and consuming reads, incorrect skb refcounting or queue unlinking, sleeping/waiting with stale queue-position observations, iterator rollback bugs after partial copies, checksum validation paths that copy data before detecting failure, zerocopy page reference leaks, `MAX_SKB_FRAGS` overflow, incorrect truesize/socket memory charging, and poll readiness mismatches for protocols using custom receive queues. Devmem support adds risk around interpreting user iterator addresses as dma-buf offsets and rejecting unsupported iterator types.

## Test Signals
Useful tests include UDP/raw/packet socket receive with blocking, nonblocking, timeout, shutdown, and signal interruption; `MSG_PEEK` with offsets, zero-length skbs, shared skbs, and concurrent consume; fault-injected iov_iter short copies verifying iterator restoration; checksum and CRC32C copy validation; send zerocopy with many fragments, adjacent fragment coalescing, and `MAX_SKB_FRAGS` boundary; devmem-backed iterator success and rejection cases; busy-poll smoke tests; and epoll/poll readiness for error queues, shutdown, hangup, connection-based sockets, and custom receive queues.
