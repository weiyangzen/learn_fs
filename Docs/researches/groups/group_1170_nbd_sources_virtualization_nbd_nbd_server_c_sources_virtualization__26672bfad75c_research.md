# Group Research: group_1170_nbd_sources_virtualization_nbd_nbd_server_c_sources_virtualization__26672bfad75c

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-server.c -->
# File Research: sources/virtualization/nbd/nbd-server.c

## Purpose
Implements the `nbd-server` daemon: configuration parsing, socket setup, modern NBD negotiation, export selection, TLS negotiation, request dispatch, backend file I/O, copy-on-write support, transaction logging, treefile mode, and process/thread lifecycle management.

## Main Entry Points
- `main()` initializes logging/configuration, parses command-line and config-file exports, daemonizes when requested, opens listening sockets, drops privileges, initializes optional GnuTLS state, and enters `serveloop()`.
- `cmdline()` parses legacy command-line export syntax and server options.
- `parse_cfile()` parses GLib key-file configuration, including `[generic]` global settings and per-export groups.
- `setup_servers()`, `open_modern()`, and `open_unix()` create TCP and Unix-domain listening sockets and install signal handlers.
- `serveloop()` accepts connections, monitors child IPC sockets, handles SIGCHLD/SIGTERM/SIGHUP, and appends newly configured exports on reload.
- `handle_modern_connection()` forks per connection unless `dontfork` is enabled, performs negotiation, and starts request serving.
- `negotiate()` implements fixed new-style negotiation and option dispatch for export name, list, abort, STARTTLS, INFO/GO, and structured replies.
- `mainloop_threaded()` reads NBD requests, logs them when enabled, consumes write payloads, and queues work on a GLib thread pool.
- `handle_request()` dispatches read, write, flush, trim, and write-zeroes requests.

## Internal Mechanics
Configuration maps textual parameters to `SERVER` fields and flags. Export groups specify backing path, size, auth file, virtualization mode, COW, treefiles, waitfile, temporary file creation, trim/flush/FUA exposure, TLS enforcement, splice, datalog, and max connections. Included config directories are scanned for `*.conf` snippets.

Negotiation starts with `INIT_PASSWD`, option magic, and fixed-newstyle flags. TLS may be required globally or per export. `NBD_OPT_LIST` lists configured exports when enabled, hiding TLS-only exports before STARTTLS. `NBD_OPT_EXPORT_NAME` and `NBD_OPT_GO` call `commit_client()` to enforce max-client count, derive the peer name and virtualized export path, check ACLs, run prerun hooks, open/export backend storage, prepare transaction logs, and initialize COW/waitfile state.

The I/O path abstracts backend storage through `get_filepos()`, `rawexpread()`, and `rawexpwrite()`. Multifile exports map offsets across a `GArray` of `FILE_INFO`; treefile exports open per-4KiB files on demand; waitfile mode initially records writes into a diff file until the real file appears. COW mode tracks dirty 4KiB pages in `difmap`, reading unmodified data from the base export and modified pages from a per-client diff file.

Replies are serialized under `client->lock`. Ordinary replies use `struct nbd_reply`; structured replies use `send_structured_chunk*()` and `READ_CTX` to split read data or report structured errors. Optional `splice()` paths avoid userspace copies for non-TLS exports when supported.

## Dependencies
Uses GLib arrays/hash tables/key files/thread pools, POSIX sockets/fork/signals/select/pselect, pthread mutex/rwlock primitives, POSIX semaphores, file I/O, optional Linux `splice`, `fallocate`, `BLKDISCARD`, optional Windows zero-data support, and optional GnuTLS. Relies on local protocol helpers from `cliserv.h`, `nbd.h`, `nbd-helper.h`, `nbdsrv.h`, `backend.h`, and `treefiles.h`.

## Risks and Notes
The file mixes daemon-global state, per-export state, per-client state, and per-request worker state, so concurrency behavior depends on disciplined use of `client->lock`, export rwlocks, semaphores, and parent-child IPC. `bad_range()` checks `req->from + req->len` directly, which is sensitive to unsigned overflow. `handle_info()` uses byte-order conversion functions in a semantically confusing way for inbound fields, even if `htonl` and `ntohl` are equivalent on common platforms. Structured error payload fields are not consistently converted at the call site. Some cleanup paths after negotiation or partial client setup return `false` without releasing every object initialized earlier. The COW `difmap` allocation uses `exportsize / DIFFPAGESIZE`, so exports whose size is not a whole diff page need careful boundary assumptions.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-server.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-trdump.c -->
# File Research: sources/virtualization/nbd/nbd-trdump.c

