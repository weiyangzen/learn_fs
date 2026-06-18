# Research group subset-b-006210

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrconf.c -->
# sources/distributed-fs/ceph-client/net/ipv6/addrconf.c

## Purpose
`addrconf.c` is the main IPv6 address autoconfiguration implementation for this kernel-derived Ceph client source tree. It owns per-interface IPv6 device state creation, IPv6 address creation/deletion/modification, duplicate address detection (DAD), router solicitation timing, prefix information option handling from router advertisements, temporary/privacy address regeneration, rtnetlink address/link/netconf surfaces, `/proc/net/if_inet6`, and sysctl-backed IPv6 device configuration. It integrates the IPv6 address model with netdevices, routing, neighbor discovery, multicast/anycast membership, network namespaces, and transport/source-address selection.

## Important APIs, Types, and Functions
- Global/default configuration: `ipv6_devconf` and `ipv6_devconf_dflt` define compiled defaults for per-netns `conf/all`, `conf/default`, and per-device `struct ipv6_devconf` values. Important fields include `forwarding`, `accept_ra`, `autoconf`, `dad_transmits`, `use_tempaddr`, `max_addresses`, `stable_secret`, `addr_gen_mode`, `disable_ipv6`, `keep_addr_on_down`, `disable_policy`, segment routing, RPL, and IOAM toggles.
- Per-device lifecycle: `ipv6_add_dev()`, `ipv6_find_idev()`, `addrconf_add_dev()`, `addrconf_ifdown()`, `addrconf_notify()`, and `addrconf_cleanup()` allocate and tear down `struct inet6_dev`, SNMP state, neighbor parameters, multicast state, sysctl entries, and `dev->ip6_ptr`.
- Address lifecycle: `ipv6_add_addr()`, `ipv6_del_addr()`, `inet6_addr_add()`, `inet6_addr_del()`, `inet6_addr_modify()`, `addrconf_add_ifaddr()`, `addrconf_del_ifaddr()`, `inet6_rtm_newaddr()`, `inet6_rtm_deladdr()`, and `inet6_rtm_getaddr()` implement ioctl and rtnetlink creation, deletion, replacement, dump, and get flows.
- Lookup helpers exported to the rest of IPv6: `ipv6_dev_get_saddr()`, `ipv6_get_lladdr()`, `ipv6_chk_addr()`, `ipv6_chk_addr_and_flags()`, `ipv6_chk_custom_prefix()`, `ipv6_chk_prefix()`, `ipv6_dev_find()`, `ipv6_get_ifaddr()`, and `ipv6_chk_rpl_srh_loop()`.
- Router advertisement and prefix handling: `addrconf_prefix_rcv()` validates PIOs, updates on-link prefix routes, chooses token/stable/EUI-64 interface identifiers, calls `addrconf_prefix_rcv_add_addr()`, and notifies prefix listeners.
- DAD and solicitation: `addrconf_dad_start()`, `addrconf_dad_work()`, `addrconf_dad_begin()`, `addrconf_dad_failure()`, `addrconf_dad_completed()`, `addrconf_rs_timer()`, and `addrconf_dad_run()` drive tentative address validation, retry, failure handling, optimistic DAD, enhanced DAD nonce use, and router solicitation backoff.
- Privacy/stable address generation: `ipv6_create_tempaddr()`, `manage_tempaddrs()`, `delete_tempaddrs()`, `ipv6_generate_stable_address()`, `ipv6_gen_mode_random_init()`, `ipv6_gen_rnd_iid()`, `ipv6_generate_eui64()`, and link-type-specific IID builders cover RFC 4941 temporary addresses and stable privacy/EUI64 link-local generation.
- Routing integration: `addrconf_f6i_alloc()` is used indirectly for host routes; local functions `addrconf_prefix_route()`, `addrconf_get_prefix_route()`, `modify_prefix_route()`, `cleanup_prefix_route()`, `check_cleanup_prefix_route()`, and `addrconf_add_mroute()` maintain prefix, peer, host, and multicast routes.
- Netlink/proc/sysctl surfaces: `inet6_fill_ifaddr()`, `inet6_dump_addr()`, `inet6_fill_ifinfo()`, `inet6_ifinfo_notify()`, `inet6_netconf_*()`, `inet6_prefix_notify()`, `if6_proc_init()`, `addrconf_sysctl[]`, and registration helpers expose state to iproute2, procfs, and `/proc/sys/net/ipv6/conf/*`.

