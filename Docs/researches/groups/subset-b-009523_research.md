# subset-b-009523 Research

Grouped research for the requested xfstests-bld dbench and e2fsprogs-libs files. Each section preserves its source path and is wrapped for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h

Source read: complete file, 190 lines, 3938 bytes, sha256 `bb109ca6217103f6653741050952ba8325bb7135c1fcd103074d19860706494e`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h_research.md`.

Purpose: central public header for the bundled dbench/tbench sources. It gathers portability includes from `config.h`, defines shared constants, declares benchmark state structs, imports generated prototypes from `proto.h`, and exposes the global `options` instance.

Important APIs/types/functions: `struct op` records per-operation counts, total time, and max latency; `struct child_struct` carries per-client identity, status flags, byte counters, rate state, per-operation statistics, benchmark directory, and a backend-private pointer; `struct options` holds command-line/build-time behavior such as process count, sync behavior, fsync policy, TCP options, warmup/timelimit, target rate, xattr enablement, fake I/O, cleanup, and reporting flags. It also defines SMB-style create disposition and create option constants used by trace replay functions.

Control flow: this file has no executable control flow. Its inclusion order is important: system headers and fallback macros are established before `proto.h`, so generated prototypes can refer to `struct child_struct`, `struct options`, `BOOL`, `uint32`, and `uint32_t`.

State and persistence behavior: no state is persisted by the header itself. It defines the in-memory contract used by child processes and declares `extern struct options options`, whose concrete storage is supplied by program modules such as `tbench_srv.c` or the dbench main program.

Dependencies and integration: depends on autoconf feature macros for headers, xattr APIs, `MSG_WAITALL`, and `O_DIRECTORY`. It integrates the direct file backend (`fileio.c`), socket backend (`sockio.c`), socket helpers, xattr wrappers, utility functions, and generated prototypes into one compile-time interface.

Risks: `uint32` is an old unsigned-int alias that can hide width assumptions; `O_DIRECTORY` fallback is Linux-specific octal; duplicate `nb_*` prototypes in `proto.h` assume mutually exclusive link targets for file and socket backends. Any change to shared structs has cross-file ABI impact inside the benchmark.

Test signals: successful compilation across configured platforms is the main signal. Trace replay tests should exercise both dbench and tbench builds because they select different `nb_*` implementations behind the same header contract.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c

Source read: complete file, 622 lines, 13907 bytes, sha256 `8d7f185e9b229bf7070a11e7e8559cebf4820874e2823d4ed592633684e62f06`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c_research.md`.

Purpose: implements the dbench direct filesystem replay backend. It translates SMB-like trace operations into local POSIX file, directory, xattr, stat, locking, and fsync calls while maintaining each synthetic client's open-handle table and byte counters.

Important APIs/types/functions: `nb_setup()` allocates a 200-entry `struct ftable` in `child->private`; `find_handle()` resolves trace handles to file descriptors; `sync_parent()` fsyncs/fdatasyncs a containing directory for NFS-like synchronous metadata behavior; `resolve_name()` optionally simulates case-insensitive name resolution and xattr reads. The exported `nb_*` functions implement unlink, mkdir, rmdir, create/open, read, write, close, rename, flush, path/file/fs info probes, findfirst, deltree cleanup, fileinfo updates, byte-range locks, unlocks, and sleeps.

Control flow: trace runner calls `nb_setup()` once per child, then dispatches parsed trace records to the relevant `nb_*` function. Open/create paths compute POSIX flags from SMB create disposition/options, handle directory special cases, store descriptors in the ftable, and initialize optional DOS-attribute xattrs. Read/write/flush/lock paths first resolve a handle, operate on the descriptor, update byte counters, and abort on hard mismatches. Metadata operations often call `resolve_name()` first, compare actual return values with `expected_status()`, and optionally sync the parent directory after mutating operations.

State and persistence behavior: persistent effects are intentional benchmark filesystem mutations under each child directory: files, directories, renames, truncations, timestamps, locks while descriptors are open, and optional `user.DosAttrib` extended attributes. In-memory state includes per-child ftable slots, `child->bytes`, `child->bytes_since_fsync`, failure flags, and rate timing. `nb_cleanup()` recursively removes the child tree unless higher-level options skip cleanup.

Dependencies and integration: includes `dbench.h`, uses `options` for sync, fsync, xattr, stat-check, fake-I/O, no-resolve, one-byte-write, and cleanup behavior, calls xattr wrappers from `system.c`, time helpers from `util.c`, and generated prototypes from `proto.h`. It must not be linked with `sockio.c` in the same executable because both provide the same `nb_*` symbols.

