# subset-b-009166 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/clientserver.c -->
# sources/sync-backup/rsync/clientserver.c

## Purpose
Implements rsync daemon socket setup and the client side of the rsyncd in-band protocol. It negotiates the `@RSYNCD` greeting, selects/list modules, performs daemon authentication, applies module policy, prepares chroot/uid/gid/security state, runs configured transfer hooks, and hands an accepted module request into the normal sender/receiver server path.

## Important APIs, Types, and Functions
`start_socket_client()` opens a wrapped TCP connection and then calls `start_inband_exchange()` before `client_run()`. `exchange_protocols()` emits and parses daemon greetings, subprotocols, MOTD, and authentication digest lists. `start_inband_exchange()` sends the module name, handles `AUTHREQD`, `OK`, `EXIT`, `@ERROR`, early input, and daemon argument transport. `start_daemon()` is the accepted-connection entrypoint. `rsync_module()` is the main per-module policy and transfer setup routine. `daemon_main()`, `become_daemon()`, and `create_pid_file()` implement inetd/standalone daemon startup. `namecvt_call()` talks to a configured name-converter helper.

## Control Flow
Client flow validates that the remote path starts with a module, extracts optional `user@host`, connects, negotiates daemon protocol, sends module/options, and then enters `client_run()`. Server flow loads daemon config before logging, optionally reads PROXY protocol, pre-resolves DNS when ACLs may need it, applies daemon-level chroot/uid/gid, negotiates protocol, reads optional early input, lists modules or resolves a module name, then enters `rsync_module()`. Module flow checks access/auth, claims max-connection lock slots, resolves uid/gid/group policy, normalizes/chroots into the module path, loads daemon filters, starts early/pre/post/name-converter exec hooks, drops privileges, parses client options, starts multiplexing as needed, and calls `start_server()`.

## State and Persistence Behavior
The file mutates global transfer/daemon state such as `auth_user`, `read_only`, `module_id`, `module_dir`, `module_dirlen`, `full_module_path`, `early_input`, `namecvt_pid`, `daemon_chmod_modes`, `am_daemon`, `am_chrooted`, `am_root`, `sanitize_paths`, `munge_symlinks`, `use_secure_symlinks`, `numeric_ids`, `tmpdir`, and logging flags. Persistent process effects include pid-file creation and locking, max-connection lock ranges, environment variables for hooks (`RSYNC_MODULE_NAME`, `RSYNC_HOST_*`, `RSYNC_USER_NAME`, `RSYNC_MODULE_PATH`, `RSYNC_PID`, request/arg variables), chroot, setuid/setgid/setgroups, and long-lived helper pipes for name conversion.

## Dependencies and Integration Points
Depends on daemon parameter accessors (`lp_*`), auth helpers, socket helpers, logging, filter parsing, path normalization, secure syscall wrappers, option parsing, protocol setup, multiplexed IO, process helpers, and cleanup/error handling. It integrates with `compat.c` via daemon greeting/subprotocol negotiation and with `exclude.c` via daemon filter construction and `set_filter_dir()`.

## Risks and Test Signals
High-risk areas are daemon path confinement, `/./` chroot split handling, daemon-chroot versus module-chroot symlink defenses, reverse-DNS timing for hostname ACLs, pid-file race protection, hook pipe lifecycle, early-input framing, privilege drop order, max-connection locks, and compatibility with old daemon protocols. Test signals include successful module listing, auth-required and auth-free module access, denied/unknown module errors, chrooted and non-chrooted transfers, `use chroot = no` symlink-race coverage, max-connection exhaustion, pid-file locking, hook failure propagation, and protocol downgrade behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/clientserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/cmd-or-msg -->
# sources/sync-backup/rsync/cmd-or-msg

## Purpose
Small shell helper that runs a command and, on failure, tells the user which configure option can disable the failing feature. It is used as user-facing build/configuration glue rather than runtime rsync logic.

## Important APIs, Types, and Functions
The script takes an option name as `$1`, shifts it off, echoes the command to be executed, runs the remaining arguments as a command via `"${@}"`, and prints `re-run .../configure with --$opt` before exiting 1 if the command fails.

## Control Flow
It derives `srcdir` from `$0`, captures `opt`, shifts, echoes the exact command arguments, executes them, and only enters the diagnostic branch on non-zero exit.

