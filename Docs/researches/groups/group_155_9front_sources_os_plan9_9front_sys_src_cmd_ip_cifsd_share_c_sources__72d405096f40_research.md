# Group Research: group_155_9front_sources_os_plan9_9front_sys_src_cmd_ip_cifsd_share_c_sources__72d405096f40

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/share.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/share.c

Implements CIFS share mapping for `cifsd`. `mapshare` derives a share name from a requested SMB path, rejects unsafe names, special-cases `local` and `IPC$`, and lazily creates a `Share` record with filesystem/service metadata.

`run9fs` forks `/bin/9fs <share>` to populate `/n/<share>` for normal disk-tree shares, redirecting child output to `/sys/log/<progname>`. The share list is process-global and reused by name.

Notable dependencies: `unixidmap`, `logit`, `strtr`, Plan 9 namespace convention `/n/<name>`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/share.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/smb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/smb.c

Main SMB/CIFS command dispatcher for `cifsd`. It handles negotiation, NTLM challenge setup, session setup/logoff, tree connect/disconnect, file open/create/read/write/close, directory creation/removal, rename/delete, metadata query/set, echo, transactions, and transaction2 subcommands.

The implementation maps SMB operations directly to Plan 9 file operations through helpers such as `createfile`, `getfile`, `xdirstat`, `openfind`, `readfind`, `dirwstat`, `pread`, and `pwrite`. It supports Unicode names, large files, NT status responses, NT create, Trans2 query/set path/file/fs information, directory enumeration levels, and CIFS Unix extensions for basic stat fields.

Authentication state is global per process/session: `smbnegotiate` may obtain an NTLM challenge, `smbsessionsetupandx` validates it with Plan 9 auth, changes connection ownership, and sets a hashed session UID. `smbcmd` enforces negotiation order, login completion, and UID checks before dispatch.

Limitations are explicit: many SMB commands return not supported or not implemented, locking is parsed but not actually enforced, and transaction responses are single-buffer responses constrained by the client buffer size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/smb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/tree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/tree.c

Maintains SMB tree IDs, file IDs, and search IDs. It uses dynamically grown arrays of pointers, assigning one-based IDs with `newid`, clearing slots on delete, and preserving object references through `ref` counters.

`connecttree` maps a requested service/path to a `Share`, validates service type, allocates a `Tree`, and returns a TID. `disconnecttree` and `logoff` release all files/finds associated with active trees.

`getfile`, `getpath`, and `getfind` are the primary request-time resolvers used by `smb.c`, returning SMB error codes such as bad TID/FID through out parameters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/util.c

Utility layer for `cifsd`: logging, remote endpoint reading, path construction/splitting, hex dumps, DOS date/time and Windows FILETIME conversion, allocation rounding, SMB/DOS file attribute mapping, and case-insensitive name hashing.

The string packing/unpacking helpers encode and decode SMB 8-bit and UTF-16LE strings, including optional terminators, alignment padding, surrogate handling, and name translation between SMB backslashes and Plan 9 slashes. Space-to-nonbreaking-space translation is gated by `trspaces`.

Exports the pack/unpack adapter functions used by the SMB packing format engine, including normal strings, file names, and unterminated variants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcp.h

Shared DHCP/BOOTP definitions for IPv4 DHCP programs. Defines lease constants, packet-size constants, BOOTP opcodes/flags, DHCP message types, BOOTP/DHCP option numbers, Plan 9 vendor option numbers, DHCP client states, and `Lforever`.

Defines the packed `Bootp` structure, including Plan 9 `Udphdr`, BOOTP fixed fields, DHCP magic, and option buffer. This header is the common contract for `dhcpclient.c` and `dhcpd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcp6d.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcp6d.c

Minimal stateless DHCPv6 server for network boot. It listens on `dhcp6s`, joins `ff02::1:2` on link-local IPv6 interfaces, parses client/server ID and option-request TLVs, and replies to Solicit, Request, and Information-request messages.

Client identity is derived from DUID client ID when possible, otherwise from EUI-64-like link-local IPv6 address bytes. Address and option data are looked up in ndb using Ethernet address, target IPv6 records, interface networks, and requested attributes.

Supported responses include server ID, client ID, IA_NA with infinite preferred/valid lifetimes for ndb IPv6 addresses, DNS servers, DNS domain list, and bootfile URL assembled from `bootf`/`tftp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcp6d.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpclient.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpclient.c

