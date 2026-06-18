# Group Research: group_1595_plan9_sources_os_plan9_plan9_sys_src_cmd_ip_ppp_testppp_c_sources_o_5c05a919e66c

Scope: `Docs/research_subset_a.md` source tree `sources/os/plan9/plan9`. All listed files were read completely and are reported below in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/testppp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/testppp.c

Small PPP test harness that creates two Plan 9 IP stacks, launches two `ppp` instances, and shuttles bytes between them through pipes.

Key behavior:
- Parses test flags for compression, IP compression, PPP framing, MTU, debug level, packet error rate, packet drop rate, and alternate PPP executable.
- `pppopen()` forks and execs the PPP daemon with one side bound to `/net.alt2` and the other to `/net.alt`.
- `xfer()` forks transfer loops in both directions, optionally corrupting bytes or dropping packets using `lnrand()`.
- Debug mode prints short packet previews with printable characters and hex bytes.

Integration:
- Exercises `/bin/ip/ppp` or a provided PPP binary via standard input/output.
- Uses Plan 9 `bind("#I*", ...)` to create alternate network mounts.

Risks and notes:
- Intended as a destructive/fault-injection test tool, not production code.
- `pppopen()` exits with `exits(0)` on fork failure, which hides failure status.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/testppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thw.c

PPP integration layer for the THWACK compressor/decompressor.

Key behavior:
- Defines compressor state `Cstate` and decompressor state `Uncstate`.
- Exposes `Comptype cthwack` and `Uncomptype uncthwack` hooks for the PPP stack.
- `comp()` prepends compressed PPP protocol and optional acknowledgment fields, calls `thwack()`, and falls back to uncompressed packets when compression is not worthwhile or MTU would be exceeded.
- `uncomp()` decodes THWACK packet classes: compressed, uncompressed, and uncompressed-add-to-window.
- Maintains ack sequence/mask feedback from decompressor to compressor.
- Issues LCP reset requests on decompression corruption and processes reset acks to reactivate the decompressor.

Integration:
- Depends on `ppp.h` block/LCP helpers and `thwack.h` compressor primitives.
- Uses PPP CCP data protocol `Pcdata`.
- Interacts with peer reset packets through `alloclcp(Lresetreq/Lresetack, ...)`.

Risks and notes:
- Header space is assumed available and calls `sysfatal()` if not.
- Corruption handling deactivates decompression until reset acknowledgment.
- Acks are protected with `QLock`, but sequence state is simple and assumes PPP control flow correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.c

THWACK encoder implementation, a compact LZ77-like compressor with acknowledged history windows.

Key behavior:
- `thwackinit()` resets hash/history slots and frees retained blocks.
- `thwackcleanup()` frees retained encoder blocks.
- `thwackack()` marks transmitted history blocks as safe for future references based on a sequence number and bitmask.
- `thwack()`:
  - Adds the current source block into the encoder window.
  - Builds a history set from recently acknowledged blocks.
  - Emits sequence delta and history mask.
  - Finds repeated strings through per-block hash tables.
  - Encodes literals with adaptive literal history and matches with variable-length length/offset codes.
  - Rejects output when it is larger than the destination unless `mustadd` forces dictionary insertion.

Integration:
- Used by `thw.c` as the PPP compressor.
- Uses `Block` ownership: the compressor retains successful source blocks in `tw->data`.

Risks and notes:
- Compression assumes source blocks are at most `ThwMaxBlock`.
- `mustadd` can cause dictionary insertion even when output is not useful.
- Retained `Block*` ownership is subtle and must align with PPP block lifetime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.h

Shared THWACK compressor/decompressor declarations and constants.

Key contents:
- Defines limits: `ThwMaxBlock`, hash size, minimum match, encoder/decoder window sizes, sequence-mask sizes, and stats count.
- `ThwBlock` stores encoder history metadata, hash table pointer, and source data pointer.
- `Thwack` stores encoder lock, current slot, block metadata, per-slot hash tables, and retained source `Block*`.
- `UnthwBlock` and `Unthwack` store decoder history and fixed decode buffers.
- Declares encoder/decoder APIs: init, cleanup, encode, ack, decode, state, and add-uncompressed-block.

Integration:
- Included by PPP THWACK integration and encoder/decoder implementations.
- Depends on Plan 9 `Block` and `QLock` types via including contexts.

Risks and notes:
- The constants encode the wire format assumptions; compressor and decompressor must stay in lockstep.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/thwack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/unthwack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/unthwack.c

THWACK decompressor implementation.

Key behavior:
- `unthwackinit()` clears decoder state and points block data fields at fixed storage.
- `unthwackstate()` returns the newest sequence and bitmask of nearby available history blocks for compressor acknowledgments.
- `unthwackinsert()` inserts decoded blocks into sequence-ordered history, rotating the decode window.
- `unthwackadd()` stores an uncompressed block in decoder history.
- `unthwack()`:
  - Validates compressed block size.
  - Reconstructs history block set from sequence delta and mask.
  - Decodes adaptive literals, variable-length match lengths, and match offsets.
  - Copies reconstructed output to caller buffer and inserts it into history.
  - Writes human-readable decode errors into `ut->err`.

