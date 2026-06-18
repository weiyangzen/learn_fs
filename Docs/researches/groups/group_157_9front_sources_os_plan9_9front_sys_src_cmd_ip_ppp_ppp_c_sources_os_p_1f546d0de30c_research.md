# Group Research: 9front IP/PPP and snoopy protocol sources

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All files listed in this work item were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.c

This is the main user-space PPP implementation for Plan 9/9front. It implements PPP framing, LCP/IPCP/IPv6CP/CCP negotiation, PAP/CHAP authentication, optional TCP header compression, optional packet compression, link quality reporting, and attachment to Plan 9’s packet IP interface.

Important entry points are `main`, `pppopen`, `pppread`, and `pppwrite`. `main` parses modem/device/network/auth/compression options, opens the media endpoint, starts an `rc` helper pipe, then forks into the PPP engine. `pppopen` initializes addresses, media fds, interface metadata, PPP state, and runs the media input loop. `pppread` consumes PPP frames from the media and returns IP/IPv6 payloads. `pppwrite` accepts IP packets from the Plan 9 packet interface and sends PPP frames.

The file has several intertwined state machines. `Pstate` instances drive LCP, CCP, IPCP, and IPv6CP through closed/request/ack/open states. `setphase` moves the whole link through link authentication and network phases. `config`, `getopts`, `rejopts`, and `rcv` encode and parse LCP-style options. `ppptimer` retransmits configuration requests, drives echo keepalives, authentication retry, and link-quality packets.

The frame layer supports raw packets and HDLC-style byte-stuffed framing. It computes and checks RFC 1331 FCS via `fcstab`, handles address/control and protocol-field compression, and keeps packet/byte/discard counters.

Authentication supports PAP client mode plus CHAP MD5, MS-CHAP, and MS-CHAPv2 using Plan 9 auth APIs. MS-CHAP key material feeds MPPE/MPPC style send/receive keys. Server mode sends CHAP challenges and requires successful auth before opening network protocols unless `-a` disables auth.

Network setup is Plan 9-specific. `ipopen` opens `/net/ipifc/clone`, binds the packet device, runs `ip/ipconfig` commands through an `rc` pipe, and adds/removes IPv4 and IPv6 point-to-point addresses. IPv6CP derives link-local addresses from EUI data.

Compression paths include Van Jacobson TCP header compression and CCP data compression through `Comptype`/`Uncomptype` vtables. Unknown protocols are rejected with LCP Protocol-Reject when LCP is open.

Notable details: global `dying` coordinates shutdown across rforked processes; `terminate` removes configured IP addresses and posts a note to the process group. The implementation is tightly coupled to Plan 9 fd namespaces, `/net`, `ipifc`, and auth conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.h

This header defines the core PPP data model shared by the PPP engine and compression modules. It declares `Block`, `PPP`, `Pstate`, `Chap`, `Qualstats`, compression vtables, LCP option/message structures, and protocol constants.

`Block` is the local packet-buffer abstraction with `rptr`, `wptr`, `base`, and `lim`, plus `BLEN` and `BALLOC`. The header only declares allocation helpers; definitions live elsewhere in the PPP program set.

The large enum captures HDLC constants, PPP phases, PPP protocol numbers, LCP codes, LCP/CCP/ECP/IPCP/IPv6CP options, auth protocols, state names, timers, buffer sizes, and MTU bounds. These constants are consumed directly by `ppp.c`, `thw.c`, and related modules.

`PPP` is the central runtime object. It embeds locks, media/IP fds, Plan 9 network paths, IPv4/IPv6 negotiated/current addresses, DNS/WINS values, input/output buffers, LCP/CCP/IPCP/IPv6CP/CHAP state pointers, compression state, encryption keys, auth name, link-quality counters, and packet statistics.

The compression interface is abstracted through `Comptype` and `Uncomptype`, allowing MPPC and Thwack modules to plug into CCP without changing the main PPP state machine.

Exports include `pppread`, `pppwrite`, `pppopen`, LCP allocation/checksum helpers, TCP compression hooks, MS-CHAP key derivation, MPPC/Thwack vtables, and `netlog`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ppp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/testppp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/testppp.c