Risks: `resolve_name()` leaks `dname` when no slash is present; `nb_findfirst()` mutates the supplied `fname` buffer despite receiving a `const char *`; `nb_deltree()` skips freeing `fname` on stat failure; many system-call return values are ignored when status comparison is not central; xattr writes cast a byte buffer to `time_t *`, which can be alignment-sensitive. The fixed 200-open-file table can abort on traces with more concurrent handles.

Test signals: replay traces should validate create/read/write byte counts, expected-status handling for failing operations, cleanup idempotence, directory fsync behavior with `sync_dirs`, `fake_io` accounting, and xattr-enabled runs on filesystems with and without user xattr support.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/fileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh

Source read: complete file, 238 lines, 4773 bytes, sha256 `593667e06b70dbc89d41a88c790691ff09349a4427557730fd81ea2accac6ad6`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh_research.md`.

Purpose: portable X11R5-style install helper used by generated makefiles when a platform lacks a suitable BSD-compatible `install` command. It installs files or creates directories while applying mode, owner, group, strip, and optional filename transformations.

Important APIs/types/functions: command-line options include `-c` for copy instead of move, `-d` for directory creation, `-m MODE`, `-o OWNER`, `-g GROUP`, `-s` for strip, `-t=SED_EXPR`, and `-b=SUFFIX`. Environment overrides such as `MVPROG`, `CPPROG`, `CHMODPROG`, `DOITPROG`, and related variables let makefiles substitute tool paths or dry-run behavior.

Control flow: parses options into shell command variables; validates source/destination unless in directory mode; treats directory destinations by appending the source basename; computes `dstdir`; creates missing parent directories component by component; for directory mode creates/chowns/chgrps/strips/chmods the directory; for file mode installs into a temporary `#inst.$$#`, applies attributes, removes the final destination, and renames the temp file atomically into place.

State and persistence behavior: creates directories, copies or moves files, may remove an existing destination, may strip binaries, and applies ownership/mode changes. It installs via a temp file in the destination directory and cleans it through a shell trap.

Dependencies and integration: used by autoconf/automake-like build rules through `INSTALL`, `INSTALL_PROGRAM`, `INSTALL_DATA`, or `INSTALL_SCRIPT`. Depends on POSIX shell plus `mv`, `cp`, `chmod`, `chown`, `chgrp`, `strip`, `rm`, `mkdir`, `basename`, and `sed`.

Risks: many variable expansions are unquoted, so paths with spaces, shell metacharacters, or leading dashes can misbehave. Temporary filename `#inst.$$#` can collide in unusual concurrent scenarios. Ownership changes require privileges and can fail late after the temp file is created.

Test signals: `make install DESTDIR=...` or direct dry-run with `DOITPROG=echo` should show the intended parent directory creation, temp install, chmod, and final rename. Smoke tests should include file install to an existing directory and `-d` hierarchy creation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/install-sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c

Source read: complete file, 209 lines, 4359 bytes, sha256 `0b92196b7a80cd75a0b63cd1cbbead832b387b5e03df12e9a6e4cce46d41b593`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c_research.md`.

Purpose: older direct syscall wrapper layer for simple file-operation trace replay. It maintains a process-global open-file table and exposes `do_*` helpers for create/open/read/write/stat/close/unlink/mkdir/rmdir/rename.

Important APIs/types/functions: `ftable[MAX_FILES]` maps integer trace handles to fds; static `buf[70000]` provides shared read/write data; `do_open()` creates/truncates/expands files and records handles; `expand_file()` writes zeroed chunks; `do_write()` and `do_read()` seek then transfer; `do_stat()` checks file size; `do_create()` opens and closes a fixed temporary handle.

Control flow: callers pass mutable path strings, which are uppercased by `strupper()` before filesystem operations. `do_open()` creates the file, adjusts size to match trace expectations, inserts the handle into the first empty table slot, and prints progress every hundred opens. Read/write/close search the global table linearly and return with diagnostics if the handle is absent.

State and persistence behavior: modifies files/directories in the current working tree, persists created file sizes, and keeps open descriptor mappings in static process state. It uses external `line_count` only for diagnostics and does not maintain per-child state.

Dependencies and integration: includes `dbench.h` for POSIX headers, `MIN`, and prototypes. It relies on `strupper()` from another dbench source file not in this item and on `line_count` from the trace parser. This layer appears to coexist with newer `nb_*` replay code but is a simpler API family.

Risks: fixed 1000-entry handle table, ignored short reads, partial error handling, no bounds check when `do_write()` writes `size` bytes from a 70000-byte buffer, and path mutation via `strupper()` can surprise callers. The global table is not thread-safe and is unsuitable for multi-client sharing without process isolation.

Test signals: simple trace tests should check case transformation, open/expand/truncate behavior, handle-missing diagnostics, file size validation, and cleanup after mkdir/rmdir/rename/unlink operations.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl

Source read: complete file, 112 lines, 2174 bytes, sha256 `bde40ab154569441127efa032dd8b658c5214665858a02147f3207b8cd96088c`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl_research.md`.

