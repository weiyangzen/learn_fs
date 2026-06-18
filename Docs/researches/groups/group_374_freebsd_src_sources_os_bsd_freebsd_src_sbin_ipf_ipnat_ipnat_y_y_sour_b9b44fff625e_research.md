# Group Research: group_374_freebsd_src_sources_os_bsd_freebsd_src_sbin_ipf_ipnat_ipnat_y_y_sour_b9b44fff625e

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat_y.y

## Purpose
Yacc grammar and loader implementation for `ipnat` NAT rule files. It parses map, bimap, map-block, redirect, rewrite, divert, proxy, pool/hash lookup, address, port, protocol, and option syntax into `ipnat_t` structures, then applies those rules through IPFilter NAT ioctls.

## Main Elements
- Grammar handles `map`, `bimap`, `map-block`, `rdr`, `rewrite`, `divert`, `from/to`, `portmap`, `icmpidmap`, `proxy`, `mssclamp`, `round-robin`, `sticky`, `tag`, `purge`, `inet`, and `inet6`.
- `ipnat_parsefile()` and `ipnat_parsesome()` initialize lexer state and repeatedly parse configuration input.
- `newnatrule()` allocates and links a new variable-sized `ipnat_t` rule object.
- `setnatproto()`, `setmapifnames()`, and `setrdrifnames()` normalize protocol, port, interface, and map-block/group-map behavior.
- `ipnat_addrule()` wraps parsed NAT rules in `ipfobj_t` and dispatches add, remove, purge, or zero-rule ioctls.
- Proxy config support parses DNS proxy allow/deny lists and pushes them through `SIOCPROXY`.

## Dependencies And Integration
Includes `ipf.h`, `netinet/ipl.h`, and generated lexer header `ipnat_l.h`. It relies on shared libipf helpers such as `gethost()`, `getport()`, `getportproto()`, `getproto()`, `count4bits()`, `count6bits()`, `ntomask()`, `nat_setgroupmap()`, `printnat()`, `binprint()`, and `ipf_perror_fd()`.

## Risk Notes
This file mutates a variable-length `ipnat_t` with `realloc()` in `addname()` and stores string offsets into the trailing name area, so pointer repair is critical. Parser actions perform many family and mask checks, but the grammar remains stateful through globals such as `nat`, `nattop`, `yyexpectaddr`, and `suggest_port`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/Makefile

## Purpose
FreeBSD build file for the `ippool` utility.

## Main Elements
- Builds `ippool` from generated parser/lexer files and `ippool.c`.
- Installs `ippool.5` and `ippool.8`.
- Generates `ippool_y.c`/`ippool_y.h` with `yacc`, then rewrites `yy` symbols to `ippool_yy`.
- Generates `ippool_l.c`/`ippool_l.h` from shared `lexer.c`/`lexer.h` with matching symbol and include rewrites.

## Dependencies And Integration
Uses the common IPFilter lexer and yacc grammar in the local directory. Includes `<bsd.prog.mk>`.

## Risk Notes
The build depends on sed-based symbol renaming; stale generated files are cleaned through `CLEANFILES`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool.c

## Purpose
Command-line utility for managing IPFilter lookup objects: pools, hash tables, group maps, and destination lists.

## Main Elements
- `main()` dispatches add/remove pool, add/remove node, file load, flush, list, and stats modes.
- `poolnodecommand()` adds or removes pool/hash nodes, including TTL and IPv4/IPv6 address parsing.
- `poolcommand()` creates or removes named pools and hash tables.
- `loadpoolfile()` opens `IPLOOKUP_NAME` and invokes `ippool_parsefile()`.
- `poolstats()` and `poolflush()` use lookup ioctls to report or clear kernel lookup objects.
- `poollist_live()` lists live kernel objects with iterator ioctls; `poollist_dead()` reads kernel/core memory via `kmem`.
- `setnodeaddr()` converts CLI address/prefix strings into `ip_pool_node_t` or `iphtent_t`.

## Dependencies And Integration
Uses `ipf.h`, `netinet/ip_lookup.h`, `ip_pool.h`, `ip_htable.h`, and `kmem.h`. It calls libipf loader/remover/printer helpers such as `load_poolnode()`, `load_hashnode()`, `remove_pool()`, `printpool_live()`, and `printhash_live()`.

## Risk Notes
Option parsing is mode-specific and order-sensitive: type/role must be known before parsing node addresses. Dead-kernel listing depends on kernel symbol names and structure layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool_y.y

## Purpose
Yacc grammar for `ippool` configuration files. It parses table, pool, hash, group-map, destination-list, and whois/file-backed address-list syntax and loads the resulting objects.

