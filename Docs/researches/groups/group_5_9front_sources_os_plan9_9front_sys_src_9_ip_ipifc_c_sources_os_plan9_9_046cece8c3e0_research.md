# Group Research: 9front IP stack and Kirkwood platform files

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipifc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ipifc.c

Implements Plan 9 IP interface management.

Key elements:
- Registers link media types and binds/unbinds `Ipifc` conversations to media.
- Manages logical interface addresses, masks, remote networks, point-to-point routes, proxy routes, and IPv6 autoconf-derived addresses.
- Maintains the `Ipself` cache of local, broadcast, and multicast addresses accepted by the host.
- Adds/removes route-table entries as interface addresses and multicast memberships change.
- Provides source address selection helpers for IPv4 and IPv6.
- Handles `/net/ipifc` control commands: `bind`, `add`, `try`, `del`, `unbind`, `add6`, `del6`, `mtu`, `speed`, `delay`, `reflect`, `reassemble`, and `ra6`.

Dependencies:
- Uses `Medium` implementations such as loopback, pkt, null, and netdev.
- Calls routing APIs from `iproute.c`.
- Uses IPv6 helpers from `ipv6.h` and medium address-resolution hooks.

Research notes:
- Binding a non-loopback medium also binds loopback support for local packet injection.
- The self-address cache is deliberately delayed-free to avoid heavy locking while packets may still reference entries.
- IPv6 source selection prefers global, then ULA, then link-local, while avoiding deprecated/tentative addresses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipifc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipmux.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ipmux.c

Implements an IP packet filter/demultiplexer protocol.

Key elements:
- Parses filter expressions over version, protocol, source, destination, interface address, IP header bytes, and payload bytes.
- Builds canonical ordered filter chains and merges them into a decision tree.
- Supports masks and multiple values per comparison.
- Converts IPv6-style address filters to IPv4 offsets/widths where needed.
- Delivers matching packets to connected `ipmux` conversations, prepending the interface address.
- Sends unmatched packets to the normal protocol receiver.

Dependencies:
- Uses `Ip4hdr`, `Ip6hdr`, `Conv`, `Proto`, and queue primitives from the IP stack.
- Uses `Fsrcvpcol` to fall back to protocol dispatch.

Research notes:
- A missing `ver=` filter is expanded into both IPv6 and IPv4 branches.
- The tree stores refs so shared merged filter nodes can be removed safely on close.
- `ipmuxkick` expects user writes to be complete IP packets and injects them through IPv4 or IPv6 output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipmux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/iproute.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/iproute.c

Implements IPv4/IPv6 route storage, lookup, readback, and control parsing.

Key elements:
- Stores routes in bucketed balanced range trees, with separate IPv4 and IPv6 roots.
- Represents destination ranges and optional source-specific ranges.
- Supports route types for interface, unicast, broadcast, multicast, point-to-point, proxy, transparent, and IPv4.
- Provides `addroute`, `delroute`, `flushrouteifc`, `v4lookup`, `v6lookup`, `v4source`, and `v6source`.
- Implements route generation counters and `Routehint` cache validation.
- Parses `/net/iproute` control messages for `add`, `del/remove`, `flush`, and `tag`.
- Formats route table reads with address, mask, gateway, type, tag, interface, source, and source mask.

Dependencies:
- Uses `Ipifc` source selection helpers from `ipifc.c`.
- Uses route structures from `ip.h`.
- Integrates with per-channel route tags through `IPaux`.

Research notes:
- Routes associated with an interface are invalidated by incrementing `ifc->ifcid`.
- A route can be more specific either by destination range or by source range.
- Interface routes are protected from being overwritten by non-interface routes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/iproute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipv6.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ipv6.c

Implements IPv6 initialization, output, input forwarding, extension-header handling, fragmentation, and reassembly.

Key elements:
- Initializes IPv6 router-advertisement defaults and neighbor-discovery timing parameters.
- `ipoput6` routes outbound packets, fills IPv6 headers, handles loopback bypass, clamps TCP MSS when forwarding, and fragments local output when needed.
- Refuses intermediate IPv6 fragmentation unless the outgoing interface has `reassemble` enabled.
- `ipiput6` validates incoming packets, forwards routable packets, enforces hop-limit behavior, and dispatches local packets to protocol handlers.
- Handles hop-by-hop/routing/fragment header traversal through `unfraglen`.
- Reassembles IPv6 fragments with overlap trimming, timeout cleanup, and IP_MAX bounds.