Purpose: Perl prototype generator used by `make proto` to produce `proto.h` from C source files. It is inherited from Samba-style tooling and emits public function declarations grouped by source filename.

Important APIs/types/functions: `-h HEADER_GUARD` overrides the default `_PROTO_H_`; `print_header()` and `print_footer()` write include guards; `process_file()` scans one source file; `handle_loadparm()` expands `FN_GLOBAL_*` and `FN_LOCAL_*` macro declarations into accessor prototypes; `process_files()` applies the scanner to all arguments.

Control flow: for each file, it prints a comment header, skips indented lines, non-function-looking lines, comments, semicolon declarations, and `main()`, then matches allowed return-type prefixes. Single-line function signatures ending in `)` get a semicolon; multi-line signatures are printed until a line ending in `)` is reached.

State and persistence behavior: no persistent state beyond generated stdout. It reads listed source files and exits on open failure. The generated header content depends on input order, so build rules must pass sources deterministically.

Dependencies and integration: requires Perl with `strict` but intentionally avoids `warnings` for old portability. Integrates with the dbench build system to regenerate `proto.h`, and its return-type whitelist includes many Samba-era typedefs beyond this small dbench tree.

Risks: regex parsing is approximate and can miss static/indented declarations, emit malformed prototypes for unusual formatting, or duplicate symbols from mutually exclusive backends such as `fileio.c` and `sockio.c`. It does not parse C comments robustly and assumes prototype-worthy signatures start at column zero.

Test signals: run `make proto` and compare the generated `proto.h` with the checked-in version. Add edge-case source snippets only if changing function formatting or return types.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/proto.h -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/proto.h

Source read: complete file, 120 lines, 5605 bytes, sha256 `6922faf139c16be4ae72a631528d83734522cb86a0ef1eb5dade3875ca8935fd`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/proto.h_research.md`.

Purpose: generated prototype header for dbench. It declares cross-file functions used by the trace runner, file backend, socket backend, socket library, xattr portability layer, and utilities.

Important APIs/types/functions: declares `child_run()`, all `nb_*` operations for both `fileio.c` and `sockio.c`, legacy `do_*` operations from `io.c`, socket helpers (`open_socket_in`, `open_socket_out`, `set_socket_options`, `read_sock`, `write_sock`), xattr wrappers (`sys_getxattr`, `sys_fgetxattr`, `sys_fsetxattr`), and utility helpers (`shm_setup`, `all_string_sub`, `next_token`, timeval functions, `msleep`).

Control flow: no runtime control flow. Compile-time inclusion through `dbench.h` gives all modules declarations for functions that may be supplied by different executable link sets.

State and persistence behavior: no direct state. It exposes functions that mutate filesystem state, sockets, shared memory, xattrs, and child benchmark counters.

Dependencies and integration: automatically generated by `mkproto.pl`; depends on types from `dbench.h` being visible first. It integrates modules that are not all linked together in one binary; duplicate `nb_*` prototypes from `fileio.c` and `sockio.c` are acceptable only because the implementations are link-time alternatives.

Risks: editing this file manually risks drift from source definitions. Duplicate prototypes are currently text-identical, but any backend signature divergence would cause compile/link failures. Empty sections for `dbench.c`, `snprintf.c`, and `tbench_srv.c` reflect generator filtering rather than absence of code.

Test signals: regenerate with `make proto`, then compile all dbench/tbench targets. A clean diff and no duplicate-symbol link failures indicate the generated interface still matches the selected backends.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c

Source read: complete file, 981 lines, 22744 bytes, sha256 `a21ecbc52d8fe6626e13579b09b2d07c68ccb21ca75404fbd6a0810c8167f0c1`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c_research.md`.

Purpose: portability implementation of C99-like `snprintf`, `vsnprintf`, `asprintf`, and `vasprintf` for systems missing those functions or having non-C99 behavior. It is a bundled fallback derived from Patrick Powell/Mutt/Samba code.

