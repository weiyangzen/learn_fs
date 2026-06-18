# sources/distributed-fs/ceph-client/net/ipv4/tcp.c

## Purpose

`tcp.c` is the address-family-neutral core of the Linux TCP implementation for this source tree. It provides socket lifecycle handling, stream send/receive paths, polling and ioctl behavior, TCP-level socket options, information export, authentication option dispatch, memory-pressure accounting, connection close/reset/disconnect handling, and global TCP initialization. IPv4 and IPv6 files provide family-specific connect, route, address, and hashing operations; this file owns the common stream semantics that `struct proto` operations and TCP submodules call.

The file is on multiple hot paths: every normal `sendmsg()`, `recvmsg()`, `poll()`, close, `setsockopt(SOL_TCP)`, `getsockopt(SOL_TCP)`, MD5/AO inbound authentication check, and TCP subsystem initialization reaches code here. It also contains optional support for zero-copy transmit, splice, receive zero-copy mmap, devmem/dmabuf receive cmsgs, TCP repair, Fast Open, TCP-AO/MD5 option handling, and BPF-observable state and sockopt behavior.

## Important APIs, Types, and Functions

Memory and initialization:

- Global state includes `tcp_sockets_allocated`, `tcp_orphan_count`, `tcp_tw_isn`, `sysctl_tcp_mem`, `tcp_memory_pressure`, `tcp_memory_per_cpu_fw_alloc`, and optional static keys such as `tcp_have_smc` and `tcp_tx_delay_enabled`.
- `tcp_enter_memory_pressure()` and `tcp_leave_memory_pressure()` maintain the advisory pressure flag and related MIB counters.
- `tcp_init_sock()` initializes `struct tcp_sock` and `struct inet_connection_sock`: retransmit/out-of-order trees, timers, RTO bounds, congestion control, buffer defaults, write-space callback, timestamp/RTT minima, xarray user-frag state, and zero-copy socket support.
- `tcp_init()` builds global hash tables and caches, initializes orphan monitoring, default TCP memory sysctls, TCPv4, metrics, Reno congestion control, TSQ work, and MPTCP.
- `tcp_struct_check()` enforces `struct tcp_sock` cacheline grouping assumptions at build time.

Send path:

- `tcp_sendmsg()` locks the socket and delegates to `tcp_sendmsg_locked()`.
- `tcp_sendmsg_locked()` handles cmsgs, `MSG_ZEROCOPY`, devmem binding, `MSG_SPLICE_PAGES`, Fast Open, connection wait, TCP repair send-queue handling, page-frag copying, skb coalescing, write-memory scheduling, push decisions, timestamp tagging, and error unwinding.
- `tcp_sendmsg_fastopen()`, `tcp_free_fastopen_req()`, and Fast Open branches integrate active TFO with deferred connect.
- `tcp_stream_alloc_skb()`, `sk_forced_mem_schedule()`, `tcp_wmem_schedule()`, and `tcp_remove_empty_skb()` are the local allocation/accounting helpers used to keep send progress possible and edge-triggered epoll behavior correct.
- `tcp_skb_entail()`, `tcp_push()`, `tcp_mark_push()`, `tcp_mark_urg()`, and `tcp_should_autocork()` attach data skbs to the write queue and decide when to push frames.
- `tcp_rate_check_app_limited()` marks delivery-rate samples as application-limited for congestion controls such as BBR.

Receive path:

