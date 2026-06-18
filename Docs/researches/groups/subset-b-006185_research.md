# subset-b-006185 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/rtnetlink.c -->
# sources/distributed-fs/ceph-client/net/core/rtnetlink.c

## Purpose

`rtnetlink.c` is the protocol-independent core of the Linux `NETLINK_ROUTE` / rtnetlink interface. It owns the global RTNL lock, per-network-namespace rtnetlink sockets, message handler registration, dispatch, and a large set of default handlers for network link, bridge, FDB, MDB, and link statistics operations. User space tools such as `ip`, `bridge`, and ethtool-facing code reach this file through rtnetlink messages like `RTM_NEWLINK`, `RTM_GETLINK`, `RTM_SETLINK`, `RTM_NEWNEIGH`, `RTM_GETSTATS`, and bridge-family MDB/FDB operations.

The file is central infrastructure rather than a device driver. It converts netlink payloads into calls on `struct net_device`, `struct net_device_ops`, `struct rtnl_link_ops`, and `struct rtnl_af_ops`, then serializes kernel network-device state back into netlink attributes.

## Important APIs, Types, And Functions

The RTNL locking API is exported through `rtnl_lock()`, `rtnl_lock_interruptible()`, `rtnl_lock_killable()`, `rtnl_trylock()`, `rtnl_unlock()`, `__rtnl_unlock()`, `rtnl_is_locked()`, `lockdep_rtnl_is_held()`, and `refcount_dec_and_rtnl_lock()`. With `CONFIG_DEBUG_NET_SMALL_RTNL`, per-net namespace locks are layered under the global RTNL lock through `rtnl_net_lock()`, `rtnl_net_unlock()`, `rtnl_net_trylock()`, `rtnl_net_lock_killable()`, and lockdep comparison helpers.

`struct rtnl_link` is the registered handler entry for a protocol/message pair. It holds `doit`, `dumpit`, `owner`, `flags`, and an RCU head. `rtnl_msg_handlers` is a two-level RCU table indexed by protocol family and rtnetlink message index. `__rtnl_register_many()`, `__rtnl_unregister_many()`, `rtnl_unregister_all()`, and the internal `rtnl_register_internal()` manage this table.

`struct rtnl_link_ops` registration is handled by `rtnl_link_register()` and `rtnl_link_unregister()`. Link ops provide kind-specific virtual-device creation, validation, serialization, deletion, stats, and slave-link behavior. `struct rtnl_af_ops` registration is handled by `rtnl_af_register()` and `rtnl_af_unregister()` and gives address families a way to add link attributes, validate AF-specific changes, and fill stats.

Message emission helpers include `rtnetlink_send()`, `rtnl_unicast()`, `rtnl_notify()`, `rtnl_set_sk_err()`, `rtmsg_ifinfo_build_skb()`, `rtmsg_ifinfo_send()`, `rtmsg_ifinfo()`, and `rtmsg_ifinfo_newnet()`. Routing helper serializers include `rtnetlink_put_metrics()` and `rtnl_put_cacheinfo()`.

The link-reporting core is `if_nlmsg_size()` plus `rtnl_fill_ifinfo()`. It fills `RTM_NEWLINK` messages with names, indexes, flags, MTU, queue sizes, carrier counters, address data, qdisc, stats, XDP attachment state, VF/SR-IOV information, link kind data, slave info, alternate names, namespace IDs, devlink port handles, DPLL pin handles, parent device data, and AF-specific nests.

The major link mutation handlers are `rtnl_setlink()`, `do_setlink()`, `rtnl_newlink()`, `__rtnl_newlink()`, `rtnl_newlink_create()`, `rtnl_changelink()`, `rtnl_dellink()`, `rtnl_delete_link()`, and `rtnl_configure_link()`. They parse `IFLA_*` attributes, resolve target namespaces, validate policy, and call network core helpers or driver callbacks.

