# Group Research: group_1594_plan9_sources_os_plan9_plan9_sys_src_cmd_ip_imap4d_list_c_sources_o_626c76a1eb72

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/list.c

Implements IMAP `LIST`, `LSUB`, and subscription maintenance for Plan 9 `imap4d`, mapping mailbox names onto `/mail/box/$user` entries and emitting IMAP mailbox list responses.

Key behavior:
- `lsubBoxes` reads `imap.subscribed`, creates it with default `INBOX` via `mkSubscribed` if absent, and filters each subscribed mailbox through `checkMatch`.
- `subscribe` updates `imap.subscribed` under the mailbox lock, normalizing `inbox` to `INBOX`.
- `listBoxes` always checks `INBOX`, then delegates wildcard traversal to `listMatch`.
- `listMatch` implements IMAP wildcard traversal for `%` and `*`, avoiding full recursion for `%` and only doing recursive-ish listing for `*`.
- `listAll` is intentionally non-recursive in practice because recursive call is guarded by `if(0 && ...)`; it lists one level and lets `checkMatch` filter.
- `mayMatch` and `matches` implement UTF-aware segment wildcard matching over `/`-separated mailbox names.
- `checkMatch` validates with `okMbox`, computes flags such as `\Noselect`, `\Noinferiors`, and `\Marked`, encodes mailbox names using modified UTF-7, and writes untagged IMAP responses.

Integration points:
- Depends on mailbox locking and path helpers from `imap4d.h`/utils: `mbLock`, `mbUnlock`, `cdOpen`, `cdDirstat`, `cdCreate`, `readFile`, `okMbox`, `impName`, `strmutf7`.
- Uses global `mboxDir` and output `bout`.