- `tcp_recvmsg()` handles error-queue receives, optional busy polling, socket locking, and post-receive cmsg emission.
- `tcp_recvmsg_locked()` is the main byte-stream receive loop. It supports `MSG_PEEK`, `MSG_WAITALL`, urgent data gaps, FIN consumption, timestamp tracking, devmem skb cmsg receive with `MSG_SOCK_DEVMEM`, and normal copying from readable skbs.
- `tcp_recv_urg()` implements BSD-style out-of-band urgent receive semantics.
- `tcp_cleanup_rbuf()` and `__tcp_cleanup_rbuf()` decide whether reads require immediate ACK/window update.
- `tcp_recv_skb()`, `tcp_eat_recv_skb()`, `tcp_read_sock()`, `tcp_read_sock_noack()`, `tcp_read_skb()`, and `tcp_read_done()` expose nonblocking skb/actor receive helpers used by splice, kernel consumers, and internal data-drain paths.
- `tcp_splice_read()` and `tcp_splice_data_recv()` move socket data into pipes.
- Under `CONFIG_MMU`, `tcp_mmap()` and `tcp_zerocopy_receive()` implement `TCP_ZEROCOPY_RECEIVE` by mapping eligible receive pages into a user VMA with fallback copying and timestamp cmsg finalization.
- `tcp_recvmsg_dmabuf()` exports devmem-backed frags through `SO_DEVMEM_LINEAR` and `SO_DEVMEM_DMABUF` control messages and tracks user frag tokens in `sk_user_frags`.

State and lifecycle:

- `tcp_set_state()` centralizes TCP state transitions, BPF state callbacks, current-establishment counters, unhashing, and bind-port release on close.
- `tcp_shutdown()`, `tcp_close_state()`, and `new_state[]` implement send-side shutdown/FIN state movement.
- `__tcp_close()` and `tcp_close()` handle descriptor close, unread-data resets, linger aborts, FIN generation, orphaning, FIN_WAIT2 handling, OOM orphan cleanup, Fast Open request cleanup, and final destruction.
- `tcp_disconnect()` implements abort/disconnect semantics and resets a large set of per-connection fields so the socket can be reused.
- `tcp_done()` and `tcp_abort()` close sockets from protocol/BPF/control paths with correct timers, resets, listener/request/time-wait handling, and callbacks.
- `tcp_write_queue_purge()` and `tcp_rtx_queue_purge()` free write and retransmit queues and clear retransmit hints.

Socket options and user-visible information:

- `do_tcp_setsockopt()` handles SOL_TCP options including congestion control, ULP, Fast Open key/configuration, keepalive knobs, RTO/delack bounds, repair mode, queue sequence repair, `TCP_CORK`, `TCP_NODELAY`, quickack, AO/MD5 dispatch, timestamp repair, `TCP_NOTSENT_LOWAT`, `TCP_INQ`, and `TCP_TX_DELAY`.
- `tcp_setsockopt()` delegates non-SOL_TCP levels to the current AF ops.
- `do_tcp_getsockopt()` returns TCP integer options and structured options including `TCP_INFO`, `TCP_CC_INFO`, Fast Open keys, repair window/queue state, saved SYN data, `TCP_ZEROCOPY_RECEIVE`, TCP-AO key/info/repair state, MPTCP marker, RTO/delack values, and congestion/ULP names.
- `tcp_get_info()` fills `struct tcp_info` with state, RTT, retransmit, congestion, pacing, delivery-rate, ECN/AccECN, byte, segment, RTO, and listener backlog fields.
- `tcp_get_timestamping_opt_stats()` creates a netlink-attribute skb with optional timestamping stats such as pacing/delivery rate, cwnd, retransmits, bytes, EDT, TTL, and rehash counters.
- `tcp_poll()`, `tcp_ioctl()`, `tcp_peek_len()`, `tcp_set_rcvlowat()`, `tcp_set_rcvbuf()`, and helpers implement file/socket API behavior.

Authentication integration:

- `tcp_md5_destruct_sock()`, `tcp_md5_hash_skb_data()`, `tcp_md5_hash_key()`, and `tcp_inbound_md5_hash()` implement MD5 cleanup and validation when configured.
- `tcp_do_parse_auth_options()` parses TCP MD5 and TCP-AO options and rejects duplicate or malformed auth option combinations.
- `tcp_inbound_hash()` is the shared inbound authentication gate. It parses auth options, enforces AO/MD5 requirement policies, checks request-socket AO consistency, and dispatches to `tcp_inbound_ao_hash()` or `tcp_inbound_md5_hash()`.

## Control Flow

Initialization starts at `tcp_init()`: cacheline assertions run first, then counters/timers/hash tables/caches are set up, default memory sysctls are derived from available buffer pages, and dependent modules are initialized. Per-socket setup later happens through `tcp_init_sock()`, which establishes baseline sequence/control fields and binds congestion-control operations before data paths can execute.

