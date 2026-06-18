# subset-b-009650 Research

Grouped research for selected libfuse public headers and implementation files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_common.h -->
# sources/user-network-fs/libfuse/include/fuse_common.h

## Purpose
`fuse_common.h` is the shared public API surface included indirectly by both high-level and low-level libfuse headers. It defines version macros, ABI-sensitive data structures, connection capability flags, buffer vector abstractions, signal helpers, loop configuration helpers, and feature-flag helpers used throughout libfuse.

## Important APIs, Types, And Functions
Key exported types are `struct fuse_file_info`, `struct fuse_loop_config` or ABI-compatible `struct fuse_loop_config_v1`, `struct fuse_conn_info`, `struct fuse_buf`, `struct fuse_bufvec`, and `struct libfuse_version`. `struct fuse_file_info` carries open flags, file handles, lock owners, cache and direct I/O hints, passthrough `backing_id`, and compatibility fields. `struct fuse_conn_info` carries protocol version, max read/write and background limits, timestamp granularity, passthrough stack depth, interrupt behavior, request timeout, and both legacy 32-bit and extended 64-bit capability masks. Public functions include `fuse_parse_conn_info_opts`, `fuse_apply_conn_info_opts`, `fuse_daemonize`, `fuse_version`, `fuse_pkgversion`, `fuse_pollhandle_destroy`, `fuse_buf_size`, `fuse_buf_copy`, signal handler setup/removal, loop config setters, and `fuse_set_feature_flag`/`fuse_unset_feature_flag`/`fuse_get_feature_flag`.

## Control Flow
The header itself has no executable control flow, but it defines negotiation and dataflow contracts. Applications include it through `fuse.h` or `fuse_lowlevel.h`; the session `init` callback receives `struct fuse_conn_info`; filesystems inspect `capable_ext`, use helper functions to alter `want_ext`, and may apply parsed command-line overrides. I/O reply paths use `fuse_bufvec` with `fuse_buf_copy` to move data among memory buffers, file descriptors, and splice-capable paths.

## State And Persistence
State is per-open-file (`fuse_file_info`), per-connection (`fuse_conn_info`), per-loop (`fuse_loop_config`), and per-buffer copy cursor (`fuse_bufvec.idx`/`off`). No persistent storage is managed here, but capability choices affect kernel cache persistence, writeback behavior, inode invalidation semantics, passthrough backing file lifetimes, and request timeout behavior for the whole mount.

## Dependencies And Integration Points
The header depends on `libfuse_config.h`, `fuse_opt.h`, `fuse_log.h`, standard integer/boolean/system types, and a 64-bit `off_t`. It integrates with the low-level reply/session API, the high-level API, `buffer.c`, signal handling implementation files, daemonization, and kernel protocol constants mirrored from `fuse_kernel.h`.

## Risks
The structures are ABI sensitive; adding fields in the wrong place or changing bitfield widths can break existing binaries. Capability bits span beyond 32 bits, so new code must prefer `capable_ext`/`want_ext` and helper functions over legacy `capable`/`want`. Cache flags such as writeback, explicit invalidation, passthrough, direct-I/O mmap, readdirplus, and no-open support alter kernel behavior substantially and need conservative defaults. The header enforces 64-bit offsets; 32-bit builds need `_FILE_OFFSET_BITS=64`.

## Test Signals
Useful tests include ABI size/layout checks, compile tests for multiple `FUSE_USE_VERSION` values, feature-flag helper tests for 32-bit and extended capability bits, mount option parsing tests for connection overrides, buffer-copy tests via `buffer.c`, and integration tests that validate cache invalidation, writeback, passthrough, no-open/no-opendir, and request-timeout negotiation against supported kernels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_daemonize.h -->
# sources/user-network-fs/libfuse/include/fuse_daemonize.h

## Purpose
`fuse_daemonize.h` exposes the newer early daemonization API used when mount setup and `FUSE_INIT` synchronization require explicit parent/child handshaking. It supplements the older `fuse_daemonize(int foreground)` declaration in `fuse_common.h`.

