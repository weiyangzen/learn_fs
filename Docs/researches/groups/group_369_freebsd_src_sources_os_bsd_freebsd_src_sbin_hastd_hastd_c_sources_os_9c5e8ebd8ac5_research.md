# Group Research: group_369_freebsd_src_sources_os_bsd_freebsd_src_sbin_hastd_hastd_c_sources_os_9c5e8ebd8ac5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hastd.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hastd.c

Read completely: 1337 lines.

This is the top-level HAST daemon process. It parses command-line options, loads the GEOM Gate kernel module, parses configuration, opens pid/control/listen sockets, daemonizes when requested, handles synchronous signal processing, accepts peer connections, and supervises per-resource worker children.

Key responsibilities:
- Maintains global daemon state: `cfgpath`, parsed `cfg`, pidfile handle, foreground/debug mode, and termination state.
- Starts listening on the configured control socket and all HAST peer listen addresses.
- Accepts remote HAST connections and performs the two-step secondary-side handshake using resource name, protocol version, and per-session token.
- Spawns/restarts primary workers and invokes secondary workers when both incoming and outgoing peer connections are established.
- Handles SIGHUP reloads by parsing a new config, switching listen/control sockets, adding/removing resources, restarting resources when required, and live-reloading compatible primary settings.
- Uses socketpair protocol connections for parent/child control, event, and connection-migration channels.
- Cleans descriptors aggressively in worker children and asserts that only expected descriptors remain open.

Important interactions:
- Uses `yy_config_parse()`/`yy_config_free()` from `parse.y`.
- Uses `proto_*` for TCP/socketpair abstractions, `hast_proto_*` for NV-framed HAST messages, and `control_*`/`event_*` for local daemon control.
- Calls `hastd_primary()` and `hastd_secondary()` to transfer resource work into role-specific workers.
- Uses hooks (`hook_init`, `hook_check`, `hook_fini`) for external event execution and `pjdlog` for daemon/syslog output.

Reliability and security notes:
- Peer admission first checks whether the remote address matches any configured resource, then verifies the requested resource and token.
- Reload distinguishes changes requiring full restart from changes safe for primary worker live reload.
- `select()` is bounded by `FD_SETSIZE`; many resources/listeners can hit the explicit assertion.
- Descriptor cleanup is intentionally strict and aborts if unexpected descriptors remain in children, which helps prevent fd leaks across privilege boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hastd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hastd.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hastd.h

Read completely: 53 lines.

This header exposes shared daemon globals and cross-module entry points for the HAST daemon core.

Key responsibilities:
- Declares global `cfgpath`, `sigexit_received`, and pidfile handle `pfh`.
- Declares descriptor cleanup/assertion helpers used after forking worker processes.
- Declares primary and secondary worker entry points.
- Declares `primary_config_reload()` for parent-to-primary live reload requests.

Important interactions:
- Includes `hast.h` for `struct hast_resource`.
- Includes `<nv.h>` because primary reload messages are NV encoded.
- Shared by `hastd.c`, `primary.c`, and other role/control modules.

Reliability notes:
- This is a small cross-module contract; changes affect process lifecycle, signal shutdown, worker startup, and reload behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hastd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hooks.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hooks.c

Read completely: 389 lines.

This file manages asynchronous external hook execution for HAST events. It forks configured executables, tracks child PIDs and command strings, reports long-running hooks, and logs hook termination status.

Key responsibilities:
- Initializes and destroys a global `hookprocs` queue protected by a mutex.
- Builds a bounded printable command string from hook path and arguments.
- Forks hook children with almost all descriptors closed and stdio redirected to `/dev/null` when logging to syslog.
- Restores an empty signal mask in hook children before `execv()`.
- Tracks hook PID, birth time, and last report time.
- Reaps known hook children through `hook_check_one()` and warns about missing or long-running hook processes through `hook_check()`.

Important interactions:
- Called by the daemon main loop after SIGCHLD and at periodic intervals.
- Uses `pjdlog` for status/error reporting and local synchronization wrappers from `synch.h`.
- Hook command construction uses `snprlcat()` from `subr.h`.

