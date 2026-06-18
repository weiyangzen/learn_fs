# Group Research: group_1169_nbd_sources_virtualization_nbd_github_workflows_build_yml_sources_v_e75fb812a8fd

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/nbd` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/.github/workflows/build.yml -->
# File Research: sources/virtualization/nbd/.github/workflows/build.yml

GitHub Actions workflow for push-time CI on `ubuntu-latest`.

It installs DocBook, GLib, GnuTLS, libnl-genl, Autoconf Archive, and `gcovr`; checks out the tree; runs `./autogen.sh`; configures with `--enable-syslog`; builds and runs `make check` with coverage flags; generates Cobertura XML plus HTML coverage; submits coverage to Coveralls; and uploads `coverage.xml` and `coverage.html`.

The dependency set mirrors important optional project features: manpages, GLib/gthread server support, TLS, netlink client support, and Autotools bootstrap.
<!-- END FILE RESEARCH: sources/virtualization/nbd/.github/workflows/build.yml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/Makefile.am -->
# File Research: sources/virtualization/nbd/Makefile.am

Top-level Automake file for the NBD source tree.

It builds installed programs `nbd-server`, `nbd-trdump`, and `nbd-trplay`; conditionally builds `nbd-client`; and lists `make-integrityhuge` as an extra program. It defines internal libtool libraries `libnbdsrv.la`, `libcliserv.la`, and `libnbdclt.la`.

Client build behavior depends on `CLIENT` and `GNUTLS`. With GnuTLS, it builds `nbd-client` with `crypto-gnutls.c`/`buffer.c` and also builds `min-nbd-client` with `-DNOTLS`. Without GnuTLS, `nbd-client` is compiled with `-DNOTLS`.

It wires Bison generation for `nbdtab_parser.tab.h`, distributes helper files including `maketr`, `CodingStyle`, `autogen.sh`, `README.md`, and `support/genver.sh`, and sets distcheck to configure with `--enable-syslog`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/args.c -->
# File Research: sources/virtualization/nbd/args.c

Refactored command-line parser for `nbd-client`.

`init_client()` initializes a `CLIENT` with block size 512, one connection, and default port `10809`. `free_client_fields()` resets the struct instead of freeing individual string fields, with comments indicating this is test-oriented behavior.

`parse_nbd_client_args()` uses `getopt_long_only()` to parse long options, short options, and old-style positional `bs=`/`timeout=` arguments. It fills target host/port/device fields, export name, block size, forced size, connection count, timeout/dead-timeout, Unix socket mode, TLS files/hostname/priority, read-only, persist, preinit, check/disconnect/list/version actions, and netlink-only `identifier`/`nonetlink` when compiled with netlink support.

The parser returns `parse_result_t` rather than exiting directly, and it recognizes nbdtab-style invocations where a single `nbdX` or `/dev/nbdX` argument implies later config lookup. Integration details to watch: `-S` appears in the short option string but has no switch case, and `-V` sets `show_version` without setting `should_exit`, while `main()` only handles version inside the `should_exit` path.
<!-- END FILE RESEARCH: sources/virtualization/nbd/args.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/args.h -->
# File Research: sources/virtualization/nbd/args.h

Header for the refactored `nbd-client` argument parser.

It includes `config.h`, `stdbool.h`, `stdint.h`, and `nbdclt.h`, then defines `parse_result_t`. That result carries an exit code, error buffer, immediate-action flags, check/disconnect/list/version state, and netlink-only fields when `HAVE_NETLINK` is enabled.

It declares `parse_nbd_client_args()`, `free_client_fields()`, and `init_client()`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/args.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/autogen.sh -->
# File Research: sources/virtualization/nbd/autogen.sh

Autotools bootstrap script.

It runs with `set -ex`, generates `systemd/nbd@.service.sh.in` by invoking `make -C systemd -f Makefile.am`, then executes `autoreconf -f -i`.

CI calls this before `./configure`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/autogen.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/backend.h -->
# File Research: sources/virtualization/nbd/backend.h

Small backend header declaring `void punch_hole(int fd, off_t off, off_t len);`.

It is guarded by `NBD_BACKEND_H` and relies on includers to make `off_t` visible before inclusion.
<!-- END FILE RESEARCH: sources/virtualization/nbd/backend.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/buffer.c -->
# File Research: sources/virtualization/nbd/buffer.c

Circular buffer implementation used by TLS proxying.

The private `struct buffer` stores a heap buffer, total size, high-water mark, read index, write index, and explicit empty flag. The empty flag distinguishes empty from full when read and write indexes are equal.

APIs allocate/free buffers, expose maximal contiguous read/write spans, mark bytes consumed or produced, test empty/full/high-water state, and compute free/used bytes. The implementation is single-threaded and designed for event-loop data pumping in `crypto-gnutls.c`.

Allocation failure is not checked in `bufNew()`, so callers assume successful `calloc()`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/buffer.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/buffer.h -->
# File Research: sources/virtualization/nbd/buffer.h

Public interface for the TLS proxy circular buffer.

It declares opaque `buffer_t` and functions for allocation, freeing, read/write span discovery, completed read/write accounting, empty/full/high-water checks, and free/used byte counts.

The header carries an MIT license block from Wrymouth Innovation Ltd and includes `stdlib.h` plus `sys/types.h` for `ssize_t`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/buffer.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/cliserv.c -->
# File Research: sources/virtualization/nbd/cliserv.c

Shared client/server utility implementation.

It defines classic and newstyle negotiation magic constants, `set_nonblocking()`, TCP socket tuning through `TCP_NODELAY`, nonfatal/fatal error helpers, optional syslog setup, endian conversion for 64-bit network order, and full-length `readit()`/`writeit()` loops.

`readit()` and `writeit()` loop until the requested byte count is transferred, treating `EAGAIN` as retryable and other errors as diagnostics/failures. Both loops use pointer arithmetic on `void *`, relying on compiler extension behavior.

`logging()` disables stdout/stderr buffering and opens syslog only when `ISSERVER` is defined.
<!-- END FILE RESEARCH: sources/virtualization/nbd/cliserv.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/cliserv.h -->
# File Research: sources/virtualization/nbd/cliserv.h

Shared protocol and helper declarations for NBD client/server code.

It includes network headers, `nbd.h`, large-file fallback definitions, GCC compatibility macros, extern protocol magic constants, `INIT_PASSWD`, error/logging helpers, endian helpers, full read/write helpers, and the default NBD port `10809`.

It also defines important option-negotiation constants: export selection, abort, list, STARTTLS, INFO, GO, structured replies, reply errors, global/client flags, and info type identifiers.

This header is central glue for `nbd-client.c`, server code, and transaction tools.
<!-- END FILE RESEARCH: sources/virtualization/nbd/cliserv.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/configure.ac -->
# File Research: sources/virtualization/nbd/configure.ac

Autoconf script for the NBD package.

It initializes package metadata from `support/genver.sh`, enables Automake/libtool, and exposes toggles for large file support, syslog, debug mode, GnuTLS, libnl/netlink, and manpage generation.

It checks compiler/tooling requirements including C compiler, C preprocessor, lex, Bison from Autoconf Archive, pkg-config, endian support, integer sizes, dirent type support, and functions such as `llseek`, `mkstemp`, `fdatasync`, `splice`, and `sync_file_range`.

Platform checks define support for hole punching, block discard, splice pipe sizing, Windows zero-data ioctl, GLib/gthread, socket/nss wrapper tests, `g_memdup2`, and `_BSD_SOURCE` needs. `nbd-client` is built only on Linux hosts. Darwin marks `tlshuge` as an expected failure.

It substitutes manpage config paths, links selected source files into test run directories, and configures Makefiles, generated SGML manpages, docs, tests, and systemd files.
<!-- END FILE RESEARCH: sources/virtualization/nbd/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/coverity_model.c -->
# File Research: sources/virtualization/nbd/coverity_model.c

Small Coverity model file for GLib array append behavior.

It forward-declares `GArray`, maps `g_array_append_val(a, v)` to `g_array_append_vals(a, &(v), 1)`, and models `g_array_append_vals()` by calling `__coverity_escape__`.

This is static-analysis support, not production runtime code.
<!-- END FILE RESEARCH: sources/virtualization/nbd/coverity_model.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/crypto-gnutls.c -->
# File Research: sources/virtualization/nbd/crypto-gnutls.c

GnuTLS-backed TLS session and proxy implementation.

It defines `tlssession`, initializes certificate credentials, optional trust anchors, optional key/cert files, hostname verification, GnuTLS priority, server certificate request behavior, and custom push/pull hooks when `SOCKET_WRAPPER_DIR` is set. The default priority string permits TLS 1.2.

Certificate verification checks trust status, revocation, expiration, activation, X.509 type, peer certificate import, and optional hostname matching.

`tlssession_mainloop()` performs the TLS handshake, switches encrypted and plaintext FDs to nonblocking mode, then uses `select()` to move data between plaintext and encrypted endpoints. It uses two circular buffers for plaintext-to-crypt and crypt-to-plaintext flow, handles pending GnuTLS records, EOF propagation, interrupted sends, `GNUTLS_E_AGAIN`, shutdown, and cleanup.
<!-- END FILE RESEARCH: sources/virtualization/nbd/crypto-gnutls.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/crypto-gnutls.h -->
# File Research: sources/virtualization/nbd/crypto-gnutls.h

Public TLS proxy interface.

It declares `tlssession_init()`, opaque `tlssession_t`, `tlssession_new()`, `tlssession_close()`, and `tlssession_mainloop()`.

The constructor accepts server/client mode, key/cert/CA files, hostname, GnuTLS priority string, insecure/debug flags, quit callback, error-output callback, and opaque callback data.
<!-- END FILE RESEARCH: sources/virtualization/nbd/crypto-gnutls.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/lfs.h -->
# File Research: sources/virtualization/nbd/lfs.h

Large-file and sync feature compatibility header.

When `NBD_LFS` is enabled, it defines `_FILE_OFFSET_BITS 64`, ensures `_LARGEFILE_SOURCE`, and maps `PARAM_OFFT` to `PARAM_INT64`; otherwise `PARAM_OFFT` maps to `PARAM_INT`.

When `HAVE_SYNC_FILE_RANGE` is defined, it enables `USE_SYNC_FILE_RANGE` and `_GNU_SOURCE`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/lfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/make-integrityhuge.c -->
# File Research: sources/virtualization/nbd/make-integrityhuge.c

Utility for generating a synthetic binary NBD transaction stream.

It writes 250 request/reply packet pairs to stdout for a 50 MB virtual file. It randomly chooses aligned offsets and lengths, emits reads or writes, sometimes forces FUA writes, sometimes emits flushes, and finally writes a disconnect request.

It uses NBD request/reply structures and byte-order helpers from shared headers. The output is test data for transaction replay/integrity paths, not human-readable logging.
<!-- END FILE RESEARCH: sources/virtualization/nbd/make-integrityhuge.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/maketr -->
# File Research: sources/virtualization/nbd/maketr

Example shell script for producing an NBD transaction log.

It creates a temporary server config exporting a 50 MB file with transaction logging, flush/FUA/rotational flags, starts `nbd-server`, connects `/dev/nbd0`, formats and mounts ext3, extracts and archives a configured tarball, runs `dbench`, unmounts, disconnects the client, stops the server, removes temporary files, and lists `output.tr`.

The script assumes root privileges, `/dev/nbd0`, `/mnt`, locally built `nbd-server`/`nbd-client`, ext3 tools, `dbench`, and a hard-coded tarball path.
<!-- END FILE RESEARCH: sources/virtualization/nbd/maketr -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/Makefile.am -->
# File Research: sources/virtualization/nbd/man/Makefile.am

Automake file for manpage generation.

It marks generated manpage artifacts as clean/distclean, distributes the `.sgml.in` templates, and, when `MANPAGES` is enabled, builds/install manpages for `nbd-server`, `nbd-client`, `nbd-trdump`, `nbd-trplay`, and `nbdtab` using `docbook2man`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbd-client.8.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbd-client.8.sgml.in

DocBook manpage template for `nbd-client(8)`.

It documents connecting a Linux NBD device to an `nbd-server` export over TCP or Unix domain sockets, nbdtab-based lookup, disconnect, connection check, export listing, netlink usage, and version/help modes.

Options include block size, multiple connections, timeout, named export, check/disconnect/list, netlink disablement, backend identifier, persist, preinit, read-only, forced size, SDP, swap, systemd mark, nofork, no-optgo, Unix socket mode, and TLS files/hostname/priority.

The TLS section explains the userspace proxy design: `nbd-client` upgrades the network socket with STARTTLS, creates a socketpair, gives one side to the kernel, and runs an encrypt/decrypt proxy on the other. It also documents why TLS plus swap can reintroduce memory-pressure deadlocks because PF_MEMALLOC applies to the kernel-facing socket rather than the actual network socket.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbd-client.8.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbd-server.1.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbd-server.1.sgml.in

DocBook manpage template for `nbd-server(1)`.

It describes serving a file or block device over NBD for Linux or Hurd clients, including diskless clients, swap, and filesystem use over exported storage. It documents legacy command-line export configuration while noting configuration files are preferred.

Options cover listen address/port, exported filename, size, read-only, multifile, copy-on-write, auth host list, config file, max connections, version output, foreground/no-fork modes, and conversion of command-line options into a config section.

It also documents SIGHUP behavior: re-reading config adds newly defined exports but does not modify exports already being served.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbd-server.1.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbd-server.5.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbd-server.5.sgml.in

DocBook manpage template for the `nbd-server` configuration file.

It defines the config grammar: `[generic]` must appear first, other sections define exports, comments occupy comment lines, and option lines use `name = value` with string/integer/boolean values. Boolean values are `true` or `false`.

Generic options include export listing, TLS CA/cert/key, forced TLS mode, user/group privilege drop, include directory, listen address, max worker threads, obsolete oldstyle handling, default port, splice, Unix socket and dual-listen behavior, and GnuTLS priority.

Export options include authorization file, copy-on-write, COW directory, backend file path, fixed file size, flush, per-export TLS requirement, FUA, max connections, multifile, treefiles, pre/post run hooks, read-only, rotational flag, SDP, sparse COW, sync, temporary exports, timeout, transaction log, trim, virtualization style, TLS-only, and waitfile migration support.

The virtualization section defines filename mapping from client address using `none`, `ipliteral`, `iphash`, and `cidrhash`. The waitfile section describes accepting writes into a diff file before the backend arrives, then merging on SIGUSR1 for live migration.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbd-server.5.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbd-trdump.1.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbd-trdump.1.sgml.in

DocBook manpage template for `nbd-trdump(1)`.

It documents a filter that reads an `nbd-server` transaction log from stdin and writes human-readable output to stdout. The log is produced by the server `transactionlog` configuration directive.

The output legend identifies request, reply, structured-reply markers and fields for cookie, command, offset, length, error, structured reply type, and structured reply flags.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbd-trdump.1.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbd-trplay.1.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbd-trplay.1.sgml.in

DocBook manpage template for `nbd-trplay(1)`.

It documents replaying all or part of an NBD transaction log produced by `nbd-server`, specifically logs generated with transaction logging including data.

The manpage defers command-line details to `nbd-trplay --help` and states that the tool updates the image provided with `-i`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbd-trplay.1.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/man/nbdtab.5.sgml.in -->
# File Research: sources/virtualization/nbd/man/nbdtab.5.sgml.in

DocBook manpage template for `nbdtab(5)`, the client-side predefined connection file.

It documents one connection definition per line with four fields: short device name without `/dev/`, server hostname or Unix socket path, export name, and optional comma-separated options.

Documented options mirror client options relevant to stored profiles: block size, CA/cert/key files, connection count, no-optgo, persist, port, GnuTLS priority, swap, timeout, TLS hostname, and Unix socket mode. Unknown options warn unless prefixed with `_`, which is reserved for local/distribution customization.

The example shows a swap/persist entry and a plain data export entry.
<!-- END FILE RESEARCH: sources/virtualization/nbd/man/nbdtab.5.sgml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-client.c -->
# File Research: sources/virtualization/nbd/nbd-client.c

Main implementation of `nbd-client`.

It includes client configuration globals, nbdtab parser callbacks, optional libnl netlink integration, TCP and Unix socket connection logic, newstyle negotiation, STARTTLS upgrade, export listing, kernel device setup, disconnect/check operations, and main process lifecycle.

The nbdtab callbacks populate `CLIENT` fields from parsed properties/flags and select the matching config row by device name. `get_from_config()` opens `SYSCONFDIR/nbdtab`, runs the generated parser, and validates that a matching row was found.

Netlink support can connect, disconnect, query status, and configure sockets through the kernel NBD generic netlink family. It sends size, block size, server flags, timeout, dead connection timeout, optional backend identifier, and socket FDs. Netlink mode skips the older daemon/ioctl path.

Connection setup supports TCP via `getaddrinfo()` and Unix domain sockets. Negotiation reads `INIT_PASSWD`, option magic, global flags, sends client flags, optionally upgrades with `NBD_OPT_STARTTLS`, handles `NBD_OPT_LIST`, prefers `NBD_OPT_GO`, and falls back to `NBD_OPT_EXPORT_NAME` on unsupported GO/INFO replies.

TLS support creates a socketpair and forks a proxy process running `tlssession_mainloop()`, then uses the plaintext socket for NBD traffic handed to the kernel.

The ioctl path opens the NBD device, sets size/block size, flags, read-only state, timeout, socket FDs, optional swap memory behavior, daemonizes unless suppressed, forks a helper to trigger partition reread, runs `NBD_DO_IT`, clears sockets on exit, and supports reconnect loops in persist mode.

Newer netlink persist scaffolding includes multicast monitoring and reconnect/reconfigure helpers, but callback logic currently only logs link-dead messages and contains TODO-level device matching/reconnect integration. Another integration detail: command parsing sets `persist`, while main reconnect checks use `persist_mode`, so the active field mapping should be verified against `nbdclt.h`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-client.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-debug.h -->
# File Research: sources/virtualization/nbd/nbd-debug.h

Small debug macro header.

It includes `config.h`, defines `DEBUG(...)` as `printf(__VA_ARGS__)` when `DODBG` is enabled and as an empty macro otherwise, and provides a fallback empty `PACKAGE_VERSION`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-debug.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-helper.h -->
# File Research: sources/virtualization/nbd/nbd-helper.h

Helper header for transaction logging and readable protocol names.

It defines transaction log control constants, including `NBD_TRACELOG_SET_DATALOG` and `NBD_TRACELOG_FROM_MAGIC`.

It provides inline string conversion helpers for NBD commands, trace log parameter names, and structured reply types. Known constants are mapped to macro-name strings; unknown values return `UNKNOWN`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-helper.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-netlink.h -->
# File Research: sources/virtualization/nbd/nbd-netlink.h

Local copy of Linux NBD generic netlink UAPI definitions.

It defines the family name, version, multicast group name, NBD configuration attributes, nested device-list attributes, nested socket attributes, and netlink commands: connect, disconnect, reconfigure, link-dead, and status.

`nbd-client.c` uses these definitions when compiled with libnl support to configure NBD devices without the older ioctl flow.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-netlink.h -->