## State and Persistence Behavior
No persistent state is written. Effects are limited to stdout/stderr messages and the wrapped command's side effects.

## Dependencies and Integration Points
Depends on POSIX `/bin/sh`, `dirname`, and the caller passing a valid command. It integrates with configure/build checks that want a consistent fallback message for optional generated artifacts or feature probes.

## Risks and Test Signals
Risks are mostly shell portability and argument handling: an empty command will fail unclearly, and the option text is trusted. Test signals are that a successful wrapped command returns 0 with only the echo, while a failing wrapped command returns 1 and names the expected `configure --<option>` remediation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/cmd-or-msg -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/compat.c -->
# sources/sync-backup/rsync/compat.c

## Purpose
Centralizes protocol compatibility negotiation for rsync peers, including protocol version exchange, feature flags, incremental recursion eligibility, checksum/compression name negotiation, daemon-auth digest negotiation, file-list extra indexes, and old-protocol option constraints.

## Important APIs, Types, and Functions
Exports global negotiation state such as `remote_protocol`, `file_extra_cnt`, `inc_recurse`, `compat_flags`, `use_safe_inc_flist`, `want_xattr_optim`, `proper_seed_order`, `inplace_partial`, `do_negotiated_strings`, and file-extra indexes. `setup_protocol()` is the main entrypoint. `set_allow_inc_recurse()` gates incremental recursion. `parse_compress_choice()`, `get_nni_by_name()`, `get_nni_by_num()`, `get_default_nno_list()`, `validate_choice_vs_env()`, and the static negotiate helpers implement named algorithm negotiation. `output_daemon_greeting()` and `negotiate_daemon_auth()` support rsyncd startup. `get_subprotocol_version()` hides pre-release subprotocols from older protocol choices.

## Control Flow
`setup_protocol()` first assigns file-list extra slots based on selected preservation options, exchanges protocol numbers when needed, validates min/max compatibility, applies old-protocol restrictions, chooses delete timing defaults, sends or reads protocol 30+ compatibility flags, finalizes incremental recursion and symlink/iconv/xattr/varint capabilities, injects partial-dir filters, negotiates checksum and compression strings, exchanges checksum seed, finalizes checksum/compression choices, selects the xattr checksum, emits batch shell metadata, and initializes file-list internals.

## State and Persistence Behavior
This file mutates process-global capability state that downstream sender, receiver, generator, file-list, xattr, checksum, compression, batch, and filter code consumes. It reads environment variables `RSYNC_COMPRESS_LIST` and `RSYNC_CHECKSUM_LIST` to constrain algorithm negotiation. It persists no files itself except indirectly through write-batch setup.

## Dependencies and Integration Points
Depends on `valid_checksums`, `valid_auth_checksums`, compression constants, option globals, filter parsing, batch helpers, checksum initialization, `init_flist()`, and daemon greeting code used by `clientserver.c`. Its file-extra indexes must match file-list serialization/deserialization code.

## Risks and Test Signals
Risks include incompatible feature flags, protocol downgrade mistakes, mismatched checksum/compression lists, environment restrictions that reject valid explicit choices, batch files produced with different capabilities, and incorrect file-extra ordering. Test signals include protocol matrix transfers against older rsyncs, daemon auth negotiation, `--checksum-choice`/`--compress-choice` with environment lists, protocol 29/30/31 option boundaries, batch read/write tests, crtimes rejection without varint flags, and incremental recursion disabled by incompatible delete/delay/prune options.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/configure -->
# sources/sync-backup/rsync/configure

## Purpose
Bootstrap wrapper for rsync configuration. It ensures generated configure artifacts exist, optionally switches into an auto-prepared build directory, and delegates to `configure.sh` with the correct `--srcdir`.

## Important APIs, Types, and Functions
The script computes `dir` from `$0`, invokes `packaging/prep-auto-dir` when run from the source root, calls `prepare-source build` if `configure.sh` is missing, removes a failed generated `configure.sh`, and finally `exec`s `./configure.sh --srcdir="$dir" "$@"`.

## Control Flow
On startup it normalizes an empty `dirname` result to `.`. If run from `.`, it lets `packaging/prep-auto-dir` decide whether to use `build/`. It then requires `configure.sh`, generating it via `prepare-source build` when absent. Failure emits a clear diagnostic and exits. Success replaces the shell process with the real configure script.