## Important APIs, Types, And Functions
The public flags are `FUSE_DAEMONIZE_NO_CHDIR` and `FUSE_DAEMONIZE_NO_BACKGROUND`. The functions are `fuse_daemonize_early_start`, `fuse_daemonize_early_success`, `fuse_daemonize_early_fail`, and `fuse_daemonize_early_is_active`. The start call returns `0` or negative errno and may fork unless backgrounding is disabled.

## Control Flow
A filesystem calls `fuse_daemonize_early_start()` before `fuse_session_mount()`. The parent waits for a later success or failure signal. The child continues setup, mounts the session, and then signals success or failure. For synchronous `FUSE_INIT`, success/failure must be sent after mount and before the loop; for asynchronous `FUSE_INIT`, the init callback can call the same success/failure helpers and libfuse decides whether the parent still needs signaling.

## State And Persistence
The API manages process-level daemonization state and a parent/child synchronization channel. It does not persist data, but failure paths can determine the parent process exit code and whether cwd changes to `/`.

## Dependencies And Integration Points
The header uses `<stdint.h>` and `<stdbool.h>`, exports C linkage for C++, and integrates with `fuse_session_mount`, `fuse_session_loop*`, `fuse_session_set_sync_init`, and traditional foreground/background command-line handling.

## Risks
Calling the API after mount, forgetting to signal failure on errors, or mixing it incorrectly with `fuse_daemonize` can leave a parent waiting or report a successful daemon before the mount is usable. `fork()` timing is especially sensitive when synchronous init or io-uring session threads are involved.

## Test Signals
Tests should cover foreground/no-background mode, default background mode, no-chdir behavior, child failure propagation, success after sync mount, async init callback signaling, double success/fail calls, and cleanup when early daemonization was never active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_daemonize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_kernel.h -->
# sources/user-network-fs/libfuse/include/fuse_kernel.h

## Purpose
`fuse_kernel.h` is the userspace copy of the FUSE kernel wire ABI. It defines protocol version 7.45, the request and reply opcodes, capability/init flags, notify codes, ioctl constants, and packed request/reply structures exchanged over `/dev/fuse`, CUSE, and newer io-uring transport paths.

## Important APIs, Types, And Functions
There are no functions. Core wire types include `struct fuse_attr`, `fuse_statx`, `fuse_kstatfs`, `fuse_file_lock`, `fuse_entry_out`, `fuse_attr_out`, `fuse_setattr_in`, `fuse_open_in/out`, `fuse_read_in`, `fuse_write_in/out`, `fuse_init_in/out`, `cuse_init_in/out`, `fuse_in_header`, `fuse_out_header`, `fuse_dirent`, `fuse_direntplus`, notification payloads, passthrough `fuse_backing_map`, DAX mapping structs, security-context extension structs, supplementary group extensions, and `fuse_uring_*` command/header structs. Enumerations include `enum fuse_opcode`, `enum fuse_notify_code`, `enum fuse_ext_type`, and `enum fuse_uring_cmd`.

## Control Flow
The header defines the protocol state machine used by libfuse implementations: the kernel sends `FUSE_INIT`, userspace replies with compatible versions and flags, and later requests use `fuse_in_header` plus opcode-specific payloads. Replies use `fuse_out_header` plus opcode-specific output. Notifications reverse the direction, letting userspace invalidate, store, retrieve, prune, wake pollers, increment epochs, or trigger resend handling. CUSE uses `CUSE_INIT` and `cuse_init_out` for character-device registration. Io-uring mode wraps the same FUSE header concepts in ring command structures.

## State And Persistence
This header does not own state, but its structures define all state crossing the kernel/userspace boundary: inode ids, lookup counts, file handles, lock owners, cache timeouts, open flags, uid/gid/pid context, security context extensions, supplementary groups, DAX mappings, backing file IDs, and request unique IDs. Persistent correctness depends on stable inode/generation pairs and accurate cache timeout/invalidation semantics.

## Dependencies And Integration Points
It depends on Linux-style integer definitions or `<stdint.h>` in userspace. It is included by libfuse internals and CUSE code, and its constants correspond to public capability macros in `fuse_common.h` and low-level callback/reply APIs in `fuse_lowlevel.h`.