Simple IPv4 DHCP client that broadcasts Discover, accepts Offer, sends Request, prints `ip=`, `mask=`, and `end`, then keeps the lease alive by renewing at half the lease interval.

State is held in a global locked `dhcp` struct. A timer process resends or transitions between selecting, requesting, renewing, and rebinding; a stdin watcher sends Release on shutdown.

Includes local option construction/parsing and BOOTP packet validation. Packet dump code is unconditional (`if(1)`), so received packets are always printed through `bootpdump`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dat.h

Internal header for the IPv4 DHCP server. Defines `Binding` for file-backed lease state and `Info` for ndb-derived host/network metadata including IP, mask, gateway, boot files, TFTP, fs/auth, root server/path, and vendor text.

Declares cross-file functions from `db.c`, `ndb.c`, and ICMP probing, plus globals such as `binddir`, `blog`, `now`, `ndbfile`, and lease policy values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/db.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/db.c

Lease database for `dhcpd`. Maintains an in-memory binding cache backed by exclusive files under `/lib/ndb/dhcp`, with each lease file storing expiration time and bound client ID.

Core operations include client ID formatting, binding initialization over configured pools, stale-file synchronization, old-binding reuse, free-binding search, ICMP conflict probing, offer creation, lease commit, and release.

The file-backed locking model lets multiple DHCP server processes coordinate. Existing lease files win over cache state whenever qid version changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpd.c

Main IPv4 BOOTP/DHCP server. It parses configured dynamic pools, listens on `bootp`, reads the latest queued packet, validates interface/relay context, parses DHCP options, finds static ndb host info, and dispatches BOOTP or DHCP handling.

Implements RFC2131-style handling for Discover, Request, Decline, Release, and Inform. Static bindings are answered from ndb; dynamic bindings come from `db.c`, with lease offers, commit checks, NAKs, conflict handling, and release support.

Also serves legacy BOOTP, including Plan 9 vendor fields, generic RFC1048 options, boot file selection, TFTP server selection, and ARP entry injection for unicast replies. `miscoptions` supplies subnet mask, router, host/domain, DNS, WINS, SMTP/POP/WWW/root/NTP/time servers, TFTP/bootfile, DNS search domains, and Plan 9 vendor options.

Command-line flags control debug, mute modes, BOOTP disabling, PPTP-only behavior, slow replies, IPv6-text Plan 9 options, net mountpoint, ndb file, homedir, and lease bounds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpleases.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpleases.c

Small lease-reporting utility. It scans `binddir`, parses filenames as IP addresses, synchronizes each binding through `syncbinding`, and prints active leases with bound client ID and expiration time.

Uses the same binding structures and validation logic as `dhcpd`, making it a read-side view over the DHCP lease directory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpleases.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ndb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ndb.c

Ndb integration for the IPv4 DHCP server. Opens/reopens the ndb file on change, finds interfaces, derives local reply addresses, and looks up host/network metadata by IP and hardware address.

`lookupip` fills `Info` with address, mask, gateway, domain, boot files, TFTP, fs/auth, NFS root, and vendor attributes. `lookup` maps a BOOTP client to an `Info` record using `ciaddr` or Ethernet address constrained to the requester/relay network.

Also provides helpers for server-address lists and domain names used by DHCP option generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ndb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ping.c

ICMP probe used before handing out dynamic leases. `icmpecho` sends up to three IPv4 echo requests with a fixed payload and short alarm timeout, returning true if a matching echo reply arrives.

Non-IPv4 addresses are treated as not answering. The DHCP server uses this to avoid reassigning addresses that still respond despite expired lease state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/testping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/testping.c

Tiny test harness for `icmpecho`. It initializes IP formatters, expects an address argument, and reports whether the address answers the DHCP probe.

