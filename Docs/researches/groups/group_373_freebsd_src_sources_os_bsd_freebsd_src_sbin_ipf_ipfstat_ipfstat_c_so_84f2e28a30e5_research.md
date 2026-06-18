# Group Research: group_373_freebsd_src_sources_os_bsd_freebsd_src_sbin_ipf_ipfstat_ipfstat_c_so_84f2e28a30e5

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/ipfstat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/ipfstat.c

`ipfstat.c` implements the IPFilter status and inspection command. It opens the filter, state, auth, and NAT device nodes for live inspection, or switches to crash-dump/kernel-memory mode with `-M`/`-N`. It verifies user/kernel version compatibility, drops elevated privileges after opening privileged resources, and retrieves `friostat_t`, `ips_stat_t`, `ipfrstat_t`, and `ipf_authstat_t` through ioctls or symbol-table/kmem copies.

Major behaviors:
- Prints global filter counters, packet log flags, block reasons, fastroute counters, pullup/coalesce/checksum counters, and IPv4/IPv6 packet totals.
- Lists active/inactive filter and accounting rules, including hits, bytes, line numbers, nested groups, callfunc rules, and optional binary debug dumps.
- Lists or summarizes state table entries, including custom field output via `parsefields`, expression filtering via `parseipfexpr`, and bucket distribution statistics.
- Shows fragment cache entries for filter and NAT fragment tables.
- Shows auth queue statistics and pending auth entries.
- Shows configured filter/accounting/auth groups.
- When compiled with `STATETOP`, provides a curses top-like live state view with source/destination/protocol/port filters, sorting by protocol/packets/bytes/TTL/source/destination, reverse ordering, refresh interval, resize handling, and closed-TCP suppression.

Notable implementation details:
- Live iteration uses `SIOCGENITER`, `SIOCIPFITER`, `SIOCIPFDELTOK`, `SIOCGTABL`, and related object wrappers (`ipfobj_t`, `ipfgeniter_t`).
- Dead-kernel support depends on hard-coded symbol names such as `frstats`, `ips_stats`, `ipfr_stats`, `ipf_rules`, `ipf_acct`, and `ipf_state_logging`.
- `state_matcharray()` evaluates parsed filter expressions against `ipstate_t` fields for protocol, IPv4/IPv6 addresses, TCP/UDP ports, idle time, and TCP states.
- Several code paths are diagnostic and trust kernel/core structures heavily; failures usually print and exit or silently stop iteration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/ipfstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipfsyncd.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipfsyncd.c

`ipfsyncd.c` is the daemon form of the IPFilter sync bridge. It relays synchronization records between the kernel sync device (`IPSYNC_NAME`) and a UDP peer or multicast group.

Major behaviors:
- Parses `-I interface`, `-i address`, `-p port`, and `-d` debug options.
- Defaults to UDP port `0xaf6c` and multicast group `INADDR_UNSPEC_GROUP | 0x697066`.
- Daemonizes when debug is disabled, installs termination handlers, and reconnects/reopens resources with exponential backoff.
- Builds sockets bound to a named interface, including multicast setup through IGMP raw socket, `IP_MULTICAST_IF`, `IP_MULTICAST_LOOP=0`, `IP_MULTICAST_TTL=63`, and `IP_ADD_MEMBERSHIP`.
- Uses `select()` to multiplex the kernel sync device and UDP socket.

Data handling:
- Kernel-to-network path reads buffered sync records, validates `SYNHDRMAGIC`, handles incomplete records with a retained buffer, and sends complete records over UDP.
- Network-to-kernel path receives UDP datagrams, validates sync headers, and writes complete records to `IPSYNC_NAME`.
- Debug helpers print sync header fields, command names (`SMC_CREATE`, `SMC_UPDATE`), table names (`SMC_NAT`, `SMC_STATE`), and TCP update state/age data.

Risks and quirks:
- Uses fixed 1400-byte buffers and manual record framing.
- Error recovery generally tears down fds and retries.
- `do_kbuff()` has fragile buffer accounting and copies leftover bytes manually.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipfsyncd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncm.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncm.c

