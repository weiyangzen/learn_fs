# Group Research: group_1470_plan9_sources_os_plan9_plan9_sys_src_9_ip_rudp_c_sources_os_plan9_p_130388cc979c

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/rudp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/rudp.c

## Purpose
Implements Plan 9's Reliable User Datagram Protocol (`rudp`), an IPv4-only reliable datagram protocol using a UDP-compatible packet shape plus a 16-byte reliability header. It registers as protocol number `254` and exposes the standard Plan 9 IP `Proto` interface.

## Main Data Structures
- `Udphdr` and `Rudphdr`: IPv4 pseudo-header plus UDP header, with `Rudphdr` adding reliable sequence, generation, ack, and ack-generation fields.
- `Reliable`: per-peer state keyed by remote IP and port. Tracks send/receive sequence numbers, generations, unacked packet list, retransmit timers, flow-control sleep state, and reference count.
- `Rudpcb`: per-conversation private state containing the peer `Reliable` list plus `headers` and `randdrop` controls.
- `Rudppriv`: protocol global hash table, MIB-like counters, checksum/length/retransmit/out-of-order stats, and ack kproc startup state.

## Protocol Flow
- `rudpinit` allocates and registers the `rudp` protocol with connect, announce, create, close, receive, control, advise, state, and stats callbacks.
- `rudpconnect` and `rudpannounce` start the global ack/retransmit kproc, use `Fsstdconnect`/`Fsstdannounce`, mark the conversation connected, and add it to the protocol hash table.
- `rudpkick` dequeues user data from `wq`, optionally parses user-supplied address headers, constructs IPv4/UDP/RUDP headers, assigns a next send sequence, piggybacks the latest receive ack, computes checksum, stores a retransmission copy through `relackq`, sends with `ipoput4`, and applies simple flow control when `UNACKED(r) > Maxunacked`.
- `rudpiput` validates the UDP checksum, finds a conversation via `iphtlook`, calls `reliput` for reliability state handling, trims off protocol headers, optionally prepends source metadata for `headers`, then queues payload to `rq`.
- `relackproc` wakes every `Rudptickms`, retransmits peers whose first unacked packet has timed out, and sends delayed ACK-only packets when needed.
- `reliput` handles ack validation by generation, hangup packets, receive-generation changes, unacked queue advancement, flow-control wakeups, duplicate/out-of-order rejection, and in-order receive acceptance.
- `relhangup` posts a hangup event to the conversation event queue, discards unacked data, resets peer sequence/generation state, and wakes blocked writers.

## Control and Observability
- `headers`: enables Plan 9 UDP-style address headers on read/write.
- `hangup ip port`: forgets a peer and sends a hangup ack.
- `randdrop [percent]`: intentionally drops outgoing packets for testing.
- `rudpstate` reports open/closed state plus per-peer unacked counts.
- `rudpstats` reports datagram counters, retransmits, and out-of-order packets.

## Dependencies and Integration
Uses core Plan 9 IP stack helpers: `Fsstdconnect`, `Fsstdannounce`, `Fsconnected`, `iphtadd`, `iphtlook`, `iphtrem`, `ptclcsum`, `icmpnoconv`, `ipoput4`, queues, `Block` manipulation, `QLock`, `Rendez`, and kernel process timers.

## Risks and Notes
The implementation is IPv4-only despite carrying IPv6-sized internal addresses. Reliability is per-destination inside one conversation, uses a global `generation` counter with wrap avoidance for `Hangupgen`, and assumes in-order delivery to users by rejecting out-of-order data rather than buffering it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/rudp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/tcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/tcp.c

## Purpose
Implements Plan 9's TCP protocol for IPv4 and IPv6. It provides connection setup/teardown, data transfer, retransmission timers, delayed ACKs, keepalives, congestion control, resequencing, SYN-flood limbo handling, protocol stats, and the Plan 9 IP `Proto` interface.

## Main Data Structures
- `Tcp4hdr` / `Tcp6hdr`: pseudo-header plus TCP header layouts used for checksum and packet construction.
- `Tcp`: normalized per-segment metadata decoded from packet headers and encoded back to headers.
- `Tcpctl`: per-conversation TCP control block. Tracks state, send/receive sequence variables, windows/scaling, congestion window, slow-start threshold, RTT estimators, timers, keepalive counters, resequencing queue, and protocol header templates.
- `Tcptimer`: linked-list timer entry driven by the protocol timer kproc.
- `Reseq`: queued out-of-order segment with associated `Block`.
- `Limbo`: half-open listener-side SYN/SYN-ACK state held outside normal conversations to reduce SYN attack pressure.
- `Tcppriv`: protocol-global timer list, conversation hash table, limbo hash table, kproc startup state, and stats.

