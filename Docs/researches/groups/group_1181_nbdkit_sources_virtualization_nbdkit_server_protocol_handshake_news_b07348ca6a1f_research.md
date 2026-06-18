# Group Research: group_1181_nbdkit_sources_virtualization_nbdkit_server_protocol_handshake_news_b07348ca6a1f

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nbdkit`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake-newstyle.c -->
# File Research: sources/virtualization/nbdkit/server/protocol-handshake-newstyle.c

This file implements the server side of NBD fixed-newstyle negotiation. It sends `NBD_MAGIC`, `NBD_NEW_VERSION`, and masked global flags, receives client flags, rejects unknown requested flags, then enters a bounded option-negotiation loop.

The option loop handles `NBD_OPT_EXPORT_NAME`, `NBD_OPT_ABORT`, `NBD_OPT_LIST`, `NBD_OPT_STARTTLS`, `NBD_OPT_INFO`, `NBD_OPT_GO`, `NBD_OPT_STRUCTURED_REPLY`, `NBD_OPT_LIST_META_CONTEXT`, and `NBD_OPT_SET_META_CONTEXT`. Unknown options are answered with `NBD_REP_ERR_UNSUP` after payload draining. Payload sizes are capped by `MAX_REQUEST_SIZE`, and negotiation is bounded by `MAX_NR_OPTIONS`, with extra option allowance after export listing.

TLS policy is enforced during negotiation. In forced TLS mode, only `NBD_OPT_ABORT` and `NBD_OPT_STARTTLS` are accepted before upgrade. `NBD_OPT_STARTTLS` sends its ACK before calling `crypto_negotiate_tls`, then marks the connection TLS-enabled and clears cached negotiation state such as structured replies, selected metadata context, export name from metadata context negotiation, and cached default export names.

Export finalization is centralized in `finish_newstyle_options`. It copies the wire export name into a NUL-terminated buffer, invalidates a previously selected metadata context if it was negotiated for a different export, calls `protocol_common_open`, and stores export flags in `conn->eflags`. `NBD_OPT_EXPORT_NAME` completes the handshake with the export size and flags. `NBD_OPT_GO` sends ACK and leaves the export open for the data phase. `NBD_OPT_INFO` opens temporarily, reports requested information, then finalizes and closes.

The INFO/GO path always replies with `NBD_INFO_EXPORT`, even if not requested, then conditionally sends `NBD_INFO_NAME`, `NBD_INFO_DESCRIPTION`, and `NBD_INFO_BLOCK_SIZE`. Export names and query strings are checked for maximum length, containment within payload, and embedded NUL bytes; UTF-8 validation is noted as a TODO.

Metadata-context support is intentionally limited to `base:allocation`. Listing can return it without requiring structured replies, while setting it requires structured replies. `SET_META_CONTEXT` records the export name, resets existing context state, and enables `conn->meta_context_base_allocation` only when `base:allocation` is selected. The data phase later uses `base_allocation_id`.

Important integration points are `protocol_common_open`, `backend_list_exports`, `backend_default_export`, `backend_export_description`, `backend_block_size`, `crypto_negotiate_tls`, thread-local last-error reporting for error replies, and connection fields later consumed by `protocol.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake-newstyle.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake-oldstyle.c -->
# File Research: sources/virtualization/nbdkit/server/protocol-handshake-oldstyle.c

This file implements the legacy NBD oldstyle handshake. Oldstyle has no option phase, so the server immediately opens the default export name `""` through `protocol_common_open`, computes export flags, and sends an `nbd_old_handshake` containing `NBD_MAGIC`, `NBD_OLD_VERSION`, export size, zero global flags, and export flags.

Because oldstyle cannot send structured negotiation errors, any backend open, prepare, size, or capability failure results in disconnect. The file asserts that forced TLS is not active, because oldstyle cannot negotiate TLS and that mode is filtered before this path.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake-oldstyle.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake.c -->
# File Research: sources/virtualization/nbdkit/server/protocol-handshake.c

This file chooses oldstyle versus newstyle negotiation under the global request lock. `protocol_handshake` calls `protocol_handshake_oldstyle` when `newstyle` is false, otherwise `protocol_handshake_newstyle`, then releases the lock.

