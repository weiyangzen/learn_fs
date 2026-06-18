# subset-b-009727 Research

Grouped research for the requested NFS-Ganesha multilock/tracing/tool files and nfs-utils build/export-cache files. Each section is source-path aligned for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_console.c -->
# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_console.c

Purpose: `ml_console.c` is the TCP console/orchestrator for the multilock test suite. It listens for multilock clients, accepts interactive or scripted commands, sends parsed requests to named clients, and verifies asynchronous responses against expected results. It is a control-plane process rather than a lock backend.

Important APIs, types, and functions: `open_socket()` creates the listening socket with `SO_REUSEADDR`; `do_accept()` converts accepted sockets to unbuffered `FILE *` streams and registers clients in the shared `client_list`; `receive()` wraps `pselect()` over the listener, client sockets, and optional stdin; `receive_response()` normalizes socket, timeout, stdin, and signal cases; `process_client_response()` parses client lines via `parse_response()`. Console commands are represented by `enum console_cmd` and dispatched through `console_command()`, with helpers for `CLIENTS`, `FORK`, `EXPECT`, simple expected-status commands, sleeps, strict/fatal toggles, and brace groups.

Control flow: `main()` installs signal handlers, blocks signals around `pselect()`, parses options, opens the listener, optionally syntax-checks and replays a script, then loops between receiving unsolicited responses and reading console commands. Script mode first runs with `syntax = true`, then rewinds the input and uses source line numbers as initial tags. `handle_quit()` sends `QUIT` to all connected clients and builds expected `QUIT` responses before reporting `SUCCESS` or `FAIL`.

State and persistence: state is in process globals: `expected_responses`, `client_list`, `sockets`, `maxfd`, `global_tag`, `num_errors`, `terminate`, and mode booleans. No durable state is written. Client lifetime is reference-counted through `struct response` ownership and `free_response()`.

Dependencies and integration points: this file depends on the shared parser/protocol in `multilock.h` and `ml_functions.c`, POSIX sockets, `pselect()`, signal handling, and stdio streams. It integrates with clients that emit `HELLO` and request/response lines using the multilock protocol.

Risks: `fdopen()` is called twice on the same socket descriptor, so stream close semantics need care; the code explicitly calls `close()` but does not always `fclose()` both streams. `maxfd` is not reduced after closing clients, which is acceptable for `select()` but inefficient. Signal/termination logic relies on global flags and blocked signal masks. The parser uses fixed-size buffers; most helpers bound copies, but protocol fields near `MAXXFER` remain important test cases.

Test signals: sample scripts under `sample_tests/` exercise client registration, braces, simple expected-status commands, forks, lock waits, and quit paths. Useful validation includes script syntax-only mode (`-k`), strict mode behavior on unsolicited responses, interrupted `pselect()`, client disconnect producing tag `-2 QUIT OK`, and error-accounting mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_functions.c -->
# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_functions.c

Purpose: `ml_functions.c` is the shared multilock protocol library. It defines command/status names, token parsers, request/response serializers, response comparison, expected-response list management, global tag handling, and memory cleanup shared by the console and clients.

Important APIs, types, and functions: `commands[]`, token tables for on/off, lock types, read/write flags, open flags, and lock modes encode the text protocol. `readln()`, `SkipWhite()`, `get_token()`, `get_token_value()`, `get_long()`, `get_unsignedlonglong()`, `get_fpos()`, `get_rdata()`, `get_client()`, `get_status()`, and `get_open_opts()` are the parser primitives. `parse_request()` dispatches to `parse_open()`, `parse_lock()`, `parse_unlock()`, `parse_list()`, and related functions; `parse_response()` parses status-specific response payloads. `sprintf_req()`, `sprintf_resp()`, `send_cmd()`, and `respond()` serialize protocol messages. `compare_responses()` implements wildcard-like comparison using `-1` for numeric fields and `"*"` for strings.

Control flow: callers parse input into `struct response`, execute or send commands, then serialize output. Request parsing first obtains an optional/generated tag, command name, and command-specific payload. Response parsing obtains tag, command, status, and status-specific fields. The comparison path checks client, command, tag, status, and command/status payload fields before declaring a match.

State and persistence: globals include `errdetail`, `badtoken`, `client_list`, `input`, `output`, `script`, `quiet`, `duperrors`, `strict`, `error_is_fatal`, `global_tag`, `saved_tags[26]`, `syntax`, and `lno`. There is no durable persistence. Client objects are reference-counted through responses, and `free_client()` unlinks clients from `client_list`.

Dependencies and integration points: this file depends on `multilock.h`, C/POSIX string and file APIs, and lock constants such as `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`. It is the compatibility layer binding `ml_console.c`, `ml_posix_client.c`, and `ml_glusterfs_client.c` to a single textual test grammar.

