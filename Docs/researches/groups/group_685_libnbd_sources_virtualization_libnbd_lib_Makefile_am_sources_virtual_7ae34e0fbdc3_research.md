# Group Research: group_685_libnbd_sources_virtualization_libnbd_lib_Makefile_am_sources_virtual_7ae34e0fbdc3

Scope validated against `Docs/research_subset_a.md`: `sources/virtualization/libnbd` is included in subset A. All 25 listed files were read completely, totaling 7,918 lines.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/Makefile.am -->
# File Research: sources/virtualization/libnbd/lib/Makefile.am

Build recipe for the core libnbd library. It declares generated sources (`api.c`, `states.c`, `states-run.c`, `states.h`, `unlocked.h`), hand-written library sources, pkg-config output, and two fork-safety unit tests.

Key points:
- Builds `libnbd.la` from connection, TLS, debug, error, flag, handle, option, polling, protocol, read/write, socket, URI, utility, and generated state-machine files.
- Adds includes from public headers and common utility directories.
- Links against common utils, pthreads, GnuTLS, and libxml2 when configured.
- Installs `libnbd.pc`.
- Test programs compile `errors.c` and `utils.c` directly with small focused test drivers.

Dependencies:
- Autotools/libtool variables, generated state-machine files, `common/utils/libutils.la`, GnuTLS/libxml2 configure substitutions.

Research notes:
- This file is the manifest showing the library architecture: generated API/state code plus small hand-written modules around handle state, transport, protocol, and utilities.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/aio.c -->
# File Research: sources/virtualization/libnbd/lib/aio.c

Implements async-facing helpers for file descriptor access, readiness notification, command completion, and in-flight count tracking.

Key functions:
- `nbd_internal_retire_and_free_command`: releases command callbacks and any block-status filter id vector, then frees the command.
- `nbd_unlocked_aio_get_fd`: returns the transport fd through socket ops, failing if not connected.
- `nbd_unlocked_aio_notify_read` / `nbd_unlocked_aio_notify_write`: feed external readiness events into the generated state machine.
- `nbd_unlocked_aio_command_completed`: finds a completed command by cookie, validates read byte coverage, unlinks it from `cmds_done`, frees it, and reports success or command error.
- `nbd_unlocked_aio_peek_command_completed`: returns the oldest completed command cookie without retiring it.
- `nbd_unlocked_aio_in_flight`: returns queued plus issued command count.

Interactions:
- Uses command queues in `struct nbd_handle`.
- Calls `nbd_internal_run` with `notify_read`/`notify_write`.
- Uses protocol names from `protocol.c` for error messages.

Research notes:
- Read completion treats short structured reads as `EPROTO` unless the server already reported an error.
- Disconnect commands are deliberately excluded from public completion tracking.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/aio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/connect.c -->
# File Research: sources/virtualization/libnbd/lib/connect.c

Provides synchronous and asynchronous connection entry points for Unix sockets, vsock, TCP, preconnected sockets, local commands, and systemd socket activation.

Key functions:
- `nbd_internal_wait_until_connected`: polls while the generated state machine is in a connecting group, then validates ready/negotiating/closed/dead outcome.
- Synchronous `nbd_unlocked_connect_*` wrappers: start the matching async connect and wait for completion.
- `nbd_unlocked_aio_connect`: stores a caller-provided sockaddr and starts `cmd_connect_sockaddr`.
- `nbd_unlocked_aio_connect_unix`: validates path length and stores `sockaddr_un`.
- `nbd_unlocked_aio_connect_vsock`: uses `sockaddr_vm` when available, otherwise fails with `ENOTSUP`.
- `nbd_unlocked_aio_connect_tcp`: stores hostname and port strings for generated TCP connection states.
- `nbd_unlocked_aio_connect_socket`: makes caller fd nonblocking and close-on-exec, wraps it in a socket object, then starts handshake directly.
- Command connection functions copy argv then trigger generated command/socket-activation connect states.

Interactions:
- Relies on generated external events such as `cmd_connect_sockaddr`, `cmd_connect_tcp`, `cmd_connect_socket`, `cmd_connect_command`, and `cmd_connect_sa`.
- Uses `utils.c` argv copying and `socket.c` socket wrapping.

