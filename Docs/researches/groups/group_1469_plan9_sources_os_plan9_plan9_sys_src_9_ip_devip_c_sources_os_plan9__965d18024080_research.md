# Group Research: group_1469_plan9_sources_os_plan9_plan9_sys_src_9_ip_devip_c_sources_os_plan9__965d18024080

Scope: `Docs/research_subset_a.md`, Plan 9 IP stack files under `sources/os/plan9/plan9/sys/src/9/ip`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/devip.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/devip.c

Implements the Plan 9 `#I` IP device namespace and the generic filesystem-facing control plane for IP protocols.

Key responsibilities:
- Builds qid layout for top-level files (`arp`, `bootp`, `ndb`, `iproute`, `ipselftab`, `log`), protocol directories, conversation directories, and per-conversation files (`ctl`, `data`, `err`, `listen`, `local`, `remote`, `status`, `snoop`).
- Lazily creates per-device `Fs` stacks in `ipgetfs`, initializes IP, ARP, logging, and registered protocol initializers.
- Handles attach, walk, stat, open, close, read, block read, write, block write, and wstat for the IP namespace.
- Owns conversation cloning through `Fsprotoclone`, including queue creation/reopen, owner/permission initialization, route cache reset, local/remote address defaults, TTL/TOS defaults, and per-protocol create hooks.
- Provides shared connect/announce/bind helpers: `Fsstdconnect`, `Fsstdannounce`, `Fsstdbind`, local/remote address parsing, local port selection, restricted port handling, and unique tuple checks.
- Implements listen queue handling through `Fsnewcall` and `listen` file opens.
- Routes ctl commands such as `connect`, `announce`, `bind`, `ttl`, `tos`, `ignoreadvice`, multicast add/remove, and `maxfragsize`, with fallback to protocol-specific ctl handlers.
- Supports `ndb` writes with version/mtime tracking and route tags via `IPaux`.

Notable design:
- Protocols register a `Proto` with callbacks and conversation limits through `Fsproto`.
- `Fsrcvpcol` routes inbound packets to `ipmux` when installed, otherwise directly to the IP protocol table.
- Conversation lifecycle is reference-counted by opens; last close resets owner, permissions, multicast memberships, protocol state, and queues.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/devip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/eipconvtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/eipconvtest.c

Standalone test program for the IP/Ethernet formatting conversion logic.

Key behavior:
- Defines local `eipconv` formatter for `%E`, `%I`, `%i`, `%V`, and `%M`.
- Formats Ethernet addresses, IPv4-mapped IPv6 addresses, IPv6 addresses with longest-zero-run elision, IPv4 addresses, and masks as either prefix lengths or full IP strings.
- Includes `prefixvals` and test vectors for IPv4-mapped addresses, all-ones masks, prefix masks, zero masks, and sparse IPv6 values.
- `main` installs `%I` and `%M`, then prints each test vector as an address and mask.

Notable use:
- Mirrors kernel formatter behavior in a user-space style test harness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/eipconvtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/esp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/esp.c

Implements IPsec Encapsulating Security Payload for IPv4 and IPv6, focused on tunnel mode.

Key responsibilities:
- Registers protocol `esp` for IP protocol number 50.
- `espconnect` binds a remote address and SPI, or allocates a random inbound SPI when `*` is supplied.
- Maintains per-conversation `Espcb` state: direction, optional user header mode, SPI, sequence, cipher algorithm/state, auth algorithm/state, IV/block/auth lengths, and function pointers.
- `espkick` encapsulates outgoing packets: optional user header parsing, ESP padding/trailer, encryption, ESP header construction, authentication, and dispatch through `ipoput4` or `ipoput6`.
- `espiput` receives ESP packets: determines IP version, extracts SPI/address tuple, finds inbound conversation, authenticates, decrypts, strips ESP/IP headers and trailer, optionally prepends user header, and queues plaintext.
- `espctl` supports `esp <alg> <key>`, `ah <alg> <key>`, `header`, and `noheader`.
- `espadvise` maps ICMP/ICMPv6 errors to matching ESP conversations.
- `espstats`, `esplocal`, and `espremote` expose status.