This is a small PPP test harness. It creates two pipes, starts one PPP process as a server on `/net` and one as a client on `/net.alt`, then shuttles bytes between them.

`pppopen` forks and execs the selected PPP binary, building arguments for debug, server/client mode, no-auth, framing, compression flags, MTU, network mount point, proxy, and local/remote addresses.

`xfer` forwards data from one pipe endpoint to the other. It can inject byte corruption with `-e errrate`, drop whole chunks with `-d droprate`, and optionally print packet prefixes when debug is high. This makes it useful for exercising PPP retransmission, FCS rejection, and compression-reset behavior.

The program expects exactly local and remote address arguments. It is not a protocol implementation itself; it is a local impairment harness for the PPP executable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/testppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thw.c

This file adapts the Thwack compressor/decompressor to PPP CCP. It provides `Comptype cthwack` and `Uncomptype uncthwack`, which match the vtable interface declared in `ppp.h`.

The compressor state `Cstate` tracks a sequence number, a `Thwack` encoder, and stats. The decompressor state `Uncstate` tracks acknowledgment scheduling, reset state, and an `Unthwack` decoder.

`comp` wraps PPP payloads into `Pcdata` compressed datagrams. It prepends compressed protocol fields, embeds decompressor acknowledgments when available, decides whether small packets must be added to history, and falls back to uncompressed output when compression is not worthwhile or does not fit the MTU.

`uncomp` decodes Thwack data frames, uncompressed-add frames, and plain uncompressed frames. On decoder errors it sends CCP Reset-Request and marks the decompressor inactive until the matching Reset-Ack arrives. It also derives ACK masks from the decoder history and feeds incoming ACKs back to the compressor via `thwackack`.

`compresetreq` resets the encoder and converts a peer Reset-Request into Reset-Ack. `uncresetack` reactivates and resets the decoder after the expected reset id.

The file is glue code: sequence, ACK, reset, and PPP protocol-field handling live here; the actual LZ/Huffman-style codec lives in `thwack.c` and `unthwack.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.c

This is the Thwack encoder. It implements a sliding-window LZ-style compressor with custom variable-length coding for literals, match lengths, and offsets.

`thwackinit` resets the encoder window, per-slot hash tables, block metadata, and retained `Block` references. `thwackcleanup` frees retained blocks. `thwackack` marks sequence blocks acknowledged by the decoder, enabling them as usable history for future compression.

`thwmatch` searches current and acknowledged history blocks through per-block hash tables keyed by a three-byte rolling value. Matches are encoded as length plus backward offset over a compound history assembled from the current block and acknowledged previous blocks.

`thwack` is the main compressor. It rejects oversized or too-small source blocks, inserts the source block into the encoder window, builds a bounded history list, emits sequence/history mask metadata, then encodes literals and matches. It bails out when output would exceed the destination and `mustadd` is false. It also has a progress heuristic that stops compression if the first half of a block shows poor compression.

The encoder keeps original source `Block` objects in the history window after successful insertion, so ownership is transferred to the encoder until cleanup or window replacement.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.h

This header defines Thwack codec limits, state structures, and exported functions.

Important constants include `ThwMaxBlock` 1600, `HashLog` 12, `MinMatch` 3, encoder/decode window sizes of 64 blocks, and history encoding bounds such as `CompBlocks`, `MaxSeqMask`, and `MaxSeqStart`.

`ThwBlock` describes an encoder history block with sequence number, acknowledgment status, rolling hash table, byte range, and offset metadata. `Thwack` contains the encoder slot pointer, per-slot block descriptors, hash tables, and retained `Block` pointers.

`UnthwBlock` and `Unthwack` are the decoder-side history store. The decoder uses fixed byte arrays per slot rather than retaining input `Block`s.

Exports are `thwackinit`, `thwackcleanup`, `thwack`, `thwackack`, `unthwackinit`, `unthwack`, `unthwackstate`, and `unthwackadd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/thwack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/unthwack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/unthwack.c

This is the Thwack decoder. It reconstructs compressed blocks using the current output buffer plus prior decoder-history blocks identified by sequence metadata.