Integration:
- Called by `thw.c` decompression path.
- Wire-format counterpart to `thwack.c`.

Risks and notes:
- Detects common corruption modes: missing history, output overflow, offset/length invalidity, compressed overrun.
- Uses static maximum block sizes and fixed per-window buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/unthwack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pppoe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pppoe.c

User-level PPP over Ethernet client for RFC 2516 discovery and session framing.

Key behavior:
- Parses PPPoE client options for access concentrator, service name, PPP net mount, MTU, keyspec, primary route, and debug.
- Builds PADI and PADR discovery packets with service-name, AC-name, and optional AC-cookie tags.
- Reads discovery replies with alarm-based exponential timeout.
- Selects matching PADO/PADS packets by service name and optional access concentrator name.
- After session establishment, creates a pipe:
  - One child reads PPP bytes, wraps them in PPPoE session Ethernet frames, and writes to the Ethernet session fd.
  - Another child reads PPPoE session frames, validates session id/code/type, and writes payload bytes to PPP.
- `execppp()` execs `/bin/ip/ppp` with `-F`, MTU, and optional auth/network flags.

Integration:
- Uses Plan 9 `dial()` on Ethernet packet types `0x8863` and `0x8864`.
- Hands a byte stream to `/bin/ip/ppp`.

Risks and notes:
- Packet validation checks type/length but not all PPPoE tag semantic errors.
- Discovery state is global.
- Debug helpers dump packet headers, tags, and optional hexdumps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pppoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pptp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pptp.c

PPTP client that negotiates the control channel, carries PPP over GRE, and launches Plan 9 PPP.

Key behavior:
- Uses libthread and Plan 9 processes/channels for control, GRE receive, PPP receive, and timer loops.
- Implements RFC 2637 control operations for start, echo, call-out request/response, and stop-on-fatal.
- `pptpctlproc()` reads length-prefixed control messages, validates magic/type, responds to echo requests, and forwards expected replies through a channel.
- `grereadproc()` validates GRE source/destination/protocol, records ACKs, reorders a single swapped packet pair, writes PPP payloads to the PPP pipe, and schedules ACKs.
- `pppreadproc()` wraps outgoing PPP payloads in GRE/PPTP headers with sequence and ack numbers.
- `gretimeoutproc()` drives ticks, server timeout, and echo requests.
- `pushppp()` forks `/bin/ip/ppp -C -m1450` on the tunnel stream.

Integration:
- Dials TCP service `pptp`, derives local/remote IPs from the TCP connection directory, then dials GRE toward the peer.
- Uses `/bin/ip/ppp` for PPP negotiation/authentication.

Risks and notes:
- `waitacks()` is disabled by comments, so outgoing send-window enforcement is effectively inactive.
- `tcallout()` appears to read `remid` and `remwin` from the transmit packet rather than the received reply, which is suspicious.
- GRE ACK-only packet writes use `hnputs()` for an apparent sequence/ack field in `sendack()`, while other paths use long stores.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pptp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pptpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pptpd.c

PPTP server-side helper for one TCP control connection and associated GRE tunnel.

Key behavior:
- Parses PPTP control messages from stdin/stdout, validates magic/type, and handles start, stop, echo, outgoing-call, call-clear, disconnect, WAN info, and link info.
- Allocates per-call `Call` objects in a hash table with refcounting and locks.
- `callalloc()` allocates a remote PPP IP via `dhcpclient`, starts `/bin/ip/ppp -SC`, stores PPP pipe fd, and launches PPP read and GRE timeout workers.
- `greinit()` dials GRE based on TCP connection path and remote IP.
- `greread()` validates GRE headers, looks up call id, updates ACKs, writes in-order PPP payloads to the call PPP fd, drops duplicates/out-of-order packets, and sends ACKs when receive window advances.
- `pppread()` reads PPP payloads, wraps them in GRE headers with key/sequence/ack, and waits for window space with timeout.
- `timeoutthread()` kills idle control sessions.

Integration:
- Designed to be launched by a TCP listener with a Plan 9 network connection directory argument.
- Uses `/bin/ip/dhcpclient` to allocate client addresses and `/bin/ip/ppp` to run PPP.
- Logs to syslog facility `pptpd`.

Risks and notes:
- `scallreq()` and `scallcon()` are explicitly unimplemented.
- `secho()` writes result byte into `p[16]` rather than response `buf[16]`, likely a bug.
- GRE packet handling has optional artificial drop support via `-D`.
- Refcounting is manual; correct `callfree()` pairing is essential.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/pptpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rarpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rarpd.c

Reverse ARP daemon for Plan 9 network boot support.