Risks: several parsing helpers compare `strtol`/`strtoull` end pointers to the post-token cursor, so whitespace/comment edge cases matter. The tag helpers use `if (tolower(*c) >= 'a' || tolower(*c) <= 'z')`, which is logically broad because of `||`; this can index `saved_tags` for non-letter bytes. `sprintf_*` helpers track remaining space but do not explicitly reject truncation. READ data is string-oriented and stores a NUL terminator, so binary data is not represented safely.

Test signals: test coverage should include round-trip parsing/formatting for every command, status-specific parser failures, generated tags and `$a` saved tags, wildcard comparisons, quoted strings with spaces, READ length mismatch, optional open flags and lock modes, and error reporting through `errdetail`/`badtoken`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_glusterfs_client.c -->
# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_glusterfs_client.c

Purpose: `ml_glusterfs_client.c` is a multilock client backend using the GlusterFS libgfapi. It speaks the shared multilock text protocol but performs open/read/write/seek/lock operations through `glfs_*` handles instead of POSIX file descriptors.

Important APIs, types, and functions: `openserver()` connects to the console and sends `HELLO`. `do_open()` uses `glfs_h_lookupat()`, `glfs_h_creat()`, and `glfs_h_open()`; `do_write()`, `do_read()`, and `do_seek()` use `glfs_write()`, `glfs_read()`, and `glfs_lseek()`. Lock operations use `glfs_fd_set_lkowner()` and `glfs_posix_lock()`. The threaded blocking-lock infrastructure is built from `struct work_item`, `work_queue`, `poll_queue`, `fno_work[]`, `schedule_work()`, `cancel_work()`, `get_work()`, and `worker()`.

Control flow: `main()` initializes per-fpos queues, starts one poller plus four worker threads, installs signal handlers, parses console/script/GlusterFS options, initializes the Gluster volume with `glfs_new()`, `glfs_set_volfile_server()`, `glfs_set_logging()`, and `glfs_init()`, then reads protocol commands. Commands are parsed by `parse_request()` and dispatched to backend operations. Blocking `LOCKW` attempts first try nonblocking lock acquisition; if unavailable, the work item is queued and a later worker/poller response completes it.

State and persistence: process state includes console connection strings, `volname`, `glusterserver`, `fds[MAXFPOS+1]`, `handles[MAXFPOS+1]`, `lock_mode[]`, global `glfs_t *fs`, `alarmtag`, worker queues, and mutex/condition variables. No durable state is written by this tool; file content and locks live in the target Gluster volume. The code stores synthetic `r_fno = r_fpos` rather than an OS fd.

Dependencies and integration points: it depends on libgfapi headers (`glusterfs/api/glfs.h`, `glfs-handles.h`), pthreads, the local `gsh_list` intrusive list, POSIX signals, and the shared multilock parser. It integrates with `ml_console` and Gluster volume servers (`-g`, `-v`).

Risks: the `FORK` dispatcher checks `oflags == 7`, but full Gluster server mode sets bits through 31, so `FORK` may be rejected despite server mode. A stale comment and unused `ceph_mount_info *cmount` suggest copy/paste drift. `do_unhop()` does not set `lkowner` before each lock attempt, unlike other lock operations. Negative-return handling mixes `-rc` and `errno` conventions from gfapi. Worker cancellation relies on `pthread_kill(SIGIO)` interrupting lock waits, which may vary by libgfapi behavior.

Test signals: useful tests include Gluster volume initialization failures, create vs lookup open paths, POSIX-owner vs OFD-like owner behavior, LOCKW scheduling and cancellation through UNLOCK, hop/unhop range failure cleanup, script mode EOF, and server-mode `FORK` with all required Gluster options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_glusterfs_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_posix_client.c -->
# sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_posix_client.c

Purpose: `ml_posix_client.c` is the POSIX filesystem backend for multilock tests. It can be driven interactively, by a local script, or by `ml_console`, and it maps protocol commands to `open`, `read`, `write`, `lseek`, `close`, and `fcntl` lock operations.

Important APIs, types, and functions: `fno[MAXFPOS+1]` maps protocol file positions to OS file descriptors, and `lock_mode[]` records POSIX or OFD lock mode. `do_open()` validates OFD lock support with `F_OFD_GETLK` when requested. `do_lock()`, `do_unlock()`, `do_test()`, `do_hop()`, `do_unhop()`, and `do_list()` implement byte-range lock scenarios. `schedule_work()`, `cancel_work()`, `get_work()`, and `worker()` manage asynchronous/blocking `LOCKW` requests using pthreads and `glist`.