`ipsyncm.c` is a simple one-way IPFilter sync sender. It reads records from `IPSYNC_NAME` and writes them to a connected UDP destination.

Major behaviors:
- Usage is `<destination IP> <destination port>`, defaulting to port `43434`.
- Opens the sync device read-only, creates a UDP socket, connects to the destination, and loops forever with one-second retry sleeps.
- Accumulates reads into a 1400-byte buffer, validates `SYNHDRMAGIC`, waits for complete sync records, then writes the framed record to the UDP socket.
- Has always-on `IPSYNC_DEBUG` printing for header fields, command/table names, sequence number, and TCP update state.

Notes:
- Signal handling code exists but is compiled out with `#if 0`, so normal termination is external process termination.
- Partial reads are handled by moving remaining bytes to the front of the buffer.
- This is more of a debug/legacy utility than the robust daemon in `ipfsyncd.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncs.c

`ipsyncs.c` is the receiving counterpart to `ipsyncm.c`. It listens on UDP and writes received sync records into `IPSYNC_NAME`.

Major behaviors:
- Usage is `<destination IP> <destination port> [remote IP]`, defaulting to port `43434`.
- Opens `IPSYNC_NAME` write-only, binds a UDP socket with `SO_REUSEADDR`, and loops forever with one-second retry sleeps.
- Reads UDP data into a 1400-byte buffer, validates `SYNHDRMAGIC`, waits for complete records, then writes them to the sync device.
- Prints debug information for command/table/type/sequence and TCP update data.

Important note:
- The source explicitly comments that it does not check the datagram source address, calling this a possible security risk. The optional `remote IP` argument is parsed into `in.sin_addr`, but not actually used for validation in the receive loop.

Like `ipsyncm.c`, signal handling is disabled under `#if 0`, and the code appears intended for testing or simple deployments rather than hardened operation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/Makefile

This Makefile builds the `ipftest` program in the FreeBSD IPFilter userland tree.

Key points:
- `PROG=ipftest`, `PACKAGE=ipf`, manual page `ipftest.1`.
- Sources combine local test harness files (`ipftest.c`, `ip_fil.c`, `md5.c`) with many kernel IPFilter implementation files from `${SRCTOP}/sys/netpfil/ipfilter/netinet`.
- Enables `IPFILTER_LOG`, `IPFILTER_COMPILED`, `IPFILTER_LOOKUP`, `IPFILTER_SYNC`, `IPFILTER_CKSUM`, and `HAS_SYS_MD5_H`.
- Explicitly does not enable `IPFILTER_SCAN`; comments say the original tarball did not define it and it is believed to fail building.
- Generates renamed parser/lexer files for IPF, IPNAT, and IPPOOL grammars by running yacc and sed-rewriting `yy` prefixes to `ipf_yy`, `ipnat_yy`, and `ippool_yy`.

The build design lets `ipftest` link large portions of the kernel packet filter/NAT/state/lookup code into a user-space executable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ip_fil.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ip_fil.c

`ip_fil.c` supplies user-space kernel compatibility hooks for `ipftest`. It lets kernel IPFilter modules run in a test harness without real kernel networking.

Major behaviors:
- Defines the global `ipfmain` softc.
- Provides trivial `ipfattach()`/`ipfdetach()`.
- Routes ioctl handling through `ipf_ioctlswitch()` with the current UID.
- Maintains synthetic `ifnet` objects in an expandable array, parses names with optional `=address`, initializes address lists, and resolves interface names.
- Provides fake interface output functions: `no_output()` discards packets, while `write_output()` appends packet bytes to `/tmp/<ifname>` for saved outbound traffic.
- Implements `ipf_fastroute()` by selecting a destination/interface, running accounting/state/NAT checkout, printing the packet, and calling the synthetic interface output callback.
- Provides test versions of reset/ICMP error sending, mbuf free/copy, uio read movement, interface address lookup, source verification, packet injection, pullup, pseudo checksums, pseudo random values, and IP ID/ISS generation.

