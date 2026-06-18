# Group Research: group_1498_plan9_sources_os_plan9_plan9_sys_src_cmd_acme_wind_c_sources_os_pla_a5dc59001c2a

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/plan9/plan9`, which is in subset A. I read the listed source files completely from the checkout. Note: the checked-out `smblisten.c` reports 154 lines by `wc`, while the prompt lists 155.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/wind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/wind.c

Implements Acme `Window` lifecycle, layout, tag maintenance, dirty-state presentation, and event buffering.

Key functions:
- `wininit` initializes tag/body `Text` structures, clone state, fonts, scroll/button drawing, file menu, and dirty/scratch flags.
- `winresize` lays out the tag, border, body, and modified button, while preserving maximum body line tracking.
- `winlock`, `winunlock`, and `winclose` coordinate reference counting and locking across all windows sharing the same body file.
- `winsettag1` reconstructs the tag command prefix (`Del`, `Snarf`, `Undo`, `Redo`, `Put`, `Get`, `Look`) and preserves user selection around the `|`.
- `wincommit` commits cached text and treats a tag filename edit as a body file rename.
- `winevent` appends owner-tagged event text and wakes a pending event reader.

Interactions:
- Depends on Acme `Text`, `File`, `Column`, `Row`, `rfget`, `fileaddtext`, `textresize`, `textinsert`, `textdelete`, and `fileundo`.
- Works with `xfid.c` via `eventx`, `events`, `ctlfid`, `nopen`, and window control/event files.

Notable details:
- `winunlock` walks shared text windows backward because closing one window can mutate the shared `File` text list.
- Scratch windows include `/guide` and `+Errors`; they are exempt from dirty-close warnings.
- Include directories are stored as front-inserted rune strings after validation with `dirstat`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/xfid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/xfid.c

Implements Acme filesystem fid operations for window pseudo-files: open, close, read, write, flush, event I/O, address I/O, and index reads.

Key functions:
- `xfidctl` is the worker loop receiving operation functions on an `Xfid` channel.
- `xfidopen` initializes per-qid state for `addr`, `data`, `xdata`, `event`, `rdsel`, `wrsel`, and `editout`.
- `xfidclose` reverses open state, releases exclusive ctl locks, restores menus, closes temp selection fds, and decrefs windows.
- `xfidread` dispatches reads for window body/tag text, control metadata, addr, data, selected text, event stream, and global index.
- `xfidwrite` dispatches writes to console, label, addr, editout, errors, body, selected text, ctl, data, events, and tag.
- `xfidctlwrite` parses textual control commands such as `lock`, `unlock`, `clean`, `dirty`, `show`, `name`, `dump`, `dumpdir`, `delete`, `del`, `get`, `put`, `dot=addr`, `addr=dot`, `limit=addr`, `nomark`, `mark`, `nomenu`, `menu`, `noscroll`, `cleartag`, and `scroll`.
- `xfideventread` blocks on window event availability and handles flush/shutdown wakeups.
- `xfidutfread`, `xfidruneread`, and `fullrunewrite` preserve UTF-8/rune boundaries.

Interactions:
- Uses `Window` state from `wind.c`, including `addr`, `limit`, `events`, `eventx`, `nopen`, `wrselrange`, `filemenu`, and dirty flags.
- Calls Acme editing/search helpers such as `address`, `execute`, `look3`, `edittext`, `cut`, `get`, and `put`.

Notable details:
- Read selection uses a temp file rather than a pipe to avoid broken-pipe behavior and mutation races.
- UTF reads cache the last byte/rune offset per qid to avoid always rescanning from the beginning.
- Event writes encode actions through Acme’s external event protocol and execute/look selected tag/body regions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/acme/xfid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/addname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/addname.c

Implements NBNS name registration through `nbnsaddname`.

Key behavior:
- Builds a name registration request with `nbnsmessagenameregistrationrequestnew`.
- Uses `NbnsAlarm` plus a transaction response channel in an `Alt` loop.
- Retries `NbnsRetryBroadcast` times with `NbnsTimeoutBroadcast` timeout.
- Accepts only NBNS registration responses and returns the NBNS rcode, `0`, or `-1`.

Interactions:
- Depends on `message.c`, `nbns.c`, `alarm.c`, and `nbnsconv.c`.
- Broadcast mode is selected when `serveripaddr == nil`.

Notable details:
- Frees the transaction before leaving the response loop.
- Frees both request and response messages before returning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/addname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/alarm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/alarm.c

Provides timer support for NBNS request retry/timeout logic.

Key functions:
- `alarmist` is a process that scans an ordered alarm list, sends on expired channels, and sleeps until the next deadline.
- `nbnsalarmnew` allocates an alarm and buffered channel.
- `nbnsalarmset` cancels any existing placement, computes expiry in milliseconds, inserts by expiry order, and starts/interrupts the alarm process.
- `nbnsalarmcancel` removes an alarm from the list and drains pending channel messages.
- `nbnsalarmend` asks the alarm process to exit.
- `nbnsalarmfree` cancels, frees the channel, and clears the pointer.

Interactions:
- Used by `findname.c` and `addname.c`.

Notable details:
- Uses `QLock` around the global list.
- `threadint` is used to wake the sleeping alarm process when deadlines change.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/alarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/alloc.c

Defines `nbemalloc`, the NetBIOS allocation wrapper.

Key behavior:
- Calls `malloc`.
- On allocation failure, prints an error and exits all threads with status `mem`.

Interactions:
- Used throughout NetBIOS and SMB support as the lower-level fatal allocator.
- `smballoc.c` builds SMB allocators on top of it.

Notable details:
- Does not zero memory; callers requiring zeroing use wrappers such as `smbemallocz` or `mallocz`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/aquarela.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/aquarela.c

Main SMB/CIFS server entry point and per-session request dispatcher for Aquarela.

Key functions:
- `smbsessionwrite` parses an SMB request, validates session state, dispatches through `smboptable`, translates process results into SMB errors/replies, sends responses, and frees sessions on shutdown.
- `smbsessionfree` releases tree/search id maps, buffers, transaction storage, auth challenge state, and client strings.
- `nbssaccept` and `cifsaccept` allocate `SmbSession` objects for NetBIOS session service and direct CIFS transports.
- `logset` enables command-specific and subsystem debugging.
- `threadmain` parses options, initializes globals, starts direct CIFS listening, optionally starts NetBIOS service/listeners, and periodically sends browser host announcements.

Interactions:
- Central consumer of `smboptable`, `smbbuffer`, `smbresponse`, `nbss`, `smblisten`, `smbbrowse`, and authentication/session setup code.
- Uses id-map cleanup callbacks to close trees and searches.

Notable details:
- Only negotiate, session setup, tree connect, and echo are allowed before the session is established.
- Supports `-n` to enable NetBIOS in addition to direct CIFS.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/aquarela.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/cifscmd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/cifscmd.c

Interactive SMB client command tool focused on testing remote operations.

Key functions:
- `tokenise` and `parse` split command lines, including single-quoted strings and doubled embedded quotes.
- `cmdhelp` prints command help.
- `cmdopen` maps textual share/open modes and calls `smbclientopen`.
- `threadmain` optionally connects to a server/share, reads commands from stdin, dispatches them, and writes status to stdout.

Interactions:
- Uses `smbconnect` for connection setup and `smbclientopen` for file open testing.
- Uses local mode lookup tables similar to server-side `smbopenmodeslut` and `smbsharemodeslut`.

Notable details:
- Currently exposes only `help` and `open`.
- Prints parsed argument count unconditionally through `Bprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/cifscmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/client.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/client.c