## Control Flow
- Initialization starts in `addrconf_init()`: initialize addrlabel defaults, register per-net operations, create the single-thread `ipv6_addrconf` workqueue, create the blackhole IPv6 device, initialize special routes, register the netdevice notifier, schedule address verification, register AF-specific rtnetlink ops, and register IPv6 address/netconf/addrlabel netlink handlers.
- Per-network namespace initialization in `addrconf_init_net()` allocates the hash table `net->ipv6.inet6_addr_lst`, clones default/all `ipv6_devconf`, applies module defaults and optional inheritance, registers `conf/all` and `conf/default` sysctls, and initializes delayed verification work.
- A netdevice event enters `addrconf_notify()`. Register/up/change/MTU events create or reuse `inet6_dev`, update readiness, restore permanent address routes, generate loopback/link-local/tunnel addresses, start DAD, resync routes, and notify link info. Down/unregister calls `addrconf_ifdown()`, which removes address hash entries, cancels timers/work, optionally preserves non-local permanent addresses, removes multicast/anycast state, unregisters sysctls, and releases neighbor/device references.
- Manual address adds enter either `addrconf_add_ifaddr()` ioctl or `inet6_rtm_newaddr()` netlink. Both converge on `inet6_addr_add()`, which validates prefix length and flags, ensures the IPv6 device exists, optionally joins multicast for `IFA_F_MCAUTOJOIN`, creates the `inet6_ifaddr` through `ipv6_add_addr()`, installs prefix routes unless suppressed, starts DAD, manages temporary addresses, and schedules lifetime verification.
- RA prefix handling enters `addrconf_prefix_rcv()`. It rejects invalid prefix options, updates or deletes on-link prefix routes according to valid lifetime, and for 64-bit autoconf prefixes chooses a tokenized IID, stable privacy IID, generated EUI-64 IID, or inherited EUI-64 IID. `addrconf_prefix_rcv_add_addr()` then creates or refreshes the autoconfigured address, applies RFC 4862 lifetime rules, marks managed-tempaddr, starts DAD, and updates temporary children.
- DAD progresses through delayed work. New/tentative addresses are moved to `PREDAD`, `DAD`, and `POSTDAD`; neighbor solicitations are sent until probes run out; success clears tentative/optimistic/DADFAILED flags, notifies RTM_NEWADDR, inserts routes, joins anycast if forwarding, resends MLD, and may send router solicitations. Failure marks DADFAILED, may retry stable privacy generation with incremented `dad_count`, or disables IPv6 for MAC-derived link-local conflicts when `accept_dad > 1`.
- Lifetime verification in `addrconf_verify_rtnl()` scans the global address hash under RTNL and RCU/bh protection. It regenerates temporary addresses before deprecation, deprecates addresses at preferred lifetime expiry, deletes addresses at valid lifetime expiry, batches notifications, and reschedules itself with fuzzed timing.
- Source address selection in `ipv6_dev_get_saddr()` scores candidate addresses under RCU using RFC 6724-like rules: same address, scope, preferred/deprecated/optimistic state, home address if enabled, outgoing interface/L3 master, address label, privacy preference, ORCHID match, longest prefix match, and optimistic ordering.

## State and Persistence Behavior
- Persistent runtime state is held in `struct net` IPv6 members, `struct inet6_dev`, `struct inet6_ifaddr`, route tables, neighbor parameters, multicast/anycast lists, sysctl tables, and proc/netlink-visible counters. There is no disk persistence in this file.
- `net->ipv6.inet6_addr_lst` is a per-netns hash table keyed by IPv6 address; each `inet6_ifaddr` is also in the owning `inet6_dev->addr_list`, with temporary addresses additionally tracked on `tempaddr_list`.
- Address state is reference-counted and RCU-protected. `inet6_ifa_finish_destroy()` requires the address to be unhashed and dead before `kfree_rcu()`. Device state is released through `in6_dev_finish_destroy()` in `addrconf_core.c`.
- Timed state uses `jiffies`, `valid_lft`, `prefered_lft`, `tstamp`, `cstamp`, DAD delayed work, router solicitation timers, and namespace `addr_chk_work`. Lifetime values may be infinite or converted through `addrconf_timeout_fixup()`.
- Sysctl writes can mutate defaults, all-devices values, or one device. Some writes have side effects: forwarding toggles multicast/all-router membership and purges default routers; disable IPv6 drives synthetic down/up handling; stable secrets force stable privacy mode; addr_gen_mode can generate new automatic addresses; disable_policy updates host route `DST_NOPOLICY`.