`unthwackinit` clears decoder state and points every `UnthwBlock` at its fixed backing buffer. `unthwackstate` returns the newest received sequence plus a mask of nearby history blocks, which the PPP glue sends back as compressor acknowledgments.

`unthwackinsert` stores a decoded or uncompressed-add block in sequence order, replacing the oldest slot. `unthwackadd` inserts a raw block into decoder history.

`unthwack` parses the compressed stream. It first reconstructs the history block list from sequence-delta and mask bytes. It then decodes literals and length/offset references using tables that mirror the encoder’s variable-length format. Output is written to a temporary decoder slot, copied to the caller’s destination, and inserted into decoder history if successful.

Errors are reported through `ut->err` and negative returns, covering missing history blocks, invalid offsets, excessive output, bad lengths, and compressed data overrun.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/unthwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pppoe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pppoe.c

This is a user-level PPPoE client for RFC 2516. It performs PPPoE discovery over Ethernet, establishes a session, bridges session payloads to a pipe, and execs `/bin/ip/ppp` on that pipe.

It defines Ethernet, PPPoE, and tag headers plus constants for discovery/session ethertypes, discovery codes, and standard tags. `padi` constructs Active Discovery Initiation packets; `padr` constructs Active Discovery Request packets including service name, access concentrator name, and optional cookie.

`pppoe` opens discovery and session Ethernet endpoints, sends PADI/PADR with exponential timeouts, accepts offers and confirmations through `wantoffer` and `wantsession`, and then forks bridge processes. One process copies PPPoE session payloads from Ethernet to the PPP pipe, another wraps PPP bytes from the pipe into PPPoE session frames, and another waits for PADT termination. With `-r`, failed sessions are retried in the background.

`execppp` builds PPP arguments for MTU, primary mode, compression flags, network mount point, IP net names, auth keyspec, DUID, and disables PPP’s own address/control framing with `-F`.

The parser includes validation helpers `malformed`, `findtag`, `dumppkt`, and `dumptags`. DUID-LL is generated from the local Ethernet address when not provided.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pppoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pptp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pptp.c

This is a PPTP client that negotiates the PPTP TCP control channel, establishes a GRE PPP tunnel, and runs `/bin/ip/ppp` over a local pipe.

`threadmain` parses primary/debug/keyspec/window/network options, dials the server, and calls `pushppp`. `pptp` dials TCP service `pptp`, reads local/remote addresses from the dial directory, starts the control reader, sends Start-Control-Connection and Outgoing-Call requests, opens a GRE endpoint, then starts GRE reader, PPP reader, and timeout processes.

`pptpctlproc` reads length-prefixed PPTP control messages, validates magic/type, handles peer echo requests, rejects unexpected control operations, and delivers expected responses through a channel. `tstart` and `tcallout` construct client control messages and validate returned control replies.

GRE handling uses PPTP GRE protocol `0x880B`. `pppreadproc` wraps PPP bytes with source/destination IPv4 addresses, GRE flags, call id, sequence, and ACK. `grereadproc` validates source/destination/protocol, extracts ACK and sequence fields, and forwards in-order PPP payloads to the PPP pipe. `schedack`, `sendack`, `recordack`, and `waitacks` implement basic sequencing and acknowledgment behavior, with a small out-of-order swap recovery path.

`gretimeoutproc` advances ticks, sends control-channel echo requests, and fails on server timeout. `myfatal` tries to send a PPTP Stop-Control-Connection request before terminating all threads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pptp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pptpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/pptpd.c

This is the PPTP server-side handler. It is intended to be run for an accepted PPTP TCP connection, using the passed TCP dial directory to discover local/remote addresses. It negotiates PPTP control messages, opens a GRE endpoint, allocates per-call PPP sessions, and bridges GRE payloads to `/bin/ip/ppp`.

The central server object `srv` stores connection addresses, GRE fds, PPP executable/net mount settings, receive window, DHCP-derived base address, and a call hash table. Each `Call` stores call id, PPP fd, GRE sequence/ACK/window state, error stats, DHCP pipes, and refs.

