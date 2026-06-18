# subset-b-000622 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_vport.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_vport.yaml

Purpose: this YAML describes the Open vSwitch vport generic-netlink legacy family, binding the userspace ABI in `linux/openvswitch.h` to generated netlink documentation and schema data. It models datapath vports, their tunnel options, upcall delivery, statistics, and notifications.

Important APIs, types, and functions: the top-level family is `ovs_vport` version 2 with fixed `ovs-header` containing `dp-ifindex`. The main enum is `vport-type` (`unspec`, `netdev`, `internal`, `gre`, `vxlan`, `geneve`). Attribute sets include `vport-options` (`dst-port`, `extension`), `upcall-stats` (`success`, `fail`), and `vport` attributes such as `port-no`, `type`, `name`, `options`, `upcall-pid`, `stats`, `ifindex`, `netnsid`, and nested `upcall-stats`. `ovs-vport-stats` carries packet, byte, error, and drop counters as 64-bit fields.

Control flow: generated consumers use `ovs-vport-cmd-new` to create vports with `name`, `type`, optional `upcall-pid`, `ifindex`, and tunnel `options`; `del` removes by `port-no`, `type`, or `name`; `get` supports both single lookup by name and dump. Replies return port identity, upcall state, interface indices, and counters. Multicast group `ovs_vport` is the integration point for asynchronous vport updates.

State and persistence: this file itself is declarative. Runtime state is owned by the OVS datapath in the kernel: vport membership, names, tunnel port options, upcall pids, namespace ids, and monotonically changing stats.

Dependencies and integration: depends on the generic netlink legacy generator, `linux/openvswitch.h`, and OVS datapath semantics. The schema is consumed by documentation/generation tooling and by userspace ABI readers such as OVS control utilities.

Risks: binary fields (`upcall-pid`, `stats`) rely on exact struct layout and endian expectations. The `dst-port` tunnel option is typed as `u32`, so callers must track kernel interpretation. Dumps must handle concurrent datapath mutation. Tests should validate generated enum values against `openvswitch.h`, create/get/delete vport round trips, nested tunnel option encoding, and stats/upcall-stats presence in dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/ovs_vport.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/psp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/psp.yaml

Purpose: this YAML defines the PSP Security Protocol generic-netlink family used to discover PSP-capable devices, configure accepted protocol versions, rotate device keys, bind Rx/Tx associations to sockets, and read PSP statistics.

Important APIs, types, and functions: the `version` enum distinguishes AES-GCM and AES-GMAC variants with 128-bit or 256-bit keys. Attribute set `dev` exposes `id`, `ifindex`, supported version bitmask, and enabled version bitmask. `assoc` contains `dev-id`, `version`, nested `rx-key`/`tx-key`, and `sock-fd`. Nested `keys` carries raw `key` and `spi`. `stats` contains device id plus kernel and device counters such as key rotations, stale events, authenticated packet/byte counts, auth failures, framing errors, miscellaneous Rx errors, and Tx errors.

Control flow: `dev-get` does lookup or dump under `psp-device-get-locked`/`psp-device-unlock`; device add/delete/change notifications publish to `mgmt`. `dev-set` is admin-only and changes enabled versions. `key-rotate` is admin-only and publishes `key-rotate-ntf` to `use`. `rx-assoc` allocates an Rx key/SPI pair and associates a socket; `tx-assoc` installs a caller-provided Tx key; both use `psp-assoc-device-get-locked`. `get-stats` reads per-device counters and supports dump.

State and persistence: kernel PSP devices persist while the netdevice/device exists. Enabled versions, key rotation state, associations, socket bindings, and statistics live in kernel memory and are guarded by the named pre/post lock hooks. The YAML is declarative and does not persist data.

Dependencies and integration: integrates with PSP kernel support, generic netlink code generation, socket file descriptor passing semantics, and two multicast groups (`mgmt` and `use`). Userspace managers must subscribe to notifications for hotplug and key rotation.

Risks: key material is transported as binary netlink payloads and must be length-checked according to `version`; stale sockets may lose Rx after full key rotation; admin-only operations must remain protected. Test signals include schema validation, min-check enforcement for ids, notification coverage, lock-hook generation, key rotation event delivery, and association tests with valid/invalid socket FDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/psp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-addr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-addr.yaml

Purpose: this raw rtnetlink schema documents address configuration messages for IPv4/IPv6 interface addresses and multicast addresses. It maps `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_GETADDR`, and multicast address dumping onto YAML netlink metadata.

Important APIs, types, and functions: fixed header `ifaddrmsg` carries address family, prefix length, `ifa-flags`, scope, and interface index. `ifa-cacheinfo` stores preferred/valid lifetimes and timestamps. `ifa-flags` defines secondary, nodad, optimistic, dadfailed, homeaddress, deprecated, tentative, permanent, managetempaddr, noprefixroute, mcautojoin, and stable-privacy. `addr-attrs` includes address, local, label, broadcast, anycast, cacheinfo, multicast, flags, route priority, target netns id, and protocol.

