# Research Group subset-b-009169

This grouped report covers the requested rsync source files in manifest order. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysacls.c -->
# sources/sync-backup/rsync/lib/sysacls.c

## Purpose
`sysacls.c` is rsync's portability layer for filesystem ACL operations. It normalizes several platform-specific ACL APIs behind the `sys_acl_*` interface declared in `sysacls.h`, allowing the higher-level ACL synchronization code to enumerate, create, validate, set, delete, and free ACLs without knowing whether the platform uses POSIX.1e, Tru64, Solaris/UnixWare, HPUX, IRIX, AIX, or macOS ACL semantics.

## Important APIs, Types, and Functions
The exported surface includes `sys_acl_get_entry()`, `sys_acl_get_tag_type()`, `sys_acl_get_info()`, `sys_acl_get_file()`, `sys_acl_get_fd()`, `sys_acl_init()`, `sys_acl_create_entry()`, `sys_acl_set_info()`, `sys_acl_set_access_bits()`, `sys_acl_valid()`, `sys_acl_set_file()`, `sys_acl_set_fd()`, `sys_acl_delete_def_file()`, `sys_acl_free_acl()`, and `no_acl_syscall_error()`. `SAFE_FREE()` is a small local helper. Most functions have separate conditional implementations selected by `HAVE_POSIX_ACLS`, `HAVE_TRU64_ACLS`, `HAVE_UNIXWARE_ACLS`, `HAVE_SOLARIS_ACLS`, `HAVE_HPUX_ACLS`, `HAVE_IRIX_ACLS`, `HAVE_AIX_ACLS`, or `HAVE_OSX_ACLS`.

## Control Flow
The file compiles only under `SUPPORT_ACLS`. POSIX and Tru64 paths are thin wrappers over native calls, with permission bits converted to rsync's read/write/execute bit mask. Solaris, UnixWare, and HPUX allocate synthetic `SMB_ACL_T` buffers, fetch access and default entries with `acl()` loops that handle `ENOSPC`, split or combine default ACL entries for directories, and sort before validation or setting. HPUX adds runtime probing for the `acl()` system call and a local `hpux_acl_sort()` fallback. AIX maps its ACL linked-list structures into rsync's simplified POSIX-like entries and fabricates owner, group, and other entries. macOS maps NFSv4-style extended ACL allow/deny entries and UUID qualifiers into rsync's tag and bit encoding.

## State and Persistence
ACL objects are transient heap allocations, but `sys_acl_set_file()` and `sys_acl_delete_def_file()` persist changes to filesystem metadata. HPUX caches the successful presence check in a static flag. AIX mutates entry access bits while converting between shifted mode-style bits and AIX ACL bits, so callers must not assume entries remain immutable across set operations.

## Dependencies and Integration Points
The file depends on `rsync.h`, `sysacls.h`, platform ACL headers, libc allocation, `stat()`, and platform APIs such as `acl_get_file()`, `acl()`, `statacl()`, `chacl()`, membership UUID conversion, and `acl_set_file()`. It is consumed by rsync ACL preservation code that expects POSIX-like traversal and permission extraction. `no_acl_syscall_error()` feeds higher-level fallback behavior when a filesystem or platform reports unsupported ACLs.

## Risks
The main risk is semantic loss across incompatible ACL models, especially AIX deny entries and macOS extended ACL bits. Several branches use historical platform APIs and custom memory layouts with manual resizing and sorting. Directory updates on Solaris/HPUX rewrite combined access plus default ACL sets, which can race with external ACL changes. Some file-descriptor ACL functions are compiled out, so path-based operations are the real supported path in several branches.

## Test Signals
Strong signals are platform matrix builds with ACL support enabled, round-trip tests preserving named user/group entries, default directory ACLs, mask recalculation, unsupported filesystem errors, and macOS allow/deny ACLs. Regression tests should check that `EINVAL`, `ENOTSUP`, and `ENOSYS` are recognized as no-ACL conditions where intended, and that setting access ACLs on directories does not drop existing default ACLs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysacls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysacls.h -->
# sources/sync-backup/rsync/lib/sysacls.h

## Purpose
`sysacls.h` defines rsync's portable ACL type vocabulary and function prototypes. It maps platform-native ACL tags, entry handles, ACL handles, and ACL type constants into `SMB_ACL_*` names originally inherited from Samba code, giving the rest of rsync a stable interface when `SUPPORT_ACLS` is enabled.

## Important APIs, Types, and Functions
The header conditionally defines `SMB_ACL_TAG_T`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `SMB_ACL_ENTRY_T`. It also defines common tag constants such as `SMB_ACL_USER`, `SMB_ACL_USER_OBJ`, `SMB_ACL_GROUP`, `SMB_ACL_GROUP_OBJ`, `SMB_ACL_OTHER`, and `SMB_ACL_MASK`, plus traversal constants `SMB_ACL_FIRST_ENTRY` and `SMB_ACL_NEXT_ENTRY`. Valid permission bit masks are expressed as `SMB_ACL_VALID_NAME_BITS` and `SMB_ACL_VALID_OBJ_BITS`. The prototypes exactly match the implementation surface in `sysacls.c`.