Algorithms:
- Encryption: `null`, `des_56_cbc`, `des3_cbc`, `aes_128_cbc`, `aes_ctr`.
- Authentication: `null`, `hmac_sha1_96`, `aes_xcbc_mac_96`, `hmac_md5_96`.
- Includes local HMAC-MD5/SHA1 helpers and Plan 9 libsec AES/DES setup.

Notable constraints:
- Comments state tunnel mode only; transport mode is TODO.
- Block lists are concatenated before cryptographic processing where needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/esp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ethermedium.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ethermedium.c

Implements Ethernet and gigabit Ethernet IP media bindings.

Key responsibilities:
- Defines `ethermedium` and `gbemedium` with Ethernet header sizes, MTUs, MAC length, bind/unbind/write, multicast, address-resolution, registration, and IPv6 prefix-to-EUI-64 callbacks.
- `etherbind` opens device conversations for IPv4 (`0x800`), ARP (`0x806`), and IPv6 (`0x86DD`), makes IP channels nonblocking, reads device stats to obtain MAC address and speed, stores channels in `Etherrock`, and starts IPv4, IPv6, and ARP reader kprocs.
- `etherunbind` posts notes to reader processes, waits for shutdown, closes channels, and frees state.
- `etherbwrite` resolves destination MAC via ARP/ND cache, handles broadcast/multicast resolution, sends ARP or neighbor solicitations when unresolved, pads/concats blocks, fills Ethernet headers, and writes to the proper device channel.
- `etherread4` and `etherread6` strip Ethernet headers and hand packets to `ipiput4`/`ipiput6`.
- Implements IPv4 ARP request/reply handling, gratuitous ARP, duplicate address warnings, proxy ARP checks, and ARP cache updates.
- Implements IPv6 address resolution by sending neighbor solicitations.
- Maps IPv4 and IPv6 multicast IP addresses to Ethernet multicast MAC addresses.
- `etherpref2addr` builds an IPv6 interface identifier from a MAC address.

Notable design:
- ARP and IPv6 neighbor discovery integrate with the common ARP cache abstraction.
- Broadcast/multicast destinations bypass ordinary unresolved ARP wait by synthesizing MAC entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ethermedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/gre.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/gre.c

Implements Generic Routing Encapsulation over IPv4.

Key responsibilities:
- Registers protocol `gre` for IP protocol number 47.
- `greconnect` uses standard IP connect parsing, then rejects duplicate remote address/protocol conversations.
- `grecreate` sets up a packet read queue and bypass write path.
- `grekick` builds outgoing IPv4/GRE packets, supports raw and cooked modes, fills source/destination addresses and encapsulated protocol, and sends through `ipoput4`.
- `greiput` receives GRE packets, normalizes block lists, parses optional checksum/routing/key/sequence fields, matches forwarding retunnel sessions first, then raw/conversation sessions, trims IP header, and queues payload.
- Supports specialized retunneling state: home address, north/south endpoints, care-of address, sequence numbers, downlink/uplink suspension, uplink key, pending and buffered ring queues.
- Control commands include `raw`, `cooked`, `retunnel`, `report`, `dlsuspend`, `ulsuspend`, `dlresume`, `ulresume`, `forward`, and `ulkey`.
- `grestats` reports packet and byte counters plus length errors.

Notable behavior:
- Uses bounded power-of-two rings for pending/buffered retunnel packets and drops oldest entries on overflow.
- Avoids forwarding while holding retunnel locks where possible, at the cost of explicit race handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/gre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/icmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/icmp.c

Implements ICMPv4 as a devip protocol.

Key responsibilities:
- Registers protocol `icmp` for IP protocol number 1.
- Creates read queues and bypass write handling.
- Uses standard connect/announce helpers for addressing and conversation setup.
- `icmpkick` fills IPv4 and ICMP fields, sets local/remote addresses, writes ICMP id from local port, computes checksum, updates stats, and sends via `ipoput4`.
- Emits ICMP TTL exceeded, destination/port unreachable, and fragmentation-needed messages for IPv4 stack error paths.
- `icmpiput` validates length and checksum, counts message types, replies to echo requests, maps unreachable/time-exceeded payloads to protocol `advise` callbacks when possible, and otherwise delivers matching ICMP packets to conversations.
- `icmpadvise` hangs up matching ICMP conversations on lower-layer advice.
- `icmpstats` reports aggregate and per-type in/out counters.