Control flow: `main()` initializes queue heads, starts worker threads, installs `SIGALRM`, `SIGPIPE`, and `SIGIO` handlers, parses modes, optionally connects to the console, then reads and dispatches one request per line. Nonblocking lock failure for `LOCKW` queues work and suppresses immediate response; completion is emitted by a worker. `QUIT` exits after responding.

State and persistence: state is process-local: file descriptors, per-fpos lock modes, alarm tag, worker queues, poll queue timing, and global parser I/O streams. File content and kernel locks are external state. Lock wait cancellation tracks queued ranges in `fno_work[]` and cancels work fully covered by an UNLOCK range.

Dependencies and integration points: it depends on POSIX file and lock APIs, OFD lock constants defined in `multilock.h` when absent, pthreads, signals, `gsh_list`, and the shared multilock parser. It is the primary backend for local filesystem lock test scripts.

Risks: `pthread_create()` return values are compared with `-1` even though pthreads return nonzero error numbers. `fno[0]` defaults to descriptor 0; most checks permit `fpos == 0`, so stdin can be used as an implicit fd unless scripts avoid it. `do_read()` converts bytes to C string length, which truncates at NUL. Blocking lock cancellation assumes `SIGIO` interrupts `fcntl(F_SETLKW)`. `get_work()` constructs `struct timespec` with fields reversed for `pthread_cond_timedwait()` (`tv_sec` receives delay but initializer order is `{ seconds, nanoseconds }` only if the implementation layout matches).

Test signals: sample scripts should cover POSIX and OFD modes, blocking lock grant/cancel/deadlock, lock splitting, hop/unhop, READ/WRITE/SEEK, alarm completion/cancel, client fork, and invalid fpos/fd paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/ml_posix_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/multilock.h -->
# sources/user-network-fs/nfs-ganesha/src/tools/multilock/multilock.h

Purpose: `multilock.h` is the public interface and protocol contract for the multilock console and clients. It centralizes buffer sizes, command/status enums, client/response structures, parser/serializer prototypes, utility macros, and textual command/response documentation.

Important APIs and types: `MAXSTR`, `MAXDATA`, `MAXXFER`, and `MAXFPOS` bound protocol fields. `enum commands` defines OPEN, CLOSE, LOCKW, LOCK, UNLOCK, TEST, LIST, HOP, UNHOP, SEEK, READ, WRITE, COMMENT, ALARM, HELLO, FORK, and QUIT. `enum status` defines OK, AVAILABLE, GRANTED, DENIED, DEADLOCK, CONFLICT, CANCELED, COMPLETED, ERRNO, PARSE_ERROR, and ERROR. `struct client` stores socket streams, name, list links, and refcount. `struct response` stores parsed protocol fields and original text. `enum lock_mode` chooses POSIX vs OFD locks.

Control flow and integration: the header exposes parser helpers (`parse_request()`, `parse_response()`), formatters (`sprintf_req()`, `sprintf_resp()`), response list helpers, and send/respond functions implemented in `ml_functions.c`. Console and client files include it as the single protocol schema.

State and persistence: state is declared as extern globals: parser error buffers, `client_list`, `input`, `output`, mode flags, `global_tag`, `syntax`, and line number. The header does not persist data; it defines in-memory layouts and conventions.

Dependencies: it includes standard C/POSIX headers for file, socket, signal, select, netdb, and path constants. It conditionally defines Linux OFD lock constants if the platform headers do not.

Risks: the utility macros use GNU variadic macro syntax (`args...`) and assume arrays, not pointers, for `array_strcpy`/`array_strncpy`. `array_sprintf` computes but does not use `left` after one call. Protocol buffers are fixed-size; callers must maintain max lengths. `struct sockaddr c_addr` may not hold all address families even though current code uses IPv4.

Test signals: compile coverage should include systems with and without `F_OFD_*` constants. Protocol tests should confirm the documented command/response forms match the parser and formatter behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/multilock/multilock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/test_findlog.c -->
# sources/user-network-fs/nfs-ganesha/src/tools/test_findlog.c

Purpose: `test_findlog.c` is intentionally not valid C; it is a fixture of logging-call patterns for `findlog.sh`. It exercises the script's ability to find log macro invocations while ignoring comments, strings, unrelated identifiers, and malformed contexts.

Important content: the file includes `LogTest()` calls with tabs, spaces, semicolons inside quoted strings, multi-argument calls, calls split over lines, macro-expanded calls, calls after assignments, `LogCrit()` in `else if` contexts, and lower-case `Logtest()` that should not match if matching is case-sensitive. Comments label cases where the expected extraction is currently too broad.

Control flow: there is no executable control flow. The apparent C statements are test input for a text parser. The fixture's ordering and line placement matter because expected results refer to concrete line numbers.

State and persistence: no runtime state. Persistence is the fixture text itself; changing whitespace or line numbers can affect `findlog.sh` expectations.