## Control Flow
There is no runtime flow; compile-time preprocessor branches select the correct platform layout. POSIX and Tru64 use native `acl_t` and `acl_entry_t`. Solaris/UnixWare and HPUX define an expandable struct containing `struct acl acl[1]`. IRIX wraps a native `struct acl *` plus traversal and ownership flags. AIX defines a linked-list entry model and a `new_acl_entry` wrapper around `ace_id`. macOS maps only user and group ACL identities and uses extended ACL constants.

## State and Persistence
The header has no persistent state. Its definitions determine ownership expectations for allocations returned by `sys_acl_get_file()` and `sys_acl_init()`, and the prototypes make `sys_acl_free_acl()` the required release path for all platform variants.

## Dependencies and Integration Points
The header includes system ACL headers when available and uses rsync allocation macros (`new_array`, `realloc_array`) through macro aliases such as `SMB_MALLOC`. It is included by `sysacls.c` and by higher-level ACL transfer code that needs the portable types and function declarations.

## Risks
Because the type definitions are selected entirely at compile time, a misdetected configure macro can produce incompatible ABI assumptions or the hard `#error` path. The AIX branch embeds assumptions about `/usr/include/acl.h` and specific internal structs. macOS exposes a different permission-bit domain from POSIX, so callers must honor the valid-bit masks.

## Test Signals
Compile tests on each supported ACL platform are essential because many branches cannot be covered on a single host. Header-level signals include successful builds with `SUPPORT_ACLS`, detection of `SMB_ACL_NEED_SORT` where expected, and unit or integration tests that compile callers against only this portable API rather than native ACL types.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysacls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysxattrs.c -->
# sources/sync-backup/rsync/lib/sysxattrs.c

## Purpose
`sysxattrs.c` provides rsync's portable extended-attribute syscall wrapper layer. It exposes a Linux-like lget/fget/lset/lremove/llist API while hiding platform differences among Linux, macOS, FreeBSD, and Solaris xattr implementations.

## Important APIs, Types, and Functions
The exported functions are `sys_lgetxattr()`, `sys_fgetxattr()`, `sys_lsetxattr()`, `sys_lremovexattr()`, and `sys_llistxattr()`. Solaris also has the internal helper `read_xattr()` for reading file-backed attributes from a descriptor. macOS defines `GETXATTR_FETCH_LIMIT` to handle resource forks larger than the platform's single-call fetch limit.

## Control Flow
Under `SUPPORT_XATTRS`, preprocessor branches select a platform. Linux is a direct wrapper around `lgetxattr()`, `fgetxattr()`, `lsetxattr()`, `lremovexattr()`, and `llistxattr()`. macOS adds `XATTR_NOFOLLOW` for path operations and loops additional `getxattr()` calls with offsets when a fetch returns exactly 64 MiB but the requested size is larger. FreeBSD wraps `extattr_*` in the user namespace and converts the list format from length-prefixed strings into NUL-terminated strings in place. Solaris treats xattrs as files in an attribute directory, using `attropen()`, `openat(... O_XATTR)`, reads and writes, `unlinkat()`, and directory iteration.

## State and Persistence
The functions do not maintain process state. `sys_lsetxattr()` and `sys_lremovexattr()` persist changes to filesystem xattrs. Solaris operations open temporary descriptors and close them in all normal paths; list operations create a `DIR *` from the xattr directory descriptor.

## Dependencies and Integration Points
The file depends on `rsync.h`, `sysxattrs.h`, platform xattr headers, descriptor I/O, directory traversal, and errno normalization. It is used by rsync's higher-level xattr preservation code, which expects Linux-style size-probe, fetch, list, set, and remove behavior even on non-Linux systems.

## Risks
FreeBSD list conversion is sensitive to malformed kernel output and signals `EINVAL` when lengths overrun. Solaris `sys_lsetxattr()` writes chunks using `size` rather than `size - bufpos`, which deserves scrutiny for partial-write behavior. The macOS 64 MiB loop depends on offset types and only engages when the initial fetch exactly hits the limit. Namespace mismatches can hide non-user attributes on FreeBSD.

## Test Signals
Useful tests include size-probe calls with `value == NULL`, symlink xattrs, values larger than macOS's chunk limit, FreeBSD list conversion with multiple attributes, Solaris attribute read/write/remove, ERANGE retry behavior, and preservation round trips through rsync's `-X` option.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysxattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysxattrs.h -->
# sources/sync-backup/rsync/lib/sysxattrs.h

