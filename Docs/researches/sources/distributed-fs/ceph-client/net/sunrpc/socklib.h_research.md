# sources/distributed-fs/ceph-client/net/sunrpc/socklib.h

## Purpose
`socklib.h` is the small internal header that exposes common SUNRPC socket helper routines to transport implementations.

## Important APIs, Types, And Functions
It declares `csum_partial_copy_to_xdr(struct xdr_buf *xdr, struct sk_buff *skb)` for receive-side skb-to-XDR copy/checksum validation and `xprt_sock_sendmsg(struct socket *sock, struct msghdr *msg, struct xdr_buf *xdr, unsigned int base, rpc_fraghdr marker, unsigned int *sent_p)` for send-side XDR buffer transmission.

## Control Flow
The header has no executable control flow. Including files call the declared helpers from transport receive or send paths after preparing an `xdr_buf`, socket, message header, stream marker, and resend base offset.

## State And Persistence
No state is stored in the header. It defines the compile-time contract between `socklib.c` and its users.

## Dependencies And Integration Points
The prototypes depend on SUNRPC/XDR data structures, Linux sockets, sk_buffs, and RPC stream record marker types supplied by including translation units. The header is included by socket transport code that needs shared client/server helper behavior.

## Risks And Edge Cases
Because this is a narrow declaration header, risks are ABI-style drift: mismatched prototypes, missing forward declarations in users, or changes to argument semantics that are not reflected in all transport callers. Callers must honor the ownership and offset semantics implemented in `socklib.c`.

## Test Signals
Compile coverage of all socket transport users is the main signal. Runtime validation comes from the `socklib.c` receive checksum and send-offset tests that exercise these declarations through real transport call sites.
