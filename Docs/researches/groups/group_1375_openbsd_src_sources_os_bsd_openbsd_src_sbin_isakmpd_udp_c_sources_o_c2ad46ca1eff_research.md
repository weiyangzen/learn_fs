# Group Research: group_1375_openbsd_src_sources_os_bsd_openbsd_src_sbin_isakmpd_udp_c_sources_o_c2ad46ca1eff

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.c

`udp.c` implements the physical UDP transport backend for `isakmpd`. It registers the `udp_physical` transport method, binds UDP sockets, clones listening transports into peer-specific transports, receives ISAKMP packets, and sends messages through `sendmsg()`.

Key paths include `udp_init()`, `udp_bind()`, `udp_make()`, `udp_create()`, `udp_clone()`, `udp_handle_message()`, and `udp_send_message()`. Address and port selection comes from per-peer config, `General:Listen-on`, virtual default transports, and `udp_default_port`.

The socket setup uses `sysdep_cleartext()` to avoid IPsec-encrypting daemon traffic, `SO_REUSEADDR`/`SO_REUSEPORT` depending on wildcard binding, and `monitor_bind()` for privileged bind mediation. Incoming packets on default wildcard virtual transports trigger virtual reinitialization and are dropped because the daemon cannot know the destination address.

Notable coupling: depends on `transport`, `message`, `monitor`, `virtual`, config lookup, sockaddr utilities, and `udp_encap.c`, which reuses several non-static UDP helper functions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.h

`udp.h` declares the plain UDP transport API and shared state for `isakmpd`. It exposes `udp_init()`, `udp_bind()`, `udp_default_port`, and `bind_family`.

The header defines `BIND_FAMILY_INET4`/`BIND_FAMILY_INET6` filters and `struct udp_transport`, which embeds a generic `struct transport` plus source sockaddr, destination sockaddr, and socket fd.

This file is shared by `udp.c`, `udp_encap.c`, and `virtual.c`; changes affect both plain IKE UDP and NAT-T UDP encapsulation plumbing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.c

`udp_encap.c` implements the NAT-T UDP encapsulation transport backend for `isakmpd`. It closely mirrors `udp.c` for socket creation, config-based transport creation, fd integration, reporting, cloning, and send/receive operations, but registers as `udp_encap`.

The transport binds the configured or default NAT-T encapsulation port, usually `UDP_ENCAP_DEFAULT_PORT_STR`, and reuses plain UDP helpers for clone, remove, fd set/isset, source/destination access, and ID decoding. It is connected through `virtual.c`, which switches exchanges between main UDP and encapsulated UDP.

Protocol-specific behavior: receive validates a 32-bit NULL-ESP marker, drops short/nonzero-marker packets, ignores one-byte `0xff` NAT keepalives, strips the marker before message allocation, and marks messages with `MSG_NATT`. Send prefixes real ISAKMP messages with a NULL-ESP marker and sends a one-byte `0xff` marker when called with `msg == NULL`.

Security-relevant details: malformed encapsulated packets are rejected before parser handoff, but the marker check casts the buffer to `u_int32_t *`. Socket binding and cleartext setup follow the same privileged/cleartext path as plain UDP.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.h

`udp_encap.h` declares the NAT-T UDP encapsulation transport API. It exposes `udp_encap_init()`, `udp_encap_bind()`, and the global `udp_encap_default_port`.

The header is intentionally narrow and relies on the shared `struct udp_transport` from `udp.h`. It is consumed by the virtual transport layer to create and switch to encapsulated transports.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.c

`ui.c` implements the legacy FIFO/stdin control interface for `isakmpd`. It creates `/var/run/isakmpd.fifo` unless `-f -` selects stdin, reads nonblocking commands line-by-line, and dispatches single-letter commands.

Supported command paths include connection setup (`c`), teardown (`t`/`T`), SA deletion by cookies/message ID (`d`), debug control (`D`), live config get/set/add/remove (`C`), packet logging (`p`), shutdown (`Q`), reload/reinit (`R`), report output (`r`/`S`), and active/passive mode switching (`M`). Configuration changes to phase-2 connection lists schedule a delayed connection reinitialization timer.