Important APIs/types/functions: compile-time gates `HAVE_SNPRINTF`, `HAVE_VSNPRINTF`, `HAVE_C99_SNPRINTF`, `HAVE_C99_VSNPRINTF`, `HAVE_ASPRINTF`, and `HAVE_VASPRINTF` decide which replacements are emitted. Internal formatter functions include `dopr()` state-machine parser, `fmtstr()`, `fmtint()`, `fmtfp()`, `dopr_outch()`, and helpers for long double/long long support and decimal splitting.

Control flow: if the platform already has conforming `snprintf` and `vsnprintf`, the file emits only `dummy_snprintf()`. Otherwise `dopr()` scans the format string through states for flags, minimum width, precision, length modifier, and conversion, dispatching to string/integer/floating formatters and counting would-have-written length. Replacement `vsnprintf()` calls `dopr()`; replacement `snprintf()` wraps `vsnprintf()`; `vasprintf()` first computes length with `vsnprintf(NULL, 0, ...)`, allocates, and formats; `asprintf()` wraps `vasprintf()`.

State and persistence behavior: no persistent state. It writes only to caller-provided buffers or malloc-allocated strings. The `TEST_SNPRINTF` block provides a standalone diagnostic program comparing behavior with system `sprintf()`.

Dependencies and integration: uses `config.h`, standard varargs/string/ctype/stdlib headers, optional long double/long long support, and optional math only for the test harness. Integrated implicitly by linking into dbench builds on older platforms.

Risks: the formatter is old and only approximates full modern printf behavior; exponential/significant formats are parsed but routed through fixed-point formatting; `%n` is implemented; pointer formatting casts to `long`, which is width-sensitive; `vasprintf()` does not `va_end()` copied lists; floating conversion caps precision and uses custom arithmetic. Replacement of standard symbols can conflict with libc/linker behavior on partially conforming systems.

Test signals: compile with `-DTEST_SNPRINTF` and run the built-in comparisons. Build configuration should also include autoconf checks for C99 return-length semantics and targeted tests for truncation, `NULL` buffers with count zero, integer widths, and `asprintf()` allocation failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c

Source read: complete file, 250 lines, 5889 bytes, sha256 `2d7fee80c98abf7b7183d38b60ad4e5dea0dd83c56f2bdce737ef4d0227d1297`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c_research.md`.

Purpose: implements the tbench client-side socket replay backend. It maps the same `nb_*` trace-operation API used by dbench onto synthetic SMB-like request/response packet exchanges with a tbench server instead of local filesystem calls.

Important APIs/types/functions: `struct sockio` stores a 70000-byte packet buffer and connected socket fd in `child->private`; `do_packets()` sends a request with encoded send/receive sizes and validates the response header; `nb_setup()` connects to `options.server` on `TCP_PORT`, applies TCP options, and performs an initial small exchange. All exported `nb_*` operations compute operation-specific packet sizes and call `do_packets()`.

Control flow: setup opens a TCP connection and initializes per-child rate state. Each trace callback ignores most semantic fields and models wire cost by calculating an approximate SMB packet size from path length, data size, or result count. Read/write callbacks update `child->bytes`; sleep delegates to `usleep()`. Cleanup/deltree are no-ops because the backend has no local filesystem tree.

State and persistence behavior: persistent state is network-side only: a live TCP connection per child and byte counters in `child_struct`. No files are created locally by this backend.

Dependencies and integration: depends on `socklib.c` for connect, socket options, and robust read/write; depends on `tbench_srv.c` for the echo-like server protocol; shares API names with `fileio.c`, making it a link-time alternative backend for the same trace runner.

Risks: the 70000-byte buffer bounds are implicit; large trace sizes could exceed it. `MSG_TRUNC` behavior with stream sockets is platform-sensitive. Protocol validation checks only payload size, not operation identity or content. Fatal `exit(1)` on short I/O makes transient network failures abort the whole client.

Test signals: run `tbench_srv`, then tbench clients with representative load files and TCP options. Useful signals include stable packet synchronization, expected aggregate throughput, no buffer overflow diagnostics, and byte counter agreement for read/write-heavy traces.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/sockio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c

Source read: complete file, 222 lines, 5487 bytes, sha256 `1b07fb88009edc39665c8891ba4bc5e9457da2a1ae47906530a4ecc8404225be`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c_research.md`.

Purpose: socket utility library for dbench/tbench. It opens inbound/outbound TCP sockets, applies configurable socket options, and provides read/write loops that transfer a requested byte count.

Important APIs/types/functions: `open_socket_in(type, port)` creates, sets `SO_REUSEADDR`, binds to all IPv4 addresses, and applies configured options; `open_socket_out(host, port)` resolves with `gethostbyname()`, connects, and applies options; `set_socket_options(fd, options)` parses comma/space-separated option tokens using `next_token()`; `read_sock()` and `write_sock()` loop over `recv()`/`send()`.

