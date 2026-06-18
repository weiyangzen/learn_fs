# subset-b-006204 TCP IPv4 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ao.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_ao.c

## Purpose

`tcp_ao.c` implements TCP Authentication Option support for this tree, following RFC 5925/5926. It manages Master Key Tuples, derives per-connection traffic keys, signs outgoing TCP segments, validates incoming AO MACs, handles AO across SYN/listen/request/established/time-wait states, exposes AO socket options, and supports repair/checkpoint restore of AO sequence-number-extension state.

Although located under `net/ipv4`, the file also contains common AO logic and conditional IPv6 handling. IPv4-specific wrappers are exported here; IPv6-specific operations are delegated when `CONFIG_IPV6` is enabled. It is tightly integrated with the common TCP auth parser and inbound gate in `tcp.c`, AF-specific TCP operations, `include/net/tcp_ao.h`, crypto ahash sigpools, tracepoints, and AO selftests.

## Important APIs, Types, and Functions

Global and lookup state:

- `DEFINE_STATIC_KEY_DEFERRED_FALSE(tcp_ao_needed, HZ)` enables fast-path elision when no AO sockets exist.
- `struct tcp_ao_info` stores a socket's MKT hlist, current send key, receive-next key, counters, local/remote ISNs, SNE values, `ao_required`, `accept_icmps`, and refcount.
- `struct tcp_ao_key` stores peer match criteria, key material, digest/MAC lengths, send/receive IDs, VRF index, cached traffic keys, sigpool ID, counters, and RCU node.
- `tcp_ao_do_lookup()`, `__tcp_ao_do_lookup()`, `tcp_ao_established_key()`, `tcp_v4_ao_lookup()`, and `tcp_v4_ao_lookup_rsk()` find matching MKTs by address family, prefix, l3index, sndid, and rcvid.
- `tcp_ao_key_cmp()` and `__tcp_ao_key_cmp()` implement address/prefix/ID/interface matching, including IPv4-mapped IPv6 address handling.

Key lifecycle:

- `tcp_ao_alloc_info()`, `tcp_ao_key_alloc()`, `tcp_ao_link_mkt()`, `tcp_ao_copy_key()`, `tcp_ao_key_free_rcu()`, `tcp_ao_info_free()`, and `tcp_ao_destroy_sock()` allocate, link, copy, RCU-free, and destroy AO state.
- `tcp_ao_time_wait()` transfers AO info into a time-wait socket by refcounting AO info and moving memory accounting out of the full socket.
- `tcp_ao_copy_all_matching()` clones matching keys from a listener to an accepted child socket and caches child traffic keys.
- `tcp_ao_delete_key()` and `tcp_ao_del_cmd()` remove MKTs, with special async delete support for listeners and strict current/rnext safety for established sockets.

Cryptography and packet authentication:

- `tcp_ao_calc_traffic_key()` performs the KDF hash operation over a context block using the MKT key.
- `tcp_v4_ao_calc_key()`, `tcp_v4_ao_calc_key_sk()`, `tcp_v4_ao_calc_key_rsk()`, `tcp_v4_ao_calc_key_skb()`, and common wrappers derive traffic keys from 4-tuples and initial sequence numbers.
- `tcp_ao_hash_sne()`, `tcp_v4_ao_hash_pseudoheader()`, `tcp_ao_hash_pseudoheader()`, `tcp_ao_hash_header()`, `tcp_ao_hash_hdr()`, and `tcp_ao_hash_skb()` compute AO MACs over SNE, pseudoheader, TCP header/options, and payload.
- `tcp_v4_ao_hash_skb()` and `tcp_v4_ao_synack_hash()` are IPv4 exports used by AF-specific transmit/SYNACK paths.
- `tcp_ao_compute_sne()` calculates sequence-number extension changes across 32-bit sequence wrap.
- `tcp_ao_transmit_skb()` fills the AO MAC on outgoing skbs, deriving temporary SYN traffic keys when necessary.
- `tcp_inbound_ao_hash()` and `tcp_ao_verify_hash()` validate incoming AO packets, update counters, handle established fast path, listen/request/SYN states, syncookie inference, and key-rotation `RNext` requests.
- `tcp_ao_prepare_reset()` prepares key and traffic-key material for authenticated RST generation.

Connection lifecycle hooks:

- `tcp_ao_connect_init()` prunes non-matching keys on active connect, selects current/rnext keys, expands TCP header length, and records local ISN.
- `tcp_ao_established()` caches traffic keys for all keys after establishment.
- `tcp_ao_finish_connect()` records remote ISN and caches keys for active opens.
- `tcp_ao_syncookie()` records AO key IDs in a request sock when a SYN with AO is handled through syncookies.
- `tcp_ao_ignore_icmp()` implements RFC-required default ICMP hard-error suppression for synchronized AO-protected sockets unless `accept_icmps` is set.

Socket option surface:

- `tcp_v4_parse_ao()` and `tcp_parse_ao()` dispatch `TCP_AO_ADD_KEY`, `TCP_AO_DEL_KEY`, and `TCP_AO_INFO`.
- `tcp_ao_add_cmd()` validates user add-key structures, address/prefix/family/interface constraints, MD5 conflicts, duplicate overlapping IDs, cryptographic algorithm settings, and first-use static-key activation.
- `tcp_ao_parse_crypto()` validates algorithm/key/MAC sizes, handles RFC 5926 `cmac(aes128)` KDF normalization, initializes sigpool crypto, and enforces option-space limits.
- `tcp_ao_info_cmd()` sets AO-required/ICMP policy, counters, current key, and rnext key.
- `tcp_ao_get_mkts()`, `tcp_ao_copy_mkts_to_user()`, and `tcp_ao_get_sock_info()` implement `TCP_AO_GET_KEYS` and `TCP_AO_INFO` getsockopt output.
- `tcp_ao_set_repair()` and `tcp_ao_get_repair()` allow repair mode to restore/read ISNs and SNEs and then recache traffic keys.

## Control Flow

Adding AO starts through `tcp_v4_parse_ao()` from TCP setsockopt dispatch. `tcp_ao_add_cmd()` copies the extensible user structure, validates address family and prefix, optional l3 master device binding, key flags, MD5 incompatibility, and duplicate overlapping key IDs. It then allocates a key and crypto sigpool, parses the cryptographic settings, optionally derives traffic keys immediately for established sockets, links the key into `ao_info`, activates `tcp_ao_needed` on first AO use, disables GSO for the socket, and optionally updates current/rnext pointers.

Active open uses `tcp_ao_connect_init()`: when the peer address is known, keys that do not match the peer are removed, a matching key is selected, AO option length is added to the TCP header length, local ISN is recorded, and SNE starts at zero. When the connection finishes, `tcp_ao_finish_connect()` records the remote ISN and caches send/receive traffic keys. Passive open uses `tcp_ao_syncookie()` and `tcp_ao_copy_all_matching()` to propagate AO negotiation from listener/request to child, clone matching MKTs, set current/rnext keys from request-sock IDs when possible, cache traffic keys, and attach AO info to the new socket.

Transmit flow enters `tcp_ao_transmit_skb()` from TCP output option construction. For non-SYN established packets it uses cached send traffic keys. For initial SYN it derives a temporary traffic key because the peer ISN is not known; for SYNACK it derives using local and remote ISNs. It computes SNE from `ao->snd_sne`, `tp->snd_una`, and the segment sequence, then calls the AF-specific AO hash callback to write the MAC.

Inbound flow is called from `tcp_inbound_hash()` in `tcp.c` after TCP option parsing. `tcp_inbound_ao_hash()` first ensures AO info exists, then uses a fast path for established states: the expected rnext key is tried first, fallback lookup uses the packet keyid, cached receive traffic key is used, and successful verification may rotate `current_key` if peer requests a new `RNext`. Non-established paths look up a key by peer address/keyid, infer ISNs and SNE from SYN/SYNACK/request/syncookie state, derive a temporary traffic key, and verify the MAC. Failures increment MIB, AO-info, and key counters and return precise skb drop reasons.

Deleting AO keys uses `tcp_ao_del_cmd()`, which finds a key by exact address/prefix/family/sndid/rcvid/interface properties. Established sockets cannot remove a key that remains current or rnext unless replacement pointers are provided. Synchronous deletion unlinks, waits for an RCU grace period, updates current/rnext, and only frees if the removed key is no longer referenced. Listener async delete avoids current/rnext handling and frees after RCU.

Getsockopt flow for keys uses an extensible first-entry filter. `tcp_ao_copy_mkts_to_user()` validates user structure size/version, address filter, `get_all`, current/rnext filters, and output capacity. It copies matching key metadata, counters, key material, and algorithm names back to the user array and writes the matched count into entry zero.

