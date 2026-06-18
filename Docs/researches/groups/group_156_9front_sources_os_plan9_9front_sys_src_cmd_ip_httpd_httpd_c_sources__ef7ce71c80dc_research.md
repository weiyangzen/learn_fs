# Group Research: group_156_9front_sources_os_plan9_9front_sys_src_cmd_ip_httpd_httpd_c_sources__ef7ce71c80dc

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpd.c

Main Plan 9 httpd listener. It parses server options, optionally loads TLS certificate/chain, forks into the background, opens logs and rewrite/content tables, becomes user `none`, then announces an HTTP or HTTPS TCP service.

Each accepted connection is served in a child process with parsed `HConnect` state. Requests pass through magic URI handling, rewrite redirects, virtual-host masquerading, authorization, directory/index normalization, and static file transfer via `sendfd`.

Magic requests under `/magic/<program>/...` exec `/bin/ip/httpd/<program>` with preserved request metadata, buffered input, log descriptors, webroot, netdir, scheme, port, and remote address. Redirect and MIME/state tables are periodically refreshed after batches of accepted connections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpsrv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpsrv.h

Shared private header for httpd server and magic helper programs. It defines `HSPriv`, rewrite modifier constants, redirect flags, log globals, webroot/netdir globals, and prototypes for allocation, static file serving, content classification, redirects, logging, initialization, hints/stats, and authorization.

