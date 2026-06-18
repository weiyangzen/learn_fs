# Group Research: group_4_9front_sources_os_plan9_9front_sys_src_9_imx8_usdhc_c_sources_os_plan9_86c7bc0a6460

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/usdhc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/usdhc.c

Implements the i.MX8 USDHC SD/MMC host-controller backend for Plan 9’s `SDio` interface. It defines controller register offsets, bit fields, ADMA2 descriptors, a per-controller `Ctlr`, and two concrete controllers: `usdhc1` and `usdhc2`.

Key responsibilities:
- Initializes pad muxing, GPIO reset, clocks, and controller reset for USDHC1/USDHC2.
- Programs bus width and SD clock rate through `usdhcbus()` and `usdhcclk()`.
- Issues SD/MMC commands through `usdhccmd()`, including response decoding and command/data inhibit recovery.
- Sets up ADMA2 transfers in `usdhciosetup()` and waits for completion in `usdhcio()`.
- Registers interrupt handling with `intrenable()` and wakes blocked data I/O through a `Rendez`.

Important implementation details:
- ADMA descriptors are allocated with `sdmalloc()`, filled in `Maxdma` chunks, and written back with `cachedwbse()`.
- Data buffers must be 4-byte aligned, length must be 4-byte aligned, and block size is asserted <= 2048.
- Multi-block data commands use `Autocmd12`; explicit `STOP_TRANSMISSION` is ignored because hardware handles stop.
- Read buffers are writeback-invalidated before DMA and invalidated after successful DMA completion.
- `nomultiwrite = 1` is set on both registered `SDio` instances.

Dependencies and integration:
- Uses architecture services from i.MX8 support: `iomuxpad`, `gpioout`, `setclkgate`, `setclkrate`, `getclkrate`.
- Uses Plan 9 kernel primitives: `Rendez`, `sleep`, `wakeup`, `error(Eio)`, cache maintenance, physical address conversion.
- Exposes itself through `usdhclink()` via `addmmcio()`.

Research notes:
- This file is storage-controller code, not part of the IP stack.
- The driver is tightly coupled to fixed physical MMIO addresses under `VIRTIO`.
- Error paths reset command/data circuits when inhibit bits stick, which is important for recovery from failed card commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/usdhc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/arp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/arp.c

Implements the shared IPv4 ARP and IPv6 neighbor-discovery cache for one `Fs` IP stack instance. The cache stores `Arpent` entries indexed by IP address and interface, holds outbound packets while resolution is pending, and runs a retransmission/drop worker.

Key responsibilities:
- Initializes per-stack ARP state with `arpinit()`.
- Provides lookup/queue behavior through `arpget()`.
- Completes resolution through `arpresolve()` and `arpenter()`.
- Supports manual control through `arpwrite()` commands: `flush`, `add`, `del`, and `garp`.
- Provides formatted cache reading through `arpread()`.
- Retransmits IPv6 neighbor solicitations and times out IPv4 ARP waits in `rxmitproc()`.

Important implementation details:
- `Arp` contains a 64-bucket hash table, 256 fixed cache entries, separate retransmit chains for IPv6 and IPv4, and a drop queue.
- `newarpent()` evicts the least recently used cache slot based on `utime`.
- `arpget()` may return with the ARP write lock held; caller must continue with `arpcontinue()`, `arpresolve()`, or `arprelease()`.
- Pending packets are held as a `Block->list` chain, but `arpcontinue()` trims all but the last queued packet to avoid buildup.
- Timed-out packets are later converted to ICMP unreachable messages outside the ARP lock.
- Route hints can cache a successful `Arpent` in `Routehint.a`.

Dependencies and integration:
- Used by media layers such as `ethermedium.c`.
- Calls `v4lookup`, `v6lookup`, `ipifcoput`, `icmpnohost`, `icmpnohost6`, `icmpns6`, and `arpforme`.
- Relies on `Ipifc->ifcid` to detect stale interface references.

Research notes:
- ARP and NDP resolution are unified behind the same cache object.
- `arpforme()` centralizes the decision to answer for local non-tentative addresses or proxy routes.
- The design intentionally avoids sending ICMP drops while holding the ARP lock.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/chandial.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/chandial.c

Provides a kernel helper for dialing Plan 9 network device conversations from a dial string. It parses strings of the form `[/net/]proto!dest`, opens the protocol clone file, writes a `connect` control message, and returns the data channel.