Key behavior:
- Opens NDB, Ethernet RARP packet stream, local IP, local Ethernet address, and optional `/net/arp`.
- Daemonizes, then reads RARP packets.
- Validates packet size and request opcode.
- Looks up target Ethernet address in NDB to obtain the client IP.
- Converts request into RARP reply, fills server hardware/protocol address, and writes a 60-byte Ethernet frame.
- Optionally updates the local ARP table with the client Ethernet/IP mapping.

Integration:
- Uses NDB lookup through `ndbipinfo()`.
- Uses EtherType `0x8035`.
- Uses Plan 9 network mount selected by `-x`.

Risks and notes:
- The packet opcode check uses byte-level logic for RARP request/reply.
- `lookup()` has a static local `Ndb *db` that shadows the global `db`, reopening the default database instead of using the configured one.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rarpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rexexec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rexexec.c

Authenticated remote command executor intended to be run by `listen`.

Key behavior:
- Authenticates on stdin/stdout using `auth_proxy()` with `proto=p9any role=server`.
- Rejects authenticated user `none`.
- Changes uid/name space with `auth_chuid()`.
- Reads a NUL-terminated command from stdin into an 8192-byte buffer.
- Sets `service=rx` and execs `/bin/rc -lc <command>`.

Integration:
- Relies on Plan 9 auth server and listen-service fd wiring.

Risks and notes:
- Remote command execution is intentional but high privilege; security rests on auth_proxy/auth_chuid.
- Full buffer without NUL forces final byte to NUL.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rexexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rip.c

RIP v1 routing daemon for IPv4 routes.

Key behavior:
- Reads interfaces and existing routes from Plan 9 `/net/iproute`.
- Opens UDP port `rip` in header mode.
- Receives RIP response packets, ignores packets from local interfaces, computes destination/mask/gateway/metric, and considers each route.
- Maintains in-memory route hash with fixed maximum route count.
- Installs better or refreshed routes into `/net/iproute`, unless read-only mode is enabled.
- Periodically broadcasts route tables to selected interfaces/networks.
- Times out non-static routes after 10 minutes.

Integration:
- Uses Plan 9 IP interface discovery via `readipifc()`.
- Uses route control file commands `add` and `delete`.
- Supports alternate net mount via `-x`.

Risks and notes:
- RIP v1 has no authentication and weak routing security.
- Default route is protected from hijacking by comparing against the saved default.
- The “ignore our own messages” loop uses `continue` inside the interface loop, which does not skip the packet as a whole.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rlogind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rlogind.c

Compatibility wrapper for rlogin-style service startup.

Key behavior:
- Reads four NUL-terminated strings from stdin: initial error/status, remote user, local user, and terminal.
- Acknowledges by writing one NUL byte.
- Defaults empty local user to remote user.
- Logs target user and execs `/bin/ip/telnetd -n -u <user>`.

Integration:
- Delegates actual terminal/session handling to `telnetd`.
- `-n` disables telnet protocol handling in telnetd.

Risks and notes:
- Trusts incoming rlogin identity enough to pass `-u`; telnetd authentication/trust flags determine security.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/rlogind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoe.c

`snoopy` decoder for ATA over Ethernet common header.

Key behavior:
- Parses AoE version/flags, error, major, minor, command, and tag.
- Filters on shelf, slot, or command.
- Demuxes commands to `aoeata`, `aoecmd`, `aoemask`, or `aoerr`.
- Formats header fields as version, flags, error, major.minor, command, and tag.

Integration:
- Reached from Ethernet EtherType `0x88a2`.
- Shares the common `Proto` interface.

Risks and notes:
- Filter field labels appear swapped: `shelf` maps to minor and `slot` maps to major.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoeata.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoeata.c

`snoopy` decoder for AoE ATA command payloads.

Key behavior:
- Parses ATA flag, feature/error, sector count, command/status, and 48-bit LBA.
- Filters on flag, command, feature, sectors, LBA, status, or error.
- Formats ATA fields and terminates protocol walk.

Integration:
- Selected by `aoe.c` command demux value `0`.

Risks and notes:
- Status/error filtering is noted in code as wrong because direction is not available.
- LBA filter stores into `vlv`, but generic numeric compile path primarily uses `ulv`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoeata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoecmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoecmd.c

`snoopy` decoder for AoE config command payloads.

Key behavior:
- Parses buffer count, firmware version, sector count, config command/version nibble, and config string length.
- Filters on low-nibble config command.
- Formats fields and prints the config string payload.

Integration:
- Selected by `aoe.c` command demux value `1`.

Risks and notes:
- Prints `len` bytes from packet payload without independently clamping to remaining packet size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoecmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemask.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemask.c

`snoopy` decoder for AoE mask command wrapper.

Key behavior:
- Parses reserved byte, mask command, error, and count.
- Filters on command, error, or count.
- Demuxes command values `0` and `1` to `aoemd`.
- Formats command/error/count with small textual tables.

Integration:
- Selected by `aoe.c` command demux value `2`.