## State and Persistence Behavior

AO state persists per socket in `tcp_sock->ao_info` or per time-wait socket in `tcp_timewait_sock->ao_info`. `ao_info` is refcounted when shared with time-wait state. Keys are stored in an RCU-protected hlist and may remain alive after unlink until readers finish. Key material is freed with `kfree_sensitive()`.

Cached traffic keys persist inside each `tcp_ao_key`: send and receive traffic-key buffers are allocated as digest-size trailing storage after the key object. `tcp_ao_cache_traffic_keys()` refreshes both directions whenever ISNs/SNE repair state changes or a connection becomes established.

Counters persist in both `tcp_ao_info` and individual keys via atomics: good packets, bad packets, key-not-found, AO-required drops, and dropped ICMPs. The `TCP_AO_INFO` setsockopt can overwrite counters when requested, which supports restore/testing.

`current_key` controls outbound send ID; `rnext_key` controls the receive key ID requested from the peer. Incoming `RNext` values can rotate `current_key` dynamically when a matching key exists. These pointers are updated with `WRITE_ONCE()` and coordinated with RCU deletion.

AO policy persists in `ao_required` and `accept_icmps`. `ao_required` makes unsigned segments unacceptable for matching peers and is rejected if MD5 keys already exist on the socket. `accept_icmps` flips the RFC-default behavior of ignoring selected hard ICMP errors on synchronized AO connections.

SNE state (`snd_sne`, `rcv_sne`) and local/remote ISNs (`lisn`, `risn`) persist in `ao_info` and are exposed/restorable through `TCP_AO_REPAIR` while TCP repair mode is enabled.

## Dependencies and Integration Points

The file depends on `include/net/tcp_ao.h`, `net/tcp.h`, Linux TCP UAPI structures in `include/linux/tcp.h`, crypto ahash APIs, `tcp_sigpool`, RCU, socket memory accounting, l3mdev/VRF helpers, IPv4/IPv6 address helpers, TCP tracepoints, MIB counters, and skb drop reasons.

Integration points:

- `tcp.c` dispatches AO socket options, parses auth options, checks whether AO is required, and calls `tcp_inbound_ao_hash()`.
- TCP output paths use `tcp_ao_transmit_skb()` and AF-specific callbacks to fill AO options.
- AF-specific operation tables provide AO lookup, key derivation, and hash callbacks for IPv4 and IPv6.
- Request-socket and syncookie paths store AO negotiation fields such as `used_tcp_ao`, `ao_keyid`, and `ao_rcv_next`.
- Time-wait code calls `tcp_ao_time_wait()` and later `tcp_ao_destroy_sock()`.
- TCP repair uses `tcp_ao_set_repair()`/`tcp_ao_get_repair()` through TCP sockopts.
- MD5 integration is intentionally exclusive for overlapping peers; add-key and AO-required validation call MD5 lookup helpers to enforce this.

## Risks and Edge Cases

- AO is security-sensitive. Any mismatch in KDF context ordering, ISN direction, SNE computation, pseudoheader choice, option exclusion, or MAC offset can either drop valid traffic or accept forged traffic.
- SNE wrap logic is compact and sequence-number comparisons are subtle. Bugs around wrap or RST preparation could invalidate long-lived high-throughput flows.
- Key deletion is race-prone. Established fast paths read current/rnext and key lists under RCU; deletion must not free a key that an RX path has just selected or that current/rnext still references.
- `tcp_ao_prepare_reset()` has an unavoidable limitation when no socket exists: initial sequence numbers are unknown, so authenticated reset cannot be built. That behavior is deliberate and must remain conservative.
- Listener async deletion and child-key cloning can diverge if a key disappears between SYN validation and accept. The code rejects child creation if the negotiated AO status cannot be preserved.
- AO and MD5 conflict checks must stay aligned with lookup semantics across VRFs/l3index and IPv4-mapped IPv6 addresses.
- User structure handling is extensible and strict about reserved/trailing bytes. Relaxing checks can break forward/backward compatibility or leak uninitialized data.
- MAC length and TCP option-space validation affect interoperability with SACK/timestamp/window-scale options; increasing defaults can make SYN or established options exceed `MAX_TCP_OPTION_SPACE`.
- GSO is disabled when AO is attached. Changes to this behavior require careful validation of per-segment MAC correctness.

## Test Signals