## Purpose
Implements `nbd-trdump`, a command-line utility that reads an NBD transaction log from standard input and prints a human-readable stream of requests, replies, structured replies, and trace-log option records.

## Main Entry Points
- `doread()` reads an exact byte count from a file descriptor, exiting cleanly on EOF or with an error on read failure.
- `main()` validates optional help usage, then loops over log records by magic value and decodes each record.

## Control Flow
The utility reads a 32-bit magic number, converts it from network order, and dispatches on the record type. Request records decode cookie, command, offset, and length, then print command text from `getcommandname()`. Reply records print cookie and error. Trace-log records update `g_with_datalog` when `NBD_TRACELOG_SET_DATALOG` is seen. When datalog is active, write payload bytes after a write request are consumed and discarded. Structured replies print cookie, type, flags, and payload length.

## Dependencies
Uses `cliserv.h`, `nbd.h`, and `nbd-helper.h` for protocol constants, byte-order helpers, and command-name formatting.

## Risks and Notes
Structured reply `paylen` is a 32-bit field, but the code converts it with `ntohs()` instead of `ntohl()`, so displayed payload lengths can be wrong for larger values. The tool intentionally does not interpret structured reply payload bodies.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-trdump.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd-trplay.c -->
# File Research: sources/virtualization/nbd/nbd-trplay.c

## Purpose
Implements `nbd-trplay`, a transaction-log replay tool that applies logged write-like operations to an existing disk image.

## Main Entry Points
- `main()` parses `-i`, `-l`, `-m`, `-b`, `-v`, and help options, opens the image and log, and calls `main_loop()`.
- `main_loop()` reads mixed request/reply/trace records from the transaction log.
- `process_command()` validates block alignment and applies supported commands.
- `dowriteimage()` writes a full buffer to the image at a given offset.
- `doread()` reads exact byte counts from the log.

## Control Flow
Replay requires an image path and log path. The default replay block size is 512 bytes; `-m` limits the number of blocks applied. Trace-log records toggle `g_with_datalog`; actual NBD writes can only be replayed when datalog was enabled in the trace. READ, DISC, and FLUSH are ignored. WRITE consumes logged data and writes it into the image block by block. TRIM and WRITE_ZEROES write zero-filled blocks over the target range.

## Dependencies
Uses POSIX `open`, `read`, and `pwrite`, plus local NBD protocol constants and helpers from `cliserv.h`, `nbd.h`, and `nbd-helper.h`.

## Risks and Notes
Replay operates at `g_blocksize` granularity and rejects unaligned offset/length values. It treats TRIM as zeroing, which may be useful for image reconstruction but does not preserve sparse/hole semantics. The log must contain datalog payloads for WRITE replay; otherwise the program exits.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd-trplay.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbd.h -->
# File Research: sources/virtualization/nbd/nbd.h

## Purpose
Defines userspace-visible NBD protocol constants, ioctl numbers, command codes, feature flags, packet structures, structured-reply types, and protocol error constants.

## Main Contents
- Linux NBD ioctl macros such as `NBD_SET_SOCK`, `NBD_DO_IT`, `NBD_DISCONNECT`, and `NBD_SET_FLAGS`.
- Command enum values for READ, WRITE, DISC, FLUSH, TRIM, CACHE, WRITE_ZEROES, BLOCK_STATUS, and RESIZE.
- Command flag masks for FUA, NO_HOLE, and DF.
- Export/server flags such as read-only, flush/FUA/trim/write-zeroes support, DF support, and multi-connection safety.
- Wire magic values for requests, replies, structured replies, option replies, and transaction logs.
- Packed wire structs: `nbd_request`, `nbd_reply`, `nbd_structured_reply`, and `nbd_structured_error_payload`.

## Dependencies
Requires fixed-width integer types to be available before inclusion. The ioctl macros assume `_IO` is defined by platform ioctl headers when used.

## Risks and Notes
The packed wire structs are central ABI definitions; callers must explicitly convert every multibyte field to or from network byte order. The header intentionally omits kernel-only `nbd_device` details.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbdclt.h -->
# File Research: sources/virtualization/nbd/nbdclt.h

