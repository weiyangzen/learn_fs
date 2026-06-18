# sources/distributed-fs/ceph-client/net/sunrpc/socklib.c

## Purpose
`socklib.c` provides common socket/XDR helpers shared by SUNRPC client and server transports. It copies received sk_buff data into XDR buffers while validating checksums, and sends an `xdr_buf` directly through a socket, including stream record markers and paged payloads.

## Important APIs, Types, And Functions
The exported APIs are `csum_partial_copy_to_xdr()` and `xprt_sock_sendmsg()`. Internal helpers include `xdr_skb_read_bits()`, `xdr_partial_copy_from_skb()`, `xprt_sendmsg()`, `xprt_send_kvec()`, `xprt_send_pagedata()`, and `xprt_send_rm_and_kvec()`. `struct xdr_skb_reader` tracks the source skb, copy offset, remaining byte count, checksum state, and accumulated checksum.

## Control Flow
Receive copy initializes an `xdr_skb_reader` over the skb. If the skb checksum is already unnecessary, it copies head, page, and tail data into the target XDR buffer and verifies all data was consumed. Otherwise it copies while accumulating checksum blocks, checks any remaining skb bytes, folds the checksum, and reports checksum faults for unchecked `CHECKSUM_COMPLETE` packets. Send flow walks the record marker plus XDR head, page data, and tail in order, advances over the caller's `base` offset, sets `MSG_MORE` until the final fragment, and returns queued bytes via `sent_p`.

## State And Persistence
The file keeps no persistent global state. All state is per-call: skb offset/count/checksum while receiving, iterator state in `msghdr`, and caller-visible sent byte accounting. Sparse XDR pages can be allocated lazily with `GFP_NOWAIT` during receive copy.

## Dependencies And Integration Points
The file depends on Linux skb copy/checksum APIs, page mapping helpers, XDR buffer layout, RPC record markers, socket `sock_sendmsg()`, `iov_iter` kvec/bvec setup, and network checksum fault reporting. It is used by socket transport implementations for UDP receive and TCP/stream send paths.

## Risks And Edge Cases
Partial skb copy failures return short counts or `-ENOMEM`, which callers treat as failed receive. Sparse page allocation is nonblocking and may return a partial copy. Send logic must handle nonzero `base` correctly across optional record marker, head, pages, and tail; off-by-one errors would retransmit or skip payload bytes. `MSG_MORE` must be cleared for the final segment to avoid delaying transmission. The checksum path must validate both copied XDR bytes and any uncopied skb remainder.

## Test Signals
Useful tests include UDP checksum-good and checksum-bad packets, CHECKSUM_COMPLETE fault reporting, sparse page allocation failure injection, XDR buffers with head/page/tail combinations, stream sends with and without record markers, partial sends with nonzero base offsets, and packetdrill or transport tests that verify `sent_p` and `MSG_MORE` behavior.