Reliability and security notes:
- Hooks run as forked external programs and inherit only intentionally preserved descriptors.
- Argument collection is capped at 64 entries and asserts that the varargs list terminates.
- Long command strings are rejected if they fill `PATH_MAX`.
- `hook_fini()` frees tracked hook records but does not kill running hooks; shutdown policy is handled elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hooks.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hooks.h

Read completely: 48 lines.

This header declares the HAST hook execution API.

Key responsibilities:
- Declares hook subsystem initialization and finalization.
- Declares child-status handling for a known PID/status pair.
- Declares periodic hook health checking.
- Declares variadic and `va_list` forms of hook execution.

Important interactions:
- Consumed by the daemon parent and role/event code that needs to run configured external commands.

Reliability notes:
- The variadic hook interface requires a NULL-terminated argument list, enforced by assertions in `hooks.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/hooks.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/lzf.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/lzf.c

Read completely: 408 lines.

This is the bundled liblzf compression/decompression implementation used by HAST when LZF compression is configured.

Key responsibilities:
- Implements `lzf_compress()` using a hash table of recent byte sequences and LZ-style literal/back-reference encoding.
- Implements `lzf_decompress()` for the compressed format documented in the source comments.
- Supports compile-time tuning through macros from `lzf.h`: hash size, fast modes, strict alignment, state passing, errno behavior, and input checking.
- Uses little fixed-format control bytes for literal runs, short backrefs, and long backrefs.
- Returns `0` on compression failure or decompression error, with decompression setting `errno` unless `AVOID_ERRNO` is enabled.

Important interactions:
- Included as a local compression primitive for HAST protocol data paths outside this file.
- The public ABI is declared in `lzf.h`.

Reliability and security notes:
- Decompression checks output bounds and, with `CHECK_INPUT`, input buffer bounds; it also rejects backrefs before the output base.
- Compression requires non-overlapping input/output buffers and returns failure when output would not fit.
- Some fast paths use unaligned 16-bit loads when permitted by platform macros.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/lzf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/lzf.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/lzf.h

Read completely: 217 lines.

This is the public and configuration header for the bundled liblzf implementation.

Key responsibilities:
- Declares `lzf_compress()` and `lzf_decompress()`.
- Documents compression/decompression contracts, buffer requirements, and errno behavior.
- Defines `LZF_VERSION`.
- Provides compile-time tuning defaults for `HLOG`, `VERY_FAST`, `ULTRA_FAST`, `STRICT_ALIGN`, `INIT_HTAB`, `AVOID_ERRNO`, `LZF_STATE_ARG`, and `CHECK_INPUT`.
- Defines internal byte/hash-table types used by `lzf.c`.

Important interactions:
- `LZF_STATE_ARG` can intentionally change the effective function prototype, so users must compile consistently.
- `STRICT_ALIGN` defaults differ by architecture and affect generated compression code.

Reliability notes:
- Header comments explicitly state compressed output can be larger than input and callers should keep uncompressed fallback logic.
- `CHECK_INPUT` is enabled by default, improving decompressor robustness against truncated or malformed streams.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/lzf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/metadata.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/metadata.c

Read completely: 224 lines.

This file reads and writes the fixed-size on-disk HAST metadata block at the beginning of a local provider.

Key responsibilities:
- Opens and probes the local provider on first metadata read through `provinfo()`.
- Optionally takes an exclusive nonblocking `flock()` for read/write metadata access.
- Reads `METADATA_SIZE` bytes from offset 0 and decodes them as an NV buffer.
- Validates that any stored `resource` name matches the configured resource.
- Populates data size, extent size, dirty extent retention, data offset, resource UUID, local/remote generation counters, and previous role.
- Serializes current metadata fields into an NV buffer, pads to `METADATA_SIZE`, and writes it to offset 0.

Important interactions:
- Uses the local `nv` encoder/decoder and `ebuf`.
- Uses `role2str()` and provider helpers from shared HAST support code.
- Primary metadata writes are protected by `metadata_lock` in `primary.c`.

Reliability and security notes:
- Partial metadata reads/writes are treated as failure.
- The fixed metadata size is 4096 bytes; the header notes sector size is not accounted for.
- On first open failure, the file descriptor is closed and reset to avoid leaving a half-initialized resource.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/metadata.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/metadata.h

Read completely: 47 lines.

This header defines the HAST metadata block size and metadata read/write API.

Key responsibilities:
- Defines `METADATA_SIZE` as 4096 bytes.
- Declares `metadata_read(struct hast_resource *, bool openrw)`.
- Declares `metadata_write(struct hast_resource *)`.

Important interactions:
- Included by primary/secondary role code and metadata implementation.
- Depends on `struct hast_resource` from `hast.h`.

Reliability notes:
- The comment flags a known limitation: metadata sizing does not account for actual provider sector size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/nv.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/nv.c

Read completely: 961 lines.

This file implements HAST’s local name/value container and wire serialization format. It stores typed fields in an `ebuf` as aligned TLV records and supports endian conversion between host and network representation.

Key responsibilities:
- Defines supported scalar, array, and string types for signed/unsigned 8/16/32/64-bit values and strings.
- Allocates/frees `struct nv` containers and records the first error encountered.
- Validates an entire buffer for header size, name termination, type range, data size alignment, scalar/array sizing, and string termination.
- Converts buffers to network byte order with `nv_hton()` and from network byte order with `nv_ntoh()`.
- Provides typed add/get functions generated by macros.
- Provides formatted string insertion and formatted-name lookup.
- Provides existence/assertion helpers and a debug dump routine.
- Lazily swaps individual records to host byte order during lookup.

Important interactions:
- Used by metadata, daemon handshakes, control messages, events, and HAST protocol headers.
- Depends on `ebuf` for backing storage and `pjdlog`/assertion macros for invariant enforcement.

Reliability and security notes:
- `nv_validate()` is the key trust boundary for buffers received from disk/network.
- Duplicate names are noted as a TODO and are not rejected.
- Name formatting is bounded to 255 bytes by assertions; production behavior depends on those invariants being met by callers.
- `nv_find()` mutates records into host order, while `nv_hton()` mutates them back to network order, so callers should avoid sharing one mutable NV buffer across unsynchronized users.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/nv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/nv.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/nv.h

Read completely: 132 lines.

This header declares the HAST name/value API.

Key responsibilities:
- Declares allocation, freeing, error inspection, error setting, and validation.
- Declares conversion to/from `struct ebuf` network representation.
- Declares typed add/get functions for integer scalars, integer arrays, and strings.
- Declares formatted string helpers, existence/assertion helpers, and dump support.
- Annotates formatted-name APIs with `__printflike`.

Important interactions:
- Used across HAST daemon protocol, metadata, control, and event code.
- Exposes opaque `struct nv`, keeping wire details private to `nv.c`.

Reliability notes:
- The get functions return zero/NULL both for absent fields and true zero values; callers must use `nv_error()`, `nv_exists()`, or `nv_assert()` when absence matters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/nv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/parse.y -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/parse.y

Read completely: 1037 lines.

This yacc grammar parses HAST daemon configuration files and resolves global, node-level, resource-level, and resource-node-level settings into a `struct hastd_config`.

Key responsibilities:
- Parses directives for control socket, pidfile, listen addresses, replication mode, checksum, compression, timeout, exec hook, metaflush, node blocks, and resource blocks.
- Matches `on <node>` sections against hostname, short hostname, `kern.hostuuid`, and `hostid<kern.hostid>`.
- Applies defaults: control address, pidfile, IPv4/IPv6 listen addresses, memsync replication, no checksum, hole compression, default timeout, no exec hook, and metaflush enabled.
- Validates positive timeout, string lengths, duplicate resource names, required remote/local configuration, and presence of a matching node section per resource.
- Fills per-resource provider name, local path, remote/source addresses, replication/checksum/compression/timeout/exec/metaflush, role state, file descriptors, ggate unit, and protocol version.
- Synthesizes default listen addresses only for address families supported by the kernel.

Important interactions:
- Consumed by `hastd.c` at startup and reload.
- Uses tokenization state from the generated lexer via `yyin`, `yytext`, `depth`, and `lineno`.
- Uses `hast.h` constants for roles, replication, checksum, compression, addresses, and defaults.

Reliability and security notes:
- Host identity matching is central: only sections for the current node affect local configuration.
- `remote none` is accepted as the literal string `"none"`, later treated by primary code as no real remote.
- Config reload reparses through this same path, so parse failures leave the previous live config active.
- Memory cleanup is explicit in `yy_config_free()`, including both temporary default listen entries and accepted config lists.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.c

Read completely: 613 lines.

This file implements HAST’s logging layer, supporting foreground stderr/stdout logging and daemon syslog logging, with debug filtering, prefixes, errno-aware messages, exit helpers, and assertion aborts.

Key responsibilities:
- Initializes and finalizes logging mode.
- Registers FreeBSD extended printf renderers for humanized numbers (`%N`) and socket addresses (`%S`), plus standard `%T` support.
- Maintains global log mode, debug level, and a bounded prefix string.
- Routes errors/warnings to stderr and informational/debug output to stdout in standard mode.
- Routes messages through `syslog()` in daemon mode.
- Preserves `errno` across logging setup and output routines.
- Provides `pjdlog_exit`, `pjdlog_exitx`, and `pjdlog_abort`.

Important interactions:
- Used by all HAST daemon modules for ordinary logging, debug traces, fatal exits, and assertions.
- The `%S` renderer is used by TCP address rendering in protocol code.

Reliability notes:
- Debug messages above the configured level are discarded early.
- Syslog messages are assembled into a 1024-byte buffer, so long messages are truncated by `snprintf`/`vsnprintf`.
- The implementation is process-global rather than thread-local; concurrent threads share prefix and debug mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.h

Read completely: 117 lines.

This header declares the logging API and convenience macros used throughout HAST.

Key responsibilities:
- Defines standard and syslog logging modes.
- Declares initialization, finalization, mode, debug-level, and prefix functions.
- Declares common, regular, debug, errno-aware, exit, exitx, and abort logging functions.
- Provides log-level convenience macros such as `pjdlog_error`, `pjdlog_warning`, and `pjdlog_info`.
- Provides verification/assertion macros: `PJDLOG_VERIFY`, `PJDLOG_RVERIFY`, `PJDLOG_ABORT`, `PJDLOG_ASSERT`, and `PJDLOG_RASSERT`.

Important interactions:
- The macros are used as hard invariants throughout protocol, worker, parser, and metadata code.
- `NDEBUG` disables `PJDLOG_ASSERT`/`PJDLOG_RASSERT` but not `PJDLOG_VERIFY`.

Reliability notes:
- Fatal helpers are annotated `__dead2`; formatted APIs are annotated `__printflike`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/primary.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/primary.c

Read completely: 2450 lines.

This file implements the primary-role worker. It exposes the GEOM Gate provider to the kernel, forwards I/O to local and remote components according to the selected replication mode, maintains the activemap, performs synchronization, reconnects to the secondary, and handles live primary configuration reloads.

Key responsibilities:
- Creates parent/child socketpair channels for control, events, and connection requests, then forks the primary worker.
- In the child, cleans descriptors, reinitializes logging, reads metadata, initializes activemap and range locks, opens `/dev/ggctl`, creates or recovers `hast/<provider>`, drops privileges, and starts worker threads.
- Maintains a fixed pool of 256 `hio` request objects with per-component error slots and queue linkage.
- Runs queues for free requests, local send, remote send, remote receive, done completion, and synchronization.
- Receives GEOM Gate I/O (`BIO_READ`, `BIO_WRITE`, `BIO_DELETE`, `BIO_FLUSH`) and dispatches it to local and/or remote components.
- Implements replication semantics: async can complete writes after local success, memsync completes after local success plus remote receive acknowledgment, and fullsync waits for final remote completion.
- Tracks dirty ranges in the activemap, writes it after dirty/clean transitions, and uses range locks to serialize regular writes against synchronization.
- Performs two-stage primary-to-secondary handshake, validates data/extent sizes, negotiates protocol version, exchanges counters/resource UUID, receives remote activemap data, detects split-brain messages, and starts synchronization.
- Runs a guard thread for signals and periodic reconnection.
- Supports live reload of remote/source address, replication, checksum, compression, timeout, hook path, and metaflush.

Important interactions:
- Depends on GEOM Gate ioctls for virtual block-device I/O.
- Uses `metadata.c` for persistent resource identity/counters and `activemap` for dirty extent tracking.
- Uses `proto_*` and `hast_proto_*` for remote communication.
- Uses `event_send()` for connect/disconnect/sync/split-brain notifications.
- Uses `ctrl_thread()` for child control messages and `primary_config_reload()` for reload commands.

Reliability and security notes:
- Remote connection access is protected by per-component rwlocks; metadata counters are protected by `metadata_lock`.
- Local reads can fall back to remote reads when appropriate.
- The synchronization source is determined by local/remote counters and remote handshake state outside this file’s visible helpers, then used to read from the up-to-date side and write to the stale side.
- If the remote disconnects, the primary bumps local counters on subsequent writes to preserve divergence tracking.
- Many fatal paths destroy the GEOM Gate provider before exiting; worker restart is supervised by the parent daemon.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/primary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto.c

Read completely: 444 lines.

This file implements the generic transport abstraction for HAST connections. Protocol backends register themselves at constructor time, and callers use uniform client/server/send/recv/descriptor/address APIs.

Key responsibilities:
- Maintains a global queue of `struct proto` backends.
- Registers default and non-default protocols, with the default inserted last.
- Allocates typed `struct proto_conn` wrappers for client, server-listen, and server-work sides.
- Selects a backend by asking each protocol to create a client or server context for an address.
- Wraps backend connect, connect-wait, accept, send, receive, descriptor, address-match, local-address, remote-address, timeout, and close operations.
- Sends and receives already-open protocol connections by passing the backend name plus a file descriptor over another proto connection.

Important interactions:
- `proto_tcp.c` registers the default `tcp` backend.
- `proto_socketpair.c` registers `socketpair` for parent/child and descriptor-migration channels.
- `proto_common.c` provides shared send/recv helpers for socket-like backends.

Reliability notes:
- The abstraction relies heavily on backend function-pointer completeness and side assertions.
- `proto_timeout()` sets both send and receive socket timeouts on the descriptor returned by the backend.
- Connection passing requires the receiving process to have a backend with the transmitted protocol name.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto.h

Read completely: 60 lines.

This header declares the public HAST protocol transport abstraction.

Key responsibilities:
- Declares opaque `struct proto_conn`.
- Declares client/server creation, connect, connect-wait, accept, send, receive, connection passing, descriptor lookup, address matching, address rendering, timeout configuration, and close functions.

Important interactions:
- Used by daemon parent/worker code, control/event channels, and HAST remote protocol framing.

Reliability notes:
- The API hides backend details, but callers must respect connection side semantics and close every returned `proto_conn`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_common.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_common.c

Read completely: 231 lines.

This file provides shared socket send/receive helpers for protocol backends, including optional descriptor passing over UNIX-domain sockets.

Key responsibilities:
- Detects whether a socket is blocking.
- Sends file descriptors using `sendmsg()` and `SCM_RIGHTS`.
- Receives file descriptors using `recvmsg()` and validates the control message.
- Sends data in chunks up to `MAX_SEND_SIZE` with `MSG_NOSIGNAL`.
- Retries `ENOBUFS` send failures with increasing delays for up to about 11 seconds.
- Uses `shutdown()` with NULL data to declare one-way direction in socketpair-style channels.
- Receives data with `MSG_WAITALL` and translates blocking-socket `EAGAIN` to `ETIMEDOUT`.

Important interactions:
- Used by both TCP and socketpair protocol backends.
- Descriptor send/receive is required for passing established TCP connections between daemon parent and primary worker.

Reliability notes:
- Send loops handle partial writes.
- Receive relies on `MSG_WAITALL`; short positive reads are not separately checked in this wrapper.
- Descriptor passing assumes the underlying transport supports `SCM_RIGHTS`, so TCP backend asserts descriptor passing is not requested.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_impl.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_impl.h

Read completely: 78 lines.

This internal header defines the protocol backend interface.

Key responsibilities:
- Defines the constructor attribute used by backend modules.
- Declares backend callback typedefs for client/server setup, connect, accept, wrapping inherited descriptors, send/receive, descriptor lookup, address matching/rendering, and close.
- Defines `struct proto`, including backend name, callback table, and queue linkage.
- Declares `proto_register()`.
- Declares shared `proto_common_send()` and `proto_common_recv()`.

Important interactions:
- Included by `proto.c`, `proto_tcp.c`, `proto_socketpair.c`, and `proto_common.c`.

Reliability notes:
- This is a private ABI between the registry and backends; callback signature mismatches or missing callbacks surface as assertions in `proto.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_socketpair.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_socketpair.c