Results that need file output are written through `monitor_fopen()` to `/var/run/isakmpd.result`. The command parser uses bounded `sscanf()` fields and hex decoding for SA cookies, but it is a trusted local-control interface with broad daemon control authority.

Notable coupling: calls into connection, SA, exchange, timer, config, logging, monitor, and daemon shutdown/reinit code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.h

`ui.h` declares the FIFO control interface constants and public entry points. It defines `FIFO` as `/var/run/isakmpd.fifo` and `RESULT_FILE` as `/var/run/isakmpd.result`.

The header exports `ui_fifo`, `ui_socket`, `ui_daemon_passive`, `ui_init()`, `ui_handler()`, and `ui_report()`. It is small but exposes daemon-wide control state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/util.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/util.c

`util.c` provides shared low-level helpers for `isakmpd`: big-endian integer encode/decode, zero-buffer tests, hex/raw conversion, service-name-to-port parsing, sockaddr parsing/formatting, sockaddr address/port accessors, network-address formatting, secret-file permission checks, monotonic timeout calculation, and bounded substring expansion.

`text2sockaddr()` is the most involved helper. It uses numeric `getaddrinfo()` unless name lookups are enabled, supports the special `default` keyword by querying the route socket, and can resolve interface names to IPv4/IPv6 addresses or netmasks with link-local IPv6 preference handling.

Security-relevant details: `check_file_secrecy_fd()` rejects secret files owned by neither root nor the process user and files accessible by group/other. Address parsing defaults to numeric-only to avoid daemon stalls from DNS unless `allow_name_lookups` is set.

The file is common infrastructure for transport binding, config parsing, certificate printable conversion, UI hex decoding, and logging/reporting.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/util.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/util.h

`util.h` declares the shared utility API for `isakmpd`. It exposes byte-order helpers, hex conversion, sockaddr conversion/accessors, port parsing, address formatting, zero tests, secret-file checks, timeout math, string expansion, and the `allow_name_lookups` flag.

It also declares the platform hook `sysdep_cleartext()`, used by UDP transports to keep IKE control traffic out of IPsec processing.

Because many daemon modules include this header, API changes here have broad impact across transport, config, crypto/cert, UI, and message code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.c

`vendor.c` handles OpenBSD vendor ID payload support for `isakmpd`. It hashes configured vendor capability strings with MD5 at startup and can add/check corresponding ISAKMP Vendor ID payloads.

The current table contains `OpenBSD-6.3`. `vendor_init()` prepares hashes, `add_vendor_openbsd()` appends vendor payloads to outgoing messages, and `check_vendor_openbsd()` compares inbound payloads and sets `EXCHANGE_FLAG_OPENBSD` on a match.

This is compatibility/capability signaling rather than authentication. Payloads are marked as processed whether already known or matched during the check.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.h

`vendor.h` defines `struct vendor_cap`, holding a vendor text string plus computed hash and hash size. It declares the OpenBSD vendor-ID initialization, outgoing payload addition, and incoming payload check functions.

The header connects vendor handling with the message and payload structures from the exchange layer.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/vendor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.c

`virtual.c` implements the higher-level `udp` transport method that wraps plain UDP and NAT-T UDP-encap transports. It owns the listener list, per-address virtual transports, default wildcard IPv4/IPv6 transports, interface probing, transport reinitialization, and NAT-T switching.

Startup registers the virtual transport method, binds all eligible interface addresses through `if_map()`, honors `General:Listen-on`, filters by `bind_family`, and optionally binds wildcard default transports so new addresses can trigger rescans. Interface filtering skips non-IP, unusable wildcard/broadcast-ish addresses, down interfaces, tentative/duplicated/detached IPv6 addresses, and addresses outside the current rdomain.

`virtual_clone()` creates peer-specific virtual transports, with main and encap children as needed. `virtual_send_message()` enables NAT-T when message/exchange flags allow it, preserves translated peer ports, and routes output through either main UDP or encapsulated UDP. `virtual_handle_message()` drops old-port traffic after encapsulation is active.