Strong local test signals exist under `sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/`, including add/delete/set/get key behavior, closed-socket setup, self-connect, resets, ICMP discard policy, and lookup benchmarking. These should be run with `CONFIG_TCP_AO`, relevant crypto algorithms, IPv4 and IPv6 where applicable, and VRF/l3mdev coverage when changing match logic.

Additional validation signals include TCP MIB counters `LINUX_MIB_TCPAOGOOD`, `TCPAOBAD`, `TCPAOKEYNOTFOUND`, `TCPAODROPPEDICMPS`; tracepoints for AO mismatch, wrong MAC length, key-not-found, `RNext` request, and handshake failure; packet captures showing AO keyid/rnext/MAC lengths; and repair-mode tests that restore ISNs/SNEs and verify traffic continues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_ao.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bbr.c -->
# sources/distributed-fs/ceph-client/net/ipv4/tcp_bbr.c

## Purpose

`tcp_bbr.c` implements the BBR congestion-control module. BBR models the path using recent bottleneck bandwidth and minimum RTT rather than directly treating loss or delay as the primary congestion signal. On ACKs it updates its model, sets pacing rate, and sets congestion window. It registers as the `"bbr"` TCP congestion algorithm and exposes selected callbacks as BPF struct-ops kfuncs.

The implementation is the classic BBR mode machine: `STARTUP` rapidly probes for bandwidth, `DRAIN` removes startup queue, `PROBE_BW` cycles pacing gain to share/probe bandwidth, and `PROBE_RTT` periodically caps inflight to refresh the min-RTT estimate. It also includes long-term bandwidth sampling for policer detection and ACK aggregation compensation.

## Important APIs, Types, and Functions

Core state and constants:

- `enum bbr_mode` defines `BBR_STARTUP`, `BBR_DRAIN`, `BBR_PROBE_BW`, and `BBR_PROBE_RTT`.
- `struct bbr` is stored in `inet_csk_ca(sk)` and tracks min RTT, max bandwidth filter, round counting, mode, recovery state, gain cycle, long-term bandwidth sampling, full-pipe detection, prior cwnd, and ACK aggregation windows.
- Constants define bandwidth/rate scaling (`BW_SCALE`, `BW_UNIT`, `BBR_SCALE`, `BBR_UNIT`), gain values, min RTT window, PROBE_RTT duration, min TSO behavior, cwnd floor, full-bandwidth threshold, policer thresholds, and ACK aggregation clamps.

Rate, pacing, and cwnd helpers:

- `bbr_max_bw()`, `bbr_bw()`, and `bbr_full_bw_reached()` expose the current bandwidth model, using long-term bandwidth when policer mode is active.
- `bbr_rate_bytes_per_sec()` and `bbr_bw_to_pacing_rate()` convert BBR packet-per-usec bandwidth estimates into byte-per-second pacing rates with gain and a pacing margin.
- `bbr_init_pacing_rate_from_rtt()` seeds pacing from initial cwnd and SRTT/default RTT.
- `bbr_set_pacing_rate()` updates `sk_pacing_rate`, allowing increases before full bandwidth is reached and normal gain-driven changes afterward.
- `bbr_min_tso_segs()` and `bbr_tso_segs_goal()` choose TSO sizing from pacing rate.
- `bbr_bdp()`, `bbr_quantization_budget()`, `bbr_inflight()`, and `bbr_packets_in_net_at_edt()` estimate BDP/cwnd/inflight targets and account for packets already scheduled by EDT pacing.
- `bbr_ack_aggregation_cwnd()` and `bbr_update_ack_aggregation()` add bounded cwnd allowance for ACK aggregation.
- `bbr_set_cwnd_to_recover_or_restore()` and `bbr_set_cwnd()` implement recovery packet conservation, loss adjustment, slow-start toward target, cwnd restoration, global clamp enforcement, and PROBE_RTT cwnd cap.

Mode and model updates:

- `bbr_update_bw()` consumes `struct rate_sample`, advances packet-timed rounds, updates long-term policer sampling, and refreshes the windowed max bandwidth filter.
- `bbr_lt_bw_sampling()`, `bbr_lt_bw_interval_done()`, `bbr_reset_lt_bw_sampling()`, and `bbr_reset_lt_bw_sampling_interval()` detect token-bucket policers and temporarily pace at a long-term rate.
- `bbr_check_full_bw_reached()` determines when STARTUP has likely filled the pipe.
- `bbr_check_drain()` moves STARTUP to DRAIN and DRAIN to PROBE_BW when inflight has drained to target.
- `bbr_is_next_cycle_phase()`, `bbr_advance_cycle_phase()`, `bbr_update_cycle_phase()`, and `bbr_reset_probe_bw_mode()` implement PROBE_BW gain cycling.
- `bbr_update_min_rtt()` refreshes min RTT, enters/exits PROBE_RTT, marks low-rate samples app-limited, and clears idle restart.
- `bbr_update_gains()` maps mode to pacing/cwnd gain.
- `bbr_update_model()` runs the full ACK-time model pipeline.

Congestion-control callbacks and registration:

- `bbr_main()` is the `cong_control` callback; it updates the model, pacing rate, and cwnd on ACK processing.
- `bbr_init()` initializes per-flow BBR state and requests pacing.
- `bbr_cwnd_event_tx_start()` handles idle restart, resets ACK aggregation epoch, and refreshes pacing or PROBE_RTT completion.
- `bbr_sndbuf_expand()`, `bbr_undo_cwnd()`, `bbr_ssthresh()`, and `bbr_set_state()` implement TCP congestion-control callbacks for send-buffer sizing, undo, loss recovery threshold, and state changes.
- `bbr_get_info()` exposes `INET_DIAG_BBRINFO` fields: bandwidth, min RTT, pacing gain, and cwnd gain.
- `tcp_bbr_cong_ops` registers the algorithm name `"bbr"` and its callbacks.
- BTF kfunc registration exposes BBR callbacks to `BPF_PROG_TYPE_STRUCT_OPS`; `bbr_register()` registers both kfunc IDs and congestion control, and `bbr_unregister()` unregisters the congestion control module.

## Control Flow

When a socket selects BBR, `bbr_init()` clears the private control block, sets infinite ssthresh, initializes RTT/bandwidth filters and round counters, seeds pacing rate, resets long-term sampling, enters STARTUP, clears ACK aggregation state, and moves `sk_pacing_status` to `SK_PACING_NEEDED` if no pacing was active.

ACK processing calls `bbr_main()`. The control flow is deliberately staged: `bbr_update_model()` updates bandwidth, ACK aggregation, gain-cycle phase, full-pipe state, drain transition, min RTT/PROBE_RTT state, and mode gains. Then `bbr_main()` reads the selected bandwidth estimate, updates `sk_pacing_rate` with the current pacing gain, and updates cwnd using the current cwnd gain and ACKed packet count.

The STARTUP path uses high pacing/cwnd gain while bandwidth grows. `bbr_check_full_bw_reached()` watches non-app-limited packet-timed rounds; when bandwidth fails to grow by 25 percent for three rounds, `full_bw_reached` is set. `bbr_check_drain()` then enters DRAIN with inverse high gain and sets ssthresh to estimated BDP. Once packets in network fall to the unit-gain inflight target, BBR enters PROBE_BW.

The PROBE_BW path cycles through an eight-phase pacing-gain array. A high-gain phase attempts to increase inflight to probe for more bandwidth; a low-gain phase drains; the rest cruise at unit gain. Phase advancement depends on elapsed min RTT and, for non-unit gains, inflight relative to target and loss.

The PROBE_RTT path starts when the min-RTT filter expires and the flow is not idle-restarting. It saves prior cwnd, caps cwnd to four packets, marks samples app-limited, waits for at least 200 ms and a packet-timed round at low inflight, then restores cwnd and returns to STARTUP or PROBE_BW depending on whether full bandwidth had been reached.

Long-term policer detection starts only after loss. It samples delivered/lost packets over bounded round intervals, requires high loss ratio and consistent measured rates across intervals, then sets `lt_use_bw` so `bbr_bw()` uses `lt_bw` and PROBE_BW pacing gain becomes unit gain. After a fixed number of rounds, it resets policer mode and restarts gain cycling.

Loss recovery is handled as an overlay rather than a primary mode. `bbr_set_cwnd_to_recover_or_restore()` reduces cwnd by observed losses, applies packet conservation on the first recovery round, then restores the saved cwnd when recovery exits. `bbr_set_state()` treats RTO loss as a round boundary and feeds long-term sampling.

## State and Persistence Behavior

All BBR per-connection state persists in the congestion-control private area (`ICSK_CA_PRIV_SIZE`) as `struct bbr`. It is initialized once per algorithm selection and updated on ACKs, TX-start events, and TCP CA state transitions.

