# subset-b-009652 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_lowlevel.c -->
# sources/user-network-fs/libfuse/lib/fuse_lowlevel.c

Purpose: `fuse_lowlevel.c` is the main implementation of libfuse's low-level FUSE session API. It translates kernel FUSE wire requests into `struct fuse_lowlevel_ops` callbacks, serializes replies and notifications back to `/dev/fuse`, manages session lifecycle and mount setup, negotiates kernel capabilities during `FUSE_INIT`, and bridges normal read/write transport with optional splice and io_uring paths.

Important APIs, types, and functions: Public reply helpers include `fuse_reply_err`, `fuse_reply_none`, `fuse_reply_entry`, `fuse_reply_attr`, `fuse_reply_open`, `fuse_reply_write`, `fuse_reply_buf`, `fuse_reply_data`, `fuse_reply_statfs`, xattr/lock/ioctl/poll/lseek/statx replies, and directory-entry builders `fuse_add_direntry` and `fuse_add_direntry_plus`. Session APIs include `fuse_session_new_versioned`, `fuse_session_mount`, `fuse_session_unmount`, `fuse_session_receive_buf`, `fuse_session_process_buf`, `fuse_session_destroy`, `fuse_session_exit/reset/exited`, custom I/O registration, sync-init toggles, and teardown watchdog management. Notification APIs cover inode/entry invalidation, expire-only entries, delete, store, retrieve, prune, poll wakeups, and epoch increment. Internal state centers on `struct fuse_session`, `struct fuse_req`, interrupt request lists, notify request lists, thread-specific splice pipes, optional `struct fuse_timeout_thread`, and io_uring flags embedded in request state.

Control flow: receive paths allocate or reuse read buffers, optionally splice from the FUSE fd into a per-thread pipe, then call `fuse_session_process_buf_internal`. Processing validates INIT ordering, `allow_root` access rules, opcode support, and interrupt state before dispatching through `fuse_ll_ops`. Most `_do_*` handlers adapt a wire struct and payload into a low-level callback, synthesize `struct fuse_file_info` where needed, or return `ENOSYS`. Replies build a `fuse_out_header` plus payload iovecs and use normal `writev`, custom I/O, splice, or io_uring commit depending on request/session state. `FUSE_INIT` is special: it derives `capable_ext`, default wanted capabilities, user callback overrides, max-write/buffer sizes, request timeout, passthrough, security context, and optional `FUSE_OVER_IO_URING`, then marks `got_init` before replying. Mount flow supports `/dev/fd/N`, new Linux mount API with sync-init, fallback to fusermount, and old kernel mount helpers.

State and persistence behavior: The file owns in-memory session state only; filesystem data remains in user callbacks and kernel caches. Request objects are reference-counted, listed for interrupt lookup unless interrupts are disabled or the request is io_uring-backed, and freed after reply. Security contexts from FUSE extensions are copied into the request because request buffers are transient. `se->mountpoint`, `se->fd`, `got_init`, `got_destroy`, `mt_exited`, negotiated connection fields, notify counters, and per-thread pipes survive across requests. Notifications mutate kernel cache state but do not persist local data.

Dependencies and integration points: It depends on `fuse_i.h`, kernel ABI structs from `fuse_kernel.h`, mount helpers, daemonization helpers, buffer copying, optional USDT tracing, optional splice/vmsplice, optional io_uring via `fuse_uring_i.h`, POSIX threads, atomics, semaphores, eventfd, polling, and Linux ioctls for passthrough and sync init. It is called by high-level libfuse setup in `helper.c`/`fuse.c`, loop implementations, service mount flow, signal handlers, and external users of the low-level API.