Notable coupling: depends on `udp.c`, `udp_encap.c`, interface enumeration/ioctl state, NAT traversal flags, exchange state, and transport queues.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.h

`virtual.h` declares the virtual UDP transport wrapper for `isakmpd`. `struct virtual_transport` embeds a generic transport, pointers to the main UDP and NAT-T encapsulated transports, an `encap_is_active` switch, and a listener-list link.

The header exports `virtual_init()`, `virtual_get_default()`, and `virtual_listen_lookup()`. It is the bridge between configured peer transports and actual per-address UDP sockets.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.c

`x509.c` implements X.509 certificate support for `isakmpd`. It loads trusted CA certificates, accepted peer/local certificates, and CRLs; maintains certificate stores; builds a separate subject/subjectAltName hash table for lookup by ISAKMP identity; validates received certificates; serializes/deserializes DER certificates; and generates KeyNote assertions from certificate chains.

Initialization paths are `x509_cert_init()` and `x509_crl_init()`. Directory reads are mediated through monitor helpers, skip non-regular entries, parse PEM certificates/CRLs, add them to OpenSSL stores, and optionally enter certs into the daemon hash table. CRL verification flags are enabled only after CRLs successfully load.

Certificate lookup uses `x509_cert_get_subjects()` to synthesize ISAKMP identity blobs from the subject DN and one supported subjectAltName. Supported subjectAltName mappings include DNS, RFC822/email, IPv4, and IPv6. `x509_cert_obtain()` finds a certificate for a local identity and returns DER serialization.

Validation uses OpenSSL `X509_STORE_CTX` against the CA store and optionally accepts self-signed certificates if configured. Key extraction is RSA-only. `x509_generate_kn()` finds issuer certificates, extracts RSA public keys, validates certificate validity-time encodings, and emits KeyNote credentials both by RSA key and DN.

Security-relevant details: chain validation depends on configured CA/CRL stores, self-signed acceptance is explicit config, secret/private-key handling is outside this file, DER and PEM parsing is delegated to OpenSSL, and the subjectAltName parser manually interprets the extension’s ASN.1 bytes in a limited way.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.h

`x509.h` declares the certificate handler API for `isakmpd`. It defines subjectAltName type constants for RFC822, DNS, and IP address names, plus small structures for acceptable CA attribute values.

The exported API covers certificate request validation/decoding, certificate load/init, CRL init, ASN.1/printable conversion, duplication/freeing, public-key extraction, subject identity extraction, certificate insertion/lookup/validation, CA counting, and directory readers.

This header couples certificate handling to OpenSSL/libcrypto types and the daemon’s ISAKMP identity/cert infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/x509.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/kbd/Makefile

This Makefile builds the `kbd` utility from `main.c` and `kbd_wscons.c`, installs `kbd.8`, and includes `<bsd.prog.mk>`.

It disables the program on `octeon` by setting `NOPROG=Yes`. A comment notes that architecture changes here must also be reflected in `src/distrib/special/kbd/Makefile`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/kbd_wscons.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/kbd/kbd_wscons.c

`kbd_wscons.c` implements wscons keyboard encoding listing and setting for the `kbd` utility. It maps wscons keyboard types to readable families and uses `KB_ENCTAB`/`KB_VARTAB` to translate encoding and variant names.

`kbd_list()` scans `/dev/wskbd0` through `/dev/wskbd9`, opens each keyboard read/write or read-only, obtains keyboard type with `WSKBDIO_GTYPE`, fetches supported encodings with `WSKBDIO_GETENCODINGS`, groups them by keyboard type, and prints available tables.

`kbd_set()` parses an encoding string with optional dot-separated variants, maps it to a `kbd_t`, and applies it to all detected keyboards with `WSKBDIO_SETENCODING`. Unsupported encodings on individual devices are reported without aborting unless the ioctl fails for another reason.

The file is direct device-control code with bounded local parsing and no persistent state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/kbd_wscons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/kbd/main.c