Control flow: socket option parsing optionally accepts `NAME=value`, looks up tokens in `socket_options[]`, decides whether to pass caller value or predefined value, calls `setsockopt()`, and logs unknown/failed options without aborting. Read/write loops advance buffer pointers until the requested size is transferred or a nonpositive syscall result occurs.

State and persistence behavior: creates sockets and kernel socket option state. No local persistence. Errors are returned as `-1` for opens or partial byte counts for transfer loops.

Dependencies and integration: includes `dbench.h` for networking headers, `options.tcp_options`, `BOOL`, and `next_token()`. Used by `sockio.c` clients and `tbench_srv.c` listener/server.

Risks: uses legacy IPv4-only `gethostbyname()` and does not close the socket on hostname resolution failure. `open_socket_in()` returns `-1` on bind failure without closing. `SO_SNDTIMEO`/`SO_RCVTIMEO` are treated as integer options though many platforms expect `struct timeval`. Error handling logs but often continues, so misconfigured TCP options can be silent performance variables.

Test signals: unit-style smoke tests can bind/listen/connect on localhost, set `TCP_NODELAY SO_REUSEADDR`, and verify full-size transfers. Negative tests should cover unknown options, failed DNS, occupied port bind, and server disconnects.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/socklib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c

Source read: complete file, 114 lines, 3758 bytes, sha256 `00d3d9852cc33c76c5b5fd45dc60bcbe4f9b14036e1432904b481cb095279373`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c_research.md`.

Purpose: portability wrappers for extended attribute operations used by dbench's optional DOS-attribute simulation. It normalizes Linux, BSD/extattr, and IRIX attr APIs behind three functions.

Important APIs/types/functions: `sys_getxattr(path, name, value, size)`, `sys_fgetxattr(fd, name, value, size)`, and `sys_fsetxattr(fd, name, value, size, flags)` dispatch to platform-specific xattr APIs when configured. It defines fallback `XATTR_CREATE` and `XATTR_REPLACE` constants when libc lacks Linux xattr headers.

Control flow: each wrapper uses preprocessor feature tests. Linux-style paths call `getxattr`, `fgetxattr`, or `fsetxattr`; BSD-style paths choose system/user namespace from the attribute prefix and strip text before the dot; IRIX-style paths map to `attr_get`, `attr_getf`, or `attr_setf`; unsupported platforms set `errno = ENOSYS` and fail.

State and persistence behavior: get calls only read metadata; `sys_fsetxattr()` persists extended-attribute values on an open file descriptor. State lives in the filesystem, not in process memory.

Dependencies and integration: included via `dbench.h`, which selects available xattr headers. `fileio.c` calls these wrappers when `options.ea_enable` is set to read/write `user.DosAttrib`.

Risks: IRIX branches assume attribute names contain a dot before taking `strchr(name, '.') + 1`; unsupported-platform failures can become fatal in `fileio.c` write hooks when xattrs are enabled. Namespace mapping based on `strncmp(name, "system", 6)` is coarse. Return semantics differ across OS APIs and are only lightly normalized.

Test signals: run dbench with extended attributes enabled on Linux/user-xattr, BSD/extattr, and unsupported filesystems. Verify expected failure handling for `ENOSYS`, permission-denied system namespaces, and successful read/write of `user.DosAttrib`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c

Source read: complete file, 114 lines, 2225 bytes, sha256 `6d51a3696ec0809d08e020337ac1795850e4fc4554d42834036fed3e8bfee3de`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c_research.md`.

Purpose: standalone tbench server that accepts synthetic SMB-size requests from `sockio.c` clients and replies with payloads of the requested size. It is the network counterpart for throughput benchmarking.

Important APIs/types/functions: global `struct options options` defaults `tcp_options` to `TCP_OPTIONS`; `process_opts()` supports `-t` to override socket options; `listener()` opens/listens on `TCP_PORT`, accepts connections, and forks per client; `server(fd)` performs the packet echo protocol.

Control flow: `main()` parses options and enters `listener()` forever. The listener ignores `SIGCHLD`, reaps exited children opportunistically, accepts connections, forks a child to run `server(fd)`, and closes the accepted fd in the parent. Each server child ignores `SIGPIPE`, reads a 4-byte request length, reads that payload, reads response length from the second word, writes a response header plus requested payload, and exits on disconnect or malformed oversized input.

State and persistence behavior: maintains live sockets and forked child processes only. It writes progress markers to stdout and does not persist files.