FDB support is implemented by `rtnl_fdb_add()`, `rtnl_fdb_del()`, `rtnl_fdb_get()`, `rtnl_fdb_dump()`, default exported operations `ndo_dflt_fdb_add()`, `ndo_dflt_fdb_del()`, `ndo_dflt_fdb_dump()`, and notification helpers. Bridge link support is implemented by `ndo_dflt_bridge_getlink()`, `rtnl_bridge_getlink()`, `rtnl_bridge_setlink()`, `rtnl_bridge_dellink()`, and `rtnl_bridge_notify()`.

Statistics support is implemented by `rtnl_stats_get()`, `rtnl_stats_dump()`, `rtnl_stats_set()`, `rtnl_fill_statsinfo()`, `if_nlmsg_stats_size()`, and offload-xstats helpers such as `rtnl_offload_xstats_fill()` and `rtnl_offload_xstats_notify()`. MDB support is implemented by `rtnl_mdb_dump()`, `rtnl_mdb_get()`, `rtnl_mdb_add()`, and `rtnl_mdb_del()`.

Initialization is performed by `rtnetlink_init()`, which registers pernet operations, installs a netdevice notifier, and registers the built-in rtnetlink handlers declared in `rtnetlink_rtnl_msg_handlers[]`.

## Control Flow

For each network namespace, `rtnetlink_net_init()` creates a `NETLINK_ROUTE` socket using `netlink_kernel_create()` with `rtnetlink_rcv()` as input and `rtnetlink_bind()` as the group bind gate. Received skbs are passed through `netlink_rcv_skb()` to `rtnetlink_rcv_msg()`.

`rtnetlink_rcv_msg()` validates the message type, minimal payload length, and operation kind. Non-GET operations require `CAP_NET_ADMIN`. Dump GET operations lookup a `dumpit` handler by family and message type, take a module reference, optionally compute a minimum allocation for `RTM_GETLINK`, and start a netlink dump through `rtnetlink_dump_start()`. Non-dump operations lookup a `doit` handler, enforce bulk-delete support, and either call it unlocked when flagged or call it under RTNL.

`RTM_GETLINK` dump requests flow through `rtnl_dump_ifinfo()`: parse request attributes, optionally resolve a target namespace, apply master/kind filters, iterate devices with dump cursor state, and call `rtnl_fill_ifinfo()` for each device. Single getlink requests flow through `rtnl_getlink()`, which resolves one device, synchronizes linkwatch carrier state, fills one skb, and unicasts it back.

`RTM_SETLINK` and change parts of `RTM_NEWLINK` flow into `do_setlink()`. It validates address lengths and size limits, optionally moves a device to another netns, locks device ops, then applies attributes in sequence: hardware map, MAC address, MTU, group, name, alias, broadcast address, flags, master linkage, carrier, queue length, GSO/GRO limits, operstate, link mode, VF data, VF port data, AF-specific data, protodown, and XDP FD replacement. Several changes can be committed before a later attribute fails.

`RTM_NEWLINK` parses base and nested link-info attributes, resolves the link kind via `rtnl_link_ops_get()` and optional module autoload, validates kind-specific data, resolves target/link/peer namespaces, locks the ordered namespace set with `rtnl_nets_lock()`, then either changes an existing device or creates a new one. Creation uses `rtnl_create_link()` and either `ops->newlink()` or `register_netdevice()`, followed by flag/master configuration.

FDB and MDB handlers follow a similar pattern: parse and validate strict or legacy netlink payloads, resolve the device, decide whether the operation applies to bridge master behavior or self behavior, call the appropriate `net_device_ops` callback, and emit notifications when a default operation succeeds without driver notification.

## State And Persistence Behavior

The global `rtnl_mutex` serializes most link and device topology changes. `defer_kfree_skb_list` temporarily stores skbs to free after RTNL unlock. `rtnl_msg_handlers` persists registered rtnetlink operations in RCU-protected tables. `link_ops` and `rtnl_af_ops` persist registered link-kind and address-family extension providers, guarded by mutex/RTNL plus RCU/SRCU grace periods.