Dependencies and integration points: it integrates with `src/tools/findlog.sh` and whatever test harness compares discovered logging calls. It imitates Ganesha logging macros such as `LogWarn`, `LogCrit`, and arbitrary `LogTest`.

Risks: because the file is not valid C, build systems and static analyzers must not compile it. Test fragility is high: line number changes, macro formatting changes, or additional comments can change expected output. It also documents known overmatching areas rather than enforcing them.

Test signals: run `findlog.sh` against this fixture after parser changes; verify comments are ignored, multiple macro calls are discovered, quoted semicolons are handled, and non-log tokens such as `LogComponents` or `LogFile` are not mistaken for calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tools/test_findlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/tracing/CMakeLists.txt

Purpose: this CMake file builds and installs Ganesha's optional LTTng tracing module and exposes weak-symbol tracepoint support for other targets.

Important targets and APIs: it includes `${LTTNG_INCLUDE_DIR}`, builds `ganesha_trace` as a `MODULE` from `lttng_probes.c`, applies `add_sanitizers()`, and links `${LTTNG_LIBRARIES}`. It also defines `ganesha_trace_symbols` as an `INTERFACE` library that contributes `lttng_defines.c` to consumers and links LTTng libraries. `gsh_trace_header_generate` depends on `ntirpc_generate_lttng_trace_headers` and `gsh_generate_lttng_trace_headers`.

Control flow: generated trace headers are made prerequisites of both the loadable module and interface symbol target via `add_dependencies()`. Installation places `ganesha_trace` in `${LIB_INSTALL_DIR}` under component `tracing`.

State and persistence: build outputs are CMake target artifacts; no runtime state is handled here.

Dependencies and integration points: this file integrates CMake, LTTng discovery variables, sanitizer helpers, and generated trace header targets elsewhere in the project. Consumers that call tracepoints should link `ganesha_trace_symbols`; runtime tracing loads the module.

Risks: missing generated-header target definitions or unset LTTng variables will break configuration/build. Since `ganesha_trace` is a module, runtime loader paths and install component packaging need validation. The interface source pattern is unusual but intentional for weak tracepoint definitions.

Test signals: configure with `USE_LTTNG`, build both targets, verify generated headers run first, confirm linked consumers resolve tracepoint weak symbols without loading the module, and install/package the tracing component.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/lttng_defines.c -->
# sources/user-network-fs/nfs-ganesha/src/tracing/lttng_defines.c

Purpose: `lttng_defines.c` emits weak LTTng tracepoint symbols for code that calls tracepoints while allowing tracing to remain disabled unless the real probe module is loaded.

Important macros and includes: under `USE_LTTNG`, it defines `TRACEPOINT_DEFINE` and `TRACEPOINT_PROBE_DYNAMIC_LINKAGE`, then includes `gsh_lttng/generated_traces/generated_lttng.h` unless `LTTNG_PARSING` is set. These macros drive LTTng tracepoint header expansion.

Control flow: there is no runtime control flow. Compilation of this file into targets via `ganesha_trace_symbols` supplies weak functions; dynamic loading of `libganesha_trace.so` supplies overriding implementations from `lttng_probes.c`.

State and persistence: no persistent or mutable state. Symbol tables and link behavior are the meaningful artifact.

Dependencies and integration points: depends on generated trace headers and LTTng macro semantics. It is linked into any target that directly references tracepoints.

Risks: including generated trace headers more than once with definition macros in one binary can cause duplicate symbols. If consumers forget `ganesha_trace_symbols`, tracepoint calls may fail to link. If `USE_LTTNG` is off, this compiles to an inert file.

Test signals: build LTTng-enabled targets with and without loading the trace module; verify link success and that weak definitions do not emit events until overridden.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/lttng_defines.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/lttng_probes.c -->
# sources/user-network-fs/nfs-ganesha/src/tracing/lttng_probes.c

Purpose: `lttng_probes.c` instantiates the actual LTTng tracepoint probes for Ganesha's loadable tracing module.

Important macros and includes: under `USE_LTTNG`, it defines `TRACEPOINT_CREATE_PROBES` and includes `gsh_lttng/generated_traces/generated_lttng.h` unless `LTTNG_PARSING` is defined. This is the canonical LTTng pattern for creating tracepoint probe implementations.

Control flow: no explicit runtime control flow. The generated probe symbols are loaded with the `ganesha_trace` module and override/couple with the weak symbols from `lttng_defines.c`.

State and persistence: no local state. Runtime tracing state is handled by LTTng and the dynamic loader.

Dependencies and integration points: depends on generated trace headers, `USE_LTTNG`, and the CMake module target. It must include every trace header once, according to the file comments, to avoid missing or duplicate probes.

