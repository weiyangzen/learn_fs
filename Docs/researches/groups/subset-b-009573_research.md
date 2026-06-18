# subset-b-009573 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/mount_davfs.c -->
# sources/user-network-fs/davfs2/src/mount_davfs.c

## Purpose
`mount_davfs.c` is the setuid mount helper and daemon launcher for davfs2. It gathers command-line, fstab, configuration, environment, and secrets data into `dav_args`, validates mount permissions and filesystem support directories, initializes WebDAV/cache/kernel modules, forks into daemon mode, writes mount bookkeeping, and drives the FUSE/kernel message loop until unmount or termination.

## Important APIs, Types, and Functions
- `main(int argc, char **argv)`: top-level mount lifecycle. It parses options, drops/reacquires effective root as needed, checks fstab for non-root users, reads config/secrets, prevents duplicate mounts, switches persona, initializes `webdav`, `cache`, and `kernel_interface`, forks, writes mtab/utab in the parent, and runs `dav_fuse_loop()` in the child.
- `dav_user_input_hidden()`: public hidden-input helper used for passwords and client certificate decryption.
- `change_persona()`: permanently changes process group to configured `dav_group` and sets effective uid to `dav_user` or invoking user before daemon final privilege drop.
- `check_dirs()`: validates `/proc/mounts` or mtab/utab usage, creates runtime/cache/config/cert directories, checks ownership/mode constraints, and copies default per-user config/secrets templates.
- `check_fstab()`: for non-root mounts, canonicalizes fstab mountpoints, verifies URL/type/options match the invocation, and requires `user` or `users`.
- `check_permissions()`: enforces that non-root users cannot mount with a foreign uid, must belong to requested gid, and must be in the configured davfs group.
- `parse_commandline()`, `get_options()`, `parse_config()`, `parse_secrets()`: implement precedence across `-o`, config files, secrets files, environment password, and interactive prompts.
- `split_uri()`: davfs-specific URI parser for http/https URLs, default path, host normalization, IPv6 brackets, and no userinfo.
- `write_mtab_entry()` and `save_pid()`: persist runtime bookkeeping.

## Control Flow
The mount starts in the user’s locale, syslogs startup, parses `-o` options plus URL/mountpoint, then verifies it is installed setuid root. It temporarily drops effective root to the invoking uid while reading user-specific policy. Non-root callers must match an fstab entry. Config is read system-first, then user or explicitly supplied config. Directory and permission checks run before secrets so missing private files can be created. Secrets are read system-first as root, then user, then `DAVFS_PASSWORD` and interactive prompts can override.

After duplicate mount and pidfile checks, `change_persona()` sets the group/persona for the future daemon. `dav_init_webdav()`, `dav_init_cache()`, and `dav_init_kernel_interface()` are initialized before fork. Parent writes `/etc/mtab` or util-linux `utab` metadata and exits. Child installs SIGTERM/SIGHUP handlers, permanently drops root with `setuid(daemon_id)`, detaches from terminal with `setsid()` and `/dev/null`, writes a pid file, and enters `dav_fuse_loop(dev, mpoint, buf_size, idle_time, is_mounted, &keep_on_running, debug)`. Shutdown closes cache and WebDAV, removes the pid file, and returns.

## State and Persistence
Global state includes `url`, canonical `mpoint`, Linux `mounts`, `pidfile`, `keep_on_running`, and `got_sigterm`. Persistent state touched by the helper includes per-user `~/.davfs2` config/cache/cert/secrets templates, system runtime directory `DAV_SYS_RUN`, pid files named from mountpoint slashes converted to dashes, optional system cache, `/etc/mtab` or `/var/run/mount/utab`, and davfs cache state through `dav_init_cache()`/`dav_close_cache()`. Secrets are zeroed before free in `delete_args()` and `read_secrets()` zeroes parsed input lines.

## Dependencies and Integration Points
This file integrates with `defaults.h` constants, `util.h` error/canonicalization helpers, Neon utility functions (`ne_concat`, `ne_strdup`, URI defaults), davfs modules `kernel_interface.h`, `cache.h`, and `webdav.h`, system passwd/group databases, fstab/mtab APIs, Linux/FreeBSD mount tables, syslog, termios, and setuid/setgid process APIs. The `dav_args` structure defined in `mount_davfs.h` is the cross-module configuration contract consumed by WebDAV, cache, and kernel layers.

## Risks and Edge Cases
This is security-sensitive setuid code. Ownership/mode checks are extensive but failures in privilege switching or path canonicalization are fatal. `parse_commandline()` reports canonicalization failure using `mpoint` after a NULL return rather than the original path, which can weaken diagnostics. `arg_to_int()` does not require full-string consumption after `strtol`, so values with numeric prefixes may be accepted. `write_mtab_entry()` checks `if (!ld)` after `open()`, so a valid fd 0 would be treated as failure; unlikely after normal stdio state, but still a correctness risk. Shell-free parsing is used for config/secrets, but `umount_davfs.c` uses shell commands separately. Debug logging can expose secrets when `DAV_DBG_SECRETS` is enabled, intentionally but dangerously. Fork-before-mount success means parent/child coordination depends on signals and may leave stale pid/mtab state on rare failures as the header notes.