Research notes:
- The preconnected socket path takes ownership of the fd on entry; failures close it.
- State validation preserves a previous fatal error if the machine enters DEAD.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/crypto.c -->
# File Research: sources/virtualization/libnbd/lib/crypto.c

Implements TLS configuration and the GnuTLS-backed socket wrapper used after `NBD_OPT_STARTTLS`.

Key public configuration:
- `nbd_unlocked_set_tls`, `get_tls`, `get_tls_negotiated`
- Certificate directory, peer verification, username, hostname, PSK file, and priority setters/getters.
- Username fallback uses `$LOGNAME`, then `getlogin_r`.

TLS socket ops:
- `tls_recv`, `tls_send`, `tls_pending`, `tls_get_fd`, `tls_shut_writes`, `tls_close`.
- Converts GnuTLS retry conditions to `EAGAIN`.
- Downgrades qemu-nbd-style unclean TLS close after client write shutdown to EOF/debug.

Credential setup:
- PSK mode reads `username:hexkey` entries from the configured PSK file and extends the priority string with PSK key exchanges.
- Certificate mode searches explicit cert dir, user pki dirs, or system config pki dir, loading CA, optional CRL, client cert/key, and numbered extra client cert/key pairs.
- Falls back to system CA when no private cert dir is found.
- Peer verification uses configured TLS hostname, falling back to connection hostname.

State-machine integration:
- `nbd_internal_crypto_create_session`: initializes nonblocking GnuTLS session, sets SNI, credentials, transport fd, timeout, and returns a TLS socket wrapper.
- `nbd_internal_crypto_is_reading`: reports GnuTLS handshake direction.
- `nbd_internal_crypto_handshake`: advances handshake and distinguishes complete, retry, and fatal error.
- `nbd_internal_crypto_debug_tls_enabled`: logs negotiated cipher, key exchange, MAC, and optional kTLS status.

Compile-time behavior:
- Without GnuTLS, TLS setters only allow disabling TLS, public support checks report false elsewhere, and internal TLS functions abort if reached.

Research notes:
- TLS is layered as a socket ops wrapper, so most library I/O is transport-agnostic.
- Certificate search behavior is security-sensitive because URI local-file parameters are separately policy-gated in `uri.c`.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/debug.c -->
# File Research: sources/virtualization/libnbd/lib/debug.c

Implements handle-level debug flag and debug callback dispatch.

Key functions:
- `nbd_unlocked_set_debug` / `get_debug`: toggle or read `h->debug`.
- `nbd_unlocked_clear_debug_callback`: frees the installed callback.
- `nbd_unlocked_set_debug_callback`: transfers callback ownership into the handle.
- `nbd_internal_debug`: formats a message, preserves `errno`, uses current error context if none is supplied, then calls the callback or writes to stderr.

Interactions:
- `internal.h` wraps this with `debug` and `debug_direct` macros guarded by `if_debug`.
- Error context comes from `errors.c`.

Research notes:
- Debug logging is designed to be safe on error paths by preserving `errno`.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/disconnect.c -->
# File Research: sources/virtualization/libnbd/lib/disconnect.c

Implements synchronous shutdown and async disconnect queuing.

Key functions:
- `nbd_unlocked_shutdown`: gracefully aborts option mode if negotiating, optionally abandons pending commands, queues disconnect if ready/processing, then polls until CLOSED or DEAD.
- `nbd_unlocked_aio_disconnect`: queues `NBD_CMD_DISC` through `nbd_internal_command_common` and marks `disconnect_request`.

Interactions:
- Uses option abort from `opt.c`.
- Uses command queue abort helper from generated state code.
- Uses polling and state predicates.

Research notes:
- `NBD_CMD_DISC` has no server reply, so the command remains in-flight until close/dead cleanup and no public completion cookie is returned.
- `LIBNBD_SHUTDOWN_ABANDON_PENDING` only aborts commands not yet sent to the server.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/disconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/errors.c -->
# File Research: sources/virtualization/libnbd/lib/errors.c

Owns thread-local last-error storage for libnbd API calls.