Risks: This is ABI-critical code with many protocol minor-version gates, so struct sizes, payload offsets, and capability bit translations are high risk. Interrupt handling uses layered locks and list mutation, with explicit io_uring exclusions. Splice paths must clear pipes after partial consumption or fallback, and buffer ownership differs for internal and external callers. `FUSE_INIT` accepts user-mutated capability fields, so invalid `want`/`want_ext` conversion can abort the session. Sync-init and new mount API fallback have complex fd/thread sequencing. Security context parsing assumes extensions are at the end of the relevant buffer and only copies the first security-context extension.

Test signals: Useful coverage would exercise INIT negotiation across protocol minors, invalid want flags, max-write mismatch, normal and `write_buf` dispatch, interrupt-before/after-request ordering, notify retrieve replies, security context extension iteration/reset, splice fallback paths, `/dev/fd/N` mounts, sync-init failure paths, and teardown watchdog behavior. Existing build signals should also catch source-level syntax regressions in the `fuse_ll_ops` tables and platform ifdefs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_lowlevel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_misc.h -->
# sources/user-network-fs/libfuse/lib/fuse_misc.h

Purpose: `fuse_misc.h` centralizes small portability macros used throughout libfuse. It hides platform differences for symbol versioning and nanosecond timestamp fields in `struct stat`.

Important APIs, types, and functions: `FUSE_SYMVER(sym1, sym2)` expands to either a compiler `symver` attribute, an assembler `.symver` directive, or nothing, depending on configuration. Timestamp helpers `ST_ATIM_NSEC`, `ST_CTIM_NSEC`, `ST_MTIM_NSEC` and corresponding setters map to Linux `st_atim`, FreeBSD `st_atimespec`, or no-op/zero fallbacks when nanosecond fields are unavailable.

Control flow: There is no runtime control flow. Preprocessor conditionals choose definitions at compile time from `LIBFUSE_BUILT_WITH_VERSIONED_SYMBOLS`, `HAVE_SYMVER_ATTRIBUTE`, `HAVE_STRUCT_STAT_ST_ATIM`, and `HAVE_STRUCT_STAT_ST_ATIMESPEC`.

State and persistence behavior: The header has no state. The setter macros mutate caller-owned `struct stat` objects when a platform exposes nanosecond fields.

Dependencies and integration points: It includes `pthread.h` and is used by low-level conversion code and helper APIs that need exported ABI symbol names or portable timestamp copying. `fuse_lowlevel.c` relies on these macros when translating between `struct stat` and FUSE wire attributes.

Risks: Macro-only portability code can silently drop timestamp precision on platforms without recognized fields. `FUSE_SYMVER` correctness is build-system and object-format dependent; an incorrect configuration can break ABI compatibility or produce duplicate/missing public symbols.

Test signals: Build tests across Linux, FreeBSD, macOS/no-versioned-symbols, and compilers with and without `symver` attribute are the main signal. Attribute conversion tests should verify nanosecond round-tripping on supported platforms and clean compilation with no-op setters elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_opt.c -->
# sources/user-network-fs/libfuse/lib/fuse_opt.c

Purpose: `fuse_opt.c` implements libfuse's argument and `-o` option parsing framework around `struct fuse_args`, `struct fuse_opt`, and optional callback processors. It is the shared parser used by low-level session options, high-level helper options, mount options, modules, and connection capability options.