## Purpose
`sysxattrs.h` declares rsync's portable extended attribute wrapper API and includes the platform headers needed by `sysxattrs.c` when xattr support is enabled.

## Important APIs, Types, and Functions
The header declares `sys_lgetxattr()`, `sys_fgetxattr()`, `sys_lsetxattr()`, `sys_lremovexattr()`, and `sys_llistxattr()`. It also normalizes `ENOATTR` to `ENODATA` on systems where Linux 2.4-style headers lack a distinct `ENOATTR` value.

## Control Flow
There is no runtime control flow. When `SUPPORT_XATTRS` is defined, the header includes one of `<sys/xattr.h>`, `<attr/xattr.h>`, or `<sys/extattr.h>` depending on configure results. When support is not enabled, it intentionally exposes no compatibility API.

## State and Persistence
The header owns no state and performs no persistence. It defines the call contract that implementation functions use to persist xattr changes through platform syscalls.

## Dependencies and Integration Points
The declarations are consumed by xattr transfer code and implemented by `sysxattrs.c`. The API deliberately resembles Linux xattr calls so higher-level rsync logic can use one call shape for path and descriptor xattr operations.

## Risks
The main risk is configuration drift: missing or incorrect `HAVE_*_XATTR_H` and platform xattr macros can leave the implementation without the expected prototypes or constants. The `ENOATTR` alias means callers should treat `ENOATTR` and `ENODATA` consistently but not assume platforms distinguish them.

## Test Signals
Header-level validation is mostly compile coverage across Linux, macOS, FreeBSD, and Solaris configurations. Integration tests should include builds with `SUPPORT_XATTRS` disabled to ensure callers are properly conditionalized.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/sysxattrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/wildmatch.c -->
# sources/sync-backup/rsync/lib/wildmatch.c

## Purpose
`wildmatch.c` implements rsync's shell-style pattern matcher for exclude/include filters and path matching. It supports `?`, `*`, `**`, backslash literals, bracket classes, POSIX character classes, case-insensitive matching, and matching over arrays of path fragments treated as a virtually joined string.

## Important APIs, Types, and Functions
Public functions are `wildmatch()`, `iwildmatch()`, `wildmatch_array()`, and `litmatch_array()`. Internal helpers are `dowild()`, `doliteral()`, and `trailing_N_elements()`. Constants `ABORT_ALL` and `ABORT_TO_STARSTAR` distinguish a hard mismatch from a slash-boundary abort that can still be handled by a `**` wildcard.

## Control Flow
`dowild()` is a recursive matcher that walks pattern and text in tandem. A single `*` does not match slash, while `**` can cross slash boundaries. Character classes handle negation via `!` or `^`, ranges, escapes, and named classes such as `[:alpha:]`. The matcher can consume an array of strings by advancing to the next fragment whenever the current text fragment ends. `wildmatch_array()` optionally restricts matching to trailing path elements or retries the pattern after slash boundaries for "match anywhere below" behavior. `iwildmatch()` toggles the static `force_lower_case` flag around a call to `dowild()`.

## State and Persistence
There is no persistent storage. The static `force_lower_case` flag is process-global and temporarily modified by `iwildmatch()`, which means the matcher is not thread-safe if used concurrently. Optional `wildmatch_iteration_count` state exists under `WILD_TEST_ITERATIONS` for instrumentation.

## Dependencies and Integration Points
The implementation depends on `rsync.h`, ctype-style macros, and rsync's unsigned character typedef. It integrates with filter, include/exclude, daemon module, and file-list logic that need rsync-specific `**` path semantics rather than libc `fnmatch()`.

## Risks
Recursive wildcard matching can be expensive on adversarial patterns with many stars and partial matches. `force_lower_case` only lowercases text, so callers must pass already-normalized patterns for case-insensitive behavior. Slash-special handling is subtle; changing `ABORT_TO_STARSTAR` behavior can break rsync filter semantics. Character-class parsing deliberately aborts malformed classes.

## Test Signals
Tests should cover `*` versus `**`, slash boundaries, `where > 0` trailing element matching, `where < 0` retry-after-slash behavior, arrays split at path separators, bracket negation, escaped characters, POSIX classes, malformed classes, and `iwildmatch()` with uppercase text.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/wildmatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/wildmatch.h -->
# sources/sync-backup/rsync/lib/wildmatch.h

## Purpose
`wildmatch.h` declares the small public interface for rsync's custom wildcard matcher.

## Important APIs, Types, and Functions
The header declares `wildmatch(const char *pattern, const char *text)`, `iwildmatch(const char *pattern, const char *text)`, `wildmatch_array(const char *pattern, const char *const *texts, int where)`, and `litmatch_array(const char *string, const char *const *texts, int where)`.

## Control Flow
There is no control flow in the header. The `where` parameter documented by the implementation determines whole-array matching, trailing path element matching, or slash-boundary retry behavior.