Dependencies and integration: uses `socklib.c` for socket setup and full reads/writes, `dbench.h` for constants and networking headers, and the packet format expected by `sockio.c`.

Risks: no authentication, IPv4-only listener on all interfaces, unbounded accept loop, fork-per-connection scaling, and fixed 70000-byte buffer. If `open_socket_in()` fails, `listen(-1, ...)` will fail with a generic message rather than reporting bind reason.

Test signals: start the server and connect a tbench client; verify `waiting for connections`, per-client `^` markers, stable throughput, and no `overflow in server!` for representative trace sizes. Port-conflict and socket-option tests should exercise failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/tbench_srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c

Source read: complete file, 180 lines, 4458 bytes, sha256 `808d607c5636fec0fa3e6a4f7ab3337302be90ee07bcecbdb31ac0fa96393cc5`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c_research.md`.

Purpose: miscellaneous portability and utility functions for dbench/tbench: shared memory allocation, in-place string substitution, token parsing, timeval math, and millisecond sleep.

Important APIs/types/functions: `shm_setup(size)` allocates zeroed SysV shared memory that survives fork and is marked for deletion; `all_string_sub()` replaces all occurrences of a pattern in a mutable string; `next_token()` parses separator-delimited tokens with double-quote support; `timeval_current()`, `timeval_elapsed()`, and `timeval_elapsed2()` provide timing helpers; `msleep()` sleeps with `select()`.

Control flow: shared memory setup creates `IPC_PRIVATE` memory, attaches it, immediately `IPC_RMID`s the id, zeroes the segment, and returns the attached pointer. `next_token()` either uses an explicit pointer or static continuation pointer, skips separators, copies until a separator outside quotes, and updates the caller pointer. Time helpers wrap `gettimeofday()`.

State and persistence behavior: SysV shared memory persists across forked children until all attachments exit, but is not left behind after process termination because the id is removed immediately. `next_token()` has static parser state when called with a null pointer. Other functions have no persistence.

Dependencies and integration: used by socket option parsing, child/rate timing, benchmark shared stats, and delay logic. Requires SysV shared memory APIs and standard POSIX time/select calls from `dbench.h`.

Risks: `all_string_sub()` assumes the destination buffer is large enough for expansions, so longer replacement strings can overflow caller storage. `next_token()` static state is not thread-safe and strips quotes rather than preserving escaped quotes. `shm_setup()` exits on allocation failure but returns NULL on attach failure after printing, creating inconsistent caller expectations.

Test signals: shared-memory smoke tests should fork and verify shared counters; token tests should cover comma/space separators and quoted tokens; substitution tests should include shrinking and expanding replacements with adequately sized buffers; timing tests should check monotonic-enough elapsed values for benchmark reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/.missing-copyright -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/.missing-copyright

Source read: complete file, 4 lines, 106 bytes, sha256 `6b674e29b1bd5bbd84152041cbd271098c3072795818b0af1c3f9f319c3637fe`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/.missing-copyright_research.md`.

Purpose: repository audit helper that lists files under the current tree that do not contain `Begin-Header`, excluding editor backups and the `./build` subtree.

Important APIs/types/functions: shell pipeline uses `find . -type f ! -name '*~' ! -exec grep -q Begin-Header {} ; -print | grep -v ^./build`.

Control flow: `find` visits regular files, skips backup names, runs `grep -q Begin-Header` on each, prints files where grep does not find the marker, and filters build paths from the output.

State and persistence behavior: read-only audit script. It prints results to stdout and creates no files.

Dependencies and integration: depends on POSIX shell, `find`, `grep`, and the e2fsprogs convention that license/copyright headers contain `Begin-Header`. It is likely invoked manually by maintainers rather than the normal build.

Risks: filenames with unusual characters are only as robust as the `find -exec`/line-oriented grep pipeline. A file containing `Begin-Header` for another reason is treated as compliant, and generated or vendored paths outside `./build` may produce noise.

Test signals: run from the e2fsprogs-libs root and inspect the printed file list. A clean or intentionally reviewed list is the only expected signal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/.missing-copyright -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in