Dependencies:
- Uses `iproute.c` lookups, `ipifc.c` local-address checks, `icmpv6` error helpers, and `tcpmssclamp`.
- Uses IPv6 constants and header layouts from `ipv6.h`.

Research notes:
- Forwarding blocks link-local destinations and link-scope multicast.
- Fragment reassembly stores metadata in block base space and concatenates enough state to return a valid packet chain.
- `procopts` is currently a pass-through placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipv6.h -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/ipv6.h

Defines IPv6 constants, header layouts, address predicates, and ICMPv6 helper prototypes.

Key elements:
- Defines multicast/link-local/ULA tests.
- Lists IPv6 next-header values and neighbor-discovery option constants.
- Defines IPv6 minimum MTU, base header size, and fragment header size.
- Declares `Ip6hdr`, `Opthdr`, `Routinghdr`, and `Fraghdr6`.
- Exposes common IPv6 multicast, loopback, link-local, and mask globals.
- Declares ICMPv6 neighbor solicitation/advertisement and error routines.

Dependencies:
- Included by IPv6, TCP, UDP, and interface code that needs IPv6 protocol metadata.

Research notes:
- Routing header type 0 is explicitly flagged as dangerous in comments.
- IPv4-mapped address handling is implemented elsewhere, but this file defines shared IPv6 wire layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/ipv6.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/loopbackmedium.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/loopbackmedium.c

Implements the loopback IP medium.

Key elements:
- Creates a large message queue for loopback packets.
- Starts a `loopbackread` kernel process to feed queued packets into `ipiput4`.
- Writes enqueue packets directly onto the loopback queue.
- Registers a `Medium` named `loopback`.

Dependencies:
- Used by `ipifc.c` for local delivery and as auxiliary loopback support for other media.

Research notes:
- The read path processes through the IPv4 input function, which also handles version dispatch in this stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/loopbackmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/netdevmedium.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/netdevmedium.c

Implements a generic network-device-backed IP medium.

Key elements:
- Binds an IP interface to an already-openable device path.
- Stores the device channel and reader process in `Netdevrock`.
- Starts a `netdevread` kernel process to read blocks from the device and inject them into IP input.
- Writes outbound packets through the underlying device’s `bwrite`.
- Unbinds by posting a note to the reader and waiting for it to exit.

Dependencies:
- Uses `namec`, `devtab` `bread`/`bwrite`, and `mediumunbindifc`.

Research notes:
- `unbindonclose` is false, so the medium is not automatically detached merely by closing a conversation.
- Reader death triggers interface unbind unless another unbind is already in progress.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/netdevmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/netlog.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/netlog.c

Implements the IP stack action/debug log.

Key elements:
- Maintains a circular 16 KiB log buffer with blocking reads.
- Tracks open count and allocates/frees the buffer on first open/last close.
- Supports log-mask controls: `set`, `clear`, and `only`.
- Maps named flags such as `ip`, `tcp`, `udp`, `icmp`, `tcpwin`, `tcprxmt`, and `ipmsg` to bit masks.
- `netlog` appends formatted messages and wakes readers.

Dependencies:
- Used throughout the IP stack for protocol diagnostics.
- Uses Plan 9 `parsecmd`, `lookupcmd`, locks, qlocks, and rendezvous sleep/wakeup.

Research notes:
- The `only` control sets an IP address filter field, but filtering is not applied inside this file’s `netlog` function.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/netlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/nullmedium.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/nullmedium.c

Defines null and temporary unbound IP media.

Key elements:
- `nullmedium` has no-op bind/unbind and a write path that frees the block then errors.
- `unboundmedium` is a sentinel used while bind/unbind transitions are in progress.
- Registers `nullmedium` with the IP media table.

Dependencies:
- Used by `ipifc.c` during bind/unbind state transitions.

Research notes:
- The sentinel prevents code from treating an interface as fully usable while medium operations are still underway.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/nullmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/pktmedium.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/pktmedium.c