Risks and notes:
- `p_compile()` calls `compile_cmp(aoerr.name, ...)`, likely copy/paste error; should refer to `aoemask`.
- In `p_seprint()`, error-name assignment writes into `s` instead of `t`, so error label can corrupt command label.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemd.c

`snoopy` decoder for AoE mask directive entries.

Key behavior:
- Parses reserved byte, edit command, and Ethernet address.
- Filters on command or Ethernet address.
- Formats command with textual edit marker and Ethernet address.

Integration:
- Reached from `aoemask.c`.

Risks and notes:
- Ethernet address filter treats configured value as numeric `ulv`, which is awkward for 48-bit addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoerr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoerr.c

`snoopy` decoder for AoE error/list style payloads.

Key behavior:
- Parses command and Ethernet-address count.
- Filters on command, count, or contained Ethernet address.
- Formats command name, count, and up to several Ethernet addresses.

Integration:
- Selected by `aoe.c` command demux value `3`.

Risks and notes:
- Field table maps `"ea"` to `Onea` instead of `Oea`, so Ethernet-address filtering is unreachable.
- Printing loop uses `m->pe + 6*i` instead of `m->ps + 6*i`, likely invalid output.
- Loop condition `if(h->nea < i)` should likely be `i >= h->nea`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoerr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/arp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/arp.c

`snoopy` ARP/RARP decoder.

Key behavior:
- Parses standard Ethernet/IPv4 ARP fields.
- Filters on source/target protocol address or hardware address.
- Formats opcode, protocol/hardware lengths, protocol addresses, and Ethernet addresses.
- Defines both `Proto arp` and `Proto rarp` using the same implementation.

Integration:
- Reached from Ethernet demux for ARP and RARP placeholder.

Risks and notes:
- Hardware-address comparisons use packet `hln` as comparison length, so malformed large `hln` can over-read filter address storage conceptually.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/arp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/bootp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/bootp.c

`snoopy` BOOTP decoder and DHCP/Plan 9 BOOTP demux.

Key behavior:
- Parses BOOTP fixed header including op, hardware fields, xid, flags, client/server/gateway addresses, hardware address, server name, boot file, and option magic.
- Filters on client address, server address, or option magic.
- Demuxes generic DHCP magic to `dhcp`, Plan 9 magic to `plan9bootp`, otherwise dump.
- Formats fixed BOOTP metadata and optional server/file strings.

Integration:
- Reached from UDP port 67 demux.

Risks and notes:
- Uses a minimum check up to `sname`, not full fixed BOOTP header, before accessing later fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/bootp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/cec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/cec.c

`snoopy` decoder for CEC packets.

Key behavior:
- Parses type, connection, sequence, and length.
- Filters on those fields.
- Formats type name and payload string.

Integration:
- Reached from Ethernet EtherType `0xbcbc`.

Risks and notes:
- Filter cases for `conn`, `seq`, and `len` use assignment (`=`) instead of comparison, mutating packet fields and always returning the assigned value.
- `p_compile()` reports unknown fields under the `aoe` protocol name, likely copy/paste.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/cec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dat.h

Core data model for `snoopy` protocol decoding and filtering.

Key contents:
- Network byte-order helper macros `NetS`, `Net3`, and `NetL`.
- `Proto`: protocol module callbacks for compile/filter/format, mux table, fields, and framer.
- `Mux`: maps protocol values to next protocol names and resolved `Proto*`.
- `Field`: filterable field metadata.
- `Msg`: mutable packet walk state and output buffer state.
- `Filter`: parsed filter AST node plus compiled protocol-specific comparison data.
- Declares shared parser/compiler/demux/framer APIs and global flags.

Integration:
- Included by every `snoopy` module.
- Used by yacc grammar and main filter optimizer.

Risks and notes:
- `Filter` stores numeric, vlong, and byte-array values in a union; field compile code must choose the right member consistently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dhcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dhcp.c

`snoopy` DHCP option formatter.

Key behavior:
- Walks DHCP option TLVs after BOOTP magic.
- Recognizes DHCP message type, requested IP, lease, server id, message, max message size, client id, parameter request list, vendor class, and many BOOTP options.
- Formats addresses, integers, strings, or hex depending on option type.
- Stops on option `255` and skips pads.

Integration:
- Reached from `bootp.c` when option magic is generic DHCP.

Risks and notes:
- No compile/filter callbacks; formatter only.
- Some printed labels contain typos, e.g. `discovermsak` and `rousupplymaskter`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dhcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dns.c

`snoopy` DNS decoder using Plan 9 NDB DNS conversion routines.

Key behavior:
- Calls `convM2DNS()` to parse DNS wire messages into `DNSmsg`.
- Formats DNS id/flags, then exposes pseudo-protocol stages for question, answer, authority, and additional records.
- `fmtrr()` prints RR owner/type/TTL and type-specific data for common RR types.
- Supplies local implementations/stubs required by imported DNS code: `dnlookup`, `rralloc`, `rrfree`, `rrfreelist`, `dnslog`, and allocation helpers.
- Maintains a temporary DN list and frees it when a message walk completes.