Notable design:
- Conversation matching for received ICMP uses ICMP id plus remote address.
- Error advice unwraps the embedded original IP header to find the affected protocol.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/icmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/icmp6.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/icmp6.c

Implements ICMPv6, including neighbor discovery support.

Key responsibilities:
- Registers protocol `icmpv6` for next-header 58.
- Creates read/write queues and supports a `headers` ctl mode where user data supplies explicit IPv6 source/destination addresses.
- Computes ICMPv6 checksums by temporarily treating the IPv6 header as a pseudoheader.
- Sends echo replies, neighbor solicitations, neighbor advertisements, host unreachable, TTL exceeded, and packet-too-big messages.
- `valid` verifies ICMPv6 length/checksum and applies RFC 2461-style checks for neighbor solicit/advert, router solicit/advert, hop limit, code, target address, and option lengths.
- `icmpiput6` dispatches echo requests, unreachable/time-exceeded advice, router solicit/advert delivery, neighbor solicitation responses, duplicate-address-discovery-relevant neighbor advertisements, packet-too-big, and default queued delivery.
- Integrates with ARP/ND cache via `arpenter` for IPv6 neighbor entries.
- `icmpstats6` reports aggregate and per-type counters.

Notable behavior:
- Neighbor solicitation for tentative local addresses is treated specially for duplicate address detection.
- Link-local and multicast-specific validation is enforced for ND control messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/icmp6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/igmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/igmp.c

Implements an unfinished IGMPv1-style multicast group management protocol.

Key responsibilities:
- Defines IGMP packet format, report scheduling structures, global report state, and basic stats.
- `igmpsendreport` builds and sends a membership report to the all-systems multicast address with TTL 1.
- `igmpproc` sleeps until reports are queued, walks report lists, waits randomized tick counts, sends pending reports, and frees completed multicast entries.
- `igmpiput` validates incoming IGMP length, version/type, checksum, handles queries by scheduling reports for multicast groups, and handles reports by suppressing duplicate local reports for the same group.
- `igmpstats` returns query/report receive/send counts.
- `igmpinit` registers protocol `igmp`, installs `igmpreportfn`, and starts the report process.

Notable constraint:
- File header explicitly marks the implementation unfinished.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/igmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/inferno.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/inferno.c

Provides small compatibility shims shared between Plan 9 and Inferno variants.

Functions:
- `commonuser` returns `up->user`.
- `commonerror` returns `up->errstr`.
- `bootpread` is a stub returning 0.

Notable use:
- `devip.c` uses `commonuser` for channel attach ownership.
- `bootpread` backs the `bootp` file in this Plan 9 source variant but provides no data here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/inferno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ip.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ip.c

Implements core IPv4 stack operations plus shared IP initialization.

Key responsibilities:
- Initializes IPv4/IPv6 fragment pools and IPv6 parameter defaults.
- Tracks MIB-II style IP counters.
- `iprouting` toggles forwarding behavior.
- `ipoput4` performs IPv4 output: length validation, route lookup, gateway/interface selection, TTL/TOS/header setup, checksum generation, MTU selection, DF handling, fragmentation, and medium write.
- `ipiput4` performs IPv4 input: version dispatch to IPv6 if needed, header pullup, checksum validation, local-address check, option stripping for local delivery, forwarding path, TTL exceeded handling, optional reassembly before forwarding, local fragment reassembly, and protocol dispatch.
- `ip4reassemble` maintains reassembly queues keyed by source/destination/id, trims overlaps, times out old queues, and returns complete packet block lists.
- `ipfragfree4` and `ipfragallo4` manage IPv4 fragment queue allocation.
- `ipcsum` computes IPv4 header checksums.

Notable design:
- Route results may be cached in `Conv`.
- Fragment metadata is stored in space before block data using `Ipfrag`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ip.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ip.h

Central header for the Plan 9 IP stack.

