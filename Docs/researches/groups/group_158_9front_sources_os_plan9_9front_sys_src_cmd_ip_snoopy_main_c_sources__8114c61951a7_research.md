# Group Research: group_158_9front_sources_os_plan9_9front_sys_src_cmd_ip_snoopy_main_c_sources__8114c61951a7

Scope validated against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/main.c

This is the main driver for `snoopy`, the Plan 9 network sniffer. It parses CLI flags, selects the capture source, initializes protocol formatters, builds the generated protocol graph, compiles optional filter expressions, then either prints decoded packets or emits Plan 9 trace / pcap output.

Key behavior:
- Supports live capture from ether and ipifc snoop files, or trace replay with `-t`.
- Uses `Proto` objects from generated `protos.c/protos.h` and per-protocol `mux` tables to walk packet layers.
- Implements filter evaluation, graph path completion, protocol-specific filter compilation, and simple tree optimization.
- Handles pcap headers/records with nanosecond timestamps and Plan 9 trace format.
- Provides protocol/filter help via `-?`, piping long output through `/bin/mc`.

Research notes:
- `mkfile` generates `protos.h` and `protos.c` from the `PROTOS` list; `protos.h` is not checked in.
- Filter completion assumes protocol reachability from `root`; unreachable filters become fatal internal errors.
- `parseba()` accepts exactly 16 hex bytes, despite storage room for larger arrays.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ninep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ninep.c

This snoopy protocol module decodes 9P messages. It uses `convM2S()` from Plan 9 fcall support and `%F` formatting to render a packet as an `Fcall`.

Key behavior:
- Attempts to decode the full remaining payload as one 9P message.
- Rewrites embedded newlines in the formatted `Fcall` as backslashes so snoopy packet output remains one logical line.
- Falls back to `dump.seprint()` if conversion fails.
- Sets `m->pr = nil`, making 9P a terminal decoder.

Research notes:
- Registered as `Proto ninep`; muxed from TCP ports including 564 and several CPU/exportfs ports, and from UDP port 6346.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ninep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ospf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ospf.c

This snoopy module formats OSPF packets and several OSPF payload types. It defines OSPF packet headers, hello packets, database description packets, link-state advertisement headers, link-state update formats, and link-state acknowledgements.

Key behavior:
- Validates the 24-byte OSPF header and packet length before decoding.
- Prints version, type, router ID, area, checksum, and authentication description.
- Handles hello, database description, link-state update, and link-state ack packets specially.
- Dumps unknown or request payloads as hex, capped to 64 bytes.
- Terminal protocol: no filters or mux table.

Research notes:
- `ospfauth()` appears to switch on `ospf->type` rather than `autype`, so authentication text may be inaccurate.
- Link-state update decoding chooses the union interpretation from the first LSA type and does not deeply validate per-LSA lengths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ospf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp.c

This is the shared PPP snoopy implementation. It defines the top-level `ppp` decoder plus subprotocol `Proto` objects for IPCP, LCP, CCP, CHAP, and compressed PPP packets.

Key behavior:
- Parses optional PPP address/control bytes and one- or two-byte protocol IDs.
- Muxes PPP protocols to `ip`, VJ TCP placeholders, multilink, compressed packets, IPCP, CCP, PAP, LCP, LQM, and CHAP.
- Provides filters for PPP subprotocol selection.
- Formats LCP/IPCP/CCP configure options and termination/reset codes.
- Formats CHAP challenge/response/success/failure and compressed packet flags/count.

Research notes:
- Several `ppp_*.c` files are one-line placeholders because their `Proto` definitions live here.
- `seprintlcpopt()` lacks an explicit `break` after `Oquality`, causing fall-through to `Omagic`; this may be intentional display aggregation or a formatting bug.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ccp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ccp.c

This file is a placeholder containing only the comment that CCP support is implemented in `ppp.c`.

Research notes:
- It exists so the generated snoopy protocol list has a source file matching the `ppp_ccp` `Proto`.
- The actual `Proto ppp_ccp` decoder formats CCP configure/reset packets in `ppp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ccp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_chap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_chap.c

This file is a placeholder containing only the comment that CHAP support is implemented in `ppp.c`.

Research notes:
- It preserves one-file-per-protocol build shape for generated `protos.c`.
- The actual `Proto ppp_chap` decoder is in `ppp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_chap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_comp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_comp.c

This file is a placeholder containing only the comment that compressed PPP packet support is implemented in `ppp.c`.