## Connection Lifecycle
- `tcpinit` registers the TCP protocol with `Fsproto`, using `scalednconv()` for maximum conversations.
- `tcpconnect` validates closed state, performs standard connect setup, then calls `tcpstart(..., TCP_CONNECT)`.
- `tcpannounce` performs standard announce setup, then starts a listening TCP control block.
- `tcpstart` starts the timer kproc if necessary, initializes the TCB, adds the conversation to the IP hash table, and either enters `Listen` or sends a SYN and enters `Syn_sent`.
- `tcpclose` maps local close to state-machine transitions: immediate local close for listening/closed/syn-sent, FIN transmission for established states, and `Last_ack` from `Close_wait`.
- `localclose` removes the conversation from the hash table, stops timers, dumps resequencing state, wakes listeners/connect waiters as needed, hangs up queues, and moves to `Closed`.

## Packet Input
- `tcpiput` detects IPv4 versus IPv6, verifies checksum, parses TCP options, trims the packet to the declared payload, looks up the conversation, and handles listener limbo cases.
- Listener SYNs are placed in `Limbo` via `limbo`; matching final ACKs are promoted to a new conversation via `tcpincoming`.
- The state-machine logic handles `Closed`, `Syn_sent`, `Syn_received`, established transfer states, FIN states, `Time_wait`, RSTs, ACK validation, urgent-pointer bookkeeping, data queueing, FIN processing, and forced ACK decisions.
- `tcptrim` enforces receive-window acceptance, trims duplicates at the left edge and excess at the right edge, and clears SYN/FIN/URG as appropriate.
- Out-of-order data is queued by `addreseq`; adjacent queued segments are later pulled with `getreseq`.

## Packet Output
- `tcpoutput` sends up to 100 packets per pass, applying delayed-ACK rules, window opening ACKs, zero-window probes, congestion window, advertised send window, MSS limit, SYN/SYN-ACK option generation, PSH/FIN flags, and per-version header/checksum construction.
- `htontcp4` and `htontcp6` build wire packets and encode MSS/window-scale options on SYN packets.
- `ntohtcp4` and `ntohtcp6` parse incoming header length, flags, window, urgent pointer, payload length, MSS, and window-scale options.
- `sndrst` and `tcphangup` generate reset packets and close local state.

## Timers and Reliability
- `tcpackproc` is the global timer kproc. It ticks every `MSPTICK`, advances active timers, invokes ready callbacks, and calls `limborexmit`.
- `tcpsettimer` derives retransmit timeout from smoothed RTT, mean deviation, and exponential backoff, clamped between 300 ms and 64 s.
- `tcptimeout` handles retransmission timeout, congestion response, recovery reset, and eventual timeout close.
- `tcprxmit` retransmits one segment at `snd.una` while preserving the normal send pointer and congestion window.
- `tcpsynackrtt` and `update` maintain RTT estimates from SYN/SYN-ACK and later acknowledged full-MSS packets.
- `tcpkeepalive`, `tcpsendka`, and `tcpstartka` implement BSD-style keepalives and optional port-hog defense probes.

## Congestion and Flow Control
- Implements slow start and congestion avoidance with appropriate byte counting (`tcpabcincr`).
- Implements NewReno-style fast retransmit/recovery with duplicate ACK threshold, recovery window inflation/deflation, partial ACK handling, and RTO recovery counters.
- Supports RFC 1323-style window scaling. `tcpsetscale` configures queue limits, receive scaling, send scaling, and receive window size while bounding local queue commitment with `Maxqscale`.
- `tcprcvwin` calculates receive window from queue occupancy and avoids moving the right edge backward.

## Control and Observability
- Control commands:
  - `hangup`: send RST and close.
  - `keepalive [ms]`: enable keepalives for established connections.
  - `checksum n`: toggles outgoing checksum behavior.
  - `tcpporthogdefense on|off`: toggles stateless port-hog defense.
- `tcpstate` reports TCP state, queue lengths, resequencing size, RTT state, congestion/window values, timers, and rereceive bytes.
- `tcpstats` prints MIB and non-MIB counters including opens, resets, segment counts, checksum/header/length errors, resequencing limits, delayed ACKs, and recovery statistics.
- `tcpgc` opportunistically closes stale `Syn_received` and long-lived `Finwait2` conversations when channel pressure occurs.

## Dependencies and Integration
Integrates with Plan 9 IP hash tables, queues, block buffers, ICMP advice, IPv4/IPv6 output, timers, locks, and filesystem connection management. It depends on common IP helpers for local address selection, protocol checksum, packet output, and conversation allocation.

## Risks and Notes
This is a complete in-kernel TCP implementation with many coupled state transitions. Notable edge areas include overflow-sensitive RTT calculations, resequencing queue limits tied to receive window and MSS, limbo list linear scans, optional checksum disabling, and hardware/offload checksum flag interaction via `Btcpck`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/udp.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/ip/udp.c

## Purpose
Implements Plan 9 UDP for IPv4 and IPv6, exposing datagram send/receive through the IP protocol conversation interface.

## Main Data Structures
- `Udp4hdr` and `Udp6hdr`: IPv4/IPv6 pseudo-header plus UDP header layouts used for checksum and packet construction.
- `Udpstats`: MIB-style datagram, no-port, error, and output counters.
- `Udppriv`: protocol-private hash table and stats.
- `Udpcb`: per-conversation state containing the `headers` mode flag.