Integration:
- Reached from TCP/UDP port 53 demux.
- Includes `../../ndb/dns.h` and copies resource-record helper code from `ndb/dn.c`.

Risks and notes:
- Uses a static `DNSmsg dm`, so decoding state is global and not reentrant.
- `rrfree()` contains `assert(rp->magic = RRmagic)`, assignment rather than comparison, copied from source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dump.c

Fallback `snoopy` payload formatter.

Key behavior:
- Prints up to `Nflag` bytes.
- Chooses escaped printable text if all bytes are printable/space, otherwise hex.
- Terminates protocol walk.

Integration:
- Used as default demux target for unknown protocols and payload tails.

Risks and notes:
- Leaves `m->ps` unchanged while setting `m->pr=nil`; this is fine for terminal formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap.c

`snoopy` Extensible Authentication Protocol decoder.

Key behavior:
- Parses EAP code, id, length, and optional request/response type.
- Demuxes request/response subtypes to identity, notify, nak, MD5, OTP, GTC, TTLS, expanded, or experimental handlers.
- Formats EAP operation name, id, type, and length.
- Implements `eap_identity` pseudo-protocol formatter for identity/prompt/options payloads.

Integration:
- Reached from `eapol.c`.
- `eap_identity.c` is only a placeholder; real symbol lives here.

Risks and notes:
- Context is lost for identity request vs response, so identity payloads are interpreted uniformly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap_identity.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap_identity.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that EAP identity support is implemented in `eap.c`.

Integration:
- Exists so build/protocol lists can reference `eap_identity.c` while the actual `Proto eap_identity` definition is in `eap.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eap_identity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol.c

`snoopy` EAP over LAN decoder.

Key behavior:
- Parses EAPOL version, type, and payload length.
- Filters/demuxes EAPOL packet type: EAP, start, logoff, key, ASF alert.
- Truncates message to EAPOL payload length and formats type/version/data length.

Integration:
- Reached from Ethernet EtherType `0x888e`.
- Demuxes key packets to `eapol_key`.

Risks and notes:
- Start/logoff/asf alert fall back to dump unless corresponding protocol exists.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol_key.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol_key.c

`snoopy` EAPOL-Key decoder and RC4 key descriptor formatter.

Key behavior:
- Parses key descriptor type and demuxes descriptor type `1` to `rc4keydesc`.
- `rc4keydesc` formatter parses key length, replay counter, IV, index, digest, and trailing data length.

Integration:
- Reached from `eapol.c` type `Key`.
- `rc4keydesc.c` is a placeholder; real `Proto rc4keydesc` is here.

Risks and notes:
- Several multi-byte RC4 descriptor fields are wider than `NetS()` output shown by formatter, so printed replay/IV/MD values are abbreviated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol_key.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ether.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ether.c

`snoopy` Ethernet decoder.

Key behavior:
- Parses Ethernet destination, source, and type.
- Filters on source, destination, either address, or EtherType.
- Demuxes to IPv4, ARP/RARP, IPv6, PPPoE discovery/session, EAPOL, AoE, and CEC.
- Formats source/destination/type/packet length.

Integration:
- Default root protocol for Ethernet packet capture and trace files.

Risks and notes:
- RARP maps to the same EtherType as ARP in this file, even though RARP commonly uses `0x8035`; may be historical or erroneous in this decoder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ether.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/filter.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/filter.y

Yacc grammar and lexer for `snoopy` filter expressions.

Key behavior:
- Supports protocol words, field equality, inequality, grouping, negation, AND, and OR.
- Builds `Filter` AST nodes using `newfilter()`.
- Lexer splits on `!|&()= ` and recognizes `!=`, `&&`, and `||`.
- `yyinit()` sets the input filter string.
- `yyerror()` exits with a parse error.

Integration:
- `main.c` compiles and optimizes the resulting `filter` tree.

Risks and notes:
- Lexer delimiter list does not include tabs as token separators, though leading whitespace uses `isspace()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/filter.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/gre.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/gre.c

`snoopy` GRE decoder for RFC 1701/2784 and PPTP-style GRE.

Key behavior:
- Parses GRE flags, protocol, optional checksum/offset, key, sequence, ack, and routing blocks.
- Filters/demuxes on encapsulated protocol.
- Demuxes common encapsulated protocol values including IP, ARP, PPP, EAPOL, and VLAN.
- Formats version, protocol, flags, and present optional fields.

Integration:
- Reached from IPv4/IPv6 protocol number 47.

Risks and notes:
- `parthdrlen()` has operator-precedence problems; as written it likely returns `4` for most flag combinations instead of adding optional field sizes.
- Routing skip loop does not advance past the final zero-length routing marker.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/gre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/hdlc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/hdlc.c

`snoopy` HDLC/PPP framing decoder and framer.

