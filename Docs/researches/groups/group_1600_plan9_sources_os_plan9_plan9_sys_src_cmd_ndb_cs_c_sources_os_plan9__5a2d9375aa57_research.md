# Group Research: group_1600_plan9_sources_os_plan9_plan9_sys_src_cmd_ndb_cs_c_sources_os_plan9__5a2d9375aa57

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/cs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/cs.c

Implements Plan 9’s 9P connection server mounted as `/net/cs`. Clients write dial strings or generic NDB queries to the single `cs` file and read back translated clone paths such as `/net/tcp/clone host!port`.

Key structures are `Mfile` for per-fid request/reply state, `Job` for active 9P messages and flush tracking, and `Network` for network-specific lookup/translation hooks. Built-in networks include `tcp`, `udp`, `icmp`, `icmpv6`, `rudp`, `ssh`, and `telco`.

Main flow: `main()` initializes NDB state and mounted networks, `mountinit()` publishes `#s/cs...`, `io()` dispatches 9P requests, `rwrite()` parses commands or dial strings, `lookup()` tries default or explicit networks, and `rread()` streams cached replies. DNS lookups are delegated through `dnsquery()` with slave processes so blocking DNS does not stall the 9P loop.

NDB integration includes `/lib/ndb` plus `/net/ndb`; `ipid()` derives `sysname` from environment, DHCP-provided `/net/ndb`, local IP, or ethernet address. `iplookup()` resolves service names, direct IPs, `$attr` expansions, DNS names, local database entries, and interface-local address ordering. `genquery()` handles `!attr=val...` and `!ipinfo...` queries.

Notable risks and maintenance points: fixed-size request/reply buffers cap responses; `rwrite()` mutates request data in place; concurrency uses Plan 9 `rfork(RFMEM)` plus `setjmp`/`longjmp`, so shared global state and locks are delicate. Some IPv6 behavior is bolted onto IPv4-era paths, and reverse-query convenience code lives elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/cs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/csquery.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/csquery.c

Small interactive/batch client for `/net/cs`. It opens the selected connection-server file, writes a dial string, seeks back to offset zero, and prints all reply data.

Command-line behavior defaults to `/net/cs`; with a server path and address arguments it queries each address; without address arguments it reads lines from stdin with a prompt. `-s` suppresses reply printing and only records error status.

Dependencies are only libc/Biobuf and the 9P file interface exposed by `cs.c`; it does not parse replies, translate services, or access NDB directly.

Risk surface is minimal. Input lines are passed verbatim except newline removal; failures are reported via `%r`. Buffering is fixed at 128 bytes per read, but reads loop until EOF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/csquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dblookup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dblookup.c

Converts Plan 9 NDB tuples into DNS resource records and maintains database-derived cache/area state for the DNS daemon. It is the bridge between `/lib/ndb`/`/net/ndb` records and `RR` objects from `dns.h`.

`dblookup()` handles class/type filtering, `Tall` expansion, exact/lowercase/wildcard lookups, cached-db mode, owner assignment, and response-code decisions for names outside served areas. `dblookup1()` maps DNS types to NDB attributes and record constructors, including A/AAAA, CNAME, MX, NS, PTR, SOA, SRV, NULL, TXT, and AXFR/IXFR stubs.

Record constructors parse tuple attributes into typed RR payloads. SOA construction derives serials from database mtimes unless overridden, fills timers, builds mailbox names, and attaches `dnsslave` servers for notification.

Database caching is handled by `db2cache()`, `dbfile2cache()`, `dbtuple2cache()`, and `dbpair2cache()`. Reloads compare backing-file mtimes, reopen changed NDBs, rebuild owned/delegated areas, refresh straddle-server configuration, age old DB records, mark authoritative records in served zones, and synthesize reverse PTRs.

Resolver support includes `dnsservers()` and `domainlist()` from `@dns`/`dnsdomain` NDB data, rejection of local/self DNS servers, bad-delegation detection, inside/outside namespace selection for straddling servers, and local synthetic DNS server records.

Reverse PTR synthesis covers IPv4 `in-addr.arpa`, RFC2317 classless delegation, and IPv6 `ip6.arpa` nibble domains. Risks include extensive global state under `dblock`/`dnlock`, mutable static cached tuples for local DNS configuration, special-case straddle logic, and partially implemented AXFR/IXFR handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dblookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dn.c

Core DNS cache, domain-name table, RR allocation/copy/free, activity accounting, formatting, and aging logic. It owns the global `DN *ht[HTLEN]` hash table, `dnlock`, RR type/response/opcode name tables, stats dumping, and most shared memory lifecycle rules.