Risks: including generated headers from multiple probe compilation units can duplicate probes; missing generated headers disables trace coverage. Runtime behavior depends on loading the module in the right process address space.

Test signals: build `ganesha_trace`, load it in an LTTng-enabled deployment, and verify events flow for tracepoints that otherwise link through weak definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/tracing/lttng_probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/valgrind.sh -->
# sources/user-network-fs/nfs-ganesha/src/valgrind.sh

Purpose: `valgrind.sh` is a tiny wrapper to run an arbitrary command under Valgrind leak checking with a larger permitted stack frame and a fixed log file.

Important behavior: it invokes `valgrind --leak-check=full --max-stackframe=3280592 --log-file=/tmp/valgrind.log $*`.

Control flow: the script has a single command and passes all arguments to Valgrind. There is no option parsing or cleanup.

State and persistence: it writes Valgrind output to `/tmp/valgrind.log`, overwriting or appending according to Valgrind behavior. It does not create per-run logs.

Dependencies and integration points: depends on `/bin/sh` and Valgrind. It is likely used manually for Ganesha binaries that exceed Valgrind's default stack-frame expectations.

Risks: unquoted `$*` performs shell word splitting and glob expansion, so arguments containing spaces are unsafe. The fixed `/tmp/valgrind.log` path causes concurrent runs to collide. Exit status is Valgrind's status; the script does not post-process failures.

Test signals: invoke with a command containing spaces or options to confirm argument handling, and run concurrent invocations to validate log collision expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/Makefile.am -->
# sources/user-network-fs/nfs-utils/Makefile.am

Purpose: this is the top-level Automake entry for nfs-utils. It defines subdirectories, distributed macro/bootstrap files, aclocal search paths, and install/uninstall hooks for NFS state directories.

Important variables and targets: `AUTOMAKE_OPTIONS = foreign`; `SUBDIRS = support tools utils linux-nfs tests systemd`; `EXTRA_DIST` includes `autogen.sh` and aclocal macros; `ACLOCAL_AMFLAGS = -I aclocal`. `install-data-hook` creates `$(statedir)` files (`etab`, `rmtab`) and statd state directories/files under `$(statdpath)`, permissions them, and attempts ownership by `$(statduser)`. `uninstall-hook` removes state files.

Control flow: Automake recurses into subdirectories during build/install. Hooks run during data install/uninstall after normal target actions.

State and persistence: installation creates persistent runtime state under configured NFS and statd state directories. These files are not build artifacts; they are daemon state placeholders.

Dependencies and integration points: integrates with variables substituted by `configure.ac` (`statedir`, `statdpath`, `statduser`) and the recursive Automake tree.

Risks: uninstall removes state files directly and may fail if missing; install uses `-chown` to ignore ownership failures. Package managers may prefer owning directories/files explicitly rather than hook-created state. `xtab` removal remains in uninstall even install creates `etab`/`rmtab`.

Test signals: run `make install DESTDIR=...` and inspect state paths, modes, and ownership behavior; run `make dist` to ensure `EXTRA_DIST` covers bootstrap macro files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/autogen.sh -->
# sources/user-network-fs/nfs-utils/autogen.sh

Purpose: `autogen.sh` cleans generated Autotools artifacts and regenerates the configure/build system for nfs-utils from source.

Important commands: it removes common helper files (`compile`, `config.guess`, `config.sub`, `depcomp`, `install-sh`, `ltmain.sh`, `missing`, `mkinstalldirs`), generated files (`aclocal.m4`, `configure`, `config.h.in`), `autom4te.cache`, all `Makefile.in`, and all `Makefile`. Unless invoked as `autogen.sh clean`, it runs `aclocal -I aclocal`, `libtoolize --force --copy`, `autoheader`, `automake --add-missing --copy --gnu`, and `autoconf`.

Control flow: cleanup always runs first. A literal first argument `clean` exits before regeneration.

State and persistence: it deletes and recreates generated build-system files in the source tree. This is intentionally destructive to generated artifacts but not to source files.

Dependencies and integration points: depends on Autotools, libtool, local `aclocal/` macros, and the Automake/Autoconf definitions in `configure.ac`/`Makefile.am`.

Risks: removing every `Makefile` below the tree can wipe local configured build directories if run in-tree. `echo -n` portability varies by shell. The script uses `set -e`, so missing tools abort the bootstrap.

Test signals: run `./autogen.sh clean` to verify cleanup-only mode, then run `./autogen.sh` in a clean checkout to confirm all generated files are recreated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/configure.ac -->
# sources/user-network-fs/nfs-utils/configure.ac

Purpose: `configure.ac` is the Autoconf configuration source for nfs-utils 2.9.1. It defines build options, dependency probes, feature conditionals, generated files, compiler warning policy, and installed path substitutions.