Key behavior:
- Contains PPP FCS lookup table and HDLC frame constants.
- `p_framer()` reads byte stream until frame delimiter, unescapes bytes, validates PPP FCS, and returns a decoded frame.
- Decoder recognizes PPP address/control bytes and demuxes to `ppp`.
- Formats no additional fields beyond advancing past address/control.

Integration:
- Can be selected as root protocol/framer for HDLC byte streams.

Risks and notes:
- Bad FCS frames are printed to stdout and skipped.
- Static input buffer makes the framer stateful and non-reentrant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/hdlc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp.c

`snoopy` ICMPv4 decoder.

Key behavior:
- Parses ICMP type, code, checksum, and type-specific payload.
- Filters on ICMP type or embedded IP-bearing error messages.
- Demuxes error messages containing original IP header back to `ip`.
- Formats type names, echo id/sequence, timestamp fields, redirect gateway, and parameter pointer.
- Optional checksum verification when `Cflag` is set.

Integration:
- Reached from IPv4 protocol number 1.

Risks and notes:
- `p_seprint()` advances before checking minimum remaining size, but still catches short packets later.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp6.c

`snoopy` ICMPv6 and neighbor-discovery decoder.

Key behavior:
- Parses ICMPv6 type, code, checksum, and data.
- Filters on type or embedded IPv6-bearing error messages.
- Formats unreachable, packet-too-big, time-exceeded, parameter-problem, echo, router solicit/advert, neighbor solicit/advert, redirect, timestamp, and info messages.
- `opt_seprint()` decodes ND options: source/target link-layer, prefix information, redirect, and MTU.
- Demuxes selected errors and redirects to `ip6`.

Integration:
- Reached from IPv6 next-header 58.

Risks and notes:
- Checksum verification is present but commented out.
- Parameter-problem bounds check uses `>` rather than `>=` against `nelem(parpcode)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/il.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/il.c

`snoopy` decoder for Plan 9 IL transport packets.

Key behavior:
- Parses checksum, length, type, special byte, source/destination ports, id, and ack.
- Filters on source, destination, or either port.
- Demuxes selected Plan 9 service ports to `ninep`.
- Formats port/type/id/ack/checksum/length fields.

Integration:
- Reached from IPv4/IPv6 protocol number 40.

Risks and notes:
- Packet type table is small and unknown types fall back to numeric strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/il.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip.c

`snoopy` IPv4 decoder.

Key behavior:
- Parses IPv4 header, including version/IHL, TOS, length, id, fragment, TTL, protocol, checksum, source, and destination.
- Filters on source, destination, either address, or protocol number.
- Demuxes many IP protocol numbers to registered protocol names.
- Suppresses next-protocol decode for non-first fragments.
- Truncates message end to IPv4 total length and prints header options as hex.

Integration:
- Reached from Ethernet, GRE, PPP, ICMP embedded payloads, and other decoders.

Risks and notes:
- Does not validate version or minimum IHL beyond base header availability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip6.c

`snoopy` IPv6 decoder with extension-header skipping.

Key behavior:
- Parses IPv6 base header, payload length, next header, hop limit, source, and destination.
- Filters on source, destination, either address, or next-header value.
- `v6hdrlen()` walks hop-by-hop, routing, fragment, and destination extension headers.
- `v6hdr_seprint()` formats fragment extension header details and advances to final payload.
- Demuxes many next-header values including TCP, UDP, GRE, OSPF, and ICMPv6.

Integration:
- Reached from Ethernet EtherType `0x86dd`.

Risks and notes:
- Demux uses original base `proto`, not necessarily final next header after extension headers, so extension-header packets may be routed to the wrong decoder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/main.c

Main program for the `snoopy` packet sniffer.

Key behavior:
- Parses options for pcap/trace output, filter expression, root protocol, packet byte limit, promiscuous mode, trace input/output, checksum flag, and compact printing.
- Opens live Ethernet, IP interface snoop, trace file, or arbitrary file input.
- Builds protocol graph by resolving each module’s mux table to `Proto*`, creating dump-like placeholder protocols for unknown names.
- Compiles filter AST:
  - Completes omitted intermediate protocols via graph search.
  - Optimizes repeated protocol nodes and constant cases.
  - Calls protocol-specific compile hooks.
  - Rejects filters whose top-level protocol does not match the root.
- Applies filters by walking packet state through protocol filter callbacks.
- Prints decoded packets by repeatedly calling protocol `seprint` callbacks until no next protocol remains.
- Writes Plan 9 trace or pcap output when requested.

Integration:
- Central coordinator for every `snoopy` protocol module.
- Uses `filter.y` parser, `protos.h` protocol list, and Plan 9 network devices.

Risks and notes:
- Allocates packet buffer then shifts by 16 bytes without retaining original malloc pointer.
- Filter walk mutates `Msg.ps`; boolean branches copy state only for selected operators.
- Pcap timestamp structure uses a single `uvlong ts`, not the conventional separate sec/usec pair.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ninep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ninep.c

`snoopy` 9P message formatter.

Key behavior:
- Uses `convM2S()` to decode a 9P message into `Fcall`.
- Formats decoded message with `%F`.
- Replaces newlines in formatted output with backslashes.
- Falls back to `dump.seprint()` if 9P decode fails.

Integration:
- Reached from TCP/IL/UDP service-port demux entries.

Risks and notes:
- Terminal decoder only; no filtering fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ninep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ospf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ospf.c

`snoopy` OSPF packet formatter.

Key behavior:
- Parses OSPF common header and prints version, type, length, router, area, checksum, and authentication summary.
- Formats hello packets, database-description LSA headers, link-state updates, and link-state acknowledgments.
- Includes structures for router, network, summary, and AS-external LSAs.
- Falls back to hex dump for unsupported or unexpected payloads.

Integration:
- Reached from IPv4/IPv6 protocol number 89.

Risks and notes:
- No filter/compile callbacks.
- Length validation appears inverted: if OSPF header length is less than captured length, it returns short/error rather than truncating extra bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ospf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp.c

`snoopy` PPP decoder plus PPP control-protocol formatters.

Key behavior:
- Parses optional PPP address/control compression and compressed protocol field.
- Demuxes PPP protocol IDs to IP, VJ TCP, multilink, compressed, IPCP, CCP, password auth, LCP, LQM, and CHAP.
- Formats base PPP protocol and frame length.
- Implements pseudo-protocols:
  - `ppp_lcp`: LCP codes and options such as MTU, control map, auth, quality, magic, protocol/address compression.
  - `ppp_ipcp`: IPCP address/compression/DNS/WINS options.
  - `ppp_ccp`: CCP options and reset packets.
  - `ppp_chap`: CHAP challenge/response/success/failure.
  - `ppp_comp`: compressed data flags and counter.

Integration:
- Reached from HDLC, GRE PPTP, and PPPoE session decoders.
- Placeholder files for individual PPP pseudo-protocols refer back here.

Risks and notes:
- Option walkers require valid nonzero option lengths in most paths; LCP path explicitly checks zero length, IPCP/CCP only check bounds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ccp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ccp.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that CCP support is implemented in `ppp.c`.

Integration:
- Actual `Proto ppp_ccp` is defined in `ppp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ccp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_chap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_chap.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that CHAP support is implemented in `ppp.c`.