`dnlookup()` interns domain names by case-insensitive hash. `rrattach()` and `rrattach1()` insert RRs into a domain’s list while preserving type grouping, authority priority, duplicate suppression, negative/positive replacement, PTR ordering, and anti-spoof rules for local cached-db zones. `rrlookup()` returns copied records in priority order: authoritative DB, live authoritative network, live unauthoritative network, unauthoritative DB, then fallback positives.

Aging and cleanup are present but effectively disabled by huge defaults because comments say prior aging corrupted the cache. Functions still exist for explicit aging, DB-record expiration, mark/sweep of unreferenced names, and “never age” marking for DB-derived roots.

Activity control (`getactivity()`/`putactivity()`) gates concurrent resolver work and runs refresh/aging only when alone. `slave()` forks shared-memory workers for blocking work, with explicit comments about avoiding deadlock and stack-copy assumptions.

Formatting functions `%R` and `%Q` print human-readable and attribute-value forms of RRs. Allocation helpers handle deep copies and freeing for SOA/SRV/KEY/SIG/CERT/NULL/TXT payloads, with magic fields and memory poisoning for bug detection.

Risks are high because many modules depend on `dnlock` discipline and shared `RR` ownership semantics. Several helpers abort if called without expected locks. Forking with shared memory, `setjmp`, cached pointers, and disabled aging all make this a fragile but central subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnarea.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnarea.c

Maintains DNS authority areas derived from SOA records. Two global lists are used: `owned` for zones served locally and `delegated` for delegated subareas excluded from local authority.

`inmyarea()` checks whether a name is under an owned area and not under a delegated area. `addarea()` classifies SOA tuples by whether the `soa` tuple value is empty, stores a copied SOA RR, sets notify/refresh flags, and logs new areas in debug mode. `freearea()` frees area lists and their SOA copies.

`refresh_areas()` runs `zonerefreshprogram zone-name` for areas marked `needrefresh`; successful child completion clears the flag. This is used by notify handling and database reload cycles.

Risks are mostly ownership and locking: SOA records are copied under `dnlock`, and `freearea()` frees RRs while briefly holding `dnlock`. External refresh execution is synchronous per area.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnarea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnnotify.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnnotify.c

Implements DNS NOTIFY receive and send support for zone changes. `dnnotify()` handles an incoming NOTIFY message, moves the SOA question to the reply, validates that refresh is configured and the question is SOA, checks whether the zone is in a local area, and marks the area for refresh when serials differ.

Outgoing notification is handled by `send_notify()`, which builds an `Onotify` DNS request, resolves slave hostnames to A or AAAA if needed, sends UDP notify packets up to three times, and accepts any matching NOTIFY response. `notify_areas()` sends to all `dnsslave` servers listed on each area SOA and clears `neednotify`.

`notifyproc()` forks a shared-memory background process, marks its `Request` as slave to avoid further subprocess spawning, and wakes every minute to notify updated areas under activity accounting.

Risks include limited validation of responses beyond ID/opcode, synchronous serial comparison against the incoming SOA question, and reliance on `zonerefreshprogram`/area state owned by other modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnresolve.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnresolve.c

Full recursive resolver implementation for RFC1035/RFC1123-style DNS queries. It coordinates cache lookups, CNAME chasing, nameserver discovery, UDP/TCP transport, retry timing, negative caching, delegation processing, and straddling inside/outside network behavior.

`dnresolve()` handles search domains for unrooted single-label names, recursion-depth protection, direct lookup, CNAME retries, status propagation, and answer randomization. `dnresolve1()` checks cache/database authority before issuing external queries through a heap-allocated `Query`.

`Query` and `Dest` are carefully allocated off-stack because `slave()` forks shared-memory workers and stack-local locks/arrays would diverge. Resolver transport uses `udpport()`, `mkreq()`, `readnet()`, `readreply()`, `mydnsquery()`, `xmitquery()`, `tcpquery()`, and `queryns()`. UDP replies with `Ftrunc` trigger TCP retry.

Nameserver selection uses cached A/AAAA, DB hints, recursive lookup of nameserver addresses, multicast/self-address rejection, and inside/outside filtering for straddling servers. `netquery()` limits duplicate concurrent queries per `(domain,type)` with per-DN locks and `Maxoutstanding`.

`procansw()` incorporates answer, authority, and additional RRs into cache, handles bad delegations, strips SOA from authority for negative-cache processing, recurses on better NS referrals, and caches negative responses via `cacheneg()`.