## Risks
This file is ABI-critical: field order, padding, sizes, endian expectations, and compatibility constants must match the kernel. New protocol bits beyond bit 31 require correct `flags2` handling. `FUSE_UNIQUE_RESEND`, idmapped uid/gid invalid sentinels, security context extension sizes, and io-uring payload ownership are easy to mishandle. Directory record alignment must stay 64-bit clean for 32-bit userspace on 64-bit kernels.

## Test Signals
Tests should include compile-time size/offset checks against kernel UAPI, protocol negotiation tests for minor-version downgrades, serialization/deserialization tests for every opcode touched by libfuse, directory entry alignment tests, CUSE init tests, passthrough ioctl tests, security-context extension parsing tests, idmap sentinel handling, and io-uring header size/command layout checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_log.h -->
# sources/user-network-fs/libfuse/include/fuse_log.h

## Purpose
`fuse_log.h` defines libfuse's process-global logging API. It lets library code and filesystem applications emit syslog-level messages and replace the default stderr logger with a custom handler or syslog.

## Important APIs, Types, And Functions
`enum fuse_log_level` mirrors syslog severities from emergency through debug. `fuse_log_func_t` is a thread-safe variadic-message callback type receiving a `va_list`. Public functions are `fuse_set_log_func`, `fuse_log`, `fuse_log_enable_syslog`, and `fuse_log_close_syslog`; `fuse_log` has a printf-format attribute.

## Control Flow
Libfuse code calls `fuse_log(level, fmt, ...)`; the currently installed global handler receives the already-classified message. Applications can install a handler before session creation, because parsing and setup paths also emit logs. Passing `NULL` to `fuse_set_log_func` restores the default.

## State And Persistence
The selected log function and syslog state are process-global. No filesystem data is persisted, but syslog mode can outlive an individual session unless closed at teardown.

## Dependencies And Integration Points
The header depends only on `<stdarg.h>` and integrates across virtually all libfuse implementation files, including option parsing, CUSE setup, mount/service helpers, and error paths that must work before a session object exists.

## Risks
The callback must be thread-safe because logs can originate from worker threads. Global handler changes affect all mounted filesystems in the process. Format string mistakes are partly mitigated by compiler attributes, but handler implementations must not retain `va_list` or request-local pointers beyond the call.

## Test Signals
Tests should validate custom handler installation and reset, severity mapping, format attribute warnings in compile tests, concurrent logging behavior, syslog enable/close lifetimes, and early setup errors emitted before a session exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_lowlevel.h -->
# sources/user-network-fs/libfuse/include/fuse_lowlevel.h

## Purpose
`fuse_lowlevel.h` is the main public low-level API for writing FUSE filesystems directly against inode-based request callbacks. It defines request/session types, the callback table, reply functions, notification functions, session lifecycle functions, custom I/O hooks, command-line parsing, request context access, and newer sync-init/io-uring helpers.

## Important APIs, Types, And Functions
Core types are `fuse_ino_t`, `fuse_req_t`, `struct fuse_session`, `struct fuse_entry_param`, `struct fuse_ctx`, `struct fuse_forget_data`, `struct fuse_custom_io`, `enum fuse_notify_entry_flags`, and `struct fuse_lowlevel_ops`. The operation table covers lifecycle (`init`, `destroy`), namespace operations (`lookup`, `forget`, `mknod`, `mkdir`, `unlink`, `rename`, `link`, `create`, `tmpfile`), attributes (`getattr`, `setattr`, `statx`), file and directory I/O, xattrs, locks, ioctl, poll, buffer writes, retrieve replies, readdirplus, copy-file-range, lseek, and syncfs. Reply APIs include `fuse_reply_err`, `fuse_reply_entry`, `fuse_reply_create`, `fuse_reply_attr`, `fuse_reply_open`, `fuse_reply_write`, `fuse_reply_buf`, `fuse_reply_data`, `fuse_reply_iov`, `fuse_reply_ioctl*`, `fuse_reply_poll`, `fuse_reply_lseek`, and `fuse_reply_statx`. Session APIs include `fuse_parse_cmdline`, `fuse_session_new`, mount/unmount/destroy, single and multithreaded loops, custom I/O, FD access, receive/process buffer, sync init, debug, teardown watchdog, and io-uring payload helpers.

