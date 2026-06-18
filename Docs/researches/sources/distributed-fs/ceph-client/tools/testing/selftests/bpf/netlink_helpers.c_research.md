# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/netlink_helpers.c

Purpose: small route-netlink helper library, adapted from iproute2, for BPF selftests that need to build netlink requests, send them, receive acknowledgements or replies, and append rtattrs safely.

Important APIs/types/functions: `rtnl_open_byproto` and `rtnl_open` create netlink sockets and initialize `struct rtnl_handle`; `rtnl_close` closes them. `rtnl_recvmsg` peeks with `MSG_TRUNC`, allocates a large enough buffer, then receives. `__rtnl_talk_iov` sends one or more netlink messages, tracks sequence numbers, filters replies, handles `NLMSG_ERROR`, and optionally returns an answer buffer. Attribute helpers include `addattr`, typed `addattr8/16/32/64`, `addattrstrz`, `addattr_l`, `addraw_l`, `addattr_nest`, and `addattr_nest_end`.

Control flow: opening sets send/receive buffers, best-effort enables extended ACKs, binds to requested groups, validates sockaddr fields, and seeds sequence from `time(NULL)`. Talk sends messages, then loops receiving and scanning netlink headers until it finds matching pid/sequence acknowledgements or an answer. Attribute helpers append aligned payloads to the tail of an existing `nlmsghdr`.

State and persistence behavior: `struct rtnl_handle` owns the socket FD, protocol, local sockaddr, and increasing sequence. Receive buffers are heap allocated per response and handed to the caller only when an answer is requested. No persistent files are touched.

Dependencies and integration points: depends on Linux netlink/rtnetlink headers through `netlink_helpers.h`, standard sockets, and stderr/perror diagnostics. Used by tests that manipulate links, routes, qdiscs, or netdev state without shelling out.

Risks: some malformed netlink replies call `exit(1)`, which is acceptable for selftests but harsh for reusable library code. Extended ACK callback plumbing is declared but the default error printer ignores details. The returned answer buffer must be freed by callers. The `rtnl_talk` public wrapper always shows route errors except for sock diag suppression in the internal path.

Test signals: direct signals are negative errno returns or `-1` on open/send/malformed failures. Attribute helpers return `-1` if a message would exceed caller-provided bounds.