Standalone NetBIOS name registration client.

Key functions:
- `warning` logs to syslog and optionally stdout.
- `udpannounce` announces the `netbios-ns` UDP service and enables Plan 9 UDP header mode.
- `listen137` reads UDP NBNS packets, decodes them, dumps them, and routes responses to matching transactions.
- `threadmain` parses optional unicast server IP, builds a NetBIOS name, initializes network/broadcast state, starts listener, and calls `nbnsaddname`.

Interactions:
- Uses NBNS transaction globals and message conversion/dump routines.
- Overlaps with the reusable `nbns.c` logic but contains its own listener-oriented test harness.

Notable details:
- The `udpannounce` write check uses `if(write(...) , 0)`, which always evaluates false; this looks like an old bug or disabled assertion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/dump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/dump.c

Debug dump helpers for NBNS messages and raw byte data.

Key functions:
- `nbnsdumpname` prints a NetBIOS name with lower-case base name and hex suffix.
- `nbnsdumpmessagequestion` and `nbnsdumpmessageresource` print typed NBNS question/resource records.
- `nbnsdumpmessage` prints header flags plus all question/answer/ns/additional sections.
- `nbdumpdata` prints hex and ASCII byte dumps in 16-byte rows.

Interactions:
- Used by NetBIOS test/client and diagnostic paths.
- Depends on NBNS constants from `netbios.h`.

Notable details:
- Resource data is printed as contiguous hex bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/findname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/findname.c

Implements NBNS name query through `nbnsfindname`.

Key behavior:
- Builds a name query request with `nbnsmessagenamequeryrequestnew`.
- Uses an `Alt` over timeout and transaction response channels.
- Retries broadcast/unicast queries.
- On success, extracts IPv4 address from NB resource rdata and converts it to Plan 9 IPv6-format IP storage.
- Optionally returns TTL.

Interactions:
- Used by `nbresolve.c` before DNS fallback.
- Shares retry/transaction/alarm flow with `addname.c`.

Notable details:
- Requires an answer record; no answer is treated as failure even if rcode is zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/findname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/headers.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/headers.h

Central include header for Aquarela SMB/NetBIOS C files.

Contents:
- Includes Plan 9 system headers: `u.h`, `libc.h`, `ip.h`, `thread.h`, `auth.h`, and `regexp.h`.
- Includes project headers: `netbios.h`, `smb.h`, `smbdat.h`, and `smbfns.h`.

Interactions:
- Most SMB server files include this instead of listing all dependencies individually.

Notable details:
- Keeps protocol constants, shared structs, and prototypes in one compilation include path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/headers.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/message.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/message.c

Constructs NBNS request message objects.

Key functions:
- `nbnsmessagenamequeryrequestnew` creates a query request with one NB question.
- `nbnsmessagenameregistrationrequestnew` creates a registration request with one NB question and an additional NB resource containing flags plus IPv4 address.

Interactions:
- Used by `findname.c` and `addname.c`.
- Uses message allocation/list helpers from `nbnsconv.c`.

Notable details:
- Registration request stores IPv4 in 6-byte rdata: two flag bytes plus four address bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nb.c

Initializes global NetBIOS state.

Key data:
- `NbGlobals nbglobals`
- `NbName nbnameany = { '*' }`

Key function:
- `nbinit` installs IP and NetBIOS-name formatters, reads `/net` interface data, records local IP, computes broadcast IP, and sets the local NetBIOS name from `sysname()`.

Interactions:
- Required before NetBIOS datagram, name service, and session service operation.

Notable details:
- Broadcast address is computed by OR-ing IP bytes with inverse mask bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgram.c

Implements NetBIOS datagram service listener registration, packet dispatch, and send support.

Key functions:
- `udplistener` reads UDP datagrams, decodes `NbDgram`, filters unsupported fragments, validates destination names, and dispatches to registered listeners.
- `startlistener` lazily announces UDP port 138.
- `nbdgramlisten` registers a destination-name listener and records local names.
- `nbdgramsendto` encodes and writes a datagram to a target IP/port.
- `nbdgramsend` resolves or broadcasts destination names and fills source/destination datagram fields.