## Control Flow
A low-level filesystem constructs `fuse_args`, parses options, creates a `fuse_session` with an operation table and userdata, mounts it, then enters `fuse_session_loop` or `fuse_session_loop_mt`. For each kernel request, libfuse dispatches to one callback with a request handle; the callback must call exactly one valid reply function unless the request is `forget`, `forget_multi`, or `retrieve_reply`. Reply calls release the request. Notifications are asynchronous userspace-to-kernel messages for cache invalidation, poll wakeups, store/retrieve, pruning, and epoch increments.

## State And Persistence
The kernel maintains lookup counts, cache entries, open handles, and pending requests; the filesystem must mirror persistent inode identity and defer deletion until lookup/open references allow it. `fuse_file_info.fh` carries per-open state. `fuse_entry_param` timeouts decide cache persistence. Request context exposes caller uid/gid/pid/umask, security contexts, and supplementary groups. Session state includes mounted file descriptor, exit flag, debug flag, userdata, sync-init configuration, and custom I/O hooks.

## Dependencies And Integration Points
The header includes `fuse_common.h` and standard POSIX headers for `stat`, `statvfs`, `iovec`, `fcntl`, and offsets. It maps public callbacks to the kernel ABI in `fuse_kernel.h`, uses `fuse_bufvec` from `fuse_common.h`, integrates with signal/daemonization helpers, CUSE wrappers, high-level compatibility symbols, and service-mount support.

## Risks
Reply discipline is the main correctness risk: missing, duplicate, or invalid replies can hang callers or corrupt session state. ENOSYS has operation-specific permanent fallback semantics, so accidental ENOSYS can disable future requests. Readdir offsets must be stable across mutation. Lookup counts and NFS export generations need long-lived identity. Cache invalidation notifications can deadlock if called from related operation paths. Writeback cache changes read/write/append/timestamp assumptions. ABI compatibility depends on appending to `struct fuse_lowlevel_ops` only.

## Test Signals
Tests should include callback dispatch/reply matrix coverage, one-reply enforcement, ENOSYS fallback behavior, lookup/forget accounting, readdir offset stability, cache timeout and notification integration, writeback/direct-I/O behavior, xattr and ioctl retry paths, poll handle lifetimes, request context/security context iteration, session mount/loop/unmount lifecycles, multithreaded loop config compatibility, custom I/O, sync init, and io-uring request payload handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_lowlevel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_mount_compat.h -->
# sources/user-network-fs/libfuse/include/fuse_mount_compat.h

## Purpose
`fuse_mount_compat.h` provides portability shims for mount and unmount flag macros on non-BSD platforms whose libc headers may lack Linux `MS_*` or `UMOUNT_*` definitions.

## Important APIs, Types, And Functions
The header exports no functions or types. It conditionally includes `<sys/mount.h>` and defines missing `MS_DIRSYNC`, `MS_NOSYMFOLLOW`, `MS_REC`, `MS_PRIVATE`, `MS_LAZYTIME`, `UMOUNT_DETACH`, `UMOUNT_NOFOLLOW`, and `UMOUNT_UNUSED`.

## Control Flow
Preprocessor checks skip the entire compatibility block on NetBSD, FreeBSD, DragonFly, and GNU/kFreeBSD. On other platforms, missing macros are supplied with Linux UAPI values.

## State And Persistence
There is no runtime state. The constants influence mount namespace behavior such as recursive/private propagation, lazy timestamp updates, symlink-follow policy, and detached unmounts.

## Dependencies And Integration Points
Mount helper implementations can include this header before using Linux mount flags without guarding every macro. It is not installed by `include/meson.build`, so it appears intended for internal or platform-specific build use.

## Risks
Incorrect values would cause mount/unmount semantics to diverge from Linux. The `UMOUNT_UNUSED` sentinel must remain an actually unused high bit. Platform guards must remain aligned with BSD mount APIs to avoid redefining incompatible constants.

## Test Signals
Build tests should cover glibc, musl or other libc variants with missing flags, and BSD targets. Runtime integration should verify mount/private/recursive/lazytime/no-symlink-follow and lazy unmount paths on supported Linux systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_mount_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_opt.h -->
# sources/user-network-fs/libfuse/include/fuse_opt.h