## Main Elements
- Supports legacy `table role type = tree/hash` syntax and newer `pool ... / tree/hash/dstlist` and `group-map` syntax.
- Parses roles (`ipf`, `nat`, `auth`, `count`, `all`), in/out group-map direction, hash size/seed, destination-list policies, and weighted connection policy.
- Builds `ip_pool_node_t`, `iphtent_t`, and `ipf_dstnode_t` linked lists.
- `ippool_parsefile()` and `ippool_parsesome()` drive repeated parsing from files or stdin.
- `add_htablehosts()` and `add_poolhosts()` resolve hostnames or load address lists from `file://` and `http://` URLs.
- `read_whoisfile()` imports whois-style network ranges.

## Dependencies And Integration
Includes generated `ippool_l.h`, `ip_lookup.h`, `ip_pool.h`, `ip_htable.h`, `ip_dstlist.h`, and libipf helpers including `load_pool()`, `load_hash()`, `load_dstlist()`, `load_url()`, `gethost()`, `ntomask()`, and `parsewhoisline()`.

## Risk Notes
Parser state uses globals such as `ipht`, `iplo`, `ipld`, `poolname`, and `use_inet6`. Host/file URL parsing allocates temporary lists that must be freed after conversion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipresend/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipresend/Makefile

## Purpose
FreeBSD build file for `ipresend`.

## Main Elements
- Builds `ipresend` from `ipresend.c`, `ip.c`, `resend.c`, `sbpf.c`, `sock.c`, and `44arp.c`.
- Uses `.PATH` to compile sources from sibling `ipsend`.
- Installs `ipresend.1`.

## Dependencies And Integration
Includes `<bsd.prog.mk>`. It adapts the shared `ipsend` packet-sending code into a standalone FreeBSD program.

## Risk Notes
The program is assembled from files outside this directory, so source path and object ownership are split across `ipresend` and `ipsend`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipresend/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/Makefile

## Purpose
FreeBSD build file for `ipscan`.

## Main Elements
- Builds `ipscan` from generated `ipscan_y.c`.
- Generates `ipscan_y.h` with yacc.
- Installs `ipscan.5` and `ipscan.8`, with `ipscan.conf.5` as an mlink.

## Dependencies And Integration
Includes `<bsd.prog.mk>`. The lexer include is expected by `ipscan_y.y`.

## Risk Notes
Only the yacc-generated C source is listed, so parser source changes require regeneration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/ipscan_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/ipscan_y.y

## Purpose
Parser and main program for loading IPFilter scan/content rules.

## Main Elements
- Grammar parses `start`, `start-group`, and `content` rules with tags, client/server byte patterns, masks, `close`, `track`, `redirect`, and `else` actions.
- `cram()` decodes quoted strings and C-style escapes into fixed-size scan text buffers.
- `addtag()` constructs `ipscan_t` entries and adds/removes them with `SIOCADSCA`/`SIOCRMSCA`.
- `printent()` formats scan entries, including debug hex dumps and verbose hit/reference counters.
- `showlist()` reports scan statistics or walks kernel scan entries with `kmemcpy()`.
- `main()` parses `-f`, `-l`, `-n`, `-r`, `-s`, `-d`, and `-v`.

## Dependencies And Integration
Includes `ipf.h`, `opts.h`, `kmem.h`, generated `ipscan_l.h`, and `netinet/ip_scan.h`. Uses `IPL_SCAN` device ioctls and `printbuf()` from libipf.

## Risk Notes
Redirect syntax is accepted but explicitly reported as unsupported. `makepair()` allocates two pointers but downstream ownership is minimal, fitting short-lived parser execution rather than long-running reuse.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/ipscan_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/44arp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/44arp.c

## Purpose
4.4BSD-style hostname resolution and ARP cache lookup for packet-sending tools.

## Main Elements
- `resolve()` converts a hostname or numeric IPv4 string to a 4-byte address.
- `arp()` queries the routing table through `sysctl()` `PF_ROUTE`/`NET_RT_FLAGS` and copies the link-layer address from a matching `sockaddr_dl`.

## Dependencies And Integration
Used by FreeBSD/BSD BPF sender builds. Includes routing, `if_dl`, Ethernet, IP, and `ipsend.h`.

## Risk Notes
Allocated route-table buffer is not freed before return. It returns the first matching route entry and depends on route message layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/44arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/Makefile

## Purpose
Portable upstream makefile for building `ipsend`, `ipresend`, and `iptest` across older Unix platforms.

## Main Elements
- Defines object groups for BPF, NIT, DLPI, SunOS, BSD, Linux, Ultrix, and HP-UX targets.
- Provides target families such as `sunos4-bpf`, `sunos4-nit`, `sunos5`, `bsd-bpf`, `linux10`, `linux12`, `linux20`, `ultrix`, `hpux9`, and `hpux11`.
- Builds `iplang` parser/lexer objects through sibling `iplang`.
- Links `ipsend`, `ipresend`, and `iptest` from shared packet and platform backends.
- Includes clean and CVS cleanup targets.

## Dependencies And Integration
References `iplang`, `ipf`, platform network APIs, lex/yacc libraries, and platform-specific socket/link-layer objects.