Interactions:
- Used by SMB browser/mailslot announcements.
- Depends on `nbdgramconv.c`, `nblistener.c`, `nbname.c`, and `nbresolve.c`.

Notable details:
- Fragmented datagrams (`More` flag or nonzero offset) are ignored.
- Listener callback return values control one-shot removal or continued listening.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramconv.c

Serializes and parses NetBIOS datagram packets.

Key functions:
- `nbdgramconvM2S` decodes type, flags, id, IPv4 source, source port, and type-specific payload.
- `nbdgramconvS2M` encodes the same structure back to wire format.

Interactions:
- Called by `nbdgram.c` for receive/send paths.
- Uses `nbnameencode` and `nbnamedecode`.

Notable details:
- Direct/group/broadcast datagrams include a length fixup plus source and destination NetBIOS names.
- Error datagrams carry one code byte.
- Query response encode path uses `s->datagram.dstname` where the decode side stores query names in `s->query.dstname`; this is a structure-union sensitivity to watch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramdump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramdump.c

Debug printer for decoded NetBIOS datagrams.

Key behavior:
- Prints type, flags, id, source IP, and source port.
- For error packets, prints error code.
- For data packets, prints datagram length, offset, source name, and destination name.

Interactions:
- Uses `%I` IP formatter and `%B` NetBIOS name formatter.

Notable details:
- Does not dump datagram payload bytes; raw data dumping is handled by `nbdumpdata`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nblistener.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nblistener.c

UDP announce helper for NetBIOS services.

Key function:
- `nbudpannounce` announces `udp!*!<port>`, enables Plan 9 UDP header mode, opens the data file, stores the data fd, and sets `nbudphdrsize`.

Interactions:
- Used by NBNS and datagram listeners.

Notable details:
- Returns string literals on failure rather than setting `werrstr`.
- Leaves the announce ctl fd closed after data fd open.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nblistener.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbname.c

NetBIOS name encoding/decoding, formatting, local-name table, and remote-name cache.

Key functions:
- `nbnamedecode` and `_nameextract` parse RFC-style compressed NetBIOS names from NBNS packets.
- `nbnameencode` writes the 32-character encoded NetBIOS name plus terminator.
- `nbmknamefromstring`, `nbmknamefromstringandtype`, and `nbmkstringfromname` convert between readable names and fixed 16-byte names.
- `nbnameequal` supports wildcard matching through `*`.
- `nbnametablefind` tracks locally listened/owned names.
- `nbremotenametablefind` and `nbremotenametableadd` implement a TTL-based remote name cache.

Interactions:
- Shared by NBNS, datagram, session, and browse code.
- Installs with `%B` formatter via `nbnamefmt`.

Notable details:
- Name type is stored in byte 15 and may be specified as `\xNN`.
- `_nameextract` handles compression pointers recursively.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbns.c

Implements NBNS UDP transaction transport.

Key functions:
- `udplistener` reads UDP port 137 packets, decodes NBNS messages, and routes responses to matching `NbnsTransaction` channels.
- `startlistener` lazily announces the NBNS UDP port.
- `nbnsnextid` allocates transaction ids under a lock.
- `nbnstransactionnew` serializes a request, creates a response channel, registers it, and writes the UDP packet to broadcast or unicast target.
- `nbnstransactionfree` drains pending responses, unlinks the transaction, and frees it.

Interactions:
- Used by `findname.c` and `addname.c`.
- Depends on `nbnsconv.c`, `nblistener.c`, and `nbglobals`.

Notable details:
- Only response packets are routed; request packets are currently freed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbnsconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbnsconv.c

Owns NBNS message allocation, list management, decoding, and encoding.

Key functions:
- `nbnsmessagefree`, `questionfree`, and `resourcefree` free full message graphs.
- `nbnsmessagequestionnew` and `nbnsmessageresourcenew` allocate records and copy names/rdata.
- `nbnsconvM2S` parses the NBNS header, flags, questions, and resource sections.
- `nbnsconvS2M` writes header counts, flags, questions, and resource sections.
- `resourcedecode` and `resourceencode` handle common resource body parsing.

Interactions:
- Underpins all NBNS request/response code.