`serve` reads control messages from stdin, validates the PPTP magic and type, and dispatches to handlers. Implemented handlers include start, stop, echo, outgoing call, call clear/disconnect, WAN info, and link info. Incoming-call request/connect paths are present but fatal as not implemented.

`callalloc` allocates a call id, obtains a remote IP using `/bin/ip/dhcpclient`, starts `/bin/ip/ppp -SC` with local and remote addresses, inserts the call in the hash table, and starts PPP read and GRE timeout workers.

`greread` parses GRE packets, validates source/destination/protocol/key, finds the call by call id, updates ACKs, forwards in-order PPP payloads, accounts missing/dropped packets, and sends ACKs when the receive window has advanced. `pppread` reads PPP bytes, wraps them in GRE key/seq/ack headers, and waits on an event when the send window is full.

`timeoutthread` closes the server after control-channel inactivity. `myfatal` sends a PPTP stop message, logs through syslog, closes fds, and posts a process-group note.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/pptpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rarpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rarpd.c

This is a RARP daemon. It listens for Ethernet type `0x8035`, looks up client Ethernet addresses in NDB, replies with IPv4 addresses, and optionally populates the local ARP table.

`main` parses Ethernet device, net mount point, NDB file, and debug options. It opens the NDB database, dials the RARP Ethernet endpoint, gets the server’s local IP and Ethernet address, opens `/net/arp` if available, forks into the background, and loops reading RARP packets.

For each valid request, it checks packet size and operation, formats the target hardware address, looks up `ether=<addr>` to `ip=<addr>` with `lookup`, fills target protocol address, sets sender hardware/protocol fields to the server, changes op to RARP reply, and sends a minimum Ethernet frame.

`lookup` wraps `ndbipinfo`, defaulting source attribute via `ipattr` when needed. The daemon logs failures through syslog with log name `ipboot`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rarpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rexexec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rexexec.c

This is a remote execution service wrapper intended to be invoked by `listen`. It authenticates the peer with Plan 9 auth protocol `p9any` in server role.

After authentication, it rejects user `none`, changes uid with `auth_chuid`, and updates the network connection’s owner/mode to the authenticated cuid. It then reads a NUL-terminated command from fd 0 into an 8 KiB buffer.

Finally it sets environment variable `service=rx` and execs `/bin/rc -lc <command>`. It is small but security-sensitive: the effective user is established by Plan 9 auth before command execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rexexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rip.c

This is a RIP v1 routing daemon for IPv4. It receives RIP responses, maintains an in-memory route table, installs/removes routes through `/net/iproute`, and optionally broadcasts route updates.

The code defines RIP wire structs, route table storage, interface metadata, and broadcast-network selection. `main` parses broadcast/debug/read-only/net options plus optional specific broadcast networks, backgrounds unless debugging, reads interfaces and existing routes, opens UDP port `rip` in header mode, then loops receiving RIP messages.

`readifcs` uses `readipifc` to discover IPv4 interfaces, masks, direct networks, and broadcast eligibility. `readroutes` seeds internal state from `/net/iproute`, preserving an immutable default route.

`considerroute` hashes routes by class network, rejects attempts to hijack the default route, replaces stale or worse existing routes, and installs better routes. `installroute` and `removeroute` write textual commands to `/net/iproute` unless read-only mode is active.

`broadcast` refreshes interfaces and calls `sendto` for each broadcast network. `sendto` applies split-horizon-like filtering, avoids advertising a network to itself, avoids leaking subnet routes across classful boundaries, and emits RIP response packets. `timeoutroutes` expires non-infinite routes after ten minutes without refresh.

The implementation is classful and IPv4-only, matching RIP v1 expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rlogind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rlogind.c

This is a minimal rlogin compatibility wrapper. It reads the initial rlogin strings from fd 0: an ignored error/port string, remote user, local user, and terminal type. It writes a NUL byte acknowledgement.

If the local user string is empty, it falls back to the remote user. It logs the selected user under syslog facility name `telnet` and execs `/bin/ip/telnetd -n -u <user>`.