Control flow: `newaddr` value 20 adds or announces an address using address, label, local, and cacheinfo. `deladdr` value 21 removes an address by address/local. `getaddr` value 22 is dump-only and replies as value 20 with the common address attributes. `getmulticast` value 58 supports do and dump flows with multicast and cacheinfo replies.

State and persistence: interface address state is maintained by the networking stack and persists until deleted, interface teardown, namespace teardown, or address lifetime expiry. Cache info exposes lifetime and timestamp behavior but is not stored by this YAML.

Dependencies and integration: depends on `linux/rtnetlink.h`, raw netlink protocol number 0, generated schema consumers, and rtnetlink multicast groups `rtnlgrp-ipv4-ifaddr` and `rtnlgrp-ipv6-ifaddr` for change notifications.

Risks: address payloads are binary and family-dependent; broadcast is explicitly big-endian IPv4 while address/local are generic IPv4-or-IPv6. Dumps can race with concurrent address changes. Test signals include add/delete/dump round trips in a disposable namespace, IPv4/IPv6 payload rendering, flag bitmask validation, lifetime/cacheinfo formatting, and multicast notification observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-addr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-link.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-link.yaml

Purpose: this large raw rtnetlink schema documents link and link-stat operations over `linux/rtnetlink.h`. It is the netlink-spec description for creating, deleting, setting, dumping, and observing network devices plus nested link kinds, AF-specific settings, VF state, XDP data, bridge/bond/tunnel parameters, and link statistics.

Important APIs, types, and functions: fixed headers include `ifinfomsg`, `rtgenmsg`, and `if-stats-msg`. Definitions cover netdevice flags, VLAN protocol constants, 32-bit and 64-bit rtnl link stats, interface maps, IPv4/IPv6 device config arrays, IPv6 and ICMPv6 stats, VF structs, bridge ids, cacheinfo, netkit/openvpn modes, and bridge STP mode. The primary `link-attrs` set models the broad `IFLA_*` namespace, including interface identity (`ifname`, `alt-ifname`, `ifindex` through header), MTU, qdisc, master, namespaces, stats, stats64, `linkinfo`, AF-specific data, VF lists, XDP, carrier counters, parent device metadata, offload sizes, and min/max MTU. Secondary sets describe `linkinfo-*` per kind: bond, bridge, bridge port, GRE/GRE6, VTI/VTI6, Geneve, HSR, IP tunnel, IP6 tunnel, tun, VLAN, VRF, MCTP, netkit, and ovpn.

Control flow: `newlink` value 16 creates links with a large request attribute set including identity, namespace, linkinfo, VF data, XDP, protocol-down fields, parent metadata, queue counts, MTU bounds, and offload limits. `newlink-ntf` notifies link creation. `dellink` value 17 deletes by address, broadcast, ifname, linkinfo, netns fd/pid, and related metadata. `getlink` value 18 supports do lookup by names/ext-mask/netns and dump by target namespace, ext-mask, master, and linkinfo; replies are value 16 with the full link attribute set. `setlink` value 19 mutates link attributes. `getstats` value 94 returns value 92 with link64, xstats, slave xstats, offload xstats, and AF stats.

State and persistence: netdevice state lives in kernel network namespaces. Created devices, link kind options, VF settings, bridge/bond/tunnel parameters, XDP attachments, carrier counters, and stats persist according to device lifetime and kernel driver behavior. The YAML captures ABI shape, not storage.

Dependencies and integration: depends on rtnetlink raw protocol, `linux/rtnetlink.h`, `linux/if.h`, a large set of link-kind kernel implementations, and multicast groups `rtnlgrp-link` and `rtnlgrp-stats`. It is central to iproute2-like tooling and netlink code generators.

Risks: this file is high churn and easy to desynchronize from UAPI headers. Nested `sub-message`/kind dispatch must match kernel `IFLA_INFO_KIND` semantics. Many binary structs have strict layout and padding. Dumps can be partial or race with hotplug. Test signals include generator schema validation, enum/value parity with UAPI headers, network-namespace round trips for representative link kinds, XDP and VF attribute smoke tests where supported, stats dump decoding, and notification subscription checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-link.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-neigh.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-neigh.yaml

Purpose: this raw rtnetlink schema describes IP neighbour and forwarding database management plus neighbour-table dump/set operations.

Important APIs, types, and functions: `ndmsg` is the main fixed header, carrying family, ifindex, neighbour state, neighbour flags, and route message type. `ndtmsg` is used for table operations. Definitions include NUD states, neighbour flags (`use`, `self`, `master`, `proxy`, `ext-learned`, `offloaded`, `sticky`, `router`), extended flags (`managed`, `locked`, `ext-validated`), `rtm-type`, neighbour cacheinfo, table config, and table stats. `neighbour-attrs` contains destination, link-layer address, cacheinfo, probes, VLAN/VNI/port, ifindex/master, namespace id, protocol, nexthop id, FDB extension data, extended flags, and masks. `ndt-attrs` and `ndtpa-attrs` expose neighbour table thresholds and per-interface timing/queue parameters.