## Purpose
`fuse_opt.h` defines libfuse's reusable option parsing API. It supports parsing command-line arguments and `-o` comma lists into application structs, callback decisions, and rewritten `fuse_args`.

## Important APIs, Types, And Functions
`struct fuse_opt` describes one option template, target offset, and value/key. `FUSE_OPT_KEY` and `FUSE_OPT_END` construct callback-only and sentinel entries. `struct fuse_args` owns an argc/argv pair plus allocation state, initialized by `FUSE_ARGS_INIT`. Special callback keys are `FUSE_OPT_KEY_OPT`, `FUSE_OPT_KEY_NONOPT`, `FUSE_OPT_KEY_KEEP`, and `FUSE_OPT_KEY_DISCARD`. The parser callback type is `fuse_opt_proc_t`. Public functions are `fuse_opt_parse`, `fuse_opt_add_opt`, `fuse_opt_add_opt_escaped`, `fuse_opt_add_arg`, `fuse_opt_insert_arg`, `fuse_opt_free_args`, and `fuse_opt_match`.

## Control Flow
The parser matches arguments against templates. Matches either set integer values, allocate/replace string fields from formatted templates, or call the processing function with a key. Unknown options and non-options also flow through the callback. Callback return values decide whether an argument is retained in the output vector, discarded, or fails parsing.

## State And Persistence
Parser state lives in `struct fuse_args` and caller-provided data structures. `%s` formatted options allocate memory and free previous values at the target offset. `fuse_opt_free_args` releases only argument-vector contents, not the `struct fuse_args` object itself.

## Dependencies And Integration Points
The API is used by `fuse_parse_cmdline`, connection option parsing, CUSE setup, service mount helpers, and applications that need to separate filesystem-specific options from mount options. It exposes C linkage and otherwise avoids heavy dependencies.

## Risks
Offset-based writes require the caller's `data` layout to match templates exactly. `%s` options manage heap ownership and can leak or double-free if callers prepopulate fields incorrectly. Callback return semantics control whether options reach mount helpers, so mistakes can silently drop required flags or pass private flags through. `-o` list parsing and escaping are edge cases.

## Test Signals
Tests should cover exact option matches, `-o` comma-list parsing, two-argument short options, formatted numeric/string writes, unknown option callbacks, non-option handling, keep/discard keys, argument insertion before `--`, escaped comma additions, allocation failure handling, and ownership cleanup by `fuse_opt_free_args`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_service.h -->
# sources/user-network-fs/libfuse/include/fuse_service.h

## Purpose
`fuse_service.h` is the public API for libfuse servers launched under a mount service helper, gated behind `FUSE_USE_VERSION >= 3.19`. It lets a filesystem accept service-provided arguments, request privileged file opens, and ask the service to perform the mount.

## Important APIs, Types, And Functions
The opaque type is `struct fuse_service`. Functions include `fuse_service_accept`, `fuse_service_accepted`, `fuse_service_can_allow_other`, `fuse_service_can_fuseblk`, `fuse_service_release`, `fuse_service_destroy`, `fuse_service_append_args`, `fuse_service_cmdline`, `fuse_service_parse_cmdline_opts`, `fuse_service_request_file`, `fuse_service_request_blockdev`, `fuse_service_receive_file`, `fuse_service_finish_file_requests`, `fuse_service_expect_mount_format`, `fuse_service_session_mount`, `fuse_service_send_goodbye`, and `fuse_service_exit`. `FUSE_SERVICE_REQUEST_FILE_QUIET` suppresses complaints for optional file requests.

## Control Flow
A service-capable server accepts the inherited service channel, appends helper-provided args to its `fuse_args`, parses options without local mountpoint checks, optionally requests file or block-device descriptors from the helper, creates a FUSE session, and calls `fuse_service_session_mount` instead of normal mount and daemonization. On shutdown it sends goodbye, destroys the service context, and uses `fuse_service_exit` to produce the service status.

## State And Persistence
`struct fuse_service` owns the service socket/context and negotiated helper capabilities. It can hold expected mount format state and tracks requested files until `finish_file_requests`. Persistent filesystem data is not managed here, but file descriptors opened by the service can point to persistent backing files or block devices.