## Dependencies and Integration Points
- Depends heavily on Linux networking primitives: RTNL, RCU, hlist/list APIs, per-net operations, netdevice notifiers, workqueues/timers, neighbor discovery, route FIB6 APIs, netlink/rtnetlink, procfs, sysctl, SNMP/MIB allocators, and capability checks.
- Integrates with `ndisc` for RS/NS/NA, `ip6_route` for host/prefix/default/multicast routes, `addrlabel.c` through `ipv6_addr_label()`, `addrconf_core.c` for address typing/notifiers/constants/destruction, multicast and anycast subsystems, L3 master/VRF helpers, tunnels, 6lowpan, FireWire, Infiniband, GRE/SIT, segment routing, RPL, IOAM, XFRM policy flags, and BPF-visible rtnetlink state.
- External subsystems can register address validators with `inet6addr_validator_notifier_call_chain()` before add and receive address lifecycle events through `inet6addr_notifier_call_chain()`.

## Risks and Edge Cases
- Concurrency is the dominant risk: address hash, per-device lists, route pointers, timers, and delayed work cross RTNL, RCU, spinlocks, and refcounts. Any change must preserve lock ordering around `idev->lock`, `ifp->lock`, `addrconf_hash_lock`, and route table locks.
- DAD races are subtle: down/unregister, optimistic DAD, DAD failure retry, `keep_addr_on_down`, and stable privacy retries all manipulate address state and route insertion/removal.
- Lifetime arithmetic must avoid overflow and jiffies rounding bugs. RA valid/preferred lifetime handling intentionally follows RFC 4862 minimum-lifetime rules unless `ra_honor_pio_life` overrides them.
- Prefix route cleanup is shared among multiple addresses on the same prefix. Deleting one address must not remove a route still required by another permanent, managed, or user-managed address.
- Sysctl registration copies a template table and pointer-adjusts `data`; adding fields can break if offsets, `extra1`, or `extra2` are mishandled.
- Stable privacy generation uses a static SHA-1 context/data block under a spinlock and intentionally reads SHA-1 internal state without standard finalization; this is compatibility-sensitive.
- Netlink strict validation rejects unexpected attributes in newer paths; changing policies can break iproute2 compatibility or loosen validation unexpectedly.

## Test Signals
- Address lifecycle: `ip -6 addr add/change/replace/del`, duplicate add failures, `IFA_F_NODAD`, `IFA_F_OPTIMISTIC`, `IFA_F_NOPREFIXROUTE`, peer addresses, `IFA_F_MCAUTOJOIN`, and prefix-route presence in `ip -6 route`.
- Autoconf/RA: inject prefix information options with valid/preferred lifetime combinations, `ra_honor_pio_life`, `accept_ra_min_lft`, tokenized IIDs, stable privacy secret, EUI64 fallback, and wrong prefix length.
- DAD: conflict detection, stable privacy retry count, enhanced DAD nonce, optimistic DAD notifications, `accept_dad > 1` disabling IPv6 on link-local conflict, and interface down during DAD.
- Device events: register/up/down/unregister/MTU changes/name changes/type changes/VRF upper changes with checks for sysctl/proc/netlink cleanup and route synchronization.
- Source selection: scope, labels, privacy preferences, deprecated addresses, optimistic addresses, VRF/L3 master behavior, outgoing-interface-only configuration.
- Observability: `ip -6 addr show`, `ip -6 addrlabel`, `ip -6 netconf`, `ip -6 link`, `/proc/net/if_inet6`, `/proc/sys/net/ipv6/conf/*`, and MIB/proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrconf_core.c -->
# sources/distributed-fs/ceph-client/net/ipv6/addrconf_core.c