Control flow: `newneigh` value 28 adds entries; `delneigh` value 29 removes by destination and ifindex; deletion and creation notifications reuse `getneigh`. `getneigh` value 30 does single lookup by destination and dumps by ifindex/master. `getneightbl` value 66 dumps tables with reply value 64. `setneightbl` value 67 mutates table thresholds, parameters, and GC interval.

State and persistence: neighbour entries live in per-namespace neighbour tables and may be static, learned, offloaded, or garbage-collected depending on state and flags. Table parameters persist until changed or namespace/device teardown.

Dependencies and integration: depends on `linux/rtnetlink.h`, ARP/ND/FDB kernel internals, bridge/VXLAN offload users, and multicast group `rtnlgrp-neigh`.

Risks: FDB and IP neighbour use the same message family but interpret fields differently. Extended flags and masks need careful compatibility handling. Test signals include neighbour add/delete/get in an isolated namespace, bridge FDB entries with VLAN/VNI if supported, table dump parsing, table parameter mutation tests, and notification observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-neigh.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-route.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-route.yaml

Purpose: this raw rtnetlink schema documents route configuration and route dumps for `RTM_GETROUTE`, `RTM_NEWROUTE`, and `RTM_DELROUTE`.

Important APIs, types, and functions: `rtmsg` is the fixed route header with family, destination/source prefix lengths, TOS, table, protocol, scope, route type, and flags. `rtm-type` enumerates unicast, local, broadcast, anycast, multicast, blackhole, unreachable, prohibit, throw, nat, and xresolve. `route-attrs` includes destination/source, input/output interface, gateway, priority, preferred source, nested metrics, multipath, table, mark, multicast forwarding stats, via/newdst, preference, encapsulation type/data, expiry, uid, TTL propagation, protocol and port selectors, nexthop id, and IPv6 flowlabel. Nested `metrics` maps RTAX lock, MTU, window, RTT, RTT variance, ssthresh, cwnd, advmss, reordering, hoplimit, initcwnd/initrwnd, features, rto-min, quickack, congestion-control algorithm, and fastopen-no-cookie.

Control flow: `getroute` value 26 supports a do lookup using selectors (`src`, `dst`, interfaces, protocol, ports, mark, uid, flowlabel) and a full dump with no attributes; replies are value 24 with all route attributes. `newroute` value 24 creates routes using the full attribute set. `delroute` value 25 deletes using the same set.

State and persistence: routes live in per-namespace FIB tables and persist until deletion, namespace teardown, device removal, or protocol owner cleanup. Metrics and encapsulation state are route attributes owned by the kernel routing stack.

Dependencies and integration: depends on `linux/rtnetlink.h`, FIB, nexthop, tunnel encapsulation, multipath, and iproute2-style route management.

Risks: many attributes are family-specific or table/protocol-specific; `multipath`, `via`, `encap`, and `mfc-stats` are binary and need external struct knowledge. Test signals include IPv4/IPv6 route add/get/del in a netns, metric nesting validation, route lookup with UID/ports/mark, and schema value parity with UAPI message numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-route.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-rule.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-rule.yaml

Purpose: this raw rtnetlink schema documents FIB rule management, including rule creation, deletion, dumps, and IPv4/IPv6 rule notifications.

Important APIs, types, and functions: `fib-rule-hdr` is the fixed header with family, destination/source lengths, TOS, table, action, and flags. `fr-act` covers unspecified, table lookup, goto, nop, blackhole, unreachable, and prohibit actions. `fib-rule-port-range` and `fib-rule-uid-range` model selector ranges. `fib-rule-attrs` includes destination/source, input/output interface names, goto target, priority, fwmark/fwmask, flow, tunnel id, suppressors, table, l3mdev, UID range, protocol, IP protocol, sport/dport ranges, DSCP, flowlabel and masks.

Control flow: `newrule` value 32 adds a FIB rule with the full selector/action attribute set; `newrule-ntf` publishes creation notifications via `getrule`. `delrule` value 33 removes a matching rule and `delrule-ntf` announces deletion. `getrule` value 34 dumps rules and replies as value 32.

State and persistence: rules live in per-network-namespace FIB rule lists, ordered primarily by priority. They persist until deletion, namespace teardown, or owning protocol cleanup.

Dependencies and integration: depends on `linux/fib_rules.h`, rtnetlink raw protocol, policy routing, l3mdev, tunnel metadata selectors, and multicast groups `rtnlgrp-ipv4-rule` and `rtnlgrp-ipv6-rule`.