`getstr` reads NUL-terminated fields byte by byte with a fixed output length, tolerating zero-length reads by continuing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/rlogind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoe.c

This snoopy module decodes the common ATA-over-Ethernet header. It exposes filters for shelf, slot, and command, and demuxes command values to `aoeata`, `aoecmd`, `aoemask`, or `aoerr`.

The header parser consumes version/flags, error, major, minor, command, and tag. `p_filter` advances past the AoE header and compares selected fields. `p_seprint` prints version, flags, error, shelf/slot, command, and tag, then chooses the next protocol by command.

The `Proto aoe` registration includes mux table, numeric value format, fields, and default framer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoeata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoeata.c

This module decodes the AoE ATA command payload. It defines fields for ATA flags, command/status, features/error, sector count, and 48-bit LBA.

`llba` converts the six-byte little-endian AoE LBA into a `uvlong`. `p_filter` compares parsed fields and notes that status/error matching is direction-blind because the dissector lacks request/response context. `p_seprint` prints ATA flag, err/feat, sector count, cmd/status, and LBA, then terminates protocol traversal.

The module is a leaf `Proto aoeata`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoeata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoecmd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoecmd.c

This module decodes AoE configuration command payloads. The payload includes buffer count, firmware version, sector count, command/version nibble, length, and configuration string bytes.

It supports a single `cmd` filter that compares the low nibble of `ccmd`. `p_seprint` prints buffer count, firmware, sector count, version, command, length, and then renders the following config string with the declared length.

This is a leaf AoE sub-protocol with no further demux.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoecmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemask.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemask.c

This module decodes AoE mask command payloads. It filters on command, error, and count, and demuxes command values 0 and 1 to `aoemd`.

`p_seprint` prints command name, error name, and count. The command table maps values to read/edit; the error table maps values to bad/full.

Notable implementation detail: in `p_seprint`, the error-name assignment writes to `s` rather than `t`, so printed error text may not match the intended table. The module also compiles comparison filters using `aoerr.name`, likely a copy/paste mistake, though runtime behavior depends on shared compile helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemd.c

This module decodes AoE mask directive records. The payload contains a reserved byte, command byte, and Ethernet address.

Filters support command and Ethernet address. Ethernet comparison reconstructs the target six-byte address from `Filter.ulv`.

`p_seprint` prints command numeric/name and Ethernet address, then stops protocol traversal. Command names are blank, add, and remove markers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoemd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoerr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoerr.c

This module decodes AoE error/config Ethernet-address lists. It has a two-byte header containing command and Ethernet-address count, followed by a list of six-byte addresses.

Filters nominally support command, address count, and address membership. `p_seprint` prints command name and count, then prints up to three Ethernet addresses.

Notable details: the field table maps `ea` to `Onea` rather than `Oea`, so address filters may compile as count filters. The print loop checks and indexes against `m->pe` where `m->ps` appears intended, which can produce incorrect address output. The module is a leaf protocol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoerr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/arp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/arp.c

This module decodes ARP and RARP packets. It uses the same parser and printer for both `Proto arp` and `Proto rarp`.

Fields support IPv4 source protocol address, target protocol address, either protocol address, hardware source, hardware target, and either hardware address. `p_filter` validates minimum ARP length, advances past the header, and compares fields using protocol or hardware address lengths from the packet.

`p_seprint` prints operation, protocol/hardware address lengths, source protocol/hardware addresses, and target protocol/hardware addresses. It is a leaf protocol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/bootp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/bootp.c

This module decodes BOOTP headers and demuxes option payloads. It understands standard BOOTP fields, Plan 9 BOOTP magic, and generic DHCP magic.

Filters support client address and server address, plus protocol selection by option magic. The mux table routes generic DHCP magic to `dhcp`, Plan 9 magic to `plan9bootp`, and otherwise to `dump`.

`p_seprint` prints request/reply type, hardware type/length/hops, transaction id, seconds, flags, client/your/server/gateway IPs, client hardware address, magic, optional server name, and boot file. It then positions `m->ps` at the option data and demuxes based on `optmagic`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/bootp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/cec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/cec.c

This module decodes a small CEC protocol header containing type, connection, sequence, and length, then prints optional following text.