Important options and APIs: options include release, state/config/statd paths, systemd unit installation, NFSv4, blkmapd, GSS/svcgss, kprefix, rpcgen selection, uuid/blkid, mount/libmount, sbin override, junction support, TI-RPC, IPv6, nfsdcld/nfsrahead/nfsdcltrack, nfsdctl, nfsv4server, LDAP/GUMS, and plugin paths. It uses project macros such as `AC_LIBTIRPC`, `AC_LIBCAP`, `AC_LIBXML2`, `AC_TCP_WRAPPERS`, `AC_GETRANDOM`, `AC_LIBEVENT`, `AC_SQLITE3_VERS`, `AC_KEYUTILS`, `AC_KERBEROS_V5`, and `AC_RPCSEC_VERSION`.

Control flow: feature flags are parsed first, then required libraries/headers/functions are probed, then compiler and build-tool state is established. Conditional Automake variables drive subdirectory builds. At the end, path substitutions and warning flags are emitted and a long `AC_CONFIG_FILES` list enumerates generated Makefiles and systemd/pkg-config files.

State and persistence: generated outputs include `support/include/config.h`, Makefiles across the tree, systemd units, and libnfsidmap pkg-config metadata. It exports configured runtime paths such as `NFS_STATEDIR`, `NSM_DEFAULT_STATEDIR`, and `NFS_CONFFILE`.

Dependencies and integration points: this file is the root integration point for libtirpc, libnl3/genl, sqlite, keyutils, Kerberos/GSS, libevent, libblkid, libmount, libxml2, optional LDAP, and kernel netlink headers (`nfsd_netlink.h`, `lockd_netlink.h`, `sunrpc_netlink.h`). It also chooses internal vs system rpcgen.

Risks: it unconditionally defines `HAVE_NFSD_NETLINK` after checking headers, so compatibility fallback headers must be valid when system headers are absent. Many optional features become hard dependency checks when enabled. Strict warning flags can break builds on newer compilers. Cross-compilation paths make assumptions for statd user and sqlite version.

Test signals: configure matrix testing should cover minimal build, NFSv4/GSS enabled and disabled, internal vs system rpcgen, netlink header present/absent, `--disable-uuid`, systemd custom unit dir, junction support, and cross-compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/install-dep -->
# sources/user-network-fs/nfs-utils/install-dep

Purpose: `install-dep` is a convenience script that installs build dependencies for nfs-utils on common Linux distributions.

Important behavior: it detects package managers with `command -v` and runs package installation for dnf/yum-family, apt-family, or zypper-family systems. Packages include Autotools, libtool, make/gcc, rpcgen, libtirpc, libevent, sqlite, device-mapper, blkid, Kerberos, keyutils, uuid, and related development headers.

Control flow: each package-manager block is independent; on unusual systems with multiple package managers, more than one block could run. The dnf/yum detection uses shell operator precedence: `command -v dnf >/dev/null || command -v yum >/dev/null && { yum install ...; }`, so it actually invokes `yum` in the block even when only `dnf` was detected.

State and persistence: it modifies the host package database and installs system packages. It does not write repo files.

Dependencies and integration points: depends on root privileges and the target package manager. It supports building source configured by `configure.ac`.

Risks: package installs are non-idempotent but generally safe; they require network and privileges. The dnf/yum logic likely should call the detected tool rather than hard-coded `yum`. Apt uses `--ignore-missing`, which can hide missing dependencies.

Test signals: run in clean containers for Fedora/RHEL, Debian/Ubuntu, and openSUSE; verify each package list satisfies `./autogen.sh && ./configure` for desired feature sets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/install-dep -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/linux-nfs/Makefile.am -->
# sources/user-network-fs/nfs-utils/linux-nfs/Makefile.am

Purpose: this Automake file packages historical linux-nfs documentation files with the nfs-utils distribution.

Important variables: `EXTRA_DIST = ChangeLog INSTALL KNOWNBUGS NEW README THANKS TODO`; `MAINTAINERCLEANFILES = Makefile.in`.

Control flow: no build targets are defined; Automake includes these files in distribution archives and removes `Makefile.in` during maintainer clean.

State and persistence: distribution-only documentation; no runtime state.

Dependencies and integration points: included from top-level `SUBDIRS`, and generated by `configure.ac` as `linux-nfs/Makefile`.

Risks: stale historical docs can be shipped if not curated. No compile-time risk.

Test signals: `make distcheck` should confirm these files are present and no missing build rules exist.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/linux-nfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/nfs.conf -->
# sources/user-network-fs/nfs-utils/nfs.conf

Purpose: `nfs.conf` is the default/general configuration template for NFS daemons and tools. It documents configurable sections and default values, with most settings commented out.

