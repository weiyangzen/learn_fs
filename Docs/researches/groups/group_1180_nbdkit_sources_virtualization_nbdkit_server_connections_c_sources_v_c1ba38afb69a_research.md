# Group Research: group_1180_nbdkit_sources_virtualization_nbdkit_server_connections_c_sources_v_c1ba38afb69a

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/nbdkit` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/connections.c -->
# File Research: sources/virtualization/nbdkit/server/connections.c

Purpose: Implements per-client connection lifetime, request processing, worker-thread dispatch, connection status transitions, and raw transport I/O for the nbdkit server.

Key structures and state:
- Allocates and owns `struct connection`, declared in `internal.h`.
- Initializes per-connection mutexes: `request_lock`, `read_lock`, `write_lock`, `status_lock`.
- Tracks connection state through `conn_status`: `STATUS_ACTIVE`, `STATUS_SHUTDOWN`, `STATUS_CLIENT_DONE`, `STATUS_DEAD`.
- Creates `default_exportname` storage indexed by backend chain position.
- Optional `status_pipe` lets worker threads wake poll loops when status drops.

Main flow:
- `handle_single_connection(sockin, sockout)` locks connection admission according to the thread model, allocates a connection, runs `top->preconnect`, starts the handshake timeout, performs `protocol_handshake`, then serves requests.
- If the effective thread model is not parallel or only one worker is requested, request processing runs serially in the connection thread.
- Otherwise a worker pool handles `protocol_recv_request_send_reply()` until global quit or connection status reaches client-done/dead.
- On request-processing failure, workers acquire `write_lock` and call `conn->close(SHUT_WR)` to stop writes.
- Before freeing, it calls `backend_finalize(conn->top_context)` under `lock_request`.

Concurrency details:
- `connection_get_status` and `connection_set_status` lock `status_lock` only when workers exist.
- `connection_set_status` only moves status toward lower-severity enum values, and returns true when the caller should initiate shutdown.
- Worker thread names are derived from plugin name plus worker index, and thread-local connection/name state is set per worker.

I/O behavior:
- `raw_recv` reads exactly the requested length, returning `1` for complete read, `0` for EOF before any bytes, and `-1` for errors or partial-record EOF.
- `raw_send_socket` uses `send`, optionally with `MSG_MORE` when `SEND_MORE` is requested.
- `raw_send_other` uses `write` for non-socket outputs on Unix, supporting stdin/stdout-style operation and fuzzing.
- `raw_close` handles half-close versus full close, with separate sockin/sockout support.

Dependencies:
- Calls protocol entry points from handshake and request processing modules.
- Calls backend lifecycle functions and lock helpers from `backend.c`/`locks.c`.
- Uses thread-local APIs for current connection and server thread identity.
- Uses platform socket wrappers from `windows-compat.h`.

Important edge cases:
- If `top` is already null during async shutdown, a new connection returns immediately.
- If atomic `pipe2` is unavailable, pipe setup is serialized under `lock_request` and constrained by thread model.
- `free_connection` avoids calling plugin close paths after global quit, because unload may already be in progress.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/connections.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/crypto.c -->
# File Research: sources/virtualization/nbdkit/server/crypto.c

Purpose: Implements TLS initialization, certificate/PSK credential loading, connection upgrade to GnuTLS, TLS-wrapped transport I/O, TLS debug reporting, and public peer-certificate DN helpers.

Build modes:
- With `HAVE_GNUTLS`, full TLS support is compiled.
- Without GnuTLS, `crypto_init` rejects enabled TLS and public TLS peer-DN helpers report unsupported-platform errors.

Credential loading:
- X.509 mode looks for `ca-cert.pem`, optional `ca-crl.pem`, and server key/cert pairs in configured/default certificate directories.
- It supports the primary `server-cert.pem`/`server-key.pem` plus numbered `server-cert-N.pem`/`server-key-N.pem` pairs.
- Default certificate search depends on privilege: non-root checks user pki/config paths; root checks `root_tls_certificates_dir`.
- `--tls-psk` selects PSK credentials instead of certificates and resolves the PSK file to an absolute path.

Initialization:
- `crypto_init(tls_set_on_cli)` calls `gnutls_global_init`, chooses PSK or X.509 auth, and enforces `--tls=require`.
- If TLS was explicitly requested as `on` but credentials cannot load, it warns and disables TLS.
- `crypto_free` releases active credential objects and calls `gnutls_global_deinit`.

Connection upgrade:
- `crypto_negotiate_tls(sockin, sockout)` creates a server session, attaches credentials, configures priority, sets transports, runs the handshake, logs session details when enabled, then swaps `conn->recv`, `conn->send`, and `conn->close` to TLS implementations.
- Certificate mode can request/verify client certs when `tls_verify_peer` is set.
- PSK mode extends the priority string with PSK key-exchange algorithms.

TLS I/O:
- `crypto_recv` mirrors raw receive semantics: complete read, clean EOF before bytes, or error/partial-record failure.
- `crypto_send` uses GnuTLS corking/uncorking to honor `SEND_MORE`, with a 64 KiB threshold to avoid excessive corked data.
- `crypto_close` uses `gnutls_bye`, closes underlying sockets on full close, deinitializes the session, and clears `conn->crypto_session`.

Debug and inspection:
- `nbdkit_debug_tls_log` routes GnuTLS logs through nbdkit debug output.
- `nbdkit_debug_tls_session` enables negotiated-session summaries, auth type, peer certificates, group/curve/DH details, and kTLS status where supported.
- `nbdkit_peer_tls_dn` and `nbdkit_peer_tls_issuer_dn` return client certificate subject/issuer DN strings, or an allocated empty string when there is no applicable DN.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/debug-flags.c -->
# File Research: sources/virtualization/nbdkit/server/debug-flags.c

Purpose: Parses and applies `-D NAME.FLAG=N` debug flags for the server, plugins, and filters.

Core behavior:
- Stores flags in a linked list of `struct debug_flag`.
- `add_debug_flag` validates the required `NAME.FLAG=N` shape.
- `nbdkit_parse_int` parses the assigned integer value.
- `symbol_of_debug_flag` synthesizes a global variable name as `NAME_debug_FLAG`, replacing dots with underscores.

Application:
- `apply_debug_flags(dl, name)` scans pending flags matching the backend/server name.
- It resolves each synthesized symbol with `dlsym`.
- When present, it writes the requested integer value into that symbol.
- Missing symbols produce warnings, but the flag is still marked used for that name.

Cleanup:
- `free_debug_flags` emits warnings for flags never applied to any backend/server.
- It frees name, flag, symbol, and list nodes.

Dependencies:
- Uses `dlfcn.h`, `strndup`, and parsing helpers from the public nbdkit API.
- The global `debug_flags` head is declared in `main.c`/`internal.h`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/debug-flags.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/debug.c -->
# File Research: sources/virtualization/nbdkit/server/debug.c

Purpose: Implements verbose debug output and exported hexdump/hexdiff debug helpers.

Logging behavior:
- Debug output is disabled unless `verbose` is true.
- `debug_common` preserves the incoming `errno` across formatting and output.
- Messages are first formatted into an inner string, then C-string-escaped into an outer string with a standard prologue.
- The prologue includes `program_name`, optional `process_name`, thread-local name, optional instance number, and `debug:`.
- Non-server public debug calls use terminal coloring when stderr is a tty.

Public/internal entry points:
- `nbdkit_vdebug` and `nbdkit_debug` are exported for plugins/filters.
- `debug_in_server` is the server-internal implementation behind the `debug()` macro.
- `internal.h` deliberately prevents direct server use of `nbdkit_debug`.

Hex helpers:
- `nbdkit_debug_hexdump` formats 16-byte rows with offset, two hex groups, and printable ASCII.
- `nbdkit_debug_hexdiff` emits old/new rows only where bytes differ, marking rows with `-`, `+`, or space.
- Both handle unaligned starting offsets and preserve row offsets.

Dependencies:
- Uses `open_memstream`, ASCII classification, alignment and rounding helpers, and thread-local naming APIs.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/exports.c -->
# File Research: sources/virtualization/nbdkit/server/exports.c

Purpose: Implements the public `struct nbdkit_exports` list used by plugins and filters to enumerate available NBD exports.

Data model:
- Wraps a vector of `struct nbdkit_export`.
- Tracks `use_default`, a sentinel asking the server to insert the backend default export later.
- Caps the list at `MAX_EXPORTS` = 10000 to limit memory and protocol reply size.

Public API:
- `nbdkit_exports_new` allocates an empty export list.
- `nbdkit_exports_free` frees each export name/description and the vector.
- `nbdkit_exports_count` returns vector length.
- `nbdkit_get_export` returns an export by index, with an assert on bounds.
- `nbdkit_add_export` duplicates the name and optional description after enforcing `NBD_MAX_STRING` limits.
- `nbdkit_use_default_export` sets the sentinel.

Server integration:
- `exports_resolve_default(exps, b, readonly)` resolves `use_default` through `backend_default_export`, clears the sentinel, and appends the resulting export.

Error behavior:
- Allocation and length failures call `nbdkit_error` and set useful `errno` values.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/exports.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/extents.c -->
# File Research: sources/virtualization/nbdkit/server/extents.c

Purpose: Implements public extent-list management and filter helpers for NBD block status/extents.

Data model:
- `struct nbdkit_extents` wraps a vector of `struct nbdkit_extent`.
- Tracks requested `[start, end)` range and `next`, the expected offset for the next appended extent.
- Caps stored extents at `MAX_EXTENTS` = 1 Mi entries.

Public API:
- `nbdkit_extents_new(start, end)` validates `start <= end` and both values within `INT64_MAX`.
- `nbdkit_extents_free`, `nbdkit_extents_count`, and `nbdkit_get_extent` expose lifecycle and access.
- `nbdkit_add_extent` enforces strictly contiguous ascending additions, ignores zero-length entries, truncates to requested range, rejects gaps after `start`, and coalesces adjacent extents with identical type.

Filter helpers:
- `nbdkit_extents_aligned` asks the next backend for a larger aligned range, coalesces or truncates unaligned leading extents, and trims the final result back to the caller’s original offset.
- It intersects type bits when merging, using bitwise AND as the safe representation for mixed regions.
- `nbdkit_extents_full` repeatedly calls `next->extents` with `REQ_ONE` cleared until it covers the whole requested region.

Safety and assumptions:
- Plugin misbehavior is caught with API errors or asserts for no forward progress.
- `nbdkit_extents_full` rejects excessive extent counts with `ENOMEM`.
- These helpers depend on backend `get_size` and `extents` next-ops from the filter chain.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/filters.c -->
# File Research: sources/virtualization/nbdkit/server/filters.c

Purpose: Adapts a loaded `struct nbdkit_filter` into the internal `struct backend` vtable and handles filter chaining.

Structure:
- `struct backend_filter` embeds `struct backend` plus a copied `struct nbdkit_filter`.
- `filter_register` initializes the backend, calls `filter_init`, checks filter API/version compatibility against the current nbdkit build, copies the filter struct, and runs backend load.

Chain behavior:
- Most callbacks either call the filter callback with a next-function/context or pass straight through to `b->next`.
- `filter_free` frees the entire underlying chain, unloads the filter, and frees its wrapper.
- `plugin_name` and `plugin_magic_config_key` intentionally pass through to the final plugin.

Lifecycle callbacks:
- Handles usage/version/dump fields, config/config_complete, get_ready, after_fork, cleanup, preconnect, list_exports, default_export, open, prepare, finalize, close.
- `next_open` opens the next backend context and stores it in the current filter context.
- `filter_open` supports filters that explicitly call `next_open`, or default-open the next layer when no `.open` is supplied.

Data path:
- Capability and operation callbacks cover export description, size, block size, write/flush/trim/zero/extents/FUA/multi-conn/cache support, and pread/pwrite/flush/trim/zero/extents/cache.
- Missing filter callbacks transparently delegate to the next backend.
- Errors propagate through the internal backend convention using `int *err` on data operations.

Public helper exports:
- `nbdkit_context_get_backend`
- `nbdkit_next_context_open`
- `nbdkit_next_context_close`
- `nbdkit_context_set_next`

Important constraint:
- Filters have strict ABI/API coupling to the exact current nbdkit version via `_api_version` and `_version`; unlike plugins, they are not treated as long-term ABI-stable.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/filters.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/fuzzer.c -->
# File Research: sources/virtualization/nbdkit/server/fuzzer.c

Purpose: Provides a libFuzzer harness for the nbdkit server, compiled only when `ENABLE_LIBFUZZER` is enabled.

Entry point:
- `LLVMFuzzerTestOneInput(data, size)` creates a Unix socketpair and forks.
- Parent runs the nbdkit server side.
- Child acts as a synthetic NBD client feeding fuzz input.

Server side:
- Calls the renamed normal `main` function, `fuzzer_main`.
- Runs nbdkit with `-s`, `--log=null`, and the in-tree memory plugin with a `1M` size.
- Temporarily dup2s the socket over stdin/stdout so the normal `-s` path processes the fuzzed connection.
- Restores original stdin/stdout after `fuzzer_main`.

Client side:
- Polls the socket for read/write readiness.
- Writes remaining fuzz data when possible.
- Reads and discards server output.
- Shuts down the write side once all fuzz data is sent.

Error handling:
- Parent waits for the child and prints a diagnostic for nonzero/bad exit status.
- Many client read/write failures are treated as normal fuzzing termination rather than harness failure.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/fuzzer.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/internal.h -->
# File Research: sources/virtualization/nbdkit/server/internal.h

Purpose: Central private server header tying together global configuration, connection/context state, backend vtables, server helpers, and cross-module declarations.

Global state:
- Declares command-line/server globals such as `foreground`, `read_only`, `tls`, `tls_psk`, `unixsocket`, `threads`, `timeout`, `verbose`, `service_mode`, `configured`, and `top`.
- Defines `enum log_to` and `enum service_mode`.
- Exposes `service_mode_string`.

Core constants/macros:
- `MAX_API_VERSION` and `NBDKIT_API_VERSION`.
- `MAX_REQUEST_SIZE` = 64 MiB.
- `DO_DLCLOSE` policy varies under ASan, fuzzing, and Valgrind.
- DTrace probe macros become no-ops when probes are disabled.
- `debug()` macro routes server debug through `debug_in_server`.
- `GET_CONN` pulls the current connection from thread-local storage and asserts non-null.

Connection/context model:
- `struct context` stores per-backend/per-connection handle state, export name, cached size/capabilities, next context, and lifecycle state bits.
- `struct connection` stores locks, status, TLS session, worker count, top context, default export names, protocol flags, interned strings, sockets, and transport function pointers.
- Connection transport is abstracted through recv/send/close function pointers, allowing TLS replacement.

Backend model:
- `struct backend` is the internal vtable implemented by plugins and filters.
- It includes lifecycle, configuration, export discovery, open/prepare/finalize/close, capability, and data-operation callbacks.
- Backend chain is linked by `next`; plugin is last with index 0, filters have higher indices.

Declared modules:
- Connection handling, protocol handshake/request processing, crypto, debug flags, logging, backend operations, plugin/filter registration, locks, sockets, thread-local state, exports, timeout, signals, backgrounding, user/group changes, URI generation, and socket activation.

Design role:
- This header defines the internal ABI between server modules, while public plugin/filter ABI comes from `nbdkit-plugin.h` and `nbdkit-filter.h`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/local/nbdkit.pc.in -->
# File Research: sources/virtualization/nbdkit/server/local/nbdkit.pc.in

Purpose: Template for a local-build `pkg-config` file used to compile plugins against an uninstalled nbdkit build tree.

Fields:
- `prefix` and `exec_prefix` point at `@abs_top_builddir@`.
- `Name`, `Version`, and `Description` describe nbdkit.
- `Requires` is empty.
- `Cflags` includes both source and build include directories.
- `Libs` is empty.

Design implication:
- Plugins compiled locally include headers from the source/build tree but do not link against a separate nbdkit library; symbols are provided by the server process at load time.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/local/nbdkit.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/locks.c -->
# File Research: sources/virtualization/nbdkit/server/locks.c

Purpose: Implements locking policy derived from nbdkit’s selected plugin/filter thread model.

State:
- Global `thread_model` caches `top->thread_model(top)` after configuration.
- `connection_lock` serializes whole connections for `serialize_connections`.
- `all_requests_lock` serializes all requests for `serialize_all_requests`.
- `unload_prevention_lock` is an rwlock that prevents backend unload while requests are active.

Public helpers:
- `name_of_thread_model` converts thread-model constants to strings.
- `lock_init_thread_model` selects and logs the effective model.
- `lock_connection`/`unlock_connection` enforce connection serialization when required.
- `lock_request`/`unlock_request` enforce all-request or per-connection request serialization and hold an unload-prevention read lock.
- `lock_unload`/`unlock_unload` take the unload-prevention write lock.

Lock ordering:
- Request locking first applies global serialization, then per-connection serialization, then unload prevention.
- Unlocking releases in reverse for unload, per-connection, and global locks.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/log-fp.c -->
# File Research: sources/virtualization/nbdkit/server/log-fp.c

Purpose: Emits formatted nbdkit error messages to a `FILE *` target such as stderr or a configured log file.

Behavior:
- `log_fp_verror(fp, orig_errno, fs, args)` optionally locks the stream with `flockfile`.
- Applies red terminal color when the destination is a tty.
- Prefixes messages with program name, optional process name, optional thread-local name and instance number, then `error:`.
- Restores `errno = orig_errno` before `vfprintf` so `%m` expands correctly.
- Appends newline, restores terminal color, flushes the stream, and unlocks where supported.

Dependencies:
- Uses thread-local identity helpers and global `process_name`.
- Used by `log.c` according to the selected log sink.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/log-fp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/log-syslog.c -->
# File Research: sources/virtualization/nbdkit/server/log-syslog.c

Purpose: Emits formatted nbdkit error messages to syslog.

Behavior:
- Uses priority `LOG_DAEMON | LOG_ERR`.
- Formats into an allocated memory stream so thread-local name/instance can be prepended.
- Restores `errno = orig_errno` before formatting for correct `%m` expansion.
- On `open_memstream` failure, falls back to `vsyslog` with the original format and arguments.
- Sends the completed message with `syslog`.

Dependencies:
- Used by `log.c` for explicit syslog logging and default logging after background fork.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/log-syslog.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/log.c -->
# File Research: sources/virtualization/nbdkit/server/log.c

Purpose: Central error logging dispatcher and public `nbdkit_error` implementation.

Core behavior:
- `log_verror` preserves incoming `errno`.
- It copies the formatted error message into thread-local storage for structured replies when possible.
- Dispatches to stderr, syslog, configured file, or null logging based on `log_to`.
- Default logging goes to syslog if the server has forked into the background, otherwise stderr.
- Restores `errno` before returning.

Public API:
- `nbdkit_verror(fs, args)` forwards to `log_verror`.
- `nbdkit_error(fs, ...)` is the variadic public entry point for plugins, filters, and server support code.

Important detail:
- Failure to copy the message to thread-local storage is intentionally non-fatal; it is supplementary client-facing information.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/main.c -->
# File Research: sources/virtualization/nbdkit/server/main.c

Purpose: Main server entry point. Parses CLI options, initializes process-wide state, loads plugins/filters, configures backends, selects serving mode, and drives shutdown cleanup.

Global configuration:
- Defines the command-line globals declared in `internal.h`, including TLS settings, logging mode, service mode, socket/run/stdin state, thread count, timeout, read-only mode, and backend chain `top`.
- Maintains temporary random Unix socket path state for `-U -` and implied `--run`.

Startup flow:
- Verifies stdio is open, initializes Winsock on Windows, and initializes thread-local state.
- Defaults TLS to on when compiled with GnuTLS, off otherwise.
- Reads socket activation state before option parsing.
- Parses all short and long options from `options.h`.
- Validates incompatible mode combinations such as `-s` with `--run`, oldstyle with `--tls=require`, and socket activation with explicit socket options.
- Opens logging, initializes TLS, optionally configures exit-with-parent, computes service mode and URI.

Plugin/filter loading:
- First non-option argument is the plugin.
- Short plugin/filter names are resolved to `plugindir/nbdkit-<name>-plugin.<soext>` or `filterdir/nbdkit-<name>-filter.<soext>`.
- Executable script plugins in `plugindir` are exec’d directly.
- `open_plugin_so` uses `dlopen`, resolves `plugin_init`, and calls `plugin_register`.
- `open_filter_so` resolves `filter_init` and wraps the current chain with `filter_register`.
- Filters are applied in reverse collected order so command-line order matches request-processing order.

Configuration:
- Parses remaining arguments as `[key=]value` or `@PATH`.
- Bare values use the backend magic config key, or legacy first-argument `script` behavior when no magic key exists.
- `@PATH` files are read line by line, ignoring blank/comment lines, and nested relative `@PATH` entries resolve relative to the including file.
- Configuration keys are interned because plugin config receives pointers that must live for process lifetime.

Mode handling:
- `--help`, `--version`, and `--dump-plugin` load backends as needed, emit information, then clean up and exit.
- `--print-uri` emits URI information before stdio is sanitized.
- `switch_stdio` saves stdin/stdout for `-s`/`--run`, then redirects stdin/stdout to `/dev/null`.

Serving:
- `start_serving` sets up quit handling and signals, optionally locks memory for `--swap`, then serves through one of:
  - socket activation
  - stdin/stdout single connection
  - Unix socket
  - AF_VSOCK
  - TCP/IP
- Common socket modes may run a captive command, change user/group, fork into background, write pidfile, call `after_fork`, then accept incoming connections.
- Stdin mode directly calls `handle_single_connection(saved_stdin, saved_stdout)`.

Cleanup:
- Runs backend cleanup and free, releases sockets/URI/pidfile/random FIFO/TLS/quit pipe/socket activation/interned strings.
- Returns instead of exiting to support libFuzzer builds.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/main.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/nbdkit.pc.in -->
# File Research: sources/virtualization/nbdkit/server/nbdkit.pc.in

Purpose: Installed `pkg-config` template for compiling nbdkit plugins.

Fields:
- Defines install-time `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Exposes `plugindir` and `filterdir` under `@libdir@/nbdkit`.
- Provides package name, version, and description.
- Leaves `Requires`, `Cflags`, and `Libs` effectively empty.