Wait times are weighted by estimated likelihood of RR existence to reduce delays for low-probability CNAME/AAAA queries. Risks include many interleaved ownership transfers of RR lists, global stats mutation, timeouts via `alarm`, and correctness reliance on Plan 9 network “headers” UDP format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnresolve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.c

Main 9P DNS service mounted as `/net/dns` and optional UDP DNS server supervisor. It parses daemon flags, initializes cache/database state, publishes `/srv/dns...`, restarts child DNS service processes, and handles local 9P file requests.

Global configuration (`Cfg cfg`) is set from options: serving UDP (`-s`), resolver/forward-only mode (`-r`/`-F`), no recursion (`-R`), straddling inside/outside networks (`-o`), debug/testing, cache target, forwarding targets, NDB file, alternate net mount, and zone refresh program.

The 9P file contains one synthetic file `dns`. Writes accept commands (`age`, `debug`, `dump`, `poolcheck`, `refresh`, `restart`, `stats`, `target`) or DNS queries of the form `domain type`. Replies are buffered in `Mfile.reply` with offsets per RR so reads return one RR at a time.

`io()` dispatches 9P requests under request activity tracking and supports slave process escape through `setjmp`. Query writes call `dnresolve()` and `respond()` formats answers as `%R` or `%Q` when request name is prefixed by `!`.

Process model is explicit: a restarter creates `/srv/dns`, then repeatedly forks a child with separate namespace; the child may start UDP and notify processes and serves 9P until restart. This avoids deadlock from serving its own namespace.

Risks include complex restart/remount behavior, shared global cache across forked processes, fixed reply limits (`Maxreply`, `Maxrrr`), and management commands exposed through the writable 9P file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.h

Shared header for the Plan 9 DNS/NDB stack. It defines DNS protocol constants, RR type IDs, class/opcode/rcode/flag values, timing constants, payload limits, hash sizes, request timeouts, parallelism limits, and magic numbers.

Core data structures include `Request`, `Querylck`, `DN`, `RR`, DNSSEC-adjacent payload structs (`Key`, `Cert`, `Sig`, `Null`), `Txt`, `Server`, `SOA`, `Srv`, `DNSmsg`, `Area`, `Cfg`, and `Stats`. `RR` is a compact tagged structure using unions keyed by type/negative state.

The header declares globals shared across daemon, resolver, database, server, notify, and transport files: cache config, mount point, time bases, area lists, stats, debug flags, and zone refresh state. It also declares all cross-module functions for cache management, DB lookup, server dispatch, conversion, notify, resolver transport, and logging.

Important design signal: ownership of RR lists is manual and lock-sensitive. Many APIs return copied lists or transfer ownership; callers frequently free with `rrfreelist()` under `dnlock` depending on cached/shared status.

Risks include broad global coupling and typo-preserved protocol names such as `Runimplimented`. The header is the central contract; changing struct layout or enum values affects packet conversion, cache comparison, formatting, and all server paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsdebug.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsdebug.c

Interactive/batch DNS resolver debugger built on the same resolver/cache code as `dns`. It can query default configured DNS servers or an explicit `@server`, optionally with resolver mode and external `/net.alt` mode.

It initializes DNS structures, installs a pretty `%R` formatter, opens the database, and either executes command-line queries or runs an interactive prompt. Each prompt flushes cache with `dnpurge()` before querying.

`doquery()` chooses default `ip` vs `ptr`, handles trailing-root dots, synthesizes IPv4 `in-addr.arpa` names for PTR queries, creates a `Request`, and calls `dnresolve()`. Output prints separator lines and formatted answers.

Explicit server support is implemented by `setserver()`, `squirrelserveraddrs()`, `preloadserveraddrs()`, and `getdnsservers()`: server hostnames are resolved first with resolver mode temporarily disabled, then preloaded into cache for subsequent resolver-mode queries.

This tool reuses production resolver paths but replaces logging with human-readable print output. Risks are debugger-specific: IPv6 reverse synthesis is marked TODO, and temporary server state is global.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnserver.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnserver.c

DNS request-answering logic shared by UDP and TCP servers. `dnserver()` takes a parsed request message, creates one reply for one question, validates request code/type/class, enforces recursion policy, resolves answers, attaches authority/additional data, and sets DNS flags/response codes.

For local authoritative areas, AXFR/IXFR are rejected here except TCP AXFR is handled separately in `dnstcp.c`. Non-authoritative requests with recursion disabled return empty success. Recursive and nonrecursive lookup both pass through `doextquery()`, which calls `dnresolve()` and strips negative cached RRs from public answers.