## Dependencies And Integration Points
The header includes `fuse_common.h`, forward-declares `struct fuse_cmdline_opts`, and integrates with systemd-style mount.service workflows, low-level sessions, argument parsing, file descriptor passing, and helper policy for `allow_other` and `fuseblk`.

## Risks
The API is version-gated; older `FUSE_USE_VERSION` builds see none of it. Service mode must not call `fuse_daemonize`. Trust boundaries matter because the helper opens files and performs mounts on behalf of the server. Mount format expectations, block-device sizing, and `allow_other`/`fuseblk` capability checks must be enforced consistently.

## Test Signals
Tests should cover no-service fallback, successful accept and argument append, helper capability checks, generated command-line ownership, file and block-device request/receive flows, quiet optional open failures, finish-file-request ordering, mount format validation, service session mount, goodbye/exit status handling, and compile gating around `FUSE_USE_VERSION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_service_priv.h -->
# sources/user-network-fs/libfuse/include/fuse_service_priv.h

## Purpose
`fuse_service_priv.h` defines the private socket protocol between a FUSE server and the mount.service helper. It specifies command/reply magic values, protocol versions, flags, packet layouts, variable-length sizing helpers, and internal service argument names.

## Important APIs, Types, And Functions
Important structs include `fuse_service_memfd_arg`, `fuse_service_memfd_argv`, `fuse_service_packet`, `fuse_service_hello`, `fuse_service_hello_reply`, `fuse_service_simple_reply`, `fuse_service_requested_file`, `fuse_service_fsopen_command`, `fuse_service_open_command`, `fuse_service_string_command`, `fuse_service_mountpoint_command`, `fuse_service_bye_command`, and `fuse_service_mount_command`. Inline helpers validate null termination and compute sizes for variable-length packets. The internal parser hook is `fuse_parse_cmdline_service`.

## Control Flow
The helper sends a hello command with supported protocol range and flags; the server replies with a chosen version. The server then sends commands to open files/block devices, set source/mount options/mountpoint/mtab options, start mount, and say goodbye. The helper replies with simple error packets or requested-file packets and file descriptors through the surrounding socket mechanism.

## State And Persistence
Protocol state includes negotiated version, helper flags (`ALLOW_OTHER`, `FUSEBLK`), requested paths, open flags, create modes, block size, mount flags, expected mountpoint format, and exit code. Numeric fields are documented as network byte order across the socket, so persistent interpretation depends on endian conversions in implementation code.

## Dependencies And Integration Points
The header assumes integer and boolean types are available from including contexts. It backs the public `fuse_service.h` API and integrates with memfd-passed argv data, mount helper IPC, file descriptor passing, and service-specific command-line parsing.

## Risks
Protocol ABI mistakes can break service/server interoperability. Missing endian conversion, failing to verify null termination, accepting oversized packets beyond `FUSE_SERVICE_MAX_CMD_SIZE`, or not validating flags against `FUSE_SERVICE_FLAGS`/`FUSE_SERVICE_*_FLAGS` can create security and compatibility bugs. Variable-length packet size helpers must be used to avoid off-by-one errors.

## Test Signals
Tests should cover hello negotiation boundaries, endian conversions, unknown magic rejection, oversized command rejection, null-termination validation, variable-length size calculations, allowed-flag masks, open/block-device request encoding, mount command encoding, goodbye status, and public API round trips through a fake helper socket.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse_service_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/meson.build -->
# sources/user-network-fs/libfuse/include/meson.build

## Purpose
This Meson build fragment defines which libfuse headers are installed into the public `fuse3` include subdirectory.

## Important APIs, Types, And Functions
It declares `libfuse_headers` with `fuse.h`, `fuse_common.h`, `fuse_lowlevel.h`, `fuse_opt.h`, `cuse_lowlevel.h`, `fuse_log.h`, and `fuse_daemonize.h`. If `private_cfg.get('HAVE_SERVICEMOUNT', false)` is true, it appends `fuse_service.h`. It then calls `install_headers(libfuse_headers, subdir: 'fuse3')`.

## Control Flow
At configure/build time, Meson evaluates the list, conditionally adds service-mount API headers, and registers them for install. There is no runtime control flow.

## State And Persistence
The persistent output is the installed include tree. The conditional service header changes the public SDK surface based on the build configuration.

## Dependencies And Integration Points
This fragment depends on a configured `private_cfg` Meson object and the existence of the listed header files. It integrates with packaging, downstream build systems, pkg-config consumers, and source compatibility for applications including `<fuse3/...>`.

## Risks
Forgetting to install a public header breaks downstream builds. Installing `fuse_service.h` without service-mount support could expose unusable APIs; omitting it when enabled would hide supported functionality. Internal compatibility headers such as `fuse_mount_compat.h` and private service protocol headers are intentionally not installed.

## Test Signals
Build/install tests should verify the installed header set for service-mount enabled and disabled configurations, downstream compile tests with `<fuse3/fuse_lowlevel.h>` and `<fuse3/fuse_daemonize.h>`, and packaging checks that private headers are not installed accidentally.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/buffer.c -->
# sources/user-network-fs/libfuse/lib/buffer.c

## Purpose
`buffer.c` implements the `fuse_buf` and `fuse_bufvec` data movement primitives declared in `fuse_common.h`. It supports memory-to-memory, memory-to-fd, fd-to-memory, fd-to-fd, and optional splice-based copies while maintaining vector cursors.

## Important APIs, Types, And Functions
Exported functions are `fuse_buf_size` and `fuse_buf_copy`. Internal helpers are `min_size`, `fuse_buf_write`, `fuse_buf_read`, `fuse_buf_fd_to_fd`, `fuse_buf_splice`, `fuse_buf_copy_one`, `fuse_bufvec_current`, and `fuse_bufvec_advance`.

## Control Flow
`fuse_buf_copy` loops over the current source and destination buffers, copies the minimum remaining segment with `fuse_buf_copy_one`, advances both vector cursors, and stops on EOF, short copy, exhausted vector, or error. `fuse_buf_copy_one` dispatches by buffer type: memory copies use `memcpy`/`memmove`, memory-to-fd uses `write`/`pwrite`, fd-to-memory uses `read`/`pread`, fd-to-fd uses splice unless disabled/unavailable and falls back to a 4096-byte bounce buffer. Retry flags continue partial fd operations until requested size, EOF, or error.

## State And Persistence
The function mutates `idx` and `off` in both input vectors to reflect consumed bytes. It does not own file descriptors or memory. File-descriptor position is affected for non-`FUSE_BUF_FD_SEEK` buffers; seek buffers use explicit `pread`/`pwrite` offsets.

## Dependencies And Integration Points
The file depends on `fuse_config.h`, `fuse_i.h`, `fuse_lowlevel.h`, libc I/O, errno, asserts, and optional `HAVE_SPLICE`. It backs low-level replies and notifications that move data through `fuse_bufvec`, including zero-copy-capable paths.

## Risks
Short reads/writes are successful partial copies unless retry is set. Errors after partial progress return the copied byte count rather than `-errno`, so callers must understand partial completion. Splice can fail with `EINVAL` for unsupported fd pairs and falls back unless forced. Offset/cursor assertions catch internal misuse but not release builds. Very large size totals saturate to `SIZE_MAX`.

## Test Signals
Tests should cover memory overlap using `memmove`, memory/fd copies with and without seek flags, retry and non-retry short I/O, fd-to-fd splice fallback and forced splice error behavior, vector cursor advancement across multiple buffers, self-copy behavior, EOF handling, partial error semantics, and overflow in `fuse_buf_size`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/compat.c -->
# sources/user-network-fs/libfuse/lib/compat.c

## Purpose
`compat.c` provides ABI compatibility entry points for platforms or builds without versioned symbol support, and permanent forwarding wrappers for historically versioned libfuse 3.0 symbols.

## Important APIs, Types, And Functions
It forward-declares libfuse public structs and wrappers for `fuse_parse_cmdline`, `fuse_session_custom_io`, `fuse_main_real`, and `fuse_session_new`. Conditional wrappers call `fuse_parse_cmdline_30` and `fuse_session_custom_io_30` only when `LIBFUSE_BUILT_WITH_VERSIONED_SYMBOLS` is not defined. The `fuse_main_real` and `fuse_session_new` wrappers always forward to `_30` implementations.

## Control Flow
Wrapper functions have no logic beyond delegation. A preprocessor `#undef fuse_parse_cmdline` avoids macro redirection conflicts while defining the unversioned ABI symbol.