Important sections: `[general]`, `[nfsrahead]`, `[exports]`, `[exportfs]`, `[gssd]`, `[lockd]`, `[exportd]`, `[mountd]`, `[nfsdcld]`, `[nfsd]`, `[statd]`, `[sm-notify]`, and `[svcgssd]`. Active defaults in this file include `rdma=y` and `rdma-port=20049` under `[nfsd]`; most other settings are examples/comments.

Control flow: the file is read by nfs-utils components that use the configured `NFS_CONFFILE`. Daemon-specific parsers consume their sections to override compiled defaults and command-line values.

State and persistence: this is persistent system configuration, normally installed under `/etc/nfs.conf` or the configured `--with-nfsconfig` path.

Dependencies and integration points: integrates with `configure.ac` path substitution and daemons such as gssd, mountd, exportd, nfsd, statd, and sm-notify.

Risks: because `rdma=y` is uncommented, systems without RDMA support may see different behavior than a purely commented template would imply. Comments can drift from actual daemon defaults. Sensitive options such as keytab and credential cache paths need secure deployment choices.

Test signals: install and run `nfsconf`/daemon startup tests to verify each section is parsed, active RDMA defaults are honored or safely ignored, and commented options remain inert.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/nfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/Makefile.am

Purpose: this Automake file controls recursive builds for support libraries and helper modules used by nfs-utils.

Important variables: `OPTDIRS` begins empty, adds `nfsidmap` under `CONFIG_NFSV4`, and adds `junction` under `CONFIG_JUNCTION`. `SUBDIRS = export include misc nfs nsm reexport $(OPTDIRS)`. `MAINTAINERCLEANFILES = Makefile.in`.

Control flow: Automake recurses into always-built support directories plus feature-conditional directories selected by `configure.ac`.

State and persistence: build outputs are static support libraries/headers in subdirectories; no runtime state is defined here.

Dependencies and integration points: integrates Automake conditionals from `configure.ac` with support components used by tools and daemons.

Risks: feature conditionals must match generated config headers and source expectations. Directory order matters for headers/libraries consumed by later subdirectories.

Test signals: configure with NFSv4 and junction enabled/disabled and verify recursive targets include/exclude `nfsidmap` and `junction` as intended.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/export/Makefile.am

Purpose: this Automake file builds the internal `libexport.a` support library and generated mount protocol RPC sources for export-related nfs-utils code.

Important variables and targets: generated files are `mount_clnt.c`, `mount_xdr.c`, and `mount.h` from `mount.x`. `libexport_a_SOURCES` includes client/export/hostname/xtab/cache/auth/v4root/fsloc/v4clients sources plus generated RPC files. CPPFLAGS include `support/reexport` and libnl flags. `RPCGEN` is either the internal built tool or `@RPCGEN_PATH@`. Rules generate client, XDR, and header outputs, and the header rule symlinks `support/include/mount.h`.

Control flow: generated sources are listed in `BUILT_SOURCES`, so they are created before compilation. `dist-hook` removes generated files from distribution snapshots. `CLEANFILES` removes generated outputs and the include symlink.

State and persistence: build-time generated C/header files and a symlink are created. No runtime state.

Dependencies and integration points: depends on rpcgen, libnl cflags, export support sources, and configure's `CONFIG_RPCGEN` conditional. `cache.c` and `auth.c` from this subset are part of this static library.

Risks: parallel builds depend on correct `BUILT_SOURCES` ordering and symlink creation. Generated files must not be shipped in dist archives if `dist-hook` removes them. RPCGEN path mismatches can break bootstrapped builds.

Test signals: run clean parallel builds with internal and system rpcgen; verify generated files exist, the symlink points to `../export/mount.h`, and `make distcheck` succeeds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/auth.c -->
# sources/user-network-fs/nfs-utils/support/export/auth.c

Purpose: `auth.c` authenticates mount requests against the current export table. It normalizes requested paths, resolves clients, reloads exports when state changes, chooses matching exports, and enforces privileged-port restrictions.

Important APIs, types, and functions: `auth_reload()` tracks `etab.statefn` inode changes, calls `export_freeall()`, `xtab_export_read()`, `check_useipaddr()`, and `v4root_set()`, then returns a reload counter. `check_useipaddr()` enables IP-address cache mode when netgroup hostnames would exceed kernel cache name limits. `get_client_hostname()` returns composed client domains, `DEFAULT`, or `$ip` form. `client_matches()`, `ipaddr_client_matches()`, and `namelist_client_matches()` abstract client matching. `auth_authenticate()` is the public entry point.