## State and Persistence
The header owns no state. Callers should know that the implementation uses a temporary static case-folding flag for `iwildmatch()`.

## Dependencies and Integration Points
Filter and path-selection code include this header to avoid depending on implementation details. `litmatch_array()` gives callers a cheaper exact-string path matcher with the same virtual-array behavior used by `wildmatch_array()`.

## Risks
The interface exposes only integer truth values and does not report parse errors separately from mismatches. Callers must pass NULL-terminated text arrays to the array functions.

## Test Signals
Compile coverage plus tests that include the header from filter modules are sufficient at the declaration level. Runtime tests belong with `wildmatch.c`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/wildmatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/loadparm.c -->
# sources/sync-backup/rsync/loadparm.c

## Purpose
`loadparm.c` parses rsync daemon configuration parameters and exposes generated `lp_*()` accessors for global and per-module settings. It is based on Samba's loadparm model, trimmed for rsync daemon modules.

## Important APIs, Types, and Functions
Key public functions are `reset_daemon_vars()`, `lp_load()`, `set_dparams()`, `lp_num_modules()`, and `lp_number()`. Important internal helpers include `expand_vars()`, `string_set()`, `copy_section()`, `init_section()`, `strwiEQ()`, `getsectionbyname()`, `add_a_section()`, `map_parameter()`, `set_boolean()`, `do_parameter()`, and `do_section()`. Accessors are generated via `FN_GLOBAL_*` and `FN_LOCAL_*` macros from `daemon-parm.h`.

## Control Flow
`lp_load()` resets `Vars`, starts in the global section, and delegates parsing to `pm_process()` with callbacks. `do_section()` handles real module sections plus special push/pop/reset directives used by include processing. At the first transition out of global scope, it applies command-line daemon parameters from `--dparam`. `do_parameter()` maps a label to `parm_table`, rejects global-only parameters in module sections, expands `%ENV%` references immediately for non-string types, parses the typed value, and stores it in either `Vars.g`, `Vars.l`, or the current module section. `lp_number()` resolves a loaded module by name after parsing.

## State and Persistence
State is process-local: `Vars`, `Defaults`, `Vars_stack`, `section_list`, `iSectionIndex`, and `bInGlobalSection`. String settings are duplicated but intentionally not freed because daemon config is loaded once per long-lived listener or once per forked job. Environment expansion may allocate a replacement string lazily the first time an accessor is called.

## Dependencies and Integration Points
The file depends on `rsync.h`, `itypes.h`, `ifuncs.h`, `default-dont-compress.h`, generated `daemon-parm.h`, `dparam_list`, `pm_process()`, and logging via `rprintf()`. Daemon startup, authentication, logging, module selection, and transfer policy use the generated `lp_*()` accessors.

## Risks
Parsing is sequence-dependent, especially around global-to-module boundaries and include stack restoration. Unknown parameters are logged but ignored during normal load, while syntax-check mode rejects them. Environment expansion has a fixed extra buffer allowance and exits on overflow. The intentional memory leaks are acceptable for current daemon lifecycle assumptions but would matter if configs were reloaded repeatedly in one process.

## Test Signals
Tests should parse configs with global and module sections, duplicate modules, whitespace-insensitive names, invalid section names containing `/`, `--dparam` overrides, boolean reverse and tri-state values, enum values, path slash trimming, `%ENV%` expansion, include push/pop/reset behavior, and syntax-check rejection of unknown parameters.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/loadparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/log.c -->
# sources/sync-backup/rsync/log.c

## Purpose
`log.c` centralizes rsync diagnostics, daemon logging, transfer log formatting, deletion logging, stats snapshots, and exit-code reporting. It bridges local stdout/stderr output, multiplexed protocol messages, daemon log files, and syslog.

## Important APIs, Types, and Functions
Important public functions include `log_init()`, `logfile_close()`, `logfile_reopen()`, `rwrite()`, `rprintf()`, `rsyserr()`, `rflush()`, `remember_initial_stats()`, `log_format_has()`, `log_item()`, `maybe_log_item()`, `log_delete()`, and `log_exit()`. Internal helpers include `rerr_name()`, `logit()`, `syslog_init()`, `logfile_open()`, `filtered_fwrite()`, and `log_formatted()`. Global state includes `stats`, `got_xfer_error`, `output_needs_newline`, and `send_msgs_to_gen`.

## Control Flow
`log_init()` chooses a daemon log file or syslog and handles daemon restarts with changed module settings. `rwrite()` is the core dispatch path: it normalizes log codes, optionally forwards messages to the generator or remote peer, writes daemon logs with recursion protection, selects stdout or stderr, performs charset conversion if iconv is active, filters unsafe characters, and flushes line-ending messages. `rprintf()` and `rsyserr()` format safe bounded messages before calling `rwrite()`. `log_formatted()` expands `%` escapes in stdout and logfile formats using file metadata, stats deltas, daemon client identity, checksums, and itemized change flags.