## State and Persistence Behavior
May create or update generated source/configure artifacts through `prepare-source`, may `cd build`, and may delete a failed `configure.sh`. It does not itself produce `config.h` or `Makefile`; that is delegated to `configure.sh`.

## Dependencies and Integration Points
Depends on POSIX shell, `packaging/prep-auto-dir`, `prepare-source`, and generated `configure.sh`. It fronts the Autoconf output described by `configure.ac`.

## Risks and Test Signals
Risks are bootstrap recursion/path mistakes, missing generated files, or stale build-directory selection. Test signals include running `./configure` from a clean checkout without `configure.sh`, from a prepared build dir, and from release tarballs where generated files already exist.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/configure.ac -->
# sources/sync-backup/rsync/configure.ac

## Purpose
Autoconf source for rsync's platform and dependency configuration. It discovers compiler features, headers, system calls, libraries, optional compression/checksum/auth features, ACL/xattr/iconv support, daemon defaults, generated build substitutions, and portability replacement functions.

## Important APIs, Types, and Functions
Defines package/config headers, substitutes build variables such as `BUILD_POPT`, `BUILD_ZLIB`, `ROLL_SIMD`, `ROLL_ASM`, `MD5_ASM`, `MAKE_MAN`, `MAKE_RRSYNC`, object-save flags, and generated files (`Makefile`, `lib/dummy`, `zlib/dummy`, `popt/dummy`, `shconfig`). Feature macros include `HAVE_OPENAT2`, `USE_OPENSSL`, `SUPPORT_XXHASH`, `SUPPORT_ZSTD`, `SUPPORT_LZ4`, `SUPPORT_ACLS`, `SUPPORT_XATTRS`, `ICONV_OPTION`, `USE_ICONV_OPEN`, `INET6`, `HAVE_SOCKETPAIR`, `HAVE_SECURE_MKSTEMP`, and many platform probes.

## Control Flow
The script initializes Autoconf, reads `RSYNC_VERSION`, configures debug/profile/coverage/openat2/md2man/maintainer flags, selects default paths (`RSYNC_PATH`, `RSYNCD_SYSCONF`, `RSYNC_RSH`, nobody user/group), probes SIMD and assembler optimizations, handles zlib/popt inclusion, checks crypto/checksum/compression libraries, aborts if required optional-default libraries are missing, probes types/functions/network portability, configures iconv, filesystem semantics, socketpair, ACLs, xattrs, compiler object behavior, and finally emits configured files.

## State and Persistence Behavior
Generates the Autoconf output that produces `config.h`, `Makefile`, `shconfig`, and dummy dependency markers. It records platform choices in preprocessor macros and make substitutions that change compiled runtime behavior, including security-sensitive secure-open and xattr/ACL paths.

## Dependencies and Integration Points
Depends on Autoconf 2.69+, C/C++ compilers, awk/egrep/install/mkdir, optional Perl/Python3, md2man, OpenSSL, xxhash, zstd, lz4, zlib, popt, ACL/xattr system libraries, and platform headers/syscalls. It integrates with almost every C file through `config.h`.

## Risks and Test Signals
Risks include wrong cross-compilation defaults, feature macros enabled without linkable functions, optional dependency failures blocking default builds, insecure fallback selection for openat2/secure mkstemp, and platform-specific ACL/xattr misclassification. Test signals include `autoreconf`/`prepare-source`, clean `./configure`, configured builds with `--disable-*` options, coverage builds, cross-compile cache overrides, Linux and non-Linux hosts, bundled/external zlib and popt, and feature-specific tests for iconv, xattrs, ACLs, openat2 fallback, SIMD, and compression libraries.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/connection.c -->
# sources/sync-backup/rsync/connection.c

## Purpose
Implements daemon max-connection accounting by locking fixed byte ranges in a module lock file.

## Important APIs, Types, and Functions
`claim_connection(char *fname, int max_connections)` returns 1 when a slot is claimed and 0 when the lock file cannot be opened or all slots are locked. It uses `open(O_RDWR|O_CREAT, 0600)` and `lock_range(fd, i*4, 4)` for each possible slot.