The transmit path begins with `tcp_sendmsg()`, which serializes through the socket lock. `tcp_sendmsg_locked()` first parses cmsgs and zero-copy/devmem/splice choices, then handles active Fast Open or connect wait. The main loop either appends to the current write skb or allocates a new one, accounts memory, copies or attaches user data, advances `tp->write_seq` and skb `end_seq`, and pushes when the message is complete, the skb reaches `size_goal`, a forced push is needed, or memory wait requires flushing. Error paths remove empty skbs, drop zero-copy references correctly, and wake write-space waiters in the edge-triggered empty-queue case.

The receive path begins with `tcp_recvmsg()`. It can divert to error queue or busy loop before locking. `tcp_recvmsg_locked()` chooses either `tp->copied_seq` or a peek sequence, then walks the receive queue until it copies enough bytes, hits urgent data, sees FIN, encounters an error/shutdown/close, or must sleep for data. After copying it advances sequence state, updates peek offsets, records receive timestamps, frees fully consumed skbs, and calls `tcp_cleanup_rbuf()` to trigger ACK/window updates. Special branches handle urgent reads, repair queue peeks, devmem-backed skbs, and zero-copy receive via getsockopt.

Lifecycle control flows through state helpers. `tcp_set_state()` updates stats and hash membership before publishing the new state. `__tcp_close()` first shuts both directions, drains receive skbs, decides between reset, disconnect, or FIN based on unread data, repair, linger, and current state, waits for close if requested, then orphans the socket under BH locking and either destroys it or leaves it to protocol timers. `tcp_disconnect()` is a broader reset-to-reusable-state path: it emits resets where required, purges queues, clears timers, resets routing, congestion-control private state, sequence numbers, ECN/RACK/Fast Open state, and reports errors.

Socket option control flow is split between lockless simple setters/getters and locked operations. Options that affect live protocol state, queue state, AO/MD5 lists, Fast Open listener queues, or repair state take `sockopt_lock_sock()`. AF-specific options are delegated through `icsk_af_ops`, which keeps this file common across IPv4/IPv6.

Inbound authentication control begins in `tcp_inbound_hash()`. A malformed auth option drops early. Unsigned packets pass only if neither AO nor MD5 is required for the peer. Signed packets dispatch to AO or MD5 verifiers. Request sockets get an extra consistency check so a connection that negotiated AO cannot silently switch to unsigned.

## State and Persistence Behavior

Most persistent state is held in `struct tcp_sock`, `struct inet_connection_sock`, socket queues, and global/per-net sysctls. This file mutates durable per-connection fields including `write_seq`, `snd_nxt`, `snd_una`, `copied_seq`, `rcv_nxt`, congestion state, RTT estimators, receive window/clamp values, Fast Open pointers, repair settings, AO/MD5 pointers through delegated code, and many MIB/stat counters.

Memory pressure and orphan counts are global/per-CPU process state. `tcp_memory_pressure` is explicitly advisory and non-atomic in many paths; enter/leave uses compare-exchange/exchange to bound accounting. The orphan cache is periodically refreshed by `tcp_orphan_timer`, and close uses that cache plus memory usage to decide whether orphaned sockets must be reset.

Send and receive queues are persistent socket state. Sendmsg appends skbs and advances sequence state only after data is successfully copied or attached. Receive consumes skbs only when not peeking. Close/disconnect purges queues and frees or releases attached resources. Zero-copy receive persists user-visible page tokens in `sk_user_frags` until user code returns them through the broader devmem infrastructure.

TCP state is published through `inet_sk_state_store()` after close unhashing to avoid closed sockets remaining visible in hash tables. `tcp_set_state()` also maintains user-visible counters such as `TCP_MIB_CURRESTAB` and reset stats.

Socket options persist directly in socket fields: keepalive timing, `TCP_CORK`/`TCP_NODELAY` bits, `TCP_NOTSENT_LOWAT`, repair mode and queue, receive low-water, timestamps, user timeout, RTO/delack bounds, Fast Open flags, and congestion-control selection.