Authority handling adds NS records when known, SOA records for local negative answers, and cached negative SOA owners when available. `hint()` adds A/AAAA glue for NS/MX/mail records from cache or DB.

Risks include pointer assumptions around `reqp->qd`, RR list mutation/ownership, and response-code propagation only when expected DN/cache state exists.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsquery.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsquery.c

Interactive client for `/net/dns`. It mounts `/srv/dns` if `/net/dns` is unavailable, writes queries to the DNS 9P file, seeks back, and prints all returned chunks.

Input defaults to `ip` queries for names and `ptr` for numeric IPs. IPv4 PTR input without `.arpa` is rewritten into `in-addr.arpa ptr`; IPv6 reverse conversion is explicitly TODO. `-x` switches to `/net.alt/dns` and `/srv/dns_net.alt`.

The file is operational glue rather than resolver logic. It depends on the daemon’s 9P protocol and on `ipattr()` to distinguish numeric addresses.

Risks are small: fixed 1024-byte buffers, simple whitespace trimming, and no parsing of structured RR output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnstcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnstcp.c

Standalone TCP DNS server process, intended to be run for a single TCP connection. It reads length-prefixed DNS messages from stdin, answers normal queries via `dnserver()`, and handles AXFR zone transfers directly.

`main()` parses resolver/no-recursion/db/net options, initializes DNS cache, reads caller address from an optional connection directory, loads DB cache, then loops over TCP DNS messages with long request abort time. Each question is handled as either `Taxfr` via `dnzone()` or normal `dnserver()` plus `reply()`.

`dnzone()` streams AXFR by sending SOA first, then walking the global DN hash table breadth-first by label depth for records in-zone, skipping negative and SOA records, and finally sending SOA again. It uses cached DB contents, so `cfg.cachedb` is enabled.

On exit, `refreshmain()` writes `refresh` to the main `/net/dns` file. Risks include direct traversal of global `ht`, shallow copying RR structs for zone streaming, and broad reliance on cache already being authoritative/current.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnstcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnudpserver.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnudpserver.c

UDP DNS server loop for external DNS requests. It announces UDP port 53 in Plan 9 “headers” mode, parses incoming DNS packets, suppresses client retransmissions, dispatches query/notify operations, and writes replies back with UDP headers.

`clientrxmit()` records in-progress `(client header, id, owner, type)` tuples to ignore duplicate retransmissions while a request is active. `dnudpserver()` forks a shared-memory child, loops reading UDP packets with timeout, validates questions/opcodes, sets `Request` metadata, and calls `dnserver()` or `dnnotify()` per question.

Forwarding targets configured by `-T` in `dns.c` are stored as `Forwtarg` entries. `redistrib()` copies incoming packets to these debugging/forwarding UDP targets, redialing failed ports periodically.

`reply()` serializes the DNS response into the UDP payload with `Maxdnspayload` limit and writes it through the original header. Risks include shared global `inprog` without locks because the loop is single-threaded until slave forking, fixed-size forwarding packet buffer, and duplicated activity/fork lifecycle complexity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/dnudpserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/inform.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/inform.c

Implements a small RFC2136 DNS UPDATE client used to “inform” Windows 2003 DNS servers of the local host’s A record. It reads local NDB data, builds a DNS update packet manually, sends it over UDP, and checks the response code.

The program finds `$sysname`, opens NDB, queries `dom`, `dnsdomain`, `ns`, and `inform`, then chooses `inform` over `dom` when present. It obtains the local IPv4 address from `myipaddr()`, dials the configured DNS server, writes an update deleting the old A record and adding the current one with a 25-hour TTL.

Packet helpers `p16`, `p32`, `pmem`, and `pname` manually encode DNS fields/names. It waits up to three seconds for a response with matching transaction ID and treats response code 7 as a nonfatal “already exists” warning.

Risks include manual packet construction with no bounds checks on encoded names, IPv4-only update data, and use of low response-code mask (`& 7`) rather than full DNS extended code handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/inform.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/ipquery.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/ipquery.c

Tiny command-line wrapper around `ndbipinfo()`. It opens an NDB file/root, searches by `attr value`, requests one or more returned attributes, and prints `attr=value` pairs on one line.

It accepts `-f ndb-root`; otherwise it uses default NDB files. It requires at least one search attribute, value, and returned attribute.

Risks are minimal. It does not handle missing result specially beyond printing a blank line and frees the returned tuple list unconditionally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/ipquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkdb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkdb.c