## State And Persistence
No state is owned or persisted. ABI identity is the important persistent contract: downstream binaries linked against unversioned symbols must keep resolving to compatible implementations.

## Dependencies And Integration Points
The file includes `libfuse_config.h` plus standard size/integer headers. It integrates with public header macro redirections in `fuse_lowlevel.h`, the build's versioned-symbol configuration, and dynamic linker ABI compatibility for libfuse consumers.

## Risks
Incorrect wrapper signatures or missing wrappers break binary compatibility. Macro redirection can accidentally rename the symbol being defined if not undefined. Always forwarding to `_30` means the called implementation must preserve old ABI expectations even as newer public APIs add fields or parameters.

## Test Signals
Tests should inspect exported symbols with and without versioned-symbol builds, compile/link old API consumers, call each wrapper through the unversioned name, verify macro conflicts do not affect definitions, and run ABI comparison tooling across releases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/cuse_lowlevel.c -->
# sources/user-network-fs/libfuse/lib/cuse_lowlevel.c

## Purpose
`cuse_lowlevel.c` implements the CUSE low-level setup and session bridge for character devices in userspace. It adapts CUSE operation callbacks to the generic FUSE low-level operation table, performs CUSE init negotiation, opens `/dev/cuse`, and runs the chosen FUSE session loop.