Implements the packet pseudo-medium for user-visible IP packet queues.

Key elements:
- Defines a `pkt` medium with 4 KiB MTU and automatic unbind-on-close.
- Bind/unbind are no-ops.
- Writes outbound packets into the interface conversation read queue.
- Copies packets to the snoop queue when snoopers are present.

Dependencies:
- Used by `ipifcconnect` as the default medium when a dial-style interface has not been explicitly bound.

Research notes:
- This medium turns an `ipifc` conversation into a packet endpoint rather than a hardware-backed interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/pktmedium.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/rudp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/rudp.c

Implements 9front’s reliable UDP-like protocol over IPv4 protocol number 254.

Key elements:
- Uses UDP-compatible port fields plus a reliability header containing sequence, generation, ack, and ack-generation fields.
- Maintains per-peer `Reliable` state for send sequence, receive sequence, unacked queue, retransmits, and flow control.
- Starts an ack/retransmit kernel process lazily.
- Provides connect/announce, header mode, randdrop testing, and per-peer hangup control.
- Sends delayed acks, retransmits unacked packets, and tears down state after repeated failures.
- Supports header mode that passes remote/local/interface addresses and ports to user space.

Dependencies:
- Uses IPv4 output, ICMP no-conversation reporting, IP hash tables, and Plan 9 queues.
- Uses shared source-address helpers from the IP interface layer.

Research notes:
- Despite using IPv6-sized internal addresses, the wire protocol is IPv4-only.
- Generations distinguish restarted peers and avoid accepting stale acknowledgements.
- Flow control blocks writers when more than `Maxunacked` packets are outstanding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/rudp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/tcp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/tcp.c

Implements the TCP protocol for IPv4 and IPv6.

Key elements:
- Defines TCP wire pseudo-headers, segment metadata, resequencing queue entries, timers, limbo SYN state, and per-connection control blocks.
- Implements active open, passive open, close, hangup, keepalive, state reporting, and garbage collection.
- Uses SYN limbo entries to avoid allocating full conversations before SYN-ACK completion.
- Handles TCP options for MSS and window scale.
- Implements checksum validation and header parsing for IPv4 and IPv6.
- Runs the TCP state machine for SYN, ACK, RST, FIN, receive trimming, delayed ACKs, and close states.
- Implements output segmentation, send-window checks, receive-window updates, retransmission timers, RTT estimation, keepalive probes, and zero-window probes.
- Includes NewReno-style fast retransmit/recovery and appropriate byte counting.
- Supports local TCP splicing by bypassing queues between two local established conversations.
- Supports transparent forwarding/NAT hooks and MSS clamping for forwarded SYN packets.
- Exposes detailed TCP stats.

Dependencies:
- Uses `iproute.c` for route hints/source selection, `ipifc.c` for local address selection, IPv4/IPv6 output paths, IP hash tables, translation helpers, and queues.

Research notes:
- The implementation deliberately avoids allocating full `Conv` state for half-open passive connections until the final ACK arrives.
- IPv6 MSS defaults to 1220 unless route/interface conditions justify a larger value.
- Timers are maintained by a protocol kernel process that also retransmits limbo SYN-ACKs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/udp.c -->
# File Research: sources/os/plan9/9front/sys/src/9/ip/udp.c

Implements UDP for IPv4 and IPv6.

Key elements:
- Defines IPv4 and IPv6 UDP pseudo-header layouts.
- Implements connect/announce/create/close and per-conversation source IP tracking.
- Builds outbound IPv4 or IPv6 UDP packets, computes checksums, and sends through IP output.
- Supports `headers` mode, where user data includes remote/local/interface addresses and ports.
- Validates inbound checksums, performs hash lookup, creates accepted conversations for announced endpoints, trims packet headers, and queues payloads.
- Emits ICMP no-conversation errors for unmatched datagrams.
- Supports transparent forwarding/NAT translation and ICMP advice/proxy advice.
- Provides MIB-style UDP stats.