Research notes:
- The actual `Proto ppp_comp` decoder in `ppp.c` prints compression flags, count, and a short data dump.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ipcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ipcp.c

This file is a placeholder containing only the comment that IPCP support is implemented in `ppp.c`.

Research notes:
- The actual IPCP option formatter in `ppp.c` recognizes deprecated address pairs, IP compression, address, DNS, and WINS options.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_ipcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_lcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_lcp.c

This file is a placeholder containing only the comment that LCP support is implemented in `ppp.c`.

Research notes:
- The actual LCP formatter in `ppp.c` handles configure, terminate, code/protocol reject, echo, and discard codes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ppp_lcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_disc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_disc.c

This snoopy module implements both PPPoE discovery and PPPoE session protocol objects. It parses the PPPoE fixed header and optionally demuxes session payloads to PPP.

Key behavior:
- Header fields: version/type byte, code, session ID, payload length.
- Filters support version (`v`), type (`t`), code (`c`), and session ID (`s`).
- `pppoe_disc` prints header fields and stops.
- `pppoe_sess` prints header fields then demuxes to `ppp`.
- A `BUG` comment notes discovery tag types are not fully printed.

Research notes:
- `p_compiledisc()` and `p_compilesess()` have commented-out mux compilation, so filters are field-only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_disc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_sess.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_sess.c

This file is a placeholder containing only the comment that PPPoE session support is implemented in `pppoe_disc.c`.

Research notes:
- The actual `Proto pppoe_sess` is declared in `pppoe_disc.c` and demuxes payloads to `ppp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_sess.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rarp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rarp.c

This file is a placeholder containing only the comment that RARP support is implemented in `arp.c`.

Research notes:
- It exists for generated protocol registration consistency.
- Actual decoding/filtering behavior should be read from snoopy `arp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rarp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rc4keydesc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rc4keydesc.c

This file is a placeholder containing only the comment that RC4 key descriptor support is implemented in `eapol_key.c`.

Research notes:
- It maps a protocol-list entry to an implementation hosted in another snoopy module.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rc4keydesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtcp.c

This snoopy module formats RTCP sender reports plus report blocks.

Key behavior:
- Requires the minimum 28-byte sender report header.
- Validates packet length using the RTCP length field.
- Prints version, report count, packet type, SSRC, NTP/RTP timestamps, packet/octet counts, and header length.
- Iterates report blocks, printing CSRC, loss percentage/cumulative loss, highest sequence, jitter, LSR, and DLSR.
- Terminal decoder with no filters/mux.

Research notes:
- The code mutates `r->lost[0] = 0` while formatting cumulative loss, modifying the packet buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtp.c

This snoopy module formats RTP headers.

Key behavior:
- Requires the 12-byte minimum RTP header and validates CSRC list length.
- Prints version, extension bit, CSRC count, sequence number, timestamp, and SSRC.
- Prints each CSRC value and advances the message pointer past the CSRC list.
- Terminal decoder with no payload demux.

Research notes:
- Marker/payload type byte is named `marker` in the struct but is not printed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/rtp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/tcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/tcp.c

This snoopy module decodes and filters TCP packets.

Key behavior:
- Filters support source port (`s`), destination port (`d`), and either port (`a`/`sd`).
- Muxes DNS and 9P for known TCP ports.
- Parses header length, flags, sequence/ack numbers, window, checksum, and common TCP options.
- Recognizes MSS and window-scale options; unknown options are hex-dumped.
- Special-cases DNS-over-TCP by skipping the two-byte DNS length field before handing payload to DNS.

Research notes:
- `PseudoHdr` is defined but unused here.
- Header length handling relies on the packed flag/header-length word.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ttls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ttls.c

This snoopy module decodes a small TTLS tunnel/framing header.

Key behavior:
- Parses a flags byte with version bits and S/M/L flags.
- If the L flag is set, consumes and prints a 32-bit total length.
- Always demuxes to `dump` so remaining payload is printed.
- Prints remaining data length and labels empty unflagged frames as acknowledgements.

Research notes:
- No filters are implemented.
- The module’s mux table contains only `dump` to force payload display.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ttls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/udp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/udp.c

This snoopy module decodes and filters UDP packets.

Key behavior:
- Filters support source port (`s`), destination port (`d`), and either port (`a`/`sd`).
- Muxes DNS, BOOTP, 9P, RTP, and RTCP.
- RTP/RTCP use `ANYPORT`; selecting them in a filter sets a temporary default payload protocol.
- Prints source/destination ports, checksum, and UDP length.
- Resets the temporary default protocol to `dump` after each packet.