This header is the coupling point between the standalone listener, CGI-like `/magic` programs, and common helpers such as `sendfd.c`, `redirect.c`, and `init.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpsrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/imagemap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/imagemap.c

Magic helper for old-style server-side image maps. It accepts GET/HEAD, parses the query coordinates, opens the map file named by the URI, and selects a destination URL using NCSA or CERN-style map records.

Supported shapes include rectangles, circles, polygons, points, and default targets. It returns a redirect to the selected target or emits a small HTML “Nothing Found” response when no target matches.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/imagemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/init.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/init.c

Common initializer used by `/bin/ip/httpd/*` magic helper programs after `httpd.c` execs them. It reconstructs an `HConnect` from command-line arguments: buffered request input, domain, remote address, scheme, port, log fds, netdir, webroot, original request line, method, version, URI, and optional search string.

It installs HTTP formatters, initializes input/output Hio streams, sets conservative defaults, reopens syslog, parses HTTP version text, marks helpers as close-after-response, and approximates request time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/log.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/log.c

HTTP logging implementation. `logit` writes syslog messages, prefixing the remote system when available from `HSPriv`.

`writelog` writes two styles of access log: a verbose alternating daily trace log with request headers and request metadata, and a Common Log Format-style log in `logall[2]` for `Reply:` messages. It extracts status and response size from selected reply format strings used by `sendfd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/man2html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/man2html.c

Magic helper and standalone converter for Plan 9 manual pages. It can convert a direct man-page URI using `troff -manhtml | troff2html`, serve section indexes, look up page names through `/sys/man/*/INDEX`, and handle query-based man or keyword searches.

It rejects `..` in man-page URIs, redirects directories and lowercase variants, binds `/usr/web/sys/man` onto `/sys/man`, and emits HTML search/result pages. In magic mode it validates GET/HEAD and expectation headers, then logs generated output length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/man2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_find.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_find.c

Magic helper invoked from Netlib search forms. It parses `db` and `pat` query fields, mounts the selected searchfs database from `/srv/netlib_*` at `/mnt`, writes a `search=` request, then streams matching records as HTML.

The database table controls log labels, maximum hits, backing service, record formatter, and page trailer. Formatters preserve plain records, turn Netlib `file:`/`lib:` fields into links, and link BibNet `URL` fields. HEAD requests return headers and no body.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_history.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_history.c

Magic helper that renders historical versions of a Netlib file under `/usr/web/historic`. Query fields select `file` and optional `diff`; it rejects parent-directory traversal and overly long names.

It searches backwards by day for prior snapshots, lists up to 50 versions, or 10 with diffs. Diff mode gunzips `.gz` snapshots into temporary files and runs `diff -nb` between adjacent versions, embedding results in HTML.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/redirect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/redirect.c

Rewrite-table loader and lookup engine for httpd. `redirectinit` reads `/sys/lib/httpd.rewrite`, tracks qid changes, strips comments, and populates separate hash tables for URI redirects and virtual-host-to-webroot-prefix mappings.

Replacement prefixes may be decorated with silent, permanent, subordinate, or exact-only modifiers. `redirect` finds the longest path prefix match and returns a per-request allocated replacement; `masquerade` maps Host headers to implicit webroot subdirectories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/redirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/save.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/save.c

Magic helper for simple web form logging. GET uses the query string and POST reads the request body, truncates at the first newline, caps each logged request at 24 KiB, and appends `at <time> <data>` to `/usr/web/save/<uri>.data`.

It serves `/usr/web/save/<uri>.html` as the response through `sendfd`. The `.data` file can use exclusive-use mode; `openLocked` retries briefly when the file is locked to avoid interleaved appends.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/save.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/sendfd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/sendfd.c

Static-file response engine for httpd. It classifies content from URI suffix or data sniffing, generates ETags from qid path/version, checks Accept/Content-Encoding, conditional request headers, and If-Range, then emits 200, 206, 304, 406, 412, or 416 responses.

It supports HEAD, full-body transfer, single byte ranges, and multipart byte ranges with MIME boundaries. `fixrange` normalizes suffix ranges, clamps ranges to file length, removes invalid ranges, and merges adjacent/overlapping ranges while preserving request order where possible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/sendfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/webls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/webls.c

Magic helper and standalone tool for HTML directory listings. It loads allow/deny regexes from `/sys/lib/webls.allowed` and `/sys/lib/webls.denied`, then lists only permitted directories.

`dols` binds webroot to `/` in magic mode, reads and sorts directory entries, formats Plan 9 mode/type/dev/uid/gid/length/mtime fields, links subdirectories back through `/magic/webls?dir=...`, and includes parent navigation only when permitted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/webls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/wikipost.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/wikipost.c

POST-only magic helper for wiki edits. It parses form fields including title, version, text, service, comment, author, and base URL; decodes URL escaping with a Latin-1 fallback heuristic; removes carriage returns; and rejects dangerous service/title/comment inputs.

It mounts a private or `/srv/wiki.<service>` wiki filesystem at `/mnt/wiki`, writes the edit record to `/mnt/wiki/new`, commits with a zero-length write, reads the resulting page name, and returns a `303 See Other` redirect to the new index or error page.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/wikipost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpfile.c

9P filesystem that exposes an HTTP URL as a read-only file. It uses `/mnt/web` to issue HEAD for content length and GET requests with Range headers for block-sized reads.

The server maintains a block cache and an in-progress queue, serializes HTTP range fetches through worker threads, satisfies queued 9P read requests from cached blocks, and supports flush by removing pending reads. It can post a srv file or mount at a mount point, with configurable cache size and displayed filename.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/icmp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/icmp.h

Shared ICMP constants and packet structures for IPv4 and IPv6 users such as `ping.c` and IPv6 configuration code. It defines common ICMPv4 message types, ICMPv6 error/informational/router-neighbor message types, header size, an IPv4 header layout, and a common echo-style ICMP payload header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/icmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcp.c

DHCPv4 client engine for `ipconfig`. It builds Discover/Request/Release BOOTP packets, opens UDP port 68 in header mode, tracks selecting/requesting/bound/renewing/rebinding states, retransmits with timeouts, and can spawn a watcher to renew or reacquire leases.

It validates incoming BOOTP/DHCP packets by transaction id, op, magic cookie, and option bounds. ACK processing fills local address, mask, gateway, DNS/NTP, host/domain names, lease time, server id, and Plan 9-specific vendor options for fs/auth/address/mask/gateway.

The file also defines DHCP option metadata and helpers for adding, parsing, formatting, and requesting options, including domain-name decoding through `gnames` and extra requested options stored for `/net/ndb`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcpv6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcpv6.c

DHCPv6 client used by IPv6 RA processing when managed configuration is indicated. It binds UDP port 546 on the link-local address, sends Solicit/Request or Renew/Rebind transactions to `ff02::1:2`, and includes client DUID, IA_NA, IA_PD, requested DNS servers, and server id when appropriate.

Responses are checked by transaction id and expected message pair. It handles server/client identifiers, IA_NA addresses, IA_PD delegated prefixes, DNS server options, status codes, prefix/address lifetimes, and computes the lease timeout from T1/preferred lifetimes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcpv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipconfig.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipconfig.h

Shared declarations for `ipconfig`. It defines verb/media constants, the central `Conf` structure containing local interface state, learned IPv4/IPv6/DHCP/RA parameters, server addresses, client IDs, DUID, and prefix lifetimes, plus queued device control messages.

It declares globals and cross-file functions for DHCPv4, DHCPv6, IPv6 RA/prefix handling, route updates, ndb updates, utility parsing/formatting, warning/debug output, and PPP binding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipv6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipv6.c

IPv6 configuration support for `ipconfig`. It initializes RA defaults, parses static prefix and RA parameters, derives link-local addresses from Ethernet addresses, adds IPv6 addresses with duplicate-neighbor detection, and configures kernel RA parameters.

Host-side RA handling listens for router advertisements, processes link-layer address, MTU, prefix, RDNSS/DNSSL, and Plan 9 fs/auth options, manages learned route/prefix lifetimes, updates `/net/ndb`, refreshes cs/dns, and invokes DHCPv6 when the managed flag is set.

Router-side support sends router advertisements, responds to router solicitations, includes current global prefixes and ndb-derived DNS/fs/auth/domain options, sends final zero-lifetime RAs when disabled, and coordinates send/receive RA daemons.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipv6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/main.c

Main `ipconfig` command. It parses media, device, verbs, IPv4/IPv6 addresses, DHCP flags, ndb configuration, route options, MTU, DNS, DUID, and control messages; binds or reuses an IP interface; then dispatches add, delete, unbind, IPv6 prefix, or RA actions.

IPv4/IPv6 add paths configure addresses, default routes, proxy/translation flags, DHCP or static settings, and refresh `/net/cs` and `/net/dns`. DHCP-learned and ndb-learned data is written into `/net/ndb` with duplicate filtering and checksum-based rewrite suppression.

The file also owns route-control formatting, primary/non-primary behavior, ndb lookups by Ethernet/IP, address/name packing helpers, warning/debug output, random jitter, interface discovery, and cleanup/removal paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ppp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ppp.c

PPP binding bridge for `ipconfig`. `pppbinddev` forks and execs `/bin/ip/ppp` or `/ppp` with `-uf -p <dev> -x <netmtpt>` and optional baud rate, waits for PPP setup to complete, and then marks `noconfig` because the PPP process performs the IP configuration itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ppp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/linklocal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/linklocal.c

Utility that prints an IPv6 link-local address, or a 6to4 address with `-t ipv4`, for each Ethernet MAC address argument. It converts MAC-48 to EUI-64 by inserting `ff:fe` and toggling the universal/local bit, then formats either `fe80::/64` or `2002:<ipv4>::/48`-derived addresses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/linklocal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/measure.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/measure.c

Ethernet traffic sampler for a target MAC address. It opens an Ethernet device in promiscuous mode, reads timestamped frames, recognizes IPv4/Ethernet variants, and accumulates inbound/outbound byte and packet counts by IP protocol.

At each sample interval it prints epoch time, elapsed capture time, and counters for all IP traffic plus selected multicast, UDP, and TCP protocols. Options enable debug output and limit the number of samples.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/measure.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ping.c

IPv4/IPv6 ping implementation. It chooses ICMP or ICMPv6, sends echo requests with sequence numbers and patterned payload data, records send times in a locked request list, and receives replies in a forked process.

It reports RTT, average RTT, TTL, optional source/destination addresses, corrupted replies, lost messages, and final loss count. Options control IPv6, address printing, quiet/lost-only modes, interval, randomized interval, flood mode, message count, size, and wait timeout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/block.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/block.c

Small PPP block allocator. `allocb` allocates a `Block` with 128 bytes of leading pad for protocol/header prepending, `resetb` positions read/write pointers after the pad, and `freeb` poisons pointers before freeing blocks whose data buffer is inline with the `Block`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/compress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/compress.c

Van Jacobson TCP/IP header compression for PPP. It keeps transmit and receive header state tables, compresses eligible non-fragmented TCP ACK/data packets by encoding changed sequence, ack, window, urgent, and IP id fields, and emits compressed, uncompressed-VJ, or plain IP protocol ids.

Decompression restores headers from saved state, handles explicit/implicit connection ids, reconstructs TCP/IP length and checksum fields, and discards packets after line errors until state is resynchronized. Negotiation records whether connection ids are compressed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doclient -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doclient

Tiny rc helper for PPP testing. It binds IP stack `#I2` onto `/net.alt2` and starts a connection server for the `.alt2` network namespace.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doclient -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doserve -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doserve