Key structures/functions:
- `struct last_error`: current API context, allocated error string, errno value.
- Constructor creates a pthread TLS key with destructor.
- Destructor frees current thread data but intentionally avoids `pthread_key_delete` due to a documented race.
- `nbd_internal_set_error_context`: records API function context.
- `nbd_internal_set_last_error`: replaces current error string and errno.
- `nbd_internal_get_error_context`: returns current context.
- `nbd_get_error` / `nbd_get_errno`: public accessors for last error.

Interactions:
- `internal.h` defines `set_error` macro around these functions.
- Generated API wrappers set context for functions that may set errors.

Research notes:
- Error state is per-thread, not per-handle.
- If TLS allocation fails, the code falls back to stderr diagnostics rather than losing all error information silently.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/flags.c -->
# File Research: sources/virtualization/libnbd/lib/flags.c

Maintains negotiated export size, export flags, block constraints, payload limit, and public feature queries.

Key functions:
- `nbd_internal_reset_size_and_flags`: clears export size, flags, block sizes, payload cap, canonical name, and description.
- `nbd_internal_set_size_and_flags`: validates nonzero eflags, masks inconsistent server claims, handles metadata-valid shortcut, then records export size/flags.
- `nbd_internal_set_block_size`: validates server-advertised block size constraints and ignores malformed advertisements.
- `nbd_internal_set_payload`: derives max payload from block maximum or defaults to 32 MiB.
- `nbd_unlocked_can_*` and `is_*`: query per-export feature flags.
- `nbd_unlocked_can_meta_context`: checks negotiated metadata context names.
- `nbd_unlocked_get_size`: returns export size with signed overflow guard.
- `nbd_unlocked_get_block_size`: returns minimum/preferred/maximum/payload sizes.

Interactions:
- State machine calls internal setters during negotiation.
- `rw.c` uses feature queries to enforce strict command validation.

Research notes:
- The file tolerates some invalid server feature combinations by clearing dependent flags instead of failing.
- Export size is considered valid only after `eflags != 0`.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/flags.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/handle.c -->
# File Research: sources/virtualization/libnbd/lib/handle.c

Primary handle lifecycle and configuration implementation.

Lifecycle:
- `nbd_create`: allocates handle, assigns debug name, initializes defaults, mutex, negotiation preferences, strictness, URI policy, export name, state, and generated create event.
- `nbd_close`: runs close callbacks in two phases, frees callbacks and vectors, aborts/free command queues, tears down socket/subprocess/socket-activation temp files, frees all owned strings, destroys mutex, poisons magic, and frees handle.
- `free_cmd_list`: completes pending commands with existing error or `ENOTCONN` before freeing.

Configuration APIs:
- Handle name, close callbacks, socket activation name, private data.
- Export name, requested block size/full info/canonical name/description.
- Metadata context request list.
- Extended headers, structured replies, metadata context request toggles.
- Handshake flags, pread initialization, strict mode.
- Package/version accessors.
- Subprocess kill/PID accessors.
- Feature support probes for TLS/vsock/URI.
- URI policy setters.
- Traffic stats.
- Keepalive and TCP keepalive option storage/getters.

Interactions:
- `flags.c` reset is triggered by export-name changes and close.
- `socket.c`/`crypto.c` close through socket ops.
- Generated state machine is initialized by `cmd_create`.

Research notes:
- Defaults request extended headers, structured replies, metadata contexts, and block size information.
- Close callbacks are called before their user data is freed, allowing callbacks to share backing structs.
- Keepalive getter reads the live socket option when connected, not just the stored desired flag.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/handle.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/internal.h -->
# File Research: sources/virtualization/libnbd/lib/internal.h

Private internal contract for libnbd hand-written code and generated state-machine code.

Major definitions:
- GCC hot-path helpers `unlikely` and `if_debug`.
- `MAX_REQUEST_SIZE` set to 64 MiB.
- Vector types for metadata contexts, uint32 lists, and close callbacks.
- `struct command_cb`: callback union for extents, reads, lists, contexts, and completion.
- `struct nbd_handle`: central state object containing configuration, negotiated state, transport, buffers, command queues, state-machine state, subprocess/TCP/socket-activation data, metadata state, stats, and strictness.
- `struct socket_ops` and `struct socket`: abstraction over plain sockets and TLS-wrapped sockets.
- `struct command`: queued command object with flags/type/cookie/offset/count/data/callback/error tracking.
- `struct execvpe`: precomputed fork-safe exec context.