## Risk Notes
This is not the modern FreeBSD `<bsd.prog.mk>` build path. It preserves many obsolete platform assumptions and manual recursive make invocations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/arp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/arp.c

## Purpose
Generic/Solaris-style hostname resolution and ARP lookup helper for `ipsend`.

## Main Elements
- `resolve()` resolves numeric or named IPv4 hosts.
- `arp()` caches the last IP/MAC pair, optionally uses `arp_getipv4()`, tries `ether_hostton()`, then falls back to `SIOCGARP`.
- Sends a small UDP datagram to stimulate ARP if the first lookup fails.

## Dependencies And Integration
Includes `ipsend.h` and `iplang/iplang.h`. Used in non-4.4BSD builds from the portable makefile.

## Risk Notes
Uses static cache state and raw ARP ioctl behavior. The retry path opens a UDP socket and sleeps, so failures can block briefly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dlcommon.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dlcommon.c

## Purpose
Shared DLPI helper routines for STREAMS/DLPI packet I/O tests.

## Main Elements
- Request helpers build and send DLPI control messages: info, attach, bind, unbind, multicast, promiscuous, physical address, and unitdata.
- Acknowledgment helpers read and validate `DL_INFO_ACK`, `DL_OK_ACK`, `DL_ERROR_ACK`, `DL_BIND_ACK`, and `DL_PHYS_ADDR_ACK`.
- `strgetmsg()` wraps `getmsg()` with timeout and MORECTL/MOREDATA checks.
- `printdlprim()` and many `printdl*()` helpers dump DLPI primitive contents.
- String mapping helpers translate DLPI primitive, state, errno, promiscuous level, service mode, provider style, and MAC type values.
- `strioctl()` wraps `I_STR` STREAMS ioctls.

## Dependencies And Integration
Includes STREAMS, `sys/dlpi.h`, and `dltest.h`. Used by the Solaris/HP-UX DLPI sender backend.

## Risk Notes
Old K&R-style declarations and some printer code are highly platform-specific. Several request helpers appear to set copied primitive constants incorrectly, matching historical code rather than polished modern DLPI wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dlcommon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dltest.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dltest.h

## Purpose
Small header for DLPI helper buffer sizes and utility declarations.

## Main Elements
- Defines `MAXDLBUF`, `MAXWAIT`, and `MAXDLADDR`.
- Defines `OFFADDR()` for offset-based address access in DLPI messages.
- Declares `sigalrm()`.

## Dependencies And Integration
Included by `dlcommon.c`.

## Risk Notes
`MAXDLBUF` is expressed in `long` units as used by stack `long buf[MAXDLBUF]` arrays, so actual byte size is platform-dependent.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dltest.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ip.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ip.c

## Purpose
Packet construction and sending primitives for `ipsend`, `iptest`, and `ipresend`.

## Main Elements
- `chksum()` computes Internet checksums.
- `send_ether()` builds an Ethernet header and sends a raw Ethernet/IP frame.
- `send_ip()` fills IP defaults, resolves source/destination MACs, computes checksums, and optionally fragments packets.
- `send_tcp()`, `send_udp()`, and `send_icmp()` build protocol checksums and delegate to `send_ip()`.
- `send_packet()` dispatches by IP protocol.

## Dependencies And Integration
Relies on platform backends providing `initdevice()` and `sendip()`, plus ARP helpers from `44arp.c` or `arp.c`.

## Risk Notes
Fragment handling deliberately sends unusual packet layouts for firewall testing. The code mutates packet headers temporarily and restores only the saved IP header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipresend.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipresend.c

## Purpose
CLI frontend for replaying captured IP packets through `ip_resend()`.

## Main Elements
- Parses device, gateway, MTU, input file, raw mode, and input-format options.
- Selects an `ipread` reader such as pcap, hex, or text when IPFilter readers are enabled.
- Resolves optional gateway and defaults the device by platform.
- Calls `ip_resend()` with the selected reader and input file.

## Dependencies And Integration
Uses `ipsend.h` and external `ipread` readers (`pcap`, `iphex`, `iptext`) when `NO_IPF` is not defined.

## Risk Notes
Option handling has a fall-through from `-m` to `-r`, so MTU parsing can also assign `resend` from the same option argument. This is legacy code and should be treated cautiously.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipresend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.c

## Purpose
CLI packet generator for crafting and sending raw IPv4 TCP, UDP, ICMP, or arbitrary protocol packets.

## Main Elements
- `main()` parses protocol, source/destination, gateway, device, MTU, IP options, TCP flags/window/port, and IP language file options.
- `do_icmp()` builds ICMP headers, including redirect embedded gateway/destination/source fields.
- `udpcksum()` computes UDP pseudo-header checksums.
- `send_packets()` opens the output device and delegates to `send_packet()`.
- Supports `-L` to run the separate IP language parser.

## Dependencies And Integration
Uses `ipsend.h`, `ipf.h`, `buildopts()`, `resolve()`, `initdevice()`, `send_packet()`, and optionally `do_socket()`.