Notable details:
- `ipf_newisn()` uses the bundled MD5 implementation over flow tuple data plus a monotonic offset, with the secret update commented out.
- `ipf_random()` deliberately returns boundary-case values for early calls to exercise test ranges.
- `ipf_pullup()` intentionally fails when the requested length exceeds current mbuf length, setting `FRB_PULLUP`.
- There is a suspicious syntax fragment in `ipf_fastroute()` as read: `return (0; /* no routing table out here */);`, which looks malformed unless hidden by build conditions or historical source context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ip_fil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ipftest.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ipftest.c

`ipftest.c` is the main offline packet-filter test runner. It loads IPFilter/NAT/pool rules into a user-space IPFilter instance, reads packets from text/hex/pcap inputs, runs them through `ipf_check()`, and prints the resulting action and packet details.

Major behaviors:
- Initializes parser state, loads all IPFilter modules, creates and initializes all softc state, and enables filtering through the local ioctl path.
- Accepts input formats through `-F pcap|hex|text`; defaults to text.
- Loads filter rules with `-r`, NAT rules with `-N`, pools with `-P`, and tuning with `-T`.
- Supports IPv6 selection, checksum fixing, debug/verbose/hex/brief modes, output interface saving, source-direction override, binary log draining, and final dump output.
- For each packet, determines interface and direction, optionally fixes checksums, calls `ipf_check()`, prints pass/block/auth/account/nomatch/bad-packet style results, then flushes transient state and writes outbound packets when requested.
- Cleans up softc, modules, mutexes/rwlocks, and optionally aborts under `FINDLEAKS`.

Local ioctl adapters:
- `ipftestioctl`, `ipnattestioctl`, `ipstatetestioctl`, `ipauthtestioctl`, `ipscantestioctl`, `ipsynctestioctl`, and `ipooltestioctl` forward ioctl calls to the in-process softc using the correct IPL log unit.
- `kmemcpy()` and `kstrncpy()` are direct user-space memory copies for code paths expecting kernel-memory access.

Diagnostics:
- `dumpnat()` prints configured NAT rules, active sessions, proxy activity, and hostmaps.
- `dumpgroups()` and `dumprules()` print configured groups and rule lists.
- `drain_log()` drains all IPFilter logs into a file.
- `fixv4sums()` recomputes IPv4 and L4 checksums for TCP/UDP/ICMP.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/ipftest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.c

`md5.c` is the RSA Data Security, Inc. reference MD5 implementation bundled for the IPFilter test harness.

Contents:
- Standard MD5 context initialization (`MD5Init`).
- Incremental update logic (`MD5Update`) with 64-byte block processing and bit count tracking.
- Final padding, length append, digest serialization, and output copy (`MD5Final`).
- The four MD5 round functions/macros and a private `Transform()` routine with the standard constants and rotations.
- Kernel/user include split: includes `<sys/systm.h>` under `_KERNEL`, otherwise `<string.h>`.

Use in this group:
- `ipftest/ip_fil.c` uses this implementation to compute pseudo TCP initial sequence numbers for user-space test behavior.
- `md5.h` gates definitions to avoid conflicts with system MD5 headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.h

`md5.h` declares the bundled RSA MD5 interface.

Key contents:
- License and provenance text for the RSA Data Security MD5 Message-Digest Algorithm.
- Include guard conditional on both `__MD5_INCLUDE__` and `_SYS_MD5_H`, preventing conflict with a system MD5 header.
- Defines `UINT4` as `unsigned int`.
- Defines `MD5_CTX` with bit counters, four-word buffer, 64-byte input buffer, and 16-byte digest.
- Declares `MD5Init`, `MD5Update`, and `MD5Final`.

This header is only support infrastructure for the local MD5 implementation used by the IPFilter test harness.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/Makefile

This is a standalone, older-style Makefile for building the `iplang` parser objects rather than a normal FreeBSD `bsd.prog.mk` program Makefile.