## Dependencies and Integration Points

Core dependencies include Linux socket, skb, proto memory, timer, xarray, pipe/splice, VM, cgroup BPF, BTF, tracepoint, random, crypto MD5, and net namespaces. Network-layer dependencies include `net/tcp.h`, `inet_connection_sock`, `inet_common`, IPv4/IPv6 AF callbacks, IP/ICMP, ECN/AccECN, MPTCP, SMC static key support, PSP enqueue metadata, devmem receive support, and RST reason tracing.

Major integration points:

- Socket file operations call `tcp_poll()`, `tcp_ioctl()`, `tcp_sendmsg()`, `tcp_recvmsg()`, `tcp_splice_read()`, `tcp_mmap()`, `tcp_close()`, `tcp_shutdown()`, `tcp_setsockopt()`, and `tcp_getsockopt()` through protocol/socket tables outside this file.
- Congestion controls receive delivery-rate/app-limited signals through fields updated here and can expose `TCP_CC_INFO` through `icsk_ca_ops->get_info`.
- BPF integrates through state callbacks, cgroup sockops timestamping, getsockopt bypass for `TCP_ZEROCOPY_RECEIVE`, and SOL_TCP sockopt hooks.
- TCP-AO and TCP-MD5 integrate with parsing, set/get option dispatch, cleanup, and inbound authentication.
- Fast Open, MPTCP, ULP, SMC, timestamping, devmem, and zero-copy all depend on feature-specific helpers and compile-time configuration.
- `tcp_init()` is a global subsystem entry and must run before normal TCP socket allocation.

## Risks and Edge Cases

- The send and receive loops are dense hot-path code with many optional branches. Reordering sequence advancement, memory accounting, or skb unlinking can cause data corruption, stuck epoll waiters, leaks, or protocol-visible sequence gaps.
- `tcp_sendmsg_locked()` has delicate unwinding for zero-copy `ubuf_info`, devmem bindings, pure zero-copy skb downgrade, and partially allocated empty skbs. Bugs here can leak pins/references or return success after data was not queued.
- `tcp_recvmsg_locked()` must preserve byte-stream semantics across `MSG_PEEK`, urgent data, FIN, devmem skbs, and timestamp cmsgs. Incorrect `copied_seq` or peek-offset updates can duplicate or skip bytes.
- `tcp_zerocopy_receive()` touches VMAs under either RCU VMA locking or mmap read lock, speculatively inserts pages, may zap ranges, and rolls back partial failures. It is sensitive to alignment, VMA identity, page eligibility, and timestamp side effects.
- Close/disconnect code mixes process context, BH locking, orphan accounting, timers, and protocol state. Race mistakes can double-destroy sockets, leave hash entries, or emit incorrect resets.
- TCP-AO and MD5 must not both appear on a segment. The parser and inbound gate are security-sensitive; permissive changes can allow unsigned packets on protected flows.
- Lockless `READ_ONCE()` snapshots in `tcp_get_info()`, poll, and stats are intentionally best effort. They must not be treated as strongly consistent.
- `tcp_struct_check()` means structure layout changes can break builds when hot cacheline group assumptions change.

## Test Signals

Useful validation signals in this tree include:

- Kernel networking selftests that exercise TCP-AO live behavior and sockopts under `sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/`.
- BPF sockopt tests under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/`, including coverage for `TCP_CONGESTION` and `TCP_ZEROCOPY_RECEIVE`.
- Driver/net devmem selftest code such as `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ncdevmem.c`, which uses `MSG_SOCK_DEVMEM`.
- Build coverage with `CONFIG_TCP_AO`, `CONFIG_TCP_MD5SIG`, `CONFIG_MMU`, `CONFIG_BPF`, `CONFIG_TCP_CONG_BBR`, and devmem-related options catches many compile-time branches.
- Runtime smoke signals include `TCP_INFO`, `TCP_CC_INFO`, `ss -ti`/inet_diag output, TCP MIB counters for memory pressure/aborts/auth failures, tracepoints such as TCP AO/MD5 hash events, and packet captures for FIN/RST/AO/MD5 option behavior.