Tiny rc helper for PPP service-side testing. It binds IP stack `#I1` onto `/net.alt`, starts `ndb/cs` for `.alt`, and runs `aux/listen` on `/net.alt/tcp` with `/rc/bin/service`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doserve -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/dotest -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/dotest

PPP test launcher rc script. It ensures `/net.alt` and `/net.alt2` are bound to `#I1` and `#I2`, kills prior `8.out` and `testppp` processes if present, then starts `testppp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/dotest -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ipaux.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ipaux.c

PPP checksum helpers. `ptclcsum` computes a protocol checksum over a `Block` slice using `ptclbsum`, bounded by block length, and returns the complemented 16-bit result. `ipcsum` computes the IPv4 header checksum over the header length encoded in the first byte.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ipaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/mppc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/mppc.c

Microsoft Point-to-Point Compression/encryption support for PPP. The compressor keeps 8 KiB history arenas and a rolling hash table, emits literal/copy codes, handles history reset/front flags, packet counts, optional RC4 encryption, and falls back to uncompressed packets when compression expands data and encryption is not required.

The decompressor validates packet counts, handles reset/front/encryption flags, updates RC4 keys on count boundaries, reconstructs compressed streams into history, returns reset requests on loss or decode failure, and extracts the original PPP protocol from the decompressed frame.

It also provides MPPE-style asymmetric key derivation and key updates using SHA-1 plus RC4, and includes diagnostic IP/TCP/UDP checksum/history validation helpers used for debugging decompression correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ppp/mppc.c -->