Research notes:
- The global `defproto` is mutable during filtering, so RTP/RTCP interpretation depends on filter path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/udp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/vlan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/vlan.c

This snoopy module decodes IEEE 802.1Q VLAN headers.

Key behavior:
- Parses 16-bit tag and 16-bit encapsulated EtherType.
- Filters support VLAN ID (`v`), priority (`q`), and type (`t`).
- Reuses external `ethertypes[]` for subprotocol demux and filter compilation.
- Prints VLAN ID, queue priority, EtherType, and packet length.
- Demuxes to the EtherType-selected protocol or `dump`.

Research notes:
- The priority is taken from the upper four bits of the tag, although VLAN priority is usually three bits plus CFI/DEI.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/vlan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/socksd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/socksd.c

This is a SOCKS4/SOCKS4a/SOCKS5 proxy server for Plan 9 network files.

Key behavior:
- Supports `CONNECT`, `BIND`, and SOCKS5 `UDP ASSOCIATE`.
- Accepts SOCKS5 “no authentication” only.
- Converts between SOCKS address encodings and Plan 9 dial strings.
- Provides UDP relay using Plan 9 UDP header mode and forked bidirectional forwarding.
- Supports `-x` and `-o` to choose inside/outside network mount points.

Research notes:
- SOCKS4a domain parsing is implemented.
- The program relies on Plan 9 `announce`, `listen`, `accept`, `dial`, and network connection metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/socksd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/sol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/sol.c

This is an Intel AMT Serial-over-LAN and KVM redirection client.

Key behavior:
- Connects to AMT redirection ports 16995 with TLS or 16994 without TLS.
- Supports digest authentication through factotum and plaintext fallback.
- Provides raw console handling through `/dev/consctl`.
- For SOL, forks bidirectional forwarding between local console and AMT transmit/receive messages.
- For KVM mode, sends the KVM redirect command then relays bytes directly.

Research notes:
- Uses compact `send()`/`recv()` format strings for little-endian AMT records.
- On post-auth EOF, it kills the helper process and reconnects via `longjmp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/sol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnet.c

This is the Plan 9 telnet client frontend. It handles dialing, terminal raw mode, keyboard/network forwarding, escape menu handling, and client-side telnet subnegotiation callbacks.

Key behavior:
- Options include debug, no-keyboard mode, CR handling, suppress local echo negotiation, and posting a pipe in `/srv`.
- Forks two processes: keyboard-to-network and network-to-screen.
- Recognizes Ctrl-\ escape menu for break, interrupt, quit, CR mode toggle, and shell command execution.
- Uses shared telnet negotiation code from `telnet.h`.
- Sends terminal type from `$TERM` and X display location from `$XDISP`.

Research notes:
- `xlocsub()` uses `strncpy(p, term, p - buf - 2)`, which appears to compute a negative/invalid remaining length; this is a likely bug.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnet.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnet.h

This header contains shared telnet constants, option state, negotiation handlers, and small I/O helpers used by both `telnet.c` and `telnetd.c`.

Key behavior:
- Defines Telnet IAC commands and common option codes.
- Maintains an `Opt opt[]` table with local/remote state and optional callbacks.
- Implements `control()`, `will()`, `wont()`, `doit()`, `dont()`, and subnegotiation parsing.
- Provides `send2()`, `send3()`, process note sending, fatal errors, and interrupt-tolerant read/write wrappers.

Research notes:
- This is a header with function definitions and global state, so each including program gets its own telnet engine instance.
- `noway` options are refused automatically.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnetd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/telnetd.c

This is the Plan 9 telnet daemon. It authenticates users, creates a shell namespace, simulates `/dev/cons` and `/dev/consctl`, and bridges telnet network input/output to an interactive rc shell.

Key behavior:
- Supports raw/no-protocol modes, trusted user mode, explicit user, no-`none` controls, and noworld-only login.
- Uses p9cr challenge-response auth or password login for noworld accounts.
- Negotiates echo, terminal type, and X display options unless protocol mode is disabled.
- Implements cooked-line editing, echo, CR/LF normalization, EOF, word erase, line kill, and interrupt notes.
- Creates pipe-backed `/dev/cons` and `/dev/consctl`, sharing console raw/hold state via a shared segment.

Research notes:
- Includes `../ip/telnet.h`, which defines global option state and negotiation functions.
- Logs auth/session events through `syslog` under `telnet`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/telnetd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tftpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tftpd.c

This is a TFTP daemon implementing RFC 1350 plus option negotiation from RFC 2347/2348/2349.

Key behavior:
- Serves read and write requests over UDP using Plan 9 `announce/listen/accept`.
- Drops into user `none` and builds a namespace before serving.
- Supports `timeout`, `blksize`, and `tsize` options, including OACK responses.
- Implements retransmit/ack handling, error packets, upload creation, and download streaming.
- Supports restricted path mode, homedir selection, namespace file, net mount selection, service/address override, and filename map files.

Research notes:
- Contains PXE/u-boot compatibility handling, including Bandt MTU blksize clamping and Cavium 1432-byte exception.
- `mapname()` can substitute remote IP, PXE config MAC path, or MAC address using `/net/arp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tftpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tftpfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tftpfs.c