## Behavior
- `udpinit` registers protocol `17` with connect, announce, create, close, receive, advise, ctl, state, and stats callbacks.
- `udpconnect` and `udpannounce` use standard Plan 9 connection setup and add the conversation to the protocol hash table.
- `udpcreate` opens a message receive queue and a bypass write queue that calls `udpkick` directly.
- `udpkick` builds IPv4 or IPv6 UDP packets, optionally consuming the Plan 9 `headers` address prefix, selecting a local address when needed, computing the pseudo-header checksum, and sending via `ipoput4` or `ipoput6`.
- `udpiput` validates IPv4 or IPv6 checksum, looks up the conversation, creates a new accepted conversation for announced non-header sockets, trims IP/UDP headers, optionally prepends source/local/interface/port metadata, and queues the datagram to `rq`.
- `udpadvise` maps ICMP-style advice back to matching conversations and hangs up queues unless advice is ignored.

## Control and Observability
- `headers` enables 52-byte address metadata on read/write.
- `udpstate` reports open/closed plus input/output queue lengths.
- `udpstats` reports in, no-port, error, and out datagram counters.

## Dependencies and Integration
Uses Plan 9 IP hash lookup, ICMP no-conversation responses, IPv6 host-unreachable responses, queue operations, block trimming/padding, local address selection, and protocol checksum helpers.

## Risks and Notes
IPv6 UDP checksums are always verified, while IPv4 checksum validation is conditional on a nonzero checksum field. Header mode lets users specify addresses per datagram, bypassing the connected peer fields for output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/ip/udp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/arch.c

## Purpose
Provides ARM architecture glue for the Kirkwood Plan 9 kernel: process register setup, user/kernel accounting on exit, alignment validation, kproc bootstrap, process save/restore hooks, user-mode detection, and simple atomic operations.

## Main Functions
- `setkernur`: fabricates enough `Ureg` context to show a sleeping kernel process stack.
- `validalign`: validates user address alignment, relaxing 64-bit alignment to 32-bit on this 32-bit ARM port.
- `kexit`: updates user-visible `Tos` cycle accounting before returning to user mode and flushes the cache line to make it visible.
- `userpc`, `dbgpc`, `userureg`: inspect saved user register state.
- `kprocchild` and `linkproc`: set initial stack/PC and run the kernel-process function.
- `procsetup`, `procsave`, `procrestore`: delegate FPU process hooks and maintain process cycle accounting.
- `_xinc`, `_xdec`, `ainc`, `adec`, `cas32`: interrupt-masked atomic primitives with coherence after successful CAS.

## Dependencies and Integration
Depends on ARM `Ureg`, `Proc`, scheduler labels, `Tos`, FPU helpers, interrupt priority primitives, and cache maintenance.

## Risks and Notes
The atomic operations are coarse-grained, implemented by raising interrupt priority rather than hardware atomic instructions. `setregisters` is a placeholder and deliberately does not allow devproc register modification here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/archkw.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/archkw.c

## Purpose
Contains Marvell Kirkwood/SheevaPlug platform-specific setup: SoC register base addresses, CPU address window repair, cache discovery, L2 cache enablement, GPIO reset setup, clock/power gating, reboot, Ethernet discovery, and flash discovery.

## Main Data Structures
- `GpioReg`, `L2uncache`, `Dramctl`, `Addrmap`: memory-mapped Kirkwood register layouts.
- `soc`: global `Soc` register map for CPU, interrupt controller, NAND, crypto, EHCI, SPI, TWSI, RTC, clock, Ethernet, SATA, UART, and GPIO controllers.

## Initialization Flow
- `archreset` runs early: disables watchdog, configures GPIO outputs for LEDs/USB power, enables CPU clocks, marks L2 as present, adjusts DRAM control, and applies an analog register guideline.
- `archconfinit` runs later: sets CPU frequency/delay loop, repairs address maps, optionally prints windows, prints cache configuration, and enables L2 cache.
- `fixaddrmap` scans CPU windows and enables/remaps the crypto SRAM target to `PHYSCESASRAM`, then verifies the device internal base address.
- `cacheinfo`, `prcache`, and `prcachecfg` read CP15 cache type data and derive cache size, associativity, sets, and line size.
- `l2cacheon` follows Marvell guidelines for cache lockdown, L2 config, timing, uncached windows, writeback/write-through choice, and final L1/L2 enable.

## Platform Services
- `archether` reports up to two Ethernet controllers as type `88e1116`.
- `archreboot` requests a soft reset through CPU reset registers, then waits.
- `archconsole` is currently effectively disabled/commented.
- `archflashreset` exposes NAND flash at detected physical locations for `devflash`.
- `archflashwp` is a stub.

## Dependencies and Integration
Integrates with CP15 helpers, cache maintenance, Kirkwood `io.h` constants, Ethernet and flash device layers, clock shutdown, and global `soc`.