Macros:
- Callback null/test/call/free helpers.
- `debug`, `debug_direct`, and `set_error`.
- State access macros for generated and hand-written code.
- `NBD_INTERNAL_FORK_SAFE_ASSERT`.

Declared internal APIs:
- Command retirement, connection wait, TLS session/handshake helpers, debug/error helpers, flag setters, state predicates, option cleanup, protocol mapping, command queuing, socket creation, generated state-machine hooks, utility and fork-safe exec helpers.

Interactions:
- Includes public `libnbd.h`, local `nbd-protocol.h`, generated `states.h` and `unlocked.h`, byte-swapping, and string vector helpers.

Research notes:
- This header reveals the full architecture: one locked handle, generated state transitions, pluggable socket ops, and linked-list command queues.
- Public state is atomic and distinct from internal current state.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/is-state.c -->
# File Research: sources/virtualization/libnbd/lib/is-state.c

Defines internal and public state classification helpers.

Key functions:
- Internal predicates for created, connecting, negotiating, ready, processing, dead, and closed.
- Connecting and processing use generated state-group hierarchy rather than enumerating every concrete state.
- Public `nbd_unlocked_aio_is_*` APIs read `public_state`.
- `nbd_unlocked_aio_get_direction` returns public-state poll direction.

Interactions:
- Depends on generated `nbd_internal_state_group`, `nbd_internal_state_group_parent`, and `nbd_internal_aio_get_direction`.
- Other internal code should use internal predicates on `state`, not public API predicates.

Research notes:
- The file documents the distinction between real internal state and externally visible state.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/is-state.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/libnbd.pc.in -->
# File Research: sources/virtualization/libnbd/lib/libnbd.pc.in

Installed pkg-config template for libnbd.

Content:
- Uses configured prefix, exec_prefix, libdir, and includedir.
- Exposes package name, version, description.
- Leaves `Requires` and `Cflags` empty.
- Emits `Libs: -lnbd`.

Research notes:
- Because no `-L${libdir}` or include path is emitted here, consumers rely on pkg-config installation context/default paths or compiler/linker defaults.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/libnbd.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/local/libnbd.pc.in -->
# File Research: sources/virtualization/libnbd/lib/local/libnbd.pc.in

Build-tree pkg-config template for out-of-tree packages using an uninstalled libnbd tree.

Content:
- Sets prefix/exec_prefix to `@abs_top_builddir@`.
- Points `libdir` at `lib/.libs`.
- Points `includedir` at source `include`.
- Emits `Cflags: -I${includedir}` and `Libs: -L${libdir} -lnbd`.

Research notes:
- This is intentionally a dummy local development pkg-config file.
- Comments note that the project `./run` script handles `PKG_CONFIG_PATH`.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/local/libnbd.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/nbd-protocol.h -->
# File Research: sources/virtualization/libnbd/lib/nbd-protocol.h

Local NBD wire protocol definitions shared by libnbd internals.

Major contents:
- Packed wire structs for old/new handshakes, newstyle options, option replies, export-name replies, requests, extended requests, simple/structured/extended replies, data/hole/block-status/error chunks.
- Magic constants for handshake, requests, and replies.
- Global flags, per-export flags, option codes, reply codes, info codes.
- Structured reply flags/types.
- Command codes and command flags.
- NBD wire error codes.

Interactions:
- `internal.h` embeds many of these structs in static buffers.
- `protocol.c` maps NBD error and command codes.
- Generated state machine reads/writes these wire layouts.

Research notes:
- All fields are network byte order; callers must use byte-swapping helpers.
- The header is BSD-licensed and notes it originated from nbdkit-style protocol definitions.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/nbd-protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/opt.c -->
# File Research: sources/virtualization/libnbd/lib/opt.c

Implements option-negotiation mode APIs, both synchronous and asynchronous.