It supports filters for type, connection, sequence, and length. `p_seprint` maps type values to names such as `Tinita`, `Tdata`, `Tack`, `Tdiscover`, and prints the text payload up to the declared length.

Notable detail: `p_filter` uses assignment instead of comparison for `conn`, `seq`, and `len`, so those filter cases modify the packet header and return the assigned value rather than performing equality tests.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/cec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dat.h

This is the core data header for snoopy protocol modules. It defines shared types `Proto`, `Mux`, `Field`, `Msg`, and `Filter`, plus network-byte-order macros `NetS`, `Net3`, and `NetL`.

`Proto` is the module vtable: name, compile hook, filter hook, print hook, mux table, value format, fields, and framer. `Mux` maps protocol names and numeric values to next `Proto` objects. `Field` describes filterable protocol fields.

`Msg` carries packet cursor state and print-buffer state during protocol walking. Modules advance `ps`, may truncate `pe`, set `pr` for the next protocol, and append to `p`.

`Filter` is the parsed filter-expression tree node. It stores operator, string token, child nodes, selected protocol, sub-operation, and typed comparison values.

The header also declares parser functions, compile/demux helpers, global display flags, and `filter`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dhcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dhcp.c

This module prints DHCP option data after BOOTP has positioned the message cursor at the option stream. It has no compile/filter hooks and is print-only.

Helper printers format byte arrays as hex, strings, signed/unsigned integers, IPv4 server lists, classful routes, and classless routes. `dhcptype` maps DHCP message type option values to names.

`p_seprint` walks TLV options until end option 255, skipping pad option 0 and stopping on malformed overrun. It recognizes common DHCP and BOOTP option constants from `../dhcp.h`: requested address, lease, message type, server id, message text, max message size, client id, parameter request list, vendor class, subnet mask, router, DNS, hostname, domain, MTU, static routes, classless routes, NetBIOS options, NTP, SMTP, POP3, WWW, IRC, and many others. Unknown options are printed as hex under `T<number>`.

The module terminates traversal with no next protocol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dhcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dns.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dns.c

This module decodes DNS messages using 9front’s NDB DNS parser structures from `../../ndb/dns.h`. It prints the DNS header first, then exposes synthetic sequential protocols for question, answer, authority, and additional records.

`p_seprint` calls `convM2DNS`; on success it prints id and flags and sets `m->pr` to the first non-empty section. The section printers `p_seprintqd`, `p_seprintan`, `p_seprintns`, and `p_seprintar` each print one RR via `fmtrr`, advance the linked list, and select the next section or clean up.

`fmtrr` handles many RR types: A, AAAA, NS, CNAME, SOA, MX, PTR, TXT, NULL, RP, KEY, SIG, CERT, CAA, OPT, and unknown data. It frees each RR after printing.

The bottom portion is copied support logic from `/sys/src/cmd/ndb/dn.c`, including RR type name lookup, allocation, and freeing. Local `dnlookup`, `emalloc`, `estrdup`, and `dnslog` stubs support parsing without normal resolver database behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dump.c

This is the fallback leaf printer for raw payload bytes. It has an empty compile hook and no filter hook.

`p_seprint` limits output length to global `Nflag`. If all selected bytes are printable or whitespace, it emits a string form with tab, carriage return, and newline escaped. Otherwise it emits lowercase hex bytes. It sets `m->pr = nil`.

This module is used as the default demux target throughout snoopy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap.c

This module decodes Extensible Authentication Protocol packets and includes the `eap_identity` sub-protocol implementation.

The EAP header contains code, id, length, and optional type for Request/Response. The mux table maps Identity, Notify, Nak, MD5, OTP, GTC, TTLS, expanded, and experimental types.

`p_filter` validates/truncates to the EAP length, advances past the EAP header and type byte for Request/Response packets, and matches selected type. `p_seprint` prints id, code name, type name when present, and length, then demuxes the remaining body.

`p_seprintidentity` prints EAP Identity data. It has special handling for a NUL-separated prompt/options layout; otherwise it prints the remaining bytes as text.