Integration:
- Actual `Proto ppp_chap` is defined in `ppp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_chap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_comp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_comp.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that PPP compressed-packet support is implemented in `ppp.c`.

Integration:
- Actual `Proto ppp_comp` is defined in `ppp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ipcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ipcp.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that IPCP support is implemented in `ppp.c`.

Integration:
- Actual `Proto ppp_ipcp` is defined in `ppp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_ipcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_lcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_lcp.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that LCP support is implemented in `ppp.c`.

Integration:
- Actual `Proto ppp_lcp` is defined in `ppp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ppp_lcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_disc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_disc.c

`snoopy` PPPoE discovery/session decoder.

Key behavior:
- Parses PPPoE version/type, code, session id, and payload length.
- Defines shared filtering fields for version, type, code, and session id.
- `pppoe_disc` prints discovery header and terminates walk.
- `pppoe_sess` prints session header and demuxes payload to PPP.

Integration:
- Reached from Ethernet EtherTypes `0x8863` and `0x8864`.
- `pppoe_sess.c` is only a placeholder; actual `Proto pppoe_sess` is here.

Risks and notes:
- Discovery tags are not decoded here, only the fixed PPPoE header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_disc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_sess.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_sess.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that PPPoE session support is implemented in `pppoe_disc.c`.

Integration:
- Actual `Proto pppoe_sess` is defined in `pppoe_disc.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_sess.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rarp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rarp.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that RARP support is implemented in `arp.c`.

Integration:
- Actual `Proto rarp` is defined in `arp.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rarp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rc4keydesc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rc4keydesc.c

Placeholder translation unit.

Key behavior:
- Contains only the comment that RC4 key descriptor support is implemented in `eapol_key.c`.

Integration:
- Actual `Proto rc4keydesc` is defined in `eapol_key.c`.

Risks and notes:
- No runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rc4keydesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtcp.c

`snoopy` RTCP sender-report style formatter.

Key behavior:
- Parses RTCP header, packet type, report length, sender SSRC, NTP/RTP timestamps, packet count, and octet count.
- Iterates reception report blocks and formats source, loss fraction, cumulative lost, highest sequence, jitter, last sender report, and delay since last sender report.
- Terminates protocol walk.

Integration:
- Reached from UDP demux when selected by filter/default protocol path.

Risks and notes:
- Assumes sender-report layout with 28-byte minimum, so other RTCP packet types are not generally decoded correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtp.c

`snoopy` RTP formatter.

Key behavior:
- Parses RTP version, extension bit, CSRC count, sequence, timestamp, and SSRC.
- Prints each CSRC when present.
- Terminates protocol walk.

Integration:
- Reached from UDP demux when selected.