`main.c` is the entry point for `kbd`. It parses `-l` to list keyboard tables and `-q` to suppress successful set messages.

The argument contract is either `kbd -l` or `kbd [-q] name`. It dispatches to `kbd_list()` or `kbd_set()` and exits.

The file contains no device logic; it is command-line validation and dispatch.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/kbd/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/Makefile

This Makefile builds `ldattach` from `ldattach.c` and `atomicio.c`, links against `libutil`, installs `ldattach.8`, enables `-Wall`, and clears `CDIAGFLAGS`.

It is a small build wrapper for the tty line-discipline attachment utility.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.c

`atomicio.c` implements robust full-buffer I/O helpers. `atomicio()` repeatedly calls `read` or write-compatible functions until the requested byte count is transferred, interrupted operations retry, `EAGAIN` waits with `poll()`, and EOF sets `EPIPE`.

`atomiciov()` does the same for `readv`/`writev`, copying and mutating an iovec array as partial transfers complete. It rejects `iovcnt > IOV_MAX`.

These helpers are used by `ldattach` relay mode to avoid short writes while copying data between tty and pty fds.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.h

`atomicio.h` declares `atomicio()` and `atomiciov()` and defines `vwrite` as a casted write function pointer compatible with the `atomicio()` signature.

It is a local utility header for reliable complete reads/writes in `ldattach`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/ldattach.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/ldattach.c

`ldattach.c` attaches tty line disciplines to serial devices, optionally relaying data through a newly allocated pty. Supported disciplines are `nmea`, `msts`, and `endrun`, mapped to kernel line-discipline constants.

The command-line parser handles serial settings for data bits, parity, stop bits, hardware flow control, hangup-on-close, baud rate, timestamp conditions, no-daemon mode, and pty relay mode. It recognizes init-launched execution by parent PID and delays restart after failure when run from init.

After opening the device, it updates termios selectively, sets DTR, attaches the line discipline with `TIOCSETD`, configures timestamping with `TIOCSTSTAMP`, and for supported disciplines forces raw-ish input/output settings. With `-p`, it opens a pty pair, prints the slave path, daemonizes if requested, and relays both directions with `poll()` and `atomicio()`.

Signal handling is minimal: SIGHUP/SIGTERM set a global `dying` flag to exit the relay or suspend loop.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ldattach/ldattach.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mknod/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mknod/Makefile

This Makefile builds `mknod`, installs both `mknod.8` and `mkfifo.1`, and creates a hard link from `mknod` to `mkfifo`.

The shared binary changes behavior based on `__progname`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mknod/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mknod/mknod.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mknod/mknod.c

`mknod.c` implements both `mknod` and `mkfifo`. It pledges `stdio dpath`, parses all arguments into an array of `struct node`, supports `-m mode`, and then creates each requested node with `mknod()`.

For `mkfifo`, all remaining operands become FIFO nodes. For `mknod`, it supports FIFO (`p`), block (`b`), and character (`c`) nodes; block/character devices require major and minor numbers parsed with overflow checks and round-tripped through `makedev()`/`major()`/`minor()`.

Mode handling uses `setmode()`/`getmode()`, forbids bits outside `ACCESSPERMS`, and clears umask only when an explicit mode was provided. Errors creating individual nodes are warned and reflected in the exit status.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mknod/mknod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount/Makefile

This Makefile builds the generic `mount` command, links against `libutil`, installs `mount.8`, and includes `<bsd.prog.mk>`.

Filesystem-specific mount helpers reuse code from this directory, especially `getmntopts.c` and `mntopts.h`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/getmntopts.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount/getmntopts.c

`getmntopts.c` implements shared parsing for comma-separated `-o` mount options. `getmntopts()` duplicates the option string and repeatedly calls `getmntopt()`; `getmntopt()` handles empty entries, `no` prefixes, `key=value` assignments, option-table lookup, flag setting/clearing, and integer/string option values.

Recognized options are defined by caller-provided `struct mntopt` tables. Options can set mount flags directly, return alternate flags for caller-specific handling, require values, accept optional values, or invert negative forms.