The key persistent model fields are:

- `bw`: windowed max delivery-rate filter over roughly ten packet-timed rounds.
- `min_rtt_us` and `min_rtt_stamp`: min RTT and freshness window.
- `mode`, `pacing_gain`, `cwnd_gain`, and `cycle_idx`: current mode and gain-cycle state.
- `rtt_cnt`, `next_rtt_delivered`, and `round_start`: packet-timed round tracking.
- `full_bw`, `full_bw_cnt`, and `full_bw_reached`: STARTUP exit detection.
- `lt_*`: long-term policer sampling and selected long-term bandwidth.
- `prior_cwnd`, `prev_ca_state`, and `packet_conservation`: recovery overlay state.
- `ack_epoch_*` and `extra_acked[]`: ACK aggregation window state.

BBR also persists effects into generic TCP/socket fields: `sk_pacing_rate`, `sk_pacing_status`, `tp->snd_ssthresh`, `tp->snd_cwnd`, `tp->app_limited`, and TCP delivery/loss counters consumed from `struct tcp_sock`.

There is no on-disk persistence. Module registration persists globally until module unload or kernel shutdown. BTF kfunc IDs persist while the module is loaded.

## Dependencies and Integration Points

BBR depends on generic TCP congestion-control infrastructure (`struct tcp_congestion_ops`, `tcp_register_congestion_control()`), TCP delivery-rate sampling (`struct rate_sample`, `tp->delivered`, `tp->delivered_mstamp`, `tp->lost`, app-limited marking), pacing support (`sk_pacing_rate`, fq/EDT or internal pacing), `win_minmax`, inet_diag, BTF/kfunc registration, random cycle start selection, and module infrastructure.

Integration points:

- Users select BBR with `TCP_CONGESTION` or sysctl/default congestion-control configuration.
- TCP ACK processing invokes `cong_control` and passes rate samples.
- TCP recovery invokes `ssthresh`, `undo_cwnd`, and `set_state`.
- TCP transmit start invokes `cwnd_event_tx_start`.
- TSO sizing calls `min_tso_segs`.
- `TCP_CC_INFO`/inet_diag call `get_info`.
- BPF struct-ops programs can call the registered BBR kfuncs; local BPF selftests reference these symbols.

## Risks and Edge Cases

- Rate math uses fixed-point scaling and carefully ordered 64-bit operations. Changing order or types can overflow at high rates or underflow low-rate paths.
- BBR depends on accurate delivery-rate samples. App-limited filtering, ACK aggregation, delayed ACKs, GSO/TSO, EDT scheduling, and loss recovery can bias bandwidth estimates if fields are updated incorrectly elsewhere.
- PROBE_RTT intentionally reduces cwnd; bugs in exit conditions can leave flows stuck at four packets or prevent min RTT refresh.
- `bbr_packets_in_net_at_edt()` estimates inflight at scheduled departure time; pacing timestamp or `tcp_clock_cache` mistakes can cause too much or too little inflight.
- Long-term policer detection can suppress bandwidth probing for many rounds. Threshold changes risk underutilization or excessive policer loss.
- Loss recovery deliberately does not behave like Reno/CUBIC multiplicative decrease. External code expecting loss-driven ssthresh behavior may misinterpret BBR state.
- `BUILD_BUG_ON(sizeof(struct bbr) > ICSK_CA_PRIV_SIZE)` constrains future state growth.
- BPF kfunc exposure means callback signatures and BTF registration are ABI-like for BPF struct-ops users in this tree.

## Test Signals

Build-time signals include `CONFIG_TCP_CONG_BBR`, module build/load, `BUILD_BUG_ON` private-state size, and BTF kfunc registration success. Runtime smoke tests can set `TCP_CONGESTION` to `"bbr"`, verify pacing is active, inspect `TCP_INFO` and `TCP_CC_INFO`/inet_diag BBR info, and compare throughput/latency behavior under paced and unpaced qdiscs.

Local BPF selftest signals include `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c`, which imports BBR kfuncs, and broader TCP CA struct-ops tests under `tools/testing/selftests/bpf`. Network emulation tests should cover STARTUP-to-DRAIN-to-PROBE_BW, PROBE_RTT after min-RTT expiry, idle restart, loss recovery, app-limited samples, ACK aggregation, and policer-like loss/rate caps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/tcp_bbr.c -->