Risks and notes:
- `subscribe` opens `tfd` with truncation but writes via `fd`, relying on both descriptors pointing at the same file; this is unusual and worth care if porting.
- Wildcard matching is byte-preserving for multibyte UTF by copying rune byte counts, but pattern semantics are custom.
- Mailbox filtering explicitly hides mail-internal directories such as `mails`, `out`, `obox`, and `.imp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mbox.c

Manages IMAP mailbox state over Plan 9 `upas/fs`, including mailbox open/refresh, `.imp` metadata files, UID assignment, flags, expunge/delete, and mailbox-name safety.

Key behavior:
- `openBox` maps `INBOX` to `msgs` or `mbox`, opens the mailbox through `/mail/fs/ctl`, builds a `Box`, reads message directories, then opens or creates the `.imp` file.
- `checkBox` refreshes message state when the backing `upas/fs` directory qid/version/mtime changes and optionally returns a held `.imp` mailbox lock.
- `readBox` scans numeric message directories, preserves existing `Msg` nodes, marks missing messages expunged, allocates new messages, reads message `info`, and assigns IMAP sequence numbers.
- `.imp` files persist `uidvalidity`, `uidnext`, message digest, UID, and flags. `openImp`, `parseImp`, `closeImp`, `createImp`, `emptyImp`, `wrImpFlags`, and `impFlags` maintain this format.
- `boxFlags` assigns UIDs to new messages and counts `\Recent`.
- `deleteMsgs` sends batched `delete` commands to `/mail/fs/ctl` for messages flagged `\Deleted`.
- `expungeMsgs` emits `EXPUNGE` responses when requested, removes expunged `Msg` nodes, renumbers sequences, and marks `.imp` dirty.
- `okMbox` rejects unsafe/internal mailbox names, optionally allowing only names from `imap.ok`.

Integration points:
- Owns the mailbox/UID persistence contract used by fetch/search/store/list code.
- Depends on `msgInfo`, `freeMsg`, path helpers, Plan 9 `Dir`/`Qid`, and global `username`, `mboxDir`.
- Uses `/mail/fs/ctl` as the control plane for opening, closing, and deleting mail messages.

Risks and notes:
- Duplicate message digest handling is explicitly fragile; comments note concurrent IMAP servers may temporarily disagree on UID mapping.
- `.imp` locking is central. Calls that mutate flags or UIDs must hold the mailbox lock via `openImp`.
- `okMbox` can switch behavior entirely if `imap.ok` exists, making allowed mailbox names deployment-configurable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/msg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/msg.c

Implements message metadata loading, MIME/RFC822 header parsing, address parsing, MIME tree construction, bogus-message repair views, message sizing, and selected-header extraction for IMAP responses.

Key behavior:
- `msgFile` resolves files inside an `upas/fs` message directory. For corrupt messages marked `bogus`, it synthesizes fake MIME structure and body parts using temporary files.
- `msgInfo` loads the `info` file and populates indexed fields such as subject, digest, message-id, dates.
- `msgStruct` lazily builds MIME/message child trees, parses `unixheader`, `rawheader`, `mimeheader`, and body size, and constructs a single body child for non-multipart leaves.
- `msgReadFile` reads message files into allocated NUL-terminated buffers, using `dirfstat` for larger files.
- `msgBodySize` counts raw body bytes/lines and adjusts size for bare LF conversion; null bytes mark the body bogus.
- `msgHeader` normalizes headers to CRLF, appends final blank line, parses MIME headers and envelope addresses, and synthesizes `From`/`Date` when needed.
- MIME parsers populate `Header` fields: `mimeType`, `mimeParams`, `mimeEncoding`, `mimeId`, `mimeDescription`, `mimeDisposition`, `mimeMd5`, `mimeLanguage`.
- Address parser handles atoms, quoted strings, comments, groups/routes partly, local names, and bang paths via `headAddress`, `headAddrSpec`, `domBang`, `headDomain`.
- `selectFields` copies matching or non-matching header fields for IMAP `BODY.PEEK[HEADER.FIELDS...]` style responses.
- `freeMsg`, `cleanupHeader`, `freeMAddr`, `freeMimeHdr` own recursive cleanup.

Integration points:
- Used by mailbox open, fetch, search, and store paths through `Msg`, `Header`, `MAddr`, and helper functions such as `msgSize`, `msgStruct`, `msgFile`.
- Depends on Plan 9 `upas/fs` message directory conventions: `info`, `raw`, `rawbody`, `rawheader`, `mimeheader`, `unixheader`.
- Uses global `username`, `site`, and temporary file helper `imapTmp`.

Risks and notes:
- Header parsing is permissive and hand-written; malformed input can trigger fallback/bogus paths rather than strict rejection.
- Bogus-message handling synthesizes multipart content with stripped and base64 alternatives, preserving access to corrupted original data.
- `mimeLanguage` loops while `headChar(0) != ','` and consumes with `headChar(1)`; malformed endings rely on `headChar`/NUL behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mutf7.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mutf7.c

Implements IMAP modified UTF-7 encoding and decoding for mailbox names.

Key behavior:
- `initm64` builds the modified base64 alphabet, using `,` instead of `/`.
- `encmutf7` copies printable ASCII directly, encodes non-ASCII/control runs as `&...-`, and encodes literal `&` as `&-`.
- `decmutf7` reverses this format, validating alphabet entries and zero padding bits.

Integration points:
- Used by mailbox list/command parsing helpers for IMAP mailbox name transport.
- Uses Plan 9 rune conversion functions `chartorune`, `runetochar`, and `runelen`.

Risks and notes:
- Enforces output limits and returns `-1` on malformed input or insufficient buffer.
- Encoding intentionally does not allow escaped printable ASCII except `&`, matching IMAP modified UTF-7 behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/mutf7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/nodes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/nodes.c

Provides small parser/data-structure helpers for IMAP message sets, fetch lists, store operations, numeric/string lists, and IMAP-safe output formatting.

Key behavior:
- `forMsgs` iterates `MsgSet` ranges by sequence number or UID, applying a callback and accumulating errors.
- `mkStore`, `mkFetch`, `mkNList`, `mkSList` allocate parser nodes from `parseBin`.
- `revFetch`, `revNList`, `revSList` reverse parser-built linked lists.
- `BNList` and `BSList` print numeric and IMAP string lists.
- `Bimapdate` and `Brfc822date` format dates through `imap4date`/`rfc822date`.
- `Bimapstr` emits `NIL`, quoted strings, or IMAP literals depending on content and length.

Integration points:
- Shared by command parser/executor logic for FETCH, STORE, SEARCH, and response formatting.
- Depends on `parseBin`, `parseErr`, `Bprint`, `Bimapstr`, and IMAP data model types from `imap4d.h`.

Risks and notes:
- `forMsgs` treats missing sequence numbers as errors but missing UIDs as ignorable, matching IMAP UID command semantics.
- `Bimapstr` switches to literals for long or unsafe strings, avoiding quote escaping complexity for those cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/nodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/search.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/search.c

Implements IMAP `SEARCH` predicate evaluation over parsed `Msg` structures.

Key behavior:
- `searchMsg` ensures `msgStruct(m, 1)` is available, then evaluates a linked list of `Search` predicates with AND semantics.
- Supports boolean operators `NOT` and `OR`, flag predicates, keyword masks, size predicates, address fields, subject, internal/sent dates, UID/sequence sets, header search, body search, and text search.
- `fileSearch` streams a message file with overlap equal to pattern length so matches spanning read boundaries are found.
- `headerSearch` uses `selectFields` to isolate a named header and searches only the value region after `:`.
- `addrSearch` converts `MAddr` entries to strings and performs case-insensitive substring search.
- `dateCmp` compares only year/month/day from parsed dates.

Integration points:
- Relies on `msgStruct`, `msgSize`, `msgFile`, `selectFields`, `maddrStr`, and flag/date fields populated by `msg.c`.
- Search AST types and constants come from the IMAP parser definitions in `imap4d.h`.

Risks and notes:
- Comments note header/envelope searches should decode MIME charset escapes, but this implementation does not.
- `dateCmp` assumes `date2tm` yields meaningful fields; invalid dates are not explicitly rejected here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/store.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/store.c

Implements IMAP `STORE` flag mutation and flag response emission.

Key behavior:
- `storeMsg` applies replace/add/remove flag operations from a `Store` descriptor to a message.
- `\Recent` is protected from client mutation by preserving the old `MRecent` bit.
- `setFlags` updates a message, marks the `.imp` metadata dirty, and maintains `box->recent`.
- `sendFlags` emits untagged `FETCH FLAGS` updates for messages marked `sendFlags`.
- `writeFlags` serializes system flags in IMAP form.
- `msgSeen` marks a message seen as a fetch side effect and schedules a flag update.
- `mapFlag` maps IMAP flag names to internal bitmasks.

Integration points:
- Mutations rely on caller holding the `.imp` lock when persistence is required.
- Uses `bout`, `Bprint`, and shared flag constants from `imap4d.h`.

Risks and notes:
- Silent store operations still update persistent state but suppress immediate flag response.
- Keyword support is bitmask-based through parser-supplied `Store.flags`; arbitrary custom keyword strings are not visible here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/store.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/utils.c

Provides common utility routines for `imap4d`: string predicates, file reading, temporary-file creation, lock-spinning opens, qid lookup, named integer mapping, and fatal allocation wrappers.

Key behavior:
- `strrev`, `isdotdot`, `issuffix`, `isprefix`, `ciisprefix` support parsing and mailbox validation.
- `readFile` reads an entire fd into `parseBin` allocation with trailing NUL.
- `imapTmp` creates a single ORCLOSE temporary file under `/mail/box/$user/mbox.tmp.imp`, retrying if locked.
- `openLocked` retries `cdOpen` while a file appears locked.
- `fqid` extracts a file `Qid`.
- `mapInt` case-insensitively maps names to values.
- `estrdup`, `emalloc`, `ezmalloc`, `erealloc` abort the IMAP session via `bye` on OOM and tag allocations.

Integration points:
- Shared across list, mailbox, parser, and message modules.
- Uses globals `username`, `parseBin`, and Plan 9 allocation/debug APIs.

Risks and notes:
- `readFile` uses `long length` from `Dir.length`; very large files would not be safe, but inputs are small metadata files.
- Temporary file naming assumes only one temp is needed at a time per user mailbox.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipconfig.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipconfig.h

Defines shared state, constants, packet layouts, globals, and prototypes for Plan 9 `ipconfig`.

Key contents:
- `Conf` stores requested/local interface configuration, learned DHCP/NDB values, hardware/client IDs, DHCP lease state, and IPv6 router-advertisement/prefix parameters.
- `Ctl` stores extra device control strings from `-c`.
- Declares global config and flags such as `conf`, `noconfig`, `ipv6auto`, `dodhcp`, `debug`, `plan9`, `dupl_disc`, `myifc`.
- Declares DHCP option helpers, interface configuration functions, NDB functions, IPv6 entry points, and logging helpers.
- Defines IPv6/ICMPv6 packet structures for router solicitation/advertisement, link-layer address option, prefix option, and MTU option.
- Defines protocol numbers, RA flags, IPv6 defaults, and helper prototypes `ea2lla` and `ipv62smcast`.

Integration points:
- Included by `main.c`, `ipv6.c`, and `ppp.c` under `ipconfig`.
- Bridges Plan 9 IP stack control-file operations, DHCP, NDB, and IPv6 RA logic.

Risks and notes:
- `Conf` is a global mutable state bag shared across forked helper processes.
- IPv6 support is explicitly partial: comment notes no IPv6 lease support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipv6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipv6.c

Implements IPv6 address autoconfiguration, router solicitation reception, router advertisement sending/receiving, and RA control-file updates for `ipconfig`.

Key behavior:
- Defines IPv6 multicast, unspecified, loopback, global-unicast, link-local, solicited-node, and default-mask addresses.
- `ea2lla` converts Ethernet MAC to link-local IPv6 address using EUI-64 expansion.
- `ipv62smcast` builds solicited-node multicast address.
- `v6paraminit` initializes default RA and prefix parameters.
- `dialicmp` opens `/net/icmpv6` connections in header mode.
- `ip6cfg` adds an IPv6 address to an interface, optionally autogenerating link-local, and can perform duplicate neighbor discovery by checking the ARP cache after a `try`.
- `recvrahost` consumes router advertisements, updates RA params, ARP neighbor entry for source link-layer address, MTU, and prefix settings via `add6`.
- `recvra6` forks a daemon that sends initial router solicitations and processes router advertisements according to interface `recvra6`/`sendra6` state.
- `recvrs` parses router solicitations and updates ARP from source link-layer option.
- `sendra` builds router advertisements from current interface global unicast prefixes and MAC address.
- `sendra6` forks a daemon that responds to solicitations and sends periodic/final RAs.
- `startra6` starts RA daemons and enables IP routing when advertising.
- `doipv6` is the CLI entry for `add6` and `ra6` actions.

Integration points:
- Uses Plan 9 IP interface introspection `readipifc`, control-file writes to `ipifc/ctl`, and ARP control updates.
- Shares global `conf`, `myifc`, `nip`, `dolog`, `debug`.

Risks and notes:
- Packet option parsing trusts option length fields enough to advance through the packet; several cases validate expected sizes but default/ignored paths just skip `8 * len`.
- Router mode currently only logs received RAs from other routers.
- Duplicate detection is coarse: after `try`, it scans the ARP table for the configured address string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/main.c

Main implementation of Plan 9 `ipconfig`: command-line parsing, interface bind/add/remove/unbind, DHCP client, DHCP option encoding/decoding, NDB integration, lease renewal, and primary-interface publication.

Key behavior:
- CLI supports media selection (`ether`, `gbe`, `ppp`, `loopback`, etc.), verbs (`add`, `remove`, `unbind`, `add6`, `ra6`), DHCP/NDB modes, IPv6 autoconfig, primary selection, custom DHCP option requests, gateway/host/MTU, alternate net mount point, and PPP baud.
- `doadd` binds/configures the interface, performs IPv6 setup if requested, otherwise uses explicit address, NDB lookup, or DHCP; publishes learned config to `/net/ndb` when primary.
- `doremove` and `dounbind` locate matching interfaces and write `remove`/`unbind` to the relevant `ipifc/*/ctl`.
- `binddevice`, `controldevice`, `lookforip`, and `ip4cfg` handle Plan 9 control-file operations for IP stack binding and logical IPv4 address addition.
- DHCP flow:
  - `dhcpquery` opens UDP port 68, sends discover/request, and loops on receive/timer.
  - `dhcpsend` builds BOOTP/DHCP packets with client ID, hostname, vendor class, parameter request list, lease/server/address options.
  - `dhcprecv` validates replies, handles Offer/Ack/Nak, extracts address, mask, gateway, DNS, NTP, hostname/domain, custom requested options, and Plan 9 vendor options.
  - `dhcpwatch` forks a renewal daemon, renews at half lease, reconfigures on expiration, and republishes NDB.
- DHCP option helpers `optadd*`, `optget*`, `parseoptions`, and `parsebootp` encode/decode and sanity-check options.
- NDB flow:
  - `ndbconfig` looks up config by Ethernet address.
  - `putndb`, `writendb`, `putaddrs`, `getndb`, `tweakservers` publish and refresh `/net/ndb`, `cs`, and `dns`.
- `addoption`, `optgetx`, and `getoptions` support user-requested extra DHCP options and append them to NDB text.

Integration points:
- Includes `dhcp.h`, `ipconfig.h`, `ndb.h`, Plan 9 `/net` control files, and `pppbinddev` from `ipconfig/ppp.c`.
- Shares IPv6 entry points with `ipv6.c`.

Risks and notes:
- Most state lives in global `conf`; forked renewal/RA helpers inherit mutable state.
- `parseoptions` writes an `OBend` sentinel at the end of the provided buffer when no end option appears, mutating receive storage.
- `getoptions` does not guard `s == nil` before using it in `smprint`, which may matter for requested options absent in a reply.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ppp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ppp.c

Adapter that lets `ipconfig` delegate interface binding/configuration to `/bin/ip/ppp`.

Key behavior:
- `pppbinddev` clears `/net/ndb` if no IP interfaces exist.
- Forks and execs `ppp -uf -p <dev> -x <mpoint>` plus optional baud.
- Waits for PPP to complete connection/configuration.
- Sets `noconfig = 1` because PPP created the IP interface itself, then reads resulting NDB state via `getndb`.

Integration points:
- Called by `binddevice` in `ipconfig/main.c` when `conf.type == "ppp"`.
- Uses shared globals `conf`, `nip`, `noconfig`.

Risks and notes:
- Falls back from `/bin/ip/ppp` to `/ppp`.
- Treats any non-empty PPP child status as fatal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/linklocal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/linklocal.c

Small command that prints IPv6 link-local or 6to4 addresses derived from Ethernet MAC addresses.

Key behavior:
- `ea2eui64` expands MAC-48 to EUI-64 and flips the universal/local bit for IPv6.
- `ea2lla` builds `fe80::/64` link-local addresses from MACs.
- `eaip26to4` builds `2002:<ipv4>::/48` 6to4-style addresses and appends EUI-64 interface ID.
- `main` accepts `-t ipv4` for 6to4 mode and one or more Ethernet addresses.

Integration points:
- Uses Plan 9 IP formatting/parsing helpers `parseether`, `v4parseip`, `%I`.

Risks and notes:
- No explicit validation of `-t` parse success beyond `v4parseip` call behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/linklocal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/measure.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/measure.c

Ethernet traffic sampler that counts inbound/outbound IP bytes and packets by protocol for a target MAC address.

Key behavior:
- Opens an Ethernet device in promiscuous mode with timestamped packet capture.
- Parses Ethernet and IPv4 headers, tracking byte and packet counters for all IP, IP-in-IP/MBONE, UDP, and TCP.
- Treats packets with source MAC equal target as inbound counters named `protoin`; destination MAC equal target as outbound counters named `protoout`.
- Periodically prints timestamp, elapsed capture time, and protocol counters, then resets.
- `-s` limits sample count; `-d` prints per-packet debug.

Integration points:
- Uses Plan 9 `dial` on `<device>!-2`, control message `promiscuous`, and IP formatting helpers.

Risks and notes:
- Packet timestamp and captured length are read from fixed offsets in the Ethernet buffer (`e.d[60]`, `e.d[58]`), assuming a specific Plan 9 capture layout.
- Program labels errors as `snoopy`, likely copied from another tool.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/measure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ping.c

IPv4/IPv6 ICMP echo client with RTT tracking, protocol autodetection, optional address display, randomized intervals, and loss reporting.

Key behavior:
- `Proto` abstracts IPv4 vs IPv6 ICMP command/reply types, IP header sizes, and output formatting.
- `isv4name` parses dial strings and consults connection server lookups to choose IPv4 or IPv6 unless `-6` forces IPv6.
- `sender` constructs ICMP echo packets, chooses a non-loopback local source address via `myipvnaddr`, stores outstanding `Req` nodes, and writes packets.
- `rcvr` reads replies, validates length/type/code/sequence and payload pattern, computes RTT, and calls `clean`.
- `clean` matches replies to outstanding requests and marks old requests lost after one minute.
- `reply` and `lost` update counters and print per-message output unless quiet/lost-only options suppress it.
- Options include message size, interval, count, quiet, flood, lost-only, randomized interval, wait timeout, and address printing.

Integration points:
- Uses Plan 9 `/net/icmp` and `/net/icmpv6` via `dial`, `readipifc`, `csgetvalue`, and `%I`/`%V` formatting.

Risks and notes:
- `rcvr` checks `n < msglen`, so IP stacks returning shorter-than-requested echo replies are reported as bad length.
- Source address selection deprecates link-local/multicast and falls back to link-local only if no global address exists.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/block.c

Implements the PPP `Block` buffer allocator and block-chain manipulation routines.

Key behavior:
- `allocb` allocates blocks with front padding and reuses free-list buckets.
- `freeb` returns a chain to bucketed free lists and poisons pointers to catch use-after-free.
- `concat`, `blen`, `pullup`, `padb`, `btrim`, `copyb`, and `pullb` manipulate chained packet buffers.
- Optional allocation tracing records caller PCs under `ADEBUG`.

Integration points:
- Used throughout PPP framing, compression, checksum, and IP data paths.
- Shared `Block` structure is declared in `ppp.h`.

Risks and notes:
- Free-list bucket selection is approximate: `(bsz >> 10) & 31`.
- `pullup` can allocate a new leading block if the first block lacks room, then pulls data from following blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/compress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/compress.c

Implements Van Jacobson TCP/IP header compression and decompression for PPP.

Key behavior:
- `compress_init` initializes transmit/receive header state arrays.
- `compress` filters to non-fragmented IPv4 TCP packets and delegates to `tcpcompress`.
- `tcpcompress` finds or allocates a connection state, validates invariant IP/TCP header fields, encodes deltas for urgent pointer, window, ack, seq, IP ID, and special interactive/data cases, or sends uncompressed state refresh.
- `tcpuncompress` restores headers from compressed or uncompressed VJ packets, tracks missing explicit connection IDs after line errors, updates IP checksum, and frees bad packets.
- `compress_negotiate` validates peer state count and stores whether connection IDs are compressed.
- `compress_error` marks receive state invalid after a bad PPP frame.

Integration points:
- Used by `pppwrite` and `pppread` when IPCP negotiates `Fipcompress`.
- Uses `Block` helpers, `ipcsum`, and PPP protocol constants `Pvjctcp`, `Pvjutcp`, `Pip`.

Risks and notes:
- Only TCP is compressed; other IP protocols remain plain.
- Decompression assumes enough front padding for reconstructed headers, with fallback through `padb`/`pullup`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doclient -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doclient

Tiny rc helper for setting up a PPP client-side alternate network namespace.

Behavior:
- Binds `#I2` at `/net.alt2`.
- Starts connection server `ndb/cs -x .alt2`.

Integration points:
- Companion script for PPP testing/demo setups using alternate Plan 9 IP stacks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doclient -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doserve -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doserve

Tiny rc helper for setting up a PPP server-side alternate network namespace.

Behavior:
- Binds `#I1` at `/net.alt`.
- Starts `ndb/cs -x .alt`.
- Starts `aux/listen` with `/rc/bin/service` on `/net.alt/tcp`.

Integration points:
- Companion script for PPP service/testing setups.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/doserve -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/dotest -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/dotest

Tiny rc helper for PPP test setup.

Behavior:
- Ensures `/net.alt/tcp` and `/net.alt2/tcp` are bound from `#I1` and `#I2`.
- Kills old `8.out` and `testppp` processes if present.
- Runs `testppp`.

Integration points:
- Intended local test harness helper for the PPP implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/dotest -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ipaux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ipaux.c

Provides checksum helpers for PPP IP/TCP/UDP processing.

Key behavior:
- `ptclbsum` computes a 16-bit partial checksum over a byte buffer, handling alignment and host endianness.
- `ptclcsum` computes an Internet checksum across a chained `Block` list with offset/length.
- `ipcsum` computes an IPv4 header checksum based on the IHL field.

Integration points:
- Used by VJ compression and MPPC debug validation for reconstructed IP packets.
- Depends on `Block` and `BLEN` from `ppp.h`.

Risks and notes:
- Optimized around unaligned/aligned short reads in Plan 9 C; portability needs care.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ipaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/mppc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/mppc.c

Implements Microsoft Point-to-Point Compression (MPPC) and optional RC4-based encryption support for PPP CCP.

Key behavior:
- Compression state `Cstate` keeps 8 KiB history arenas, hash table, packet count, reset/front flags, bit output register, and optional RC4 key state.
- `compinit` initializes history/hash state and encryption key material from `PPP.key` when `sendencrypted` is set.
- `comp` prepends protocol, compresses with `comp2`, chooses compressed vs expanded/plain output, sets MPPC count/flags, and encrypts payload if negotiated.
- `comp2` performs LZ-style hash matching against current/old history, emits literals through `complit` and copies through `compcopy`.
- `compfront` and `compreset` manage history window rollover and reset flags.
- `uncomp` strips MPPC header, calls `uncomp2`, returns CCP reset requests on failure, and extracts the original protocol.
- `uncomp2` validates packet counts, handles reset/front/encryption flags, decodes literal/copy bitstream into history, and returns reconstructed payload.
- `setkey` derives RC4 keys using SHA-1 padding sequence.
- Tail functions `ipcheck` and `hischeck` are debug validators for reconstructed IP/TCP/UDP checksums.

Integration points:
- Exposes `cmppc` and `uncmppc` virtual tables consumed by `ppp.c` CCP negotiation.
- Uses PPP `Block`, LCP reset request allocation, RC4/SHA from `libsec`, and checksum helpers from `ipaux.c`.

Risks and notes:
- Packet count continuity is strict; missing packets trigger reset request.
- Several debug logs are unconditional in decompression paths.
- `comp` requires two bytes of headroom and calls `sysfatal` if absent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/mppc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.c

Main PPP implementation: HDLC-like framing, LCP/IPCP/CCP negotiation, CHAP/PAP authentication, IP interface binding, packet forwarding, compression integration, link quality monitoring, modem/chat handling, and CLI.

Key behavior:
- `pppopen` initializes a `PPP` instance, stores media fds/IP preferences, starts media input processing, and enters LCP negotiation.
- `init`, `setphase`, `pinit`, `newstate` drive PPP phases and protocol state machines for LCP, authentication, network protocols, and termination.
- `getframe` reads PPP frames, handles optional HDLC framing, escape decoding, FCS verification, address/control compression, and protocol extraction.
- `putframe` serializes PPP frames, applies protocol/address compression when negotiated, escapes control characters, appends FCS, and writes to media.
- `config`, `getopts`, `rejopts`, and `rcv` implement Configure-Request/Ack/Nak/Rej processing for LCP, CCP, and IPCP.
- IPCP supports local/remote IPv4 address negotiation, DNS/WINS options for primary links, and VJ TCP header compression.
- CCP supports MPPC and hooks compression/uncompression virtual tables.
- `ipopen` binds a Plan 9 `pkt` interface, configures point-to-point local/remote addresses, sets default route if primary, starts `ipinproc`, and rendezvous-signals configuration complete.
- `pppread` dispatches inbound frames by protocol: LCP, CCP, IPCP, IP, LQM, CHAP, PAP, VJ TCP, compressed data, and protocol rejects.
- `pppwrite` sends outbound IP, applying VJ and MPPC compression when negotiated.
- `ipinproc` reads packets from the Plan 9 packet interface and sends them over PPP.
- `mediainproc` reads PPP IP packets and writes them to the packet interface, enforcing source address on server links.
- LQM support is in `getlqm` and `putlqm`.
- CHAP/PAP:
  - `chapinit` sends server challenges.
  - `getchap` handles CHAP challenge/response/success/failure for MD5 and MS-CHAP, derives MPPE/MPPC key material for MS-CHAP.
  - `putpaprequest`, `papinit`, and `getpap` implement client-side PAP auth flow.
- `connect` supports manual modem interaction or scripted chat file send/expect sequences.
- `main` parses PPP CLI options, opens serial/dial/stdin media, configures serial control settings, optionally runs chat/user interaction, starts PPP, waits for IP configuration, and publishes NDB if primary.

Integration points:
- Central user of `ppp.h`, `block.c`, `compress.c`, `mppc.c`, `ipaux.c`, Plan 9 auth/factotum APIs, `/net/ipifc`, `/net/ndb`, and serial control files.
- `ipconfig/ppp.c` invokes this binary for PPP-backed interface configuration.

Risks and notes:
- `nipifcs` appears to loop `for(lifc = ifc->lifc; ...)` instead of `nifc->lifc`, likely a bug in interface counting.
- Global `dying`, `server`, `primary`, `debug`, etc. are process-wide and shared by forked processes using `RFMEM`.
- Authentication has server CHAP support and client PAP/CHAP response support; PAP auth requests as server are logged unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.h

Shared PPP declarations: buffer blocks, protocol constants, state structures, compression interfaces, PPP session state, packet layouts, and external function prototypes.

Key contents:
- `Block` packet buffer definition and block helper prototypes.
- PPP framing constants, protocol IDs, PPP phases, LCP codes/options, auth protocols, CHAP/PAP states, link states, CCP/ECP/IPCP options, option flag masks, timeout/MTU/default constants.
- `Pstate` stores per-control-protocol negotiation state.
- `Chap` stores authentication state and challenge.
- `Qualstats` and `Qualpkt` model link quality monitoring.
- `Comptype` and `Uncomptype` are compression virtual tables for MPPC/thwack.
- `PPP` is the main session object, containing fds, addresses, negotiated flags, compression/encryption/auth state, LQM counters, and statistics.
- Declares public PPP APIs `pppread`, `pppwrite`, `pppopen`, compression/checksum helpers, MPPC/thwack type tables, and `netlog`.

Integration points:
- Included by all files under `cmd/ip/ppp`.
- Defines the ABI between PPP core, block allocator, VJ compression, MPPC compression, checksum helpers, and optional thwack modules.

Risks and notes:
- `PPP` is a large mutable shared object passed across forked processes with `RFMEM`.
- IPCP DNS/WINS flags are manually mapped above bit 8 because option numbers exceed direct low-bit range.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.h -->