## Risk Notes
This is a raw packet tool intended for firewall testing; it can craft malformed or hostile packets. It uses mutable packet buffers and assumes IPv4 header layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.h

## Purpose
Shared declarations for `ipsend`, `ipresend`, and `iptest`.

## Main Elements
- Includes `ipf.h`, `tcpip.h`, and `ipt.h`.
- Declares resolver, ARP, checksum, raw send, TCP/UDP/ICMP send, IP option, device, resend, test, socket, and kernel-memory helpers.
- Defines `KMCPY()` wrapper and fallback `OPT_RAW`.

## Dependencies And Integration
Included by all packet-sending frontends and platform backends.

## Risk Notes
This header exposes legacy prototypes with broad platform assumptions and depends on kernel TCP/IP headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsopt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsopt.c

## Purpose
IP option construction support for `ipsend`.

## Main Elements
- Defines supported IP option names: EOL, NOP, RR, TS, security, LSRR, SATID, and SSRR.
- Defines security level names.
- `ipseclevel()` maps security strings to option values.
- `addipopt()` emits one option and optional address/level/value payload.
- `buildopts()` parses comma-separated option strings and pads the option area.

## Dependencies And Integration
Used by `ipsend.c` for the `-o` option.

## Risk Notes
The option buffer is capped at 48 bytes. Parsing mutates the input string with `strtok()` and temporary separators.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsopt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptest.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptest.c

## Purpose
CLI frontend for running predefined firewall/stack packet robustness tests.

## Main Elements
- Parses destination, optional source/gateway/device/MTU, selected test number, and subtest number.
- Resolves source, destination, and gateway addresses.
- Calls `ip_test1()` through `ip_test7()` individually or all in sequence.

## Dependencies And Integration
Uses `ipsend.h` packet send/test declarations and platform default device selection.

## Risk Notes
The tool emits intentionally malformed and high-volume packet sequences. Running it on a real network can disrupt hosts or trigger security controls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptests.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptests.c

## Purpose
Implementation of the `iptest` packet test suite.

## Main Elements
- `ip_test1()` tests malformed IP headers, length/header mismatches, version values, zero-length fragments, large fragment sets, odd offsets, and TTL values.
- `ip_test2()` tests malformed IP options and option lengths.
- `ip_test3()` sends ICMP type/code combinations and short ICMP packets.
- `ip_test4()` tests UDP length, port, and MTU edge cases.
- `ip_test5()` tests TCP flags, sequence/ack/window/urgent/data-offset/port cases, and LAND-style packets.
- `ip_test6()` sends repeated fragmented UDP sequences to stress mbuf/reassembly behavior.
- `ip_test7()` sends random IP packets with destination fixed to the target.

## Dependencies And Integration
Uses `initdevice()`, `send_ip()`, `send_ether()`, `send_icmp()`, `send_udp()`, `send_tcp()`, `find_tcp()`, and kernel memory helpers from `sock.c`.

## Risk Notes
This file intentionally generates malformed traffic and stress patterns. Several tests depend on kernel TCP structure access and are disabled on some platforms.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/iptests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/resend.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/resend.c

## Purpose
Replay engine for `ipresend`.

## Main Elements
- `dumppacket()` prints concise IP/TCP/UDP packet details.
- `ip_resend()` opens an input reader, reads packets into `mb_t`, wraps IP packets in Ethernet headers unless raw replay is requested, recomputes missing IP checksums, and writes frames with `sendip()`.

## Dependencies And Integration
Uses `struct ipread` reader callbacks, `arp()`, `chksum()`, `initdevice()`, and `sendip()`.

## Risk Notes
When no gateway is supplied, the ARP lookup path uses `gwip` even though it is zero, suggesting fragile legacy behavior. Replay can send arbitrary captured traffic.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/resend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sbpf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sbpf.c

## Purpose
BPF backend for opening an interface and writing raw packets.

## Main Elements
- `initdevice()` opens `/dev/bpf*`, checks BPF version, binds to an interface, obtains buffer size, allocates buffer storage, sets read timeout, and flushes the descriptor.
- `sendip()` writes a complete packet/frame to the BPF descriptor.

## Dependencies And Integration
Used by BSD BPF builds of `ipsend` and FreeBSD `ipresend`. Includes BPF and network headers.

## Risk Notes
Requires BPF device access and root-like privileges. The allocated read buffer is not used by the send path.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sbpf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sdlpi.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sdlpi.c

## Purpose
DLPI backend for sending raw packets through STREAMS devices.

## Main Elements
- `initdevice()` derives DLPI device name/PPA from interface string, opens it, attaches, optionally enables promiscuous SAP mode, binds to IP, and requests raw DLPI mode when available.
- `sendip()` sends packet data with `putmsg()`, using HP raw-data control messages when needed.

## Dependencies And Integration
Uses `dlcommon.c` helper functions and DLPI/STREAMS APIs.