Key responsibilities:
- Parses dial strings in `_dial_string_parse()`.
- Defaults the network directory to `/net` if absent.
- Opens `<netdir>/<proto>/clone`, reads the allocated conversation number, and constructs the conversation path.
- Writes `connect <dest>` or `connect <dest> <local>` to the control channel.
- Opens and returns the conversation `data` channel.

Important implementation details:
- `DS` stores parsed dial-string components and output pointers for the control channel and directory path.
- If `ctlp` is supplied, ownership of the open control channel is returned to the caller; otherwise it is closed.
- `dir`, if supplied, receives the concrete conversation directory path.
- Uses direct `devtab[type]->read/write` on the clone/control channel.

Dependencies and integration:
- Used by media code such as `ethermedium.c` to bind Ethernet ethertype conversations.
- Depends on Plan 9 namespace/device APIs: `namec`, `cclose`, `devtab`.

Research notes:
- This is a small compatibility/convenience layer, not a protocol implementation.
- There is no connection server translation here; it directly targets the Plan 9 network device namespace.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/chandial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/devip.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/devip.c

Implements the Plan 9 `#I` IP device filesystem. It exposes protocols, conversations, ARP, routes, logs, NDB data, and per-conversation control/data/status files through Qids.

Key responsibilities:
- Creates and attaches per-device `Fs` IP stacks in `ipattach()`.
- Generates the virtual directory tree through `ipgen()`, `ip1gen()`, `ip2gen()`, and `ip3gen()`.
- Implements open/read/write/stat/wstat/close for IP device files.
- Clones protocol conversations through `Fsprotoclone()`.
- Provides generic protocol control handling: `connect`, `announce`, `bind`, `ttl`, `tos`, multicast controls, and protocol-specific controls.
- Implements standard local/remote address and port parsing helpers for protocols.
- Maintains small per-stack NDB content.

Exposed namespace shape:
- Top-level files include `arp`, `bootp`, `ndb`, `iproute`, `ipselftab`, and `log`.
- Each protocol directory exposes `clone`, `stats`, optional `trans`, and conversation directories.
- Each conversation exposes `ctl`, `data`, `err`, `listen`, `local`, `remote`, `status`, and optional `snoop`.

Important implementation details:
- Qid path bits encode type, conversation index, and protocol index.
- `IPaux` attached to channels records the attaching user and a route tag.
- Conversation permissions are owner-sensitive; first open claims owner and resets default permissions.
- `closeconv()` tears down incoming calls, multicast memberships, protocol state, and returns the conversation to idle.
- `setlport()` picks restricted ports from 600-1023 or random unrestricted ports from 32768-65535.
- `Fsnewcall()` creates accepted inbound calls and queues them on a listener’s `incall` list.

Dependencies and integration:
- Initializes `ip_init`, `arpinit`, `netloginit`, and all registered `ipprotoinit[]`.
- Protocol modules register with `Fsproto()`.
- Uses helper APIs from routing, ARP, IP interface, multicast, and NAT translation code.

Research notes:
- This is the main user/kernel control plane for the networking stack.
- Protocol implementations rely on `devip.c` for common conversation lifecycle and address parsing.
- `scalednconv()` scales default conversation count on larger CPU servers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/devip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/esp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/esp.c

Implements IPsec ESP protocol handling for IPv4 and IPv6, primarily tunnel mode. It supports null encryption/authentication, DES/3DES CBC, AES CBC, AES CTR-named mode, HMAC-SHA1-96, and HMAC-MD5-96.

Key responsibilities:
- Registers protocol `esp` for IP protocol number 50.
- Connects ESP conversations to remote address/SPI pairs in `espconnect()`.
- Encapsulates outbound packets in `espkick()`.
- Decapsulates inbound ESP packets in `espiput()`.
- Handles algorithm control commands through `espctl()`: `esp`, `ah`, `header`, `noheader`.
- Handles ICMP advice in `espadvise()` and exposes stats/local/remote formatting.

Important implementation details:
- `Espcb` stores SPI, sequence, selected ESP/AH algorithm state, IV length, block length, auth length, and callback pointers.
- Incoming conversations match by SPI only through `convlookup()`.
- Outbound packets are padded to satisfy ESP cipher/auth alignment, encrypted, then authenticated.
- Inbound packets authenticate before decryption, validate payload sizing, strip ESP/IP headers, and optionally prepend a small user header.
- Algorithm keys are accepted as hex strings and zeroed after conversion.
- IVs are generated with `prng()` during algorithm initialization and embedded at the start of encrypted payload.