## Test Signals
Useful tests include URI parsing with schemes, IPv6, missing path, userinfo rejection, and trailing slash behavior; config parser quoting/escaping and mountpoint sections; fstab option equivalence for non-root mounts; secrets precedence and permission failures; no-proxy matching; pidfile naming; duplicate mount detection against mocked mount tables; and daemon lifecycle tests verifying pid file cleanup and signal-triggered graceful shutdown. Security tests should cover wrong owner/mode for secrets/client certs and non-root membership failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/mount_davfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/mount_davfs.h -->
# sources/user-network-fs/davfs2/src/mount_davfs.h

## Purpose
`mount_davfs.h` defines the central `dav_args` configuration structure and public declarations for the davfs2 mount helper. It documents the mount/daemon lifecycle and provides the cross-module contract that `mount_davfs.c`, `webdav.c`, cache, and kernel-interface initialization consume.

## Important APIs, Types, and Functions
- `typedef struct dav_args`: collects almost all parsed configuration, security, network, cache, and debug settings. Comments annotate the expected source of each field and therefore the precedence model.
- `main(int argc, char *argv[])`: declared with a long lifecycle comment describing setuid startup, validation, daemonization, running, and cleanup.
- `dav_user_input_hidden(const char *prompt)`: hidden-input prompt used by mount and WebDAV TLS client certificate handling.

## Control Flow
The header’s lifecycle comment is an architectural map: gather and validate input, initialize kernel/WebDAV/cache modules, fork into parent mount bookkeeping plus daemon loop, then terminate through signal or unmount-driven loop exit and close modules. `dav_args` fields are populated in phases by command line, fstab, system config, user config, secrets, environment, and interactive prompts.

## State and Persistence
`dav_args` carries persistent/runtime decisions: mount options, uid/gid/modes, WebDAV endpoint, certificate and secrets paths, credentials, proxy settings, lock/cookie/redirect behavior, retry and timeout policy, character sets, custom headers, cache directories and sizing, refresh/upload behavior, memory tuning, and debug flags. The struct owns many heap strings that `delete_args()` in `mount_davfs.c` frees and partially zeroes.

## Dependencies and Integration Points
It depends on standard POSIX types (`uid_t`, `gid_t`, `mode_t`, `time_t`, `size_t`) via including translation units. `webdav.h` relies on this type for `dav_init_webdav(const dav_args *)`; cache and kernel modules also take it as initialization input. Defaults are supplied from `defaults.h` and interpreted by the mount helper.

## Risks and Edge Cases
The struct is a broad mutable bag, so initialization completeness is critical. Adding fields requires updates to `new_args()`, `delete_args()`, config parsing, debug logging, and consumers. The comments encode precedence but the type itself cannot enforce it. Credential fields must remain carefully zeroed on free, and ownership transfer for `cl_username` to `username` in `parse_secrets()` is a notable convention.

## Test Signals
Tests should assert that `new_args()` initializes every field consistently with documented defaults, `delete_args()` handles partially initialized structs, and every config/secrets field has a corresponding parser and cleanup path. Integration tests should confirm that WebDAV/cache/kernel modules receive expected values after layered config precedence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/mount_davfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/umount_davfs.c -->
# sources/user-network-fs/davfs2/src/umount_davfs.c

## Purpose
`umount_davfs.c` is the unmount helper for davfs2. It delegates the actual unmount to the platform `umount` command, but waits for the associated `mount.davfs` daemon process to terminate so dirty cached files can be synchronized before the user’s `umount` returns.

## Important APIs, Types, and Functions
- `main(int argc, char **argv)`: parses helper options, canonicalizes the mountpoint, derives the davfs pidfile name, validates that the pid belongs to a `PROGRAM_NAME` process, invokes `umount`, and polls process termination.
- `UMOUNT_CMD`: `"umount -i"` on Linux to avoid recursive helper invocation, `"umount"` on FreeBSD.
- Uses `mcanonicalize_file_name()` from `util.h` and Neon string helpers for concatenation.

## Control Flow
The program accepts version/help options and ignores common `umount` flags passed by the real `umount`. It requires exactly one mountpoint argument. If canonicalization fails, it warns and runs `umount` anyway. Otherwise it converts the canonical mountpoint into the pidfile naming scheme used by `mount_davfs.c`, reads the pid, verifies via `ps -p <pid>` that a matching davfs process exists, then runs `umount`. If unmount succeeds, it prints progress dots while polling `ps` every three seconds until the daemon disappears.

## State and Persistence
The helper reads, but does not remove, the pidfile under `DAV_SYS_RUN`. It constructs shell command strings for both `umount` and `ps`, and its only long-lived state is process existence. Cleanup of pidfile/cache state remains the mount daemon’s responsibility.

## Dependencies and Integration Points
It integrates with the system `umount` tool and process table, davfs runtime pidfile naming, `defaults.h` for directories/program names, `util.h` for fatal/warning behavior, i18n, and Neon allocation/string helpers.