Risks: selector masks and ranges must match kernel support by address family; priority collisions and action semantics can affect routing globally inside a namespace. Test signals include netns add/delete/dump of rules with fwmark, UID range, port range, DSCP/flowlabel selectors, and multicast notification checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/rt-rule.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/tc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/tc.yaml

Purpose: this large raw rtnetlink schema documents traffic-control qdisc, class, filter, chain, action, option, and statistics ABI data over `linux/pkt_cls.h`.

Important APIs, types, and functions: the fixed header `tcmsg` carries family, ifindex, handle, parent, and info. Definitions model qdisc/classifier structs and xstats for CBS, ETF, FIFO, HTB, GRED, HFSC, MQPRIO, MULTIQ, NETEM, PLUG, PRIO, RED, SFB, SFQ, TBF, generic stats, u32 selectors, action timestamps, police, pedit, MPLS, VLAN, and many queue-specific stats. Attribute set `attrs` covers common TCA attributes such as kind, options, stats, xstats, rate, fcnt, stats2, stab, chain, block ids, dump flags, and invisible dump control. Numerous `*-attrs` sets represent action (`act-bpf`, `act-ct`, `act-mirred`, `act-vlan`, etc.), classifier (`flower`, `bpf`, `u32`, `matchall`, `basic`, etc.), and qdisc (`cake`, `fq`, `fq-codel`, `taprio`, `netem`, `red`, `tbf`, etc.) options. Sub-message formats dispatch option parsing based on `kind`, and app stats dispatch by qdisc kind.

Control flow: operations use directional rtnetlink values. `newqdisc` 36 creates qdiscs; `delqdisc` 37 deletes; `getqdisc` 38 retrieves/dumps and replies as 36. Class operations use 40/41/42, filter operations use 44/45/46, and chain operations use 100/101/102. Create-style requests use `kind`, `options`, rate, chain, and block attributes; replies return common stats and option fields. `gettfilter` dump supports chain and dump flags. Multicast group `rtnlgrp-tc` carries traffic-control notifications.

State and persistence: qdiscs, classes, filters, chains, blocks, and actions live in kernel networking state attached to devices or shared blocks. Counters and xstats are mutable runtime state and can be offloaded to hardware depending on flags and driver support.

Dependencies and integration: depends on rtnetlink, `linux/pkt_cls.h`, `linux/rtnetlink.h`, kernel qdisc/classifier/action modules, hardware offload paths, and user tools such as `tc`.

Risks: the schema spans many independent kernel modules and can drift quickly. `options-msg`, `act-options-msg`, and stats sub-message dispatch must align exactly with string `kind` names. Many fixed headers are binary UAPI structs with padding and signedness constraints. Test signals include schema generation, qdisc/filter/class round trips in a netns, representative kind coverage for simple and nested options, dump parsing, action nesting, hardware-skip flag behavior, and UAPI enum/value comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/tc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/tcp_metrics.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/tcp_metrics.yaml

Purpose: this generic-netlink legacy schema documents the TCP metrics management interface: retrieving cached destination metrics and deleting them.

Important APIs, types, and functions: family metadata uses `tcp-metrics-genl-name`, `tcp-metrics-genl-version`, `max-by-define`, and a global kernel policy. The constant `tcp-fastopen-cookie-max` is 16. Attribute set `tcp-metrics` includes destination and source IPv4/IPv6 addresses, age, nested metric values, Fast Open MSS, SYN drop counters/timestamp, Fast Open cookie, and padding. Nested `metrics` contains RTT, RTT variance, ssthresh, cwnd, reordering, RTT in microseconds, and RTT variance in microseconds; the file notes metric attribute numbers are offset from kernel `TCP_METRIC_*` enum names.

Control flow: `get` accepts destination/source address selectors and returns address identity, age, metric values, and Fast Open state; it supports dumps. `del` is admin-only and deletes matching metrics using the same selectors. Both disable strict/dump validation for compatibility with legacy behavior.

State and persistence: TCP metrics live in the kernel TCP metrics cache and change as connections update route/destination performance data. Entries age out or are deleted by the admin operation.

Dependencies and integration: depends on the generic netlink legacy family, TCP metrics cache internals, and Fast Open state. Userspace diagnostics and cleanup tools consume this ABI.

Risks: the intentionally offset metric numbering is easy to mis-generate. The attribute `reodering` appears misspelled in the schema and likely mirrors ABI naming or an existing typo. Fast Open cookie length uses `min-len` rather than exact length. Test signals include get/dump decoding, delete permission checks, IPv4/IPv6 selector coverage, metric numbering parity tests, and compatibility checks for non-strict validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/tcp_metrics.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/team.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/team.yaml

Purpose: this generic-netlink legacy schema documents the network team driver family, covering option management, port listing, and change-event integration.