## Purpose
`addrconf_core.c` contains small IPv6 address-configuration primitives that must remain available to static components even when the full IPv6 module is not configured or loaded. It exports core address classification, address notifier chains, well-known IPv6 constants, an optional FIB6 flush hook, and final `inet6_dev` destruction.

## Important APIs, Types, and Functions
- `void (*__fib6_flush_trees)(struct net *)`: exported function pointer used by XFRM or other code to request IPv6 route tree flushes when full IPv6 registers an implementation.
- `__ipv6_addr_type(const struct in6_addr *addr)`: exported classifier returning `IPV6_ADDR_*` type and encoded scope bits for multicast, link-local, site-local, ULA, compatible IPv4, mapped IPv4, loopback, unspecified, and global unicast addresses.
- `register_inet6addr_notifier()`, `unregister_inet6addr_notifier()`, `inet6addr_notifier_call_chain()`: exported atomic notifier chain for address lifecycle events.
- `register_inet6addr_validator_notifier()`, `unregister_inet6addr_validator_notifier()`, `inet6addr_validator_notifier_call_chain()`: exported blocking notifier chain used before address creation so validators can veto or annotate errors.
- Exported constants: `in6addr_loopback`, `in6addr_any`, `in6addr_linklocal_allnodes`, `in6addr_linklocal_allrouters`, `in6addr_interfacelocal_allnodes`, `in6addr_interfacelocal_allrouters`, and `in6addr_sitelocal_allrouters`.
- `in6_dev_finish_destroy()`: exported final destroy path for `struct inet6_dev`; it validates that address/multicast/timer state is gone, drops the netdevice reference, marks alive-free bugs, and schedules RCU freeing.

## Control Flow
- Address classification is a straight decision tree over the leading address bits and special low-word forms. It returns early for broad global-unicast prefixes, multicast with multicast scope, link/site local, ULA, unspecified, loopback, IPv4-compatible, and IPv4-mapped forms.
- Notifier registration functions delegate to kernel atomic/blocking notifier helpers; `addrconf.c` invokes the validator chain during blocking address add and invokes the atomic chain on address up/down notifications.
- `in6_dev_finish_destroy()` is called after higher-level addrconf teardown has removed addresses, multicast state, and timers. It warns on leftover state, drops the `net_device` hold, refuses to free an object not marked dead, and otherwise calls `call_rcu()` to free SNMP allocations and the `inet6_dev`.

## State and Persistence Behavior
- The file owns two static notifier heads: `inet6addr_chain` and `inet6addr_validator_chain`.
- It exports immutable aligned `struct in6_addr` constants for common protocol addresses.
- Device destruction frees memory only after RCU grace period via `in6_dev_finish_destroy_rcu()`, including per-device IPv6, ICMPv6, and ICMPv6 message MIB allocations. No persistent storage is involved.

## Dependencies and Integration Points
- Used by `addrconf.c`, `af_inet6.c`, routing, XFRM, tunnel, and transport code needing IPv6 address type tests and well-known addresses.
- Includes only core networking headers (`ipv6.h`, `addrconf.h`, `ip.h`) so these symbols are available to static/non-module pieces.
- The validator notifier is an integration point for subsystems that must reject address assignment before `inet6_ifaddr` allocation is committed.

## Risks and Edge Cases
- `__ipv6_addr_type()` is a foundational classifier; any change to masks or scope encoding affects source selection, bind validation, addrlabel matching, routing, and DAD behavior.
- The classifier treats ULAs (`fc00::/7`) as global scope per RFC 4193. That can be surprising but is intentional for address-selection scope.
- Destroy path warnings indicate lifecycle bugs elsewhere. Freeing an `inet6_dev` not marked dead intentionally leaks/returns after warning rather than freeing active state.
- Notifier chains differ intentionally: validators are blocking and may sleep; lifecycle notifications are atomic.

## Test Signals
- Unit-style address classification vectors for `::`, `::1`, `::ffff:0:0/96`, `::/96`, `ff00::/8` scopes, `fe80::/10`, `fec0::/10`, `fc00::/7`, and ordinary global unicast.
- Register/unregister notifier probes and verify calls on address add/delete and validator rejection propagation.
- Device teardown tests should verify no warnings with clean addrconf teardown and intentional warnings when address list, multicast list, timer, or `dead` state is wrong.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrconf_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrlabel.c -->
# sources/distributed-fs/ceph-client/net/ipv6/addrlabel.c