Key definitions:
- Core constants for address lengths, IPv4 offsets, protocol counts, channel counts, TTL/TOS defaults, IP versions, IPv4 header size, fragmentation flags, and route-tree sizing.
- Conversation states: `Idle`, `Announcing`, `Announced`, `Connecting`, `Connected`.
- IP stats enum matching counters emitted by `ipstats`.
- Fragment queue structures for IPv4 and IPv6 plus `Ipfrag` metadata layout.
- `IP` per-stack state: stats, fragment locks/free lists, fragment IDs, and routing flag.
- Wire `Ip4hdr`.
- `Conv` conversation object: addressing, ports, ownership, permissions, queues, listen queue, multicast bindings, protocol-private storage, and route cache.
- `Medium` media driver interface with bind/unbind/write, multicast, route propagation, address resolution, registration, prefix-to-address, and unbind policy hooks.
- `Iplifc`, `Iplink`, `Ipifc`, and `Ipmulti` for physical/logical interface and multicast bookkeeping.
- `Ipht` conversation hash-table declarations and match classes.
- `Proto` protocol registration callback table.
- `Fs` per-IP-stack container for protocols, ARP, self table, routes, log, IPv6 params, and ndb data.
- Router/host IPv6 parameter structures.
- Route tree, IPv4/IPv6 route payloads, and route type bits.
- `IPaux` channel auxiliary state used by devip and route tagging.
- ARP entry layout and public function prototypes across the stack.

Notable design:
- IPv4 is represented as IPv4-mapped 16-byte addresses throughout much of the stack.
- `Fs` contains several documented “kludge” pointers for `ipifc`, `ipmux`, and self-table access, reflecting tight coupling among stack modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipaux.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipaux.c

Provides shared IP utility data and helpers.

Key responsibilities:
- Defines IPv6 header type names and well-known IPv6 addresses/masks: unspecified, loopback, link-local, multicast, all-nodes/all-routers node/link scopes, solicited-node multicast.
- `ptclcsum` computes protocol checksums across block chains, handling odd byte alignment and multi-block carry folding.
- `ipv62smcast` maps an IPv6 address to its solicited-node multicast address.
- `parsemac` parses colon-separated hex MAC addresses.
- Implements connection hash helpers: `iphash`, `iphtadd`, `iphtrem`, and `iphtlook`.
- `iphtlook` applies precedence for exact connected 4-tuple, announced local address+port, port-only, address-only, and wildcard matches.

Notable design:
- The hash table stores match class at insertion time based on how specific a conversation’s local/remote tuple is.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipifc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipifc.c

Implements the `ipifc` protocol: interface binding, address management, local self-cache, multicast, and IPv6 autoconfiguration controls.

Key responsibilities:
- Maintains registered `Medium` implementations and looks them up by name.
- `ipifcbind` attaches an interface conversation to a medium, calls medium bind, initializes MTUs/router-advertisement defaults, increments interface generation, and reopens queues.
- `ipifcunbind` removes logical interfaces, routes, self-cache entries, medium bindings, and closes queues.
- Reports interface state and local self-cache links through `status`/`local`.
- `ipifckick` passes packets written to an interface’s `data` file to the medium `pktin` hook.
- `ipifcadd` parses address/mask/remote/MTU/proxy arguments, adds logical interfaces, local routes, self-cache entries, broadcast/multicast entries, IPv6 solicited-node multicast entries, and optional duplicate-address-detection solicitation.
- `ipifcrem` and `ipifcremlifc` remove logical addresses and their routes/self-cache links.
- Propagates route additions/removals to media that provide route hooks.
- Supports ctl commands: `add`, `try`, `remove`, `unbind`, `joinmulti`, `leavemulti`, `mtu`, `reassemble`, `iprouting`, `add6`, and `ra6`.
- Owns `Ipselftab`, used by `ipforme`, `iptentative`, `ipselftabread`, and route/interface selection.
- Selects local source addresses with IPv4/IPv6 scope and preferred-lifetime logic in `findlocalip`.
- Handles multicast membership records per conversation and maps them onto interface self-cache entries.
- Registers proxy addresses for ARP/ND on appropriate interfaces.
- `ipifcadd6` builds an IPv6 address from a prefix and medium-provided MAC-derived interface identifier.

Notable design:
- Removed self-cache links are delayed before free to reduce lock contention with readers.
- A null/unspecified address in self-cache enables accept-all behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipifc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipmux.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipmux.c

Implements a packet filter/demultiplexer protocol that can intercept IP packets before normal protocol dispatch.