This is a read-only 9P filesystem client for TFTP. It exposes remote TFTP paths as files under a mount point or srv name.

Key behavior:
- Uses libthread and lib9p `Srv`.
- `attach` selects a default or per-attach server IP.
- Walking builds synthetic paths; any path containing a dot is treated as file data.
- Reads/stat on a file spawn or use a `download` process that sends TFTP RRQ packets and caches data.
- ACKs blocks, handles retransmitted blocks, and serves reads while download is in progress.

Research notes:
- File paths with no dot can be forced as files by appending a trailing dot, stripped from the TFTP request.
- Only read/exec opens are allowed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tftpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tinc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tinc.c

This is a Plan 9 implementation of a tinc-like VPN node. It manages host/subnet topology, authenticated meta connections, encrypted packet transport, and routing through a Plan 9 packet `ipifc`.

Key behavior:
- Reads host config files with RSA public keys, Address, Port, Subnet, PMTU, TCP-only, indirect-data, MSS clamp, and PMTU discovery settings.
- Authenticates meta TCP connections using RSA via factotum and negotiates AES keys.
- Propagates graph updates: subnets, edges, key changes, key requests/answers, ping/pong, and TCP packet fallback.
- Encrypts UDP packet traffic with AES-CBC plus truncated SHA2-256 HMAC and replay tracking.
- Routes Ethernet-framed IPv4/IPv6 packets, supports VLAN stripping, subnet lookup, TCP MSS clamping, UDP fast path, and TCP fallback.
- Creates a Plan 9 `ipifc` packet interface and runs rc hook scripts for host/subnet/up/down events.

Research notes:
- Uses global graph arrays protected by `netlk`, with `lconn` preventing echoing updates back to the origin.
- Default PMTU accounts for worst-case UDPv6 over 6in4 over PPPoE plus crypto overhead.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/tinc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/torrent.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/torrent.c

This is a compact BitTorrent client and torrent-file generator.

Key behavior:
- Implements bencode parsing, dictionary lookup, torrent metadata loading, infohash generation, piece map tracking, and SHA1 piece verification.
- Supports single-file and multi-file torrents, path sanitization that replaces spaces with non-breaking spaces, and on-demand directory creation.
- Implements BitTorrent peer handshake and messages: bitfield, have, interested, choke/unchoke, request, piece, cancel, and port.
- Runs incoming peer server, outgoing peer workers, HTTP trackers, UDP trackers, and webseed fetchers.
- `-c` creates a torrent for a file with trackers/webseeds.
- Tracks upload/download/left counters and can print progress.

Research notes:
- Uses `/mnt/web` for HTTP tracker and webseed fetches.
- Peer scheduling picks randomly among missing pieces advertised by a peer.
- The piece message truncation path has suspicious code: `if(o+n > pieces[x].len) n = o - pieces[x].len;`, which can make `n` negative.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/torrent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/traceroute.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/traceroute.c

This is a Plan 9 traceroute utility built around network control/data files.

Key behavior:
- Parses dial strings with optional netdir/protocol and defaults to `/net`, `tcp`, and port 32767.
- Uses the connection server to translate names unless bypassed or unavailable.
- Probes TCP/IL by attempting connect, UDP by writing to a likely-unused port, and ICMP/ICMPv6 by sending echo requests.
- Sets TTL through the connection control file and times each probe in microseconds.
- Optionally reverse-resolves hop names and prints latency low/avg/high plus optional histograms.

Research notes:
- Handles Plan 9 error strings such as `ttl exceeded at`, `refused`, and `unreachable`.
- Probe count defaults to three and TTL stops at 31.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/traceroute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/udpecho.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/udpecho.c