## Purpose
`addrlabel.c` implements the IPv6 address label policy table used by default source address selection. Labels follow RFC 6724 with Linux extensions and are exposed through rtnetlink `RTM_NEWADDRLABEL`, `RTM_DELADDRLABEL`, and `RTM_GETADDRLABEL`. `addrconf.c` calls `ipv6_addr_label()` while scoring source addresses.

## Important APIs, Types, and Functions
- `struct ip6addrlbl_entry`: one policy row containing prefix, prefix length, optional ifindex selector, special address type selector, label value, RCU hlist node, and RCU free head.
- `ip6addrlbl_init_table[]`: per-net default policy entries for `::/0`, ULA, site-local, 6to4, 6bone, Teredo, ORCHID, IPv4-mapped, IPv4-compatible, and loopback labels.
- `ipv6_addr_label()`: exported lookup-style function returning a label for an address/type/ifindex or `IPV6_ADDR_LABEL_DEFAULT` when no row matches.
- `ip6addrlbl_alloc()`, `__ip6addrlbl_add()`, `ip6addrlbl_add()`, `__ip6addrlbl_del()`, `ip6addrlbl_del()`: allocation and mutation helpers that normalize prefixes, validate special mapped/compat/loopback prefix lengths, keep rows sorted, and update sequence numbers.
- `ip6addrlbl_net_init()` and `ip6addrlbl_net_exit()`: per-net namespace setup and teardown of the label table.
- Rtnetlink handlers: `ip6addrlbl_newdel()`, `ip6addrlbl_get()`, `ip6addrlbl_dump()`, `ipv6_addr_label_rtnl_register()`.

## Control Flow
- Initialization registers a per-net subsystem; each namespace initializes a spinlock and hlist head, then inserts the default table rows with `ip6addrlbl_add()`.
- Lookup masks the caller's address type down to mapped/compatible/loopback bits, enters RCU, scans the sorted hlist, and returns the first row matching ifindex, address type, and prefix. Longest-prefix ordering makes first match the best match.
- Add/replace parses netlink attributes, rejects non-AF_INET6 and invalid prefix length/label, checks ifindex existence, allocates a normalized row, and inserts under `ip6addrlbl_table.lock`. Replacement swaps the existing hlist node using RCU and frees the old row after grace period.
- Delete normalizes the requested prefix and removes an exact prefix length, ifindex, and prefix match under the table lock.
- Dump validates strict requests, snapshots `seq`, iterates rows under RCU from `cb->args[0]`, and emits `ifaddrlblmsg` with address and label attributes. Get requires a /128 query address and returns the matching row for that full address.

## State and Persistence Behavior
- State is per network namespace in `net->ipv6.ip6addrlbl_table`, including an RCU hlist, spinlock, and sequence counter.
- Rows are dynamic kernel allocations and are not persisted outside the running namespace. Defaults are recreated on namespace initialization.
- Readers are lockless under RCU; writers serialize with a spinlock and use `hlist_*_rcu()` plus `kfree_rcu()`. The sequence is incremented on successful add/replace to support dump consistency.

## Dependencies and Integration Points
- Uses core address helpers from `addrconf_core.c`, especially `ipv6_addr_type()`, `ipv6_prefix_equal()`, and well-known address constants.
- Feeds `addrconf.c` source selection rule "Prefer matching label" through `ipv6_addr_label()`.
- Exposes policy management to userspace through rtnetlink and is commonly exercised by `ip addrlabel`.

## Risks and Edge Cases
- Ordering in `__ip6addrlbl_add()` is security/behavior-sensitive: the table must prefer longer prefixes and ifindex-specific entries correctly. Bad ordering changes source-address selection globally.
- Special address types have strict prefix-length rules; mapped addresses longer than /96 are rejected, while broader mapped prefixes lose the special type constraint.
- Netlink handlers reject the sentinel label `0xffffffff`, because that value represents "no policy."
- Get requires prefix length 128 and an address attribute; dump strictness rejects nonzero header fields and trailing attributes.
- If default table initialization fails partway through, the error path removes rows already inserted; changes must preserve that cleanup.