Unsupported options, missing/unexpected values, and illegal integer values are fatal via `errx()`. This parser is central to `mount` and most `mount_*` helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/getmntopts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/mntopts.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount/mntopts.h

`mntopts.h` defines the shared mount-option table format used by `getmntopts.c`. It provides option behavior flags, `struct mntopt`, `union mntval`, and macros for common user-visible mount options.

The common option macros cover async, noatime/accesstime, nodev, noexec, nosuid, noperm, wxallowed, rdonly/ro/rw, sync, quota placeholders, softdep, force, update, reload, and fstab compatibility flags such as `auto` and `net`.

`MOPT_STDOPTS` is the standard option set consumed by most filesystem-specific helpers. The header is a compatibility layer between text `-o` options and kernel `MNT_*` flags.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/mntopts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/mount.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount/mount.c

`mount.c` implements the generic OpenBSD `mount` command. It lists current mounts, mounts fstab entries with `-a`/`-A`, filters by type and network/non-network selection, handles updates, infers filesystem type from NFS-like specs or disklabels, builds helper arguments, and execs `/sbin/mount_<type>` or `/usr/sbin/mount_<type>`.

`mountfs()` canonicalizes the mount point, merges fstab and command-line options with command-line priority, forces root mounts to use `update`, optionally skips already mounted filesystems, transforms option strings into helper argv entries, forks, execs the helper, waits, and prints the resulting mount when verbose.

Printing paths convert `statfs` flags to human-readable options and include filesystem-specific display for NFS, MFS, MSDOS, CD9660, and TMPFS. `disklabelcheck()` compares fstab type to disklabel type and warns about mismatches, with compatibility exceptions.

Security/operational details: the program pledges `stdio rpath disklabel proc exec`, runs helpers rather than calling `mount(2)` directly for most filesystems, and signals `mountd` by reading `/var/run/mountd.pid` after successful root mounts.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount/pathnames.h

`pathnames.h` defines path constants used by the generic `mount` command: `/sbin`, `/usr/sbin`, and `/var/run/mountd.pid`.

These paths control where `mount` searches for filesystem helpers and where it finds `mountd` for post-mount SIGHUP notification.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_cd9660/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_cd9660/Makefile

This Makefile builds `mount_cd9660` from `mount_cd9660.c` plus shared `getmntopts.c`, installs `mount_cd9660.8`, adds the generic `mount` directory to include paths, and uses `.PATH` to find shared source.

It follows the common pattern for filesystem-specific mount helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_cd9660/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_cd9660/mount_cd9660.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_cd9660/mount_cd9660.c

`mount_cd9660.c` mounts ISO-9660 filesystems. It parses CD9660-specific flags for extended attributes (`-e`), generation numbers (`-g`), disabling Joliet (`-j`), disabling Rock Ridge (`-R`), and session selection (`-s`), plus shared `-o` options.

The helper resolves the mount point, fills `struct iso_args`, defaults export root to `-2`, forces `MNT_RDONLY`, sets export read-only state, and calls `mount(MOUNT_CD9660, ...)`.

Errors distinguish unsupported kernel filesystem support from other mount failures.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_cd9660/mount_cd9660.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/Makefile

This Makefile builds `mount_ext2fs` from `mount_ext2fs.c` plus shared `getmntopts.c`, installs `mount_ext2fs.8`, and imports the generic `mount` directory for `mntopts.h`.

It is a standard filesystem helper build file.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/mount_ext2fs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/mount_ext2fs.c

`mount_ext2fs.c` mounts ext2 filesystems. It accepts shared `-o` options, resolves the mount point, fills a `struct ufs_args` with the device path and export info, and calls `mount(MOUNT_EXT2FS, ...)`.

The helper sets export flags to read-only when `MNT_RDONLY` is present. Error handling maps mount-table-full, device mismatch/update errors, unsupported kernel support, and generic errno into readable fatal messages.