## Risks and Notes
Most behavior is hardware-guideline-specific. The L2 uncached window disables caching for the upper half of physical address space to avoid caching I/O registers. Debug printing is compiled but disabled by `Debug = 0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/archkw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/arm.h

## Purpose
Defines ARM processor status bits, CP15 register encodings, cache/TLB operation constants, Sheeva/Kirkwood L2 test/config registers, and MMU page-table permission/cache bits.

## Key Contents
- Program status register mode and flag constants such as `PsrMusr`, `PsrMirq`, `PsrMsvc`, `PsrDirq`, `PsrDfiq`, and condition flags.
- Coprocessor numbers and CP15 primary/secondary register selectors.
- CP15 control bits for MMU, alignment, data/instruction cache, write buffer, endian mode, permissions, and high vectors.
- Cache, TLB, and L2 test/config operation constants used by assembly and dynamic CP15 helpers.
- ARM page-table entry constants for L1/L2 mappings, cache/bufferability, domains, access permissions, and `HVECTORS`.
- PHY-facing helper register constants are not here; those are in `ethermii.h`.

## Dependencies and Integration
Used by ARM assembly, coprocessor access helpers, cache/MMU setup, exception handling, and platform initialization.

## Risks and Notes
The constants target pre-v7 ARM/ARM926EJ-S behavior, including implementation-defined `Mbo` and Sheeva-specific L2 control registers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arm.s -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/arm.s

## Purpose
Provides shared ARM assembly macros and constants for the SheevaPlug/Kirkwood ARM926EJ-S port.

## Key Contents
- Address translation macros `PADDR`, `KADDR`, and L1 page-table index `L1X`.
- PTE template constants for DRAM and I/O sections.
- `PUTC` debug-output macro writing to `PHYSCONS`.
- `CLZ` instruction encoding macro.
- Barrier macros:
  - `DMB`: data memory barrier using CP15.
  - `DSB`: drain/write-buffer/data synchronization barrier.
  - `ISB`: instruction prefetch flush.
  - `BARRIERS`: combined ISB and DSB.
- Page-table fill/zero macros `FILLPTE` and `ZEROPTE`.

## Dependencies and Integration
Included by low-level assembly files needing memory barriers, page-table construction, early console output, and ARM CP15 encodings from `arm.h`.

## Risks and Notes
The barrier implementation is ARM926/Sheeva-specific and uses CP15 cache operations rather than newer architectural barrier mnemonics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/arm.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/cga.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/cga.c

## Purpose
Implements a simple CGA-style text console backend using memory at `0xB8000`.

## Behavior
- Maintains `cgapos` as a byte offset into the 80x25 text buffer.
- `cgascreenputc` handles newline, tab, backspace, normal character output, scrolling, and cursor update.
- `cgascreenputs` serializes writes with `cgascreenlock`, avoiding deadlock if called from interrupt context.
- `screeninit` reads the cursor position from CGA registers and installs `cgascreenputs` as `screenputs`.

## Dependencies and Integration
Uses Plan 9 screen output hook `screenputs`, kernel lock primitives, and `KADDR` mapping.

## Risks and Notes
`inb` and `outb` are TODO stubs in this port, so cursor register access is nonfunctional unless replaced elsewhere. This file appears more like inherited PC console code than real Kirkwood display hardware support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/cga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/clock.c

## Purpose
Implements Kirkwood timer, watchdog, delay, and fast tick support.

## Main Data Structures
- `TimerReg`: memory-mapped timer control, reload, current timer, watchdog reload, and watchdog counter registers.

## Behavior
- `clockshutdown` disables all timers and watchdog.
- `clockinit` verifies timer interrupt delivery, configures timer0 as the periodic kernel tick, timer1 as a free-running cycle/performance counter, and enables watchdog reset output.
- `clockintr` refreshes the watchdog, increments a local sanity tick counter, calls generic `timerintr`, and clears the CPU timer interrupt.
- `timerset` programs timer0 for the next deadline, clamped between `MinPeriod` and `MaxPeriod`.
- `fastticks` combines the 32-bit down/up performance tick source with `m->fastclock` high bits to produce a monotonic 64-bit value.
- `perfticks`, `lcycles`, and `µs` expose performance/cycle time.
- `microdelay` and `delay` busy-wait from `m->delayloop`.

## Dependencies and Integration
Uses `soc.clock`, `soc.cpu`, interrupt setup/clear helpers, generic timer interrupt code, CPU frequency constants, watchdog reset bits, and per-Mach time state.

## Risks and Notes
Timer0 sanity checking briefly lowers interrupt priority during initialization. Delay calibration starts from a fixed estimate until later adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/coproc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/coproc.c

## Purpose
Provides dynamic ARM coprocessor and VFP register access helpers by generating short instruction sequences in memory, flushing caches, and calling them.

## Main Functions
- `cpwr`: emits an `MCR` instruction plus return, then executes it to write a coprocessor register.
- `cpwrsc`: CP15/system-control wrapper around `cpwr`.
- `cprd`: emits an `MRC` instruction plus return, then executes it to read a coprocessor register.
- `cprdsc`: CP15/system-control wrapper around `cprd`.
- `fprd`: emits `VMRS` to read a VFP register.
- `fpwr`: emits `VMSR` to write a VFP register.

## Dependencies and Integration
Uses interrupt masking, cache writeback/invalidate, instruction cache invalidation, caller-PC segment mapping, and constants from `arm.h`.

## Risks and Notes
This approach depends on executable stack/data mapping behavior via `MAP2PCSPACE`, careful cache synchronization, and correct instruction encoding. It is powerful but architecture-specific.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/coproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/dat.h

## Purpose
Defines core machine-dependent kernel types and globals for the Plan 9 Kirkwood ARM port.

## Key Definitions
- Forward declarations for core kernel structures such as `Conf`, `FPsave`, `Label`, `Lock`, `Mach`, `Proc`, `Page`, `Soc`, and `Ureg`.
- `Lock`: spin lock state including key, saved status register, PC, owning proc/mach, and interrupt-lock flag.
- `Label`: saved stack and PC for scheduler context.
- `FPsave`: emulated floating-point save area and FP state flags.
- `Conf` / `Confmem`: boot-time memory and sizing configuration.
- `MMMU` and `PMMU`: machine/proc MMU state, including L1 table tracking and cached L2 page list.
- `Mach`: per-CPU state including current proc, scheduler label, alarms, ticks, CPU/SOC IDs, fast clock, stats, exception save stacks, and performance state.
- `ISAConf` and `DevConf`: parsed device configuration descriptors.
- `Memcache`: cache geometry summary.
- `Soc`: global memory-mapped SoC register base addresses.

## Globals and Constants
- Declares register globals `m` and `up`.
- Declares `kseg0`, `machaddr`, `memsize`, debug flags, and `soc`.
- Defines `Frequency = 1200 MHz`, one cache color, vector page layout, fake `kmap`, and `active` machine state.

## Dependencies and Integration
Included broadly by kernel C files in this port. It bridges architecture-specific structures to common `portdat.h`.

## Risks and Notes
This is foundational ABI/configuration surface for the port. Changes affect scheduler, memory management, interrupt handling, device setup, and process accounting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devarch.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/devarch.c

## Purpose
Implements the `#P` architecture device namespace for Kirkwood, exposing architecture-specific read/write files and CPU/timebase information.