Important APIs, types, and functions: family metadata points to `team-genl-name`, `team-genl-version`, global kernel policy, and `linux/if_team.h`. Constants include string max length 32 and multicast group name `change_event`. The top-level `team` attribute set contains `team-ifindex`, nested option list, and nested port list. Option list entries nest `attr-option` fields: option name, changed/removed flags, type, raw data, per-port ifindex, and array index. Port list entries nest `attr-port`: ifindex, changed/linkup/removed flags, speed, and duplex.

Control flow: `noop` value 0 returns the family/team ifindex. `options-set` is admin-only and sends `team-ifindex` plus option list, with an echo-like reply. `options-get` is admin-only and fetches options for a team ifindex. `port-list-get` is admin-only and fetches port information.

State and persistence: team device state, options, and ports are owned by the team driver and persist while the team interface exists. The schema documents change flags but does not implement storage.

Dependencies and integration: depends on the generic netlink legacy team family, team kernel driver, `linux/if_team.h`, and userspace team management daemons/tools.

Risks: option `data` is binary and typed by a separate `type` field, so consumers must decode per option. `dont-validate: strict` indicates legacy messages may not pass modern strict policy. Test signals include option get/set round trips on a team device, nested list parsing, per-port option handling, port list dump, and change-event notification monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/team.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/wireguard.yaml -->
# sources/distributed-fs/ceph-client/Documentation/netlink/specs/wireguard.yaml

Purpose: this generic-netlink legacy schema documents the WireGuard device control ABI for retrieving and setting interface, peer, and allowed-IP configuration.

Important APIs, types, and functions: constants include `wg-key-len` of 32 bytes. Struct `--kernel-timespec` models handshake time. Flags include device `replace-peers`, peer `remove-me`, `replace-allowedips`, `update-only`, and allowed-IP `remove-me`. Attribute sets are hierarchical: `wgdevice` has ifindex/ifname, private/public keys, flags, listen port, fwmark, and indexed-array `peers`; `wgpeer` has public/preshared keys, flags, endpoint, keepalive interval, last handshake, byte counters, indexed-array allowed IPs, and protocol version; `wgallowedip` has family, IP address, CIDR mask, and flags.

Control flow: `get-device` value 0 is a dump operation requiring exactly one of ifindex or ifname. It may emit multiple `NLM_F_MULTI` messages; peers or allowed IP lists can be fragmented and must be coalesced by userspace. The final `NLMSG_DONE` carries a zero or negative errno. `set-device` value 1 accepts the device tree and may be sent in fragments when configuration exceeds max message size; replace flags should only appear in the first relevant fragment.

State and persistence: WireGuard device keys, listen port, fwmark, peer list, endpoints, counters, keepalive timers, and allowed IPs live in kernel WireGuard device state. Private/preshared keys can be cleared with all-zero payloads.

Dependencies and integration: depends on the WireGuard generic netlink family name/version, kernel netdevice instances, AF_INET/AF_INET6 endpoint and allowed-IP formats, and userspace tools such as `wg`.

Risks: key material is sensitive binary payload. Fragmented dump/set semantics require correct coalescing and careful use of replace flags. Interface selector exclusivity is semantic rather than represented as a YAML check. Test signals include get/set round trips, invalid key length rejection, peer/allowed-IP fragmentation tests, selector exclusivity tests, and counter/handshake decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/netlink/specs/wireguard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/device_drivers/atm/cxacru-cf.py -->
# sources/distributed-fs/ceph-client/Documentation/networking/device_drivers/atm/cxacru-cf.py

Purpose: this small Python utility converts a Conexant AccessRunner `cxacru-cf.bin` configuration blob from packed little-endian 32-bit words into the text format expected by the driver's sysfs `adsl_config` attribute.

Important APIs, types, and functions: it imports only `sys` and `struct`. The program reads from `sys.stdin` in 4-byte chunks, unpacks each chunk with `struct.unpack("<I", buf)[0]`, and writes `index=value` pairs to stdout with the value formatted in decimal and index in lowercase hexadecimal. Pairs are separated by spaces and terminated by a newline.

Control flow: a loop reads four bytes at a time. End-of-file with zero bytes exits normally. A partial final read writes a newline, emits an error to stderr, and exits with status 1. The index counter starts at zero and increments for every complete word.

State and persistence: there is no persistent state. Runtime state is the current word index and the output stream contents.

Dependencies and integration: integrates with shell pipelines: `cxacru-cf.py < cxacru-cf.bin` produces a string suitable for writing to sysfs. It relies on Python's binary stdin behavior and little-endian word layout documented in the header comments.

Risks: the script uses `sys.stdin.read(4)` without explicitly opening binary stdin; under Python 3 text mode can mishandle arbitrary binary data if invoked as `python3` despite the generic `python` shebang. The file is documentation-era utility code and warns about a known bad MD5/misaligned firmware blob. Test signals include converting a known sequence of little-endian words, partial trailing byte failure, empty input producing only newline, and execution under the intended Python interpreter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/device_drivers/atm/cxacru-cf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/hostapd.conf -->
# sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/hostapd.conf