The code is intentionally thin and delegates filesystem interpretation to the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ext2fs/mount_ext2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ffs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ffs/Makefile

This Makefile builds `mount_ffs` from `mount_ffs.c` plus shared `getmntopts.c`, installs `mount_ffs.8`, and includes the generic mount directory.

It provides the FFS-specific helper used by the generic `mount` command.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ffs/mount_ffs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ffs/mount_ffs.c

`mount_ffs.c` mounts FFS/UFS filesystems. It accepts shared options plus FFS-relevant flags including `wxallowed`, `noperm`, `async`, `sync`, `update`, `reload`, `force`, and `softdep`.

After resolving the mount point, it fills `struct ufs_args`, sets export flags according to read-only state, expands `MNT_NOPERM` into `MNT_NODEV | MNT_NOEXEC`, and calls `mount(MOUNT_FFS, ...)`.

Errors get filesystem-specific messages for full mount table, unsupported kernel support, and read-only-required filesystems that may need fsck.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ffs/mount_ffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_msdos/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_msdos/Makefile

This Makefile builds `mount_msdos` from `mount_msdos.c` plus shared `getmntopts.c`, installs `mount_msdos.8`, and reuses the generic mount include/source path.

It is the build wrapper for the MS-DOS/FAT mount helper.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_msdos/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_msdos/mount_msdos.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_msdos/mount_msdos.c

`mount_msdos.c` mounts FAT/MS-DOS filesystems. It parses name-mode flags (`-s`, `-l`, `-9`), uid/gid/mask overrides, and shared mount options.

If uid/gid/mask are omitted, it inherits them from the mount point’s existing stat data. User and group arguments can be names or numeric IDs validated with `strtonum()`, and masks are parsed as octal modes.

The helper fills `struct msdosfs_args`, sets export root to `-2`, sets read-only export flags when needed, and calls `mount(MOUNT_MSDOS, ...)`. It reports unsupported kernel support, full mount table, and invalid FAT filesystem errors distinctly.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_msdos/mount_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_nfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_nfs/Makefile

This Makefile builds `mount_nfs` from `mount_nfs.c` plus shared `getmntopts.c`, installs `mount_nfs.8`, defines `NFS`, includes the generic mount directory, and uses `.PATH` for shared source.

It is the build wrapper for the RPC/NFS mount helper.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_nfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_nfs/mount_nfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_nfs/mount_nfs.c

`mount_nfs.c` implements NFS mount negotiation and the final `mount(MOUNT_NFS, ...)` call. It supports NFSv2/v3 selection, UDP/TCP transport, background retries, soft/intr/noconn/dumbtimer/rdirplus/reserved-port behavior, size/time/retrans/readahead/cache tuning, max group count, and shared mount options.

`getnfsargs()` parses `host:path` and `path@host` specs, resolves IPv4 host addresses, queries portmap for the NFS port, contacts the remote mount daemon over TCP or UDP, obtains the file handle through RPC, falls back from NFSv3 to v2 on version mismatch unless forced, and supports background retry by forking and detaching.

The file contains XDR helpers for mount path and file-handle replies. For NFSv3, it validates file-handle size and checks the server’s auth list for `RPCAUTH_UNIX`, accepting an empty list as Unix auth for compatibility.

Important coupling: uses SunRPC client APIs, portmap, NFS kernel argument structures, and shared mount-option parsing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_nfs/mount_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ntfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ntfs/Makefile

This Makefile builds `mount_ntfs` only on `alpha`, `amd64`, and `i386`; other architectures set `NOPROG`. It uses `mount_ntfs.c` plus shared `getmntopts.c`, installs `mount_ntfs.8`, and includes the generic mount directory.

The architecture gate reflects NTFS helper/kernel support constraints.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ntfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ntfs/mount_ntfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_ntfs/mount_ntfs.c

`mount_ntfs.c` mounts NTFS filesystems. It parses case-insensitive lookup (`-i`), all-names exposure (`-a`), uid/gid/mode overrides, and shared mount options.