This is a minimal UDP echo service.

Key behavior:
- Announces `udp!*!echo` on a configurable network mount point.
- Enables UDP header mode on the control file.
- Opens the data file read/write and writes every received packet back unchanged.
- Supports `-x netmtpt`.

Research notes:
- Because header mode is enabled, echoing the entire received buffer preserves the remote address header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/udpecho.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/wol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/wol.c

This sends Wake-on-LAN magic packets.

Key behavior:
- Parses a target Ethernet MAC address.
- Builds the standard packet: six `0xff` bytes followed by the MAC repeated 16 times.
- Optional `-c` appends a password up to six bytes.
- Optional `-a` overrides the default destination `udp!255.255.255.255!0`.
- Optional `-v` prints packet details.

Research notes:
- Uses Plan 9 `%E` formatting for Ethernet addresses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/wol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/join.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/join.c

This is the Plan 9 implementation of the `join` text utility.

Key behavior:
- Joins two sorted input files on selected fields.
- Supports `-1`, `-2`, `-j`, `-a`, `-e`, `-t`, and `-o` output field selection.
- Handles UTF input by converting lines to `Rune` buffers before field splitting/comparison.
- Requires at least one randomly seekable input and has separate algorithms depending on which file can seek.
- Outputs default joined fields or explicit field lists, with null replacement for missing fields.

Research notes:
- Maximum fields per line is fixed at `NFLD=100`; long/truncated lines set `discard`.
- Uses stdio rather than Plan 9 `Biobuf`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/join.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.c

This is the BMP viewer/converter frontend for the Plan 9 image tools.

Key behavior:
- Reads BMP via `readbmp(fd, CRGB)`.
- Displays images using libdraw/event unless `-d` or output flags suppress display.
- Converts decoded `Rawimage` to CMAP8, GREY8, or RGB24 via `torgbv()` / `totruecolor()`.
- Can write Plan 9 uncompressed image format with `-9` or compressed raw image with `-c`.
- Supports color/dither options shared with other image frontends.

Research notes:
- Output modes exit after one file when multiple inputs are given.
- The display path centers the image and waits for one keyboard event.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.h

This header defines BMP constants and header structures.

Key contents:
- Compression constants: RGB, RLE8, RLE4, and bitfields.
- `Rgb` palette entry struct.
- `Filehdr` and `Infohdr` structures matching BMP file and info header fields.
- `Filehdrsz` constant for the 14-byte file header.

Research notes:
- The structures use Plan 9 C scalar types and are likely read through helper code that handles little-endian layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/bmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/close.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/close.c

This is a code-generation helper for color quantization tables.

Key behavior:
- Converts YCbCr to approximate RGB and finds the nearest Plan 9 colormap index by squared RGB distance.
- Buckets colors into a 5-bit-per-component cube.
- Prints per-bucket colormap index lists.
- Intended to generate lookup data, not to operate as an image viewer/converter.

Research notes:
- This program is computationally heavy: it iterates all 256^3 Y/Cb/Cr combinations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/close.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/gif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/gif.c

This is the GIF viewer/converter frontend.

Key behavior:
- Reads GIF frames via `readgif(fd, CRGB, dflag)`.
- Handles animated GIFs, frame delays, loop counts, disposal modes, and transparency masks.
- Displays animation with libdraw/event unless suppressed.
- Converts output to CMAP8, GREY8, RGB24, or alpha-bearing formats when transparency is present.
- Writes Plan 9 image or compressed raw image output for the first frame.

Research notes:
- `addalpha()` and `blackout()` convert GIF transparency into alpha channels for output formats.
- Uses a global `allims`/`which` pair for resize redraw of the current animation frame.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/gif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/ico.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/ico.c

This is an ICO file reader/viewer and optional image extractor.

Key behavior:
- Parses ICO headers and directory entries.
- Supports icon payloads that are embedded PNGs or BMP-style DIB data.
- Converts paletted BMP icons through a Plan 9 colormap, handles XOR image data and optional AND masks.
- Displays all icons in a grid-like window and shows dimensions on hover.
- Right-click menu can write selected image or mask; `-c` writes the first icon image to stdout.

Research notes:
- Uses `memdraw` `Memimage` internally and converts to display `Image` row by row.
- For BMP icons, it composites image plus mask over white before display/export.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/ico.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/imagefile.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/imagefile.h