Control flow: `auth_authenticate()` rejects non-absolute paths, copies and fixes duplicate/trailing slashes, resolves the caller address, then repeatedly tries the longest path prefix by truncating at slashes. `auth_authenticate_internal()` calls `auth_authenticate_newcache()` and rejects high source ports unless the export has `NFSEXP_INSECURE_PORT`. Logging reports distinct auth errors.

State and persistence: static `my_exp` and `my_client` hold the returned export/client data, so the return value is not independently owned. `auth_reload()` keeps the last open etab fd and inode to avoid stale inode reuse, and updates the global export/client lists. It may flush kernel caches when `use_ipaddr` changes.

Dependencies and integration points: depends on export parsing/list structures, client resolution/matching helpers, `cache_flush()`, `v4root_set()`, state file metadata, xlog, and sockaddr utilities. Used by mountd/exportd authentication flows.

Risks: the returned static export is overwritten on subsequent authentication. `auth_reload()` treats unchanged inode as unchanged content, so in-place edits without replacement could be missed if the state workflow allowed them. Long netgroup behavior changes cache keying and flushes caches, which can affect live clients. Privileged-port enforcement depends on caller sockaddr correctness.

Test signals: cover absolute-path validation, duplicate slash cleanup, longest-prefix export matching, netgroup thresholds toggling `use_ipaddr`, V4ROOT exclusion for v2/v3 auth, insecure-port exports, and etab replacement vs unchanged-inode reload behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/cache.c -->
# sources/user-network-fs/nfs-utils/support/export/cache.c

Purpose: `cache.c` is the nfs-utils userspace bridge for kernel NFS/SUNRPC caches. It answers auth.unix.ip, auth.unix.gid, nfsd.export, and nfsd.fh upcalls via legacy `/proc/net/rpc/*/channel` files or newer generic netlink families, and it can proactively seed export and filehandle cache entries.

Important APIs, types, and functions: legacy handlers are `auth_unix_ip()`, `auth_unix_gid()`, `nfsd_export()`, and `nfsd_fh()`. Export/filehandle matching uses `parse_fsid()`, `match_fsid()`, `lookup_export()`, `path_matches()`, `same_path()`, `subexport()`, `uuid_by_path()`, and `dump_to_cache()`. Netlink support is opened by `cache_nfsd_nl_open()` and `cache_sunrpc_nl_open()`, drains notifications, gets pending requests, and sets replies through `cache_nl_process_export()`, `cache_nl_process_expkey()`, `cache_nl_process_ip_map()`, and `cache_nl_process_unix_gid()`. Public entry points are `cache_open()`, `cache_set_fds()`, `cache_process_req()`, `cache_process()`, `cache_export()`, `cache_get_filehandle()`, `cache_wait_for_workers()`, and `cache_fork_workers()`.

Control flow: `cache_open()` prefers netlink unless `no_netlink` is set or family setup fails, then falls back to opening procfs cache channels. Service loops call `cache_set_fds()` and `cache_process()`/`cache_process_req()` to handle ready fds. Netlink handlers receive cache-type notifications, reload exports, fetch batched kernel requests, resolve them, and send SET_REQS replies. Legacy handlers read one qword-encoded line, resolve it, and write a qword-encoded reply. Filehandle lookups that cannot be answered because a mountpoint is temporarily unavailable are queued in `delayed` and retried every `RETRY_SEC`.

State and persistence: persistent kernel cache entries are written with expiries based on `default_ttl` or long-lived fsid-path cache timeouts. Process state includes netlink sockets/family ids, procfs fds in `cachelist`, reusable group buffers, `delayed` retry list, and static blkid cache. Export data is refreshed through `auth_reload()` before resolving requests.

Dependencies and integration points: depends on kernel nfsd/sunrpc cache ABIs, libnl/genl, nfs-utils export/client databases, reexport fsid database, mount table parsing, blkid, optional junction/libxml support, pseudo-flavor security helpers, xprtsec, v4clients fd processing, and `nfsd_path_*` wrappers.

Risks: this file is highly coupled to kernel ABI constants and qword/netlink schemas. Export matching for crossmnt and reexport fsidnum is complex and can choose the wrong export if paths alias or filehandles collide. `name_to_handle_at` fallback to inode can be wrong for bind mounts. Large netlink batches can overflow messages and trigger partial flush/retry paths. Static buffers and process-global state are not thread-safe, though workers are process-forked rather than threaded. Long expkey expiries can preserve stale mapping until explicit flush.

Test signals: validate both netlink and procfs modes, negative cache entries, IP-domain mapping with `use_ipaddr`, managed group expansion, fsid types 0-7, UUID fallback with/without blkid, crossmnt submount export, reexport fsidnum allocation/uncover, mountpoint-unavailable delayed retry, junction referral synthesis, proactive `cache_export()`, and worker forking/reaping behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/cache.c -->