Purpose: this is a minimal hostapd configuration for mac80211_hwsim testing. It starts a WPA2-PSK access point on simulated interface `wlan0`.

Important APIs, types, and functions: hostapd keys include `interface=wlan0`, `driver=nl80211`, `hw_mode=g`, `channel=1`, `ssid=mac80211 test`, `wpa=2`, `wpa_key_mgmt=WPA-PSK`, `wpa_pairwise=CCMP`, and `wpa_passphrase=12345678`.

Control flow: hostapd consumes this declarative file at startup, opens the nl80211 driver backend for `wlan0`, configures 2.4 GHz channel 1, advertises the SSID, and enables WPA2 personal authentication with CCMP.

State and persistence: the file itself is static. Runtime AP state, beaconing, association tables, and keys are held by hostapd and the mac80211_hwsim kernel module while the process is running.

Dependencies and integration: depends on `hostapd`, nl80211, cfg80211/mac80211, and a hwsim radio exposed as `wlan0`. It pairs with the sibling `wpa_supplicant.conf`, which uses the same SSID and passphrase.

Risks: fixed interface name, channel, SSID, and weak test passphrase make it suitable only for controlled test namespaces/labs. Interface naming may differ when multiple hwsim radios exist. Test signals include hostapd parsing, AP startup on `wlan0`, beacon visibility, and successful WPA2 association from the paired supplicant config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/hostapd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/wpa_supplicant.conf -->
# sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/wpa_supplicant.conf

Purpose: this is a minimal wpa_supplicant configuration for connecting a mac80211_hwsim station to the companion hostapd test AP.

Important APIs, types, and functions: it sets `ctrl_interface=/var/run/wpa_supplicant` and defines one `network` block with `ssid="mac80211 test"`, `psk="12345678"`, `key_mgmt=WPA-PSK`, `proto=WPA2`, `pairwise=CCMP`, and `group=CCMP`.

Control flow: wpa_supplicant parses the network block, scans for the SSID, performs WPA2-PSK authentication and four-way handshake, and then exposes control operations through the configured control interface path.

State and persistence: static config is stored in this file. Runtime state includes scan cache, association state, negotiated keys, and control socket state in `/var/run/wpa_supplicant`.

Dependencies and integration: depends on `wpa_supplicant`, nl80211/cfg80211, a station hwsim interface, and the companion hostapd config using matching SSID/passphrase/ciphers.

Risks: fixed credentials and control path are intended for local testing only. If the hwsim topology or interface names differ, the config alone is insufficient. Test signals include config parse success, association to the hostapd AP, WPA2 handshake completion, and `wpa_cli` visibility through the control interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/wpa_supplicant.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/scheduler/sched-pelt.c -->
# sources/distributed-fs/ceph-client/Documentation/scheduler/sched-pelt.c

Purpose: this C helper generates constants used by scheduler PELT load average calculations. It is documentation/support code, compiled manually with `-lm`, and prints C definitions rather than being linked into the kernel.

Important APIs, types, and functions: constants `HALFLIFE` and `SHIFT` are 32. Global `double y` stores the decay factor `pow(0.5, 1 / HALFLIFE)`. `calc_runnable_avg_yN_inv()` prints `runnable_avg_yN_inv[]`. `calc_runnable_avg_yN_sum()` can print accumulated sums but is disabled in `main`. `calc_converged_max()` iterates fixed-point decay until convergence and prints `LOAD_AVG_PERIOD` and `LOAD_AVG_MAX`. `calc_accumulated_sum_32()` is present but disabled. `main()` initializes `y`, prints a generated-by comment, emits inverse constants, and emits converged max.

Control flow: execution is deterministic: compute decay factor, print inverse powers for 32 periods, then iterate max update using a fixed-point inverse until the value stops changing.

State and persistence: mutable globals `sum`, `n`, and `max` hold intermediate generation state. No persistent state is written except stdout output when redirected.

Dependencies and integration: depends on libc, libm (`pow`), and the scheduler constants expected by kernel PELT code. It integrates by generating snippets copied into scheduler sources.

Risks: fixed-point rounding and host type widths matter; `1UL << 32` assumes `unsigned long` is wider than 32 bits. `void main(void)` is non-standard C. Disabled functions may diverge from current kernel needs. Test signals include compiling with warnings, comparing generated constants against checked-in scheduler constants, and running on 32-bit/64-bit build hosts if still supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/scheduler/sched-pelt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sound/cards/multisound.sh -->
# sources/distributed-fs/ceph-client/Documentation/sound/cards/multisound.sh

Purpose: this file is both a historical README for Turtle Beach MultiSound cards and a shell archive that extracts small utility programs for Pinnacle/Fiji firmware conversion and device configuration.