Notable details:
- On decode failure, partially built messages are freed through `nbnsmessagefree`.
- There is a likely typo in `resourcedecode`: after `r->rdata = malloc(...)`, it checks `if (r == nil)` rather than `if (r->rdata == nil)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbnsconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbresolve.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbresolve.c

Resolves NetBIOS names to IP addresses.

Key function:
- `nbnameresolve` checks the remote NetBIOS cache, queries NBNS, caches successful NBNS results by TTL, then falls back to DNS using the name without NetBIOS type byte.

Interactions:
- Used by NetBIOS session connect and direct unique datagram send.

Notable details:
- NBNS is preferred over DNS.
- DNS query uses `/net` and record type `ip`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbresolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbss.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbss.c

Implements NetBIOS session service over TCP port `netbios`.

Key functions:
- `nbsslisten` announces TCP NetBIOS service and registers called/calling name accept filters.
- `tcpreader` parses NBSS frames, handles session requests, positive/negative responses, keepalives, and session messages.
- `nbssconnect` resolves a NetBIOS name, dials TCP, sends a session request, and validates the response.
- `nbssgatherwrite` and `nbssscatterread` frame and unframe SMB payloads.
- `nbsswrite`, `nbssread`, and `nbssfree` are simple public wrappers.

Interactions:
- Server path feeds accepted SMB payloads to `smbsessionwrite` via `aquarela.c`.
- Client path used by `smbconnect.c`.

Notable details:
- Session request matching distinguishes called-name-not-present from called-name-present/calling-name-not-listened errors.
- Supports 17-bit NBSS length via low bit in flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/netbios.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/netbios.h

Defines NetBIOS/NBNS/NBSS constants, wire structs, runtime structs, globals, and function prototypes.

Major contents:
- NBNS constants for ports, retries, opcodes, flags, rcodes, question/resource types/classes.
- `NbName`, `NbnsMessageQuestion`, `NbnsMessageResource`, `NbnsMessage`, and `NbnsTransaction`.
- `NbnsAlarm` timer abstraction.
- `NbSession`, `NbScatterGather`, and session-service I/O prototypes.
- `NbDgram` and `NbDgramSendParameters`.
- Local/remote name table APIs.
- `NbGlobals` with local IP, broadcast IP, and local NetBIOS name.

Interactions:
- Included by all NetBIOS files and indirectly by most Aquarela SMB files through `headers.h`.

Notable details:
- Uses Plan 9 IPv6-format `IPaddrlen` arrays while NetBIOS wire protocol carries IPv4 addresses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/netbios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smb.h

Defines SMB wire header and protocol constants.

Major contents:
- `SmbRawHeader` matching SMB protocol header layout.
- Header flag and `flags2` capability constants.
- SMB command opcode enum.
- DOS/server/hardware/error class and error code constants.
- Capability flags.
- RAP procedure ids and server/share type constants.
- Transaction2 opcodes and find/query/set information levels.
- DOS attribute constants.
- Open mode/share mode, create disposition, desired access, share access, and create option constants.

Interactions:
- Used throughout command handlers and client/server packet construction.

Notable details:
- Covers classic SMB/CIFS era commands with many unimplemented op table entries elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smballoc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smballoc.c

SMB memory allocation helpers.

Key functions:
- `smbemallocz` allocates through `nbemalloc` and optionally zeros memory.
- `smbemalloc` is nonzeroing allocation.
- `smbestrdup` duplicates strings using fatal allocation.
- `smbfree` frees and nils a pointer.
- `smberealloc` wraps `realloc` and asserts success for nonzero sizes.

Interactions:
- Used across SMB code for small structs, strings, and dynamic arrays.

Notable details:
- Under `LEAK`, macros in `smbfns.h` can bypass these wrappers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbrowse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbrowse.c

Builds SMB browser mailslot datagrams for host announcements.

Key functions:
- `smbmailslotsend` wraps a mailslot transaction and sends it over NetBIOS datagram transport.
- `smbbrowsesendhostannouncement` builds a browser host announcement message containing period, server name, version, server type, magic value, and comment.

Interactions:
- Called periodically by `aquarela.c` when NetBIOS mode is enabled.
- Uses `smbtransactionmethoddgram` and `nbdgramsend`.

Notable details:
- Sends to the primary domain name with NetBIOS type `0x1d`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbrowse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbuffer.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbuffer.c

Core bounded read/write buffer abstraction for SMB packet parsing and construction.

Key capabilities:
- Owns or wraps packet storage with read offset, write offset, max length, and pushed read-limit state.
- Writes bytes, shorts, longs, vlongs, raw byte ranges, fixed strings, and protocol strings.
- Reads bytes, shorts, longs, vlongs, raw byte ranges, ASCII strings, UCS-2 strings, and SMB strings selected by header flags.
- Supports alignment, write/read backup, write limits, read-limit push/pop, fixups for relative/absolute offsets, filling, copying, and offset string extraction.

Interactions:
- Used by almost every SMB command, transaction, client, and response path.
- Delegates string conversion to functions declared in `smbfns.h`.

Notable details:
- `smbbuffergetucs2` optionally inserts leading `/` for paths and converts path separators/case/space according to flags.
- `smbbufferoffsetgetb` compares `offset` against `rn` but then indexes `buf[rn + offset]`; callers use it for response command byte lookup, so offset semantics deserve care.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbclientopen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbclientopen.c

Client-side implementation of `SMB_COM_OPEN`.

Key function:
- `smbclientopen` builds an open request using the client prototype header, share tree id, mode, and path; sends it through NBSS; reads the response; validates header; and returns fid, attributes, mtime, size, and access-allowed fields.

Interactions:
- Called by `cifscmd.c`.
- Uses `smbbuffer`, `smbcommon`, and `nbss` client transport.

Notable details:
- The assignment `*sizep = smbnhgets(pdata); pdata += 4;` reads a 16-bit value while advancing four bytes, which looks suspicious for a 32-bit size field.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbclientopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomclose.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomclose.c

Server handler for `SMB_COM_CLOSE`.

Key behavior:
- Requires word count 3.
- Validates tree id and fid.
- Calls `smbfileclose`, which removes the fid map entry, releases shared-file state, closes fd, and frees the file object.
- Returns an SMB ack.

Interactions:
- Uses `smbidmap`, `smbfile.c`, and `smbbufferputack`.

Notable details:
- Ignores close time fields in the request.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomclose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomcreatedir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomcreatedir.c

Server handler for `SMB_COM_CREATE_DIRECTORY`.

Key behavior:
- Requires zero parameter words and buffer format `0x04`.
- Reads an SMB path, resolves the tree id, prefixes the service path, and calls Plan 9 `create` with `DMDIR | 0775`.
- Returns ack or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses `smbbuffergetstring` for path conversion and `smbidmapfind` for tree lookup.

Notable details:
- Logs the requested path and failure reason.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomcreatedir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdelete.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdelete.c

Server handler for wildcard file deletion.

Key functions:
- `smbremovefile` constructs a full path from service path, optional directory, and name, then calls `remove`.
- `smbcomdelete` parses search attributes and path pattern, splits directory/name, opens a directory cache, compiles SMB wildcard to regexp, removes matching files, and returns ack if at least one removal succeeds.

Interactions:
- Uses `smbpathsplit`, `smbmkdircache`, `smbmkrep`, `smbmatch`, and Plan 9 `remove`.

Notable details:
- Search attributes are logged but not used for filtering.
- Returns `ERRnoaccess` if no matched file was removed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdelete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdeletedir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdeletedir.c

Server handler for `SMB_COM_DELETE_DIRECTORY`.

Key behavior:
- Parses a path, resolves tree id, prefixes service root, and calls `remove`.
- Returns ack on success or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses same tree/path pattern as create-directory handler.

Notable details:
- Does not distinguish nonexistent path, nonempty directory, and permission failures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdeletedir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdir.c

Server handler for `SMB_COM_CHECK_DIRECTORY`.

Key behavior:
- Requires zero word count and path buffer format `0x04`.
- Resolves tree, stats full path, verifies `DMDIR`, checks read access, and returns ack.

Interactions:
- Uses Plan 9 `dirstat` and `access`.

Notable details:
- Logs stat path through `smblogprintif(1, ...)`, which is unconditional.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomecho.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomecho.c

Server handler for `SMB_COM_ECHO`.

Key behavior:
- Reads echo count.
- For each echo index, writes a response header, sequence number, and copied request byte payload.
- Sends each response immediately.
- Returns `Ok` after all echoes or `Die` on send failure.

Interactions:
- Uses `smbresponsesend` and response buffer reset behavior.

Notable details:
- Echo is allowed before session establishment by `aquarela.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomecho.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomfindclose2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomfindclose2.c