## Behavior
- Maintains a fixed-size `archdir` table plus matching read/write callback arrays.
- `addarchfile` adds immutable named files to `#P`, rejecting duplicates and paths beyond `Qmax`.
- Standard device methods attach, walk, stat, open, close, read, and write through Plan 9 device helpers.
- `archread` dispatches directory reads and per-file read callbacks.
- `archwrite` dispatches per-file write callbacks or rejects with `Eperm`.

## Exposed Files
- `cputype`: read via `cputyperead`, reporting ARM/Marvell SoC identity and CPU MHz.
- `timebase`: read via `tbread`, reporting cycle counter hex.
- `nsec` support exists as `nsread` but is commented out in `archinit`.

## Hardware Identification
- `cputype2name` reads the SoC/device ID through PCIe and CP15, identifies Marvell/ARM926EJ-S architecture, and decodes known 88F6281 revisions (`Z0`, `A0`, `A1`).

## Dependencies and Integration
Uses Plan 9 device table plumbing, `soc` register mappings, CP15 ID helper `cpidget`, PCIe register layout from `io.h`, and `cycles`.

## Risks and Notes
The file table is capped at 16 entries and cannot delete files. CPU naming relies on the same unusual PCIe-derived device identity approach noted in the code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devarch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devether.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/devether.c

## Purpose
Implements the generic Plan 9 Ethernet device `#l` for this port. It wraps controller-specific drivers behind a common `Ether`/`Netif` interface and handles channel operations, packet fanout, loopback, card registration, reset, shutdown, and CRC utilities.

## Main Behavior
- `etherattach`, `etherwalk`, `etherstat`, `etheropen`, `etherclose`, `etherread`, `etherbread`, `etherwrite`, and `etherbwrite` implement the device interface by delegating to `netif` helpers and controller callbacks.
- `etheriq` receives an Ethernet frame, validates multicast interest, determines local/broadcast/promiscuous delivery, fans packets out to matching `Netfile`s, and optionally avoids a copy for one receiver.
- `etheroq` handles outgoing packets, loops back local/broadcast/promiscuous-visible frames, queues non-loopback traffic to the controller output queue, and calls the controller transmit callback.
- `etherrtrace` emits compact trace records for header-only listeners.
- `addethercard` registers controller reset functions by type.
- `parseether` parses colon-separated MAC strings.
- `etherreset` asks `archether` for platform devices, matches registered card types, parses options, invokes controller reset, enables interrupts, initializes `netif`, allocates output queues, and publishes `etherxx`.
- `ethershutdown` calls controller shutdown hooks before reboot.
- `ethercrc` computes Ethernet CRC slowly in software.
- `dumpnetif` and `dumpoq` provide diagnostic printing.