Converter from merged UUCP/Internet-style host data on stdin into Plan 9 NDB entries on stdout. It classifies tokens as comments, system names, Datakit names, IP addresses, or domain names, groups related tuples, and prints normalized NDB records.

Classification helpers identify Datakit names by alnum plus slash, domains by dot plus alphabetic/hyphen chars, and IPs by dotted digits. `tprint()` emits a preferred `sys = name` first, then indented `dom=`, `ip=`, `dk=`, and additional `sys=` attributes. Some Datakit console paths add `flavor=console`.

The main loop merges adjacent lines that share a domain already in the current tuple set; otherwise it flushes the current NDB entry and starts a new one. Duplicate tuple/type pairs are skipped.

Risks include fixed `tup[64][64]` storage with unchecked `strcpy`, legacy domain/IP parsing, and assumptions about old Datakit naming conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhash.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhash.c

Builds an on-disk hash sidecar for a given NDB file and attribute. It parses the whole database twice: first to count matching attributes and size an in-memory hash table, then to insert file offsets for matching values.

`enter()` hashes attribute values with `ndbhash()`, stores direct pointers where possible, and creates chained entries using `NDBCHAIN`/`NDBNAP` pointer encoding. The output file is named `file.attribute` and starts with database mtime and hash length followed by the pointer table/chains.

After writing, it verifies the source file’s qid path/version still match the opened database; if the DB changed underfoot it removes the generated hash and exits with `changed`.

Risks include whole-hash memory allocation sized for worst case, pointer-format coupling to NDB macros, and no atomic temporary rename for the generated sidecar.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhosts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhosts.c

Generates legacy host/DNS export files for a selected domain from NDB sources. Default domain is `research.att.com`; default input files are `/lib/ndb/local` and `/lib/ndb/friends`.

`parse()` reads NDB entries with IP data, skips console-flavored entries, keeps only entries in the selected domain or with `ipnet`, and records each IP tuple in a fixed global array. Output functions generate DNS-style A/CNAME/MX records, equivalence domain lists, and text host/net records.

`main()` writes `/lib/ndb/db.<domain>`, `/lib/ndb/equiv.<domain>`, and `/lib/ndb/txt.<domain>`, with a generated-file warning in the DB output. Some old hosts-file output is commented out.

Risks include fixed `x[4096]`, in-place uppercasing of tuple values, domain-specific formatting width assumptions, and hard-coded `/lib/ndb` output paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhosts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/query.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/query.c

Generic NDB query tool. It searches an NDB database for `attr value` and either prints full matching entries, a returned attribute, or all returned-attribute values depending on flags.

`-f` selects the NDB file, `-a` requests all matches instead of first matching returned attribute, and `-m` prints multiple values from the first returned entry. An optional fourth positional argument repeats the search multiple times, apparently for testing/timing.

The main logic uses `ndbgetvalue()` for first returned attribute, `ndbsearch()`/`ndbsnext()` for all entries, and prints through a buffered `Biobuf`.

Risks are low; semantics differ subtly among no returned attr, returned attr with `-a`, and returned attr without `-a`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/query.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/netstat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/netstat.c

Plan 9 network status utility. It lists active protocol conversations under `/net` or a supplied network root, optionally restricted to interfaces (`-i`), numeric output (`-n`), or selected protocols (`-p proto`).

For protocol stats, `nstat()` reads protocol directories and calls `pip()` on each conversation. `pip()` reads `status`, `local`, and `remote`, translates ports via `csgetvalue()` unless `-n`, and translates remote IPs to domain names through connection server lookup when possible.

`pipifc()` uses `readipifc()` to print interface device, MTU, IP, mask, network, and packet/error counters, dynamically sizing IP columns.

Risks include fixed buffers for status/local/remote paths and contents, assumptions about Plan 9 network file layout, and translation dependencies on `/net/cs` that can fail or block.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/netstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/news.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/news.c

User-facing Plan 9 `news` command for `/lib/news`. It prints all news (`-a`), names of new items (`-n`), explicit items, or default items newer than the user’s `$home/lib/newstime`, updating that timestamp file on default runs.

`read_dir()` gathers directory entries from `/lib/news`, ignores configured names, optionally records the previous newstime marker, updates the marker file, and sorts entries newest first. `eachitem()` emits entries until it reaches the marker unless printing all.

`print_item()` prints a heading with item name, modifying user, and timestamp, then prints file contents with tab-indented nonblank lines and collapsed leading blank pages. `note()` emits compact names-only output.

Risks are small but legacy: fixed path buffers, no allocation failure handling, and a timestamp marker based on directory file mtime rather than persisted state content.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/news.c -->