## Purpose
Declares client-side configuration structures used by `nbd-client` and the `nbdtab` parser.

## Main Contents
- `CLIENT` stores parsed client options: export name, device, host/port, TLS files, block size, timeouts, connection count, forced size, option flags, persist-mode settings, and priority string.
- Parser callback declarations: `nbdtab_set_property()`, `nbdtab_set_flag()`, `nbdtab_commit_line()`, and `yyerror()`.
- `saved_connection_t` and `persist_connection_t` hold connection and negotiated metadata for persistent/reconnect behavior.

## Dependencies
Uses `struct addrinfo`, fixed-width integer types, and `bool`; including files must provide the corresponding headers.

## Risks and Notes
This header is a shared data contract for parser and client code, so changes to `CLIENT` fields affect argument parsing, `nbdtab` parsing, and tests.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbdclt.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbdsrv.c -->
# File Research: sources/virtualization/nbd/nbdsrv.c

## Purpose
Provides shared server-side helpers for address matching, client authorization, `SERVER` duplication/refcounting, export size detection, and TRIM/hole-punch handling.

## Main Entry Points
- `address_matches()` checks whether a sockaddr belongs to an address or CIDR mask, including IPv4/IPv6 mapped comparisons.
- `getmaskbyte()` constructs an 8-bit prefix mask.
- `authorized_client()` reads an authorization file and checks the client address against allowed masks.
- `dup_serve()` deep-copies most string fields from a `SERVER`.
- `size_autodetect()` detects export size using `BLKGETSIZE64`, `fstat`, or `lseek(SEEK_END)`.
- `exptrim()` handles NBD TRIM by deleting treefiles or punching holes in backend files.
- `serve_inc_ref()` and `serve_dec_ref()` maintain a global mutex-protected refcount.

## Control Flow
Authorization files are optional; absent or unreadable auth files grant access, while present files are parsed line by line with comments and whitespace stripped. Address matching first parses mask text with `getaddrinfo()`, validates mask length against the client address family, and compares full and partial bytes. Size detection prefers block-device ioctl size, then stat size, then seek-to-end.

## Dependencies
Uses GLib errors/allocation, POSIX networking, file/stat/ioctl/lseek APIs, pthread mutexes, and local `treefiles.h`, `backend.h`, `cliserv.h`, and `nbdsrv.h`.

## Risks and Notes
`authorized_client()` treats an auth file that cannot be opened as allow-all. `serve_dec_ref()` frees only the `SERVER` struct and not dynamically allocated string fields, which is consistent with some call paths but means ownership is delicate. `exptrim()` contains multifile range logic that should be reviewed carefully for cross-file trim ranges.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbdsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbdsrv.h -->
# File Research: sources/virtualization/nbd/nbdsrv.h

## Purpose
Defines the server-side public data model, flag constants, error domain codes, and shared helper prototypes for NBD server code.

## Main Contents
- `VIRT_STYLE` enumerates export-name virtualization strategies: none, literal IP, IP hash, and CIDR hash.
- `SERVER` stores export configuration, including backing path, expected size, listen address, auth file, export flags, virtualization, hooks, named export, connection limits, transaction log, COW directory, and refcount.
- `CLIENT` stores per-connection state: export size/name, peer address, backend file array, locks, socket, selected server, COW/logging state, negotiated flags, TLS session, and socket callback functions.
- `FILE_INFO` maps an open file descriptor to its export start offset.
- `READ_CTX` tracks fragmented or structured read replies.
- `NBDS_ERRS` enumerates configuration, socket, system, splice, and waitfile validation errors.
- Export flags define read-only, multifile, COW, sparse COW, SDP, sync, flush/FUA/rotational/temporary/trim, fixed-newstyle, treefiles, forced TLS, splice, waitfile, and datalog behavior.

## Dependencies
Includes `lfs.h`, GLib, pthread-related declarations through users, semaphores, sockets, and `nbd.h`.

## Risks and Notes
`SERVER` and `CLIENT` are broad shared structs used across daemon, helper library, and tests. Many fields have manual ownership rules, and several flags interact in mutually exclusive ways that are enforced in `nbd-server.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbdsrv.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbdtab_lexer.l -->
# File Research: sources/virtualization/nbd/nbdtab_lexer.l

## Purpose
Defines the flex lexer for `nbdtab` configuration lines.

## Main Rules
- Includes generated `nbdtab_parser.tab.h`.
- Ignores comment lines starting with `#`.
- Returns `SPACE` tokens for spaces/tabs.
- Returns `STRING` tokens for runs excluding whitespace, comma, and equals.
- Returns literal single-character tokens for other characters, including newline.