Source read: complete file, 237 lines, 6942 bytes, sha256 `f1fba893dd385596fa190f84765705f35d7555d539faf33fc86a9515ef90c307`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in_research.md`.

Purpose: autoconf-substituted make configuration template for the bundled e2fsprogs libraries. It centralizes installation paths, compiler/linker flags, tool variables, library names, warning flags, substitution tooling, ownership/mode defaults, and generic rules for config regeneration and dependency generation.

Important APIs/types/functions: defines make variables such as `prefix`, `root_prefix`, `bindir`, `libdir`, `CC`, `BUILD_CC`, `ALL_CFLAGS`, `ALL_LDFLAGS`, `LIBEXT2FS`, `LIBCOM_ERR`, `LIBBLKID`, static/profiled library variants, `INSTALL_*`, `MKINSTALLDIRS`, `SUBSTITUTE`, and `WFLAGS`. Rules include config.status regeneration, MCONFIG generation, `lib/substitute_sh`, `util/subst.conf`, Makefile regeneration, optional autoconf, `.depend`, `depend`, `gcc-wall`, and `gcc-wall-new`.

Control flow: included by generated makefiles through `@MCONFIG@`. Autoconf replaces `@...@` tokens and conditional `@ifGNUmake@`/`@ifNotGNUmake@` blocks. Dependency rules run the compiler with `-M`, transform paths with `sed`, wrap lines with Perl, and splice dependency output back into `Makefile.in` during `make depend`.

State and persistence behavior: generated build state includes `MCONFIG`, `util/subst.conf`, `lib/substitute_sh`, `.depend`, possibly updated `Makefile.in`, and rebuilt configure output. Install variables guide persistent installation of libraries, headers, and manuals elsewhere in the tree.

Dependencies and integration: integrates all e2fsprogs sub-makefiles with autoconf `config.status`, `configure.in`, `util/subst`, compiler dependency generation, and library build fragments in `lib/Makefile.*`. It is consumed by the top-level `Makefile.in` in this item and by subdirectories.

Risks: recursive make and autoconf substitutions make behavior highly environment-sensitive. `make depend` mutates source `Makefile.in`, which can dirty the tree. Warning flags force strict C99/GNU feature macros and may expose platform-specific issues. Incorrect library extension substitutions can break static/shared/profiled link paths.

Test signals: run configure to generate `MCONFIG`, then `make libs`, `make progs`, `make check`, and optionally `make gcc-wall`. Regeneration tests should verify `config.status` updates MCONFIG and Makefiles without unintended diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/MCONFIG.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in

Source read: complete file, 144 lines, 4310 bytes, sha256 `82df8ace90c8c1d5732edf62b5047c741b0e18b13081bc472f90f3f3d9ca4cc6`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in_research.md`.

Purpose: top-level make template for building, installing, cleaning, and checking the bundled e2fsprogs library/program subset inside xfstests-bld.

Important APIs/types/functions: variables include `LIB_SUBDIRS`, `PROG_SUBDIRS`, `SUBDIRS`, generated type headers in `SUBS`, and feature-gated subdirectories for resize/debugfs/uuid/blkid. Targets include `all`, `subs`, `libs`, `progs`, `docs`, install/uninstall variants, recursive clean/distclean/depend/check targets, generated `ext2_types.h`, `blkid_types.h`, `uuid_types.h`, and local clean rules.

Control flow: `all` builds substitutions, libraries, programs, and docs. `subs` generates type headers and prerequisite tools like `compile_et` and `ext2_err.h` when their directories exist. Recursive targets iterate over configured subdirectories and invoke corresponding target names. Program recursion depends on library recursion. Install targets install programs, shared libs, docs, and, if program directories are absent, library-only artifacts.

State and persistence behavior: creates generated headers, build outputs across subdirectories, docs, spec files, and install artifacts. Clean targets remove generated type headers and local build/config files; distclean removes autoconf outputs and generated Makefiles; realclean can remove `configure`.

Dependencies and integration: includes `@MCONFIG@` from `MCONFIG.in`, depends on `config.status`, `util/subst`, `asm_types.h`, and subdirectory makefiles. This file is the recursive build coordinator for e2fsprogs-libs.

Risks: recursive targets skip missing directories silently, so misconfigured source subsets can produce partial builds without obvious failures. The `% : %.sh` suffix-style rule can influence script targets. Install logic has special library-only behavior when program directories are missing, which may surprise package rules.

Test signals: after configure, run `make all`, `make check`, `make install DESTDIR=...`, `make clean`, and `make distclean`. Verify generated type headers exist after `subs` and are removed by clean/distclean as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh

Source read: complete file, 238 lines, 4772 bytes, sha256 `8c0dd928b0220f15e6690ef2ca9763a16d08711ac8707421ba74dee5092084cc`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh_research.md`.

Purpose: portable BSD-compatible install helper for e2fsprogs-libs configure/make installations. It mirrors the dbench `install-sh` behavior for file installs and directory creation.

Important APIs/types/functions: supports `-c`, `-d`, `-m`, `-o`, `-g`, `-s`, `-t=`, and `-b=`; uses environment-overridable tools `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, `MKDIRPROG`, and `DOITPROG`.

