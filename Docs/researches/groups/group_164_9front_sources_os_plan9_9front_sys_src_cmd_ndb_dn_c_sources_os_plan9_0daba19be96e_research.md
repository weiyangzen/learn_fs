# Group Research: group_164_9front_sources_os_plan9_9front_sys_src_cmd_ndb_dn_c_sources_os_plan9_0daba19be96e

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dn.c

Implements the DNS domain-name and resource-record cache core for `ndb/dns`.

Key elements:
- Maintains a hash table of `DN` objects keyed by case-insensitive domain name plus class.
- Provides global time state via `timems`, and installs DNS-specific formatters in `dninit`.
- Implements `dnlookup`, `idnlookup`, and `ipalookup` for canonical DNS object allocation.
- Implements RR cache insertion, duplicate removal, TTL/expiry handling, and positive/negative RR replacement.
- Uses a two-mark activity/GC scheme: `getactivity` and `putactivity` track active request marks, while `dnageall` ages expired RRs and sweeps unreferenced `DN`s only when safe.
- Handles authoritative database conversion rules in `dnauthdb`, including minimum SOA TTL enforcement and anti-spoofing for local areas.
- Provides RR list helpers: `rrlookup`, `rrcopy`, `rrcat`, `rrremneg`, `rrremtype`, `rrremowner`, `unique`, and `randomize`.
- Provides text and RR formatters `%R`, `%Q`, and `%\`, including escaping for TXT data.
- Allocates/frees type-specific RR payloads in `rralloc` and `rrfree`.
- Generates reverse PTR records with `dnptr`.

Notable behavior:
- Database RRs get an effective attach TTL of one year; short network TTLs are extended to at least ten minutes to keep answers usable during a request.
- `rrlookup` prioritizes authoritative database data, then fresh authoritative network data, then fresh unauthoritative network data, then unauthoritative database hints.
- Negative cached records are first-class `RR`s with `negative`, `negsoaowner`, and `negrcode`.
- `slave` forks request worker processes with shared memory and returns the parent to the main loop via `longjmp`.

Risks and quirks:
- `certequiv` compares fields to themselves (`a->type == a->type`, etc.), which appears to ignore the `b` certificate fields except for the block comparison.
- The GC logic depends on correct `getactivity`/`putactivity` pairing across forked request workers.
- `rrfree` asserts the RR is not cached, so all cache unlink paths must clear `cached` first.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnarea.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnarea.c

Tracks DNS authority areas owned by this server and delegated subareas.

Key elements:
- Defines global `Area *owned` and `Area *delegated`.
- `nameinarea` finds the longest matching suffix area for a domain name.
- `inmyarea` returns the owned area containing a name unless a longer delegated subarea contains it.
- `addarea` creates an `Area` from an SOA RR, placing it in either `owned` or `delegated` depending on the ndb tuple value.
- `freeareas` releases all areas and their copied SOA records.

Notable behavior:
- Areas are sorted by decreasing name length so more-specific areas are checked first.
- Each `Area` stores a copied SOA RR, and new areas default to `neednotify = 1`.
- Delegation is represented as an area with a non-empty tuple value.

Risks and quirks:
- `addarea` logs `"delegated"` only when the insertion pointer is literally `&delegated`; after list traversal this comparison may not reflect the original list.
- The SOA owner `DN` must remain valid through the DN cache lifecycle, as noted by the comment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnnotify.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnnotify.c

Implements DNS NOTIFY receive and send support for zone refresh propagation.

Key elements:
- `dnnotify` handles incoming NOTIFY requests by moving the question into the reply, validating SOA type, checking `inmyarea`, and marking the area for refresh when serials differ.
- `getips` resolves slave names to A and AAAA addresses, excluding local interface addresses.
- `send_notify` builds a NOTIFY request with `mkreq`, sends it over UDP up to three times, and waits for an acknowledgement with matching ID/opcode.
- `notify_areas` sends notifications to every `dnsslave` listed in each owned area’s SOA.
- `notifyproc` forks a background process that periodically calls `notify_areas`.

Notable behavior:
- Incoming NOTIFY replies are always formed with `Fresp | Onotify | Fauth`.
- Outgoing notifications use UDP port 53 and include the SOA owner as the question.
- The background process sets `req.isslave = 1` to avoid spawning further resolver slaves.

Risks and quirks:
- `send_notify` passes `Cin` as the second argument to `mkreq`, whose parameter is named `type`; this mirrors existing code but is suspicious because NOTIFY normally asks for SOA.
- `notifyproc` only sends notifications; actual database refresh is coordinated through `needrefresh` and the main activity/aging path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnresolve.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnresolve.c

Implements recursive DNS resolution and outbound DNS transport.

Key elements:
- Public entry point `dnresolve` resolves `(name, class, type)` with optional recursion, CNAME chasing, search-domain expansion, and negative response reporting.
- `dnresolve1` checks cache/database, local authoritative areas, then performs network lookup through `issuequery`.
- `issuequery` chooses configured resolver servers, local authoritative NS entries, cached NS entries, or database NS hints while walking up the DNS tree.
- `netquery`, `doquery`, `udpqueryns`, `tcpquery`, and `tlsqueryns` implement outbound DNS over UDP, TCP, and TLS.
- `mkreq` builds DNS query packets, including EDNS options from `mkednsopt`.
- `readreply` validates response ID, question owner, and query type, and detects truncation.
- `procansw` validates and incorporates answer, authority, and additional sections into the cache.
- `serveraddrs` finds or resolves nameserver A/AAAA addresses while avoiding multicast/broadcast, self-addresses, and recursive loops.
- `cacheneg` stores negative responses with SOA-derived TTL when available.

Notable behavior:
- EDNS advertised UDP payload is conservatively set to 1232 bytes for IPv6 MTU safety.
- TCP connections are cached briefly and reused for up to `Maxtcpresuetm`.
- DNS-over-TLS is selected for synthetic `local#dot#server` or `override#dot#server` NS owner names and validates certificates against `/sys/lib/tls/dns`.
- Bad delegations and out-of-bailiwick SOA/NS/hints are filtered before cache insertion.
- Resolver recursion depth is capped at 12.
- For 9P-originated requests, `netquery` calls `slave` and avoids blocking the 9P loop when no worker can be created.