This is the shared interface header for Plan 9 image codec frontends and writers.

Key contents:
- Defines `Rawimage`, including rectangle, colormap, channel array, channel descriptor, channel length, and GIF metadata.
- Defines channel descriptor enum values for RGB, YCbCr, luminance, RGBV, packed RGB/RGBA, and alpha variants.
- Defines GIF and PNG metadata flags plus `ImageInfo`.
- Declares decoders for JPG/PNG/TIFF/GIF/pixmap, conversion helpers, raw image writer, GIF/PPM/JPG/PNG/TIFF writers, and one/multi-channel conversion helpers.

Research notes:
- This header is the local contract linking the frontend commands to format-specific read/write implementation files elsewhere in the `jpg` directory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/imagefile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/jpegdump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/jpegdump.c

This is a standalone JPEG marker parser/dumper, written in portable stdio C style.

Key behavior:
- Reads JPEG marker streams and prints SOI/EOI, SOF, SOS, DQT, DHT, DAC, COM, APPn, restart markers, and entropy segment lengths.
- `-t` dumps quantization and Huffman table entries.
- APP marker parsing extracts printable strings.
- Supports multiple JPEG streams concatenated in one file by restarting after EOI if more input remains.

Research notes:
- Uses custom `warn`, `quit`, and `fatal` routines.
- The SOI check is commented out, so parsing starts by searching marker structure rather than enforcing JFIF/SOI upfront.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/jpegdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/jpg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/jpg.c

This is the JPEG viewer/converter frontend.

Key behavior:
- Reads JPEG via `Breadjpg()` into YCbCr or RGB depending on flags and display depth.
- Supports display, compressed raw output, Plan 9 uncompressed output, greyscale, RGB24, RGBV, no-dither, and decode-only modes.
- Supports field merging for interlaced/video JPEG pairs with `-f` and movie mode with `-F`.
- Converts `Rawimage` to display/output channel formats using `torgbv()` or `totruecolor()`.
- Handles repeated frames in movie mode by looping back to decode more JPEGs from the stream.

Research notes:
- `vidmerge()` interleaves scanlines from two decoded images and validates dimensions/channel metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/jpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/multichan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/multichan.c

This helper converts drawable images to separate color channels when required by writers.

Key behavior:
- Leaves GREY1/2/4/8 and RGB24 images unchanged.
- Converts other `Image` objects to RGB24 by drawing into a new RGB24 image.
- Provides the same operation for `Memimage`.
- Used by writer frontends that need one byte per color component and no alpha/X channel.

Research notes:
- If no conversion is needed, ownership of the original image remains with the caller.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/multichan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/onechan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/onechan.c

This helper converts images to one byte per pixel, usually CMAP8/RGBV or greyscale.

Key behavior:
- Leaves GREY and CMAP8 images unchanged.
- Fast-paths RGB16, RGB24, RGBA32, and ARGB32 by unpacking into temporary RGB channels.
- Uses `torgbv()` to quantize RGB into Plan 9 colormap indices.
- Converts other image channels by first drawing to RGB24.
- Provides both `Image` and `Memimage` versions.

Research notes:
- Temporary `Rawimage` channel buffers are manually allocated and freed around the `torgbv()` call.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/onechan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/png.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/png.c

This is the PNG viewer/converter frontend.

Key behavior:
- Reads PNG via `Breadpng(&b, CRGB)`.
- Supports display, compressed raw output, Plan 9 uncompressed output, debug flag, greyscale/RGB24/RGBV/CMAP8 modes, and dither control.
- Preserves PNG-decoded channel descriptors such as GREY+alpha and RGBA when writing/displaying true-color output.
- Uses a black background composition image for display so alpha effects are visible.
- Frees raw channel buffers after processing.

Research notes:
- Usage string mentions `-r`, but option parsing does not implement `r`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/png.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/ppm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/ppm.c

This is the PPM/pixmap viewer/converter frontend.

Key behavior:
- Reads pixmap data via `readpixmap(fd, CRGB)`.
- Supports the common frontend flags for display suppression, raw output, Plan 9 image output, dithering, greyscale, RGB24, RGBV, and three-color output.
- Converts to CMAP8 with `torgbv()` or to true-color/greyscale with `totruecolor()`.
- Displays centered image and waits for a keyboard event.
- Writes either raw compressed image or Plan 9 uncompressed image header plus pixel data.

Research notes:
- Closely mirrors `bmp.c`, with format-specific decode and command names changed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/ppm.c -->