## State and Persistence
Persistent effects are log-file appends, syslog writes, and protocol message sends. Process state tracks whether logging is initialized, whether the logfile was temporarily closed, initial byte counters for per-item deltas, and whether transfer errors occurred. `log_delete()` keeps a static synthetic `file_struct` for formatting deletion records.

## Dependencies and Integration Points
The file depends on rsync process-role globals, module config accessors (`lp_*()`), IO multiplexing (`send_msg()`), iconv wrappers, file metadata helpers, checksum formatting, and stats collected across sender, receiver, and generator. It is touched by most user-visible rsync operations.

## Risks
Logging runs in error paths, so recursion and buffer bounds are critical. The code includes explicit guards against non-NUL forwarded messages and cumulative `snprintf()` underflow. Format expansion can exit on oversized expansions. Message routing differs by daemon/server/client role and protocol version, so regressions can hide errors from users or break the wire protocol.

## Test Signals
Good tests cover daemon logfile fallback to syslog, logfile reopen after close, truncated long `rprintf()` output, `rsyserr()` bounds, non-printable filtering, UTF-8 and iconv error paths, server message forwarding for old protocol versions, `%i/%o/%f/%n/%L/%C` log format escapes, deletion logging, and `log_exit()` mappings for warning versus error exits.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/main.c -->
# sources/sync-backup/rsync/main.c

## Purpose
`main.c` owns rsync process startup, command-line role selection, local and remote connection setup, client/server transfer orchestration, receiver/generator forking, summary statistics, daemon handoff, batch mode setup, and signal handling.

## Important APIs, Types, and Functions
Key functions are `main()`, `start_client()`, `client_run()`, `start_server()`, `child_main()`, `do_server_sender()`, `do_server_recv()`, `do_recv()`, `do_cmd()`, `get_local_name()`, `check_alt_basis_dirs()`, `handle_stats()`, `output_summary()`, `write_del_stats()`, `read_del_stats()`, `wait_process()`, `wait_process_with_flush()`, `shell_exec()`, and signal handlers such as `sigusr1_handler()`, `sigusr2_handler()`, and `remember_children()`.

## Control Flow
`main()` installs early signal handlers, records uid/gid and umask, sanitizes selected environment variables, resets daemon defaults, parses options, sets batch files, and dispatches to daemon, server, or client mode. `start_client()` interprets hostspecs to decide local copy, remote-shell transfer, daemon-over-shell, or socket daemon transfer, validates remote argument consistency, starts the connection, and calls `client_run()`. `client_run()` negotiates protocol, sends or receives file lists depending on `am_sender`, starts batch IO if needed, transfers files, waits for children, and outputs summaries. Server mode enters `start_server()`, which then calls sender or receiver routines. `do_recv()` forks a receiver child and leaves the parent as generator, splitting protocol streams and coordinating final goodbye messages.

## State and Persistence
The file manages process-global role flags (`am_sender`, `am_receiver`, `am_generator`, `local_server`, `daemon_connection`), pid status caching, start/end times, batch descriptors, cooked/raw argv, uid/gid state, and stats. Persistent effects include directory creation for destinations, file transfers through downstream modules, batch files, and possible privilege changes through `--copy-as`.

## Dependencies and Integration Points
This file integrates nearly all major rsync subsystems: options, daemon config, socket and remote-shell setup, file-list send/receive, filters, IO multiplexing, generator, receiver, sender, batch mode, hard links, logging, progress, and cleanup. It depends on popt, signal APIs, process management, filesystem calls, and platform locale support.

## Risks
The highest-risk areas are process-role transitions, descriptor ownership during receiver/generator split, remote argument validation, destination path decisions, and signal/child-status races. `do_cmd()` contains shell-like parsing for `RSYNC_RSH`; quoting bugs affect remote execution. `get_local_name()` must correctly handle single-file versus directory transfers, dry-run `--mkpath`, daemon filters, and trailing slashes. Signal handlers use restricted cleanup paths and can affect final exit codes.

## Test Signals
Test coverage should include local copy, remote source, remote destination, daemon socket, daemon-over-ssh, `--files-from`, `--read-batch`, `--write-batch`, `--copy-as`, dry-run with `--mkpath`, alternate basis directories, empty source/destination args, multiple remote source validation, receiver/generator shutdown, SIGUSR2 summary behavior, and stats output at multiple verbosity levels.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/match.c -->
# sources/sync-backup/rsync/match.c

## Purpose
`match.c` implements rsync's rolling-checksum block matching on the sender side. It scans the sender's file against checksums supplied by the receiver/generator and emits literal data plus match tokens, while computing the final whole-file transfer checksum.