It also provides `protocol_common_open`, shared by both handshake styles. This function opens the top backend for a chosen export, runs backend preparation, obtains export size, rejects negative sizes, and probes backend capabilities to build NBD export flags.

Advertised flags include readonly, write-zeroes, fast-zero, trim, FUA, flush, rotational, multi-conn, cache, and DF support. Multi-conn is advertised only when the backend supports it and the effective thread model permits more than serialized connections. Extents support is probed even though it is not directly advertised in the handshake, priming backend capability caches for later block-status validation and handling.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/protocol-handshake.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/protocol.c -->
# File Research: sources/virtualization/nbdkit/server/protocol.c

This file implements the post-handshake NBD request/reply data path. It reads request packets, validates command, flags, offset, count, and negotiated capability state, receives write payloads, invokes backend operations, and sends simple or structured replies.

`validate_request` rejects writes on readonly exports, out-of-range data requests, malformed flush offsets/counts, unknown commands, invalid flag combinations, unsupported advertised features, oversized read/write requests, missing structured replies for DF or block status, and missing `base:allocation` context for `NBD_CMD_BLOCK_STATUS`.

`handle_request` maps NBD commands to backend methods: `pread`, `pwrite`, `flush`, `trim`, `cache`, `zero`, and `extents`. It clears thread-local plugin errno and last-error state before backend calls, translates NBD flags into nbdkit flags such as FUA, MAY_TRIM, FAST_ZERO, and REQ_ONE, and returns errno-style failures for later NBD error conversion.

Reply handling supports simple replies for most operations. Structured replies are used for reads and block status when structured replies were negotiated. Structured read replies send one offset-data chunk. Block-status replies translate `nbdkit_extents` into 32-bit NBD block descriptors, truncate lengths to protocol limits while preserving alignment, and include the negotiated `base_allocation_id`.

Connection state controls loop behavior. EOF and `NBD_CMD_DISC` mark the client done, malformed request magic or socket errors mark the connection dead, and server shutdown maps to `ESHUTDOWN`. Invalid write requests still drain the write payload when possible so the stream remains synchronized before an error reply is sent.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/protocol.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/public.c -->
# File Research: sources/virtualization/nbdkit/server/public.c

This file contains public utility APIs exported to nbdkit plugins and filters. Path helpers include `nbdkit_absolute_path` and `nbdkit_realpath`, with Windows using realpath replacement behavior for absolute-path resolution. `nbdkit_stdio_safe` reports whether stdin can safely be used during configuration.

`nbdkit_nanosleep` validates duration overflow and, where `ppoll` plus `POLLRDHUP` are available, sleeps in a way that wakes early on server shutdown, connection shutdown, socket hangup/error, or invalid socket. The fallback uses ordinary `nanosleep`, with comments warning that shutdown responsiveness may be delayed.

Context helpers expose `nbdkit_export_name` and `nbdkit_is_tls`. They depend on the active thread-local backend context and connection; out-of-connection backend opens report TLS only when command-line TLS is required.

The file also manages interned strings through global or per-connection vectors. `nbdkit_strndup_intern`, `nbdkit_strdup_intern`, `nbdkit_vprintf_intern`, and `nbdkit_printf_intern` allocate strings whose ownership is tracked until connection or global cleanup.

`nbdkit_disconnect` lets a plugin or filter request graceful or forced connection shutdown, updating connection status and shutting down writes under the write lock. `nbdkit_name` returns the process name, and `nbdkit_timestamp` returns a UTC timestamp stored in thread-local storage when possible.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/public.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/quit.c -->
# File Research: sources/virtualization/nbdkit/server/quit.c

This file implements process shutdown signaling. It defines the global volatile `quit` flag plus a wakeup object used by polling loops: a pipe on POSIX and an Event on Windows.

On POSIX, `set_up_quit_pipe` creates a close-on-exec pipe, `close_quit_pipe` closes both ends, and `set_quit` is intentionally async-signal-safe: it sets `quit = 1` and writes one byte to the pipe. Comments explicitly warn against signal-handler-unsafe work and cite signal-safety concerns.