Important note:
- The file explicitly documents that plugins do not link against a separate nbdkit library; symbols such as `nbdkit_error` are supplied by the main server binary when plugins are loaded.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/nbdkit.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/options.h -->
# File Research: sources/virtualization/nbdkit/server/options.h

Purpose: Defines CLI option constants, getopt tables, and helper logic for distinguishing short plugin/filter names.

Option definitions:
- Enum values beyond `CHAR_MAX` represent long-only options such as `--dump-config`, `--dump-plugin`, `--filter`, `--log`, `--tls-*`, `--vsock`, and others.
- `short_options` is `46D:e:fg:i:nop:P:rst:u:U:vV`.
- `long_options` maps aliases such as `--read-only`/`--readonly`, `--unix`, `--stdin`, `--new-style`, `--old-style`, `--print-uri`, and TLS options to getopt codes.

Helper:
- `is_short_name(filename)` returns true only for simple plugin/filter names without path separators, spaces, dots, commas, equals, path-list separators, or control characters.
- It also rejects strings containing `DIR_SEPARATOR_STR`.

Role in server:
- Included by `main.c` to drive `getopt_long` parsing and resolve plugin/filter short names to install directories.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/options.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/parsing.c -->
# File Research: sources/virtualization/nbdkit/server/parsing.c