## Important APIs, Types, and Functions
Public functions are `match_sums()` and `match_report()`. Internal helpers are `build_hash_table()`, `matched()`, and `hash_search()`. Important state includes `updating_basis_file`, `sender_file_sum`, per-file counters (`false_alarms`, `hash_hits`, `matches`, `data_transfer`), and cumulative counters for debug reporting.

## Control Flow
`match_sums()` initializes checksum state, handles append modes by skipping already-present basis data, builds a hash table for receiver checksums when available, and either runs `hash_search()` or sends literal chunks. `build_hash_table()` chooses a traditional 64K hash table or a larger odd table sized for about 80 percent load, then chains sum entries by weak checksum. `hash_search()` rolls the weak checksum byte by byte, checks candidate chains, computes strong sums lazily, prefers adjacent `want_i` matches for run-length token efficiency, and has special alignment logic for in-place updates. `matched()` sends pending literal data and optional match token, updates the running whole-file checksum, advances `last_match`, and emits progress.

## State and Persistence
The matching state is in process memory. Persistent transfer effects are protocol writes through `send_token()` and `write_buf()`. `stats.literal_data` and `stats.matched_data` are updated, and `sender_file_sum` is written to the peer. If the mapped file reports a read error, the final checksum is intentionally corrupted to force receiver-side detection.

## Dependencies and Integration Points
The file depends on rsync checksum routines (`get_checksum1()`, `get_checksum2()`, `sum_init()`, `sum_update()`, `sum_end()`), memory mapping (`map_ptr()`), token IO, progress output, and `stats`. It is called from sender file-transfer code after the receiver's block sums are available.

## Risks
Rolling checksum correctness and offset arithmetic are critical. In-place updates require avoiding matches to basis chunks that have already been overwritten unless they are known same-offset. Hash-chain mutation in that mode changes future candidate searches. Large files rely on table sizing and `OFF_T`/`int32` conversions. Read-error checksum corruption must never accidentally equal the real checksum.

## Test Signals
Tests should verify identical-file tokenization, literal-only transfers, shifted blocks, adjacent match preference, append and append-verify modes, in-place updates with zero blocks, large files using the expanded hash table, progress updates, false alarm counting, and forced checksum mismatch after a read error.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/maybe-make-man -->
# sources/sync-backup/rsync/maybe-make-man

## Purpose
`maybe-make-man` is a build helper that converts one markdown manpage source into generated output when the Python markdown conversion stack works, or falls back to copying a prebuilt manpage where available.

## Important APIs, Types, and Functions
This is a POSIX shell script with no functions. Its inputs are one `NAME.NUM.md` argument, `md-convert`, `rsync-ssl.1.md` as a probe input, and flag files `.md2man-works` and `.md2man-force`.

## Control Flow
The script validates it received exactly one argument, derives `srcdir`, and checks for `.md2man-works`. If the flag is absent, it runs `md-convert --test` against the small `rsync-ssl.1.md` page. Success creates `.md2man-works`. Failure attempts to use an already-generated manpage in the current directory or source directory. If no fallback exists, it exits successfully only for the Samba build farm compatibility file `$HOME/build_farm/build_test.fns`; otherwise it exits with failure. If `.md2man-force` exists, it passes `--force-link-text`; then it invokes `md-convert` on the requested source file.

## State and Persistence
The script persists `.md2man-works` after a successful converter probe and may copy prebuilt manpages into the current build directory. It writes generated files indirectly through `md-convert`.

## Dependencies and Integration Points
It depends on `/bin/sh`, `dirname`, `basename`, `cp -p`, `touch`, and the adjacent `md-convert` script. It integrates with rsync's build system to avoid hard failing when optional Python markdown dependencies are unavailable.

## Risks
The probe result is cached, so dependency changes after `.md2man-works` is created are not rechecked unless the file is removed. Fallback behavior can hide converter problems if stale prebuilt output exists. The build-farm compatibility exception intentionally suppresses a real generation failure.

## Test Signals
Tests should cover successful converter probing, cached flag reuse, forced link-text option, fallback copy from current directory, fallback copy from source directory, missing fallback failure, and the Samba build-farm nonfatal path.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/maybe-make-man -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/md-convert -->
# sources/sync-backup/rsync/md-convert

## Purpose
`md-convert` is a Python 3 documentation generator that converts rsync markdown files into HTML and, for files ending in `.NUM.md`, nroff manpage output. It adds rsync-specific markdown conventions, link-target validation, option-anchor generation, and manpage substitutions.

## Important APIs, Types, and Functions
Top-level functions include `main()`, `parse_md_file()`, `find_man_substitutions()`, `html_via_commonmark()`, `txt2target()`, `manify()`, `htmlify()`, `warn()`, and `die()`. `TransformHtml` subclasses `HTMLParser` and implements `handle_starttag()`, `handle_endtag()`, `handle_data()`, `handle_UE()`, `add_targets()`, and debug output. Important regexes parse filenames, Makefile assignments, version headers, variable references, option dashes, code-target spans, and unsafe anchor characters.