## Important APIs, Types, And Functions
Internal `struct cuse_data` stores copied `cuse_lowlevel_ops`, max read, device major/minor, flags, packed device info length, and flexible `dev_info`. Bridge callbacks include `cuse_fll_open`, `read`, `write`, `flush`, `release`, `fsync`, `ioctl`, and `poll`, all ignoring inode and forwarding to CUSE callbacks. Public/visible functions are `cuse_lowlevel_new`, `_cuse_lowlevel_init`, `cuse_lowlevel_init`, `cuse_lowlevel_setup`, `cuse_lowlevel_teardown`, and `cuse_lowlevel_main`.

## Control Flow
`cuse_lowlevel_setup` parses command-line options, strips `subtype=`, ensures fds 0-2 are open, creates a CUSE-backed FUSE session, opens `/dev/cuse`, installs signal handlers, and daemonizes. `cuse_lowlevel_new` packs device info, builds a `fuse_lowlevel_ops` table with bridge callbacks only for implemented CUSE callbacks, creates the session, and attaches `cuse_data`. During `CUSE_INIT`, `_cuse_lowlevel_init` validates protocol major, clamps max write by buffer size, calls the user init callback, replies with `cuse_init_out` plus packed device info, invokes `init_done`, and frees the request. `cuse_lowlevel_main` runs single or multithreaded loop and tears down.

## State And Persistence
Session state owns `se->cuse_data`, `se->fd`, `se->conn` protocol and max write values, and `se->got_init`. CUSE device identity is provided by major/minor and packed `dev_info` strings. No persistent device data is stored here; user callbacks implement character-device behavior.

## Dependencies And Integration Points
The file includes CUSE and FUSE internal/public headers, `fuse_kernel.h` for CUSE protocol structs, option parsing, signal handling, daemonization, logging, `/dev/cuse`, and FUSE session loops. It depends on `/dev/cuse` availability and the kernel CUSE module.

## Risks
`dev_info` is capped by `CUSE_INIT_INFO_MAX`; oversized data aborts setup. The code notes that clearing `capable_ext`/`want_ext` in CUSE init is not right, so capability handling may lag FUSE behavior. Error paths must free parsed mountpoints/args, destroy sessions, and remove signal handlers in the right order. Missing `/dev/cuse` or closed standard fds are handled explicitly, but daemonization and signal setup failures remain integration-sensitive.

## Test Signals
Tests should cover device info packing and size limit, bridge callback forwarding, optional callback omission, CUSE init protocol rejection for major < 7, max_write clamping by buffer size, init/init_done ordering, `/dev/cuse` open failures, signal/daemonization error unwinding, subtype removal, single vs multithreaded loop selection, and teardown resource cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/lib/cuse_lowlevel.c -->