## Risk Notes
Highly platform-specific to Solaris/HP-UX DLPI behavior. Device-name parsing assumes trailing numeric PPA.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sdlpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/snit.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/snit.c

## Purpose
SunOS NIT backend for raw packet output.

## Main Elements
- `initdevice()` opens `/dev/nit`, pushes `nbuf`, sets timeout, and binds to an interface.
- `sendip()` sends packets through STREAMS `putmsg()` with an `AF_UNSPEC` sockaddr control message and flushes writes.

## Dependencies And Integration
Used by SunOS NIT build targets in the portable makefile.

## Risk Notes
Obsolete platform backend. It expects Ethernet-sized link headers and old NIT STREAMS APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/snit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sock.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sock.c

## Purpose
Kernel-memory and TCP socket helper support for packet tests.

## Main Elements
- `kmemcpy()` reads kernel memory from `/dev/kmem`.
- `getproc()` uses `sysctl()` to locate the current process.
- `find_tcp()` follows file descriptor, file, socket, PCB, and TCP control block pointers to locate a kernel `tcpcb`.
- `do_socket()` opens a nonblocking TCP socket, binds source address, locates TCP state, connects, sends a crafted TCP packet, and writes test data.

## Dependencies And Integration
Used by `iptests.c` TCP tests and optionally by `ipsend.c` when `DOSOCKET` is enabled.

## Risk Notes
Very sensitive to kernel private structure layout and requires kernel memory access. It is inherently non-portable across kernel versions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sockraw.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sockraw.c

## Purpose
Raw IPv4 socket backend for packet output.

## Main Elements
- `initdevice()` opens `SOCK_RAW/IPPROTO_RAW`, queries interface address, and binds the socket.
- `sendip()` strips the Ethernet header and sends the IP packet with `sendto()`.

## Dependencies And Integration
Alternative sender backend for platforms where link-layer raw output is unavailable.

## Risk Notes
File warns that using it on HP-UX 11.00 can crash the system. It ignores Ethernet details and relies on raw socket semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sockraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/Makefile

## Purpose
FreeBSD build file for the internal `libipf` library.

## Main Elements
- Builds many parser, loader, printer, protocol, lookup, NAT, kernel-memory, logging, and utility source files into an internal library.
- Links with `kvm` through `LIBADD`.
- Uses `INTERNALLIB=` and `<bsd.lib.mk>`.

## Dependencies And Integration
Shared by IPFilter userland tools including `ipf`, `ipnat`, `ippool`, `ipfstat`, and related utilities.

## Risk Notes
The library centralizes many global parser/printing helpers; changes here can affect several tools at once.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addicmp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addicmp.c

## Purpose
Defines a legacy array of ICMP type names indexed by type value.

## Main Elements
- `icmptypes[]` contains common IPv4 ICMP names such as `echorep`, `unreach`, `redir`, `echo`, `timex`, and `maskrep`.

## Dependencies And Integration
Included in `libipf` for parsers/printers that use the older ICMP-name array.

## Risk Notes
Sparse entries are represented as null pointers; callers must handle missing names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addicmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addipopt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addipopt.c

## Purpose
Adds one IPv4 option to an option buffer for IPFilter tools.

## Main Elements
- Enforces a 48-byte maximum option area.
- Emits option value, length, and pointer fields.
- Handles security level, RR/TS length, LSRR/SSRR address, and SATID value payloads.
- Debug-prints option metadata when `OPT_DEBUG` is enabled.

## Dependencies And Integration
Called by `buildopts()` and uses option-name tables from libipf.

## Risk Notes
Mutates a raw caller-provided buffer and expects valid option metadata. Input class strings are parsed narrowly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addipopt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_free.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_free.c

## Purpose
Frees an `alist_t` linked list.

## Main Elements
- Iterates `al_next` and frees each node.

## Dependencies And Integration
Used by URL/file/host list loaders and `ippool_y.y`.

## Risk Notes
Only frees the list nodes, which is correct for the current `alist_t` layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_free.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_new.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_new.c

## Purpose
Parses one host/network string into an `alist_t` address-list node.

## Main Elements
- Infers IPv4 versus IPv6 when family is unspecified.
- Supports leading `!` negation and `/prefix` masks.
- Handles classful IPv4 shorthand when no explicit prefix is supplied.
- Calls `gethost()` to resolve the address and stores family, address, mask, and negation.

## Dependencies And Integration
Used by file/URL loaders that convert textual address lists into pool/hash entries.

## Risk Notes
Temporarily overwrites `/` with NUL while parsing, then restores it. Invalid family, prefix, or hostname frees the node and returns null.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/alist_new.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/allocmbt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/allocmbt.c

## Purpose
Allocates and initializes an `mb_t` message buffer wrapper.

## Main Elements
- Allocates `sizeof(mb_t)`.
- Sets length, clears next pointer, and points `mb_data` at embedded `mb_buf`.