## Control Flow
Argument parsing accepts `--test`, `--dest`, `--force-link-text`, and `--debug`. The script imports `cmarkgfm` first, falling back to `commonmark`; input containing `@USE_GFM_PARSER@` requires cmarkgfm. `parse_md_file()` validates the markdown filename, substitutes version/path variables for manpages, renders markdown to HTML, then feeds the HTML into `TransformHtml`. The parser rewrites HTML while building manpage macros: headings become `.SH`/`.SS`, lists become `.IP`/`.RS`, links become `.UR`/`.UE`, code and emphasis become nroff font escapes, and start-0 ordered lists become description lists. It writes `.html` plus optional extensionless manpage output unless `--test` was requested.

## State and Persistence
Process state includes `env_subs`, parser globals, and `warning_count`. Output files are unlinked before being rewritten. `find_man_substitutions()` reads `version.h`, `Makefile`, git log timestamps, `SOURCE_DATE_EPOCH`, and `RSYNC_OVERRIDE_PREFIX` to produce deterministic manpage headings.

## Dependencies and Integration Points
The script depends on Python 3, `html.parser`, `argparse`, `subprocess`, `cmarkgfm` or `commonmark`, rsync's `version.h`, and the generated `Makefile`. It is invoked by `maybe-make-man` and the build system; `md2man` is a symlink to this same implementation.

## Risks
Link validation is intentionally strict and exits nonzero when warnings are emitted. The HTML-to-manpage transform is stateful and sensitive to parser output shape. Makefile variable expansion assumes referenced variables are already present. The generated anchor scheme must remain stable because documentation links depend on it.

## Test Signals
Tests should run `--test` on a known page, pages requiring GFM, manpage files with substitutions, start-0 description lists, external links with punctuation, duplicate headings, option headings, tables, malformed links, `SOURCE_DATE_EPOCH`, `RSYNC_OVERRIDE_PREFIX`, and warning-to-failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/md-convert -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/md2man -->
# sources/sync-backup/rsync/md2man

## Purpose
`md2man` is a compatibility entry point for rsync's markdown-to-manpage converter. In this source tree it is a symlink to `md-convert`, so invoking `md2man` executes the same Python 3 converter implementation.

## Important APIs, Types, and Functions
The source path itself contributes no independent code beyond the symlink target. Its effective API is the `md-convert` command-line interface: `--test`, `--dest`, `--force-link-text`, `--debug`, and one or more markdown input files.

## Control Flow
At filesystem resolution time, `md2man` resolves to `md-convert`. Runtime behavior then follows `md-convert`: parse arguments, choose a markdown parser, convert each file to HTML and optional nroff, validate links, and write generated outputs.

## State and Persistence
`md2man` stores no independent state. Persistence effects are the same as `md-convert`: generated `.html` files and optional manpage files in the current or destination directory.

## Dependencies and Integration Points
The symlink preserves an older or clearer tool name for build scripts or developer workflows that expect `md2man`. It integrates with the same Python dependencies and rsync documentation inputs as `md-convert`.

## Risks
The key risk is symlink portability in packaging or archive extraction. If a platform or packaging step dereferences, omits, or breaks the symlink, callers using `md2man` fail even though `md-convert` exists. Behavioral changes must be documented against `md-convert` because this path has no separate implementation.

## Test Signals
Validation should include `ls -l` or equivalent packaging checks confirming the symlink target, invocation through `./md2man --test ...`, and build rules that call either name. Content correctness should be tested through the shared `md-convert` behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/md2man -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/mkgitver -->
# sources/sync-backup/rsync/mkgitver

## Purpose
`mkgitver` generates or refreshes `git-version.h` with an `RSYNC_GITVER` macro based on `git describe`, but only when the current repository description looks like an rsync 3.x version tag.

## Important APIs, Types, and Functions
This is a shell script with no functions. It uses `dirname`, `touch`, `git describe --abbrev=8`, `sed`, `diff`, `mv`, and `rm`.

## Control Flow
The script ensures `git-version.h` exists. If the source directory is a git worktree or gitfile, it runs `git describe --abbrev=8`, appends a dash, and filters the result through a sed expression matching `v3.<num>.<num>` with optional `pre<num>` and a following dash. On a valid description, it writes a temporary header defining `RSYNC_GITVER`, compares it to the existing header, and atomically replaces the header only when the content changed.

## State and Persistence
Persistent state is the generated `git-version.h` file. A temporary `git-version.h.new` is removed when unchanged or moved into place when updated.

## Dependencies and Integration Points
The script is used by the build process to embed a git-derived version string. It depends on being run from a build directory where `git-version.h` should be written, while using the script directory to decide whether git metadata exists.

## Risks
The sed pattern is intentionally narrow and ignores non-3.x tags or unusual descriptions. If run outside a git checkout, it leaves the header as-is after touching it. The script does not quote `$srcdir` in all places, so paths containing spaces would be fragile.

