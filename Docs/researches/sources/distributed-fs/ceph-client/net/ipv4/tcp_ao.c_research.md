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