Per-network-namespace persistent state is `net->rtnl`, the netlink socket created during namespace init and released during namespace exit. Link operations mutate persistent `struct net_device` fields such as name, MTU, group, flags, link mode, carrier, queue limits, GSO/GRO limits, protodown state, alternate names, XDP attachment, master/slave relationships, namespace placement, and offload stats enablement. FDB/MDB state is delegated to bridge/device callbacks or default unicast/multicast address list operations.

The file itself does not persist state across reboot or outside kernel memory. Its persistence is runtime kernel state plus registered callbacks.

## Dependencies And Integration Points

This code depends heavily on netlink attribute parsing (`nlmsg_parse*`, `nla_parse*`, `nla_put*`), network namespace APIs, netdevice core helpers, device notifier chains, RCU/SRCU, module references, devlink, DPLL, BPF/XDP, bridge data types, VLAN validation, and address-family extension hooks. IPv6-specific MDB validation is compiled conditionally.

Driver integration is through `struct net_device_ops`: VF setters/getters, FDB/MDB operations, bridge set/get/delete operations, offload stats hooks, XDP changes through `dev_change_xdp_fd()`, and device configuration callbacks. Virtual link-kind integration is through `struct rtnl_link_ops`: validation, allocation, setup, `newlink`, `changelink`, `dellink`, link-info serializers, slave serializers, peer netns handling, and xstats. Address-family integration is through `struct rtnl_af_ops` for per-AF link and stats data.

User-space ABI integration is strict: this file contains compatibility handling for old `RTM_GETLINK` and FDB dump request shapes, strict-check paths for newer requests, and careful netlink extack messages for invalid input.

## Risks And Edge Cases

`do_setlink()` intentionally has partial-commit behavior. If an early attribute is applied and a later driver callback or validation fails, the file logs a rate-limited warning that the interface may be left with an inconsistent configuration. Callers and tests must not assume all-or-nothing semantics.

Locking is high risk. The file mixes global RTNL, optional per-net RTNL mutexes, netdev instance locks, `dev_addr_sem`, RCU, SRCU, module references, pernet setup/cleanup exclusion, and callback paths into drivers. The ordered `rtnl_nets` helper and `rtnl_lock_unregistering_all()` exist specifically to avoid deadlocks around multi-netns link creation and link-op unregistration.

Netlink ABI validation is broad and security-sensitive. Non-GET operations require `CAP_NET_ADMIN`, target namespace operations check capabilities in the target user namespace, and multicast route groups have bind restrictions. Attribute policies reject or constrain many fields, but driver callbacks still receive parsed nested data and must maintain their own invariants.

Buffer sizing is another recurring risk. `if_nlmsg_size()` and `if_nlmsg_stats_size()` must match their fill functions; `-EMSGSIZE` in many single-message paths is treated as a kernel bug warning. Kind-specific and AF-specific callbacks can also create sizing mismatches.

RCU/SRCU lifetime rules matter for registered `rtnl_link_ops`, `rtnl_af_ops`, and handler tables. Incorrect module owner handling or missing grace periods could expose use-after-free. The code uses `try_module_get()`, `module_put()`, `kfree_rcu()`, `synchronize_net()`, `synchronize_srcu()`, and RCU list traversal to manage this.

Compatibility paths preserve older user-space behavior and therefore constrain cleanup. Changes to legacy request parsing, `RTNL_FLAG_DUMP_SPLIT_NLM_DONE`, FDB dump request handling, or default handler behavior could regress existing tools.

## Test Signals

Useful tests include rtnetlink selftests or integration tests that exercise `ip link add/set/del/show`, namespace moves, target netns IDs, XDP FD replacement, alternate interface names, protodown reasons, VF configuration failures, and group operations. Bridge/FDB/MDB coverage should include strict and legacy dump requests, `NTF_SELF` versus `NTF_MASTER`, bulk delete support flags, VLAN validation, and notification delivery.