## Test Signals
- `ip addrlabel list`, `ip addrlabel add`, `replace`, and `del` for global, ifindex-scoped, ULA, mapped, compat, and loopback prefixes.
- Source address selection tests where destination and candidate source labels match or mismatch.
- Network namespace creation/destruction should produce independent default tables and clean RCU-free teardown.
- Strict rtnetlink tests for unsupported attributes, invalid family, invalid prefix length, missing address/label, sentinel label, nonexistent ifindex, and `/128` get behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/addrlabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/af_inet6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/af_inet6.c

## Purpose
`af_inet6.c` registers and implements the PF_INET6 socket protocol family. It creates IPv6 sockets from the protocol-switch table, binds and names sockets, delegates send/receive/ioctl paths to protocol implementations, registers TCP/UDP/raw/ping IPv6 protocols, initializes per-net IPv6 MIB/proc/sysctl state, attaches the Ethernet IPv6 packet receiver, and orchestrates full IPv6 stack initialization and rollback.

## Important APIs, Types, and Functions
- Protocol switch state: `inetsw6[SOCK_MAX]` and `inetsw6_lock` hold `struct inet_protosw` entries used by `inet6_create()`. `inet6_register_protosw()` and `inet6_unregister_protosw()` are exported for protocols to add/remove socket handlers.
- Module parameters/defaults: `ipv6_defaults`, `disable_ipv6_mod`, `disable_ipv6`, and `autoconf` influence global IPv6 enablement and addrconf default behavior.
- Socket lifecycle: `inet6_create()`, `inet6_sock_destruct()`, `inet6_release()`, and `inet6_cleanup_sock()` allocate sockets, initialize IPv6 and IPv4-compatible fields, run protocol init, and release multicast, anycast, flowlabel, rx option, rx PMTU, and tx option state.
- Bind/name APIs: `__inet6_bind()`, `inet6_bind_sk()`, `inet6_bind()`, and `inet6_getname()` implement AF_INET6 bind semantics, v4-mapped support, scope-id handling, nonlocal bind policy, BPF hooks, and getsockname/getpeername.
- Operation tables: `inet6_stream_ops` and `inet6_dgram_ops` expose socket operations for stream and datagram protocols.
- I/O and control: `inet6_sendmsg()`, `inet6_recvmsg()`, `inet6_ioctl()`, and `inet6_compat_ioctl()` delegate to protocol methods, IPv6 route ioctl, addrconf address ioctl, SIT destination setup, and compat route conversion.
- Routing/options helpers: `inet6_sk_rebuild_header()` rebuilds cached IPv6 routes for connected sockets; `ipv6_opt_accepted()` decides whether received extension options should be surfaced.
- Namespace and stack init: `inet6_net_init()`, `inet6_net_exit()`, `ipv6_init_mibs()`, `ipv6_cleanup_mibs()`, `inet6_init()`, `ipv6_packet_init()`, and `ipv6_packet_cleanup()`.

## Control Flow
- `inet6_init()` is a `device_initcall`. It initializes protocol-switch lists and raw hash state, optionally exits early if the module is administratively disabled, then registers protocol slabs for TCPv6, UDPv6, rawv6, and pingv6.
- It initializes raw sockets before ICMP/IGMP/NDISC control sockets, registers PF_INET6 with `sock_register()`, registers per-net IPv6 state, initializes multicast routing, ICMPv6, neighbor discovery, IGMPv6, proc entries, IPv6 routing, flowlabels, anycast, addrconf, extension headers, fragmentation, UDP/TCP transports, packet receive hook, pingv6, CALIPSO, segment routing, RPL, IOAM, IGMP late init, and sysctls.
- Every init step has a reverse-order error label. Failure unwinds only components already initialized, unregisters rtnetlink handlers and PF_INET6, and unregisters protocol slabs.
- `inet6_create()` performs RCU lookup in the protocol switch table by socket type and requested protocol, tries module autoload twice for missing protocols, enforces raw-socket capability, allocates `struct sock`, initializes IPv6 defaults (`hop_limit`, multicast hops/loop/all, PMTU policy, flowlabel reflection, bindv6only), initializes IPv4-compatible fields, hashes fixed-number protocols, calls protocol-specific `init`, and runs cgroup socket-create BPF for userspace sockets.
- `__inet6_bind()` validates family, multicast/stream restrictions, privileged ports, socket state, v4-mapped/v6-only interactions, link-local scope-id requirements, device binding, local/nonlocal address policy through `ipv6_chk_addr()` or IPv4 address checks, updates IPv4 and IPv6 receive/source addresses, temporarily forces `sk_ipv6only` for non-any pure IPv6 binds, obtains the port, runs post-bind BPF, and sets userlocks.
- `inet6_ioctl()` routes IPv6 route add/delete to `ipv6_route_ioctl()`, address add/delete to `addrconf_add_ifaddr()` and `addrconf_del_ifaddr()`, SIT destination setup to `addrconf_set_dstaddr()`, and all other ioctls to protocol-specific handlers.