## Control Flow
If `max_connections` is 0, the function immediately permits the connection. Otherwise it opens/creates the lock file, scans slot ranges from 0 to `max_connections - 1`, and returns success while intentionally keeping the descriptor open for the process lifetime. If no range can be locked it closes the descriptor, sets `errno = 0`, and returns failure.

## State and Persistence Behavior
Creates or reuses the configured lock file and relies on advisory byte-range locks held by open file descriptors. Lock state is process/kernel state, released when the daemon worker exits or closes the descriptor.

## Dependencies and Integration Points
Used by `clientserver.c` in `rsync_module()` for the daemon `max connections` setting. Depends on `lock_range()` portability wrappers and daemon parameter values from `lp_lock_file()` / `lp_max_connections()`.

## Risks and Test Signals
Risks include filesystems without reliable advisory locking, descriptor leakage expectations, stale lock files that are harmless but confusing, and ambiguous failure handling where open failures are distinguished from capacity by `errno`. Test signals include parallel daemon connections at and above the configured limit, invalid/unwritable lock-file paths, and process exit releasing a slot.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/daemon-parm.awk -->
# sources/sync-backup/rsync/daemon-parm.awk

## Purpose
Generates `daemon-parm.h` from `daemon-parm.txt`, turning declarative daemon parameter definitions into C structs, default values, parameter-table entries, and accessor macros/functions.

## Important APIs, Types, and Functions
The AWK script recognizes `Globals:` and `Locals:` sections and parameter lines beginning with `STRING`, `CHAR`, `PATH`, `INTEGER`, `ENUM`, `OCTAL`, `BOOL`, `BOOLREV`, or `BOOL3`. It emits `global_vars`, `local_vars`, `all_vars`, `Defaults`, `Vars`, `parm_table`, and `FN_*` accessor declarations into `daemon-parm.h`.

## Control Flow
The `BEGIN` block initializes generated-code fragments. Section rules enforce that globals come first and locals follow. Parameter rules normalize public names, strip dashes from C field names, choose C value/accessor types, append struct fields, default initializers, parameter metadata rows, and expanded-string tracking fields for string/path values. The `END` block writes the complete generated header or exits with failure.

## State and Persistence Behavior
Writes `daemon-parm.h` in the current working directory. The generated file is source state for daemon config parsing and accessors but is marked do-not-edit.

## Dependencies and Integration Points
Depends on AWK and the schema in `daemon-parm.txt`. Integrates with daemon configuration code that expects `parm_table`, `Defaults`, `Vars`, and `lp_*` accessors used heavily by `clientserver.c`.

## Risks and Test Signals
Risks are schema drift, malformed section ordering, invalid default C literals, duplicate/ambiguous names after dash stripping, and writing to the wrong current directory. Test signals include regenerating `daemon-parm.h`, compiling all `lp_*` references, and intentionally malformed `daemon-parm.txt` lines producing clear failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/daemon-parm.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/define-from-md.awk -->
# sources/sync-backup/rsync/define-from-md.awk

## Purpose
Extracts documented default value lists from markdown manpage content and writes a generated C header define, currently for default compression suffixes or CVS ignore patterns depending on `hfile`.

## Important APIs, Types, and Functions
The caller passes `-v hfile=NAME` and a markdown input. The script chooses `DEFAULT_DONT_COMPRESS` with `*.` prefixes when `hfile` contains `compress`, otherwise `DEFAULT_CVSIGNORE`. It scans indented quote/list lines matching `^    > [^ ]+$`, strips backticks, accumulates `$2`, and writes `#define ... "..."` to `hfile`.

## Control Flow
`BEGIN` selects the define name and prefix. Matching list lines extend `value_list`. Sentinel conditions stop after `.gz` for compression or `SCCS` for CVS ignore. Any nonmatching line resets `value_list`, making the extraction dependent on contiguous documented lists. `END` writes the generated header or exits with failure if no list was found.

## State and Persistence Behavior
Writes exactly one generated header file named by `hfile`. No other persistent state is maintained.

## Dependencies and Integration Points
Depends on AWK and stable markdown formatting in rsync manpage sources. The generated constants feed runtime defaults for compression exclusions and CVS-style ignore handling.