Server handler for `SMB_COM_FIND_CLOSE2`.

Key behavior:
- Requires one parameter word containing search id.
- Calls `smbsearchclosebyid`.
- Returns an SMB ack.

Interactions:
- Search implementation is elsewhere; this file just dispatches close-by-id.

Notable details:
- Does not error if the search id is absent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomfindclose2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomflush.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomflush.c

Server handler for `SMB_COM_FLUSH`.

Key behavior:
- Validates tree id and fid.
- Builds an all-`0xff` `Dir` with nil name/user fields and calls `dirfwstat` on the file descriptor.
- Returns ack.

Interactions:
- Uses Plan 9 directory metadata update as a flush-ish operation.

Notable details:
- Ignores `dirfwstat` return value.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomflush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomlocking.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomlocking.c

Server handler for `SMB_COM_LOCKING_ANDX`.

Key functions:
- `getlock` parses small or large lock records into pid, offset, and length.
- `smbcomlockingandx` parses AndX header, fid, lock type, timeout, unlock count, lock count, validates unsupported options, applies unlocks, applies locks, rolls back partial locks on conflict, and chains or replies.

Interactions:
- Uses `smbsharedfilelock` and `smbsharedfileunlock`.
- Uses `smbchaincommand` for AndX continuation.

Notable details:
- Timeout, oplock, and nonzero locktype features are not implemented.
- The parsed lock record pid is logged but calls use `h->pid` for ownership.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomlocking.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcommon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcommon.c

Common SMB header, error, chaining, attribute, and lookup-table helpers.

Key functions:
- `smbsendunicode` checks global and peer Unicode capability.
- `smbcheckwordcount` and `smbcheckwordandbytecount` validate request shape.
- `smbchaincommand` moves the request buffer to an AndX offset and dispatches the chained command.
- `smbbuffergetheader` parses `SmbRawHeader`, validates protocol, fills `SmbHeader`, and pushes byte-count read limit.
- `smbbufferputheader`, `smbbufferputandxheader`, `smbbufferputerror`, and `smbbufferputack` build response headers.
- Attribute helpers translate between Plan 9 modes and DOS attributes.
- `smbl2roundupvlong` rounds file sizes to allocation units.
- `smbslut` and `smbrevslut` map string/value tables.

Interactions:
- Used by all SMB command and client paths.

Notable details:
- `smbdosattr2plan9wstatmode` tries to preserve old mode bits when only attributes change.
- Provides global share/open mode lookup tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcommon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomopen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomopen.c

Central SMB open/create implementation, including classic open, create, OpenAndX, and NTCreateAndX.

Key functions:
- `openfile` maps SMB access/share/create semantics to Plan 9 `open`/`create`, validates directory/file create options, consults shared-file share-deny state, creates `SmbFile`, allocates fid, and returns optional `Dir` and create action.
- `smbcomopenandx` parses `SMB_COM_OPEN_ANDX`, logs mode/share/attribute/ofun details, opens the file, writes response fields, and chains if requested.
- `smbcomopen` handles legacy open.
- `smbcomcreate` handles legacy create with exclusive share and create-if-not-exists semantics.
- `smbcomntcreateandx` maps NT desired access, share access, create disposition, and create options to `openfile`, then returns NT-style metadata.

Interactions:
- Uses `smbsharedfileget`, `smbidmap`, Plan 9 `dirstat`, `open`, `create`, and `dirfstat`.

Notable details:
- Compatibility share mode is rejected as `ERRbadshare`.
- Directory opens create fid entries with `ioallowed = 0`.
- Several comments mark response fields as approximate or uncertain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomquery.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomquery.c

Server handlers for legacy file information queries.

Key functions:
- `smbcomqueryinformation` stats a path under the tree and returns DOS attributes, mtime, size, and padding.
- `smbcomqueryinformation2` stats an open fid and returns date/time fields, size/allocation size, and attributes.

Interactions:
- Uses Plan 9 `dirstat`/`dirfstat`, time conversion helpers, and allocation rounding.

Notable details:
- Query-by-fid requires an open file descriptor; directory fids with `fd = -1` are not specially handled here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomread.c

Server handler for `SMB_COM_READ_ANDX`.

Key behavior:
- Supports 32-bit and 64-bit offsets via word count 10 or 12.
- Validates tree id, fid, and `ioallowed`.
- Builds an AndX response with data offset/count fixups.
- Reads at most requested max count or available response buffer space from the file descriptor.
- Chains to next command when requested.

Interactions:
- Uses `seek` plus `readn` on Plan 9 fd.
- Relies on `smbbufferwritelimit` to cap payload to SMB max transfer size.