## State and Persistence Behavior
- Global in-memory state includes the protocol-switch lists, packet type registration, module parameters, and exported protocol op tables. Per-net state includes MIB allocations, IPv6 sysctls, proc entries, and flowlabel/idgen defaults.
- Per-socket state is stored in `struct ipv6_pinfo`, `struct inet_sock`, route cache, multicast/anycast lists, options, flowlabels, and BPF/userlock-observable fields.
- No disk persistence is implemented. Proc/sysctl entries reflect runtime namespace state and are cleaned up in `inet6_net_exit()` and init rollback.

## Dependencies and Integration Points
- Integrates nearly every IPv6 subsystem: TCPv6, UDPv6, rawv6, pingv6, ICMPv6, NDISC, IGMPv6, multicast routing, route tables, addrconf, anycast, flowlabels, extension headers, fragmentation, offload, CALIPSO, segment routing, RPL, IOAM, XFRM, cgroup BPF, LSM security flow classification, procfs, sysctl, and packet receive registration.
- Depends on `addrconf.c` for SIOCSIFADDR/SIOCDIFADDR/SIOCSIFDSTADDR and on `addrconf_core.c` address typing/bind helpers through `ipv6_addr_type()` and `ipv6_chk_addr()`.
- Exposes `inet6_stream_ops`, `inet6_bind`, `inet6_release`, `inet6_getname`, protocol-switch registration, and cleanup helpers to other kernel modules.

## Risks and Edge Cases
- Init/rollback ordering is critical. Later subsystems assume earlier control sockets, routes, proc state, packet hooks, and addrconf are available; rollback must mirror successful initialization exactly.
- Protocol-switch registration protects permanent entries from override and inserts new entries after the last permanent entry. Changing ordering can affect wildcard protocol resolution and module override behavior.
- Bind semantics are compatibility-sensitive: IPv4-mapped binds, v6-only sockets, link-local scope IDs, bound devices, nonlocal bind, BPF address mutation, and post-bind port rollback must remain aligned with AF_INET behavior.
- `IPV6_ADDRFORM` can change `sk->sk_prot`, so send/recv/ioctl paths intentionally `READ_ONCE()` the protocol pointer.
- Resource cleanup must drop option memory accounting, flowlabel lists, rx option SKBs, PMTU SKBs, multicast/anycast memberships, and per-net MIB/proc allocations without double-free.

## Test Signals
- Socket creation for TCP, UDP, raw, ping, wildcard protocol, unsupported protocol with module autoload, and raw capability failure.
- Bind tests for any, loopback, global, link-local with/without scope ID, multicast stream rejection, IPv4-mapped with v6-only on/off, bound device missing, nonlocal bind, privileged ports, `BIND_ADDRESS_NO_PORT`, and cgroup bind hooks.
- Ioctl tests for route add/delete, address add/delete, SIT destination address, compat route ioctl, and protocol-specific fallback.
- Init failure injection around each `inet6_init()` step to verify reverse cleanup and no leaked packet/proc/sysctl/proto registrations.
- Runtime observability through `/proc/net/{tcp6,udp6,anycast6,...}`, MIB counters, `ss -6`, `ip -6 route`, `ip -6 addr`, and packet receive on ETH_P_IPV6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/af_inet6.c -->