## Dependencies
Uses `strdup()` to allocate token text into `yylval`. Tokens are consumed by `nbdtab_parser.y`.

## Risks and Notes
Allocated token strings are passed to parser actions without local freeing in this file. The grammar is intentionally small and line-oriented.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbdtab_lexer.l -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/nbdtab_parser.y -->
# File Research: sources/virtualization/nbd/nbdtab_parser.y

## Purpose
Defines the bison grammar for parsing `nbdtab` entries into client configuration callbacks.

## Main Grammar
- `nbdtab` accepts empty input, blank lines, or repeated mount definitions.
- `mountdef` parses `device host exportname` followed by an optional option list, then calls `nbdtab_commit_line()`.
- `option` supports bare flags via `nbdtab_set_flag()` and key/value properties via `nbdtab_set_property()`.

## Dependencies
Includes `nbdclt.h` for callback declarations and client-related types. Uses `char *` semantic values provided by the lexer.

## Risks and Notes
The grammar assumes a compact whitespace-sensitive format with exactly one `SPACE` token between required fields. It delegates all semantic validation to callback implementations.
<!-- END FILE RESEARCH: sources/virtualization/nbd/nbdtab_parser.y -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/netdb-compat.h -->
# File Research: sources/virtualization/nbd/netdb-compat.h

## Purpose
Provides a compatibility definition for `AI_NUMERICSERV` on platforms whose `<netdb.h>` does not define it.

## Main Contents
If `AI_NUMERICSERV` is missing, defines it as `0`, allowing code that sets the flag in `addrinfo.ai_flags` to compile while effectively ignoring the optimization.

## Dependencies
Intended to be included after or alongside networking headers that may define `AI_NUMERICSERV`.

## Risks and Notes
Using zero is acceptable because `AI_NUMERICSERV` is a flag used to avoid service-name resolution; ignoring it changes performance/lookup strictness rather than protocol data layout.
<!-- END FILE RESEARCH: sources/virtualization/nbd/netdb-compat.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/support/genver.sh -->
# File Research: sources/virtualization/nbd/support/genver.sh

## Purpose
Generates a version string from Git metadata for build-time use.

## Behavior
Runs `git describe --dirty`, strips a leading `nbd-`, and falls back to `0.unknown` if no description is available. Prints the resulting string.

## Dependencies
Requires `/bin/sh`, `git`, and `sed` for the preferred path.

## Risks and Notes
The stderr redirection is attached to the `sed` command in the pipeline, so Git errors may still be visible depending on shell behavior. In non-Git source distributions, the fallback version is used.
<!-- END FILE RESEARCH: sources/virtualization/nbd/support/genver.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/systemd/Makefile.am -->
# File Research: sources/virtualization/nbd/systemd/Makefile.am

## Purpose
Defines Automake rules for generating the `nbd@.service` systemd unit from shell/template fragments.

## Main Contents
- Declares `nbd@.service` as `noinst_DATA`.
- Removes generated service files on distclean.
- Distributes `nbd@.service.tmpl` and `sh.tmpl`.
- Builds `nbd@.service` by running generated `nbd@.service.sh`.
- Builds `nbd@.service.sh.in` by concatenating shell and service templates and appending `EOF`.

## Risks and Notes
The `SYSTEMD` installation stanza is commented out, so this Makefile generates but does not install the unit through the shown rules.
<!-- END FILE RESEARCH: sources/virtualization/nbd/systemd/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/systemd/nbd@.service.sh.in -->
# File Research: sources/virtualization/nbd/systemd/nbd@.service.sh.in

## Purpose
Shell template that emits a parameterized systemd unit for managing an NBD client connection for a device instance.

## Behavior
Expands Autoconf variables for prefix paths, then prints a unit with:
- `Description=NBD client connection for %i`
- `PartOf=nbd.service`
- startup before `dev-%i.device` and after `network-online.target`
- oneshot service with `RemainAfterExit=yes`
- `ExecStart=@sbindir@/nbd-client %i`
- `ExecStop=@sbindir@/nbd-client -d /dev/%i`
- install requirements for the base NBD device and partitions `p1` through `p15`

## Dependencies
Requires Autoconf substitution and a shell capable of here-documents.