Important APIs, types, and functions: the README describes ALSA modules `snd-msnd-lib`, `snd-msnd-classic`, and `snd-msnd-pinnacle`, required options (`io`, `irq`, `mem`), and optional resources (`fifosize`, `calibrate_signal`, `digital`, `cfg`, `mpu_io`, `mpu_irq`, IDE and joystick settings). The shar payload creates `MultiSound.d/setdigital.c`, `pinnaclecfg.c`, `Makefile`, `conv.l`, and `msndreset.c`. `setdigital` uses OSS mixer ioctls to select `SOUND_MASK_DIGITAL1`; `msndreset` uses `SOUND_MIXER_PRIVATE1`; `pinnaclecfg` uses `ioperm`, `inb`, and `outb` to program non-PnP card logical devices; `conv.l` converts assembler DB hex bytes to binary firmware.

Control flow: the top half is human instructions. The executable archive half checks gettext/shar support, creates a lock directory, conditionally creates `MultiSound.d`, skips existing files unless `-c` is passed, writes each embedded file via here-doc/sed, restores timestamps/modes, validates with md5 or byte counts, and removes the lock directory. Extracted utilities have their own flows: command-line validation, hardware permission setup, register writes/reads, and ioctl calls.

State and persistence: running the archive writes files into `MultiSound.d`. Running `pinnaclecfg` changes ISA card hardware resource registers. Firmware files referenced by the README are placed outside the repo, commonly `/etc/sound`.

Dependencies and integration: depends on POSIX shell, sharutils conventions, optional GNU gettext/md5sum/touch, GCC/flex for utilities, legacy OSS sound headers, root privileges for port I/O, and the corresponding kernel sound drivers.

Risks: this is old hardware-facing code; wrong I/O/IRQ/memory values can hang a machine, as the README warns. The `cfg_ide` parser appears to read both `io0` and `io1` from `argv[0]`, likely a bug. The archive will create files in the current directory and should not be run casually. Test signals include dry extraction in a temp directory, checksum validation, compiling extracted utilities, static review of privileged I/O paths, and avoiding live hardware tests except on dedicated systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sound/cards/multisound.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/automarkup.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/automarkup.py

Purpose: this Sphinx extension performs kernel-specific automatic markup after doctree resolution. It converts plain text references to functions, C types, Documentation files, ABI symbols/files, and kernel commits into cross-reference nodes where possible.

Important APIs, types, and functions: regexes detect `function()`, `struct/union/enum/typedef` names, `Documentation/*.rst|txt`, ABI file paths, ABI symbols under `/sys`, `/config`, or `/proc`, C namespaces, and commit hashes. `markup_refs()` collects regex matches, sorts by source position, and emits replacement docutils nodes. `markup_func_ref_sphinx3()` and `markup_c_ref()` resolve C-domain references with namespace fallback. `markup_doc_ref()` and `markup_abi_ref()` resolve std doc/ref links. `add_and_resolve_xref()` constructs `pending_xref` and asks the domain to resolve it. `markup_git()` creates git.kernel.org commit links. `auto_markup()` walks paragraph text nodes while avoiding literals and existing references. `setup()` connects `doctree-resolved`.

Control flow: for each paragraph text node, the extension finds all possible references, emits normal text before each match, replaces matched text with either resolved references, broken-xref literal nodes, or original text, then updates the parent node.

State and persistence: global `failed_lookups` caches failed function targets; global `c_namespace` is updated per document. No disk state is written. ABI lookup is delegated to `kernel_abi.get_kernel_abi()`.

Dependencies and integration: depends on docutils nodes, Sphinx domains, `kernel_abi`, the C domain object inventory, and the builder's ability to resolve references. It is integrated through the Sphinx event system.

Risks: overlapping regex matches are not explicitly filtered; sorted matches can produce duplicated or out-of-order replacement text if patterns overlap in future cases. Global state can interact with parallel builds, though the extension declares parallel safe. Failed lookup caching may hide later targets added in the same build. Test signals include Sphinx builds with representative function/type/doc/ABI/commit text, literal/reference exclusion checks, namespace-specific C references, LaTeX builder behavior, and parallel build runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/automarkup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_abi.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_abi.py

Purpose: this Sphinx extension implements the `kernel-abi` reStructuredText directive, rendering parsed Linux ABI documentation into the Sphinx doctree.

Important APIs, types, and functions: module initialization reads `srctree` from the environment, adds `tools/lib/python` to `sys.path`, imports `abi.abi_parser.AbiParser`, and defines global ABI path `Documentation/ABI`. `get_kernel_abi()` lazily creates and parses a singleton `AbiParser`, then runs issue checks. `KernelCmd` is the directive class with required ABI path argument and options `debug`, `no-symbols`, and `no-files`. `run()` iterates `kernel_abi.doc()` records, optionally wraps generated reST in a code block, adds source dependencies via `env.note_dependency()`, and parses content symbol by symbol through `do_parse()`.