Notable details:
- Returns `ERRbadaccess` for directory fids or read errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomrename.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomrename.c

Server handler for `SMB_COM_RENAME`.

Key behavior:
- Parses old/new path strings and requires buffer format `0x04` for each.
- Prefixes service root, splits both paths into directory/name parts, and only allows same-directory rename.
- Calls `dirwstat` with new name.
- Returns ack or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses `smbpathsplit` and Plan 9 `dirwstat`.

Notable details:
- Cross-directory rename is rejected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomrename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsessionsetupandx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsessionsetupandx.c

Server handler for `SMB_COM_SESSION_SETUP_ANDX`.

Key behavior:
- Parses AndX command, max buffer size, max mux, vc number, session key, LM/NT password lengths, capabilities, password bytes, account/domain/native strings.
- Lowercases account name.
- Enforces one user per VC.
- Validates 24-byte LM and NT MS-CHAP responses on first setup.
- Uses Plan 9 auth challenge/response and `auth_chuid`.
- Stores client identity strings and marks session established.
- Returns native OS/LANMAN/domain strings and chains if requested.

Interactions:
- Consumes challenge created by `smbnegotiate`.
- Uses `smbresponse` wrappers and `smbchaincommand`.

Notable details:
- Supports non-extended-security MS-CHAP style authentication only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsessionsetupandx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsetinfo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsetinfo.c

Server handlers for legacy set-information commands.

Key functions:
- `smbcomsetinformation2` updates access/modify times on an open fid using DOS date/time fields and `dirfwstat`.
- `smbcomsetinformation` parses attributes, Unix-style SMB time, and path, then updates mtime via `dirwstat`.

Interactions:
- Uses time conversion helpers and Plan 9 `Dir` stat updates.

Notable details:
- `smbcomsetinformation2` appears to use fields from the new `Dir d` when filling missing old date/time parts, where it likely intended the old `Dir *od`.
- `smbcomsetinformation` calls `dirwstat(name, &d)` without prefixing the connected tree service path, unlike most path handlers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsetinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtransaction.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtransaction.c

Server handlers for `SMB_COM_TRANSACTION` and `SMB_COM_TRANSACTION2`.

Key functions:
- `sendresponse` adapts `smbresponsesend` for transaction method callbacks.
- `smbcomtransaction` decodes a primary transaction, handles secondary continuation state, allocates output buffers, dispatches `/PIPE/LANMAN` to `smbrap2`, and encodes transaction responses.
- `smbcomtransaction2` decodes transaction2, validates setup count/opcode, dispatches through `smbtrans2optable`, and encodes transaction2 responses.

Interactions:
- Uses transaction encode/decode/execute/respond functions declared in `smbfns.h`.
- RAP2 implementation lives in `smbrap2.c`.

Notable details:
- Sets `s->nextcommand` to require the appropriate secondary command when decode reports an incomplete transaction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtransaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreeconnectandx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreeconnectandx.c

Server handler for `SMB_COM_TREE_CONNECT_ANDX`.

Key behavior:
- Validates session state and allowed AndX commands.
- Parses flags, password length, UNC path, and service string.
- Optionally disconnects existing tree id when flags request it.
- Resolves service through `smbservicefind`, creates a tree mapping, and returns tid plus service type and filesystem name string `9p2000`.
- Chains if requested.

Interactions:
- Uses `smbservice.c` and tree id-map functions from other SMB support files.

Notable details:
- Accepts both IPC and disk tree services through service lookup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreeconnectandx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreedisconnect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreedisconnect.c

Server handler for `SMB_COM_TREE_DISCONNECT`.

Key behavior:
- Requires zero word count.
- Disconnects the tree by request tid.
- Returns ack.

Interactions:
- Calls `smbtreedisconnectbyid`, implemented outside this file.

Notable details:
- Does not report an error for absent tid in this wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreedisconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomwrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomwrite.c

Server write and truncate handlers.

Key functions:
- `smbtruncatefile` attempts `dirfwstat` length update, falls back to manual truncate/extend behavior when needed, and writes zero blocks for extension.
- `smbcomwrite` handles legacy write, including zero-count truncate-at-offset.
- `smbcomwriteandx` handles AndX write with 32-bit or 64-bit offset, data offset validation, write, response, and optional chaining.

Interactions:
- Uses fid map, shared `SmbFile` descriptors, Plan 9 `seek`, `write`, `pwrite`, `pread`, `dirfstat`, and `dirfwstat`.

Notable details:
- Manual truncation beyond 256 KiB is reported unimplemented.
- Directory fids are rejected through `ioallowed`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconnect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconnect.c

Client-side SMB connection, negotiation, authentication, tree connect, and transaction transport adapters.

Key functions:
- `smbconnect` resolves/dials NetBIOS session service, sends `SMB_COM_NEGOTIATE`, parses peer info/challenge/domain, sends `SMB_COM_SESSION_SETUP_ANDX` with MS-CHAP response chained to IPC tree connect, optionally connects a requested disk share, and returns `SmbClient`.
- `smbclientfree` frees client peer info, buffer, and object.
- `smbtransactionclientsend` and `smbtransactionclientreceive` adapt NBSS transport for transaction execution.

Interactions:
- Uses `nbssconnect`, `smbbuffer`, `smbcommon`, auth APIs, and transaction client code.

Notable details:
- Rejects servers requiring extended security.
- Hardcodes auth server string `"cher"` in `auth_respond`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconv.c

Little-endian SMB integer conversion helpers.

Key functions:
- `smbnhgets`, `smbnhgetl`, `smbnhgetv` read 16-, 32-, and 64-bit little-endian values.
- `smbhnputs`, `smbhnputl`, `smbhnputv` write 16-, 32-, and 64-bit little-endian values.

Interactions:
- Used by SMB buffer/header/command parsing and construction.