Dependencies:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsnewcall`, IP hash tables, IPv4/IPv6 output, ICMP, and translation helpers.

Research notes:
- IPv6 UDP checksum is mandatory here; IPv4 allows a zero checksum.
- For multicast/broadcast receives, the accepted conversation stores a unicast source IP for replies.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/ip/udp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/arch.c

Provides miscellaneous ARM architecture process/register helpers.

Key elements:
- Builds kernel `Ureg` snapshots for sleeping processes.
- Enforces aligned user addresses for system calls that require them.
- Returns the user PC from the last debug register frame.
- Allows devproc register writes while preserving protected PSR mode/interrupt bits.
- Sets initial kernel process PC/SP.
- Saves/restores floating-point process state.
- Identifies user-mode exception frames.
- Implements interrupt-masked 32-bit compare-and-swap.

Dependencies:
- Uses ARM PSR constants from `arm.h` and FPU helpers from platform code.

Research notes:
- The CAS implementation is uniprocessor-style: it raises interrupt priority and then issues `coherence` after a successful store.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/archkw.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/archkw.c

Implements Marvell Kirkwood/SheevaPlug platform setup.

Key elements:
- Defines SoC register base addresses in global `soc`.
- Fixes CPU address-map windows, especially crypto SRAM mapping.
- Reads and reports L1 cache configuration.
- Enables/configures L2 cache, writeback policy, prefetch/ECC bits, and uncached upper address window.
- Initializes CPU frequency, cycle frequency, delay loop, cache info, and L2 cache.
- Performs early reset-time GPIO, clock-gate, L2, SDRAM, and analog setup.
- Provides soft reset/reboot handling.
- Exposes flash reset/probe metadata for NAND.

Dependencies:
- Uses Kirkwood register definitions from `io.h`, ARM coprocessor helpers, cache/TLB assembly helpers, and flash interfaces.

Research notes:
- The code is specific to Marvell Kirkwood systems such as SheevaPlug/OpenRD.
- It assumes a 1.2 GHz ARM926EJ-S processor and platform-specific U-Boot address mappings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/archkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arm.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/arm.h

Defines ARM processor constants for the Kirkwood kernel port.

Key elements:
- Defines PSR mode and condition bits.
- Defines coprocessor numbers and CP15 register/opcode constants.
- Defines cache, TLB, barrier, and L2 test/config operation constants.
- Defines ARM page-table entry bits for sections and small/large pages.
- Defines domain/access permission helpers and high-vector address.

Dependencies:
- Included by platform C and assembly code that manipulates ARM system registers and MMU state.

Research notes:
- Comments distinguish ARM architectural terminology where “flush” means invalidate and “clean” means writeback.
- Several constants target ARM926EJ-S/Sheeva-specific L2 behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arm.s -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/arm.s

Provides ARM assembly macros for early Kirkwood setup.

Key elements:
- Defines physical/virtual address conversion macros.
- Defines L1 page-table index and machine-address helpers.
- Defines page-table entry attributes for DRAM and I/O sections.
- Defines barrier macros for DMB, DSB, and ISB using CP15 operations.
- Defines `FILLPTE` and `ZEROPTE` macros for boot-time page-table construction.
- Provides a `WAVE` debug macro that writes a character to the physical console.

Dependencies:
- Includes `mem.h` and `arm.h`.
- Used by low-level assembly startup/exception code.

Research notes:
- The macros are tailored to ARM926EJ-S and Kirkwood cache/barrier behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/cga.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/cga.c

Implements a simple CGA text console backend.

Key elements:
- Writes characters and attributes into CGA memory at `0xB8000`.
- Handles newline, tab, backspace, scrolling, and cursor updates.
- Installs `screenputs` during `screeninit`.
- Uses a lock but avoids deadlock when printing from interrupt context.

Dependencies:
- Uses kernel screen output hook and memory mapping macros.

Research notes:
- Port I/O functions are stubbed with TODO macros, so hardware cursor register access is effectively inactive here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/cga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/clock.c

Implements Kirkwood timer, clock interrupt, watchdog, and delay support.

Key elements:
- Defines Kirkwood timer registers and control bits.
- Clock interrupt reloads the watchdog, increments a sanity counter, calls `timerintr`, and clears the bridge interrupt.
- `clockinit` verifies timer interrupts, configures periodic timer0, free-running timer1, and watchdog reset output.
- `timerset` programs timer0 for next deadline within min/max bounds.
- `fastticks` extends the 32-bit timer into a monotonic 64-bit counter.
- Provides `perfticks`, `lcycles`, `µs`, `microdelay`, and `delay`.

Dependencies:
- Uses `soc.clock`, `soc.cpu`, interrupt bridge routines, and machine timing fields.

Research notes:
- Timer1 counts down; `perfticks` returns its bitwise complement as an increasing counter.
- `clockshutdown` also disables the watchdog.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/coproc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/coproc.c

Implements dynamic ARM coprocessor and VFP register access helpers.

Key elements:
- Builds small instruction stubs at runtime for MCR/MRC coprocessor writes/reads.
- Maps the stub into the caller’s PC space, writes back data cache, invalidates instruction cache, and calls it.
- Provides CP15 wrappers `cpwrsc` and `cprdsc`.
- Provides VFP register read/write helpers `fprd` and `fpwr`.

Dependencies:
- Uses ARM instruction encodings, cache maintenance helpers, interrupt masking, and `arm.h` constants.

Research notes:
- Dynamic instruction generation avoids needing one assembly routine per coprocessor register encoding.
- The code runs with interrupts raised while patching/executing the stub.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/dat.h

Defines core machine data structures for the Kirkwood ARM port.

Key elements:
- Declares kernel architecture types such as `Conf`, `Mach`, `MMMU`, `PMMU`, `FPsave`, `Soc`, and `Memcache`.
- Defines process label layout and floating-point save state.
- Defines physical memory configuration and global system configuration fields.
- Defines per-machine state, including MMU, process pointer, exception stacks, fast clock, CPU type/revision, delay loop, and CPU frequency.
- Defines fake `kmap` helpers for this architecture.
- Defines ISA configuration parsing structure and device configuration structures.
- Defines cache description and SoC controller address layout.

Dependencies:
- Includes shared `portdat.h`.
- Referenced across the Kirkwood platform and generic kernel port code.

Research notes:
- The port assumes one cache color and uses a simple fake kmap model.
- Global `soc` is declared here and populated in `archkw.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devarch.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/devarch.c