Risks and quirks:
- Negative responses need not be authoritative before caching; this is intentional per comments but broadens cache trust.
- `procansw` aggressively filters answer owner/type, which keeps cache safer but may discard uncommon DNS response shapes.
- Timeout behavior is tuned around `Maxreqtm`, `Minreqtm`, and exponential UDP retransmits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnresolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dns.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dns.c

Main `ndb/dns` service: a mounted 9P DNS query file plus optional UDP/TCP DNS server.

Key elements:
- Parses service flags for resolver mode, forwarding-only mode, serving mode, recursion policy, cache target, database file, certificate, and network mount point.
- Initializes DNS cache/database, creates `/srv/dns...`, mounts a synthetic 9P service at the selected net mount point, and optionally starts UDP/TCP/TLS DNS servers.
- Exposes a single file named `dns` under the mounted directory.
- Handles 9P fids with `Mfile`, active requests with `Job`, and dispatches 9P messages in `io`.
- `rwrite` accepts queries in `domain type` form and owner-only commands `debug`, `refresh`, and `target N`.
- `lookupquery` calls `dnresolve`, strips negative RR objects, and formats replies.
- `respond` stores formatted `%R` or `%Q` records in the fid buffer for later reads.
- Provides shared debug logging hooks `logreply`, `logrequest`, and `getdnsservers`.

Notable behavior:
- Writes must be at offset zero and under `Maxrequest`.
- Prefixing the query with `!` switches output to attribute-value `%Q` format.
- A trailing dot on the requested name marks it as rooted.
- Each query increments DNS stats and participates in `getactivity`/`putactivity`.

