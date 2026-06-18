# sources/distributed-fs/ceph-client/net/ipv4/syncookies.c

## Purpose

This file implements IPv4 TCP SYN cookie generation and validation. It allows a listening TCP socket to complete a handshake without retaining the original SYN request when the SYN queue recently overflowed. The code encodes the peer tuple, time window, selected MSS index, and selected TCP options into the SYN-ACK sequence number and, when timestamps are available, low bits of the echoed timestamp.

## Important APIs, Types, and Functions

- `syncookie_secret[2]`: lazily initialized siphash keys used by `cookie_hash()`.
- `cookie_init_timestamp()`: encodes window scaling, SACK, and ECN option state into low timestamp bits while keeping the initial timestamp no greater than the current TCP timestamp.
- `secure_tcp_syn_cookie()` and `check_tcp_syn_cookie()`: core cookie encode/decode logic. They combine tuple hash, client sequence number, minute counter, and 24-bit data field.
- `msstab[]`: sorted MSS encoding table with four common MSS values.
- `__cookie_v4_init_sequence()` / `cookie_v4_init_sequence()`: generate IPv4 SYN cookie sequence numbers and round the advertised MSS down to the encoded MSS bucket.
- `__cookie_v4_check()`: validates ACK sequence number and returns decoded MSS or 0.
- `cookie_timestamp_decode()`: restores timestamp-carried TCP options while enforcing current sysctl policy for timestamps, SACK, and window scaling.
- `cookie_tcp_reqsk_init()` and `cookie_tcp_reqsk_alloc()`: reconstruct `request_sock` state from the ACK and decoded options.
- `cookie_tcp_check()`: validates syncookie, parses TCP options, handles timestamp offsets, and allocates a rebuilt request.
- `cookie_v4_check()`: top-level IPv4 listener path that validates syncookie ACKs, runs security hooks, computes route/window state, and creates the child socket.
- `tcp_get_cookie_sock()`: invokes the address-family `syn_recv_sock()` callback and attaches the rebuilt request/child socket.
- Optional BPF path: `cookie_bpf_check()` uses an already attached BPF-created request sock when `CONFIG_BPF` support is enabled.

## Control Flow

Cookie creation happens during SYN-ACK construction. `__cookie_v4_init_sequence()` chooses the largest `msstab` entry not exceeding the original MSS, stores the table index as the data payload, and returns a sequence number from `secure_tcp_syn_cookie()`. If timestamps are used, `cookie_init_timestamp()` stores option bits in the low six timestamp bits.

Cookie validation starts in `cookie_v4_check()` for a listener receiving an ACK. It first checks that syncookies are enabled and the packet is an ACK without RST. The BPF cookie path is used when available; otherwise `cookie_tcp_check()` rejects packets if the SYN queue has not recently overflowed, validates the sequence cookie through `__cookie_v4_check()`, counts success/failure stats, parses options, subtracts the secure timestamp offset if present, decodes timestamp-carried options, and allocates a reconstructed request.

After a request exists, `cookie_v4_check()` fills IPv4 local/remote addresses, saves IP options, invokes LSM request hooks, applies TCP-AO syncookie handling, performs an IPv4 route lookup to recover dst metrics, recomputes the initial receive window, checks ECN/AccECN eligibility, and calls `tcp_get_cookie_sock()` to create the established child socket. On failure it frees the request or drops the skb with a specific drop reason.

## State and Persistence Behavior

The design intentionally avoids retaining per-SYN state. Persistent state is limited to process lifetime secrets, minute-granularity cookie time, TCP listener/sysctl configuration, network statistics, route metrics looked up at ACK time, and reconstructed `request_sock` / child socket state after successful validation. Timestamp option encoding preserves only a compact subset of the original SYN options: send window scale, SACK permission, ECN, and the fact that timestamps were negotiated.

## Dependencies and Integration Points

The file depends on TCP core request-socket and option parsing code, IPv4 headers and route lookup, siphash secure sequence helpers, TCP ECN helpers, MPTCP request allocation when enabled, TCP-AO syncookie handling, BPF kfunc integration, LSM hooks, dst metrics, and per-net IPv4 TCP sysctls. The route lookup integration is important because the original SYN dst was discarded and the child socket still needs a valid route and metric-derived receive window.

## Risks and Edge Cases

- The cookie data field is only 24 bits after the count, so MSS and options are intentionally lossy; adding options requires careful encoding compatibility.
- `MAX_SYNCOOKIE_AGE` and minute counter arithmetic decide acceptance windows; off-by-one errors can admit stale cookies or reject valid ACKs.
- Timestamp option decoding must reject options disabled after the SYN-ACK, especially SACK, timestamps, and window scaling.
- The ACK is trusted only after cookie validation; route lookup, LSM hooks, TCP-AO, MPTCP, and BPF-created request paths each have distinct cleanup paths.
- `tcp_synq_no_recent_overflow()` prevents accepting cookies when the listener is not under recent pressure; changing this condition affects spoofing exposure and normal handshakes.
- Recomputed window and ECN state may differ from the original SYN path because no original request state is retained.

## Test Signals

Useful coverage includes SYN flood tests with `tcp_syncookies` enabled, valid/invalid/stale cookie ACK validation, MSS bucket round-down behavior, timestamp option restoration for SACK/window-scale/ECN, sysctl toggles between SYN-ACK and ACK, listener route lookup failure, LSM rejection, TCP-AO and MPTCP enabled paths, BPF syncookie request paths, and stats updates for `SYNCOOKIESRECV` and `SYNCOOKIESFAILED`.