Important APIs, types, and functions: Public APIs are `fuse_opt_free_args`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_match`, and `fuse_opt_parse`. Internal `struct fuse_opt_context` tracks input argv, output argv, accumulated `-o` options, parser callback, non-option boundary, and user data. Template handling is implemented by `match_template`, `find_opt`, `process_opt_param`, `process_opt`, `process_opt_sep_arg`, `process_gopt`, and option-group splitting helpers.

Control flow: `fuse_opt_parse` initializes a context, preserves `argv[0]`, iterates arguments, splits `-ofoo,bar` and `-o foo,bar` groups, handles `--`, matches each option against templates, writes integer/string values to `data + offset`, or calls the user callback with `FUSE_OPT_KEY_*`. Kept unknown options are copied to output argv or escaped back into a rebuilt `-o` string. On success it swaps parsed output into the caller's `struct fuse_args` and frees the old vector.

State and persistence behavior: The parser creates a new allocated argv vector and may consume/free the old vector if `args->allocated` is set. String options replace prior values at their target offset. The parser does not persist global state; all state is per-parse and freed before return.

Dependencies and integration points: It depends on `fuse_i.h`, `fuse_opt.h`, and `fuse_misc.h`. It is used by `helper.c`, `fuse_lowlevel.c`, mount option parsing, and runtime modules such as `iconv` and `subdir`. Template semantics are part of libfuse's public API, so downstream filesystems can provide their own `struct fuse_opt` tables and callbacks.

Risks: Offset-based writes assume the option table matches the target data struct; a wrong offset or `%` format corrupts memory. Escaping and octal decoding in option groups are easy to regress. `process_opt` has subtle handling for templates with separators and separate arguments. Memory ownership is strict: callers must understand when argv strings are duplicated, transferred, or freed.

Test signals: Parser tests should cover exact matches, `key` callbacks, discard/keep behavior, `-o` comma groups, escaped commas/backslashes/octal escapes, separate-argument templates, `--`, invalid numeric formats, missing arguments, string replacement, and non-allocated input argv preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_service.c -->
# sources/user-network-fs/libfuse/lib/fuse_service.c

Purpose: `fuse_service.c` implements libfuse support for "safe" systemd-managed FUSE services. It accepts a systemd-passed Unix socket, negotiates a small service protocol with a mount service, receives `/dev/fuse` and argument memfd file descriptors, requests service-side file opens, and delegates fsopen/mount operations to the privileged helper.

Important APIs, types, and functions: `struct fuse_service` stores expected mount format, socket fd, fuse device fd, argv memfd, ownership flags, and negotiated permissions for `allow_other` and `fuseblk`. Public APIs include `fuse_service_accept`, `fuse_service_receive_file`, `fuse_service_request_file`, `fuse_service_request_blockdev`, `fuse_service_send_goodbye`, `fuse_service_can_allow_other`, `fuse_service_can_fuseblk`, `fuse_service_append_args`, `fuse_service_finish_file_requests`, `fuse_service_expect_mount_format`, `fuse_service_session_mount`, `fuse_service_release`, `fuse_service_destroy`, `fuse_service_cmdline`, `fuse_service_parse_cmdline_opts`, and `fuse_service_exit`.

Control flow: Startup checks `LISTEN_PID`/`LISTEN_FDS`, validates exactly one AF_UNIX socket at `SD_LISTEN_FDS_START`, sets close-on-exec, then `negotiate_hello` validates protocol versions and service flags. The service receives an argv memfd and `/dev/fuse` fd via SCM_RIGHTS, appends helper-provided args from the memfd, disables further fd passing when supported, and mounts by first handing `/dev/fd/<fusedevfd>` to `fuse_session_mount`. It then sends fsopen, source, mountpoint, mount options, mtab options, and final mount commands over the socket, checking simple replies for remote errors. Shutdown sends a BYE command, closes fds, and compresses service exit codes for systemd.

State and persistence behavior: State is per `struct fuse_service`; it owns fds until transferred or released. `fuse_service_session_mount` transfers the fuse device fd into the session on success. Argument appending replaces the caller's `struct fuse_args` with a newly allocated vector and closes the argv memfd. There is no durable storage, but protocol commands affect the remote mount service and kernel mount namespace.

Dependencies and integration points: It depends on systemd socket activation (`sd-daemon.h`), Unix domain sockets, SCM_RIGHTS fd passing, network byte order conversions, Linux mount helper internals, `fuse_service_priv.h` wire structs, and standard libfuse session/mount option functions. `helper.c` integrates it into service-mode `fuse_main`.

Risks: The protocol is trust-boundary code, so length checks, magic checks, byte-order conversions, fd validation, and SCM_RIGHTS truncation handling are critical. Incorrect ownership transitions can leak or double-close fds. Source currently contains duplicated statements in `fuse_service_request_path` (`block_size`) and `send_mount` (`return -error;`), which are likely harmless or unreachable but signal patch hygiene risk. Service-mode logging intentionally sleeps before exit, which affects tests and failure latency.

Test signals: Integration tests need socket-activated startup with valid and invalid hello versions, rejected flags, malformed packet sizes/magic, fd passing denied/truncated, argv memfd parsing, file/blockdev requests, mount command error propagation, `allow_other`/`fuseblk` negotiation, and cleanup after partial accept failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_service_stub.c -->
# sources/user-network-fs/libfuse/lib/fuse_service_stub.c

Purpose: `fuse_service_stub.c` provides ABI-compatible service-mount functions for builds or platforms where safe systemd container support is unavailable.

Important APIs, types, and functions: It defines the same exported service functions as `fuse_service.c`: file request/receive helpers, goodbye, accept, capability queries, arg append, command-line formatting/parsing, finish-file-requests, mount-format expectation, service session mount, release/destroy, and service exit.

Control flow: Most functions immediately return `-EOPNOTSUPP`, `false`, `NULL`, or `-1`. `fuse_service_accept` is deliberately non-fatal: it stores `NULL` in the output pointer and returns 0 to signal that no service socket was accepted. `fuse_service_destroy` nulls the caller's pointer. `fuse_service_exit` returns the input code unchanged.

State and persistence behavior: The stub owns no state and closes no resources. It never creates a `struct fuse_service` instance.

Dependencies and integration points: It includes `fuse_i.h` and `fuse_service.h` so callers can link against a consistent API regardless of `HAVE_SERVICEMOUNT`. `meson.build` chooses this file when service-mount support is disabled.

Risks: Callers must distinguish "not running as a service" from unsupported service operations. Code paths that unconditionally call request/mount helpers after a null accept will see `-EOPNOTSUPP`. Because release is a no-op, accidentally passing a real service pointer from a mismatched build would leak resources, though that should not occur with one selected implementation.

Test signals: Build/link tests with `HAVE_SERVICEMOUNT=false` should verify public symbols exist. Runtime tests should confirm `fuse_service_accept` returns success with no service and all service-only operations fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_service_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_signals.c -->
# sources/user-network-fs/libfuse/lib/fuse_signals.c

Purpose: `fuse_signals.c` installs and removes process-wide signal handlers that tell a FUSE session to exit on normal teardown signals, ignore SIGPIPE, and optionally abort with a backtrace on fatal signals.

Important APIs, types, and functions: Public functions are `fuse_set_signal_handlers`, `fuse_set_fail_signal_handlers`, and `fuse_remove_signal_handlers`. Internal helpers include `exit_handler`, `exit_backtrace`, `do_nothing`, `dump_stack`, `set_one_signal_handler`, `_fuse_set_signal_handlers`, and `_fuse_remove_signal_handlers`. Static arrays define teardown signals (`SIGHUP`, `SIGINT`, `SIGTERM`), ignored signals (`SIGPIPE`), and fatal backtrace signals (`SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGBUS`, `SIGFPE`, `SIGSEGV`).

Control flow: Installing handlers walks the selected signal arrays and only replaces default handlers, preserving handlers set by the application. Teardown signals call `fuse_session_exit` and store the signal number in `se->error`. Fatal handlers exit the session, remove handlers, log the signal, dump a backtrace when available, and abort. Removal resets handlers back to default only if they still match the libfuse-installed handler and clears the global `fuse_instance` if it matches the supplied session.

State and persistence behavior: The file uses one process-global `static struct fuse_session *fuse_instance`, so the last installed session owns signal handling. There is no per-session handler table. Backtrace storage is a static buffer when enabled.

Dependencies and integration points: It depends on `fuse_lowlevel.h` and `fuse_i.h` for session access and logging, POSIX `sigaction`, and optional `execinfo` backtrace APIs. `helper.c` installs these handlers before entering single-threaded or multithreaded loops.

Risks: Signal handlers call functions that are not strictly async-signal-safe, which is common in libfuse but still a robustness risk. The global session pointer is awkward for multiple simultaneous sessions. Handler removal can log "unknown session" if sessions are removed out of order. `SIGCANCEL` is intentionally avoided because FUSE worker threads use cancellation-like wakeups around blocking reads.

Test signals: Tests should verify handler install/remove idempotence, preservation of pre-existing non-default handlers, SIGPIPE ignoring, `fuse_session_exit` on teardown signals, failure-signal abort behavior under backtrace-enabled builds, and multi-session ordering warnings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_signals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_uring.c -->
# sources/user-network-fs/libfuse/lib/fuse_uring.c

Purpose: `fuse_uring.c` implements experimental FUSE-over-io_uring transport. It creates per-CPU io_uring queues, registers request buffers with the kernel through `IORING_OP_URING_CMD`, dispatches completed ring entries into the low-level request processor, and commits replies back through the same ring entry.

Important APIs, types, and functions: Internal state types are `struct fuse_ring_pool`, `struct fuse_ring_queue`, and `struct fuse_ring_ent`. Public/internal entry points include `fuse_uring_start`, `fuse_uring_stop`, `fuse_uring_wake_ring_threads`, `send_reply_uring`, `fuse_reply_data_uring`, `fuse_send_msg_uring`, and io_uring-enabled `fuse_req_get_payload`. Key helpers set up SQE command data, queue parameters, fixed file registration, NUMA-local buffers, register/fetch commands, CQE processing, resubmission, CPU affinity, and queue thread startup.

Control flow: `fuse_uring_start` validates queue depth, allocates a ring pool sized by `get_nprocs_conf()` and configured depth, starts one thread per queue, and waits for all threads to initialize. Each thread sets a name and CPU affinity, creates an eventfd, initializes io_uring with SQE128 and larger CQ, registers the FUSE fd as fixed file 0, allocates page-aligned request header and payload buffers, prepares register SQEs plus an eventfd poll SQE, waits on `init_sem`, then repeatedly submits and drains CQEs. Successful CQEs populate an embedded `struct fuse_req`, set `is_uring`, capture the kernel commit id, and call `fuse_session_process_uring_cqe`. Reply helpers copy payload data into the ring entry, set output header fields, and submit `FUSE_IO_URING_CMD_COMMIT_AND_FETCH`.

State and persistence behavior: Ring queues and buffers live for the session's io_uring lifetime. Each ring entry embeds a request object with an extra reference so normal `destroy_req` refuses to free it. `req_commit_id` is per request cycle and must be nonzero. Queue threads run until `se->mt_exited` or eventfd teardown. No filesystem data is persisted.

Dependencies and integration points: It depends on `liburing`, NUMA allocation, Linux scheduler/affinity APIs, eventfd, pthreads, kernel FUSE io_uring command structs from `fuse_kernel.h`, and `fuse_session_process_uring_cqe` in `fuse_lowlevel.c`. It is enabled during `FUSE_INIT` only if the kernel advertises `FUSE_OVER_IO_URING`, the session wants it, and startup succeeds.

Risks: The code is concurrency- and ABI-sensitive: SQE128 command size must fit, fixed-file registration must match the FUSE fd, queue locking differs between queue thread and external reply callers, and cleanup cancels/joins threads while ring resources are live. `fuse_uring_start` calls `fuse_uring_sanity_check` but does not use its return value, so invalid queue depth handling depends on later failures. `fuse_uring_queue_handle_cqes` returns `num_completed` for errors rather than the negative error in some cases, which may obscure failures. CPU affinity by qid can fail on systems with sparse or restricted CPU sets.

Test signals: Tests should cover disabled builds, queue depth zero, startup failure cleanup, kernel `EAGAIN`/`EINTR` resubmission, eventfd teardown, payload oversize replies, write_buf dispatch, notify reply dispatch, commit id validation, and fallback from `FUSE_INIT` when ring startup fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_uring_i.h -->
# sources/user-network-fs/libfuse/lib/fuse_uring_i.h

Purpose: `fuse_uring_i.h` is the internal interface between low-level session code and the optional io_uring transport implementation.

Important APIs, types, and functions: It defines default session options `SESSION_DEF_URING_ENABLE` and `SESSION_DEF_URING_Q_DEPTH`, declares `fuse_session_process_uring_cqe`, and, when `HAVE_URING` is true, declares `fuse_uring_start`, `fuse_uring_wake_ring_threads`, `fuse_uring_stop`, `send_reply_uring`, `fuse_reply_data_uring`, and `fuse_send_msg_uring`. Without `HAVE_URING`, it provides inline stubs returning `-ENOTSUP` or doing nothing.

Control flow: Compile-time conditionals select real prototypes or no-op stubs. This lets `fuse_lowlevel.c` call io_uring hooks without wrapping every call site in preprocessor conditionals.

State and persistence behavior: The header owns no state. Defaults influence initial `se->uring` values during session creation.

Dependencies and integration points: It includes `fuse_config.h`, `fuse_lowlevel.h`, and `fuse_kernel.h`, plus `util.h` for `FUSE_VAR_UNUSED` in non-uring builds. The real implementation is `fuse_uring.c`, and the main caller is `fuse_lowlevel.c` during INIT negotiation, reply sending, and CQE dispatch.

Risks: Header/implementation signature drift would break optional builds. Returning `-ENOTSUP` in stubs must be tolerated by callers. Defaults currently disable io_uring unless environment or options enable it, so tests must verify both paths.

Test signals: Build matrix coverage with `HAVE_URING=true` and false is essential. Runtime tests should assert no-uring builds link and report unsupported behavior cleanly while uring builds wire the real functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/fuse_uring_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/helper.c -->
# sources/user-network-fs/libfuse/lib/helper.c

Purpose: `helper.c` implements convenience entry points for standalone high-level FUSE programs: command-line parsing, default subtype/fsname handling, daemonization, mount/session setup, loop selection, service-mode main flow, and connection option parsing.

Important APIs, types, and functions: Public APIs include `fuse_cmdline_help`, versioned `fuse_parse_cmdline` implementations, `fuse_main_real_versioned`, compatibility `fuse_main_real_30`, service-mode `fuse_service_main_real_versioned`, `fuse_apply_conn_info_opts`, `fuse_parse_conn_info_opts`, and `fuse_open_channel`. Internal option tables are `fuse_helper_opts` and `conn_info_opt_spec`, with `struct fuse_conn_info_opts` carrying parsed capability and numeric connection settings.

Control flow: Normal `fuse_main_real_versioned` parses args, handles help/version, validates mountpoint, starts early daemonization when needed, creates the high-level `struct fuse`, mounts it, installs signal handlers, marks daemonization success, runs single-threaded or multithreaded loop, then unmounts/destroys and frees args. Service mode parses service command lines, creates a high-level fuse object, configures loop settings, installs signals, asks `fuse_service_session_mount` to perform remote mount protocol, sends goodbye, releases the service, and runs the selected loop. Connection options parse into `fuse_conn_info_opts` and are later applied by setting/unsetting capability bits on `struct fuse_conn_info`.

State and persistence behavior: The helper mutates `struct fuse_args`, allocates/frees `opts.mountpoint`, starts daemonization state through `fuse_daemonize_*`, installs process signal handlers, and creates/destroys FUSE session/high-level objects. It does not persist filesystem data.

Dependencies and integration points: It connects `fuse_opt.c`, high-level `fuse.c`, low-level session APIs, mount utilities, daemonization helpers, signal handlers, multithreaded loop config, and optional service-mount APIs. It is the main bridge used by applications that call `fuse_main`.

Risks: Error-path result codes are user-visible and historically significant. Argument ownership is delicate because parsing may allocate and rewrite argv. Daemonization success must align with mount/init success. Service mode has extra release/goodbye paths and must avoid double-cleanup. The source currently shows a duplicated `fuse_helper_opt_proc_service) == -1)` line in the service parse block, which appears syntactically suspicious and should be caught by build tests.

Test signals: Tests should cover help/version paths, missing/bad mountpoints, default subtype/fsname insertion, debug implying foreground, loop config settings, daemonization early success/failure, signal handler failure cleanup, service-mode parse/mount/release paths, and connection option capability toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/meson.build -->
# sources/user-network-fs/libfuse/lib/meson.build

Purpose: `lib/meson.build` defines how the `fuse3` shared library is assembled, which platform-specific source files and optional features are included, what dependencies are linked, and how pkg-config metadata is generated.

Important APIs, types, and functions: It declares `libfuse_sources`, conditionally appends mount backends, service implementation or stub, iconv module, io_uring implementation, and optional libraries. It builds `library('fuse3', ...)` with version script linkage, `FUSE_USE_VERSION=319`, and `FUSERMOUNT_DIR`. It emits a `fuse3` pkg-config file and a Meson dependency object `libfuse_dep`.

Control flow: Meson conditionals select Linux vs BSD mount code, new mount API source, service-mount source vs stub, iconv support and optional `libiconv`, io_uring support with `liburing` and `numa`, dynamic loading, NetBSD perfuse/puffs, or `rt`. If service-mount is enabled it also adds pkg-config variables for service socket directory and permissions.

State and persistence behavior: This is build-time state only. It controls which compiled objects and dependency metadata persist in build outputs and installed pkg-config files.

Dependencies and integration points: It integrates configuration probes from `private_cfg`, project version variables, `include_dirs`, `base_version`, `service_socket_perms`, the linker version script, and platform dependency discovery. Its source selection directly determines whether `fuse_service.c`, `fuse_service_stub.c`, `modules/iconv.c`, and `fuse_uring.c` are part of the library.

Risks: Missing conditional dependencies will produce link failures only in specific feature matrices. `libraries_private` is hardcoded to `-ldl` even though `libdl` is optional, which may be wrong on platforms without libdl. Optional iconv handling must work both when iconv is in libc and when a separate library exists. Version-script link args are GNU-ld-specific and may need platform gating.

Test signals: CI should build Linux, BSD/NetBSD, service/no-service, iconv/no-iconv, uring/no-uring, new-mount-api/no-new-mount-api, and non-GNU linker configurations. Installed pkg-config output should include correct public/private libs and service variables only when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/modules/iconv.c -->
# sources/user-network-fs/libfuse/lib/modules/iconv.c

Purpose: `modules/iconv.c` implements a high-level libfuse stackable module that converts file paths and directory entry names between a user-facing charset and the underlying filesystem charset.

Important APIs, types, and functions: `struct iconv` stores the next filesystem, a mutex, configured charset strings, and two `iconv_t` converters (`tofs` and `fromfs`). `struct iconv_dh` wraps `readdir` filler state. `iconv_convpath` performs locked conversion with dynamic buffer growth. The module wraps nearly every high-level filesystem operation (`getattr`, `access`, `readlink`, directory ops, create/remove/rename/link, chmod/chown/truncate/utimens, open/read/write/statfs, xattr, locks, bmap, lseek, statx). `iconv_init`, `iconv_destroy`, `iconv_help`, `iconv_opt_proc`, and `iconv_new` handle lifecycle and options. `FUSE_REGISTER_MODULE(iconv, iconv_new)` registers the module.

Control flow: For path-based operations, the wrapper converts incoming paths from presentation encoding to filesystem encoding, calls the corresponding `fuse_fs_*` operation on `ic->next`, then frees converted paths. `readlink` and `readdir` convert returned link targets or names back from filesystem encoding before returning to the caller. Module creation parses `from_code` and `to_code`, defaults from UTF-8 to current locale codeset, opens both iconv directions, validates that exactly one lower filesystem is supplied, and creates a `fuse_fs` wrapper.

State and persistence behavior: Converter descriptors and charset strings live for module lifetime and are freed in destroy. A mutex serializes access because `iconv_t` conversion state is mutable. No filesystem data is stored.

Dependencies and integration points: It depends on high-level libfuse stacking APIs, libc/iconv, locale/nl_langinfo, pthread mutexes, and optional `statx`. It is included by Meson only when `HAVE_ICONV` is true and can link either libc iconv or separate libiconv.

Risks: Charset conversion errors return `-EILSEQ`, and path expansion heuristics initially allocate 4x input size but must grow correctly for larger expansions. Locking around shared `iconv_t` is necessary; missing reset on error would poison subsequent conversions, so the error path resets the descriptor. The source currently contains an extra closing brace after `iconv_unlink`, which is a compile-breaking risk if present in the active tree. The error messages in `iconv_open` failure paths appear to swap `from`/`to` in text, which can confuse diagnostics.

Test signals: Tests should mount with different `from_code`/`to_code`, exercise names requiring expansion, invalid byte sequences, readlink/readdir reverse conversion, concurrent path operations, null paths, option help/default locale behavior, and build coverage with and without `HAVE_STATX`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/modules/iconv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/modules/subdir.c -->
# sources/user-network-fs/libfuse/lib/modules/subdir.c

Purpose: `modules/subdir.c` implements a high-level stackable module that exposes an underlying filesystem subtree as the apparent root by prepending a configured base directory to most paths, with optional absolute symlink rewriting.

Important APIs, types, and functions: `struct subdir` stores `base`, `baselen`, `rellinks`, and the next filesystem. `subdir_addpath` builds underlying paths. Symlink helpers `count_components`, `strip_common`, and `transform_symlink` convert absolute symlink targets under the base into relative links when `rellinks` is enabled. The module wraps the same broad high-level operation set as iconv: getattr/access/readlink, directory ops, create/remove/rename/link, metadata updates, file I/O buffers, statfs, xattrs, locks, bmap, lseek, and optional statx. `subdir_new` parses `subdir=`, `[no]rellinks`, validates a single lower filesystem, normalizes the base with a trailing slash, and registers through `FUSE_REGISTER_MODULE`.

Control flow: Each wrapper prepends the base path to incoming paths, calls the corresponding `fuse_fs_*` operation on `d->next`, then frees the generated path. Operations with two destination paths convert both sides. `symlink` intentionally converts only the link location path, not the symlink target. `readlink` may transform absolute returned links into relative paths based on the link's location below the base.

State and persistence behavior: Module state is limited to the base string, its length, the relink flag, and the downstream filesystem pointer. It does not cache file data or directory entries. All generated paths are per-call allocations.

Dependencies and integration points: It depends on high-level libfuse module APIs and is always listed in `libfuse_sources`. It composes with other modules through the `next` filesystem pointer and `fuse_get_context()->private_data`.

Risks: Path joining is simple and assumes libfuse-normalized absolute paths; unusual null paths are allowed by passing NULL through. Symlink rewriting is subtle and must avoid truncation. The source currently shows extra braces in `subdir_rmdir` and `subdir_flock`, which appear syntactically hazardous. There is no explicit path traversal filtering here; security depends on upstream path normalization and the lower filesystem.

Test signals: Tests should cover mandatory `subdir=` validation, trailing slash normalization, root path mapping to base, two-path operations, nullpath handling, absolute and relative symlink reads with `rellinks` and `norellinks`, insufficient output buffer for transformed links, and compile/build coverage for all wrapped operations including statx when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/modules/subdir.c -->