The helper always adds `MNT_RDONLY`, inherits uid/gid/mode from the mount point when not provided, fills `struct ntfs_args`, sets export root to 65534, and calls `mount(MOUNT_NTFS, ...)`.

User/group parsing accepts names or numeric IDs. Mode parsing is octal. The implementation is thin and mostly prepares kernel mount arguments.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_ntfs/mount_ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/Makefile

This Makefile builds `mount_tmpfs` from `mount_tmpfs.c` plus shared `getmntopts.c`, installs `mount_tmpfs.8`, includes `<bsd.own.mk>`, imports the generic mount source path, and links against `libutil`.

Commented source entries show older NetBSD-derived support files were not included in this OpenBSD version.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.c

`mount_tmpfs.c` mounts tmpfs filesystems. It parses root uid/gid/mode overrides, node limit (`-n`), size limit (`-s`), and shared mount options including `wxallowed` and `update`.

`mount_tmpfs_parseargs()` initializes `struct tmpfs_args`, parses scaled numeric size/node values with `scan_scaled()`, canonicalizes the mount point, warns when a relative path is adjusted, stats the mount point, and inherits root uid/gid/mode from it unless explicitly overridden.

`mount_tmpfs()` then calls `mount(MOUNT_TMPFS, ...)`. The file also exposes parsing and mounting functions separately through `mount_tmpfs.h`, making the parser testable/reusable.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.h

`mount_tmpfs.h` declares `mount_tmpfs()` and `mount_tmpfs_parseargs()` for the tmpfs mount helper.

The parse function exposes argument parsing into `struct tmpfs_args`, mount flags, and canonical device/directory buffers. This is more modular than most other mount helpers in the group.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_tmpfs/mount_tmpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_udf/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_udf/Makefile

This Makefile builds `mount_udf` from `mount_udf.c` plus shared `getmntopts.c`, installs `mount_udf.8`, and imports the generic mount include/source path.

It follows the standard helper pattern for filesystem-specific `mount_*` commands.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_udf/mount_udf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_udf/mount_udf.c

`mount_udf.c` mounts UDF filesystems. It parses shared `-o` options, resolves the mount point, fills `struct udf_args`, and calls `mount(MOUNT_UDF, ...)`.

The helper computes `args.lastblock` by opening the device and issuing `CDIOREADTOCENTRIES` for the lead-out track LBA. If that ioctl fails, it returns zero for last block.

This is optical-media-oriented glue around the kernel UDF mount interface.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_udf/mount_udf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_vnd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_vnd/Makefile

This Makefile builds `mount_vnd`, links against `libutil`, installs `mount_vnd.8`, enables extra warning diagnostics, and includes `<bsd.prog.mk>`.

Despite the name, this utility configures a vnd device for an image file; it does not call the generic mount helper infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_vnd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_vnd/mount_vnd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/mount_vnd/mount_vnd.c

`mount_vnd.c` configures a vnode disk device for an image file via `VNDIOCSET`. It accepts optional encryption keys, PKCS#5-derived keys, mount options placeholder `-o`, salt file, and disk geometry type.

`get_pkcs_key()` reads a passphrase from a TTY, obtains or creates a 128-byte salt file, derives a Blowfish-sized key with `pkcs5_pbkdf2()`, and zeroes the passphrase. Plain `-k` uses `getpass()` and raw passphrase bytes. The program warns that softraid crypto should be considered instead.

`config()` opens the vnd device with `opendev()`, fills `struct vnd_ioctl` with image path, sector geometry, and optional key material, issues `VNDIOCSET`, closes the device, and explicitly zeroes key memory before returning.

Security-relevant details: salt files are created mode `0600`, passphrases are zeroed for the PKCS path, derived/raw key buffers are zeroed after ioctl, and `-k`/`-K` are mutually exclusive.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mount_vnd/mount_vnd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/mountd/Makefile

This Makefile builds `mountd`, installs `exports.5` and `mountd.8`, links against `libutil`, and disables default static linking by clearing `LDSTATIC`.

Only the build file is in this group; the `mountd` daemon source itself is outside the listed file set.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/mountd/Makefile -->