## Dependencies and Integration
Uses platform discovery via `archether`, controller drivers registered by `addethercard`, Plan 9 `netif`, queues, blocks, interrupts, and Ethernet packet definitions.

## Risks and Notes
Packet fanout copies frames for all but one matching receiver. Controller-specific stats may be refreshed on reads of `ifstats` or `stats`. Output writes force the source MAC to the interface address for user-provided frames.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devrtc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/devrtc.c

## Purpose
Implements the Kirkwood real-time clock device `#r`, exposing a single `rtc` file containing seconds since 1970.

## Main Data Structures
- `RtcReg`: memory-mapped RTC time/date/alarm/interrupt registers.
- `Rtc`: decoded calendar fields.

## Behavior
- `rtcattach` maps `rtcreg` to `soc.rtc`.
- `rtcread` returns the current epoch seconds via `readnum`.
- `rtcwrite` accepts a numeric epoch value, converts it to calendar fields, and writes hardware registers.
- `rtctime` reads the RTC under interrupt lock until two consecutive reads match, reducing rollover inconsistency.
- `_rtctime` decodes BCD time/date registers, handling 12-hour and 24-hour modes.
- `setrtc` writes BCD fields back to hardware.
- `rtc2sec` and `sec2rtc` convert between calendar fields and seconds since 1970.

## Dependencies and Integration
Uses Plan 9 device helpers, `soc.rtc`, lock primitives, BCD conversion, and time constants.

## Risks and Notes
Leap-year logic treats every year divisible by 4 as leap, without century exceptions. Hardware year is decoded as 2000 plus a two-digit BCD value.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devtwsi.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/devtwsi.c

## Purpose
Implements the Kirkwood TWSI/I2C device, exposing a `twsi` file for reads and writes to an I2C slave address encoded as the file offset.

## Main Data Structures
- `Kwtwsi`: memory-mapped TWSI controller registers.
- `Twsi`: serialized transfer state: lock, interrupt rendezvous, buffer pointer/range, target address, completion flag, and error string.

## Transfer Flow
- `twsixfer` serializes a transaction with `QLock`, initializes transfer state, asserts START, sleeps for interrupts, advances the read/write state machine, clears interrupt source, reenables interrupts, then returns transferred byte count or raises an error.
- `twsidoread` handles START, slave-read ack, data receive/ack, final no-ack, and abnormal status.
- `twsidowrite` handles START, slave-write ack, data ack, byte transmission, and abnormal status.
- `interrupt` marks an interrupt event, wakes the sleeper, disables further TWSI interrupts until the thread advances state, and clears the interrupt controller source.
- `twsiinit` enables the TWSI interrupt; `twsishutdown` disables it.

## Device Interface
- Device rune is `L'⁲'`; directory contains `twsi`.
- `twsiread` and `twsiwrite` call `twsixfer` with the channel offset as target address.
- `twsiopen`, `twsiwalk`, `twsistat`, and `twsiclose` use standard device helpers.

## Dependencies and Integration
Uses `soc.twsi`, interrupt controller helpers, Plan 9 device plumbing, locks, rendezvous sleep/wakeup, and hardware status codes.

## Risks and Notes
Transfers are strictly serialized globally. Error reporting is coarse (`"abnormal status"`), and the offset-as-address interface makes caller discipline important.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devtwsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devusb.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/devusb.c

## Purpose
Implements the Plan 9 USB device framework `#u`. It manages host controller registration/probing, root-hub representation, device and endpoint allocation, endpoint filesystem layout, endpoint control commands, and endpoint I/O dispatch to HCI-specific callbacks.

## Filesystem Model
- Root `#u` lists `usb` and any named endpoint aliases.
- `#u/usb` lists global `ctl` and endpoint directories named `epN.M`.
- Each endpoint directory contains:
  - `data`: exclusive endpoint I/O file.
  - `ctl`: endpoint status/control file.
- Endpoint 0 (`epN.0`) represents a device control endpoint and owns per-device state.

## Main Data Structures and Globals
- `Hcitype`: host-controller type string plus reset callback.
- `hcitypes`, `hcis`: registered/probed host-controller drivers.
- `eps`: global endpoint table, protected by `epslck`.
- `epmax`, `usbidgen`: endpoint and USB device address allocation state.
- `Ep` and `Udev` are defined in `../port/usb.h` and used throughout.

## Endpoint and Device Allocation
- `addhcitype` registers a controller type.
- `epalloc`, `getep`, and `putep` allocate, refcount, publish, and free endpoint structures.
- `newdev` creates endpoint 0 and a `Udev`, assigning speed, state, root-hub status, and default control endpoint settings.
- `newdevep` creates nonzero endpoints on an existing device and fills defaults for control, interrupt, and isochronous endpoints.
- `newusbid` monotonically allocates USB addresses and warns past the 7-bit address range.