## Dependencies And Integration
Used by packet reader/writer utilities in libipf.

## Risk Notes
The `len` argument is recorded but not used to size allocation because `mb_t` has a fixed embedded buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/allocmbt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/assigndefined.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/assigndefined.c

## Purpose
Imports semicolon-separated predefined parser variables from an environment string.

## Main Elements
- Splits on `;`.
- For each `name=value`, temporarily terminates the name, calls `set_variable()`, then restores `=`.

## Dependencies And Integration
Used by `ippool.c` with `IPPOOL_PREDEFINED` and shared parser variable support.

## Risk Notes
Mutates the input environment string in place, which assumes the runtime permits modifying the buffer returned by `getenv()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/assigndefined.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/bcopywrap.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/bcopywrap.c

## Purpose
Adapter that exposes `bcopy()` through a copy-function signature returning status.

## Main Elements
- `bcopywrap()` copies `size` bytes and returns `0`.

## Dependencies And Integration
Used where code accepts a kernel/user copy callback.

## Risk Notes
No error path exists because plain memory copying cannot report failure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/bcopywrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/binprint.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/binprint.c

## Purpose
Debug helper for printing binary structures as hex bytes.

## Main Elements
- Prints bytes in rows of 16 and flushes stdout.

## Dependencies And Integration
Used by verbose/debug code paths such as NAT rule loading.

## Risk Notes
No bounds checks beyond the supplied size; caller controls the memory span.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/binprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/buildopts.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/buildopts.c

## Purpose
Builds an IPv4 option byte buffer from comma-separated option names.

## Main Elements
- Parses optional `name=value` arguments.
- Prevents duplicate option types through a bitmask.
- Calls `addipopt()` for recognized options.
- Pads with NOPs and terminates with EOL.

## Dependencies And Integration
Used by IPFilter tools that accept textual IP option specifications.

## Risk Notes
Uses `strtok()` and mutates the option string. Unknown option names abort option building.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/buildopts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/checkrev.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/checkrev.c

## Purpose
Checks that the userland IPFilter version matches the kernel IPFilter version.

## Main Elements
- Opens the IPFilter device once.
- Issues `SIOCGETFS` for `friostat`.
- Compares `IPL_VERSION` with the kernel-reported version string.

## Dependencies And Integration
Uses `ipfobj_t`, `IPFILTER_VERSION`, `IPFOBJ_IPFSTAT`, and `ipferror()`.

## Risk Notes
Caches the device fd statically. Any ioctl or version mismatch returns failure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/checkrev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/connecttcp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/connecttcp.c

## Purpose
Opens a TCP connection to a named or numeric IPv4 server.

## Main Elements
- Parses numeric addresses with `inet_aton()` or resolves names with `gethostbyname()`.
- Creates an IPv4 stream socket and connects to the requested port.
- Returns the connected fd or `-1`.

## Dependencies And Integration
Used by URL/HTTP loading helpers.

## Risk Notes
IPv4-only and blocking. Closes the socket on connect failure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/connecttcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count4bits.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count4bits.c

## Purpose
Counts contiguous leading one bits in an IPv4 netmask.

## Main Elements
- Converts mask from network to host order.
- Counts leading one bits.
- Reconstructs the canonical mask and returns `-1` if the input is non-contiguous.

## Dependencies And Integration
Used by parsers and printers that validate or format IPv4 masks.

## Risk Notes
Only accepts canonical contiguous masks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count4bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count6bits.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count6bits.c

## Purpose
Counts leading one bits in an IPv6 mask represented as four 32-bit words.

## Main Elements
- Scans mask words and accumulates full 32-bit words plus leading bits in the first partial word.

## Dependencies And Integration
Used by NAT/address parsers for IPv6 prefix checks.

## Risk Notes
Does not explicitly reject non-contiguous bits after the first zero; callers needing strict validation must enforce it.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/count6bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/debug.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/debug.c

## Purpose
Debug logging helpers for libipf.

## Main Elements
- Global `debuglevel`.
- `debug()` prints to stderr when requested level is enabled.
- `ipfkdebug()` routes messages through `debug()` when `OPT_DEBUG` is set.

## Dependencies And Integration
Uses global `opts` from IPFilter tools.

## Risk Notes
`ipfkdebug()` passes a `va_list` as a single argument to `debug()` rather than using `vfprintf()` directly, which makes it questionable for formatted messages.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/dupmbt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/dupmbt.c

## Purpose
Duplicates an `mb_t` buffer object.

## Main Elements
- Allocates a new `mb_t`.
- Copies length and data payload.
- Preserves `mb_data` offset relative to the embedded buffer.

## Dependencies And Integration
Used by packet buffer processing helpers.

## Risk Notes
Assumes `orig->mb_data` points within `orig->mb_buf`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/dupmbt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.c

## Purpose
Maps syslog facility and priority names to numeric values and back.

## Main Elements
- Facility table covers standard and conditional syslog facilities.
- `fac_toname()` and `fac_findname()` convert facilities.
- Priority table covers emerg through debug.
- `pri_toname()` and `pri_findname()` convert priorities.

## Dependencies And Integration
Used by logging configuration/parsing code.

## Risk Notes
Facility handling has portability branches for systems with different `LOG_CRON` values and optional facility macros.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.h

## Purpose
Header for syslog facility/priority conversion helpers.

## Main Elements
- Declares facility and priority conversion functions.
- Normalizes `LOG_CRON1` and `LOG_CRON2` depending on platform value.

## Dependencies And Integration
Included by `facpri.c` and logging parsers.

## Risk Notes
Assumes `LOG_CRON` is defined before the header’s conditional macros are evaluated.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/facpri.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/familyname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/familyname.c

## Purpose
Formats an address family as a short string.

## Main Elements
- Returns `inet` for `AF_INET`.
- Returns `inet6` for `AF_INET6` when IPv6 support is enabled.
- Returns `unknown` otherwise.

## Dependencies And Integration
Used by printers and diagnostics.

## Risk Notes
IPv6 output depends on compile-time `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/familyname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/fill6bits.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/fill6bits.c