## Risks and Notes
The generated unit assumes `%i` maps correctly to both `nbd-client` lookup input and `/dev/%i` disconnect path.
<!-- END FILE RESEARCH: sources/virtualization/nbd/systemd/nbd@.service.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/Makefile.am -->
# File Research: sources/virtualization/nbd/tests/Makefile.am

## Purpose
Top-level Automake test directory dispatcher.

## Main Contents
Defines `SUBDIRS = parse code run`, causing parse tests, C unit-style tests, and runtime integration tests to participate in the test build.

## Risks and Notes
All actual test definitions live in the child directories.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/Makefile.am -->
# File Research: sources/virtualization/nbd/tests/code/Makefile.am

## Purpose
Builds and registers small C tests for server helper functions and refactored client argument parsing.

## Main Contents
- `TESTS` and `check_PROGRAMS` include `clientacl`, `dup`, `mask`, `size`, `trim`, and `args_test`.
- Most helper tests link `libnbdsrv.la`, `libcliserv.la`, and GLib.
- `args_test` compiles `args_test.c` with `../../args.c` and GLib.
- `macro.h` is distributed as shared assertion helper support.

## Risks and Notes
Some tests use `punchdummy.c` or local stubs to satisfy backend symbols and keep the tests focused on helper behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/args_test.c -->
# File Research: sources/virtualization/nbd/tests/code/args_test.c

## Purpose
Tests the refactored `nbd-client` argument parser exposed through `parse_nbd_client_args()` and `CLIENT` initialization/free helpers.

## Main Entry Points
- Test helpers `TEST_ASSERT` and `TEST_ASSERT_STR_EQ` count and report pass/fail status.
- Individual test functions cover device-only arguments, normal connection syntax, options, connection checking, disconnect, export listing, version display, netlink-specific options, and error cases.
- `main()` runs all tests and returns success only if every assertion passed.

## Test Coverage
The tests verify that `nbd0` and `/dev/nbd0` are treated as device/nbdtab-style inputs, normal host/port/device parsing works, `-N`, `-b`, and `-timeout` populate fields, `-c` and `-d` set action flags, `-l` lists exports without a device, `-V` marks version output, and invalid block sizes or bad argument counts request process exit. Conditional checks assert different behavior for `-i` and `-L` depending on `HAVE_NETLINK`.

## Dependencies
Includes `../../args.h` and links against `../../args.c`.

## Risks and Notes
The test suite is print-and-count based rather than using a unit-test framework. It assumes parser behavior where some single-argument device forms populate both `hostn` and `dev`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/args_test.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/clientacl.c -->
# File Research: sources/virtualization/nbd/tests/code/clientacl.c

## Purpose
Tests `address_matches()` CIDR matching behavior for IPv4, IPv4-mapped IPv6, and negative cases.

## Main Entry Points
- `do_test()` resolves an address, prints numeric resolved forms, and checks each result against a netmask.
- `main()` runs expected-match and expected-nonmatch cases.

## Dependencies
Uses `getaddrinfo()`, `getnameinfo()`, and `address_matches()` from the server helper library.

## Risks and Notes
The test exits immediately on name-resolution errors. It intentionally validates IPv4-mapped IPv6 compatibility.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/clientacl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/dup.c -->
# File Research: sources/virtualization/nbd/tests/code/dup.c

## Purpose
Tests that `dup_serve()` creates a distinct `SERVER` copy while preserving configured field values.

## Main Entry Points
- `stringcmp()` compares possibly NULL strings.
- `main()` constructs a populated `SERVER`, duplicates it, and uses `count_assert()` on each important field.

## Dependencies
Includes `nbdsrv.h` and `macro.h`.

## Risks and Notes
The test checks equality of values but does not verify that every duplicated string has distinct storage.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/dup.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/macro.h -->
# File Research: sources/virtualization/nbd/tests/code/macro.h

## Purpose
Provides a tiny assertion helper used by code tests.

## Main Contents
Defines a static counter and `count_assert(EXPR)`, which prints the incremented assertion number and then calls standard `assert(EXPR)`.

## Risks and Notes
Because it uses `assert()`, tests compiled with `NDEBUG` would not fail on false expressions.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/macro.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/mask.c -->
# File Research: sources/virtualization/nbd/tests/code/mask.c

## Purpose
Tests `getmaskbyte()` for prefix lengths 0 through 8.