Key responsibilities:
- Parses semicolon-separated filter expressions such as `proto=17`, `src=...`, `dst=...`, `ifc=...`, `iph[...]`, and `data[...]`, with optional masks and value alternatives.
- Represents filters as ordered decision trees (`Ipmux`) with yes/no branches, comparison type specialization, masks, values, refcounts, and target conversations.
- Canonicalizes filter chains by field type, offset, length, and mask specificity.
- Merges new filters into the global demux tree and removes them on close.
- `ipmuxconnect` installs a filter tree and connects the conversation.
- `ipmuxiput` evaluates inbound packets against installed filters; matching packets are delivered to the conversation with interface address prepended. Nonmatching packets fall back to normal protocol dispatch via `t2p`.
- `ipmuxkick` sends fully formed IPv4 or IPv6 packets written by users back down the stack.
- `ipmuxstate` and `ipmuxstats` print installed filter trees.

Notable constraints:
- Comments note no protection against overlapping specs.
- Filtering is heavily IPv4-header oriented, though output dispatch can handle IPv6 by version.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipmux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/iproute.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/iproute.c

Implements IPv4 and IPv6 route tables, lookup, readout, and route control writes.

Key responsibilities:
- Stores routes in per-bucket balanced range trees with `left`, `right`, and `mid` branches for disjoint and nested ranges.
- Keeps global freelists for IPv4 and IPv6 route node allocation.
- Adds IPv4 routes with `v4addroute` and IPv6 routes with `v6addroute`, computing address ranges from masks and inserting into all affected root buckets.
- Handles equal routes by superseding non-interface routes or refcounting interface routes.
- Deletes routes with `v4delroute`/`v6delroute`, reinserting child subtrees when a node is removed.
- Looks up longest/nested matching routes with route-generation caching in `Conv`.
- Resolves stale route interface pointers by finding the appropriate `Ipifc`.
- Converts routes to printable address/mask/gateway/type/tag/interface records.
- `routeread` walks both IPv4 and IPv6 route forests for `/net/iproute`.
- `routewrite` supports `flush`, `remove`, `add`, `tag`, and `route` control commands.
- Propagates route changes to interface media hooks.

Notable design:
- Route tags are four-character fields carried by channel `IPaux`.
- IPv4 lookups are also used for IPv4-mapped IPv6 addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/iproute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipv6.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipv6.c

Implements core IPv6 output, input, extension-header handling, and fragment reassembly.

Key responsibilities:
- `ipoput6` performs IPv6 output: tentative-source rejection, length validation, route lookup, gateway/interface selection, traffic class/hop limit setup, MTU checks, packet-too-big generation, source fragmentation, and medium write.
- Honors IPv6 rule that intermediate nodes do not fragment gated packets unless the outgoing interface is marked for reassembly/NAT-style handling.
- `ipiput6` performs IPv6 input: header pullup, self-address/tentative checks, version validation, forwarding policy, link-local forwarding rejection, hop-limit handling, extension processing, optional reassembly, and protocol dispatch.
- `procxtns` and `unfraglen` identify hop-by-hop/routing/fragment headers and optionally rewrite the next-header slot to insert a fragment header.
- `procopts` is currently a pass-through.
- `ip6reassemble` mirrors IPv4 reassembly for IPv6 fragments, keyed by source/destination/id, trims overlaps, removes fragment headers on completion, and updates payload length.
- `ipfragallo6` and `ipfragfree6` manage IPv6 fragment queue objects.

Notable behavior:
- Fragment offset accounting uses the IPv6 unfragmentable-part length rather than a fixed IP header length.
- ICMPv6 packet-too-big and time-exceeded generation is integrated into forwarding/output error paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipv6.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipv6.h

Defines IPv6 protocol constants, wire headers, and ICMPv6/ND interfaces.

Key definitions:
- Macros for multicast and link-local address tests, solicited-node multicast tests, and option-existence checks.
- Next-header values for IPv6 extension headers and common protocols.
- Multicast scope constants, prefix lengths, ICMPv6 unreachable codes, minimum IPv6 MTU, hop limit, and IPv6 header length.
- Neighbor discovery option types, including standard and Plan 9 extension values.
- Source/target mode constants for neighbor solicitation and local-target classifications.
- `IPV6HDR` packed header macro and `Ip6hdr`, `Opthdr`, `Routinghdr`, and `Fraghdr6` structures.
- Extern declarations for well-known IPv6 address arrays and prefix lengths.
- Prototypes for solicited-node multicast conversion and ICMPv6 neighbor/error send helpers.