Key points:
- Builds `iplang_y.o` and `iplang_l.o`, optionally under `$(DESTDIR)`.
- Generates `iplang_l.c` from `iplang_l.l` with `lex`.
- Generates `iplang_y.c` and `iplang_y.h` from `iplang_y.y` with `yacc -d`.
- Uses include paths for current directory, parent directory, destination directory, and `../ipsend`.
- `clean` removes objects and generated lex/yacc files.

This appears to support the IP packet language used by the `ipsend` family rather than installing a top-level FreeBSD program directly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang.h

`iplang.h` defines data structures shared by the IP language lexer/parser.

Key structures:
- `iface_t`: named interface with MTU, IPv4 address, Ethernet address, next pointer, and opened device fd.
- `send_t`: selected interface plus gateway address for sending.
- `arp_t`: IPv4-to-Ethernet ARP mapping list entry.
- `aniphdr_t`: linked nested header descriptor used while building packets. It stores a union pointer to IP/data/TCP/UDP/ICMP data, option length, last option, protocol, header length, and next/previous links.

It also defines convenience aliases (`ah_ip`, `ah_data`, `ah_tcp`, `ah_udp`, `ah_icmp`) and declares `get_arpipv4()`.

This header is the structural backbone for `iplang_y.y` packet construction.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_l.l -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_l.l

`iplang_l.l` is the lex scanner for the IP packet description language.

Major behaviors:
- Recognizes whitespace, newlines, braces, semicolons, decimal numbers, single hex digits, colons, comments, quoted strings, and generic tokens.
- Maintains line number, token count, current protocol block (`ipproto`), previous protocol, and a stack for nested protocol contexts.
- Contains a keyword table mapping words such as `interface`, `ipv4`, `tcp`, `udp`, `icmp`, `data`, `send`, IP options, TCP options, security classes, and ICMP type/code names to parser tokens.
- Uses `next_state()` to disambiguate context-sensitive keywords:
  - `sum` becomes IPv4/TCP/UDP checksum token depending on current protocol.
  - `opt` becomes IPv4 or TCP option token.
  - `off` and `len` become protocol-specific fields.
  - `nop`, `eol`, and `ts` are remapped for TCP options inside TCP context.
- `push_proto()`/`pop_proto()` preserve nested protocol context across `{}`.
- `save_token()` duplicates raw token text into `yylval.str`.
- `swallow()` skips full-line comments after newlines.

Errors are fatal through `yyerror()`, which prints the offending text and 1-based line number.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_l.l -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_y.y

`iplang_y.y` is the yacc grammar and semantic implementation for constructing and sending synthetic IPv4 packets from a textual packet language.

Grammar coverage:
- Top-level `interface`, `arp`, `router`, `send`, and `ipv4` statements.
- Interface attributes: name, MTU, Ethernet address, IPv4 address.
- Send attributes: interface and gateway (`via`).
- ARP entries mapping IPv4 addresses to Ethernet addresses.
- IPv4 fields: protocol, source/destination, offset, version, header length, id, TTL, TOS, checksum, length, and options.
- Nested TCP, UDP, ICMP, and data bodies.
- TCP fields/options: source/destination ports, sequence, ack, offset, urgent pointer, window, checksum, flags, NOP/EOL/MSS/window-scale/timestamp options.
- UDP fields: source/destination ports, length, checksum.
- ICMP types/codes and type-specific payloads for echo, unreachable, redirect, time exceeded, timestamp, info, mask, and parameter problem cases.
- IPv4 options including route, timestamp, security, CIPSO, SATID, SSRR/LSRR, and related historical options.
- Data payloads by length, inline escaped value, or external file.

Implementation model:
- Uses a 66 KiB `ipbuffer` and a linked `aniphdr_t` stack to append nested headers/data.
- `new_header()` appends a header, points it into the current buffer, and grows enclosing IP/UDP lengths.
- `inc_anipheaders()` adjusts lengths for all enclosing headers.
- `end_ipv4`, `end_tcp`, `end_udp`, and `end_icmp` compute checksums and unwind the header stack.
- `packet_done()` optionally hex-dumps the built packet, calls `prep_packet()`, and frees header metadata.
- `prep_packet()` opens the selected device with `initdevice()` and sends with `send_ip()` using selected/default gateway logic.