Risks and quirks:
- The service hand-rolls a small 9P loop instead of using lib9p.
- Per-fid reply buffers are fixed size (`Maxreply`) with a fixed maximum RR offset table.
- Owner-only commands are gated by the fid user matching the DNS server’s startup user.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dns.h

Shared DNS protocol and resolver header for the `ndb` DNS implementation.

Key elements:
- Defines RR type constants, DNS class constants, opcodes, response codes, DNS header flags, EDNS flags, length limits, TTL constants, packet limits, and request timing limits.
- Defines core structures: `Request`, `DN`, `RR`, `SOA`, `Server`, `DNSmsg`, `Area`, and type-specific payload structs for DNSSEC-like and miscellaneous records.
- Defines global configuration `Cfg` for cache, resolver, forwarding, serving, and recursion policy.
- Defines `Stats` counters for query volume, timing buckets, timeouts, cache/negative-answer behavior, and slave high-water mark.
- Declares cross-file functions for cache management, RR allocation/formatting, area management, database lookup, recursive resolution, server response generation, UDP/TCP servers, notify processing, and packet conversion.

Notable behavior:
- `RR` uses unions heavily; fields are interpreted by `type` and `negative`.
- `Request` carries fork/longjmp state and active-mark state for request workers.
- EDNS is modeled as an OPT RR stored separately in `DNSmsg.edns`.
- `Maxactive` is 250, and request processing timeout defaults to 15 seconds.

Risks and quirks:
- Many globals are declared here and defined in different programs, so utility binaries provide stubs or alternate definitions.
- Typo-preserving names like `Runimplimented` are part of the internal API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsdebug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsdebug.c

Interactive and one-shot DNS debugging client using the same resolver core.

Key elements:
- Supports flags for cached database mode, resolver mode, debug logging, alternate database/net mount, and database file selection.
- Initializes DNS core, opens database, loads DB into cache, and accepts either command-line or interactive queries.
- Provides pretty RR formatter `%P` that aligns owner, TTL, type, and data.
- Implements verbose `logreply` and `logrequest` hooks for resolver network tracing.
- `getdnsservers` can override configured resolvers with an `@server` or `!server` temporary server, where `!` selects DoT-style override naming.
- `doquery` defaults to A lookups for names and PTR lookups for numeric IPs, converts PTR names with `mkptrname`, and calls `dnresolve`.
- `docmd` supports `refresh` and temporary server queries.

Notable behavior:
- Unless `-c` is set, the cache is purged before each query.
- Temporary server overrides are cleared after the query.
- Literal IP server overrides create synthetic address RRs and attach them authoritatively.

Risks and quirks:
- Mutates the query string in place when stripping a trailing dot.
- Depends on shared DNS globals and packet conversion code, but runs as a standalone command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnserver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnserver.c

Builds DNS replies for incoming DNS server requests.

Key elements:
- Public entry point `dnserver` consumes one question from a request message and fills a reply message.
- Validates opcode, RR type support, and class.
- Distinguishes authoritative local-area answers from recursive or non-recursive external answers.
- Enforces `cfg.nonrecursive` and `cfg.localrecursive` policies.
- Uses `doextquery` to call `dnresolve`, move positive answers into `mp->an`, and retain negative-cache RR information separately.
- Adds authority NS records for known parent zones and hint A/AAAA records for NS/MX/SRV/CNAME targets.
- Adds SOA records to negative responses when local authoritative area or cached negative SOA owner is known.
- Deduplicates answer, authority, and additional sections with `unique`.

Notable behavior:
- AXFR/IXFR are rejected here for locally owned areas; TCP AXFR has special handling in `dntcpserver.c`.
- Authority flag is set for local areas and transitive authoritative cached answers.
- If recursion was requested and no answer is found, response code can be copied from the queried owner `DN`.

Risks and quirks:
- The function mutates request and reply ownership of RR lists; callers must free the correct message lists afterward.
- Negative cached RRs are intentionally not returned as answer records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsgetip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsgetip.c