## Host Controller Flow
- `usbreset` probes HCI types and controller slots using registered reset callbacks.
- `hciprobe` allocates an `Hci`, calls its reset callback, enables interrupts, and reports the root endpoint path.
- `usbinit` calls HCI init callbacks and creates a root-hub device for each controller.
- `usbshutdown` calls HCI shutdown callbacks.

## I/O Flow
- `usbopen` validates endpoint availability, mode, configuration, exclusive use, computes load, and calls `ep->hp->epopen`.
- `usbread` dispatches directory/control reads, root-hub emulated reads, or HCI `epread`.
- `usbwrite` dispatches global/endpoint control writes, root-hub emulated setup writes, or HCI `epwrite`.
- `usbclose` closes active endpoint I/O through HCI `epclose` and releases endpoint refs.

## Control Interface
Global `#u/usb/ctl`:
- `debug on|off|n`: toggles framework and HCI debug.
- `dump`: prints endpoint and HCI state.

Endpoint `ctl` commands include:
- `new nb ctl|bulk|intr|iso r|w|rw`: create endpoint.
- `newdev full|low|high port`: create a child device from a hub endpoint.
- `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `address`, `detach`, `debug`, `clrhalt`, `name`, `timeout`, `reset`.

## Root Hub Emulation
- `rhubwrite` accepts limited class/port setup requests for port enable, port reset, and get status.
- `rhubread` returns the pending root-hub reply.

## Dependencies and Integration
Relies on HCI drivers for actual controller operations, Plan 9 device helpers, endpoint and USB constants from `usb.h`, interrupt setup from HCI reset, and user-space `usbd` for enumeration/configuration policy.

## Risks and Notes
The interface intentionally exposes a nonstandard USB control model to user space. Endpoint lifetime is reference-counted but intertwined with filesystem refs, open refs, and device detach handling, making `putep` paths sensitive. Bandwidth/load accounting is rough and based on worst-case microsecond estimates.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/devusb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ether1116.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/ether1116.c

## Purpose
Implements the Marvell Kirkwood gigabit Ethernet controller and Marvell 88E1116/88E1121-family PHY driver used on SheevaPlug/OpenRD/GuruPlug-like systems.

## Main Data Structures
- `Rx` / `Tx`: hardware DMA descriptors for receive and transmit rings.
- `Mibstats`: memory-mapped MAC statistic counters.
- `Gbereg`: complete register map for the Kirkwood GbE controller, including SMI/MDIO, DMA windows, port config/status, interrupts, queue pointers, MIB counters, and address filters.
- `Ctlr`: software controller state, including descriptor rings, block arrays, ring indices, MII state, port number, receive rendezvous, and accumulated stats.
- `freeblocks`: global pool of aligned receive blocks recycled through a custom `Block.free` hook.

## Receive Path
- `ctlralloc` allocates aligned receive buffers, uncached Rx descriptors, and uncached Tx descriptors.
- `rxreplenish` fills empty Rx descriptors with recycled blocks and hands them to DMA.
- `rxkick` starts/restarts receive queue 0.
- `interrupt` notices receive events, sets `haveinput`, and wakes `rcvproc`.
- `rcvproc` periodically harvests MIB stats and calls `receive`.
- `receive` scans completed Rx descriptors, validates first/last and MAC error bits, invalidates caches for received data, skips the two-byte hardware alignment pad, passes packets to `etheriq`, and replenishes descriptors.

## Transmit Path
- `etheroq` in `devether.c` queues packets to `ether->oq`; this driver’s `transmit` drains that queue.
- `txreplenish` reclaims completed Tx descriptors and frees transmitted blocks.
- `transmit` writes back packet cache lines, fills Tx descriptors, marks them DMA-owned, kicks queue 0, and enables Tx-empty/error interrupts.
- `txkick` starts/restarts transmit queue 0.

## Interrupt and Link Handling
- `interrupt` clears main and extended interrupt causes, handles receive, transmit-end, PHY status changes, Tx/Rx errors, overrun/underrun, link-change completion, and unknown causes.
- `ethercheck` warns when the main interface has not sent or received packets for `Etherstuck` seconds.
- `etheractive` updates last-activity time.

## PHY/MII Handling
- `miird` and `miiwr` implement MDIO/SMI access through controller registers with busy/read-valid waits.
- `mymii` probes PHYs, with special handling for dual-port boards whose second Ethernet controller shares PHY discovery through controller 0.
- `kirkwoodmii` allocates `Mii`, probes PHYs, resets/autonegotiates if needed, waits for autonegotiation, and updates `ether->mbps`.
- `miiphyinit` configures Marvell PHY LED behavior, RGMII power, RGMII timing delay, MDIX, and exits power-down/energy-detect modes.

## Hardware Initialization
- `reset` allocates `Ctlr`, assigns IRQ and register base from `soc.ether`, sets I/O voltage config, shuts down/reset hardware, sets RGMII mode, assigns PHY address, initializes MII/PHY, reads/configures MAC address filters, and installs Ethernet callbacks.
- `ctlrinit`, called on first attach, configures DRAM access windows, descriptor rings, MIB counters, SDMA burst/coalescing, interrupt masks, address filters, port config, RGMII/port serial control, MTU bucket, receive kproc, and receive queue start.
- `shutdown` quiesces queues, resets the controller, powers down port serial control, and clears descriptor pointers.
- `cfgdramacc` configures controller DRAM windows for DMA.

## Control and Stats
- Custom control command `jumbo on|off` exists, but `jumbo on` immediately errors as disabled because the input queue does not expect jumbo frames.
- `ifstat` reads and accumulates hardware MIB counters, reports interrupt/error/ring/link/flow/stat counters, and accounts for errata around high halves of byte counters.
- `archetheraddr` reads MAC address registers, synthesizes a secondary MAC if needed, and programs unicast/multicast filters.
- `ether1116link` registers this driver as card type `88e1116`.

## Dependencies and Integration
Integrates with the generic `devether.c` layer, `ethermii.c` MII helpers, Kirkwood `soc` registers, cache/L2 cache maintenance routines, interrupt controller, Plan 9 queues/blocks, and IP/Ethernet packet definitions.

## Risks and Notes
DMA correctness depends on uncached descriptors, explicit cache writeback/invalidate for packet buffers, alignment, and coherent register writes. The dual-PHY board support is acknowledged as a hardware-specific hack. Receive buffering is shared globally, and low buffer conditions produce kernel diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ether1116.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/etherif.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/etherif.h

## Purpose
Defines the common Ethernet controller interface used by the generic Ethernet device and hardware-specific drivers in this port.

## Key Contents
- `MaxEther = 2` and `Ntypes = 8`.
- `Ether` structure embedding `RWlock`, `ISAConf`, controller identity/configuration, MTU bounds, MAC address, callbacks, controller private pointer, output queue, link/full-duplex state, activity timestamp, and `Netif`.
- Controller callbacks include attach, close, detach, transmit, interrupt, ifstat, ctl, power, and shutdown.
- Declares `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Defines circular ring helper macros `NEXT` and `PREV`.