Useful for checking the probe behavior independently from `dhcpd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/testping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpd.c

Plan 9 FTP server with optional explicit/implicit TLS, active/passive data channels, anonymous modes, Plan 9 auth login, per-user namespace selection, and command dispatch.

Commands cover authentication/TLS (`AUTH`, `PBSZ`, `PROT`), login (`USER`, `PASS`), navigation, listing (`LIST`, `NLST`, `MLSD`, `MLST`), file transfer (`RETR`, `STOR`, `REST`), directory/file mutation, rename, passive/active data setup, and session termination. Long operations may be forked through `asproc`.

It binds the client connection network into `/net` while opening data channels, supports TLS on the data channel, and uses Plan 9 file APIs for all filesystem access. Anonymous `none` users are restricted from delete/mkdir/rename/store-style mutations by command checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/file.c

Temporary file/cache layer for `ftpfs`. Each remote file can have a `File` cache with the first 1024 bytes in memory and larger content in a temporary `/tmp/ftpXXXXXXXXXXX` file.

Provides cached read/write, dirty/clean flags, LRU-style reuse of clean cache slots, and cleanup of temp files. `uncachedir` evicts clean cached files in sibling directories when the temporary-file count grows.

This layer is used by the 9P front end to buffer reads from FTP and stage writes before uploading on clunk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.c

9P filesystem front end for mounting an FTP server. It logs in, builds a mirror tree of `Node` objects, forks a 9P server side, and mounts it at `/n/ftp` or a requested mountpoint.

Implements core 9P messages: version, attach, walk, open, create, read, write, clunk, remove, stat, and error stubs for auth/wstat. Directories are populated from remote listings; files are fetched into the local cache on open/read and uploaded with `createfile` when dirty on clunk/uncache.

Supports cache invalidation through `.flush.ftpfs`, optional persistent cache, keepalive process, remote OS selection, TLS mode, anonymous password mode, mount root selection, and filename extension decoration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.h

Shared declarations for `ftpfs`. Defines the mirrored remote tree `Node`, supported remote OS enum, `OS` name table type, cache/protocol/misc function prototypes, global state, and cache validity macros.

Important state flags include cached/valid qid fields, directory `chdirunknown`, symlink mode bit `DMSYML`, cache timeout, remote root/current directory, remote OS, debug/quiet flags, `usenlst`, and network path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/proto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/proto.c

FTP protocol engine for `ftpfs`. Handles control connection setup, optional TLS, user/password login via auth or supplied anonymous credentials, remote OS detection, preamble/root selection, type switching, active/passive data connections, request/reply parsing, and keepalives.

Directory parsing is broad: Unix, Plan 9, TOPS, VM, VMS, MVS, NetWare, OS/2, TSO, NT-like listings, and NLST fallback. It converts remote listings into Plan 9 `Dir` records, handles Latin-1-to-UTF conversion, symbolic-link directory probing, and OS-specific path rendering.

File and directory operations map to FTP commands: `LIST`/`NLST`, `CWD`, `RETR`, `STOR`, `MKD`, `DELE`, `RMD`, `QUIT`, `PASV`, and `PORT`. Passive mode is preferred, with active fallback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/glob.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/glob.c

Custom glob implementation used by FTP tools. It builds a linked list of matches without fixed path-element limits, converting `*` and `?` per path component into regular expressions.

`glob` initializes absolute or relative matching, `globnext` recursively expands components, `globdir` scans directories, `globdot` handles `.` directory matches, and `globiter` returns allocated match strings one at a time.

Comment notes this implementation is likely slower than rc globbing but avoids size limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/glob.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/glob.h

Header for the custom glob library. Defines `Glob` linked-list nodes holding `String` paths and `Globlist` with first pointer plus tail insertion pointer.

Declares `glob`, `globadd`, `globlistfree`, and `globiter`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/gping.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/gping.c

Graphical ICMP monitor. It opens ICMP/ICMPv6 echo channels to up to 32 machines, spawns receiver processes, periodically sends echo requests, tracks outstanding sequence numbers, and graphs RTT and packet-loss data in a Plan 9 draw/event window.

The UI supports multiple graph rows, multiple machines, colorized scrolling plots, resize handling, mouse menu to add/drop RTT or loss graphs, and click-to-inspect historical values.

RTT is log-scaled; loss uses a smoothed percentage and marks unreachable events. Processes are tracked so `killall` can terminate children on exit or failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/gping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/hogports.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/hogports.c

Utility that reserves port ranges by announcing each requested address and then sleeping forever. Arguments are `proto!start-end` style ranges.

The process forks into the background, closes standard fds, announces all ports, closes stderr, and keeps the namespace alive. Useful for preventing other services from binding selected ports.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/hogports.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/hproxy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/hproxy.c

Small HTTP proxy and CONNECT tunnel. It reads the request headers, strips `Connection` and `Proxy-Connection`, parses the target URL or host form including bracketed IPv6, dials the destination, and relays data in both directions via forked copy loops.

For CONNECT it returns `200 Connection Established` or `500 Connection Failed`; for normal HTTP it rewrites the request line to origin-form and forces `Connection: close`.

It uses a 30-second dial alarm and kills the process group when either relay side exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/hproxy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/anonymous.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/anonymous.c

HTTPD helper that switches an unauthenticated request into the public web namespace. It binds `webroot` over `/` with `MREPL`, fails with internal error on bind failure, and changes directory to `/`.

This is the minimal namespace-isolation entry point for anonymous web serving.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/anonymous.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/authorize.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/authorize.c

Basic-auth authorization helper for HTTPD. For a requested file path, it looks for a sibling `.httplogin`, tokenizes it as realm plus username/password pairs, and compares against parsed request credentials.

On missing `.httplogin`, access is allowed. On failed auth, it emits a `401 Unauthorized` response with `WWW-Authenticate: Basic realm="<realm>"`, content length, connection policy, optional body for non-HEAD requests, and log entry.

The comment notes the supplied auth username is used directly here, despite older intent text about realm user behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/authorize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/classify.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/classify.c

Country/domain classifier for HTTPD/whois-related filtering. Contains tables of bad countries, good countries, government-domain tokens, and a broad country-code/name list.

`classify` examines ndb tuples for `country`, `dom`, and verified `ip` records. Bad countries always classify as bad, unapproved countries combined with government domains classify as bad government, approved countries classify OK, and missing country evidence returns unknown.

The code treats bad country codes in domain names as meaningful even without forward verification, while country-code inference from domain suffix requires a forward lookup match.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/classify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/content.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/content.c

HTTP content classification helper. `contentinit` reads `/sys/lib/mimetype`, tracks qid changes, and rebuilds a linked list of suffix-to-content-type/content-encoding mappings.

`uriclass` walks suffixes from a URI filename and returns first matching media type and encoding. `dataclass` classifies a byte buffer as `text/plain` only if it is valid text/UTF and contains no disallowed control bytes; otherwise it leaves type unknown.

Uses HTTPD allocation/content constructors (`hstrdup`, `hmkcontent`) and local fatal allocation helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/content.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/emem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/emem.c

Fatal allocation helpers for HTTPD. `ezalloc` allocates and zeroes memory, and `estrdup` duplicates a string; both call `sysfatal("out of memory")` on failure.

Used by other HTTPD support files to keep allocation call sites compact.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/emem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/hints.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/hints.c

HTTPD prefetch-hints support. It reads `/sys/log/httpd/url` into URL hash tables and `/sys/log/httpd/pathstat` into per-URL hint arrays, refreshing only when files change and are older than 300 seconds.

`urlcanon` normalizes repeated/trailing slashes and applies Bell Labs site-specific path rewrites. `hintprint` emits `Fresh:` headers for likely next resources above a probability threshold, excluding hints the client already reports having, and includes ETag-like qid/version tags plus logarithmic size estimates.

The implementation uses fixed `URLmax` tables, custom hash chaining, and arena allocation for compact refresh/rebuild behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/httpd/hints.c -->