## Risks and Test Signals
Risks include fragile markdown pattern matching, accidental extraction from the wrong list, sentinel drift, and shell invocation from an unexpected directory. Test signals include regenerating the target headers after manpage edits, checking the defines compile, and verifying defaults match documented lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/define-from-md.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/delete.c -->
# sources/sync-backup/rsync/delete.c

## Purpose
Provides receiver-side delete helpers for removing files/directories, enforcing max-delete limits, honoring filters/perishable rules, optionally making backups, and tracking delete statistics.

## Important APIs, Types, and Functions
`delete_item(char *fbuf, uint16 mode, uint16 flags)` deletes one path, recursively for directories when requested. `delete_dir_contents()` scans and optionally removes directory contents using `get_dirlist()`, local filters, and recursive calls. `get_del_for_flag()` maps file modes to `DEL_FOR_*` flags. Globals include `ignore_perishable`, `non_perishable_cnt`, and `skipped_deletes`.

## Control Flow
For directories, `delete_item()` first calls `delete_dir_contents()` unless the caller already asserts emptiness. `delete_dir_contents()` pushes local filters, gets a directory file list, detects non-perishable protected entries, optionally recurses, adjusts write permission for owned non-writable entries, and calls `delete_item()` for children. Actual deletion uses `do_rmdir_at()` for directories, `make_backup()` or `robust_unlink()` for files, updates `stats`, and reports failures or max-delete limits.

## State and Persistence Behavior
Mutates filesystem contents, backup destinations, file permissions for deletion, `stats.deleted_*`, `skipped_deletes`, and temporary filter state. It respects `max_delete`, `make_backups`, `backup_dir`, and `backup_suffix`.

## Dependencies and Integration Points
Depends on file-list generation, local filter stack from `exclude.c`, syscall wrappers, backup code, logging, and global stats. Used by generator/receiver code when delete modes or make-room operations require removing destination paths.

## Risks and Test Signals
Risks include deleting protected files when filters are wrong, unsafe permission changes, mount-point handling, recursive path buffer overflow assumptions, backup suffix false positives, and max-delete behavior in make-room mode. Test signals include recursive delete with per-dir filters, `--max-delete`, `--backup`, mount-point preservation, non-writable owned files, vanished files, and all `DEL_FOR_*` make-room error messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/errcode.h -->
# sources/sync-backup/rsync/errcode.h

## Purpose
Defines rsync process exit codes shared across the codebase, logs, documentation, and cleanup paths.

## Important APIs, Types, and Functions
The header defines `RERR_OK`, syntax/protocol/file-selection errors, socket/file/stream/message/IPC errors, sibling crash/termination codes, signal/wait/memory/partial/vanished/delete-limit codes, timeout codes, and shell/ssh-style command execution codes `RERR_CMD_*`.

## Control Flow
No executable control flow. The numeric constants are consumed by `exit_cleanup()`, protocol/setup errors, IO errors, daemon startup, and command-launch handling.

## State and Persistence Behavior
No runtime state. The numeric values are externally visible process status and therefore persistent compatibility contracts for scripts and users.

## Dependencies and Integration Points
The comment requires synchronization with string mappings in `log.c` and the EXIT VALUES section in `rsync.yo`. Many source files include these constants indirectly through `rsync.h`.

## Risks and Test Signals
Risks are numeric changes breaking automation, undocumented new codes, or stale log/doc mappings. Test signals include exit-code focused tests for syntax errors, protocol mismatch, socket failure, file IO failure, partial transfer, vanished files, delete limit, timeout, and remote command-not-found/run failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/errcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/exclude.c -->
# sources/sync-backup/rsync/exclude.c

## Purpose
Implements rsync include/exclude/filter rule parsing, matching, transmission, daemon filters, CVS ignores, implied includes from transfer args, per-directory merge files, and local filter stack management.

## Important APIs, Types, and Functions
Global lists are `filter_list`, `cvs_filter_list`, `daemon_filter_list`, and `implied_filter_list`. Public functions include `add_implied_include()`, `implied_include_partial_string()`, `free_implied_include_partial_string()`, `set_filter_dir()`, `push_local_filters()`, `pop_local_filters()`, `change_local_filter_dir()`, `name_is_excluded()`, `check_server_filter()`, `check_filter()`, `rule_template()`, `parse_filter_str()`, `parse_filter_file()`, `get_rule_prefix()`, `send_filter_list()`, and `recv_filter_list()`. Static helpers parse rule tokens, build rules, manage merge-list lifetimes, match wildcard/literal patterns, and report debug decisions.