Kernel debug signals include lockdep for RTNL/per-net lock ordering, KASAN/KCSAN for RCU and callback lifetime issues, extack strings for invalid netlink requests, `WARN_ON(err == -EMSGSIZE)` in sizing-sensitive paths, and the rate-limited partial-change warning from `do_setlink()`. User-space ABI tests should check both strict netlink validation and legacy request compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/rtnetlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/scm.c -->
# sources/distributed-fs/ceph-client/net/core/scm.c

## Purpose

`scm.c` implements common socket control-message processing for ancillary data passed through `sendmsg()` and `recvmsg()`. It handles `SOL_SOCKET` control messages such as `SCM_RIGHTS`, `SCM_CREDENTIALS`, `SCM_SECURITY`, timestamping control messages, and Unix-socket `SCM_PIDFD` receive support. The file is shared socket infrastructure used especially by Unix sockets and protocols that expose credentials, file descriptors, security labels, timestamps, or control-message output to user space.

## Important APIs, Types, And Functions

`struct scm_cookie` is the main transient container for ancillary state attached to a message. It can carry a `struct scm_fp_list` of file descriptors, credentials, a `struct pid` reference, and security data. `struct scm_fp_list` tracks referenced `struct file *` objects, the owning user, Unix-socket count, and optional Unix inflight graph state.

`scm_check_creds()` validates user-supplied `struct ucred` against the caller's current credentials and capabilities. `scm_fp_copy()` parses `SCM_RIGHTS`, validates file descriptor counts and individual descriptors, rejects io_uring file objects, takes file references, counts Unix sockets, and creates the fp list when needed.

`__scm_send()` is the main send-side parser. It walks control-message headers, validates `CMSG_OK()`, accepts `SCM_RIGHTS` only for Unix-family sockets, validates and stores `SCM_CREDENTIALS`, resolves pid references, and destroys partially built state on error. `__scm_destroy()` releases fp-list files and uid references. `scm_fp_dup()` duplicates an fp list and takes new file references.

`put_cmsg()` writes a control message to either user memory or a kernel msghdr buffer and handles truncation with `MSG_CTRUNC`. `put_cmsg_notrunc()` refuses to emit truncated output. `put_cmsg_scm_timestamping64()` and `put_cmsg_scm_timestamping()` convert internal timestamp arrays into new or old socket timestamping ABI structures.

`scm_detach_fds()` installs received `SCM_RIGHTS` files into the receiver's fd table, honoring `MSG_CMSG_CLOEXEC`, compatibility cmsg handling, truncation, and cleanup. `scm_recv()` and `scm_recv_unix()` are receive-side orchestrators. Unix receive additionally supports `scm_pidfd_recv()` when `sk_scm_pidfd` is enabled.

## Control Flow

On send, protocol code calls `__scm_send()` with a socket, userspace message, and initialized scm cookie. The function iterates each cmsghdr. Non-`SOL_SOCKET` messages are ignored by this common layer. `SCM_RIGHTS` requires `sock->ops->family == PF_UNIX` and is copied by `scm_fp_copy()`. `SCM_CREDENTIALS` must have exact length, pass `scm_check_creds()`, resolve or replace the stored pid reference with `scm_replace_pid()`, and convert uid/gid into kernel IDs. Any error destroys accumulated scm state before returning.

On receive, `scm_recv()` or `scm_recv_unix()` calls `__scm_recv_common()`. If the receiver provided no control buffer, the function marks `MSG_CTRUNC` when there was ancillary data to report, destroys scm state, and stops. Otherwise it emits credentials when requested by the socket, emits LSM security data when configured, detaches file descriptors if present, and leaves credential cleanup to the caller. `scm_recv_unix()` then optionally emits `SCM_PIDFD` and destroys credential references.

Control-message output uses `put_cmsg()`: validate control buffer capacity, optionally mark truncation, write cmsghdr fields and payload through hardened user access or kernel copies, advance `msg_control` and reduce `msg_controllen`.

## State And Persistence Behavior