Purpose: Implements exported parsing helpers used by plugins, filters, and server code.

Integer parsing:
- Provides signed parsers for `int`, `int8_t`, `int16_t`, `int32_t`, and `int64_t`.
- Provides unsigned parsers for `unsigned`, `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- Signed parsers use `strtol`/`strtoll` with range checks.
- Unsigned parsers reject leading negative signs before calling `strtoul`/`strtoull`.
- Common tail logic rejects empty input, trailing garbage, and range/parse errors, then optionally stores the result.

Other parsers:
- `nbdkit_parse_size` delegates to `human_size_parse`.
- `nbdkit_parse_probability` accepts `N:M`, `N/M`, decimal probabilities, or percentages; rejects NaN, infinity, and negative values.
- `nbdkit_parse_bool` delegates to `parse_bool` and reports user-friendly errors.
- `nbdkit_parse_delay` accepts seconds, milliseconds, microseconds (`us` or `μs`), and nanoseconds, returning seconds plus nanoseconds.

Compatibility:
- Suppresses GCC 12+ `-Wnonnull-compare` noise because older plugins may still pass null despite newer nonnull declarations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/parsing.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/password.c -->
# File Research: sources/virtualization/nbdkit/server/password.c

Purpose: Implements exported password-reading helper `nbdkit_read_password`.

Accepted forms:
- `"-"` reads interactively from a tty using `readpassphrase`.
- `"-FD"` reads from an already-open numeric file descriptor, excluding stdin/stdout/stderr.
- `"+PATH"` opens and reads a password from a file.
- Any other value is treated as the literal password.

Interactive behavior:
- Refuses interactive reads when `nbdkit_stdio_safe()` is false, such as after config phase or with stdin serving.
- Requires a tty via `RPP_REQUIRE_TTY`.
- Copies the password to heap memory and clears the stack buffer with `explicit_bzero` when available.

File descriptor/file behavior:
- `read_password_from_fd` wraps the fd with `fdopen`, reads one line with `getline`, closes the stream, and strips a trailing newline.
- EOF without data becomes an empty password.
- The helper owns and closes the fd it reads from.

Platform behavior:
- Reading from numeric file descriptors is disabled on Windows.
- Errors are reported with `nbdkit_error`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/password.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/peer.c -->
# File Research: sources/virtualization/nbdkit/server/peer.c

Purpose: Provides exported helpers for plugins/filters to inspect client peer address, credentials, and security context.

Peer address:
- `nbdkit_peer_name(addr, addrlen)` uses the current thread-local connection and calls `getpeername` on `conn->sockin`.
- Reports errors when no connection is associated with the thread or the socket is closed.

Peer credentials:
- `nbdkit_peer_pid`, `nbdkit_peer_uid`, and `nbdkit_peer_gid` call a shared helper that initializes requested outputs to `-1`.
- Linux/OpenBSD-style `SO_PEERCRED` support reads `struct ucred` or `struct sockpeercred`.
- FreeBSD-style `LOCAL_PEERCRED` support reads `struct xucred`; PID is reported unsupported there.
- Unsupported platforms return an error explaining that peer credential APIs are unavailable.
- Range checks protect conversion to `int64_t`.

Security context:
- With `SO_PEERSEC`, `nbdkit_peer_security_context` queries the label length, allocates a NUL-padded buffer, then reads the label.
- `ENOPROTOOPT` is treated as a non-error absence of security context and logged only as debug.
- Without `SO_PEERSEC`, it reports unsupported platform.
- Returned strings are heap allocated for caller ownership.

Compatibility:
- Like other public helpers, suppresses GCC 12+ nonnull-compare warnings to preserve runtime checks for older plugins.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/peer.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/plugins.c -->
# File Research: sources/virtualization/nbdkit/server/plugins.c

Purpose: Adapts a loaded `struct nbdkit_plugin` into the internal backend vtable, including capability normalization, old API compatibility, error capture, and operation emulation.

Structure:
- `struct backend_plugin` embeds `struct backend` plus a copied `struct nbdkit_plugin`.
- `plugin_register` initializes the backend, calls `plugin_init`, validates API version and required callbacks, copies only the plugin-declared struct size for ABI compatibility, then runs backend load.

Required callbacks:
- `.open`
- `.get_size`
- `.pread` or legacy `._pread_v1`

Lifecycle/config:
- Implements plugin free, thread model selection, name, usage, version, dump fields, config, config_complete, magic config key, get_ready, after_fork, cleanup, preconnect, list_exports, default_export, open/prepare/finalize/close.
- Plugins do not receive internal prepare/finalize callbacks; those are no-ops because plugin `.open`/`.close` can cover the same need.

Thread model:
- Starts from plugin `_thread_model`.
- If the platform lacks atomic CLOEXEC primitives, downgrades overly parallel models to `serialize_all_requests` to avoid fd leaks.
- Plugin-provided `thread_model` can further restrict concurrency.

Capabilities:
- Boolean-style plugin callbacks are normalized to `0`, `1`, or `-1`.
- Defaults infer write/flush/trim/zero/extents/cache support from presence of operation callbacks.
- `can_zero` maps public boolean semantics to internal native/emulate states.
- `can_fua` respects API version: API v1 cannot receive native FUA even if it reports it.
- `can_fast_zero` advertises fast failure where native zero support is absent.

Error handling:
- `nbdkit_set_error(err)` stores plugin-provided errno in thread-local state.
- `get_errno` uses thread-local error, preserved `errno` when the plugin opts in, or `EIO` fallback.

Data operations:
- `plugin_pread`, `plugin_pwrite`, `plugin_flush`, `plugin_trim`, `plugin_zero`, `plugin_extents`, and `plugin_cache` translate internal backend calls to plugin callbacks.
- FUA is emulated with a follow-up flush when native FUA is unavailable.
- Zero requests prefer native `.zero`; on unsupported non-fast zero, they emulate by writing static zero buffers through `plugin_pwrite`.
- Fast zero returns `EOPNOTSUPP` when unsupported rather than falling back to slow writes.
- `plugin_extents` rejects successful callbacks that return no extents.
- `plugin_cache` treats advertised cache without `.cache` as a no-op.

Dump support:
- `plugin_dump_fields` prints path, name, version, API version, struct size, max/effective thread model, errno behavior, magic key, presence bits for callbacks, and custom plugin dump output.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/plugins.c -->