## Purpose
Builds an IPv6 prefix mask from a prefix length.

## Main Elements
- Handles `/0` and `/128` directly.
- Fills four 32-bit words and shifts the partial word for prefix lengths in each 32-bit range.

## Dependencies And Integration
Used by `alist_new()` and parser mask handling.

## Risk Notes
Does not validate out-of-range bit counts; callers are expected to check.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/fill6bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/findword.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/findword.c

## Purpose
Looks up a lexer/parser word in a `wordtab_t` table.

## Main Elements
- Linear search by exact string match.
- Returns null when no word matches.

## Dependencies And Integration
Used by shared lexer/parser dictionaries.

## Risk Notes
Case-sensitive and requires a null-terminated word table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/findword.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/flags.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/flags.c

## Purpose
Defines shared TCP flag name/value tables.

## Main Elements
- Provides fallback constants for ECN, CWR, and AE flags.
- `flagset[]` maps printable flag characters.
- `flags[]` maps corresponding TCP flag bit values.

## Dependencies And Integration
Used by TCP flag parsers and printers.

## Risk Notes
The table includes newer/extended flags but depends on local TCP header bit definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/flags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/freembt.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/freembt.c

## Purpose
Frees an `mb_t` buffer object.

## Main Elements
- Calls `free()` on the supplied pointer.

## Dependencies And Integration
Pairs with `allocmbt()` and `dupmbt()`.

## Risk Notes
No null or chain traversal handling; callers must pass a single allocated node.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/freembt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ftov.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ftov.c

## Purpose
Converts socket address families to IP version numbers.

## Main Elements
- `AF_INET` maps to `4`.
- `AF_INET6` maps to `6` when enabled.
- `AF_UNSPEC` maps to `0`; unknown families map to `-1`.

## Dependencies And Integration
Used heavily by NAT and pool parsers.

## Risk Notes
IPv6 mapping is compile-time conditional.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ftov.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/gethost.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/gethost.c

## Purpose
Resolves a host or network name into an `i6addr_t`.

## Main Elements
- Special-cases `test.host.dots` and `<thishost>`.
- For IPv4, tries `gethostbyname()` and then `getnetbyname()`.
- For IPv6, uses `getaddrinfo()` when enabled.
- Clears the output address before resolution.

## Dependencies And Integration
Used by parsers for NAT, pools, and address lists.

## Risk Notes
IPv4 resolution uses legacy non-reentrant resolver APIs. IPv6 path assumes `res` is valid after `getaddrinfo()` without checking the return code first.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/gethost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/geticmptype.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/geticmptype.c

## Purpose
Maps an ICMP type name to the numeric type for an address family.

## Main Elements
- Searches `icmptypelist`.
- Returns IPv4 or IPv6 type value by family.
- Returns `-1` for unknown names or unsupported family.

## Dependencies And Integration
Uses the table from `icmptypes.c`.