## Test Signals
Tests should cover non-git source archives, valid `v3.2.7-...` descriptions, pre-release descriptions, invalid tag names, unchanged header no-op behavior, changed header replacement, and build-directory invocation separate from source directory.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/mkgitver -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/mkproto.awk -->
# sources/sync-backup/rsync/mkproto.awk

## Purpose
`mkproto.awk` generates `proto.h` from rsync C sources. It extracts function declarations and generated accessor prototypes, preserving an existing file when content has not changed.

## Important APIs, Types, and Functions
The AWK script has `BEGIN`, pattern-action blocks, and `END`. It reads existing `proto.h` into `old_protos`, accumulates `protos`, recognizes `FN_LOCAL_*` and `FN_GLOBAL_*` macro invocations, skips static/extern/semicolon/non-function lines, handles single-line and multi-line function headers, and touches `proto.h-tstamp`.

## Control Flow
In `BEGIN`, it loads current `proto.h` and seeds the generated warning comment. While scanning input, `inheader` mode appends continued function prototype lines until a line ending in `)` is seen, then appends a semicolon. `FN_*` lines are rewritten from macro declarations into actual `lp_*` prototypes, mapping `BOOL`, `CHAR`, `INTEGER`, and `STRING` wrapper syntax to C types and selecting `(int module_id)` for local accessors or `(void)` for globals. Ordinary function headers are appended with semicolons. In `END`, it writes `proto.h` only if content changed and always touches `proto.h-tstamp`.

## State and Persistence
Persistent outputs are `proto.h` and `proto.h-tstamp`. In-memory state is limited to `old_protos`, `protos`, and `inheader`.

## Dependencies and Integration Points
The script is run by `make proto` or old build flows and consumes C source concatenation. It is aware of rsync's loadparm accessor macro naming and keeps generated prototypes in sync with implementation files.

## Risks
The parser is intentionally heuristic. It can miss nonstandard formatting, function pointer declarations, attributes, or return types that do not match the expected leading identifier pattern. It skips all `static` functions, which is intended for public prototypes. Changing accessor macros requires updating this script.

## Test Signals
Tests should feed representative C functions, multi-line prototypes, skipped static and extern declarations, `FN_LOCAL_*` and `FN_GLOBAL_*` accessors of every supported type, unchanged-output no-op behavior, and timestamp creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/mkproto.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/old_versions/build_static.sh -->
# sources/sync-backup/rsync/old_versions/build_static.sh

## Purpose
`old_versions/build_static.sh` builds a statically linked rsync binary from a historical git tag for cross-version behavior testing. It applies best-effort compatibility patches so old rsync releases can build with modern toolchains and glibc.

## Important APIs, Types, and Functions
The script defines `VERSION`, `TAG`, `ARCHIVE_DIR`, `REPO`, `WORKTREE`, `OUT`, `CFLAGS_OLD`, and a `cleanup()` trap. It uses git worktrees, `perl`, `sed`, `autoheader`, `autoconf`, `configure`, `make`, `ldd`, `strip`, and version checks.

## Control Flow
The script validates a version argument, chooses a tag, creates a temporary worktree from `RSYNC_REPO` or a default path, and registers cleanup. It patches old `lseek64()` redeclarations when present. For trees lacking generated `configure`, it marks `OLD_TREE`, neutralizes problematic `AC_LIBOBJ` fallbacks, and regenerates configure files. It configures with bundled zlib and popt, disables OpenSSL if the option exists, forces `HAVE_GETTIMEOFDAY_TZ` when configure misdetects it, generates `proto.h` and stubs `lib/addrinfo.h` for old trees, then builds with static linker flags. It verifies the binary is static and that `rsync --version` matches the requested version before copying, stripping, and printing file information.

## State and Persistence
Persistent output is `old_versions/rsync_<version>`. Temporary state is a git worktree under `/tmp`, `conf.log`, `make.log`, generated configure/proto files inside the worktree, and patches applied only to that detached worktree.

## Dependencies and Integration Points
The script supports archival compatibility testing outside the normal build. It depends on a local rsync git repository, build tools, static libc availability, bundled dependencies, and old source layout conventions.

## Risks
The default `REPO` path is developer-specific and must usually be overridden. Static linking may fail on distributions lacking static libraries. Compatibility patches are regex-based and best-effort. Disabling fortify and downgrading warnings are intentional for historical behavior but reduce hardening. Version verification assumes the third field of `rsync --version` is the version.

## Test Signals
Tests should build known old tags such as 3.1.3 and 3.2.7, exercise a pre-3.0 tree needing autoconf/proto generation, confirm static linkage with `ldd`, confirm version mismatch failure, verify cleanup removes worktrees, and run the produced binary in client and daemon compatibility scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/old_versions/build_static.sh -->