Dependencies and integration:
- Uses `libsec` DES, AES, MD5, SHA1, and secure allocation helpers.
- Sends packets through `ipoput4()` or `ipoput6()`.
- Receives ICMP advice through protocol `advise`.

Research notes:
- Header comments explicitly say transport mode is TODO and tunnel mode is the current implementation.
- Replay protection state (`window`) exists in `Espcb` but is not actively enforced in the read path shown.
- The AES CTR function is structurally identical to CBC-style state updates here, so algorithm naming should be treated cautiously.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/esp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ethermedium.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ethermedium.c

Implements the Ethernet and gigabit-Ethernet `Medium` adapters for the IP stack. It binds `Ipifc` interfaces to Ethernet device conversations, sends IPv4/IPv6 frames, receives frames into the IP stack, and handles ARP/NDP media behavior.

Key responsibilities:
- Registers `ethermedium` and `gbemedium`.
- Binds an IP interface to an Ethernet device in `etherbind()`.
- Opens three Ethernet conversations: IPv4 ethertype `0x800`, IPv6 ethertype `0x86DD`, and ARP ethertype `0x806`.
- Runs reader processes for IPv4, IPv6, and ARP.
- Performs Ethernet header construction and ARP/NDP resolution in `etherbwrite()`.
- Manages multicast MAC subscription commands.
- Sends ARP requests, gratuitous ARP, IPv6 neighbor solicitations/advertisements, and duplicate address detection probes.

Important implementation details:
- `Etherrock` stores channels and reader process identities for one bound interface.
- `etherunbind()` posts notes to reader processes, waits for exit, closes channels, and frees the medium state.
- `multicastarp()` resolves broadcast and multicast destinations without issuing ARP/NDP queries.
- IPv4 multicast maps to `01:00:5e:...`; IPv6 multicast maps to `33:33:...`.
- `etherpref2addr()` builds an IPv6 EUI-64 address suffix from a MAC address.
- `etherareg()` sends gratuitous ARP for IPv4 and performs IPv6 neighbor advertisement or DAD behavior for IPv6.

Dependencies and integration:
- Uses `chandial()` to access Ethernet device channels.
- Uses ARP cache APIs: `arpget`, `arpcontinue`, `arpresolve`, `arpenter`, `arpforme`.
- Delivers inbound payloads to `ipiput4()` and `ipiput6()`.
- Uses ICMPv6 helpers `icmpns6()` and `icmpna6()`.

Research notes:
- This file is the concrete media bridge from IP packets to Ethernet frames.
- `gbemedium` differs mainly by MTU: 9000-byte max payload plus Ethernet header.
- Unbind logic is careful because reader processes may initiate unbind after device errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ethermedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/gre.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/gre.c

Implements Generic Routing Encapsulation over IPv4, including normal raw/cooked GRE conversations and specialized retunneling/forwarding support with buffering and sequence tracking.

Key responsibilities:
- Registers protocol `gre` for IP protocol number 47.
- Connects GRE conversations with `greconnect()`.
- Encapsulates outbound GRE packets in `grekick()`.
- Receives and demultiplexes GRE packets in `greiput()`.
- Supports control commands: `raw`, `cooked`, `retunnel`, `report`, `dlsuspend`, `ulsuspend`, `dlresume`, `ulresume`, `forward`, and `ulkey`.
- Tracks GRE packet/byte counters and short-packet errors.

Important implementation details:
- `GREconv` stores raw/cooked mode plus retunnel addresses: home address, north, south, care-of address, sequence, suspend flags, and uplink key.
- Fixed-size rings buffer pending/downlink/uplink packets during retunnel suspension.
- `gredownlink()` rewrites GRE headers for downlink forwarding, ensures a sequence number, and keeps metadata at the block base.
- `greuplink()` rewrites uplink source/destination and optionally inserts a GRE key.
- `greiput()` first checks retunnel matches on inner IPv4 source/destination, then falls back to raw or address/protocol conversation matching.
- Conversations are limited to 64.

Dependencies and integration:
- Uses `Fsstdconnect()` and `Fsconnected()` from `devip.c`.
- Sends packets through `ipoput4()`.
- Uses `Route`/forwarding integration indirectly through normal IP receive.
- Uses `qbypass()` for direct write-side packet processing.

