# sources/distributed-fs/ceph-client/net/ipv4/tcp_ipv4.c

## Purpose

`tcp_ipv4.c` is the IPv4-specific TCP protocol binding. It connects the address-family-neutral TCP core to IPv4 routing, ICMP, hash tables, request sockets, TIME-WAIT sockets, reset/ACK generation, procfs/BPF iteration, and per-network-namespace TCP defaults. It exports the `tcp_prot` protocol object used by AF_INET stream sockets and supplies `ipv4_specific` callbacks used by `inet_connection_sock`.

The file is not specific to Ceph protocol semantics; within this source tree it is the kernel TCP transport substrate that any Ceph client TCP connection relies on.

## Important APIs, Types, and Functions

Key global state includes `struct inet_hashinfo tcp_hashinfo`, per-CPU IPv4 TCP control sockets in `ipv4_tcp_sk`, and `tcp_exit_batch_mutex` for serialized namespace teardown. `tcp_prot` is the central `struct proto` with socket operations such as `connect`, `recvmsg`, `sendmsg`, `backlog_rcv`, `hash`, and memory accounting hooks. `ipv4_specific` is the `inet_connection_sock_af_ops` table for IPv4 transmit, request creation, child socket creation, PMTU handling, and socket option handling.

Connection setup runs through `tcp_v4_pre_connect()` for cgroup/BPF connect checks and `tcp_v4_connect()` for AF_INET validation, source-route handling, route lookup, local address binding, SYN-SENT hashing, route rebinding after port selection, ISN/timestamp offset generation, Fast Open deferral, and final `tcp_connect()`.

Receive-side entry is `tcp_v4_rcv()`, which validates packet host type, TCP header length, checksum setup, socket lookup, request-socket migration, XFRM policy, TCP-AO/MD5/inbound hash checks, BPF/socket filters, TIME-WAIT handling, and dispatch to `tcp_v4_do_rcv()`. `tcp_v4_do_rcv()` is the socket-locked state dispatcher, using the established fast path, LISTEN cookie/request handling, `tcp_rcv_established()`, and `tcp_rcv_state_process()`.

Reset and ACK generation is handled by `tcp_v4_send_reset()`, `tcp_v4_send_ack()`, `tcp_v4_timewait_ack()`, and `tcp_v4_reqsk_send_ack()`. SYN-ACK output is `tcp_v4_send_synack()`. ICMP/error handling is centered on `tcp_v4_err()`, `tcp_v4_mtu_reduced()`, `tcp_req_err()`, and `tcp_ld_RTO_revert()`.

MD5 support under `CONFIG_TCP_MD5SIG` adds key lookup/add/delete/copy helpers, option parsing through `tcp_v4_parse_md5_keys()`, and hash construction through `tcp_v4_md5_hash_hdr()` and `tcp_v4_md5_hash_skb()`. TCP-AO hooks are integrated beside MD5 for reset and request ACK signing.

Observability APIs include procfs iterators for `/proc/net/tcp`, `tcp_seq_start()`, `tcp_seq_next()`, `tcp_seq_stop()`, and `tcp4_seq_show()`, plus BPF iterator support that batches sockets safely across listening and established hash buckets.

## Control Flow

Outgoing connect starts by checking address length and family, resolving source route options, performing `ip_route_connect()`, rejecting multicast/broadcast routes, updating the bind hash source address if necessary, clearing stale timestamp state if the destination changed, and moving the socket to `TCP_SYN_SENT`. The socket is then inserted through `inet_hash_connect()`, route ports are updated after ephemeral port selection, capabilities are installed from the route, sequence/timestamp offsets are seeded unless TCP repair owns them, and Fast Open or normal `tcp_connect()` sends the SYN. Failures unwind by returning to `TCP_CLOSE`, resetting bind source address, dropping the route, clearing route capabilities, and clearing `inet_dport`.