Most state is per-message and reference-counted. File references taken during `SCM_RIGHTS` parsing persist until delivered to a receiver fd table or released by `__scm_destroy()`. The fp list stores a user reference to account the sender and, under Unix socket support, metadata used by inflight-cycle tracking elsewhere.

Credential and pid state lives in the `scm_cookie` for the lifetime of message transfer. `scm_replace_pid()` registers pidfs state and stores a `struct pid` reference; receive-side pidfd generation can allocate a new file descriptor and install the pidfd file only after the cmsg is successfully emitted. There is no disk persistence.

## Dependencies And Integration Points

This code integrates with VFS file references (`fget_raw()`, `fput()`, `get_file()`), fd installation (`scm_recv_one_fd()`, `fd_install()`), credential and namespace helpers, pidfs/pidfd helpers, LSM security context export, io_uring file detection, Unix socket helpers, compat cmsg handling, and hardened usercopy helpers.

It is tightly coupled to socket flags: `sk_scm_credentials`, `sk_scm_security`, and `sk_scm_pidfd` decide which ancillary data is emitted on receive. `MSG_CMSG_COMPAT`, `MSG_CMSG_CLOEXEC`, and `MSG_CTRUNC` affect ABI behavior.

## Risks And Edge Cases

Reference cleanup is the central risk. Errors while copying many file descriptors leave some references already acquired; `__scm_send()` calls `scm_destroy()` on error, and `scm_detach_fds()` destroys the fp list after successful fd installation attempts. Any future changes must preserve this ownership transfer.

Credential validation is security-sensitive. `scm_check_creds()` allows a supplied pid only if it matches the caller thread-group pid or the caller has `CAP_SYS_ADMIN` in the active pid namespace userns, and uid/gid only if they match real/effective/saved IDs or the caller has set-id capabilities. Namespace conversions must remain consistent.

Control buffer truncation is ABI-sensitive. `put_cmsg()` can emit truncated cmsgs and set `MSG_CTRUNC`, while `put_cmsg_notrunc()` and `scm_pidfd_recv()` use stricter checks. Mixing these semantics incorrectly can leak partially useful ancillary data or lose expected truncation signals.

`SCM_RIGHTS` rejects io_uring files and caps descriptor counts at `SCM_MAX_FD`. Unix sockets have additional inflight and cycle constraints outside this file; the `count_unix` and Unix-only fields must remain correctly initialized and duplicated.

## Test Signals

Test coverage should include Unix socket fd passing, invalid fd arrays, more than `SCM_MAX_FD`, io_uring fd rejection, credential spoofing attempts with and without capabilities, pid namespace behavior, empty or short cmsghdrs, no-control-buffer receive truncation, compat cmsg paths, `MSG_CMSG_CLOEXEC`, timestamping cmsg output, LSM security cmsg emission, and `SCM_PIDFD` truncation and successful fd installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/scm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/secure_seq.c -->
# sources/distributed-fs/ceph-client/net/core/secure_seq.c

## Purpose

`secure_seq.c` generates keyed, hard-to-predict TCP initial sequence numbers, TCP timestamp offsets, and ephemeral-port hash values for IPv4 and IPv6. It uses a per-boot random SipHash key and mixes endpoint addresses, ports, and a time component where appropriate. The file supports TCP/IP hardening by avoiding trivially predictable sequence and port selection inputs.

## Important APIs, Types, And Functions

`net_secret` is a static `siphash_aligned_key_t` initialized once by `net_secret_init()` through `net_get_random_once()`. `EPHEMERAL_PORT_SHUFFLE_PERIOD` controls how often ephemeral-port hash inputs change, currently every `10 * HZ`.

For TCP sequence and timestamp offsets, IPv6 builds `secure_tcpv6_seq_and_ts_off()` when IPv6 or INET is enabled, and IPv4 builds `secure_tcp_seq_and_ts_off()` under `CONFIG_INET`. Both return `union tcp_seq_and_ts_off`, whose 64-bit hash output is interpreted as sequence and timestamp-offset fields. `seq_scale()` adds a real-time based increment to the sequence value to preserve TCP-style monotonic progression.