## Behavior
Calls `count_assert()` for expected byte masks: `0`, `0x80`, `0xC0`, `0xE0`, `0xF0`, `0xF8`, `0xFC`, `0xFE`, and `0xFF`.

## Dependencies
Uses `nbdsrv.h` and `macro.h`.

## Risks and Notes
Only covers the 0-8 range; larger inputs are expected by implementation to return `0xFF`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/mask.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/punchdummy.c -->
# File Research: sources/virtualization/nbd/tests/code/punchdummy.c

## Purpose
Provides a dummy `punch_hole()` implementation for tests that link server helpers but do not expect hole punching to be called.

## Behavior
Defines `punch_hole()` to call `g_assert_not_reached()`.

## Dependencies
Includes GLib and `backend.h`.

## Risks and Notes
This is a link stub, not production behavior. Tests using it will fail if the code path unexpectedly calls `punch_hole()`.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/punchdummy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/size.c -->
# File Research: sources/virtualization/nbd/tests/code/size.c

## Purpose
Tests `size_autodetect()` on a temporary file.

## Behavior
Creates and unlinks a temporary file, seeks to byte 1023, writes one byte, and asserts that detected size is 1024 and not 1023.

## Dependencies
Uses `mkstemp()`, `lseek()`, `write()`, `size_autodetect()`, and `macro.h`.

## Risks and Notes
The test exercises regular-file size detection, not block-device ioctl or nonseekable fallback paths.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/size.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/code/trim.c -->
# File Research: sources/virtualization/nbd/tests/code/trim.c

## Purpose
Tests that `exptrim()` translates a basic TRIM request into a backend `punch_hole()` call with the expected file descriptor, offset, and length.

## Main Mechanics
Defines a local `punch_hole()` stub that records arguments. Constructs a minimal `SERVER`, `CLIENT`, and one-entry export array, then calls `exptrim()` with a 1 MiB trim from offset zero.

## Dependencies
Uses GLib arrays, pthread mutex initialization, socketpair setup, `nbdsrv.h`, `backend.h`, and `macro.h`.

## Risks and Notes
The test covers the simple single-file case only. It does not validate COW, treefile, readonly, or multifile trim behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/code/trim.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/parse/Makefile.am -->
# File Research: sources/virtualization/nbd/tests/parse/Makefile.am

## Purpose
Builds and registers parser tests for `nbdtab` input files.

## Main Contents
- Builds `parser` from `parser.c`.
- Links against `libnbdclt.la` and `libcliserv.la`.
- Runs fixture files through `TESTS_ENVIRONMENT = $(builddir)/parser`.
- Test fixtures are `empty`, `noopts`, `singleopt`, `multiopt`, `ipv6`, and `ipv4`.

## Risks and Notes
The parser executable is used as the test harness for each fixture file.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/parse/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/parse/parser.c -->
# File Research: sources/virtualization/nbd/tests/parse/parser.c

## Purpose
Implements the test harness for `nbdtab` parser fixtures.

## Main Entry Points
- Stub callbacks `nbdtab_set_property()`, `nbdtab_set_flag()`, and `nbdtab_commit_line()` assert parser output against an expected `CLIENT`.
- `main()` selects the expected `CLIENT` based on the fixture filename, opens it as `yyin`, suppresses parser output via `yyout`, runs `yyparse()`, and checks whether a commit was seen for nonempty fixtures.

## Dependencies
Uses generated `nbdtab_parser.tab.h`, lexer/parser globals, and `nbdclt.h`.

## Risks and Notes
The harness only accepts property `bs` and flag `no_optgo`, matching the included fixtures. Additional parser features would need fixture and callback expansion.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/parse/parser.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/run/Makefile.am -->
# File Research: sources/virtualization/nbd/tests/run/Makefile.am

## Purpose
Defines runtime integration tests for the NBD server and client test tooling.

## Main Contents
- Selects `cwrap_test` when socket-wrapper support is enabled, otherwise `simple_test`.
- Registers runtime tests such as config loading, write, flush, integrity, directory config, listing, readonly write failure, treefiles, Unix sockets, inetd, handshake, TLS, netlink connect/status, and persist mode.
- Builds `nbd-tester-client` from `nbd-tester-client.c` plus generated/copied `cliserv.c`, and optional TLS sources.
- Builds `libnl_mock.so` from `libnl_mock.c` for netlink-related tests.
- Distributes transaction traces and TLS certificate fixtures.

