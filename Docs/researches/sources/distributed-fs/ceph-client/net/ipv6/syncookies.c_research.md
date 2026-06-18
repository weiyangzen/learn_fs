# sources/distributed-fs/ceph-client/net/ipv6/syncookies.c

## Purpose
`syncookies.c` implements IPv6 TCP SYN cookie generation and validation. It lets a listening TCPv6 socket reconstruct enough request state from an ACK when the SYN queue overflowed, avoiding allocation on the initial SYN under pressure.

## Important APIs, types, and functions
`syncookie6_secret[2]` stores lazily initialized siphash keys. `msstab[]` maps the encoded MSS index to IPv6-appropriate MSS values. `cookie_hash()`, `secure_tcp_syn_cookie()`, and `check_tcp_syn_cookie()` create and validate the 32-bit cookie using source/destination IPv6 addresses, TCP ports, peer initial sequence, time counter, and small encoded data field. Public helpers include `__cookie_v6_init_sequence()`, `cookie_v6_init_sequence()`, `__cookie_v6_check()`, and `cookie_v6_check()`. `cookie_tcp_check()` reconstructs a `request_sock` from a valid cookie and TCP options.

## Control flow
When syncookies are needed, `__cookie_v6_init_sequence()` selects the largest supported MSS not greater than the offered MSS, rewrites the caller's MSS to that table value, and returns a secure sequence value. Later, an ACK is checked by subtracting the base hash and peer sequence, validating cookie age against `MAX_SYNCOOKIE_AGE`, and extracting the MSS index.

`cookie_v6_check()` is called on a listening socket path for non-RST ACKs when sysctl syncookies are enabled. It either delegates to a BPF cookie checker or uses `cookie_tcp_check()`. The checker rejects sockets without recent overflow, invalid cookies, failed timestamp-cookie decoding, or failed request allocation. On success it fills IPv6 remote/local addresses, runs the LSM `security_inet_conn_request()` hook, preserves packet options when the listener requested them, initializes window scaling and receive space, routes the request through `tcp_v6_syn_recv_sock()`, and returns either the created child socket, the original listener, or a drop path.

## State and persistence
The only local persistent state is the static random siphash secret array. Cookies encode transient time and MSS index but store no per-connection server memory until the final ACK. Reconstructed request state is allocated only after validation and follows normal TCP request/child socket lifetimes. Statistics are updated through `LINUX_MIB_SYNCOOKIESFAILED` and `LINUX_MIB_SYNCOOKIESRECV`.

## Dependencies and integration points
This file integrates with TCP option parsing, timestamp cookie decoding, BPF syncookie hooks, TCPv6 request socket ops, secure IPv6 sequence helpers, IPv6 packet option preservation, LSM connection-request hooks, route/child socket creation, and the IPv4 `net->ipv4.sysctl_tcp_syncookies` sysctl used by shared TCP code.

## Risks and edge cases
The MSS table must remain sorted and encodeable within `COOKIEBITS`. Cookie validation depends on using the exact same address/port/sequence tuple and time window. Timestamp offset adjustment must match `secure_tcpv6_seq_and_ts_off()` or timestamp cookies will fail. The path must not create sockets when the listener did not recently overflow, otherwise syncookies would weaken normal TCP semantics. Packet options are retained by taking an skb reference, so error paths must free reconstructed request state correctly.

## Test signals
Tests should force SYN queue overflow on TCPv6 listeners, verify valid ACKs create children, invalid cookies increment failure stats, stale cookies are rejected, MSS selection matches the table, timestamp and non-timestamp clients work, BPF syncookie hooks can accept or reject, packet options are preserved for interested sockets, LSM rejection frees the request, and syncookie handling is skipped when the sysctl is disabled or the packet is RST.