The file registers both `Proto eap` and `Proto eap_identity`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap_identity.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap_identity.c

This file is only a placeholder comment stating that the real `eap_identity` implementation is in `eap.c`.

It likely exists so build or protocol-registration machinery can refer to a source file for the nominal protocol, while avoiding duplicate implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eap_identity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol.c

This module decodes EAP over LAN headers. The header contains version, type, and data length.

The mux table maps EAPOL packet types to `eap`, start, logoff, key, and ASF alert. `p_compile` supports selecting these sub-protocols. `p_filter` matches type after consuming the EAPOL header.

`p_seprint` validates the header, truncates the message to the EAPOL payload length, demuxes based on type, and prints type name, version, and data length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol_key.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol_key.c

This module decodes EAPOL-Key descriptor selection and the RC4 key descriptor subtype.

The top-level `eapol_key` protocol reads a one-byte descriptor and demuxes descriptor type 1 to `rc4keydesc`. It prints the descriptor name.

`p_seprintrc4` consumes the RC4 key descriptor fields: key length, replay counter, IV, key index, MIC/digest, and remaining key data. It prints these values and any trailing data as hex.

Some multi-byte fields such as replay, IV, and digest are wider than `NetS`, so the printed numeric summaries are abbreviated rather than full-field decodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol_key.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ether.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ether.c

This module decodes Ethernet II headers and demuxes by ethertype. It maps IPv4, ARP, RARP, IPv6, PPPoE discovery/session, EAPOL, AoE, CEC, and VLAN ethertypes.

Filters support source, destination, either address, and type. Protocol-name filters compile to type comparisons and set the next protocol.

`p_seprint` validates the 14-byte header, consumes it, demuxes by ethertype, and prints source address, destination address, protocol type, and total frame length.

Notable detail: both ARP and RARP entries use ethertype `0x0806`; RARP normally uses a distinct ethertype, so this table may classify RARP only by explicit filter behavior rather than wire ethertype accuracy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/filter.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/filter.y

This is the yacc grammar and lexer for snoopy filter expressions. It builds `Filter` trees using `newfilter`.

The grammar supports bare words, equality, inequality via `!=`, protocol/function-style grouping `WORD(expr)`, parentheses, logical OR/AND with both symbolic and doubled operators, and unary negation.

`yyinit` sets the input string. `yylex` skips whitespace, tokenizes words and punctuation/operators, allocates a filter node for each token, and stores word strings with `strdup`. `yyerror` terminates with `sysfatal`.

The grammar encodes inequality as a negated equality subtree rather than a separate comparison primitive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/filter.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/gre.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/gre.c

This module decodes GRE headers for RFC 1701/2784 version 0 and PPTP GRE version 1. It supports filtering/demuxing by encapsulated protocol.

`parsehdr` reads flags, protocol, optional checksum/offset, key, sequence, ACK, and source-routing data. `p_filter` consumes the parsed header and matches protocol. `p_seprint` prints version, protocol, flags, optional checksum/key/sequence/ACK/routing offset, and recursion for version 0, then demuxes to protocols such as IP, ARP, PPP, EAPOL, IPv6, or Ethernet.

Notable detail: `parthdrlen` lacks parentheses around additive and ternary terms, so C precedence likely makes its result wrong for some flag combinations. That can affect `parsehdr`’s minimum-length validation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/gre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/hdlc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/hdlc.c

This module frames and decodes HDLC-style PPP byte streams for snoopy. It duplicates the PPP FCS table and constants used by the PPP implementation.

The protocol view only recognizes PPP address/control bytes as the mux key and demuxes to `ppp`. `p_filter` compares the first two bytes. `p_seprint` consumes those bytes and demuxes.

The custom `p_framer` reads from an fd into a static buffer, searches for HDLC frame delimiters, unescapes bytes, computes PPP FCS, drops bad frames with a diagnostic, and returns complete good frames to snoopy.

This framer is stream-oriented and maintains static buffered state across calls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/hdlc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp.c

This module decodes ICMPv4 packets. It supports filtering by type and selecting embedded IPv4 payloads for error messages.