One-shot resolver that prints IP addresses for a domain.

Key elements:
- Supports `-a` for all addresses, `-d` debug, and `-x` for `/net.alt`.
- Runs in resolver mode with `cfg.resolver = 1`.
- `resolve` wraps `dnresolve` for A or AAAA, strips negative entries, prints `rp->ip->name`, and exits early unless `-a` is set.
- Main resolves both IPv4 and IPv6 unless the input is already an IP literal.
- Provides standalone stubs for `syslog`, `logreply`, and `logrequest`.

Notable behavior:
- Uses `req.isslave = 1` to avoid worker forking.
- If no addresses are found, reports separate v4/v6 failure strings when they differ.

Risks and quirks:
- `resolve` calls `exits(nil)` inside the RR loop when not `-a`, so normal cleanup after the first address is skipped by process exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsgetip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsquery.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsquery.c

Interactive client for the mounted `/net/dns` 9P DNS service.

Key elements:
- Opens `/net/dns` by default, `/net.alt/dns` with `-x`, or a provided path.
- Prompts for query lines, trims whitespace, and writes each query to the DNS file.
- Defaults to `ip` query for names and `ptr` query for IP literals.
- Converts PTR inputs to reverse names with `mkptrname`.
- Preserves leading `!` to request attribute-value output from `dns.c`.
- Reads and prints all returned data after each query.

Notable behavior:
- Uses the existing mounted DNS service rather than linking resolver internals.
- Prints write errors as `!%r`.

Risks and quirks:
- Minimal parsing; queries with spaces are passed through as-is.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnsquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dntcpserver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dntcpserver.c

DNS-over-TCP and DNS-over-TLS server implementation, including AXFR support.

Key elements:
- `dntcpserver` forks a server process, accepts one TCP/TLS connection from `tcpannounce`, then loops reading length-prefixed DNS messages.
- Supports optional TLS server mode on port 853 using a PEM certificate chain.
- Parses incoming DNS messages, EDNS options, and hands normal questions to `dnserver`.
- Handles AXFR (`Taxfr`) specially through `dnzone`.
- `dnzone` checks the SOA, verifies the caller is local or listed in `dnsslave`, then streams SOA, zone RRs from `rrgetzone`, and final SOA.
- `findserver` resolves slave names and compares them to the caller IP.
- `tcpannounce` listens, controls child count with `/proc/pid/wait`, accepts connections, performs TLS when configured, and records remote address.

Notable behavior:
- Each accepted connection is handled in a forked child.
- Reply writes are bounded by remaining request timeout.
- AXFR authorization is tied to SOA `slaves` list and `myip`.

Risks and quirks:
- Only AXFR receives special transfer handling; IXFR remains unsupported elsewhere.
- Uses shared-memory forks and global state like the UDP server.
- Child count is capped at `Maxprocs = 64`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dntcpserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnudpserver.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnudpserver.c

UDP DNS server implementation.

Key elements:
- `dnudpserver` forks a UDP server process, announces UDP port 53, and loops reading packet-header mode datagrams.
- Uses `clientrxmit` to suppress exact duplicate retransmissions while a request is in progress.
- Converts packets with `convM2DNS`, validates question count/opcode, and supports query and notify opcodes.
- Handles EDNS request options and sets response size limit accordingly.
- For each question, dispatches to `dnnotify` for NOTIFY or `dnserver` for normal queries.
- `reply` converts `DNSmsg` to wire format and writes it back through the same UDP packet buffer.
- `udpannounce` configures Plan 9 UDP packet headers and ignores ICMP advice.

Notable behavior:
- Maintains `inprog[Maxactive+2]` for retransmission suppression.
- Updates UDP receive stats and participates in global request activity tracking.
- Restarts UDP announce loop if reads fail with too-short data.