## Control Flow
Filter setup parses command-line, daemon, CVS, and merge-file rules into linked lists. `add_rule()` normalizes directory suffixes, absolute paths, wildcards, side-specific flags, and per-dir merge list objects. During traversal, `push_local_filters()` updates `dirbuf`, saves inherited merge-list state, loads merge files in the current directory, and `pop_local_filters()` restores previous state. Matching walks daemon filters first, then transfer filters, recursively checking per-dir merge lists and CVS lists. Client/server filter exchange serializes compatible prefixes and elides local-only rules depending on sender/receiver side and protocol.

## State and Persistence Behavior
Maintains process-global linked lists, per-directory inherited filter state, `dirbuf`, `dirbuf_depth`, merge-list parent arrays, `cur_elide_value`, `saw_xattr_filter`, `trust_sender_args`, and `trust_sender_filter`. It reads filter files, `.cvsignore`, `$HOME/.cvsignore`, and `CVSIGNORE`, but does not write persistent files.

## Dependencies and Integration Points
Depends on wildcard matching, path sanitization, current directory/module globals, daemon config (`lp_use_chroot()`), protocol version, IO serialization, logging, and file-list/delete/generator code. `delete.c` uses local filters to decide deletability, and `clientserver.c` builds `daemon_filter_list` from module config.

## Risks and Test Signals
Risks include side-specific rule elision mistakes, daemon filter bypass, unsafe merge-file path handling under sanitized paths, inherited per-dir list lifetime bugs, protocol-incompatible rule prefixes, xattr filter mismatches, and implied-include validation holes. Test signals include command-line include/exclude combinations, `--delete-excluded`, sender/receiver-side hide/protect/risk/show rules, per-dir merge files with no-inherit/exclude-self/CVS modes, daemon filters, sanitized module paths, xattr filters, old protocol filter exchange, and implied include validation for wildcards and relative paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/exclude.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/fileio.c -->
# sources/sync-backup/rsync/fileio.c

## Purpose
Provides low-level file IO helpers for buffered writes, sparse-file creation/update, matched-data skipping for in-place transfers, and mmap-like sliding-window reads implemented with `read()`.

## Important APIs, Types, and Functions
`write_file()` writes all requested bytes, using sparse handling when `sparse_files > 0` and an internal write buffer otherwise. `flush_write_file()` drains the write buffer. `skip_matched()` advances over matching in-place data. `sparse_end()` finalizes sparse writes and truncation/hole punching. `map_file()`, `map_ptr()`, and `unmap_file()` manage `struct map_struct` windows. Static `write_sparse()` tracks leading/trailing zero runs.

## Control Flow
Buffered mode appends to a global write buffer and flushes when full. Sparse mode scans each chunk for leading and trailing zeroes, accumulates seek distance, uses `lseek` or `do_punch_hole()` depending on preallocation position, writes only nonzero middle data, and delays trailing zero handling until later data or `sparse_end()`. Read-window mode aligns requested offsets to 1 KiB, reuses overlap from the prior window when possible, seeks if needed, reads missing bytes, and zero-fills the remainder if the source changes or read fails.

## State and Persistence Behavior
Writes destination files, may punch holes, seek over sparse ranges, truncate files, and allocate/free read/write buffers. Globals include `preallocated_len`, `sparse_seek`, `sparse_past_write`, and static write-buffer state. `map_struct->status` records the first read failure or `ENODATA`.

## Dependencies and Integration Points
Depends on syscall wrappers (`do_lseek`, `do_ftruncate`, `do_punch_hole`), sparse/preallocation feature macros from configure, transfer constants, logging, and cleanup. Used by receiver/sender match-transfer code for basis reads and destination writes.

## Risks and Test Signals
Risks include partial-write handling, stale global write-buffer state across files, sparse holes interacting with preallocated extents, incorrect offset accounting in `skip_matched()`, files changing during reads, and platform differences without `ftruncate`. Test signals include sparse and non-sparse transfers, in-place updates, preallocated sparse files, interrupted writes/reads, truncated source files during transfer, large aligned and unaligned map windows, and final `sparse_end()` file size checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/fileio.c -->