`p_filter` consumes the ICMP header, compares type, or accepts embedded-IP selection for unreachable, time exceeded, source quench, redirect, and parameter problem messages. `p_seprint` prints type name, code, checksum, and type-specific fields such as echo id/sequence, timestamp values, redirect gateway, or parameter pointer.

When global `Cflag` is set, it recomputes and reports checksum mismatches. For ICMP error messages it advances past the unused/gateway/pointer data and sets `m->pr = &ip` to decode the quoted IPv4 packet.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp6.c

This module decodes ICMPv6 and several neighbor-discovery option formats. It supports filtering by type and selecting embedded IPv6 payloads for selected error messages.

`p_seprint` prints type name, code, checksum, and type-specific details for unreachable, packet-too-big, time exceeded, parameter problem, echo, router solicit/advertise, neighbor solicit/advertise, redirect, timestamp, info, and multicast query/report/done messages.

`opt_seprint` walks ICMPv6 options and formats source/target link-layer address, prefix information, redirect, and MTU options. Unknown or malformed options fall through to `dump`.

Checksum verification is present but commented out, likely because ICMPv6 checksum needs IPv6 pseudo-header context. Embedded IPv6 payloads are decoded by setting `m->pr = &ip6`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/igmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/igmp.c

This module decodes IGMP packets. It defines header fields for type, timeout, checksum, and group address, with filters declared for all four but implemented only for type.

`p_seprint` prints IGMP type name, timeout, checksum, and group address. It optionally verifies checksum when `Cflag` is set.

The module is a leaf protocol and defaults remaining bytes to `dump`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/igmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/il.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/il.c

This module decodes Plan 9’s IL protocol header. It supports filters for source port, destination port, and either port.

The mux table maps well-known Plan 9 service ports such as exportfs, 9fs, cpu, and related services to `ninep`. `p_seprint` prints source/destination ports, packet type, id, ack, special byte, checksum, and length, then demuxes by either port.

Packet type names include Sync, Data, Dataquery, Ack, Query, State, and Close.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/il.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip.c

This module decodes IPv4 headers and demuxes by protocol number. The mux table contains many assigned IP protocol names, including ICMP, IGMP, TCP, UDP, IL, GRE, OSPF, and others.

Filters support source address, destination address, either address, and protocol number. `p_filter` validates the base header and advances by IHL.

`p_seprint` truncates the packet to the IPv4 total length when extra bytes are present, advances past the IPv4 header including options, and prints source, destination, id, fragment field, TTL, protocol, and length. It demuxes to the next protocol only for non-fragmented or first-fragment packets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip6.c

This module decodes IPv6 headers, selected extension headers, and demuxes by final next-header value. The mux table includes TCP, UDP, GRE, ICMPv6, IL, and many generic IP protocol numbers.

Filters support source, destination, either address, and protocol. `v6hdrlen` walks hop-by-hop, routing, fragment, and destination extension headers to locate the final next header and payload offset.

`p_seprint` truncates to IPv6 payload length, prints source, destination, hop limit, initial next header, and payload length, then calls `v6hdr_seprint`. That helper prints fragment-header details and advances across extension headers before demuxing to the final protocol.

Malformed extension lengths set the next protocol to `dump`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ip6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ipmux.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ipmux.c

This module decodes packets prefixed by a 16-byte interface address, then demuxes the following payload as IPv4 or IPv6 based on the high nibble of the first payload byte.

Filters support the interface address and IP type. `p_filter` consumes the 16-byte address and compares either address bytes or payload type. `p_seprint` prints interface address, type nibble, and total length, then demuxes to `ip`, `ip6`, or `dump`.

This is useful for packet sources that include an interface address before raw IP payloads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ipmux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ippkt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ippkt.c

This module is a raw IP packet discriminator. It has no extra header; it inspects the high nibble of the first byte and demuxes to IPv4 for `0x40` or IPv6 for `0x60`.

Filters support type nibble comparisons or protocol-name shorthand `ip` and `ip6`. `p_seprint` prints the detected type and sets the next protocol accordingly.

It is the simplest root for raw IP packet streams.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ippkt.c -->