Notable details and risks:
- Host/service lookups are done with `gethostbyname()`/`getservbyname()`.
- `set_datafile()` refuses packet data exceeding 65535 total bytes.
- TCP/UDP port setters use `"udp"` as the protocol string even on the TCP branch, which looks like a bug in service-name lookup.
- Many semantic errors print messages but continue rather than aborting, so malformed language input can still produce partially built packets.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/iplang/iplang_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/Makefile

This Makefile builds the `ipmon` log monitor.

Key points:
- `PROG=ipmon`, `PACKAGE=ipf`.
- Sources are generated headers plus `ipmon.c`, `ipmon_y.c`, and `ipmon_l.c`.
- Installs `ipmon.5` and `ipmon.8`, with `ipmon.conf.5` linked to `ipmon.5`.
- Adds `-DLOGFAC=LOG_LOCAL0 -I.` and suppresses `unused-but-set-variable` as an error.
- Generates parser and lexer sources by yacc/sed and sed-rewriting common lexer names from `yy` to `ipmon_yy`.

The program uses the shared lexer source with an IPMon-specific yacc grammar.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon.c

`ipmon.c` implements the IPFilter log monitor. It reads filter, NAT, and state log streams and writes formatted logs to stdout, files, binary logs, syslog, or configured action savers.

Major behaviors:
- Supports log source selection for filter (`IPL_NAME`), NAT (`IPNAT_NAME`), and state (`IPSTATE_NAME`) logs.
- Supports daemon mode, syslog mode, binary log output, tail mode for regular files, pidfile writing, log flushing, name resolution, numeric ports, body/header hex dumps, and config-driven actions.
- Initializes protocol and TCP/UDP service lookup tables from system databases.
- Reads from up to three log sources with `select()`, handling character devices and regular files differently.
- Handles SIGHUP by reopening output logs, reloading service/protocol tables, and reloading the config file.

Formatting:
- `print_ipflog()` formats filter log entries with timestamps, interface/group/rule, pass/block/log flags, IPv4/IPv6 addresses, ports, protocol, lengths, TCP flags/seq/ack/window in verbose mode, ICMP/ICMPv6 names, fragment info, state/frag/NAT/log/nattag markers, low TTL/out-of-window/bad/NAT/broadcast/multicast flags, and block reason text.
- `print_natlog()` formats NAT lifecycle events (`NEW`, `FLUSH`, `CLONE`, `EXPIRE`, `DESTROY`, `PURGE`) and NAT rule types (`MAP`, `RDR`, `BIMAP`, mapblock, rewrite, encap, divert), including packet/byte counts on expiry/flush.
- `print_statelog()` formats state lifecycle events (`NEW`, `CLONED`, `EXPIRE`, `CLOSE`, `FLUSH`, `INTERMEDIATE`, `REMOVE`, `KILLED`, `UNLOAD`) and forward/backward counters.
- `dumphex()` writes hex plus printable ASCII, to syslog or file.

Configuration interaction:
- When a config file is loaded, filter log lines are passed to `check_action()` from `ipmon_y.y`; matching configured actions can suppress the default output and instead execute saver callbacks.

Notable implementation details:
- Uses static sequence counters per log type to report missed entries.
- Uses a fixed global `line[2048]` formatting buffer with extensive `sprintf`/`strcpy` appends.
- The default-log selection condition repeats `config.logsrc[0].logtype` three times, which looks like a copy/paste bug meant to check all three sources.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon_y.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon_y.y

`ipmon_y.y` is the IPMon configuration grammar and action engine.

Grammar coverage:
- `match { ...; } do { ...; }` rules.
- Variable assignments with `set_variable()`.
- Dynamic action loading through `load_action <name> <path>`.
- Match predicates: direction, destination/source IPv4 CIDR, destination/source port, rate limits by seconds or packets, group, interface, protocol, result, rule, logtag, nattag, and log type (`ipf`, `nat`, `state`).
- Action list entries call named saver backends, optionally with one string argument.