## Dependencies
Uses Automake conditionals `GNUTLS` and `CWRAP`, GLib flags/libs, optional GnuTLS flags/libs, and libnl flags/libs for the mock.

## Risks and Notes
`XFAIL_TESTS` is supplied by configure-time `@RUN_XFAIL@`. Several target names are empty rules used as Automake test labels.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/run/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/run/cwrap_test -->
# File Research: sources/virtualization/nbd/tests/run/cwrap_test

## Purpose
Wrapper script for running `simple_test` under socket-wrapper/nss-wrapper.

## Behavior
Creates a temporary `SOCKET_WRAPPER_DIR`, sets `LD_PRELOAD` to `libsocket_wrapper.so libnss_wrapper.so`, installs a cleanup trap, runs sibling `simple_test` with the same arguments, and exits with the test status.

## Dependencies
Requires POSIX shell, `mktemp`, socket-wrapper, and nss-wrapper libraries.

## Risks and Notes
The script relies on dynamic loader `LD_PRELOAD` semantics and does not quote every expansion, matching test-harness assumptions.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/run/cwrap_test -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/run/libnl_mock.c -->
# File Research: sources/virtualization/nbd/tests/run/libnl_mock.c

## Purpose
Implements an `LD_PRELOAD` libnl mock used by runtime tests to validate and simulate NBD generic-netlink operations without requiring real kernel netlink behavior.

## Main Entry Points
- `init_real_functions()` resolves real libnl symbols with `dlsym(RTLD_NEXT)`.
- Validation helpers inspect outgoing netlink messages for connect, disconnect, reconfigure, and status commands.
- Overridden libnl functions such as `genl_connect()`, `genl_ctrl_resolve()`, `nl_send_auto()`, `nl_wait_for_ack()`, and `nl_recvmsgs_default()` provide controlled mock behavior.
- Public helpers `mock_set_device_status()`, `mock_set_device_index()`, and `mock_send_link_dead_notification()` allow tests to manipulate mock state.

## Control Flow
The mock returns fixed family/group IDs for `nbd` and `nbd_mc_group`. Outgoing messages are intercepted in `nl_send_auto()`, parsed, and checked for required attributes. Connect validation checks size, block size, server flags, sockets, and optional dead-connection timeout. Disconnect and reconfigure require device index and, for reconfigure, sockets. Status requests record the queried index. `nl_recvmsgs_default()` fabricates a status response and invokes the registered callback.

## Dependencies
Depends on libdl, libnl headers/APIs, Linux netlink headers, and local `nbd-netlink.h`.

## Risks and Notes
Callback role detection in `nl_socket_modify_cb()` is heuristic: the first custom valid callback is treated as status and the next as persist. `nl_socket_get_fd()` returns fake fd `42`, so tests must avoid paths that require a real pollable descriptor. The mock both calls real allocation/parsing helpers and suppresses actual netlink sending.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/run/libnl_mock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/run/nbd-tester-client.c -->
# File Research: sources/virtualization/nbd/tests/run/nbd-tester-client.c

## Purpose
Implements a standalone protocol test client for exercising `nbd-server` without attaching a kernel NBD device.

## Main Entry Points
- `main()` parses test options, opens TCP/Unix/inetd-mode connections, chooses a test function, and runs it.
- `setup_connection_common()` performs initial NBD handshake, optional STARTTLS, export selection, and export-info reading.
- `throughput_test()` streams read or write requests over the whole export, optionally injecting FLUSH and FUA.
- `oversize_test()` verifies server behavior around large read sizes.
- `handshake_test()` sends an unsupported negotiation option and expects a proper `NBD_REP_ERR_UNSUP`, then aborts.
- `integrity_test()` replays a transaction trace while tracking expected block contents and in-flight ordering.
- Helpers manage request-context lists, buffered socket writes, exact reads/writes, generated block contents, cookie uniqueness, and connection shutdown.

## Control Flow
The client can connect by hostname/port, Unix socket, or by launching a server command in inetd mode over a socketpair. It validates `INIT_PASSWD`, option magic, fixed-newstyle flags, optional TLS negotiation, export name selection, export size, and server flags. Tests then send raw NBD request packets and validate reply headers/data.

The integrity test maps a temporary per-block state array, reads a transaction log, rewrites cookies to unique random values, generates deterministic 512-byte data for writes, verifies reads against the last successful write sequence, and prevents unsafe overlapping in-flight requests unless loose ordering is requested.

