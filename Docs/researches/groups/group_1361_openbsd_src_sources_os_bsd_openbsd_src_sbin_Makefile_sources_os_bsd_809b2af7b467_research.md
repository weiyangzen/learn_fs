# Group Research: group_1361_openbsd_src_sources_os_bsd_openbsd_src_sbin_Makefile_sources_os_bsd_809b2af7b467

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/Makefile

Top-level OpenBSD `sbin` subdirectory makefile.

It enumerates the system administration programs built under `/sbin`, including the files in this group (`atactl`, `badsect`, `bioctl`, `clri`, `dhcp6leased`, and `dhcpleased`) plus filesystem checkers, mount helpers, network daemons, routing tools, and reboot/shutdown utilities. It delegates recursion to `<bsd.subdir.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/Makefile.inc -->
# File Research: sources/os/bsd/openbsd-src/sbin/Makefile.inc

Common make include for OpenBSD `sbin` programs.

It defaults `BINDIR` to `/sbin`, propagates `${STATIC}` into `LDSTATIC`, and enables `-Werror-implicit-function-declaration` across these utility builds.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/atactl/Makefile

Build recipe for `atactl`.

It builds the `atactl` program, installs `atactl.8`, links against `libutil`, and uses the standard OpenBSD program make rules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atactl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/atactl/atactl.c

ATA device control utility.

It opens an ATA device with `opendev(..., O_RDWR, OPENDEV_PART, ...)`, dispatches named subcommands, and sends ATA requests through `ATAIOCCOMMAND`. Supported operations include trace dumping, IDENTIFY output, idle/standby/sleep and power status commands, acoustic/APM/read-ahead/write-cache/PUIS feature toggles, ATA security password/unlock/erase/freeze/disable flows, SMART enable/disable/status/autosave/offline/read/readlog, and SMART attribute reading.

The code centralizes ATA command error handling in `ata_command()`, mapping timeout, device-fault, abort, and raw error-register results to fatal diagnostics. IDENTIFY output handles endian conversion and swapped ATA strings, then prints device type, capacity, queue depth, standards, command sets, enabled features, and master password revision.

Security commands use `getpass()` prompts, enforce a 32-byte password limit, optionally confirm new passwords, and send `struct sec_password` sectors for set/unlock/erase/disable. SMART reads validate sector checksums before printing data; log parsing handles directory, summary, comprehensive, and self-test logs, including circular-buffer traversal. The comprehensive log path allocates enough 512-byte sectors for all reported errors before printing each record.

Notable constraints: most subcommands assume direct privileged access to the drive and fail hard on malformed arguments or ioctl errors; SMART attribute names are vendor-style lookup labels and unknown IDs are still displayed with raw values.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atactl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atasec.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/atactl/atasec.h

ATA Security Mode definitions for `atactl`.

It defines the security command opcodes for setting passwords, unlocking, erase prepare/unit, freeze lock, and disabling passwords. It also defines the 512-byte password sector layout with control flags for user/master passwords, normal/enhanced erase, high/maximum security level, a 32-byte password field, master password revision, and reserved padding.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atasec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atasmart.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/atactl/atasmart.h

ATA SMART protocol data definitions.

It provides SMART subcommand constants and packed/on-disk structures for SMART attributes, threshold sectors, read-data sectors, log directories, command/error records, summary and comprehensive error logs, and self-test logs. The header also defines status/capability bit constants and `SMART_SELFSTAT_PCNT()` for decoding self-test progress.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/atactl/atasmart.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/badsect/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/badsect/Makefile

Build recipe for `badsect`.

It builds the `badsect` utility, installs `badsect.8`, and uses the standard OpenBSD program make rules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/badsect/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/badsect/badsect.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/badsect/badsect.c

Legacy UFS bad-sector containment utility.

Given a bad-block directory and filesystem-relative sector numbers, it locates the mounted filesystem’s block device by scanning `/dev`, rewrites the path to the raw character device, reads the UFS superblock and cylinder group metadata, checks whether each requested filesystem block is in range and in a data area, warns if the sector is already allocated, then creates special files named after the sectors using `mknod()` with the filesystem block number as device data.

It reads disk metadata with `pread()` and exits nonzero on read, stat, open, or metadata validation failures. After creating containment nodes it reminds the operator to run `fsck` on the raw device.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/badsect/badsect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/bioctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/bioctl/Makefile

Build recipe for `bioctl`.

It builds the `bioctl` storage-controller utility, links against `libutil`, installs `bioctl.8`, and enables a set of diagnostic compiler warnings including pointer arithmetic, strict prototypes, missing prototypes, unused values, sign comparison, and shadowing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/bioctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/bioctl/bioctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/bioctl/bioctl.c

OpenBSD bio/softraid control utility.

It parses command-line operations for inquiry, disk inquiry, alarm control, enclosure blink/unblink, hotspare/offline/rebuild state changes, patrol control, RAID/crypto volume creation, volume deletion, and crypto passphrase changes. It first tries to open the named device directly; if that fails, it opens `/dev/bio`, locates the named controller/device with `BIOCLOCATE`, and stores the returned bio cookie for later ioctls.

Inquiry walks controller volumes and disks using `BIOCINQ`, `BIOCVOL`, and `BIOCDISK`, formats volume/disk status, RAID level, size, cache mode, enclosure name, vendor, serial, and patrol progress. State-changing operations validate controller target locators or device nodes, resolve volume IDs, and issue `BIOCSETSTATE`, `BIOCBLINK`, `BIOCALARM`, `BIOCPATROL`, `BIOCCREATERAID`, `BIOCDELETERAID`, or `BIOCDISCIPLINE`.

Crypto support derives or generates KDF data for softraid crypto volumes. It supports passphrase files only when root-owned and mode `0600`, derives keys with PKCS#5 PBKDF2 or bcrypt PBKDF, auto-tunes bcrypt rounds to roughly one second, verifies interactive new passphrases, and zeroes KDF/passphrase material after use. Device-list parsing opens each chunk as a block device, stores `dev_t` values, enforces maximum list size, and rejects duplicates.

Notable constraints: many operations require `/dev/bio` or direct device ioctl support; creation enforces minimum disk counts by RAID level and permits crypto key-disk mode or passphrase KDF mode.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/bioctl/bioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/clri/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/clri/Makefile

Build recipe for `clri`.

It builds the `clri` utility, installs `clri.8`, links against `libutil`, and uses the standard OpenBSD program make rules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/clri/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/clri/clri.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/clri/clri.c

UFS inode clearing utility.

It opens a filesystem device read/write, pledges `stdio`, searches known UFS superblock offsets, validates UFS1/UFS2 magic, block size, and UFS2 superblock location, then validates all requested inode numbers against the filesystem inode count. For modern inode formats it clears the filesystem clean flag and writes the superblock.

For each inode argument it locates the containing inode block, reads it, zeros the selected UFS1 or UFS2 inode, assigns a new random generation number with `arc4random()`, writes the block back, and fsyncs. This is a low-level repair tool intended for explicit operator use on damaged filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/clri/clri.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/Makefile

Build recipe for the DHCPv6 prefix-delegation daemon.

It builds `dhcp6leased` from the control, main, engine, frontend, logging, configuration parser, lease parser, and print-config sources. It installs `dhcp6leased.8` and `dhcp6leased.conf.5`, enables strict warning flags, links against `libevent` and `libutil`, generates `parse_lease.c` with a `pl` yacc prefix, and explicitly disables static linking for this daemon.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.c

Control socket handling for `dhcp6leased`.

It creates a nonblocking Unix-domain control socket, unlinks any stale path, binds with restrictive permissions, chmods the socket group-readable/writable, listens, and accepts client connections into per-client imsg buffers. Descriptor exhaustion pauses accepting briefly with an event timer to avoid a tight failure loop.

Accepted control imsgs support reload, verbosity changes, interface-info requests, and explicit DHCP request/reboot triggers. Requests are forwarded to the main or engine process as appropriate, verbosity changes also update the frontend’s local log level, and responses are relayed back to the originating control connection by matching imsg pid.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.h

Control socket API for `dhcp6leased`.

It declares initialization, listen/accept, imsg dispatch, and relay functions used by the frontend and main daemon to expose management commands over the Unix control socket.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.c

Privileged parent process for `dhcp6leased`.

The main daemon parses configuration, supports `-n` syntax/print checking, enforces root and a single-instance lock, verifies the `_dhcp6leased` user, daemonizes unless debugging, forks `engine` and `frontend` child roles via `execvp`, and wires them together with nonblocking imsg socketpairs. It owns privileged resources: route socket for reject routes, IPv6 ioctl socket for address changes, frontend route socket, per-interface UDP socket opening, control socket creation, UUID file creation, and lease-file read/write access.

It sends configuration to both children as imsg object streams, passes the frontend/engine IPC socketpair, passes route/control/UDP sockets by descriptor, and broadcasts a stable DUID UUID loaded from or atomically written to `/var/db/dhcp6leased/uuid`. It uses `unveil()` and `pledge()` after setup; if lease-directory unveil fails, it disables lease-file persistence.

The parent handles child messages to open DHCPv6 UDP sockets bound to an interface link-local address and routing domain, configure/deconfigure IPv6 addresses with `SIOCAIFADDR_IN6`/`SIOCDIFADDR_IN6`, add/delete static reject routes labeled `dhcp6leased`, and atomically write per-interface lease files. It also reads saved leases during interface updates so the engine can attempt reboot/rebind behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.h

Shared protocol, configuration, and imsg definitions for `dhcp6leased`.

It defines daemon paths, ports, DHCPv6 constants, option/status codes, limits, lease-file prefixes, DUID/UUID sizing, and OpenBSD enterprise number. It declares packed DHCPv6 wire structs for headers, options, DUID UUID, IA_PD, vendor class, and IA_PREFIX; shared imsg wrapper state; interface/prefix configuration queues; runtime interface info; DHCP packet/request/lease imsg payloads; and the full enum of internal imsg message types.

The header also declares cross-module functions for imsg event handling, config allocation/merge/free, string conversion, engine message names, frontend config lookup/change detection, config printing, config parsing, and lease parsing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.c

DHCPv6 lease-state engine for `dhcp6leased`.

The engine runs as the unprivileged `_dhcp6leased` user, receives frontend/main imsgs, then tightens pledge to `stdio` after IPC setup. It maintains per-interface state machines with randomized transaction IDs, request timing, server IDs, current and candidate delegated prefixes, T1/T2/lease timers, routing domain, link state, and event timers.

It validates DHCPv6 packets from the frontend: checks header length, client ID against the daemon DUID, server ID size/duplication, IA_PD structure, IA_PREFIX lifetimes, prefix length, status codes, and required IA coverage for configured delegations. Advertise messages move `IF_INIT` to requesting; replies from requesting, renewing, rebinding, rebooting, or rapid-commit init set T1/T2/lease time and bind the lease. Renew failures with non-success IA status trigger rebinding.

State transitions implement solicit/request/renew/rebind/reboot behavior with exponential backoff, lease expiry handling, deprecation on link down, and deconfiguration on timeout or failure. On a bound lease it asks the parent to add reject routes for delegated prefixes, configure derived addresses on downstream interfaces, and write lease files. Prefix changes cause old interface configuration to be removed before new prefixes are committed.

It also formats DHCP message/option/status names, DUID hex strings, and IPv6 prefix masks. Notable limitation: config-change handling depends on `changed_ifaces()`, while the frontend implementation currently treats existing interface configs as equal.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.h

Engine-to-main imsg payload declarations.

It defines payloads for configuring/deconfiguring IPv6 addresses and reject routes, then declares the `engine()` entry point and helper for composing messages to the frontend.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.c

Unprivileged network frontend for `dhcp6leased`.

The frontend drops to `_dhcp6leased`, pledges `stdio unix recvfd route`, receives sockets and configuration from the parent, monitors interface route messages, owns per-interface UDP receive events, and sends/receives DHCPv6 packets. It builds vendor-class data from `uname()`, sets the multicast destination to `ff02::1:2` on server port 547, and requests bound UDP sockets from the parent for configured, running interfaces.

Configuration is reconstructed from imsg streams into local SIMPLEQ structures. On reconfiguration it computes changed interfaces, updates them, and asks the engine to reboot DHCP processing. Interface route messages trigger updates or removal; UDP packets are wrapped in `IMSG_DHCP` and forwarded to the engine.

Outbound packets are built for solicit, request, renew, and rebind. The packet builder writes client ID, optional server ID, IA_PD/IA_PREFIX options for each configured IA, option request options, elapsed time, optional rapid commit, and vendor class. If the engine asks to send before the UDP socket arrives, the interface records a pending solicit and sends once `set_udpsock()` installs the event.

Notable limitation: `iface_conf_cmp()` currently always returns `0`, so changed existing interface details are not detected by that comparison path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.h

Frontend process API for `dhcp6leased`.

It declares the frontend entry point, dispatchers for main and engine imsg channels, and helpers for composing imsgs back to the main process or engine.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.c

Logging support for `dhcp6leased`.

It initializes stderr logging in debug mode or syslog logging otherwise, tracks a process name and verbosity level, preserves `errno` across logging calls, and provides warn/warnx/info/debug/fatal/fatalx helpers. Debug logging is gated by verbosity; fatal helpers log with process context and exit.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.h

Logging declarations for `dhcp6leased`.

It declares initialization, process-name setup, verbosity accessors, formatted warn/info/debug/log/fatal helpers, and printf-style attributes for compile-time format checking.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse.y

Yacc grammar and lexer for `dhcp6leased.conf`.

The grammar accepts macro assignments, `request rapid commit`, and `request prefix delegation on <iface> for { ... }` blocks. Delegated target entries are interface names with optional `/prefixlen`, defaulting to `/64`; the special name `reserve` is allowed repeatedly and is later skipped during address configuration.

The parser maintains config queues of requesting interfaces, IA_PD requests, and downstream prefix targets. After parsing it computes an addressing plan that assigns prefix masks to each downstream target and determines the requested upstream prefix length needed to cover them. Duplicate non-reserve target interfaces within an IA are rejected, interface and macro names are length checked, and too many IA requests are rejected at `MAX_IA`.

The lexer supports quoted strings, comments, backslash-newline continuation, numbers, keywords, and `$macro` expansion through an unget buffer. It records line numbers for diagnostics, supports persistent/nonpersistent macros, warns about unused macros at high verbosity, and includes file secrecy checks for secret-capable parsing even though the main config is opened non-secret here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse_lease.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse_lease.y

Yacc grammar and lexer for persisted `dhcp6leased` lease files.

It parses lease lines of the form `ia_pd <IAID> <IPv6 prefix> <prefix length>` into an `imsg_ifinfo` prefix array. Prefix lengths must be 1 through 128, prefixes must parse with `inet_pton(AF_INET6, ...)`, and invalid entries clear the affected prefix length.

The lexer mirrors the main parser’s quoted string, comment, number, keyword, and string handling while reusing shared file stack helpers from `parse.y`. Notable boundary detail: it rejects IA IDs greater than `MAX_IA`, but the destination array is sized `MAX_IA`, so an IA ID exactly equal to `MAX_IA` would address one past the valid index.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse_lease.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/printconf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/printconf.c

Configuration printer for `dhcp6leased`.

It renders the parsed configuration back as `dhcp6leased.conf` syntax. It prints `request rapid commit` when enabled, emits prefix-delegation request blocks per interface/IA, and prints each downstream interface target with its prefix length. At verbosity above one it also annotates derived prefix masks using the documentation prefix `2001:db8::`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcp6leased/printconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/Makefile

Build recipe for the IPv4 DHCP lease daemon.

It builds `dhcpleased` from BPF, checksum, control, main, engine, frontend, logging, parser, and print-config sources. It installs `dhcpleased.8` and `dhcpleased.conf.5`, enables strict warning flags, links against `libevent` and `libutil`, and disables static linking by default.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/dhcpleased/Makefile -->