## Dependencies and Integration
Shared by `devether.c`, `ether1116.c`, and other Ethernet controller drivers.

## Risks and Notes
The `Ether` structure is the ABI between generic netif-facing code and controller-specific code. Callback ownership and queue expectations must remain consistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/etherif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ethermii.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/ethermii.c

## Purpose
Provides generic MII/PHY probing, reset, autonegotiation, register access wrappers, and link-status decoding for Ethernet drivers.

## Main Functions
- `mii`: probes PHY addresses in a mask, reads ID registers, allocates `MiiPhy` entries, records OUI/PHY number, sets default advertised capability caches, and picks `curphy`.
- `miimir` and `miimiw`: access current PHY registers via driver-supplied MDIO callbacks.
- `miireset`: sets the PHY reset bit and spins until reset clears.
- `miiane`: configures autonegotiation advertisement for 10/100, pause, asymmetric pause, and optionally 1000BASE-T capabilities, then enables/restarts autonegotiation.
- `miistatus`: verifies autonegotiation/link status, determines negotiated speed and duplex from 1000BASE-T status or ANAR/ANLPAR overlap, and derives receive/transmit flow-control direction.

## Dependencies and Integration
Requires driver-supplied `Mii.mir` and `Mii.miw` callbacks, register definitions from `ethermii.h`, and memory allocation.

## Risks and Notes
Status reads follow the common sticky-link-status pattern by reading `Bmsr` twice. `miireset` busy-waits without timeout, so a stuck PHY reset bit can hang the caller.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ethermii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ethermii.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/kw/ethermii.h

## Purpose
Defines MII/PHY register numbers, bit masks, Marvell 88E1116-specific paged registers, and the `Mii`/`MiiPhy` structures used by generic and controller-specific Ethernet code.

## Key Contents
- Standard MII registers: `Bmcr`, `Bmsr`, PHY ID registers, autonegotiation advertisement/link partner registers, gigabit control/status, and extended status.
- Marvell-specific registers: `Scr`, `Ssr`, `Ier`, `Isr`, `Escr`, `Recr`, `Eadr`, `Globsts`, impedance registers, and `Scr2`.
- Basic control/status bits for reset, loopback, speed, duplex, power-down, autonegotiation, link status, capabilities, and extended status.
- Autonegotiation bits for 10/100 modes and pause/asymmetric pause.
- Gigabit capability/status bits for 1000BASE-T half/full duplex.
- Marvell page-specific bits for power-down, MDIX, energy detect, RGMII power-up, and TX/RX timing.
- `Mii`: controller pointer, PHY table, current PHY, probe mask, and MDIO callbacks.
- `MiiPhy`: OUI, address, advertised capability caches, link, speed, duplex, and flow-control state.
- Function prototypes for `mii`, `miiane`, `miimir`, `miimiw`, `miireset`, and `miistatus`.

## Dependencies and Integration
Included by `ethermii.c` and `ether1116.c`.

## Risks and Notes
The header mixes standard IEEE MII definitions with Marvell-specific extension registers, so users must select the correct register page before using page-specific constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/kw/ethermii.h -->