## Dependencies
Uses POSIX sockets, select, mmap, temporary files, GLib logging/hash tables, local `cliserv.h`, optional GnuTLS wrapper code through `crypto-gnutls.h`, and NBD protocol constants.

## Risks and Notes
The tool deliberately notes that passing here is not equivalent to kernel-client compatibility. It mostly validates ordinary reply mode, not the full structured-reply feature set. Several diagnostics are stored in a global fixed-size `errstr` buffer.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/run/nbd-tester-client.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/tests/run/simple_test -->
# File Research: sources/virtualization/nbd/tests/run/simple_test

## Purpose
POSIX shell integration-test harness that creates temporary NBD server configurations, starts `nbd-server`, runs client/test scenarios, and cleans up.

## Main Scenarios
Covers:
- single and multiple configured exports
- oversized requests
- write tests
- treefile and readonly treefile exports
- flush/FUA/rotational flags
- included config directories
- integrity and large-integrity transaction traces
- export listing through `nbd-client`
- readonly write failure expectations
- Unix-domain sockets
- inetd mode
- handshake error handling
- TLS success, huge TLS transfer, and wrong-certificate failure
- netlink connection-status checks with `libnl_mock.so`
- netlink connect/disconnect behavior
- persist mode and dead-connection timeout options

## Control Flow
The script creates a temporary directory, config file, PID file, and backing image. Each `case` arm writes a minimal config, starts `../../nbd-server` when needed, waits briefly, runs `nbd-tester-client` or `nbd-client`, and stores `retval`. Cleanup kills the daemon by PID file or background PID and removes the temp directory unless requested otherwise.

## Dependencies
Requires POSIX shell tools, `dd`, `mktemp`, `realpath` or `readlink -f`, built `nbd-server`, `nbd-client`, `nbd-tester-client`, optional TLS cert fixtures, optional `timeout`, and optional `libnl_mock.so`.

## Risks and Notes
The harness uses a fixed default delay of one second before connecting, which may be timing-sensitive on slow systems. Some Linux-only checks return skip code `77`. The script intentionally accepts expected failures in readonly/TLS-wrong-cert/netlink cases.
<!-- END FILE RESEARCH: sources/virtualization/nbd/tests/run/simple_test -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/treefiles.c -->
# File Research: sources/virtualization/nbd/treefiles.c

## Purpose
Implements helper functions for treefile exports, where an export is represented as a directory tree of 4KiB block files instead of one large file.

## Main Entry Points
- `construct_path()` recursively builds a path using `TREE%04X` directories and `FILE%04X` leaf files for a logical export position.
- `delete_treefile()` constructs and unlinks the block file for a logical offset.
- `mkdir_path()` creates all intermediate path components.
- `open_treefile()` opens or creates the block file for a logical offset under a mutex.

## Control Flow
`construct_path()` divides the export size by `TREEDIRSIZE` until it reaches leaf-file scale, encoding each path level from the logical page position. `open_treefile()` constructs the path, locks around open/create, creates missing directories when opening read-write, or creates an unlinked dummy tempfile for readonly missing blocks. Newly created block files are extended to `TREEPAGESIZE`.

## Dependencies
Uses POSIX file/path APIs, pthread mutexes, `PATH_MAX`, local `cliserv.h`, `treefiles.h`, and `nbd-debug.h`.

## Risks and Notes
The path builder mutates buffers recursively and relies on caller-provided size checks. Readonly missing blocks are served from a temporary zero-filled file, not from the tree. `mkdir_path()` mutates the path string in place while creating components.
<!-- END FILE RESEARCH: sources/virtualization/nbd/treefiles.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbd/treefiles.h -->
# File Research: sources/virtualization/nbd/treefiles.h

## Purpose
Declares treefile export constants and helper APIs.

## Main Contents
- `TREEDIRSIZE` is 1024 entries per directory level.
- `TREEPAGESIZE` is 4096 bytes per tree block file.
- Declares `construct_path()`, `delete_treefile()`, `mkdir_path()`, and `open_treefile()`.

## Dependencies
Includes pthread and sys/types declarations for mutex and `off_t`/mode usage.

## Risks and Notes
Treefile mode assumes 4KiB block granularity and directory fanout of 1024, which shapes export layout compatibility.
<!-- END FILE RESEARCH: sources/virtualization/nbd/treefiles.h -->