Notable details:
- Separate from Plan 9 network-order helpers because SMB fields are little-endian.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdat.h

Defines Aquarela SMB runtime data structures and dispatch table types.

Major contents:
- Forward declarations for session, tree, service, transaction, buffer, id-map, search, file, shared-file, CIFS session, and RAP structs.
- `SmbPeerInfo`, `SmbTransaction`, `SmbSession`, `SmbHeader`, and `SmbProcessResult`.
- `SmbOpTableEntry` and `SmbTrans2OpTableEntry` dispatch tables.
- `SmbGlobals` and logging flags.
- `SmbTree`, `SmbService`, `SmbSearch`, `SmbFile`, `SmbSharedFile`, `SmbLock`, `SmbCifsSession`, `SmbClient`, RAP and directory-info structs.
- String flag constants for SMB string parsing/formatting.

Interactions:
- Included by nearly all SMB implementation files through `headers.h`.

Notable details:
- Id-mapped object structs place `long id` first where `smbidmapadd/remove` expect to write/read ids through object pointers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdircache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdircache.c

Directory cache helper for SMB directory/pattern operations.

Key functions:
- `smbmkdircache` builds a full path from tree service root and requested path, opens it, reads all directory entries with `dirreadall`, and stores them in `SmbDirCache`.
- `smbdircachefree` frees entry buffer and cache object.

Interactions:
- Used by delete and likely transaction2 find handlers outside this group.

Notable details:
- Cache stores current index `i`, though this file only initializes it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdircache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfile.c

SmbFile close/free helper.

Key functions:
- `smbfilefree` releases shared-file state, closes fd, frees file name and object.
- `smbfileclose` logs close, removes the fid id-map entry, and frees the file.

Interactions:
- Used by close handlers and failure cleanup in open handlers.
- Calls `smbsharedfileput` to update share-deny and delete-on-close state.

Notable details:
- `smbidmapremove` relies on `SmbFile.id` being the first field written by the id map.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfns.h

Function prototype header for Aquarela SMB implementation.

Major contents:
- Endian conversion prototypes.
- SMB command handler declarations.
- Allocation, validation, string conversion, response, tree/service, globals, buffer, client, transaction, trans2, id-map, search, error, time/path/mode, file, log, shared-file, listener, RAP client, directory cache, regexp, open, rune conversion, truncate, remove, and browse prototypes.
- Optional `LEAK` macros for allocator substitution.

Interactions:
- Included through `headers.h` and provides cross-file contracts for the full SMB implementation.

Notable details:
- Declares many functions implemented outside this grouped file set, especially transaction encode/decode, string/time conversion, tree/search, and trans2 handlers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbglobals.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbglobals.c

Defines default SMB server/client global configuration.

Key data:
- `smbglobals` defaults max receive, Unicode enabled, native OS, Aquarela version, mailslot and LANMAN pipe paths, sector/allocation sizes, space conversion flag, and logging settings.

Key function:
- `smbglobalsguess` fills server name, NetBIOS name, account name, primary domain, default remark, and log fd depending on server/client mode.

Interactions:
- Read by negotiation, session setup, browser, service, RAP, and logging code.