## Risks and Edge Cases
The code uses `system()` and `popen()` with shell-constructed strings. The mountpoint is single-quoted, but embedded single quotes in a path would break shell quoting and could become a command injection vector. `fscanf(file, "%s[0-9]", pid)` does not implement a digit-only scanset as likely intended; it reads a whitespace-delimited token into a fixed 32-byte buffer without width, so malformed pidfiles could overflow. `ps` output is matched by substring for pid and program name, which can be imprecise. If verification fails, it still unmounts and leaves manual cleanup to the user.

## Test Signals
Tests should cover help/version, missing/extra arguments, canonicalization failure fallback, pidfile name parity with `mount_davfs.c`, malformed/missing pidfiles, nonexistent daemon, failed `umount`, and successful wait-loop completion. Security tests should include mountpoints containing quotes or shell metacharacters and overlong pidfile content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/umount_davfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/util.h -->
# sources/user-network-fs/davfs2/src/util.h

## Purpose
`util.h` provides shared fatal/warning macros and a portability wrapper for canonical path resolution. It is included by davfs mount and unmount helpers for consistent diagnostics and fallback behavior on systems without `canonicalize_file_name()`.

## Important APIs, Types, and Functions
- `ERR(fmt, ...)`: fatal diagnostic macro. If `errno != 0`, it calls `errx(EXIT_FAILURE, ...)`; otherwise it writes to stderr and exits.
- `WARN(fmt, ...)`: warning macro. If `errno != 0`, it calls `warnx(...)`; otherwise it writes to stdout.
- `ERR_AT_LINE(filename, lineno, fmt, ...)`: uses GNU `error_at_line()` when available, otherwise prints filename/line and exits.
- `mcanonicalize_file_name(path)`: maps to `canonicalize_file_name` when present, otherwise inline fallback using `realpath()` and `strdup()`.

## Control Flow
The macros immediately emit diagnostics and, for `ERR` and `ERR_AT_LINE`, terminate the process. The canonicalization fallback copies the input into a fixed `PATH_MAX` buffer, calls `realpath(path, buf)`, returns `NULL` on failure, and duplicates the resolved path on success.

## State and Persistence
No persistent state is held. Behavior depends on global `errno`, which callers do not always reset before invoking the macros. Returned canonical paths are heap-allocated and caller-owned.

## Dependencies and Integration Points
The header includes `config.h`, libc headers, locale/error handling headers, `err.h`, and optionally GNU `error.h`. It is used by setuid helpers where fatal errors intentionally stop startup/unmount. Its path wrapper is the normalization primitive for mountpoints, fstab entries, secrets keys that are paths, and unmount pidfile derivation.

## Risks and Edge Cases
`ERR` and `WARN` branch on the current global `errno`, but then call `errx`/`warnx`, which do not append errno text; this may be intentional but is surprising because `errno != 0` does not produce `perror`-style output. Because callers may not clear `errno`, unrelated prior errors can alter diagnostics. The fallback `mcanonicalize_file_name()` uses `realpath(path, buf)` after copying into `buf`; the initial `snprintf` is unnecessary. It requires the target to exist, matching `realpath()` behavior.