Control flow: parses options, validates inputs, detects directory mode, appends source basename for directory destinations, computes and creates parent directory hierarchy, then either creates the target directory with requested attributes or installs a file via destination-local temp file, attribute changes, removal of old target, and rename.

State and persistence behavior: creates or updates installed files/directories, removes overwritten destination files, applies permissions/ownership/group, and may strip binaries. Temporary install files are cleaned on exit.

Dependencies and integration: used by autoconf-generated install variables in `MCONFIG.in` and subdirectory makefiles. Depends on POSIX shell and standard file utilities.

Risks: unquoted shell variables make whitespace/metacharacter paths unsafe. The file initializes `tranformbasename` with a typo while later using `transformbasename`; because both default empty and option parsing assigns the correct variable, behavior is effectively unaffected. Temp filename and non-atomic parent directory creation are old-script limitations.

Test signals: run `make install DESTDIR=...` and direct `config/install-sh -d` / file install smoke tests, optionally with `DOITPROG=echo` to inspect commands. Compare behavior with the dbench copy if consolidating scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/install-sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs

Source read: complete file, 40 lines, 722 bytes, sha256 `208dfecf8a8761b964838808394c09ca887e23421df370ff65dec7773b2f345c`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs_research.md`.

Purpose: public-domain helper script that creates one or more directory hierarchies portably for old make/install flows.

Important APIs/types/functions: accepts directories as positional arguments; tracks `errstatus`; uses `sed` to split each path into components; calls `mkdir` for missing intermediate paths; prefixes `./` when a component path would start with `-`.

Control flow: for each requested path, builds a shell argument list of path components, iteratively appends each component to `pathcomp`, creates missing directories, records mkdir failure if the directory still does not exist, and exits with accumulated status.

State and persistence behavior: creates directories in the filesystem and prints `mkdir PATH` for each creation. No other persistent state.

Dependencies and integration: used by configure/make install rules through `MKINSTALLDIRS` when `install-sh -d` or native `mkdir -p` is unavailable. Depends on POSIX shell, `sed`, and `mkdir`.

Risks: line-oriented path splitting is not safe for whitespace/newlines in paths. Concurrent creators can race but the post-mkdir directory existence check tolerates many benign races. It does not set modes or ownership.

Test signals: direct invocation with nested relative and absolute paths should create all components and return zero. Failure tests should use unwritable parents and leading-dash component names.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/mkinstalldirs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh

Source read: complete file, 118 lines, 2346 bytes, sha256 `5dec511c9bba0b707794f7c88776e45571fa9ec96849b84dd19dfb28f68a0b81`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh_research.md`.

Purpose: configure-time helper that derives Linux `__u*` and `__s*` typedef backing types from `<asm/types.h>`, validates their byte widths, and writes `asm_types.h` for later substitution into generated e2fsprogs headers.

Important APIs/types/functions: builds a temporary `sed.script` that strips comments/blanks and converts typedefs such as `typedef unsigned int __u32;` into `#define __U32_TYPEDEF unsigned int`. Uses `CC`, `CPP`, and `BUILD_CC` environment variables, defaulting to gcc-style commands. Generates and compiles `asm_types.c` to validate 8/16/32/64-bit signed and unsigned widths.

Control flow: writes sed script; preprocesses an include of `<asm/types.h>`; filters macro definitions into `asm_types.h`; removes sed script; copies `asm_types.h` to a C source; appends a test program checking each discovered typedef with `sizeof`; compiles and executes the test; preserves `asm_types.h` on success or empties it on validation failure; removes temporary C and executable files.

State and persistence behavior: persistent output is `asm_types.h` in the current directory. Temporary files are `sed.script`, `asm_types.c`, and `asm_types`, all removed on the normal path.

Dependencies and integration: used by `Makefile.in` rules that generate `lib/ext2fs/ext2_types.h`, `lib/blkid/blkid_types.h`, and `lib/uuid/uuid_types.h`. Depends on a compiler/preprocessor, Linux-like `asm/types.h`, `sed`, `grep`, `cp`, and executable build host.

Risks: assumes preprocessed typedef format matches the sed expressions; cross-compilation can fail because it runs the built `asm_types` executable on the build host; uses old-style C `main()` without an explicit return type; warning directives may be compiler-specific. On validation failure it silently leaves an empty `asm_types.h`, which can move failure later into header generation.

Test signals: run during configure/build on target environments and confirm non-empty `asm_types.h` with all expected typedef defines. Cross-build tests should verify `BUILD_CC` is set correctly and that generated ext2/blkid/uuid type headers compile.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/config/parse-types.sh -->