Risks and notes:
- Does not decode marker, payload type, extension header, padding, or payload.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/rtp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/tcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/tcp.c

`snoopy` TCP decoder.

Key behavior:
- Parses source/destination ports, sequence, ack, flags/header length, window, checksum, urgent pointer, and options.
- Filters on source, destination, or either port.
- Demuxes selected ports to DNS and 9P.
- Formats flags and common options: MSS, window scale, EOL, NOOP, and generic options.

Integration:
- Reached from IPv4/IPv6 TCP protocol numbers.

Risks and notes:
- Header length is computed from flag word; short/malformed header length can advance `m->ps` inconsistently.
- Checksum is printed but not verified.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ttls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ttls.c

`snoopy` EAP-TTLS payload header formatter.

Key behavior:
- Parses TTLS flags and optional total length field.
- Prints version bits, S/M/L flag letters, optional total length, remaining data length, and ACK indication for empty no-flag packets.
- Demuxes remainder to dump so payload bytes are visible.

Integration:
- Reached from EAP subtype TTLS.

Risks and notes:
- Only handles TTLS outer flag/length wrapper; no TLS decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ttls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/udp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/udp.c

`snoopy` UDP decoder.

Key behavior:
- Parses source port, destination port, UDP length, and checksum.
- Filters on source, destination, or either port.
- Demuxes DNS, BOOTP, selected 9P-over-UDP, and optionally RTP/RTCP via `ANYPORT`.
- Formats ports, checksum, and length.

Integration:
- Reached from IPv4/IPv6 UDP protocol numbers.

Risks and notes:
- `defproto` is global mutable state used to support arbitrary-port RTP/RTCP selection during filtering.
- Checksum is printed but not verified.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/udp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.c

Plan 9 telnet client.

Key behavior:
- Dials target TCP telnet service and optionally posts a pipe in `/srv`.
- Uses shared memory for communication flags between keyboard and network processes.
- `fromkbd()` reads local input, supports control menu on Ctrl-\ when not in binary mode, converts newline to CR/LF according to option state, and writes to network.
- `fromnet()` reads network data, handles TELNET IAC control sequences via `telnet.h`, normalizes CR/LF output when requested, and writes to screen.
- Menu supports break, interrupt, quit, return-mode toggle, option probes, shell escape, and continue.
- Sends terminal type and X display location through subnegotiation handlers.

Integration:
- Shares option negotiation implementation in `telnet.h`.
- Uses `/dev/consctl` raw mode to control local terminal behavior.

Risks and notes:
- `xlocsub()` uses `strncpy(p, term, p - buf - 2)`, a negative/incorrect bound expression, likely a bug.
- Uses two cooperating processes and notes to terminate peers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.h

Shared TELNET protocol constants, option table, and negotiation helpers.

Key behavior:
- Defines TELNET command bytes and option numbers.
- Defines `Opt` with name, code, refusal flag, change/subnegotiation callbacks, and local/remote state.
- Implements control dispatch for IAC commands: WILL, WONT, DO, DONT, SB, AYT, SE.
- Negotiates option state and sends reciprocal replies.
- Parses subnegotiation payloads and invokes option-specific handlers.
- Provides robust read/write wrappers that handle interrupted syscalls, note sending, simple fatal/error helpers, and debug output.

Integration:
- Included directly by both telnet client and telnet daemon.
- Expects including file to provide `Biobuf`, `debug`, and option callback configuration.

Risks and notes:
- Header contains function definitions and global `opt[]`, so it is intended for direct inclusion into individual binaries, not normal shared compilation.
- `sub()` silently truncates subnegotiation payloads longer than 128 bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnet.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnetd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/telnetd.c

Plan 9 telnet daemon and remote login shell launcher.

Key behavior:
- Parses flags to disable protocol, allow `none`, trust current user, set user, enable debug, or restrict to noworld accounts.
- Sends initial TELNET negotiation for echo, terminal type, and X display unless protocol is disabled.
- Authenticates through Plan 9 challenge/response or noworld password login; trusted mode uses current user.
- Creates shared console state and simulates `/dev/cons` plus `/dev/consctl` using pipes/binds.
- Forks an interactive `/bin/rc -il` in a separate process group with simulated console fds.
- Runs two data pumps:
  - `fromchild()` converts child output newline to CR/LF when not raw.
  - `fromnet()` handles TELNET protocol/control characters, local echo, cooked editing, EOF, and interrupt notes.
- Handles terminal type and X display subnegotiation by setting `TERM` and `DISPLAY`.

Integration:
- Invoked directly by listeners or via `rlogind`.
- Shares TELNET parser in `telnet.h`.
- Uses Plan 9 auth, namespace, and process-note mechanisms.

Risks and notes:
- `getremote()` closes fd even if `open()` failed.
- `termsub()` and `xlocsub()` use `strncpy()` without explicit NUL termination when `n == sizeof buffer`.
- Simulated console state depends on a shared segment and a helper process reading consctl commands.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/telnetd.c -->