## Risk Notes
IPv6 support depends on `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/geticmptype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getifname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getifname.c

## Purpose
Reads a kernel `ifnet` pointer and returns an interface name string.

## Main Elements
- Handles null and sentinel pointer values.
- On Solaris, reads `qif_t` and duplicates `qf_name`.
- On BSD-like systems, reads `struct ifnet` and duplicates `if_xname`.

## Dependencies And Integration
Uses `kmemcpy()` from `kmem.h` and is used by live/dead kernel printers.

## Risk Notes
Depends on kernel memory access and private interface structure layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getifname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getnattype.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getnattype.c

## Purpose
Formats a NAT entry redirection type as a string.

## Main Elements
- Maps `NAT_MAP`, `NAT_MAPBLK`, `NAT_REDIRECT`, `NAT_REWRITE`, `NAT_BIMAP`, `NAT_DIVERTUDP`, and `NAT_ENCAP` combinations.
- Returns `unknown(...)` for unrecognized bit patterns.

## Dependencies And Integration
Used by NAT state/printer code.

## Risk Notes
Uses a static buffer for unknown values, so return value is overwritten on the next unknown conversion.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getnattype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getport.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getport.c

## Purpose
Resolves a service name or numeric string to a network-order port.

## Main Elements
- Without a filter rule context, uses `getservbyname()` and numeric parsing.
- With IPFilter rule context, considers rule protocol, `tcp/udp` combined semantics, and protocol-specific service names.
- Validates numeric port range.

## Dependencies And Integration
Used by filter and NAT parsers.

## Risk Notes
Service names can be ambiguous without protocol; the function rejects mismatched TCP/UDP mappings in combined cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getportproto.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getportproto.c

## Purpose
Resolves a port string for a specific IP protocol number.

## Main Elements
- Accepts all-digit numeric ports after validating every character and range.
- Resolves service names using the protocol name from `getprotobynumber()`.

## Dependencies And Integration
Used by NAT proxy grammar for service-name ports.

## Risk Notes
Returns network-order port values or `-1`, so callers must not treat the return as an unsigned port without checking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getportproto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getproto.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getproto.c

## Purpose
Converts a protocol string to an IP protocol number.

## Main Elements
- Numeric strings return `atoi()`.
- `ip` maps to protocol `0`.
- Other names resolve through `getprotobyname()`.

## Dependencies And Integration
Used by NAT and filter parsers.

## Risk Notes
Numeric values are not range-checked here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getproto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getsumd.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getsumd.c

## Purpose
Formats a checksum/status word for display.

## Main Elements
- Detects `NAT_HW_CKSUM` and formats hardware checksum values as `hw(...)`.
- Otherwise prints the raw hex value.

## Dependencies And Integration
Used by NAT/state printers.

## Risk Notes
Returns a static buffer overwritten by subsequent calls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getsumd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/hostname.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/hostname.c

## Purpose
Formats an IPv4 or IPv6 address as a hostname or numeric address.

## Main Elements
- Special-cases the test IPv4 address `0xfedcba98`.
- Unless `OPT_NORESOLVE` is set, tries reverse host and network lookup for IPv4.
- Falls back to `inet_ntoa()` for IPv4 or `inet_ntop()` for IPv6.

## Dependencies And Integration
Used by printers throughout IPFilter tools.

## Risk Notes
Uses static storage and legacy resolver APIs. IPv6 output is unavailable without `USE_INET6`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/hostname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmpcode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmpcode.c

## Purpose
Defines names for IPv4 ICMP unreachable/error codes.

## Main Elements
- `icmpcodes[]` maps codes to strings such as `net-unr`, `host-unr`, `proto-unr`, `port-unr`, `needfrag`, and prohibition/preference codes.

## Dependencies And Integration
Used by ICMP parsers/printers.

## Risk Notes
Only covers the fixed table up to `MAX_ICMPCODE`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmpcode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypename.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypename.c

## Purpose
Maps an ICMP type number to a canonical type name.

## Main Elements
- Rejects values outside `0..255`.
- Searches `icmptypelist` for matching IPv4 or IPv6 type by family.

## Dependencies And Integration
Uses `icmptypelist` from `icmptypes.c`.

## Risk Notes
Returns null for unmapped or unsupported values.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypes.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypes.c

## Purpose
Defines the shared ICMP/ICMPv6 type-name table.

## Main Elements
- Provides fallback zero definitions for ICMPv6 constants when IPv6 is disabled.
- Normalizes missing MLD names on IPv6 builds.
- `icmptypelist[]` maps names to IPv4 and IPv6 type numbers, including echo, unreach, redirect, router, neighbor, MLD, and query/reply types.

## Dependencies And Integration
Used by `geticmptype()` and `icmptypename()`.

## Risk Notes
When IPv6 is disabled, IPv6-only constants collapse to zero or `-1`, so callers must respect family checks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/inet_addr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/inet_addr.c

## Purpose
Compatibility implementation of `inet_aton()` for systems without a reliable local version.

## Main Elements
- Parses decimal, octal, and hex IPv4 numeric components.
- Supports one-, two-, three-, and four-part historical IPv4 formats.
- Validates trailing characters and component ranges.
- Stores network-order address in `struct in_addr`.

## Dependencies And Integration
Used by portable IPFilter code paths and older platform builds.

## Risk Notes
This is legacy BSD-derived compatibility code. The old `inet_addr()` wrapper is present but compiled out.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/inet_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/initparse.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/initparse.c

## Purpose
Initializes parser-global hostname state.

## Main Elements
- Defines `thishost`.
- `initparse()` calls `gethostname()` and NUL-terminates the buffer.

## Dependencies And Integration
Used by parsers and `gethost()` for the `<thishost>` token.

## Risk Notes
Stores hostname in a global fixed-size buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/libipf/initparse.c -->