Key functions:
- `nbd_internal_free_option`: frees option callbacks according to current option type.
- `nbd_unlocked_set_opt_mode` / `get_opt_mode`: configure option mode.
- `wait_for_option`: polls while connecting.
- Synchronous option APIs for GO, INFO, ABORT, STARTTLS, EXTENDED_HEADERS, STRUCTURED_REPLY, LIST, LIST_META_CONTEXT, SET_META_CONTEXT.
- Async option APIs set `h->opt_current`, store callbacks, transfer callback ownership, and kick the generated state machine with `cmd_issue`.
- Metadata context query helpers copy explicit queries or use the handle’s requested contexts.

Interactions:
- Generated state machine consumes `h->opt_current`, `h->opt_cb`, and `h->querylist`.
- `utils.c` supplies query-list copying.
- `flags.c`/state-machine code stores negotiated export and metadata results.

Research notes:
- Synchronous wrappers are thin async wrappers plus polling and completion-error interpretation.
- Fixed-newstyle is required for most options beyond GO/ABORT.
- STARTTLS is compile-time gated on GnuTLS.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/opt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/poll.c -->
# File Research: sources/virtualization/libnbd/lib/poll.c

Simple `poll(2)`-based event loop for users who do not integrate libnbd into their own loop.

Key functions:
- `do_poll`: builds pollfds for the NBD fd and optional extra fd, maps current state direction to POLLIN/POLLOUT, waits, and notifies read or write readiness.
- `nbd_unlocked_poll`: polls only the NBD connection.
- `nbd_unlocked_poll2`: also watches a caller-provided fd for readability.

Interactions:
- Uses `nbd_unlocked_aio_get_fd`, generated state direction, and `aio_notify_read/write`.

Research notes:
- The handle lock is intentionally not released during `poll`, to prevent another thread from closing fds being polled.
- If both read and write are ready, read notification is preferred because it services older server replies first.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/poll.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/protocol.c -->
# File Research: sources/virtualization/libnbd/lib/protocol.c

Small protocol mapping helper module.

Key functions:
- `nbd_internal_errno_of_nbd_error`: maps NBD wire error codes to local errno values.
- `nbd_internal_name_of_nbd_cmd`: maps command type codes to readable names.

Interactions:
- Completion paths in `aio.c` use command names for errors.
- Reply-handling state code can use errno mapping for server replies.

Research notes:
- Unknown NBD errors map to `EINVAL`.
- Comment notes similar command-name mapping is generated in nbdkit and could be unified.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/protocol.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/rw.c -->
# File Research: sources/virtualization/libnbd/lib/rw.c

Implements synchronous and asynchronous NBD commands for reads, writes, flush, trim, cache, zero, and block status.

Synchronous flow:
- Each synchronous API calls the async version with a null completion callback, then waits with `wait_for_command`.
- Structured read and block-status sync APIs assert callback ownership was transferred.

Core async queueing:
- `nbd_internal_command_common`: rejects commands after disconnect, checks in-flight overflow, applies strict zero-size/bounds/alignment validation, enforces request/payload limits, allocates command, assigns cookie, copies callbacks, initializes read-safety flag, appends to queue, and kicks generated state machine if ready.
- Commands move through `cmds_to_issue`, `cmds_in_flight`, and `cmds_done`.

Feature validation:
- Read structured validates DF support in strict mode.
- Write auto-manages `PAYLOAD_LEN` with extended headers when strict auto flag is enabled and checks readonly/FUA.
- Flush, trim, cache, zero check negotiated server capabilities in strict command mode.
- Block status requires structured replies and negotiated metadata contexts.
- Filtered block status requires extended headers and block-status payload support, then converts requested context names to negotiated context IDs.

Interactions:
- Uses feature queries from `flags.c`.
- Uses protocol command constants from `nbd-protocol.h`.
- Generated state machine consumes queued commands.

Research notes:
- Read buffers default to pre-initialized safety behavior through `h->pread_initialize`.
- Filtered block-status payload stores length high/low words followed by context IDs in network order.
- The command-common error cleanup path for block-status callbacks appears inconsistent with the normal retire path: it frees `extent32` when `wide` is true and `extent64` when false, while `aio.c` does the opposite.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/socket.c -->
# File Research: sources/virtualization/libnbd/lib/socket.c

Plain Berkeley socket implementation of `struct socket_ops`.