Notable details:
- Default server share namespace includes `/n/local` via `smbservice.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbglobals.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbidmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbidmap.c

Generic numeric id map for SMB fids, tids, and search ids.

Key functions:
- `smbidmapnew` creates a map with free index `-1`.
- `grow` doubles array capacity and links new slots into the free chain.
- `smbidmapadd` allocates an id, stores the pointer, marks slot active with `freechain = -2`, and writes the id into the pointed object’s first `long`.
- `smbidmapfind` validates and returns active id entries.
- `smbidmapremovebyid`, `smbidmapremove`, and `smbidmapremoveif` release ids.
- `smbidmapfree` optionally applies a cleanup callback to active entries.
- `smbidmapapply` iterates active entries.

Interactions:
- Used for session `fidmap`, `tidmap`, and `sidmap`.

Notable details:
- `smbidmapfind` checks `id > m->entries` instead of `id >= m->entries` after decrement, which can allow one-past array access.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbidmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblisten.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblisten.c

Direct CIFS TCP listener on port/service `cifs`.

Key functions:
- `smblistencifs` announces `tcp!*!cifs`, records the accept callback, and starts listener process.
- `tcplistener` accepts TCP connections and creates sessions.
- `createsession` allocates a direct `SmbCifsSession`, calls accept callback, starts `tcpreader`, and links session.
- `tcpreader` reads RFC 1002-style 4-byte length headers plus SMB payload and calls the session write callback.
- `deletesession` closes fd, unlinks, and frees session.

Interactions:
- Used by `aquarela.c` direct SMB server mode.

Notable details:
- Unlike `nbss.c`, this path skips NetBIOS session-request negotiation and treats connections as already established at the transport framing level.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblisten.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblog.c

Logging and hex dump utilities for SMB diagnostics.

Key functions:
- `smbloglock` and `smblogunlock` provide nested logging locks.
- `smblogvprint`, `smblogprint`, `translogprint`, and `smblogprintif` conditionally print to configured log fd/stderr.
- `smblogdata` prints bounded hex/ASCII dumps.

Interactions:
- Used throughout packet receive/send and command handlers.

Notable details:
- `smblogprint` checks `smbtrans2optable[cmd].debug`; for ordinary SMB command ids this appears inconsistent with `translogprint` and can index beyond the transaction2 table for large command values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smblog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbnegotiate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbnegotiate.c

Server handler for SMB dialect negotiation.

Key behavior:
- Accepts only initial negotiation state.
- Parses dialect strings and selects `NT LM 0.12` if present.
- Returns user-security encrypted-mode negotiation response, max mux/vc/buffer/raw, session key, capabilities, current NT time, timezone, 8-byte auth challenge, and primary domain.
- Creates Plan 9 MS-CHAP server challenge state.
- Moves session state to `SmbSessionNeedSetup`.

Interactions:
- Consumed by `smbcomsessionsetupandx.c` for authentication.

Notable details:
- Sets `CAP_NT_SMBS` and optionally `CAP_UNICODE`.
- If no dialect matches, returns index `0xffff`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbnegotiate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smboptable.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smboptable.c

Defines SMB and transaction2 dispatch tables.

Key data:
- `smboptable[256]` maps SMB command opcodes to names, process functions, and debug flags.
- `smbtrans2optable[]` maps transaction2 opcodes to names/process functions.
- `smbtrans2optablesize` exposes transaction2 table length.

Implemented command mappings include:
- Directory create/delete/check, open/create/close/flush/delete/rename, query/set info, write, locking AndX, transaction, echo, open/read/write AndX, transaction2, find close2, tree disconnect/connect AndX, negotiate, session setup AndX, and NT create AndX.

Notable details:
- Many legacy/raw/print/search/NT transaction commands are named but unimplemented with nil process pointers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smboptable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbpath.c

Path split helper for SMB paths.

Key function:
- `smbpathsplit` splits a path at the last `/`, returning allocated directory and base-name strings.

Behavior:
- No slash: directory is `/`, name is whole path.
- Root slash: directory is `/`, name is after slash.
- Nested path: directory is substring before last slash.

Interactions:
- Used by delete and rename handlers.

Notable details:
- Caller owns both returned strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2.c

Implements SMB RAP over `/PIPE/LANMAN` server-side procedures.

Key components:
- `InfoMethod` abstracts size, fixed-structure serialization, string serialization, and enumeration.
- Server info helpers serialize `SmbServerInfo` levels 0/1.
- Share info helpers serialize `SmbService` levels 0/1/2.
- `thingfill` and `onethingfill` fill RAP output parameter/data buffers and report `MORE_DATA` when truncated.
- RAP procedures: `NetShareEnum`, `NetServerEnum2`, `NetShareGetInfo`, `NetServerGetInfo`, and `NetWkstaGetInfo`.
- `smbrap2` parses RAP procedure number, parameter descriptor, and data descriptor, then dispatches through `raptable`.

Interactions:
- Called by `smbcomtransaction` for `/PIPE/LANMAN`.
- Uses global services and server identity from `smbglobals`/`smbservice`.

Notable details:
- `netservergetinfo` appears to pass `&shareinfo` while using `&smbglobals.serverinfo`, likely intended to use `serverinfo`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2client.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2client.c

Client-side RAP transaction helpers.

Key functions:
- `smbclientrap` fills an SMB transaction for `/PIPE/LANMAN` and executes it over the client transaction method.
- `smbnetserverenum2` builds a RAP `NetServerEnum2` request, sends it, parses return parameters, copies fixed server records and referenced remarks, and returns an array of `SmbRapServerInfo1`.

Interactions:
- Uses `smbtransactionexecute`, `smbtransactionclientsend`, and `smbtransactionclientreceive`.

Notable details:
- Applies RAP converter offset before copying remark strings from output data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrap2client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrep.c

SMB wildcard pattern to Plan 9 regexp conversion and matching.

Key functions:
- `smbmkrep` translates `*`, `*.`, `?`, repeated `?`, and regexp metacharacters into a regexp string, compiles it, and logs optional conversion.
- `smbmatch` checks that a regexp matches an entire file name.

Interactions:
- Used by wildcard delete and likely directory search code.

Notable details:
- `?` behavior differs at end or before dot: it becomes optional non-dot match.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbresponse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbresponse.c

Thin response-buffer API for `SmbSession`.

Key functions:
- `smbresponseinit`, `smbresponsereset`, and write helpers delegate to `SmbBuffer`.
- `smbresponseputheader`, `smbresponseputandxheader`, and `smbresponseputerror` build common response headers.
- `smbresponsesend` logs outgoing packet data and writes it through either NBSS scatter/gather or direct CIFS framing.

Interactions:
- Used by command handlers that prefer session-level response helpers over raw `smbbuffer` calls.

Notable details:
- Direct CIFS responses write a 4-byte big-endian-ish NetBIOS length prefix through `hnputl`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbresponse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbservice.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbservice.c

SMB share/service registry and lookup.

Key data:
- Built-in `IPC$` service for IPC.
- Built-in `local` disk tree service rooted at `/n/local`.

Key functions:
- `run9fs` forks `/rc/bin/9fs <share>` and waits for completion.
- `smbservicefind` parses UNC paths, accepts IPC, local, and session-specific shares, and can dynamically run `9fs` to create `/n/<share>` then register a session service.
- `smbserviceget`/`smbserviceput` adjust service refs.

Interactions:
- Used by tree connect handler and RAP share enumeration.

Notable details:
- Server-name validation in UNC path is present but commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbservice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbsharedfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbsharedfile.c

Tracks open shared files, share-deny state, byte-range locks, and delete-on-close behavior.

Key functions:
- `smbsharedfileget` finds or creates a shared-file entry by Plan 9 file identity (`type`, `dev`, `qid.path`), enforces current share-deny conflicts, updates aggregate share state, and refs the entry.
- `smbsharedfileput` decrefs, subtracts share state, deletes file on close when requested, frees lock list, and removes entries.
- `smbsharedfilelock` inserts nonconflicting byte-range locks in order.
- `smbsharedfileunlock` removes an exact lock owned by session/pid/range.
- Helpers convert among share mode, deny-read/deny-write booleans, and aggregate share state.

Interactions:
- Used by open/create, close, locking, and delete-on-close related paths.

Notable details:
- `sharesplit` case `SMB_OPEN_MODE_SHARE_DENY_WRITE` assigns `*denywrite` twice and never sets `*denyread`, which appears to be a bug.
- Lock conflict detection is interval based: `[base, limit)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbsharedfile.c -->