Implementation model:
- Parses match options into temporary `opt_t` lists, then builds `ipmon_action_t`.
- Detects duplicate match comparator use within one rule using `macflags`.
- Maintains a global action list and saver list.
- Built-in savers are registered by `ipmon.c`; dynamic savers are loaded with `dlopen()` and required symbols named `<name>destroy`, `<name>parse`, `<name>print`, and `<name>store`, with optional `<name>dup` and `<name>match`.
- `check_action()` evaluates parsed actions against an IPF log record and formatted message, enforcing direction/type/every/dst/src/ports/group/interface/protocol/result/rule/logtag/nattag predicates, then invokes each matched saver callback.
- `load_config()` installs lexer keyword table, opens the config file, and repeatedly runs `yyparse()`.
- `unload_config()` destroys actions and unloads dynamically loaded saver modules.
- `dump_config()` and `print_action()` reconstruct configured rules for diagnostics.

Notable issues:
- The grammar sets `a->ac_rule = o->o_num`, but the rule parser assigns `o_num = YY_NUMBER` rather than `$3`; that appears to store the token code instead of the configured rule number.
- `type` printing compares `ac_type` against `IPL_LOGIPF`/`IPL_LOGSTATE`/`IPL_LOGNAT`, while parsing stores magic constants (`IPL_MAGIC`, `IPL_MAGIC_NAT`, `IPL_MAGIC_STATE`), so dump output may not match parsed type values.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon_y.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/Makefile

This Makefile builds the `ipnat` command.

Key points:
- `PROG=ipnat`, `PACKAGE=ipf`.
- Sources are generated headers plus `ipnat.c`, `ipnat_y.c`, and `ipnat_l.c`.
- Installs `ipnat.8`, `ipnat.4`, and `ipnat.5`, with `ipnat.conf.5` linked to `ipnat.5`.
- Adds `-I.` and suppresses `unused-but-set-variable` as an error.
- Generates yacc output from `ipnat_y.y`, then sed-rewrites `yy` symbols to `ipnat_yy`.
- Generates lexer output from shared `lexer.c`, sed-rewriting includes and symbols for IPNAT-specific names.

This is the FreeBSD build glue for NAT rule parsing and NAT table inspection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat.c

`ipnat.c` implements the IPFilter NAT administration command. It loads/removes NAT rules, flushes NAT mappings/rules, and prints NAT statistics, rules, sessions, and hostmaps.

Major behaviors:
- Parses options for clear/flush/debug/file/load/list/match/core/kernel/dry-run/field output/purge/remove/no-resolve/stat/verbose.
- Reads predefined variables from `IPNAT_PREDEFINED`.
- Opens `IPNAT_NAME`, verifies version compatibility, and fetches `natstat_t` through `SIOCGNATS`.
- Supports crash-dump/kernel mode via `openkmem()` and `nlist()` symbol extraction.
- Loads NAT rule files with `ipnat_parsefile(fd, ipnat_addrule, ioctl, file)`.
- Flushes active NAT sessions or NAT rule lists using `SIOCIPFFL`, or expression-matched flushing via `SIOCMATCHFLUSH`.
- Lists NAT rules and active sessions either from live iterators or dead-kernel memory.
- Prints NAT stats, inbound/outbound side counters, hash bucket efficiency/usage/min/max/average lengths, log counters, active counts, flush counters, hostmap counters, and rule counts.
- Verbose listing includes hostmap tables.

Expression filtering:
- `nat_matcharray()` evaluates parsed IPF expressions against `nat_t` objects for protocol, IPv4/IPv6 source/destination addresses, any/source/destination TCP/UDP ports, and negation.
- NAT address matching considers both original and translated source/destination endpoints.

Live/dead split:
- Live mode uses `SIOCGENITER` for NAT rules, NAT sessions, and hostmaps, deleting iterator tokens afterward.
- Dead mode copies `nat_table`, `nat_list`, `maptable`, sizes, and `nat_instances` via kmem symbols.

Notable detail:
- In dead-mode `dotable()`, the kmem copy source for bucket data uses `nsp->ns_nattab_sz` rather than a table pointer, which looks suspicious.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat.c -->