Implements the `#P` architecture device.

Key elements:
- Maintains a fixed table of architecture-specific files with read/write callbacks.
- Provides `addarchfile` for registering permanent files.
- Implements standard Plan 9 device attach/walk/stat/open/read/write methods.
- Registers `cputype` and `timebase` files at init.
- Formats CPU/SoC identity using CPUID and PCIe/device ID registers.
- Exposes the cycle counter through `timebase`.

Dependencies:
- Uses Plan 9 device framework, `soc`, PCIe register structures, `cpidget`, and cycle counter helpers.

Research notes:
- The device table is limited to 16 entries.
- CPU naming is Marvell/Kirkwood-specific and records SoC revision for later platform use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/devrtc.c

Implements the Kirkwood real-time clock device.

Key elements:
- Defines RTC register and decoded date/time structures.
- Converts between RTC date/time and seconds since 1970.
- Handles BCD decode/encode for hardware time/date registers.
- Reads the clock repeatedly until two consecutive samples match.
- Exposes `#r/rtc` as a numeric seconds file.
- Allows writing seconds to set the RTC.

Dependencies:
- Uses `soc.rtc` and Plan 9 device framework.

Research notes:
- Leap-year handling only checks divisibility by 4.
- The hardware stores years as `year % 100` offset from 2000.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devtwsi.c -->
# File Research: sources/os/plan9/9front/sys/src/9/kw/devtwsi.c

Implements the Kirkwood TWSI/I2C device.

Key elements:
- Defines TWSI register layout, control bits, and status codes.
- Uses a single global transfer state protected by `QLock`.
- Implements interrupt-driven read and write state machines.
- Starts transfers by setting `Twsistart`, waits for interrupts, advances by status code, and finishes with STOP.
- Exposes `#²/twsi`; read/write offsets are interpreted as device addresses.
- Registers and unregisters the TWSI interrupt handler during device init/shutdown.

Dependencies:
- Uses `soc.twsi`, Kirkwood interrupt constants, Plan 9 device framework, rendezvous sleep/wakeup, and coherence barriers.

Research notes:
- The driver supports one active transfer at a time.
- Abnormal status codes terminate the transfer and raise an error.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/kw/devtwsi.c -->