Notable documentation:
- Header comments summarize relevant RFC lineage and note deprecated site-local addressing and routing-header type 0 risk.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ipv6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/loopbackmedium.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/loopbackmedium.c

Implements the loopback IP medium.

Key responsibilities:
- Defines a `loopback` medium with no media header, no MAC address, and 16 KiB MTU.
- `loopbackbind` allocates per-interface state, creates a large queue, records the `Fs`, sets speed to 1000 Mbps, and starts a reader kproc.
- `loopbackbwrite` queues outgoing blocks back into the loopback queue and updates output/error counters.
- `loopbackread` drains the queue, locks the interface, and feeds packets to `ipiput4` when logical addresses exist.
- `loopbackunbind` stops the reader, waits for exit, frees queue and state.

Notable design:
- Packets loop through normal IP input processing rather than bypassing the stack.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/loopbackmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/netdevmedium.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/netdevmedium.c

Implements a generic network-device IP medium over an already-openable Plan 9 channel path.

Key responsibilities:
- Defines `netdev` medium with no media header, 64 KiB MTU, and persistent binding.
- `netdevbind` opens the supplied path `ORDWR`, stores the channel and `Fs`, and starts a reader process.
- `netdevbwrite` concatenates/pads outgoing blocks and writes them directly to the device channel.
- `netdevread` reads packets from the channel and passes them to `ipiput4`; if read returns nil, it attempts to unbind the interface and exits.
- `netdevunbind` posts a note to the reader, waits for exit, closes the channel, and frees state.

Notable use:
- Provides a generic packet-device bridge without Ethernet/ARP framing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/netdevmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/netlog.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/netlog.c

Implements the per-stack network debug log exposed through the `log` file.

Key responsibilities:
- `netloginit` allocates the `Netlog` object.
- `netlogopen` lazily allocates a 16 KiB circular buffer and tracks open count.
- `netlogclose` decrements opens and frees the buffer on last close.
- `netlogread` blocks until data is available, then copies from the circular buffer with wrap handling.
- `netlogctl` parses `set`, `clear`, and `only` control commands to manage logging masks and optional IP filtering address.
- `netlog` formats messages, drops oldest bytes on overflow, appends into the circular buffer, and wakes readers.

Supported flags:
- `ppp`, `ip`, `fs`, `tcp`, `icmp`, `udp`, `compress`, `gre`, `tcpwin`, `tcprxmt`, `udpmsg`, `ipmsg`, and `esp`.

Notable behavior:
- Logging is skipped unless the relevant mask is enabled and the log file is open.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/netlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/nullmedium.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/nullmedium.c

Defines a placeholder `null` IP medium.

Key behavior:
- `nullbind` always errors with `cannot bind null device`.
- `nullunbind` is a no-op.
- `nullbwrite` errors with `nullbwrite`.
- `nullmediumlink` registers the medium.

Notable use:
- Installed during IP device reset as a known medium name, but it is intentionally nonfunctional.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/nullmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/pktmedium.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/pktmedium.c

Implements a synthetic packet medium for user-visible packet injection and capture.

Key responsibilities:
- Defines `pkt` medium with Ethernet-like header sizing, 4 KiB MTU, MAC length 6, write hook, and `pktin` hook.
- Bind/unbind are no-ops.
- `pktbwrite` concatenates outbound packets, optionally copies them to the conversation snoop queue, then queues them to the conversation read queue.
- `pktin` handles packets written to interface `data`: drops if no logical interface exists, optionally snoops, and injects into normal IPv4 input via `ipiput4`.
- `pktmediumlink` registers the medium.

Notable use:
- Useful for packet-level testing or user-space packet handling through `ipifc` conversations and `snoop`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/pktmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ptclbsum.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/ptclbsum.c

Implements the low-level 16-bit checksum accumulator used by protocol checksum code.

Key behavior:
- `ptclbsum` computes a partial Internet checksum over a contiguous byte range.
- Handles odd starting alignment, trailing odd byte, little- vs big-endian host layout, chunked 16-byte accumulation, and final carry folding.
- Returns the unfolded checksum sum; callers such as `ptclcsum` complement it for final protocol checksums.

Notable design:
- Uses a static runtime endian probe through a short value and byte pointer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/ptclbsum.c -->