Research notes:
- This is IPv4-only GRE; headers and address fields are IPv4.
- The retunneling logic is specialized and stateful, with explicit suspend/resume controls.
- Some code comments highlight deliberate packet loss in lock-race situations to avoid blocking receive paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/gre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/icmp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/icmp.c

Implements ICMPv4 as protocol number 1. It supports user ICMP conversations, echo reply handling, generated error messages, protocol advice delivery, source-translation forwarding, and statistics.

Key responsibilities:
- Registers protocol `icmp`.
- Sends user-provided ICMP packets through `icmpkick()`.
- Receives ICMP packets through `icmpiput()`.
- Responds to echo requests with echo replies.
- Generates errors through `icmpnohost()`, `icmpnoconv()`, `icmpcantfrag()`, and `icmpttlexceeded()`.
- Converts unreachable/time-exceeded messages into protocol advice.
- Supports ICMP forwarding/NAT translation via `icmpforward()` and `icmpproxyadvice()`.

Important implementation details:
- `Icmppriv` stores MIB-like counters and per-type in/out counts plus an `Ipht` hash table for translations.
- Generated ICMP errors include the original packet up to IPv4 minimum MTU.
- ICMP errors are not sent for multicast addresses or when no valid local source can be selected.
- `goticmpkt()` demultiplexes by ICMP id and can reverse NAT translations.
- Advice only proceeds when the embedded IPv4 packet has no options, is first fragment, and has a valid checksum.
- `hnputs_csum()` is used to adjust checksums during translation.

Dependencies and integration:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsconnected`, and `Fsrcvpcolx`.
- Sends packets through `ipoput4()`.
- Provides hooks used by IP fragmentation and ARP timeout paths.

Research notes:
- ICMPv4 is both a user-visible datagram protocol and an internal control/error mechanism.
- NAT behavior is integrated into the protocol using `Proto.ht` and translation helpers from `ipaux.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/icmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/icmp6.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/icmp6.c

Implements ICMPv6, including user conversations, echo handling, error generation/advice, neighbor discovery, and validation rules for NDP/router messages.

Key responsibilities:
- Registers protocol `icmpv6` for `ICMPv6`.
- Sends user ICMPv6 packets through `icmpkick6()`.
- Receives ICMPv6 packets through `icmpiput6()`.
- Generates IPv6 errors: no host, no conversation, TTL exceeded, packet too big.
- Sends neighbor solicitations via `icmpns6()` and neighbor advertisements via `icmpna6()`.
- Validates ICMPv6 and NDP packets in `valid()`.
- Supports a `headers` control mode where user payload includes source/destination address fields.

Important implementation details:
- ICMPv6 checksum is calculated by temporarily reusing the IPv6 header area as a pseudoheader.
- NDP validation enforces hop limit 255, code 0, target/multicast constraints, option length constraints, and router-advertisement source checks.
- Neighbor solicitation for a local/proxy target may insert sender link-layer info into ARP/NDP cache and reply with appropriate R/S/O flags.
- Neighbor advertisement updates the ARP/NDP cache, including tentative-address handling for duplicate address detection.
- Embedded first-fragment headers are normalized before advice dispatch when possible.

Dependencies and integration:
- Reuses ICMPv4 connection/open/close/state helpers where possible.
- Calls `arpenter`, `arpforme`, `ipv6local`, `iplocalonifc`, `Fsrcvpcolx`, and `ipoput6`.
- Used by `ethermedium.c` for NDP and DAD flows.

Research notes:
- This file is central to IPv6 control-plane correctness.
- The implementation assumes no extension headers for checksum validation except where advice strips a first fragment header.
- It records detailed error counters for hop-limit, code, target, option length, address mix, and router-address failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/icmp6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/igmp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/igmp.c

Implements IPv4 IGMPv1/v2 group reporting and IPv6 MLDv1 reporting. It registers both `igmp` and `mld` protocols and manages delayed multicast reports.

Key responsibilities:
- Sends IGMP reports/leaves through `igmpsendreport()`.
- Sends MLD reports/done messages through `mldsendreport()`.
- Queues randomized delayed reports in `queuereport()`.
- Cancels pending reports when another host reports the same group through `purgereport()`.
- Processes inbound IGMP in `igmpiput()` and MLD in `mldiput()`.
- Exposes `multicastreportfn` used by interface multicast membership changes.