Control flow: Sphinx loads `setup()`, registers the directive, and later `KernelCmd.run()` validates file insertion, selects display mode, streams ABI parser output into `ViewList`, notes dependencies when input files change, nested-parses each symbol-sized chunk, logs summary counts, and returns section children.

State and persistence: `_kernel_abi` caches parsed ABI data for the process. Sphinx environment dependencies persist in the build environment cache. No source files are modified.

Dependencies and integration: depends on `srctree`, `tools/lib/python/abi/abi_parser.py`, docutils directive APIs, Sphinx logging, and `switch_source_input` for correct source attribution.

Risks: missing `srctree` fails at import time. The singleton parser may hold stale data if files change within one process. Large ABI output is parsed incrementally to avoid Sphinx parser limits, but errors still surface through nested parsing. Test signals include Sphinx builds using `kernel-abi`, debug/no-symbols/no-files combinations, dependency invalidation after ABI file edits, and import behavior when `srctree` is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_abi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_feat.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_feat.py

Purpose: this Sphinx extension implements the `kernel-feat` directive, rendering kernel feature matrix data from `Documentation/features` or a requested feature subdirectory.

Important APIs, types, and functions: it reads `srctree`, adds `tools/lib/python`, imports `feat.parse_features.ParseFeature`, defines `ErrorString()`, and registers `KernelFeat`. The directive accepts one required path argument and optional second architecture argument, with a `debug` option. `warn()` formats Sphinx warnings, though it is not used in the visible control path. `run()` creates `ParseFeature(feature_dir, False, True)`, parses features, emits either `output_arch_table(arch)` or `output_matrix()`, strips dependency marker lines matching `.. FILE <path>`, and nested-parses the generated reST. `nestedParse()` optionally wraps output in a code block for debug mode.

Control flow: during directive execution, feature files are parsed, generated text is scanned line by line, file marker lines become Sphinx dependencies via `env.note_dependency()`, and all other lines are parsed into a temporary section node returned to the doctree.

State and persistence: runtime state is local to directive execution. Sphinx dependency records persist in the build environment cache. No files are modified.

Dependencies and integration: depends on `srctree`, `tools/lib/python/feat/parse_features.py`, the Sphinx/docutils directive stack, and feature files under `Documentation/<argument>`.

Risks: missing `srctree` fails at import. The `buf` tuple in `nestedParse()` is assigned but unused, suggesting leftover code. `app.warn` used by `warn()` is deprecated/removed in newer Sphinx versions, though the method is not on the main path. Test signals include matrix and per-arch directive builds, debug rendering, dependency detection from `.. FILE` markers, and feature parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_feat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_include.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_include.py

Purpose: this Sphinx extension implements the `kernel-include` directive, a kernel-specific replacement for docutils include that expands environment variables, restricts includes to `srctree`, supports literal/code/range options, and can generate C data-structure cross references.

Important APIs, types, and functions: module initialization reads `srctree`, imports `kdoc.parse_data_structs.ParseDataStructs`, and defines regexes for reference cleanup, line-number TOC entries, and domain splitting. `KernelInclude` supports options for literal output, code highlighting, encoding, tab width, line ranges, start/end text filters, line numbering, CSS class, generated cross refs, broken-ref warnings, TOC generation, and exception files. Methods include `read_rawtext()`, `apply_range()`, `xref_text()`, `literal()`, `code()`, and `run()`. Module-level functions `fill_domain_info()`, `get_suggestions()`, `check_missing_refs()`, `merge_xref_info()`, and `init_xref_docs()` support warning on broken generated references. `setup()` registers events and the directive.

Control flow: `run()` resolves the requested path against `srctree`, rejects paths outside the source tree, records dependencies, applies docutils file-insertion checks, resolves the include path relative to the current document, and either generates parsed cross-reference text or reads raw file content, applies range filters, and returns code or literal nodes. Generated cross-ref mode parses a C file with optional exception rules and either inserts a parsed literal or a TOC. Missing-reference handling reports suggestions only for files tracked in `env._xref_files`.

State and persistence: Sphinx build state stores file dependencies and `_xref_files`. Module globals cache reported warnings, domain info, and reference inventories. The directive reads included files but does not write source files.

Dependencies and integration: depends on docutils, Sphinx event APIs, `srctree`, `tools/lib/python/kdoc/parse_data_structs.py`, code-block directive support, and Sphinx domains for reference suggestions.

Risks: in this local copy, `literal()` references `include_lines` without defining it, and `code()` references `rawtext` without accepting it as a parameter, while `run()` calls `self.code(path, tab_width, rawtext)` against a two-argument signature. Those are runtime defects for literal line numbering and code mode. `xref_text()` calls `self.apply_range(rawtext)` without assigning the returned value. Import fails if `srctree` is absent. Test signals include directive builds for literal, code, range filters, generated cross refs with TOC, broken-ref warnings, parallel Sphinx merge behavior, and path traversal rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/kernel_include.py -->