For ephemeral port selection, `secure_ipv6_port_ephemeral()` hashes IPv6 source/destination addresses, destination port, and a jiffies time seed. `secure_ipv4_port_ephemeral()` hashes IPv4 source/destination addresses, destination port, and the same period-scaled time seed.

## Control Flow

Every public function first ensures the secret is initialized. TCP sequence functions construct an aligned tuple of endpoint addresses and ports, hash it with SipHash, clear timestamp offset when `net->ipv4.sysctl_tcp_timestamps != 1`, scale the sequence with `seq_scale()`, and return the union. Ephemeral-port functions hash endpoint data plus `jiffies / EPHEMERAL_PORT_SHUFFLE_PERIOD` and return a 64-bit value to the caller's port-selection logic.

The IPv4 TCP function uses `siphash_3u32()` over source address, destination address, and packed ports. The IPv6 TCP function builds an aligned struct containing two `in6_addr` values and both ports, then hashes through the destination-port field. The comments document that a zero source port would collide with the IPv4 ephemeral-port helper, but TCP source port zero is not expected.

## State And Persistence Behavior

The only persistent state in this file is `net_secret`, a kernel-memory random key initialized once per boot. There is no per-net namespace secret here. The per-call time behavior comes from `ktime_get_real_ns()` for sequence scaling and `jiffies` for ephemeral-port shuffle periods. The generated values are deterministic for a given secret and input tuple within the relevant time component.

## Dependencies And Integration Points

The file depends on the random subsystem, SipHash helpers, TCP sequence/timestamp union definitions from `net/secure_seq.h`, IPv4/IPv6 address types, jiffies, and TCP timestamp sysctl state through `struct net`. It exports sequence and ephemeral helpers for TCP/IP stack code and port selection code.

## Risks And Edge Cases

The security property depends on `net_get_random_once()` producing a secret before outputs are useful to attackers. Because the secret is global rather than per-netns, namespace isolation does not imply independent sequence-generation keys.

Timestamp offset handling is conditional: if TCP timestamps are not exactly enabled as value `1`, timestamp offset is forced to zero while the sequence still uses the hash and time scaling. Consumers must not expect a timestamp offset under all timestamp sysctl modes.

The ephemeral-port hash intentionally changes only every shuffle period; shorter periods could cause instability, while longer periods give attackers a wider observation window. The IPv4 comment about source port zero documents an input-domain assumption that should remain true.

## Test Signals

Useful tests include build coverage for `CONFIG_INET`, IPv6-only, and combined configurations; checks that repeated calls are stable for fixed inputs within a port-shuffle period but change over time; validation that timestamp offsets are zero when TCP timestamps are disabled or not in mode `1`; and statistical/regression tests that no obvious endpoint tuple collisions are introduced by struct layout or byte-order changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/secure_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/selftests.c -->
# sources/distributed-fs/ceph-client/net/core/selftests.c

## Purpose

`selftests.c` provides a common library for generic PHY ethtool offline selftests. It builds synthetic Ethernet/IPv4/TCP or UDP packets, transmits them through device/PHY loopback, validates received packets through a temporary packet handler, and exposes standard ethtool selftest entry points for drivers that want reusable PHY loopback coverage.

## Important APIs, Types, And Functions

`net_test_get_skb()` is the exported packet builder. It takes a `struct net_device`, packet id, and `struct net_packet_attrs`, then constructs an skb containing Ethernet, IPv4, TCP or UDP, a `struct netsfhdr` selftest header with `NET_TEST_PKT_MAGIC`, optional payload, optional padding to `max_size`, checksum metadata, and device/protocol fields.

`net_test_loopback_validate()` is the receive packet handler used by loopback tests. It unshares and linearizes the skb, checks source/destination MAC addresses when requested, accounts for optional double VLAN offset, validates L4 protocol and destination port, verifies selftest magic and id, detects deliberately bad TCP checksums incorrectly marked `CHECKSUM_UNNECESSARY`, completes the test, and frees the skb.