On Windows, the same abstraction is implemented with `CreateEvent`, `SetEvent`, and `CloseHandle`. `handle_quit` is the signal-handler entry point, and public `nbdkit_shutdown` triggers the same quit path for plugin/filter initiated shutdown.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/quit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/signals.c -->
# File Research: sources/virtualization/nbdkit/server/signals.c

This file installs process signal handlers. On POSIX it uses `sigaction` with `SA_RESTART` for `SIGINT`, `SIGQUIT`, `SIGTERM`, and `SIGHUP`, routing them to `handle_quit`. It also ignores `SIGPIPE` so socket write failures are handled as ordinary errors instead of terminating the process.

On Windows it installs `signal` handlers for `SIGINT` and `SIGTERM`. Shutdown state and wakeup mechanics are implemented in `quit.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/signals.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/socket-activation.c -->
# File Research: sources/virtualization/nbdkit/server/socket-activation.c

This file handles systemd-style socket activation. On POSIX, `get_socket_activation` checks `LISTEN_PID`, verifies it matches the current process, parses `LISTEN_FDS`, limits inherited descriptors to `1..16`, marks each descriptor close-on-exec, and records optional descriptor names from `LISTEN_FDNAMES`.

Names are colon-separated. Empty names and `"unknown"` are treated as absent. Invalid descriptors or allocation failures are fatal startup errors. After parsing, the socket activation environment variables are unset so child processes do not inherit them.

Windows has a no-op implementation. `free_socket_activation` frees copied descriptor names and resets the socket activation vector.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/socket-activation.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/sockets.c -->
# File Research: sources/virtualization/nbdkit/server/sockets.c

This file creates listening sockets and runs the accept loop. It supports Unix sockets, TCP/IP sockets, vsock sockets, optional SELinux socket creation labels, close-on-exec setup, and cleanup of listener file descriptors during shutdown.

Unix socket binding validates path length and listens with `SOMAXCONN`. TCP/IP binding uses `getaddrinfo`, defaults to port `10809`, sets `SO_REUSEADDR`, enforces IPv6-only sockets when available, tolerates unavailable IPv6 families or address-in-use candidates when alternatives remain, and updates the global port string when `--port=0` lets the kernel choose a port. Vsock binding parses a numeric port and binds `VMADDR_CID_ANY`.

Accepted connections are handled by detached pthreads. Each thread gets thread-local server state and an instance number before calling `handle_single_connection`. A global mutex/condition counter tracks live connection threads so shutdown waits for all of them before returning to unload-time cleanup.

The POSIX accept loop polls all listening sockets plus `quit_fd`; the Windows path uses `WaitForMultipleObjectsEx`. A readable quit object exits the loop without accepting more connections. Accepted sockets opportunistically get `TCP_NODELAY`, and `SO_KEEPALIVE` is enabled when requested.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/sockets.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/test-public.c -->
# File Research: sources/virtualization/nbdkit/server/test-public.c

This standalone unit test file provides minimal stubs for server globals and functions, then tests selected public parsing and password APIs. `nbdkit_error` only records that an error was reported, allowing tests to verify both return values and diagnostic behavior.

Covered tests include `nbdkit_parse_size` using shared human-size cases, `nbdkit_parse_probability` with invalid strings, infinities/NaNs, plain numbers, percentages, and `N:M` or `N/M` ratios, and `nbdkit_parse_delay` with seconds, milliseconds, microseconds including `us` and `μs`, and nanoseconds.

Integer parsing tests cover signed and unsigned variants from native `int` through 8/16/32/64-bit fixed-width types. They validate decimal, hexadecimal, octal, signs, boundary values, overflow, malformed tokens, trailing garbage, floats, commas, and rejection of negative values for unsigned parsers.

Password tests cover failure on missing files, direct password strings, `+FILE` password file reads, and non-Windows `-FD` descriptor reads. The test notes that stdin password reading is not covered because it would require a pty. `main` runs all test groups and returns success only if all pass.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/test-public.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/threadlocal.c -->
# File Research: sources/virtualization/nbdkit/server/threadlocal.c

This file implements nbdkit thread-local storage. Stored data includes an optional thread name, connection instance number, plugin errno value, last server error string, timestamp string, reusable I/O buffer, current connection, and current backend context.

`threadlocal_init` creates the pthread key with a destructor that frees all owned fields. `threadlocal_new_server_thread` allocates and installs an empty record for connection threads. Name and instance-number setters are best-effort diagnostic metadata.

Thread-local errno and last-error tracking influence protocol behavior. Request handling clears these before backend calls, plugins can set errors, and negotiation error replies can include the last error string when it fits protocol limits. `threadlocal_get_errno` preserves process `errno` while reading stored plugin errno.

`threadlocal_buffer` provides one reusable per-thread request buffer, growing it with `realloc` and zeroing the new allocation. Comments note that old plugin data may remain after use, but this avoids leaking unrelated heap data from the core server.

The file also tracks the active connection and backend context. Getters validate magic values where safe. Context push/pop supports scoped context switching via `PUSH_CONTEXT_FOR_SCOPE`, including a comment explaining why a saved previous context is not revalidated because it may be a freed pointer restored only for stack unwinding.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/threadlocal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/timeout.c -->
# File Research: sources/virtualization/nbdkit/server/timeout.c

This file implements optional per-connection timeouts when `HAVE_TIMEOUT_OPTION` is available. `start_timeout` creates a one-shot `CLOCK_MONOTONIC` POSIX timer using `SIGEV_THREAD`, passes the connection pointer to the callback, and arms it from global timeout seconds/nanoseconds.

The timeout callback takes the connection lock, verifies connection magic, timer state, active status, and valid socket, then calls `shutdown(conn->sockout, SHUT_RDWR)` and marks the connection dead. Comments emphasize that the callback runs asynchronously from another thread and intentionally does minimal work; `shutdown` is preferred over `close` to avoid fd reuse hazards.

`cancel_timeout` deletes an active timer and clears `timer_set`. When timeout support is not compiled in, start and cancel functions are no-ops.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/uri.c -->
# File Research: sources/virtualization/nbdkit/server/uri.c

This file builds the debug/display NBD URI for the current service mode. Socket activation and stdin modes cannot be represented and return `NULL`. TCP, Unix socket, and vsock modes choose `nbd`, `nbds`, `nbd+unix`, `nbds+unix`, `nbd+vsock`, or `nbds+vsock` depending on whether TLS is required.

The URI is assembled with `open_memstream` and `uri_quote`. Unix socket mode encodes the socket path as `?socket=...` and puts a non-empty export name in the path. TCP mode uses `localhost` plus optional port and export name. Vsock mode uses CID `1` (`VMADDR_CID_LOCAL`) plus optional port and export name.

When TLS is required and certificate or PSK configuration is present, it appends `tls-certificates=` or `tls-psk-file=` query parameters. Comments note client compatibility caveats, including older libnbd and qemu behavior. The result is logged through debug output.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/uri.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/usergroup.c -->
# File Research: sources/virtualization/nbdkit/server/usergroup.c

This file implements `--user` and `--group` privilege dropping on platforms with password and group databases. `change_user` applies group first, then user. For groups it parses the configured group, calls `setgid`, then resets supplemental groups to just that gid with `setgroups`. For users it parses the configured user and calls `setuid`.

`parseuser` tries `getpwnam` first, then falls back to numeric parsing through `nbdkit_parse_int`. `parsegroup` mirrors this with `getgrnam`. On failure each prints a command-line specific diagnostic, includes saved lookup errno when available, and exits.

On platforms without `pwd.h` and `grp.h`, `change_user` is a no-op when neither option is set, otherwise reports that `--user/--group` are not implemented on Windows.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/usergroup.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/vfprintf.c -->
# File Research: sources/virtualization/nbdkit/server/vfprintf.c

This portability file provides `replace_vfprintf` when the platform `vfprintf` lacks `%m` support. It finds the first `%m` in the format string, replaces it with `strerror(errno)` using `asprintf`, calls the real `vfprintf`, frees the replacement buffer, and returns the result.

The implementation handles only the first `%m`, explicitly documenting that multiple occurrences may produce broken output. It is compiled only when `HAVE_VFPRINTF_PERCENT_M` is false, mainly for BSD-like portability.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/vfprintf.c -->