Incoming packets enter `tcp_v4_rcv()`. The function performs cheap validation first, then looks up established, listening, request, or TIME-WAIT sockets. `TCP_NEW_SYN_RECV` requests are protected by the listener, can migrate via reuseport, and then are completed via `tcp_check_req()`. Normal sockets pass minimum TTL, XFRM, TCP-AO/MD5 hash, filter, and callback-fill checks before either entering `tcp_v4_do_rcv()` immediately or being coalesced/queued by `tcp_add_backlog()` if owned by userspace. No-socket packets get RSTs when policy and checksum allow. TIME-WAIT packets call `tcp_timewait_state_process()` and may ACK, reset, accept a valid reopening SYN through a listener, or drop.

`tcp_add_backlog()` is an important congestion/memory side path: it validates checksum, tries to coalesce adjacent compatible backlog SKBs, updates sequence/ACK/timestamp metadata, and enforces a backlog memory limit derived from receive and send buffer sizes plus headroom.

## State and Persistence

Persistent runtime state is held in sockets, request sockets, TIME-WAIT sockets, route/dst cache references, and network namespace `ipv4` fields. `tcp_sk_init()` seeds per-net sysctls including ECN, MSS probing, keepalive, retries, TIME-WAIT reuse, SACK, timestamps, RACK, Fast Open, pacing, PLB, and RTO bounds. `tcp_set_hashinfo()` either assigns global `tcp_hashinfo` or allocates per-net hashinfo according to `sysctl_tcp_child_ehash_entries`.

Per-CPU control sockets are created in `tcp_v4_init()` and used for RST/ACK output outside normal socket context. These sockets temporarily inherit net namespace, mark, priority, XFRM policy, and transmit timing from the target socket. Namespace exit uses `tcp_sk_exit_batch()` to purge TIME-WAIT sockets, free per-net hashinfo, decrement death-row references, and destroy Fast Open context under `tcp_exit_batch_mutex`.

MD5/AO key material is socket-attached and RCU-managed. TIME-WAIT and request paths copy or derive enough authentication state to sign challenge ACKs, resets, and SYN-ACK/ACK responses after the full socket is unavailable.

## Dependencies and Integration Points

The file depends on IPv4 routing (`ip_route_connect`, `ip_queue_xmit`, `ip_send_unicast_reply`), inet hash tables, request sockets, TCP core input/output/timer APIs, XFRM policy, netfilter connection tracking reset, cgroup/BPF connect hooks, BPF socket filters and iterators, MPTCP reset options, PSP policy checks, TCP-AO, TCP-MD5, syncookies, Fast Open, procfs, and per-net namespace registration.

Important cross-file integrations in this subset include `tcp_timewait_state_process()` and `tcp_child_process()` from `tcp_minisocks.c`, cached route/metrics consumed by `tcp_metrics.c`, congestion-control setup for passive opens via `tcp_ca_openreq_child()`, and offload registration in `tcp_offload.c` feeding SKBs that eventually reach this receive path.

## Risks

Risk centers on concurrency and protocol edge cases. Socket lookup and request migration rely on correct reference handling across RCU, listener locks, bottom-half locks, and reuseport migration. TIME-WAIT reopening, syncookies, TCP Fast Open, TCP-AO, and MD5 all add special cases where missing a refcount, option validation, or key lookup can cause incorrect drops or unauthenticated responses. Reset/ACK output runs from per-CPU control sockets and must restore namespace/policy state accurately.

Path MTU and ICMP handling are sensitive to spoofing and sequence validation. `tcp_v4_err()` mitigates with established lookup, sequence-window checks, TCP-AO ICMP filtering, minimum TTL checks, and soft-vs-hard error rules. Backlog coalescing is performance-critical but must preserve flags, options, ECN/AccECN bits, timestamps, PSP metadata, and accounting.

## Test Signals

Useful signals include IPv4 connect success/failure paths, PMTU blackhole and ICMP FRAG_NEEDED behavior, ICMP unreachable handling in SYN-SENT and established states, TIME-WAIT reuse and reopening, syncookie accept, TCP Fast Open accept, MD5 and AO signed reset/ACK/SYN-ACK interoperability, `/proc/net/tcp` output under listening/established/TIME-WAIT/request sockets, BPF iterator traversal across hash buckets, namespace teardown with active TIME-WAIT sockets, packet drop reason counters, checksum error counters, backlog coalescing counters, and KASAN/KCSAN/lockdep coverage under concurrent accept/close/receive.