Important implementation details:
- `Priv` contains a hash table of pending `Report` objects and a `Rendez` for the report worker.
- `igmpproc()` wakes when reports are pending, ages timeouts, sends expired reports, and sleeps at 100 ms ticks.
- MLD messages include an IPv6 hop-by-hop Router Alert option.
- MLD reports are only sent for valid multicast groups with appropriate scope and not for all-nodes link-local.
- IGMP checksum covers only the IGMP header portion after the IPv4 header.

Dependencies and integration:
- Sends through `ipoput4()` and `ipoput6()` with TTL/hop limit 1.
- Uses `ipifcgetmulti()` to enumerate matching interface multicast memberships.
- Shares one `Priv` between IGMP and MLD protocols.

Research notes:
- This file handles multicast membership signaling, not packet delivery.
- MLD input strips and validates the hop-by-hop option header before treating the payload as ICMPv6-like MLD.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/igmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/il.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/il.c

Implements IL, Plan 9’s reliable datagram protocol over IPv4, using IP protocol number 40. It provides connection setup, sequencing, acknowledgments, retransmission, out-of-order buffering, close handling, and adaptive timeout estimates.

Key responsibilities:
- Registers protocol `il`.
- Connects/listens through `ilconnect()` and `ilannounce()`.
- Sends data through `ilkick()` with IL/IP headers and sequence numbers.
- Receives packets through `iliput()` and state machine processing in `ilprocess()`.
- Maintains unacknowledged and out-of-order queues.
- Runs periodic ack/retransmit/query handling in `ilackproc()`.
- Handles ICMP advice in `iladvise()`.

Important implementation details:
- `Ilcb` stores state, sequence counters, receive window, retransmission counters, timers, RTT/rate estimates, and queues.
- State machine covers `Ilclosed`, `Ilsyncer`, `Ilsyncee`, `Ilestablished`, `Illistening`, `Ilclosing`, and `Ilopening`.
- Packet types include sync, data, dataquery, ack, query, state, and close.
- Outbound data is copied to an unacked queue so it can be retransmitted.
- `ilpullup()` delivers in-order data to the read queue and frees duplicates.
- Query/state packets support selective retransmission decisions through small query timestamp table `qt`.
- `fasttimeout` can be requested by appending `!fasttimeout` to connect arguments.