Read completely: 235 lines.

This file implements a `socketpair://` protocol backend for local in-process or parent/child communication.

Key responsibilities:
- Creates a UNIX `SOCK_STREAM` socketpair for client setup.
- Infers side lazily: first send selects the client side, first receive selects the server side.
- Closes the unused end after side selection.
- Delegates data and descriptor send/receive to `proto_common_send()` and `proto_common_recv()`.
- Returns the active descriptor for select/control logic.
- Closes both descriptors if side is still undefined, or the active descriptor for a selected side.
- Registers the backend as non-default under protocol name `socketpair`.

Important interactions:
- Used by `hastd_primary()` for control, event, and connection request channels.
- Used by `proto_connection_send()`/`recv()` paths to pass TCP descriptors between parent and child.

Reliability notes:
- Side selection is implicit and order-dependent; the caller must perform the initial direction-declaration send/recv consistently.
- The backend has no address matching or address rendering because it is local-only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_socketpair.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_tcp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_tcp.c

Read completely: 636 lines.

This file implements the default TCP transport backend for HAST peer communication and control/listen addresses.

Key responsibilities:
- Parses `tcp://`, `tcp4://`, `tcp6://`, bare host/IP, IPv4 host:port, and bracketed IPv6 address:port strings.
- Applies the default HAST TCP port when no port is provided.
- Creates client and server sockets, sets `TCP_NODELAY`, binds optional source addresses, enables `SO_REUSEADDR` for listeners, and listens with backlog 8.
- Connects using nonblocking mode to support explicit timeouts, then restores blocking mode.
- Supports waiting for asynchronous connect completion through `select()` and `SO_ERROR`.
- Accepts incoming connections and wraps inherited descriptors.
- Sends/receives data through `proto_common_send()`/`proto_common_recv()`.
- Matches a connected peer against a configured address by resolving the configured address and comparing only IP address bytes.
- Renders local/remote addresses with the `pjdlog` `%S` socket-address formatter.
- Registers itself as the default protocol named `tcp`.

Important interactions:
- Used for HAST peer replication connections and daemon listen/control sockets.
- Works with `proto.c` connection passing, where accepted or newly connected TCP descriptors can be wrapped in another process.

Reliability and security notes:
- Address parsing bounds host and port buffers and validates numeric port range 1-65535.
- `tcp_address_match()` ignores port and matches only address family and IP address, which is deliberate access control behavior to note.
- `tcp_accept()` stores the accepted peer address into the listener context’s sockaddr storage before allocating the work context, so listener-local address state is overwritten by the last accept.
- Descriptor passing is not supported directly by TCP send/recv; assertions require `fd == -1` and `fdp == NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/hastd/proto_tcp.c -->