## Test Signals
Tests should check diagnostics with `errno` set and clear, `ERR_AT_LINE` formatting on systems with and without GNU `error.h`, and canonicalization success/failure for existing, missing, relative, and overlong paths. Callers should be reviewed for stale `errno` before `WARN`/`ERR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/webdav.c -->
# sources/user-network-fs/davfs2/src/webdav.c

## Purpose
`webdav.c` is davfs2’s Neon-backed WebDAV transport layer. It owns the global HTTP/WebDAV session, TLS/auth/proxy/cookie/header configuration, server capability initialization, path encoding conversion, request execution, lock management, property parsing, file transfer, quota queries, and translation from Neon/HTTP results to filesystem errno values.

## Important APIs, Types, and Functions
- `dav_init_webdav(const dav_args *)`: initializes iconv converters, Neon sockets/session, timeouts, user-agent, redirects, auth callbacks, proxy, TLS trust/client certs, lock store, custom headers, cookies, compression, and property selection.
- `dav_init_connection(path)`: sends OPTIONS, validates WebDAV class 1 unless overridden, registers or disables lock support based on DAV class 2.
- `dav_close_webdav()`: unlocks all stored locks, destroys the session, and shuts down Neon sockets.
- Encoding helpers: `dav_conv_from_utf_8`, `dav_conv_to_utf_8`, `dav_conv_from_server_enc`, `dav_conv_to_server_enc`.
- File/resource operations: `dav_get_collection`, `dav_get_file`, `dav_head`, `dav_put`, `dav_delete`, `dav_delete_dir`, `dav_make_collection`, `dav_move`, `dav_quota`, `dav_set_execute`.
- Lock operations: `dav_lock`, `dav_lock_refresh`, `dav_unlock`, plus private `lock_by_path`, `lock_discover`, `lock_refresh`, and `lock_result`.
- Private callbacks: `auth`, `ssl_verify`, `add_header`, `get_cookies`, `file_reader`, `prop_result`, `quota_result`.
- Error normalization: `get_error()` maps Neon statuses to errno; `get_ne_error()` maps HTTP status codes to errno.

## Control Flow
Initialization builds one global `ne_session` from `dav_args`, then most public operations lazily call `dav_init_connection()` on first use. Paths are escaped using `ne_path_escape()` before requests. `dav_get_collection()` issues a depth-one PROPFIND and `prop_result()` builds a linked list of `dav_props`, normalizing directory slashes, names, etags, modification times, content length, and Apache executable properties. `dav_get_file()` builds a GET with conditional headers, optional decompression, streaming body writes to a cache file, and special redirect handling through a temporary read session. `dav_put()` optionally prechecks with HEAD, applies `If-None-Match`/`If-Match`, uses stored WebDAV locks, uploads by fd, retries after lock discovery on access failure, and refreshes etag/mtime from response or follow-up HEAD.

Locking is conditional on server support and configuration. `dav_lock()` either refreshes existing locks, creates exclusive write locks with configured owner/timeout, or discovers same-owner locks on `EACCES`. `dav_unlock()` removes local lockstore entries on success or benign missing/invalid responses. Shutdown attempts to unlock all tracked resources.

## State and Persistence
Global mutable state includes `session`, request timeouts, `locks`, `owner`, `lock_timeout`, server/proxy credentials, trusted server cert, request behavior flags, property name table, initialization flag, terminal availability, iconv descriptors, Neon debug stream, custom headers, cookie capacity/list, and TLS trust state. Remote persistent effects include WebDAV resource creation/deletion/move/upload, locks, executable properties, and cookie-driven server state. Local persistent effects are downloaded cache file writes through `file_reader()`.

## Dependencies and Integration Points
The module depends heavily on Neon (`ne_session`, auth, SSL, locks, props, redirects, compression, URI/path helpers), libc/POSIX file descriptors and syslog, optional iconv/nl_langinfo, `defaults.h`, `mount_davfs.h` for `dav_args`, and `webdav.h` for exported types. It is consumed by the cache and kernel-facing layers to implement filesystem operations on remote resources.

## Risks and Edge Cases
This file is global-session and not thread-isolated; callers must serialize appropriately or avoid concurrent mounts in one process. Credentials are duplicated into globals and are not visibly scrubbed in `dav_close_webdav()`. `dav_delete_props()` frees a single node only; callers must loop over lists. `dav_get_file()` handles redirects manually for GET only and notes that redirected sessions do not reuse configured client/server cert policy. `create_rd_session()` sets the user-agent on `session` instead of `rd_sess`, likely a bug. `file_reader()` opens with `O_WRONLY | O_TRUNC` but not `O_CREAT`; downloads require an existing cache file. Several fd checks use `<= 0`, treating fd 0 as failure. `dav_put()` can return without closing `fd` if `fstat()` fails. `prop_result()` uses prefix checks that are case-insensitive for paths and then performs duplicate/normalization-sensitive behavior; servers with unusual encoded paths or duplicate names need coverage. Cookie storage ignores attributes and security scope, sending all stored cookies on subsequent requests for the session.

## Test Signals
Unit tests with mocked Neon should cover HTTP-to-errno mapping, OPTIONS capability behavior, no-lock fallback, conditional GET/PUT headers, redirect GET sessions, etag normalization including weak etags, property parsing for directories/files/minimal prop sets, duplicate/slashy names, quota missing-property fallback, lock creation/refresh/discovery/unlock, cookie replacement/capacity, custom header injection, and TLS verification paths with and without terminal. Integration tests need live or simulated WebDAV servers for class 1/2, redirects, broken If-Match behavior, weak etags, gzip, SharePoint href behavior, and quota.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/webdav.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/webdav.h -->
# sources/user-network-fs/davfs2/src/webdav.h

## Purpose
`webdav.h` declares the davfs2 WebDAV transport interface and the `dav_props` result structure used by higher layers to reason about remote resources. It documents the contract for initialization, file/resource operations, locking, quota, encoding conversion, and cleanup.

## Important APIs, Types, and Functions
- `struct dav_props`: linked-list node with unescaped `path`, basename-like `name`, normalized `etag`, `size`, `mtime`, `is_dir`, `is_exec`, and `next`.
- Initialization/cleanup: `dav_init_webdav`, `dav_init_connection`, `dav_close_webdav`, `dav_set_no_terminal`.
- Conversion: `dav_conv_from_utf_8`, `dav_conv_to_utf_8`, `dav_conv_from_server_enc`, `dav_conv_to_server_enc`.
- Resource operations: `dav_get_collection`, `dav_get_file`, `dav_head`, `dav_delete`, `dav_delete_dir`, `dav_make_collection`, `dav_move`, `dav_put`, `dav_quota`, `dav_set_execute`.
- Lock operations: `dav_lock`, `dav_lock_refresh`, `dav_unlock`.
- Error access: `dav_get_webdav_error()`.

## Control Flow
Callers initialize once with `dav_init_webdav(args)`, then either explicitly call `dav_init_connection(path)` or let public operations lazily initialize. Directory listings return caller-owned linked lists. File GET/PUT and metadata methods update caller-provided etag, mtime, length, existence, expiration, and modified flags only on documented success paths. Lock-related operations are no-ops when initialized with `nolocks`.

## State and Persistence
The header exposes no state directly, but all functions operate on `webdav.c` global session state. Returned strings and `dav_props` lists are heap-owned by the caller and must be freed with `dav_delete_props()` node-by-node. Operations mutate remote WebDAV state and local cache files.

## Dependencies and Integration Points
The interface depends on `dav_args` from `mount_davfs.h`, POSIX `off_t`, `time_t`, and `uint64_t`, and is used by davfs cache/kernel operation code. It abstracts Neon-specific details from upper layers by returning errno-style integers.

## Risks and Edge Cases
The contract assumes a single initialized global session; no handle is passed to distinguish multiple sessions. Many output parameters are optional, so callers must preserve old state on error and check return codes. `dav_delete_props()` frees only one list node despite the common list result from `dav_get_collection()`. Header comments mention a `mime` parameter in some places where the signature no longer includes one, indicating stale documentation around `dav_head`/`dav_put`.

## Test Signals
Interface-level tests should verify ownership conventions, optional output parameter handling, no-lock behavior, lazy connection initialization, and that callers free entire property lists. Header/API consistency checks should flag stale comments when signatures change.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/webdav.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/MANIFEST.in -->
# sources/user-network-fs/fusepy/MANIFEST.in

## Purpose
`MANIFEST.in` controls source distribution inclusion for fusepy. It includes README files in package archives.

## Important APIs, Types, and Functions
No runtime APIs are defined. The only packaging directive is `include README*`.

## Control Flow
During Python packaging source distribution creation, setuptools/distutils reads this manifest and includes files matching `README*`.

## State and Persistence
No runtime state. It affects persisted release artifacts by ensuring README documentation is packaged.

## Dependencies and Integration Points
It integrates with Python packaging tools that honor `MANIFEST.in`.

## Risks and Edge Cases
The manifest is minimal; licenses, examples, tests, or other metadata are not included by this directive unless included elsewhere by setup configuration. README glob behavior depends on packaging tool conventions.

## Test Signals
Build an sdist and inspect its file list to confirm expected README files are included and no required ancillary files are omitted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/context.py -->
# sources/user-network-fs/fusepy/examples/context.py

## Purpose
`context.py` is a read-only fusepy example filesystem demonstrating `fuse_get_context()`. It exposes three virtual files, `/uid`, `/gid`, and `/pid`, whose contents reflect the uid, gid, and pid of the process making the current FUSE request.

## Important APIs, Types, and Functions
- `Context(LoggingMixIn, Operations)`: implements a minimal filesystem.
- `getattr(path, fh=None)`: returns directory or read-only regular-file metadata, with current timestamps.
- `read(path, size, offset, fh)`: returns encoded uid/gid/pid values.
- `readdir(path, fh)`: lists `.`, `..`, `uid`, `gid`, `pid`.
- Disabled operations are set to `None` so fusepy does not register them.

## Control Flow
When mounted, FUSE dispatches getattr/read/readdir to `Context`. Each request calls `fuse_get_context()` to fetch kernel-supplied caller identity. The main block parses one `mount` argument, enables debug logging, and mounts foreground read-only with `allow_other=True`.

## State and Persistence
No persistent state is stored. File contents are computed per request from FUSE context and timestamps are current `time()`.

## Dependencies and Integration Points
It depends on fusepy’s `FUSE`, `Operations`, `LoggingMixIn`, `FuseOSError`, and `fuse_get_context`, plus errno/stat/time. It requires a working FUSE mount environment and may require configuration to allow `allow_other`.

## Risks and Edge Cases
`read()` ignores `size` and `offset`, returning full content for every request, which is acceptable for demonstration but not correct general filesystem behavior. `allow_other=True` can fail unless `/etc/fuse.conf` permits it. The example exposes request pid/uid/gid to readers by design.

## Test Signals
Mount the example, read the three files as different users/processes, and verify content matches request context. Also test stat output and partial reads to document demonstration limitations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/context.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/ioctl.c -->
# sources/user-network-fs/fusepy/examples/ioctl.c

## Purpose
`ioctl.c` is a small client utility for the fusepy ioctl example. It opens a file, sends an `_IOWR('M', 1, uint32_t)` ioctl with a user-provided integer, and prints the modified result.

## Important APIs, Types, and Functions
- `M_IOWR`: ioctl command matching `ioctl.py`.
- `main(argc, argv)`: validates `value filename`, converts value with `atoi`, opens the target read-only, calls `ioctl(fd, M_IOWR, &data)`, prints success/failure, closes fd.

## Control Flow
The utility expects exactly two arguments after the program name. It opens the target file, passes a pointer to a 32-bit integer into ioctl, and prints the returned integer after the filesystem increments it.

## State and Persistence
No persistent state is changed by this program directly. It relies on the mounted filesystem’s ioctl handler to mutate the in/out integer buffer.

## Dependencies and Integration Points
It depends on libc, POSIX `open`/`close`, Linux/Unix ioctl macros, and must be run against a file served by `examples/ioctl.py`.

## Risks and Edge Cases
The return value of `open()` is not checked before `ioctl()`, so open failure is reported as ioctl failure and `close(-1)` is attempted. `atoi()` gives no validation or overflow signaling. The `_IOWR` command encoding must match Python’s `ioctl_opt.IOWR()` and platform ioctl layout.

## Test Signals
Compile it, run against `ioctl.py` mounted file, and expect input `100` to print `101`. Also test missing args, nonexistent target, non-numeric values, and command mismatch returning `ENOTTY`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/ioctl.py -->
# sources/user-network-fs/fusepy/examples/ioctl.py

## Purpose
`ioctl.py` is a fusepy in-memory example demonstrating FUSE ioctl callback handling. It creates a simple one-level filesystem and implements one read/write ioctl command that reads a 32-bit integer from the caller buffer, increments it, and writes it back.

## Important APIs, Types, and Functions
- `Ioctl(LoggingMixIn, Operations)`: minimal in-memory filesystem with ioctl support.
- `__init__()`: initializes root metadata, file map, byte data, and fd counter.
- `create()`, `open()`, `getattr()`, `read()`, `readdir()`: basic operations for files.
- `ioctl(path, cmd, arg, fh, flags, data)`: recognizes `IOWR(ord('M'), 1, ctypes.c_uint32)`, copies four bytes from `data`, unpacks little-endian uint32, increments, and writes back. Unknown commands raise `ENOTTY`.

## Control Flow
The example mounts `Ioctl()` in the foreground. Users create a file in the mount, then run the C helper. FUSE dispatches ioctl into Python with a raw pointer. The handler uses `ctypes.memmove()` and `struct` to read/write the caller’s buffer.

## State and Persistence
Filesystem state is process-local memory: `files` metadata, `data` contents, and monotonic `fd`. It is lost on unmount. The ioctl does not persist changes to file data; it only mutates the ioctl argument buffer.

## Dependencies and Integration Points
It depends on fusepy, `ioctl_opt.IOWR`, ctypes, struct, and the companion `ioctl.c` for demonstration. It must run on a platform whose ioctl encoding matches `ioctl_opt`.

## Risks and Edge Cases
The handler assumes `data` points to at least four bytes and uses little-endian unpacking. There is no write method, so data is mostly empty unless extended. `read()` ignores missing path checks and returns from defaultdict. No directory hierarchy or permission checks are implemented.

## Test Signals
Mount, create a file, run the C helper, and assert returned integer increments. Test unknown ioctl command returns `ENOTTY`, multiple created files appear in `readdir`, and unmounted/remounted state is empty.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/ioctl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/loopback.py -->
# sources/user-network-fs/fusepy/examples/loopback.py

## Purpose
`loopback.py` is a fusepy passthrough filesystem. It mirrors operations on a real root directory into a mounted FUSE view, forwarding most filesystem calls to Python `os` functions.

## Important APIs, Types, and Functions
- `Loopback(LoggingMixIn, Operations)`: wraps a real path and serializes read/write using a `Lock`.
- `__call__(op, path, *args)`: rewrites every FUSE path to `self.root + path` before normal dispatch.
- Direct aliases: `chmod`, `chown`, `mkdir`, `mknod`, `open`, `readlink`, `rmdir`, `unlink`, `utimens`.
- Implemented methods: `access`, `create`, `flush`, `fsync`, `getattr`, `link`, `read`, `readdir`, `release`, `rename`, `statfs`, `symlink`, `truncate`, `write`.

## Control Flow
The main block takes `root` and `mount`, constructs `Loopback(realpath(root))`, and mounts it in the foreground with `allow_other=True`. Every incoming operation is path-rewritten before reaching the method. File handles returned by `os.open()` are reused for read/write/flush/release. Read and write operations seek then transfer under `rwlock`.

## State and Persistence
All persistent state is the underlying real filesystem. In-memory state is limited to `root` and a lock. FUSE operations can mutate real files, directories, links, modes, owners, timestamps, and filesystem contents.

## Dependencies and Integration Points
It depends on fusepy and Python `os`, `os.path.realpath`, and `threading.Lock`. It relies on the kernel and underlying filesystem permissions. `allow_other` expands visibility to other users if configured.

## Risks and Edge Cases
Path rewriting by string concatenation assumes FUSE supplies absolute paths beginning with `/`; it does not defend against unusual paths or symlink escape because operations are delegated to the underlying filesystem. `truncate()` opens in text mode `'r+'`, which can be wrong for binary data or Python 3 newline handling. `getxattr` and `listxattr` are disabled. `link()`/`rename()`/`symlink()` argument order is intentionally adapted but easy to misunderstand. The read/write lock serializes only those operations, not metadata mutations.

## Test Signals
Mount over a temp root and compare create/read/write/rename/link/symlink/statfs behavior with direct filesystem operations. Test binary truncate behavior, concurrent reads/writes, permission failures, and `allow_other` configuration errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/loopback.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/memory.py -->
# sources/user-network-fs/fusepy/examples/memory.py

## Purpose
`memory.py` is a simple in-memory fusepy filesystem. It supports one-level files/directories, symlinks, xattrs, chmod/chown, statfs, reads/writes, truncation, rename, and timestamp updates for demonstration.

## Important APIs, Types, and Functions
- `Memory(LoggingMixIn, Operations)`: stores metadata in `self.files`, contents in `self.data`, and a simple fd counter.
- Metadata operations: `getattr`, `chmod`, `chown`, `mkdir`, `rmdir`, `utimens`, `statfs`.
- Data operations: `create`, `open`, `read`, `write`, `truncate`, `unlink`, `rename`.
- Link/xattr operations: `symlink`, `readlink`, `setxattr`, `getxattr`, `listxattr`, `removexattr`.

## Control Flow
Root directory metadata is created at initialization. FUSE calls manipulate dictionaries keyed by full paths. Creating files adds metadata and increments fd. Writes splice bytes at offsets, padding holes with NUL bytes; reads slice content. Directory listing returns every non-root key without hierarchy filtering.

## State and Persistence
All filesystem state is process memory and disappears on unmount. `files[path]` holds stat-like dictionaries and optional `attrs`; `data[path]` holds bytes or symlink targets. Root `st_nlink` is incremented/decremented for mkdir/rmdir.

## Dependencies and Integration Points
It depends on fusepy and standard errno/stat/time collections. It is an example consumer of the high-level `Operations` API and demonstrates dictionary-based stat returns.

## Risks and Edge Cases
It advertises only one-level support but does not strictly enforce it; `readdir('/')` returns stripped full paths for all entries. `rmdir()` does not check `ENOTEMPTY`. `getxattr()`/`removexattr()` return empty/pass for missing attrs instead of ENOATTR. Metadata does not consistently update ctime/mtime on write/truncate/unlink. Symlink target storage may be text while file data is bytes. No permissions or concurrency control are implemented.

## Test Signals
Mount and exercise create/write/read/truncate including sparse offsets, symlink/readlink, xattr round trips, rename, unlink/rmdir, and stat metadata. Tests should document one-level limitations and expected non-POSIX behavior for missing xattrs and non-empty directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/memory.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/memoryll.py -->
# sources/user-network-fs/fusepy/examples/memoryll.py

## Purpose
`memoryll.py` is a low-level fusepy example using `fusell.FUSELL` rather than the high-level `Operations` API. It demonstrates inode-based request/reply handling for an in-memory filesystem.

## Important APIs, Types, and Functions
- `Memory(FUSELL)`: implements low-level callbacks.
- `init()`: initializes inode counter, attrs, data, parent map, and child name maps with root inode 1.
- `create_ino()`: allocates monotonically increasing inode numbers.
- Lookup/metadata: `getattr`, `lookup`, `setattr`.
- Namespace operations: `mkdir`, `mknod`, `readdir`, `rename`.
- File operations: `open`, `read`, `write`.
- Reply helpers from `FUSELL`: `reply_attr`, `reply_entry`, `reply_err`, `reply_open`, `reply_buf`, `reply_readdir`, `reply_write`, and `req_ctx`.

## Control Flow
FUSE low-level callbacks receive request handles and inode numbers. The code looks up attrs or child names, builds reply dictionaries, and explicitly calls reply methods for every path. Create-like operations use `req_ctx(req)` to set uid/gid. `setattr()` applies only fields listed in `to_set`, preserving file type bits for mode changes.

## State and Persistence
State is in-memory and inode-indexed: `attr[ino]`, `data[ino]`, `parent[ino]`, and `children[parent][name]`. It is lost on unmount. Root starts as inode 1 with mode `S_IFDIR | 0o777`.

## Dependencies and Integration Points
It depends on `fusell.FUSELL`, low-level FUSE semantics, stat helpers (`S_IFMT`, `S_IMODE`, `S_IFDIR`), errno, and time. It is an example of raw request/reply integration rather than the high-level fusepy wrapper.

## Risks and Edge Cases
The implementation is intentionally partial. `mknod()` increments the parent directory link count even for non-directories, which is not POSIX-correct. `write()` truncates data after `off + len(buf)` rather than preserving existing suffix, unlike `memory.py`. There is no unlink/rmdir/release, no permission model, no empty-directory checks, and debugging uses `print()` in callbacks. Inode maps can become inconsistent for complex rename cases.

## Test Signals
Low-level tests should mount and exercise lookup/getattr, mkdir/mknod, read/write offsets, readdir offsets, rename across parents, and setattr mode preservation. Compare behavior with `memory.py` to document intentional differences and incomplete POSIX semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/memoryll.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/sftp.py -->
# sources/user-network-fs/fusepy/examples/sftp.py

## Purpose
`sftp.py` is a fusepy example that exposes a remote SFTP server as a FUSE filesystem through Paramiko. It forwards common file and directory operations to `paramiko.SFTPClient`.

## Important APIs, Types, and Functions
- `SFTP(LoggingMixIn, Operations)`: opens SSH/SFTP connections in `__init__`.
- Connection lifecycle: `__init__(host, username=None, port=22)` and `destroy()`.
- Metadata/namespace operations: `getattr`, `chmod`, `chown`, `mkdir`, `rename`, `rmdir`, `symlink`, `readlink`, `truncate`, `unlink`, `utimens`.
- Data operations: `create`, `read`, `write`.

## Control Flow
Main parses optional `-l`, host, and mount. If login is not provided and host contains `user@host`, it splits that into username and host. The filesystem connects using system host keys plus `AutoAddPolicy`, opens SFTP, and mounts foreground with `nothreads=True` and `allow_other=True`. Each read/write opens a remote file, seeks, transfers data, and closes it.

## State and Persistence
Persistent state is entirely remote SFTP server state. Local in-memory state is the SSH client and SFTP client. Changes to remote files, directories, links, modes, owners, and timestamps are immediate server operations.

## Dependencies and Integration Points
It depends on Paramiko for SSH/SFTP and fusepy for mounting. It integrates with SSH host-key files, authentication agents/keys, network connectivity, and remote server permissions.

## Risks and Edge Cases
`AutoAddPolicy` trusts unknown host keys, which is convenient but weakens host authenticity. The example assumes passwordless/key-based login. Each read/write opens and closes a remote file, which is simple but slow. `readdir()` returns encoded byte names while many fusepy examples return strings; this can interact with encoding expectations. `create()` returns `0` instead of a distinct file handle. `nothreads=True` avoids concurrency issues but limits parallelism.

## Test Signals
Test against a disposable SFTP server: mount, list directories, stat files, create/write/read/truncate/rename/unlink, symlink/readlink, chmod/chown if permitted, and connection teardown on unmount. Include host-key behavior and login parsing tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/examples/sftp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/fusepy/fuse.py -->
# sources/user-network-fs/fusepy/fuse.py

## Purpose
`fuse.py` is the core fusepy ctypes binding for libfuse. It discovers and loads the native FUSE library, defines platform-specific C structs and callback prototypes, maps libfuse operations into Python methods, provides error translation and context helpers, and exposes the high-level `FUSE`, `Operations`, `FuseOSError`, `LoggingMixIn`, `fuse_get_context()`, and `fuse_exit()` APIs.

## Important APIs, Types, and Functions
- Platform ctypes definitions: `c_timespec`, `c_utimbuf`, `c_stat`, `c_statvfs`, `fuse_file_info`, `fuse_context`, and `fuse_operations`, with Linux/Darwin/FreeBSD/Windows/Cygwin architecture-specific layouts.
- Library loading: `FUSE_LIBRARY_PATH`, `find_library('fuse')`, Darwin iconv loading, WinFsp registry lookup.
- `fuse_get_context()`: returns `(uid, gid, pid)` from native `fuse_get_context`.
- `fuse_exit()`: asks the native FUSE session to exit.
- `FuseOSError(errno)`: convenience exception for errno-returning operations.
- `FUSE.__init__()`: builds argv/options, wraps implemented operations in ctypes callbacks, installs temporary SIGINT default handling, calls `fuse_main_real`, then raises critical exceptions or runtime errors.
- `FUSE` operation methods: decode paths, handle `raw_fi`, marshal read/write buffers, fill `stat`/`statvfs`, xattr buffers, readdir filler, utimens timespecs, and ioctl pointers.
- `Operations`: default high-level filesystem base class with read-only defaults and documented method contracts.
- `LoggingMixIn`: logs operation entry/exit and exceptions.

## Control Flow
At import time the module determines platform and machine, defines exact struct layouts, loads libfuse, and binds `fuse_get_context.restype`. Constructing `FUSE(operations, mountpoint, ...)` builds command-line options from booleans and key/value kwargs, encodes argv, creates a `fuse_operations` struct, and for each operation field checks if the operations object implements it. Implemented functions are wrapped with `_wrapper()` to convert Python exceptions into negative errno returns. `fuse_main_real()` then owns the event loop until unmount/exit. Individual callbacks decode byte paths, translate file handles from `fuse_file_info`, call `operations(op, ...)`, and marshal return values back to C.

## State and Persistence
Module state includes loaded `_libfuse`, detected `_system`/`_machine`, platform type aliases, and logger. `FUSE` instances retain `operations`, `raw_fi`, encoding, nanosecond time mode, and `__critical_exception` during the native event loop; `operations` is deleted afterward to trigger cleanup. Persistent filesystem state is defined by user-provided `Operations` implementations, not the binding itself.

## Dependencies and Integration Points
The module depends on ctypes, native libfuse or WinFsp, OS/platform detection, signal handling, logging, errno/stat conventions, and user operation classes. It is the integration layer used by all high-level fusepy examples in this subset.

## Risks and Edge Cases
The code is ABI-sensitive: incorrect `c_stat`, `c_statvfs`, or `fuse_file_info` layouts for a platform/architecture can cause memory corruption. Import fails if libfuse cannot be found. The Windows branch imports `sys` only inside the branch but uses it there, which is correct only when that branch executes. `_wrapper()` stores critical `BaseException`s and calls `fuse_exit()` because raising through C callbacks can segfault. Most path decoding assumes valid bytes in the configured encoding. `read()` asserts returned data length <= requested size; assertions may be disabled under optimization. Floating-point timestamps are deprecated unless `operations.use_ns` is set. Callback prototypes target FUSE 2.6-era APIs and may not match newer libfuse ABI changes without compatibility layers.

## Test Signals
Tests should cover import/library discovery with `FUSE_LIBRARY_PATH`, struct size/layout smoke tests per supported platform, option normalization, exception-to-errno conversion, path encoding/optional null path handling, `raw_fi` behavior, read/write buffer marshalling, xattr size-query and ERANGE behavior, readdir names plus attr tuples, utimens float vs nanosecond modes, ioctl pointer forwarding, and critical exception shutdown. Integration tests should mount small `Operations` subclasses and exercise common syscalls through the kernel.
<!-- END_FILE_RESEARCH: sources/user-network-fs/fusepy/fuse.py -->