Dependencies and integration:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsnewcall`, and `Fsconnected`.
- Uses `Ipht` to match incoming packets to conversations/listeners.
- Sends through `ipoput4()` only; connect rejects non-IPv4.
- Uses `ptclcsum()` for IL checksums.

Research notes:
- IL is IPv4-only here.
- The ack worker is started lazily per protocol instance.
- Queue limits protect mount RPC buffer pressure by dropping data when the read queue reaches `Maxrq`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/il.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/inferno.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/inferno.c

Small compatibility shim for code shared between Inferno and Plan 9 variants of the IP stack.

Key responsibilities:
- `commonuser()` returns the current process user via `up->user`.
- `commonerror()` returns the current process error string via `up->errstr`.
- `bootpread()` is a stub returning 0.

Dependencies and integration:
- Included by Plan 9 networking code that expects common user/error abstraction.
- `bootpread()` is called by `devip.c` when reading the top-level `bootp` file.

Research notes:
- No protocol logic is implemented here.
- The file exists to smooth portability/common-source differences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/inferno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ip.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ip.c

Implements core IPv4 input/output handling, routing dispatch, fragmentation, reassembly, and IP statistics for the `Fs` stack.

Key responsibilities:
- Initializes `IP` state and fragment queues in `ip_init()`.
- Enables/disables routing through `iprouting()`.
- Sends IPv4 packets through `ipoput4()`.
- Receives IPv4 packets through `ipiput4()`.
- Handles IPv4 fragmentation and reassembly.
- Exposes IP stats through `ipstats()`.
- Computes IPv4 header checksum through `ipcsum()`.

Important implementation details:
- `ipoput4()` fills IP headers, performs route lookup, chooses gateway, clamps TCP MSS when forwarding, handles loopback bypass, fragments if needed, and sends via `ipifcoput()`.
- If DF is set and fragmentation is required, it sends ICMP “fragmentation needed”.
- `ipiput4()` validates version, header length, checksum, and packet length, then decides whether to forward or deliver locally.
- Forwarding supports route translation via protocol `forward` callbacks and reassembly-before-forwarding for selected interfaces.
- Local delivery strips IPv4 options before protocol dispatch.
- Reassembly uses per-stack fixed fragment pools, ordered fragment queues, overlap trimming, timeout cleanup, and max-size checks.

Dependencies and integration:
- Uses route lookup (`v4lookup`), interface output (`ipifcoput`), ICMP errors, protocol dispatch (`Fsrcvpcol`, `Fsrcvpcolx`), and TCP MSS clamp.
- Initializes IPv6 side through `ip_init_6(f)`, defined elsewhere.

Research notes:
- This is the IPv4 data-plane center for the Plan 9 IP stack.
- Route hints are threaded through output to cache route and ARP decisions.
- Reassembly stores `Ipfrag` metadata at block base and requires careful block pointer adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ip.h -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ip.h

Defines the core types, constants, protocol interfaces, route structures, ARP structures, and function declarations shared by the 9front kernel IP stack.

Key contents:
- Global constants for address lengths, IPv4/IPv6 versions, header sizes, max packet size, route-table sizing, states, and MIB counters.
- Core data structures: `Fs`, `IP`, `Proto`, `Conv`, `Ipifc`, `Iplifc`, `Ipmulti`, `Medium`, `Route`, `Iphash`, `Ipht`, `Translation`, `Arpent`, `Routehint`, `Ndb`.
- Protocol callbacks for connect/announce/bind/state/create/close/receive/control/advice/stats/local/remote/inuse/gc/forward.
- Media callbacks for bind/unbind/bwrite/multicast/address registration/prefix-to-address conversion.
- Routing, ARP, IP auxiliary, interface, ICMP, TCP, BOOTP, and device entry-point declarations.

Important implementation details:
- `Conv` embeds `Iphash`, allowing conversation pointers to be recovered with `iphconv()`.
- `Translation` embeds two `Iphash` structures for forward and backward NAT lookup.
- `Routehint` caches the last route generation and ARP entry for repeated sends.
- `Fs` owns one full IP stack instance, including protocol registry, route roots, ARP cache, self table, NDB, and logs.
- `Ipifc` represents a physical/logical interface binding and contains MTU, medium, MAC, logical addresses, multicast/RA flags, and traffic shaping state.
- `Proto` is the central protocol registration object used by `devip.c`.

Dependencies and integration:
- Included by nearly all files in this group.
- Declares the contracts implemented by `devip.c`, `arp.c`, `ip.c`, `ipaux.c`, `ethermedium.c`, ICMP, IL, GRE, ESP, and interface/routing modules outside this group.

Research notes:
- This header is the architectural map of the networking subsystem.
- It combines user-facing device concepts, packet data-plane concepts, and routing/NAT internals in one shared interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipaux.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ipaux.c

Provides IP stack auxiliary routines and shared constants: IPv6 well-known addresses, protocol checksum calculation, MAC parsing, multicast detection, connection IP-version selection, IP hash-table management, NAT translation management, and checksum-adjusting helpers.

Key responsibilities:
- Defines `v6hdrtypes` names and well-known IPv6 addresses/prefixes.
- Computes protocol checksums across block lists with `ptclcsum()`.
- Builds IPv6 solicited-node multicast addresses with `ipv62smcast()`.
- Parses MAC addresses with `parsemac()`.
- Detects multicast addresses with `ipismulticast()`.
- Chooses conversation IP version with `convipvers()`.
- Implements `Ipht` add/remove/lookup for conversations and translations.
- Implements NAT translation lifecycle and user-visible translation read/write operations.
- Provides `hnputs_csum()` for incremental checksum updates.

Important implementation details:
- `iphtlook()` applies precedence: exact 4-tuple, local address+port, any address+port, local address only, then wildcard.
- NAT `Translation` entries are held on an active LRU-style list and a free list; expired or excessive entries are reused.
- `transforward()` creates source-translation state only after checking source validity, forward route, local egress address, backward route, and port availability.
- UDP and ICMP backward translations may match replies from any remote endpoint to support hole punching.
- `transwrite()` can flush all translations with zero-length write at offset 0, or install a specific translation after validating routes and local addresses.
- `ptclcsum()` handles chained `Block` lists and odd byte alignment by accumulating low/high sums separately.

Dependencies and integration:
- Used by ICMP, UDP/TCP-like protocols, route translation, GRE/ESP checksums, and IPv6 neighbor code.
- Depends on `ipv6.h` constants and route/interface functions from the broader IP stack.

Research notes:
- Despite the filename, this is not just parsing glue; it contains central NAT and protocol lookup mechanics.
- Translation-related typo strings exist in error messages (`desination`, `soruce`) but do not affect behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipaux.c -->