Risks and quirks:
- The duplicate suppression key includes raw `Udphdr`, owner pointer, type, and ID.
- Multiple-question packets are processed by looping over `reqmsg.qd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dnudpserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/inform.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/inform.c

Builds and sends RFC2136 DNS UPDATE messages for Windows DNS-style “inform” updates.

Key elements:
- Reads local `sysname` and ndb attributes `dom`, `dnsdomain`, `ns`, and `inform`.
- Converts domain names to IDN wire names with `utf2idn`.
- Constructs a DNS UPDATE packet manually with zone, delete-old-A/AAAA records, and add-new A/AAAA records.
- Enumerates local interfaces with `readipifc`, skipping unspecified and loopback addresses.
- Sends the update to the configured DNS server over UDP.
- Waits up to 3 seconds for a matching transaction ID and maps response codes to human-readable errors.

Notable behavior:
- Uses opcode `5<<11` for DNS UPDATE.
- TTL for added address records is 25 hours.
- Error code 7 is treated as a warning/acceptable “RR exists” case.

Risks and quirks:
- Manual packet construction bypasses shared DNS message conversion.
- `err = g16(&p) & 7` only inspects low three bits, not the full DNS RCODE.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/inform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/ipquery.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/ipquery.c

Small wrapper around `ndbipinfo`.

Key elements:
- Usage: `ipquery attr value rattribute`.
- Supports `-f` to choose an ndb file.
- Opens the database, calls `ndbipinfo(db, attr, val, rattr, nrattr)`, and prints returned tuples as `attr=value`.
- Installs `$` formatter via `ndbvalfmt`.

Notable behavior:
- Prints all tuple entries in the returned linked entry list on one line.

Risks and quirks:
- Minimal validation beyond argument count and database open failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/ipquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkdb.c

Converts merged legacy host database lines into ndb tuple format.

Key elements:
- Classifies fields as comments, sys names, Datakit names, IP addresses, or domain names.
- Accumulates related tuples until a new domain group starts, then prints an ndb entry.
- `tprint` emits `sys=`, `dom=`, `ip=`, and `dk=` attributes with continuation indentation.
- Adds `flavor=console` for specific Datakit console names under `nj/astro`.

Notable behavior:
- Domain duplicates suppress entry splitting.
- IP detection is simple dotted numeric syntax, not full IP parsing.
- Reads stdin and writes stdout through `Biobuf`.

Risks and quirks:
- Fixed arrays of 64 tuples and 64 fields can overflow if input lines are unusually large or grouped entries accumulate too many unique fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkhash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkhash.c

Builds an on-disk hash sidecar for an ndb file attribute.

Key elements:
- Usage: `mkhash file attribute`.
- Opens the requested ndb file and finds the matching `Ndb` object.
- Counts matching attribute occurrences to size the hash table.
- Builds an in-memory hash table using `ndbhash`, `NDBPUTP`, chain flags, and fixed pointer lengths.
- Writes `<file>.<attribute>` with mtime/hash length header and hash entries.
- Verifies the source file did not change underneath by checking qid path/version after writing.

Notable behavior:
- Allocates enough for worst-case chaining.
- Fails if database offsets exceed `NDBSPEC`.
- Creates the hash file with `DMTMP|0664`.

Risks and quirks:
- The typo `"not enougth memory"` is the literal exit string.
- If source changes during build, the generated hash file is removed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkhosts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkhosts.c

Generates legacy host/db/equivalence/text files from ndb entries for a domain.

Key elements:
- Defaults domain to `research.att.com`.
- Parses `/lib/ndb/local` and `/lib/ndb/friends` unless files are provided.
- Collects entries containing `ip` and either matching domain suffix or `ipnet`.
- Stores selected entries in global `X x[4096]`.
- Writes `/lib/ndb/db.<domain>` with DNS-style A/CNAME/MX lines.
- Writes `/lib/ndb/equiv.<domain>` with domain aliases.
- Writes `/lib/ndb/txt.<domain>` with HOST/NET text records.

Notable behavior:
- `printArecord` uses first `dom` as A record and additional `dom`s as CNAMEs.
- `printtxt` uppercases names in place.
- Entries with `flavor=console` are skipped.

Risks and quirks:
- Fixed 4096-entry array has no bounds check.
- Mutates tuple values while uppercasing and trimming `.0` network suffixes.
- Some older host-file generation code is commented out.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/mkhosts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/query.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/query.c

General-purpose ndb and connection-server query tool.

Key elements:
- Usage: `query [-acim] [-x netmtpt] [-f ndbfile] attr value [rattr]...`.
- Supports all matches (`-a`), connection server lookups (`-c`), IP info mode (`-i`), and multiple values (`-m`).
- Uses `ndbipinfo`/`csipinfo` in IP mode.
- Uses `ndbgetvalue`/`csgetvalue` for simple single-attribute lookups.
- Uses `ndbsearch` for broader database scans.
- Prints either bare values for single requested attributes or `attr=value` groups for multiple attributes.
- Installs `$` formatter for ndb values.

Notable behavior:
- `@` prefixes on requested attributes are ignored for matching via `skipat`.
- Connection-server mode is disabled when only `attr value` is provided.

Risks and quirks:
- Connection-server mode does not implement broad multi-result scanning without `ipinfo`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/query.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/news.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/news.c

Displays local Plan 9 news items from `/lib/news`.

Key elements:
- Modes: default prints news newer than `$home/lib/newstime`; `-a` prints all; `-n` prints only names.
- `read_dir` collects news directory entries, injects the previous `newstime` marker, optionally updates it, filters ignored names, and sorts by reverse mtime.
- `eachitem` iterates sorted items until the marker unless printing all.
- `print_item` prints item header with owner and date, then indents nonblank content.
- `note` emits compact `news: item...` output.

Notable behavior:
- Zero-length news files are treated as “in progress” and skipped.
- Ignored names are `core` and `dead.letter`.

Risks and quirks:
- Uses fixed path buffers and `sprint`.
- Does not free allocated news names before exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/news.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nfs.c

A 9P file server backed by NFSv3 and MOUNT RPC.

Key elements:
- Wraps portmapper, MOUNT v3, and NFS v3 RPCs with helpers for null, mount, getattr, access, mkdir, create, read, write, remove, rmdir, rename, setattr, commit, lookup, and readdir/readdirplus.
- Maps Plan 9 fids to `FidAux`, storing NFS file handle, parent handle, name, readdir cookie, error buffer, and AuthSys credentials.
- Reads passwd/group files into a `Map`, supports name/id lookups, and precomputes SunAuthUnix credential blobs.
- `fsattach` mounts an export path and initializes root fid state.
- `fsopen`, `fscreate`, `fsread`, `fswrite`, `fsremove`, `fsstat`, `fswstat`, and `fswalk` translate 9P operations into NFSv3 RPCs.
- Directory reads prefer READDIRPLUS and fall back to READDIR if unsupported.
- Uses a channel/thread dispatch model so each 9P request is handled in a worker thread.
- `threadmain` can query portmapper for mount/NFS ports or accept explicit mount and NFS addresses.

Notable behavior:
- Plan 9 permissions for created files are masked using the parent directory mode, and group is inherited.
- `wstat` may rename first and then setattr, explicitly noting loss of atomicity if setattr fails.
- `fsflush` forwards flush tags to both RPC clients.
- Service is posted with `threadpostmountsrv`, and `/srv/<srvname>` permissions can be adjusted with `-p`.

Risks and quirks:
- Remove/rename depend on stored parent handle and name, described as a “botch” in comments.
- `readplus` is a global tri-state controlling READDIRPLUS fallback.
- User/group maps are optional; missing users fall back to nobody-style credentials.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nm.c

Plan 9 `nm` implementation for object files, archives, and executables.

Key elements:
- Supports flags `-a`, `-g`, `-h`, `-n`, `-s`, `-T`, and `-u`.
- Opens each file, detects archives with `isar`, object files with `objtype`, and executables with `crackhdr`/`syminit`.
- `doar` iterates archive members, skipping `__.SYMDEF`.
- `psym` filters symbols according to type and flags.
- `zenter` builds filename-element translation for `z` records.
- `printsyms` sorts by name or numeric value, prints optional file prefix, optional type signature, address, type, and name/path.
- Errors are accumulated into exit status `"errors"`.

Notable behavior:
- `-s` preserves original symbol order.
- Width expands from 8 to 16 hex digits when a symbol value exceeds 32 bits.
- Hidden dot/dollar symbols are omitted unless `-a`.

Risks and quirks:
- Comment notes sorting can mishandle `z` records with `-a`.
- Global `filename` is temporarily changed to archive member names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nntpfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nntpfs.c

A 9P filesystem view of an NNTP server.

Key elements:
- `Netbuf` tracks NNTP I/O, auth state, current group, server address, credentials, and extension flags.
- `Group` builds a tree from dotted newsgroup names with range, posting, and timestamp metadata.
- Connects to NNTP, optionally authenticates with `AUTHINFO USER/PASS`, and refreshes groups via `LIST`.
- Caches `XOVER` results in 100-message chunks for overview reads.
- Maps group hierarchy, article directories, and article files (`header`, `body`, `article`, `xover`) into 9P.
- Supports a writable `post` file in postable groups; writing zero bytes commits with NNTP `POST`.
- Uses QID path bits for group/message and QID version bits for per-message file kind.
- Refreshes root/group metadata on stat/read with rate limiting for groups.

Notable behavior:
- Article data is fetched lazily through `HEAD`, `BODY`, `ARTICLE`, or `XOVER`.
- Read offsets over directories use an auxiliary offset cache.
- `fsdestroyfid` auto-posts pending post content when a post fid is destroyed.

Risks and quirks:
- Extension probing is present but disabled/commented.
- The QID encoding limits group/message ID bit widths.
- Posting on fid destroy can surprise callers if they expected explicit zero-length commit only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nntpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ns.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ns.c

Prints a shell-reconstructable view of a process namespace.

Key elements:
- Usage: `ns [-r] [pid]`.
- Reads `/proc/<pid>/ns`, tokenizes each namespace operation, and prints it with quoting.
- Supports `cd` lines and mount/bind-like records with 3, 4, or 5 fields.
- `xlatemnt` rewrites mounts of `/net/<proto>/<conn>/data` into `proto!remote` form unless `-r` is set.
- `quote` single-quotes strings containing shell-sensitive characters.

Notable behavior:
- Defaults to current process when no pid is supplied.
- Uses `-r` for raw namespace paths without network translation.

Risks and quirks:
- Fixed buffers and maximum 5 tokens match expected `/proc/ns` format.
- Quoting uses rotating static buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/audio/audio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/audio/audio.c

USB audio class driver exposing audio endpoints and control files.

Key elements:
- Supports USB Audio 1.0 and 2.0 descriptor parsing.
- Finds audio control and streaming interfaces, IADs, terminals, clock sources, stream alt settings, isochronous endpoints, format descriptors, and sample-rate ranges.
- `Aconf` extends `Pcmdesc` with endpoint, sample size, terminal, frequency ranges, zero-bandwidth alt setting, and Audio 2 clock ID.
- `setupep` chooses the best matching alt setting for a requested PCM format, sets zero-bandwidth first, sets alt, sets clock, opens endpoint, and programs endpoint device controls.
- Discovers feature-unit controls for mute, volume, bass, mid, treble, AGC, bass boost, and loudness.
- Exposes synthetic files `audioctlU<hname>`, `audiostatU<hname>`, and `volumeU<hname>` through a USB share service.
- `fsread` reports stream on/off state, supported formats, current formats, delay, and control values.
- `fswrite` handles stream on/off, output/input format changes, speed, delay, and feature control changes.

Notable behavior:
- Audio format preference chooses exact matches when possible and otherwise closest/best candidates.
- Audio 2 sample-rate control uses `RANGE`; Audio 1 uses endpoint `SET_CUR/GET_CUR`.
- Volume-like controls are converted between user 0-100 values and hardware min/max/resolution.
- Silence is represented by `0x8000` for 16-bit volume controls.

Risks and quirks:
- `fswrite` initializes `c = epout->aux` before verifying `epout` is non-nil; input-only devices may be sensitive here.
- Some clock-setting failures are ignored because devices do not always require or support them.
- Only the first input and first output endpoint are selected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/audio/audio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/battery/battery.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/battery/battery.c

USB HID battery driver exposing a synthetic battery status file.

Key elements:
- Opens interrupt IN endpoints on a USB HID battery-like device.
- Retrieves and parses the HID report descriptor, switching to report protocol when available.
- Implements generic HID report descriptor parsing with global/local/main item state, collections, push/pop, usage ranges, and report IDs.
- `itemparse` extracts input values from report packets and maps selected HID usages to battery state fields.
- Tracks remaining/full/design/warning capacity, voltage/design voltage, runtime, missing/critical/charging/discharging states.
- `hidwork` reads interrupt reports continuously, parses them under a battery lock, and updates shared state.
- Exposes `battery` read-only file through `threadpostsharesrv`.
- `fsread` prints percentage, units, capacities, warning thresholds, voltages, runtime, and textual state.

Notable behavior:
- Defaults capacity unit to `%` and full capacity to 100.
- If full/design capacity are missing or zero, they are normalized to usable defaults.
- Runtime is formatted as `HH:MM:SS`.
- Multiple interrupt endpoints can start reader processes against the same global battery state.

Risks and quirks:
- The file prints `warncapacity` twice in the numeric fields.
- HID usage handling is selective; unknown but valid battery usages are ignored.
- After repeated endpoint read errors, the driver exits all threads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/battery/battery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/battery/hid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/battery/hid.h

HID constants used by the USB battery driver.

Key elements:
- Defines thread stack size and an unused joystick-style `Maxaxes` constant.
- Defines HID class requests: `Getreport`, `Setreport`, `Getproto`, `Setproto`.
- Defines boot/report protocol constants.
- Defines report type value for output reports.
- Defines HID report descriptor item tags for main, global, and local items.
- Defines main item flag bits for data/constant, array/variable, absolute/relative, wrap, linearity, preference, and null state.

Notable behavior:
- The header is generic HID parsing support, despite the top comment mentioning joystick constants.
- Battery code uses the item tags and flags for report descriptor parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/battery/hid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/cam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/cam.c

USB Video Class camera filesystem front-end.

Key elements:
- Parses UVC video control and video streaming class descriptors from USB descriptors.
- Builds `Cam` objects for video streaming input headers, with indexed uncompressed formats and frames.
- Tracks video-control units by unit ID for use by control logic in companion files.
- Creates one directory per camera stream: `cam<hname>.<ifaceid>`.
- Exposes `ctl`, `formats`, `video`, `frame`, and `desc` files for each stream.
- `formats` reports width, height, bits-per-pixel, fourcc-like format, and frame rates/interval ranges.
- `desc` dumps UVC descriptors and current probe control.
- `ctl` is read/write through external `ctlread`/`ctlwrite`.
- `video` and `frame` use external `videoopen`, `videoread`, `videoflush`, and `videoclose`.
- Posts a USB share service named `<devid>.cam`.

Notable behavior:
- On startup, default frame index and default frame interval are copied into the probe control when available.
- Read state for string files is stored per fid and refreshed on offset zero.
- Opening `frame` passes a flag to `videoopen` to select frame-oriented behavior.

Risks and quirks:
- Error message `"the front fell off"` is used for invalid fid/file state.
- Realloc size bookkeeping uses descriptor indexes directly, leaving sparse arrays for missing indexes.
- Relies on companion UVC files (`uvc.h`, `dat.h`, `fns.h` implementations) for controls and streaming.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/cam/cam.c -->