Key functions:
- `socket_recv`: wraps `recv`, setting libnbd error except for nonblocking retry errors.
- `socket_send`: adds `MSG_NOSIGNAL`, wraps `send`, and avoids process-wide SIGPIPE handler changes.
- `socket_get_fd`: returns fd.
- `socket_shut_writes`: calls `shutdown(SHUT_WR)` and ignores failures after debug logging.
- `socket_close`: closes fd and frees wrapper.
- `nbd_internal_socket_create`: allocates socket wrapper and installs ops.

Interactions:
- `connect.c` wraps preconnected sockets with this.
- `crypto.c` wraps this socket with TLS ops after STARTTLS.

Research notes:
- `pending` is not supplied for plain sockets; TLS supplies it because decrypted data may be buffered inside GnuTLS.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/socket.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-assert.c -->
# File Research: sources/virtualization/libnbd/lib/test-fork-safe-assert.c

Unit test driver for `NBD_INTERNAL_FORK_SAFE_ASSERT`.

Flow:
- Disables core dumps via `setrlimit(RLIMIT_CORE)` and, when available, `prctl(PR_SET_DUMPABLE, 0)`.
- Forces assertions on by undefining `NDEBUG`.
- Defines `TRUE` and `FALSE` to verify macro stringification.
- Calls assert on TRUE, then on FALSE; expected outcome is abort with a diagnostic naming `FALSE`.

Interactions:
- Uses `internal.h` fork-safe assertion helper from `utils.c`.
- Paired with `test-fork-safe-assert.sh`.

Research notes:
- Test intentionally aborts; shell wrapper validates signal and stderr.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-assert.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-assert.sh -->
# File Research: sources/virtualization/libnbd/lib/test-fork-safe-assert.sh

Shell test wrapper for the fork-safe assertion test binary.

Flow:
- Runs `./test-fork-safe-assert`, capturing stderr.
- Verifies exit status is signal-based abort.
- Accepts `ABRT` or `SIGABRT` naming from `kill -l`.
- Greps for exact assertion failure format containing `FALSE`.
- Ensures `TRUE` does not appear in stderr.

Research notes:
- Validates both behavior and diagnostic stringification of failed assertion expression.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-assert.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.c -->
# File Research: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.c

Helper binary for testing `nbd_internal_execvpe_init` and `nbd_internal_fork_safe_execvpe`.

Flow:
- Expects `program-to-exec argv0 ...`.
- Builds a null-terminated `string_vector` for target argv.
- Initializes execvpe context for the program.
- Prints generated candidate pathnames to stdout.
- Calls fork-safe execvpe directly; on failure prints machine-readable errno names for selected errors.

Interactions:
- Tests utility functions from `utils.c`.
- Uses process `environ`.
- Paired with `test-fork-safe-execvpe.sh`.

Research notes:
- The helper does not fork itself; it exercises the child-side exec function in a controlled standalone process.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.sh -->
# File Research: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.sh

Comprehensive shell test for the custom fork-safe execvpe implementation.

Setup:
- Sources shared test functions.
- Requires `realpath`.
- Skips Darwin due to known killed-process behavior.
- Resolves helper binary path, including BusyBox workaround.

Test harness:
- `run0` invokes helper with PATH unset or set narrowly and captures command, stdout, stderr, and status.
- `run` uses same string for `program-to-exec` and argv0.
- `init_fail`, `execve_fail`, and `success` validate expected behavior.

Scenarios:
- Empty program name fails during init with `ENOENT`.
- Direct path candidates: empty dir, FIFO, directory, non-executable file, trailing slash, symlink loop.
- Binary executable success via copied `expr`.
- ENOEXEC fallback to `/bin/sh` for executable script without shebang.
- PATH unset fallback to `confstr(_CS_PATH)`.
- Explicit PATH lists preserve candidate order and nonfatal execve retry behavior.
- Empty PATH elements expand to current directory.

Interactions:
- Validates the detailed semantics implemented in `utils.c`.

Research notes:
- The script encodes POSIX PATH behavior and ENOEXEC shell fallback expectations very explicitly.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/uri.c -->
# File Research: sources/virtualization/libnbd/lib/uri.c