`__net_test_loopback()` allocates `struct net_test_priv`, installs a temporary `packet_type` handler with `dev_add_pack()`, creates and transmits the skb through `dev_direct_xmit()`, waits for completion with a default timeout, maps validation state to `0`, `-ETIMEDOUT`, `-EIO`, `-ENETUNREACH`, or allocation errors, then removes the packet handler.

The test functions are `net_test_netif_carrier()`, `net_test_phy_phydev()`, `net_test_phy_loopback_enable()`, `net_test_phy_loopback_disable()`, `net_test_phy_loopback_udp()`, `net_test_phy_loopback_udp_mtu()`, `net_test_phy_loopback_tcp()`, and `net_test_phy_loopback_tcp_bad_csum()`. The exported ethtool helpers are `net_selftest()`, `net_selftest_get_count()`, and `net_selftest_get_strings()`.

## Control Flow

An ethtool-capable driver calls `net_selftest()`. The function rejects non-offline tests by setting `ETH_TEST_FL_FAILED`, resets the static packet id counter, and runs every entry in `net_selftests[]`. Failures other than `-EOPNOTSUPP` mark the ethtool result as failed; unsupported PHY operations are allowed to be reported without failing the entire suite.

Loopback tests create attributes, usually setting destination MAC to the device address and optionally enabling TCP, MTU-sized padding, or bad checksum mode. `__net_test_loopback()` registers the packet handler before sending so the looped frame can be captured. The validation callback completes the wait once the expected packet is seen, and the sender maps missing completion to timeout.

The bad TCP checksum test uses `net_test_get_skb()` to force checksum computation, then mutates the TCP checksum away from a valid value. Success means the driver did not falsely mark the bad checksum as hardware-verified; `-EIO` indicates the skb arrived with `CHECKSUM_UNNECESSARY`, which is treated as a serious RX path defect.

## State And Persistence Behavior

The only file-level state is `net_test_next_id`, a u8 packet identifier reset at the start of `net_selftest()` and incremented for each transmitted test packet. Per-test state is held in `struct net_test_priv`, including completion, result state, packet attributes, and packet handler. It is allocated and freed within `__net_test_loopback()`.

The tests temporarily change PHY loopback state through `phy_loopback(ndev->phydev, true/false, 0)`. That is persistent device state until disabled, so the ordered selftest array deliberately enables loopback before packet tests and disables it after them.

## Dependencies And Integration Points

The file integrates with ethtool selftest APIs, PHY library loopback control, skb allocation and checksum helpers, direct device transmit, packet type receive hooks, IPv4/TCP/UDP header helpers, and netdevice carrier/address state. It expects definitions from `net/selftests.h`, including `struct net_packet_attrs`, `struct netsfhdr`, `NET_TEST_PKT_SIZE`, `NET_TEST_PKT_MAGIC`, and `NET_LB_TIMEOUT`.

Drivers integrate by calling the exported helpers from their ethtool ops and using the string/count helpers to size result arrays.

## Risks And Edge Cases

The packet builder must keep skb head/tail layout consistent with the Ethernet/IP/L4/selftest header sizes. `max_size` changes both allocation/padding and UDP/IP length calculations; off-by-one errors would cause false loopback failures.

The validator assumes packets can be unshared and linearized in atomic context. Allocation or linearization failure silently leads to cleanup and no success completion, which the sender reports as timeout.

The static u8 id can wrap if the test list grows substantially, though the current list is small. Since each run resets it and waits per packet, wrap is not a practical issue today.

PHY loopback state is externally visible. If the enable test succeeds and a later step aborts unexpectedly outside this function's normal sequence, drivers still rely on the final disable test being run by `net_selftest()`.

The bad checksum result is nuanced: timeout can mean hardware dropped the frame before the driver saw it, while `-EIO` specifically means the driver incorrectly claimed a bad checksum was unnecessary to verify.

## Test Signals