Implements URI parsing, policy enforcement, connection dispatch, URI reconstruction, and URI-prefix detection.

With libxml2:
- `nbd_unlocked_connect_uri`: async connect plus wait.
- `parse_uri_queries`: decodes query string into name/value pairs, accepting `&` or `;`, CGI-style empty values, and ignoring `=value` entries.
- Recognized schemes: `nbd`, `nbds`, `nbd+unix`, `nbds+unix`, `nbd+vsock`, `nbds+vsock`, `nbd+ssh`, `nbds+ssh`.
- Enforces `scheme://` form and handle policies for allowed transports and TLS mode.
- Query parameters include `socket`, `nbd-port`, `compress`, TLS certificates/PSK/hostname/priority/username/verify-peer.
- Local file parameters require `nbd_set_uri_allow_local_file`.
- TLS priority override requires `nbd_set_uri_allow_tls_priority`.

Transport handling:
- TCP defaults to host `localhost` and port 10809, strips IPv6 literal brackets for `getaddrinfo`.
- Vsock defaults CID to host 2 and port 10809.
- SSH builds `ssh [-C] -p PORT [-o User=...] -- server nc ...`, using either Unix socket or localhost TCP on the remote.

URI reconstruction:
- `nbd_unlocked_get_uri`: reconstructs TCP/sockaddr-based Unix/vsock URIs when enough connection data is available.
- Adds TLS username, export path, TLS query params, and socket param as needed.
- Does not support abstract Unix sockets.

Without libxml2:
- URI connect/get APIs return `ENOTSUP`.

Always available:
- `nbd_unlocked_is_uri`: simple prefix check for supported NBD URI schemes.

Research notes:
- URI parsing is a major policy boundary because it can trigger local file reads for TLS material or SSH command execution.
- `append_query_params` does not escape values itself; it relies on libxml URI saving behavior for final URI creation.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/uri.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libnbd/lib/utils.c -->
# File Research: sources/virtualization/libnbd/lib/utils.c

General utility module for debug formatting, string-list copying, socket creation wrappers, fork-safe diagnostics, fork-safe assertion, and custom execvpe support.

Utility functions:
- `nbd_internal_hexdump`: formatted hex/ascii dump.
- `nbd_internal_copy_string_list`: deep-copies null-terminated string lists.
- `nbd_internal_set_argv`: validates and stores command argv on handle.
- `nbd_internal_set_querylist`: copies explicit metadata queries or defaults from requested contexts.
- Printable helpers convert buffers, strings, and string lists into bounded printable forms for API tracing.

Fork-safe diagnostics:
- `nbd_internal_fork_safe_itoa`: integer formatting without stdio allocation.
- `xwritel`: best-effort writev-based list writer intended to remain async-signal-safe.
- `nbd_internal_fork_safe_perror`: fork-safe perror-like diagnostic preserving errno.
- `nbd_internal_fork_safe_assert`: emits assertion failure using fork-safe helpers, then aborts.

Socket wrappers:
- `nbd_internal_socket`: creates close-on-exec and optionally nonblocking sockets, with fallback fcntl path when `SOCK_CLOEXEC` is missing.
- `nbd_internal_socketpair`: close-on-exec socketpair wrapper.

Execvpe implementation:
- `get_path`: copies `PATH`, falling back to `confstr(_CS_PATH)`.
- `nbd_internal_execvpe_init`: precomputes candidate pathnames and allocates shell-fallback argv before fork.
- `nbd_internal_execvpe_uninit`: frees exec context.
- `nbd_internal_fork_safe_execvpe`: child-side async-signal-safe exec loop, retrying nonfatal pathname errors and falling back to `/bin/sh` on `ENOEXEC`.

Interactions:
- Command-based connections use argv and execvpe helpers.
- Tests in `test-fork-safe-assert*` and `test-fork-safe-execvpe*` validate fork-safe paths.

Research notes:
- The execvpe split is intentionally pre-fork allocation plus post-fork exec-only behavior to avoid unsafe library calls in the child.
- Socket close-on-exec fallbacks note unavoidable race on platforms lacking `SOCK_CLOEXEC`.
<!-- END FILE RESEARCH: sources/virtualization/libnbd/lib/utils.c -->