Expected coverage is direct: invoke ethtool offline selftests on devices with and without PHYs, with carrier up/down, with PHY loopback support and without it, and inspect per-test return codes. Packet-level tests should cover UDP, MTU-sized UDP, TCP, and bad TCP checksum behavior. Driver validation should ensure packet handler cleanup, loopback disable, and ethtool string/count alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/selftests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skb_fault_injection.c -->
# sources/distributed-fs/ceph-client/net/core/skb_fault_injection.c

## Purpose

`skb_fault_injection.c` adds a fault-injection hook for skb head reallocation. It allows tests to force `pskb_expand_head()` from `skb_might_realloc()` according to standard Linux fault-injection attributes, optionally filtered by network device name. This helps exercise paths that must tolerate skb data/head pointer changes.

## Important APIs, Types, And Functions

The file-level `skb_realloc` object stores `struct fault_attr attr`, a device-name buffer, and a `filtered` boolean. `should_fail_net_realloc_skb()` checks the optional device-name filter and then calls `should_fail()` on the configured fault attributes. It is marked with `ALLOW_ERROR_INJECTION()`.

`skb_might_realloc()` is the exported hook. If `should_fail_net_realloc_skb()` returns true, it calls `pskb_expand_head(skb, 0, 0, GFP_ATOMIC)`, forcing skb head reallocation without requesting additional headroom or tailroom.

`fail_skb_realloc_setup()` wires the boot parameter `fail_skb_realloc=` into `setup_fault_attr()`. `fail_skb_realloc_debugfs()` creates a debugfs fault-injection directory named `fail_skb_realloc` and adds a `devname` file. `devname_write()` resets settings, copies a user-provided name, trims a trailing newline or whitespace, and enables filtering when non-empty. `devname_read()` returns the active filter name or EOF when unfiltered.

## Control Flow

At boot, the `__setup()` handler can initialize fault attributes from the kernel command line. During late init, debugfs controls are created through `fault_create_debugfs_attr()` and `debugfs_create_file()`.

Runtime callers invoke `skb_might_realloc(skb)` at points where tests want to simulate possible skb reallocation. The function checks the device filter first; when filtering is enabled, only matching `skb->dev->name` can trigger. It then checks the fault-injection policy. On a selected hit, it calls `pskb_expand_head()` in atomic allocation context.

Users can update the device filter by writing to debugfs. Each write clears the previous filter, copies up to `IFNAMSIZ`, null-terminates, trims, and sets `filtered` according to whether the resulting string is non-empty.

## State And Persistence Behavior

Fault policy, filter name, and filter enablement are static kernel-memory state. They can be initialized from the boot command line and adjusted at runtime through debugfs. They do not persist across reboot. The exported hook mutates the passed skb by potentially reallocating its head; callers must assume skb data pointers may be invalidated after the call.

## Dependencies And Integration Points

This file depends on `CONFIG_FAULT_INJECTION` style helpers, debugfs, skb memory helpers, and netdevice naming. It exports `skb_might_realloc()` for other networking code to place reallocation fault points. Test automation can control frequency/probability through the standard fault-injection debugfs attributes plus the custom `devname` filter.

## Risks And Edge Cases

`should_fail_net_realloc_skb()` assumes `skb->dev` is valid because it immediately reads `skb->dev->name`. Callers must not use this hook on skbs without a device unless they first guard that condition.

`skb_might_realloc()` ignores the return value of `pskb_expand_head()`. This is acceptable for a fault-injection perturbation hook whose purpose is to trigger reallocation when possible, but tests should not interpret it as guaranteed reallocation.

The debugfs filter is global and unsynchronized beyond simple writes/reads to static storage. Concurrent filter updates and hook calls can race at string-comparison granularity, which is typical for debug/test controls but unsuitable as a production policy mechanism.

## Test Signals

Tests should verify boot-parameter parsing, debugfs creation, unfiltered and filtered triggering, newline trimming in `devname`, EOF reads when unfiltered, and that callers tolerate skb head/data pointer changes after `skb_might_realloc()`. Negative tests should include nonmatching device filters and disabled fault attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/skb_fault_injection.c -->
