# Research Group subset-b-008347

This grouped report covers SELinux `libselinux` policy loading, file/context matching, restorecon, status, translation, and utility entry points plus the top-level `libsemanage` make dispatcher. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/load_policy.c -->
# sources/security-integrity/selinux/libselinux/src/load_policy.c

## Purpose
Loads a binary SELinux policy into the kernel and performs early-init policy setup. It bridges policy files under the configured policy root, `selinuxfs` control files, `/proc/cmdline`, and optional libsepol downgrade support.

## Important APIs, Types, And Functions
`security_load_policy()` writes policy bytes to `<selinux_mnt>/load`. `selinux_mkload_policy()` locates `policy.N`, optionally uses libsepol symbols to downgrade a newer policy to the running kernel policy version, mmaps the file, and calls `security_load_policy()`. `selinux_init_load_policy()` rereads config, mounts `/proc`, `/sys`, and `selinuxfs`, resolves enforcing mode, optionally disables SELinux, sets enforcing state, and invokes the load path.

## Control Flow
Policy selection starts at the max of kernel and libsepol-supported versions, walks down to the minimum supported version, maps the file, and retries older files if downgrade fails. Init loading gives kernel command-line `enforcing=` precedence over `/etc/selinux/config`, then config, then permissive fallback.

## State And Persistence Behavior
Persistent state is in kernel `selinuxfs`: `load` receives the policy image and `enforce` may be changed before policy load. The code temporarily mounts filesystems and may unmount `/proc` or `selinuxfs` after runtime-disable handling.

## Dependencies And Integration Points
Uses `policy.h`, config accessors, `security_policyvers()`, `security_getenforce()`, `security_setenforce()`, `security_disable()`, `set_selinuxmnt()`, and libsepol either linked directly or `dlopen()`ed in shared builds.

## Risks And Test Signals
Key risks are partial `write()` handling, downgrade retry correctness, mount side effects during init, and enforcing-mode precedence. Tests should cover missing selinuxfs, disabled kernel SELinux, multiple policy versions, failed downgrade fallback, and command-line/config combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/load_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lsetfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/lsetfilecon.c

## Purpose
Sets an SELinux file context on a path without following the final symlink.

## Important APIs, Types, And Functions
`lsetfilecon_raw()` writes the `security.selinux` xattr through `lsetxattr()`. `lsetfilecon()` translates a possibly human-readable context to raw form with `selinux_trans_to_raw_context()` before calling the raw setter.

## Control Flow
The raw setter writes `strlen(context) + 1` bytes. If `lsetxattr()` returns `ENOTSUP`, it reads the current raw context and treats the operation as success when the requested context already matches.

## State And Persistence Behavior
The only persistence is the file xattr. The compatibility path avoids failing no-op writes on unsupported xattr backends when the existing label is already correct.

## Dependencies And Integration Points
Depends on `policy.h` for `XATTR_NAME_SELINUX`, translation support from setrans, and `lgetfilecon_raw()`/`freecon()`.

## Risks And Test Signals
Test symlink targets, unsupported filesystems, identical/different existing labels, null/invalid contexts, and translated versus raw contexts. The ENOTSUP fallback is security-sensitive because it must not mask a requested label change.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/lsetfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.c -->
# sources/security-integrity/selinux/libselinux/src/mapping.c

## Purpose
Maintains userspace-to-kernel security class and permission mappings so object managers can use stable local class indices while querying the loaded SELinux policy.

## Important APIs, Types, And Functions
`struct selinux_mapping` stores a kernel class value and permission bit translations. `selinux_set_mapping()` builds the current mapping from `struct security_class_mapping`. `map_class()`, `unmap_class()`, `map_perm()`, `unmap_perm()`, and `map_decision()` translate classes, permission masks, and `struct av_decision`.

## Control Flow
Setting a mapping resets AVC state, resolves every class and permission string through policy stringrep helpers, handles unknown entries according to `security_reject_unknown()` and `security_deny_unknown()`, then publishes the mapping size last so setup lookups stay raw.

## State And Persistence Behavior
State is process-global heap memory in `current_mapping`; it is replaced on every successful setup and freed on errors. No disk state is written.

## Dependencies And Integration Points
Integrates with `avc_reset()`, `string_to_security_class()`, `string_to_av_perm()`, `security_reject_unknown()`, `security_deny_unknown()`, logging callbacks, and AVC decisions.

## Risks And Test Signals
Risks include global non-locked replacement, unknown-class handling, permission bit width assumptions, and `map_perm()` returning `EINVAL` when no known bit maps. Tests should exercise reject/allow unknown policy modes, empty permission names, unmapped fallback behavior, and `av_decision` remapping fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.h -->
# sources/security-integrity/selinux/libselinux/src/mapping.h

## Purpose
Declares the internal class/permission mapping interface used by libselinux AVC and string representation code.

## Important APIs, Types, And Functions
The header exposes `unmap_class()`, `unmap_perm()`, `map_class()`, `map_perm()`, and `map_decision()`. These functions convert between userspace mapped values and kernel policy values.

## Control Flow
There is no executable control flow in the header. It defines the contract that callers must use mapped classes at the public boundary and raw kernel classes when talking to selinuxfs.

## State And Persistence Behavior
No state lives in the header; the backing mapping table is process-global in `mapping.c`.

## Dependencies And Integration Points
Includes `selinux/selinux.h` and `selinux/avc.h` so it can name `security_class_t`, `access_vector_t`, and `struct av_decision`.

## Risks And Test Signals
The main risk is ABI drift between declarations and `mapping.c` definitions. Build tests plus AVC/stringrep tests that call all mapping helpers are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchmediacon.c -->
# sources/security-integrity/selinux/libselinux/src/matchmediacon.c

## Purpose
Looks up the default SELinux context for removable media names using the configured media contexts file.

## Important APIs, Types, And Functions
`matchmediacon()` opens `selinux_media_context_path()`, scans whitespace-separated records, matches the first token against `media`, and translates the remainder from raw to translated context.

## Control Flow
The function reads line by line, trims a trailing character, skips leading whitespace and empty entries, splits the media key from the context, and stops on the first exact match.

## State And Persistence Behavior
No persistent state is changed. It reads a policy configuration file and allocates the returned context for the caller.

## Dependencies And Integration Points
Uses config path resolution, `selinux_raw_to_trans_context()`, unlocked stdio, and `PATH_MAX` line buffering.

## Risks And Test Signals
Risks include fixed line length, simplistic parsing, and the trailing-character trim condition. Tests should cover missing file, blank/comment-like records, long lines, missing contexts, exact media matches, no match, and translation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchmediacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchpathcon.c -->
# sources/security-integrity/selinux/libselinux/src/matchpathcon.c

## Purpose
Provides the deprecated compatibility `matchpathcon*` API on top of modern `selabel` file-context lookup. It also tracks inode-to-spec associations for conflict diagnostics.

## Important APIs, Types, And Functions
Public entry points include `matchpathcon_init_prefix()`, `matchpathcon_init()`, `matchpathcon()`, `matchpathcon_index()`, `matchpathcon_fini()`, `selinux_file_context_verify()`, `selinux_lsetfilecon_default()`, and callback setters for printf, invalid-context checks, canonicalization, and flags. `compat_validate()` validates or canonicalizes lookup records. `realpath_not_final()` resolves parent paths while preserving a final symlink component.

## Control Flow
Initialization creates a thread-local `selabel_handle` with options derived from `set_matchpathcon_flags()`. Lookup resolves paths differently for symlinks and non-symlinks, then calls raw or translated `selabel_lookup`. Verification compares current raw xattr against expected raw context while ignoring user-field differences.

## State And Persistence Behavior
State is thread-local (`hnd`, options, context index array, `notrans`) plus a process hash table for inode/spec associations. Destructors free thread-local state. `selinux_lsetfilecon_default()` persists an xattr when a default label is found.

## Dependencies And Integration Points
Integrates with `selabel_open`, `selabel_lookup`, validation callbacks, xattr getters/setters, path canonicalization, and old `setfiles`-style conflict reporting.

## Risks And Test Signals
Risks include thread-local lifecycle, realpath behavior for missing symlink targets, inode hash conflicts, and deprecated compatibility callbacks. Tests should cover symlinks, relative paths, validation/canonicalization callbacks, no-match verification, ENOTSUP/ENOENT handling, and multi-thread init/fini.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/matchpathcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policy.h -->
# sources/security-integrity/selinux/libselinux/src/policy.h

## Purpose
Defines private libselinux constants for selinuxfs, policy file defaults, and SELinux xattr names.

## Important APIs, Types, And Functions
Exports `XATTR_NAME_SELINUX`, `INITCONTEXTLEN`, `SELINUXFS`, `SELINUX_MAGIC`, `SELINUXMNT`, `OLDSELINUXMNT`, `FILECONTEXTS`, `DEFAULT_POLICY_VERSION`, and the external `selinux_mnt`.

## Control Flow
No executable control flow exists.

## State And Persistence Behavior
`selinux_mnt` is mutable process-global state managed elsewhere and used by many selinuxfs accessors.

## Dependencies And Integration Points
Included by policy loaders, xattr setters, selinuxfs readers/writers, stringrep, and validation code.

## Risks And Test Signals
Risks are stale defaults relative to kernel/userland layout and inconsistent use of `selinux_mnt`. Compile coverage plus tests against both `/sys/fs/selinux` and legacy `/selinux` paths are relevant.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policyvers.c -->
# sources/security-integrity/selinux/libselinux/src/policyvers.c

## Purpose
Reads the running kernel SELinux policy version.

## Important APIs, Types, And Functions
`security_policyvers()` opens `<selinux_mnt>/policyvers`, parses an unsigned version, and returns `DEFAULT_POLICY_VERSION` when the control file is absent.

## Control Flow
The function fails with `ENOENT` if `selinux_mnt` is unset, otherwise reads a small fixed buffer and parses it with `sscanf()`.

## State And Persistence Behavior
It is read-only and depends entirely on selinuxfs state.

## Dependencies And Integration Points
Used by policy loading and the `policyvers` utility; depends on `policy.h` and `selinux_internal.h`.

## Risks And Test Signals
Test missing mount, missing `policyvers`, unreadable file, malformed content, and valid versions. The fallback default is important for older kernels.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policyvers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/procattr.c -->
# sources/security-integrity/selinux/libselinux/src/procattr.c

## Purpose
Implements process security attribute getters and setters through `/proc/.../attr/*`, including current, previous, exec, fscreate, sockcreate, and keycreate contexts.

## Important APIs, Types, And Functions
`openattr()` chooses `/proc/<pid>/attr`, `/proc/thread-self/attr`, or `/proc/self/task/<tid>/attr`. `getprocattrcon_raw()` and `setprocattrcon_raw()` perform raw reads/writes. Macros generate `getcon`, `setcon`, `getexeccon`, `setexeccon`, `getfscreatecon`, `setsockcreatecon`, `getkeycreatecon`, and raw variants. `getpidcon*()` and `getpidprevcon*()` query other processes.

## Control Flow
Self setters translate contexts to raw form and cache successful writes in thread-local `prev_*` pointers. Self getters return cached values when present, otherwise read procfs. Clearing a context writes zero bytes.

## State And Persistence Behavior
Persistent effects are kernel per-thread/process procattr changes. Thread-local caches mirror recent successful writes and are freed by pthread-key destructors.

## Dependencies And Integration Points
Uses setrans translation, weak pthread helpers, `selinux_page_size`, `gettid()`/syscall fallback, and procfs ABI.

## Risks And Test Signals
Risks include cache staleness after external changes, pthread destructor behavior without pthreads, path buffer overflow protection, EINTR handling, and writing NULL buffers for clears. Tests should cover self and pid paths, clear/idempotent set, thread isolation, missing `/proc/thread-self`, invalid PIDs, and translated contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/procattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/query_user_context.c -->
# sources/security-integrity/selinux/libselinux/src/query_user_context.c

## Purpose
Provides terminal-interactive helpers for selecting or manually entering a login context.

## Important APIs, Types, And Functions
`query_user_context()` prints a default context and optionally presents a numbered menu. `manual_user_enter_context()` constructs a context using `context_new()`, `context_user_set()`, `context_role_set()`, `context_type_set()`, optional `context_range_set()`, and validates it with `security_check_context()`.

## Control Flow
The default list entry is selected unless the user answers yes to choosing another one. Manual entry loops until the user provides all required fields and the resulting context validates, or declines entry.

## State And Persistence Behavior
No SELinux state is changed. The selected context is heap-duplicated for the caller.

## Dependencies And Integration Points
Uses stdin/stdout, libselinux context manipulation, `is_selinux_mls_enabled()`, and security context validation.

## Risks And Test Signals
Risks are interactive blocking, fixed field buffers, unchecked `strtol()` menu parsing, and use of `fflush(stdin)`. Tests should use scripted stdin for menu selection, EOF, MLS enabled/disabled, invalid contexts, and allocation failures where practical.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/query_user_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.c -->
# sources/security-integrity/selinux/libselinux/src/regex.c

## Purpose
Abstracts the file-context regular expression backend so label code can support PCRE2 or legacy PCRE through one internal API.

## Important APIs, Types, And Functions
`regex_arch_string()` identifies pointer width, regex size type width, and endian for serialized PCRE2 patterns. `regex_version()` reports backend version. `regex_prepare_data()` compiles and prepares match data/study data. `regex_load_mmap()` loads serialized patterns from compiled file-context mmaps. `regex_writef()` serializes patterns. `regex_match()`, `regex_cmp()`, `regex_data_free()`, and `regex_format_error()` provide matching, crude comparison, cleanup, and diagnostics.

## Control Flow
The PCRE2 path compiles with `PCRE2_DOTALL`, optionally decodes serialized code, writes serialized blobs with a length prefix, and locks a mutex around match data. The PCRE1 path maps compiled and study blobs directly from mmap and uses ownership flags to avoid freeing mapped memory.

## State And Persistence Behavior
Regex state is heap or mmap-backed `struct regex_data`. Serialization writes backend-specific binary blobs to compiled context files, and PCRE2 serialization is guarded by architecture string compatibility.

## Dependencies And Integration Points
Used by file-label parsing/loading and `sefcontext_compile`; depends on `label_file.h`, `next_entry()`, pthread mutex helpers, endian conversion, PCRE/PCRE2 APIs, and `SELABEL_*` comparison constants.

## Risks And Test Signals
Risks include backend divergence, non-portable serialized patterns, mutex lifecycle, binary comparison false negatives, and malformed mmap bounds. Tests should cover compile errors, partial matches, no matches, serialization round trips, mismatched architecture/version data, and both PCRE1/PCRE2 builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.h -->
# sources/security-integrity/selinux/libselinux/src/regex.h

## Purpose
Defines the internal regular-expression backend contract used by libselinux file labeling and context compilation.

## Important APIs, Types, And Functions
Declares match result constants, opaque `struct regex_data`, backend-specific `struct regex_error_data`, and functions for architecture/version reporting, compile/load/write/free/match/compare/error-format operations.

## Control Flow
The header documents expected success and failure returns for compile, mmap load, serialization, and match operations.

## State And Persistence Behavior
No state lives in the header, but it describes serialized regex persistence and ownership expectations for returned `regex_data`.

## Dependencies And Integration Points
Includes PCRE2 or PCRE headers depending on `USE_PCRE2`, plus stdio and bool; forward-declares `struct mmap_area`.

## Risks And Test Signals
Risks are public-internal API mismatch with `regex.c` and backend-specific struct assumptions. Compile tests for both regex backends and file-context binary round trips are the main signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/regex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/reject_unknown.c -->
# sources/security-integrity/selinux/libselinux/src/reject_unknown.c

## Purpose
Reads whether the kernel rejects policy queries involving unknown classes or permissions.

## Important APIs, Types, And Functions
`security_reject_unknown()` reads `<selinux_mnt>/reject_unknown` and parses an integer.

## Control Flow
The function validates `selinux_mnt`, opens the control file, reads a small buffer, parses with `sscanf()`, and returns the parsed value.

## State And Persistence Behavior
Read-only selinuxfs access; no local caching or persistence.

## Dependencies And Integration Points
Used by `selinux_set_mapping()` to decide whether unknown mapping entries are fatal.

## Risks And Test Signals
Tests should cover missing mount, missing/unreadable control file, malformed content, and kernel values `0`/`1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/reject_unknown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c

## Purpose
Checks whether the type component of a provided context appears in the configured `securetty_types` file.

## Important APIs, Types, And Functions
`selinux_check_securetty_context()` parses `tty_context` with `context_new()`, extracts `context_type_get()`, and scans `selinux_securetty_types_path()`.

## Control Flow
The scanner trims line newlines, skips leading whitespace and blank lines, splits on whitespace, and returns `0` on first type match or `-1` otherwise.

## State And Persistence Behavior
Read-only policy configuration access; no persistent state.

## Dependencies And Integration Points
Uses context parsing and config path helpers. The utility with the same name wraps this API.

## Risks And Test Signals
Test invalid contexts, missing securetty file, blank/whitespace lines, comments treated as tokens, and exact type matches. The function returns the same failure code for no match and read/parse errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_check_securetty_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_config.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_config.c

## Purpose
Owns libselinux configuration parsing and derived path construction for policy roots, context files, booleans, translations, and related SELinux configuration files.

## Important APIs, Types, And Functions
`selinux_getenforcemode()` reads `SELINUX=`. `selinux_getpolicytype()`, `selinux_set_policy_root()`, `selinux_reset_config()`, `selinux_policy_root()`, and many `selinux_*_path()` accessors expose cached paths. `init_selinux_config()` parses `SELINUXTYPE=` and `REQUIRESEUSERS=`, defaults to `targeted`, and builds `file_paths[]` from `file_path_suffixes.h`.

## Control Flow
Initialization is lazy via `__selinux_once()`. Reset frees all cached strings and reinitializes. `selinux_current_policy_path()` first prefers `<selinux_mnt>/policy`, then searches descending `policy.N` files from the kernel version.

## State And Persistence Behavior
Process-global cached strings hold policy type, policy root, and all derived paths. Disk state is only read from `/etc/selinux/config` and policy-root files.

## Dependencies And Integration Points
This module feeds nearly every policy/config consumer: policy load, media contexts, securetty, seusers, label file paths, and utilities. It uses `require_seusers` from `seusers.c`.

## Risks And Test Signals
Risks include one-time init plus manual reset interactions, partial allocation failure leaving incomplete `file_paths`, global state mutation from `selinux_set_policy_root()`, and permissive parsing. Tests should cover absent config, whitespace/case variations, disabled/enforcing/permissive values, policy-root override, reset after chroot-like changes, and all accessors returning source-tree-consistent paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_internal.c

## Purpose
Provides portability fallbacks for libc functions that may be absent on target platforms.

## Important APIs, Types, And Functions
Defines `strlcpy()` when `HAVE_STRLCPY` is absent and `reallocarray()` when `HAVE_REALLOCARRAY` is absent.

## Control Flow
`strlcpy()` copies up to `size - 1` bytes and always NUL-terminates when size is nonzero. `reallocarray()` checks multiplication overflow before calling `realloc()`.

## State And Persistence Behavior
No persistent state.

## Dependencies And Integration Points
Shared by code using safer string copy and overflow-checked allocation, especially path and dynamic-array logic.

## Risks And Test Signals
Tests should cover zero-size `strlcpy`, truncation return values, exact fit, `reallocarray()` overflow, zero-sized allocation, and normal allocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.h -->
# sources/security-integrity/selinux/libselinux/src/selinux_internal.h

## Purpose
Defines libselinux-wide internal portability, threading, errno, configuration, and compiler helper macros.

## Important APIs, Types, And Functions
Exports `require_seusers`, `selinux_page_size`, `has_selinux_config`, `SELINUXDIR`, `SELINUXCONFIG`, weak-pthread wrappers (`__selinux_once`, mutex/key helpers), `__pthread_supported`, fallbacks for `strlcpy`/`reallocarray`, sanitizer/deprecation macros, `fclose_errno_safe()`, `likely`/`unlikely`, `spaceship_cmp()`, and `SELINUX_PROTECT_ERRNO`.

## Control Flow
Macros conditionally call pthread functions only when linked, allowing builds without hard pthread dependencies.

## State And Persistence Behavior
Only extern declarations point to process-global state; no storage is defined here.

## Dependencies And Integration Points
Included broadly across libselinux. Threaded modules rely on these wrappers for optional pthread support and cleanup.

## Risks And Test Signals
Risks include weak-symbol behavior on unusual linkers, macros silently doing nothing without pthreads, and cleanup attribute compiler support. Build matrix tests with/without pthreads and fallback libc functions are important.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_netlink.h -->
# sources/security-integrity/selinux/libselinux/src/selinux_netlink.h

## Purpose
Defines SELinux netlink notification constants and message payload structures.

## Important APIs, Types, And Functions
Declares message IDs `SELNL_MSG_SETENFORCE`, `SELNL_MSG_POLICYLOAD`, multicast groups `SELNL_GRP_AVC`, and payload structs `selnl_msg_setenforce` and `selnl_msg_policyload`.

## Control Flow
No executable code.

## State And Persistence Behavior
No state. The structures describe kernel-to-userspace notification data.

## Dependencies And Integration Points
Consumed by AVC/netlink code and status fallback handling for setenforce and policyload events.

## Risks And Test Signals
ABI compatibility with kernel headers is the main risk. Compile checks and netlink event integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c

## Purpose
Implements `selinux_restorecon()` and related APIs for computing default file labels from file-context specs, applying xattrs, skipping unchanged subtrees via digests, excluding non-seclabel filesystems, and optionally walking in parallel.

## Important APIs, Types, And Functions
Public APIs include `selinux_restorecon()`, `selinux_restorecon_parallel()`, `selinux_restorecon_set_sehandle()`, `selinux_restorecon_default_handle()`, `selinux_restorecon_set_exclude_list()`, `selinux_restorecon_set_alt_rootpath()`, `selinux_restorecon_xattr()`, and counters for skipped errors and relabeled files. Key internals are `restorecon_sb()`, `selinux_restorecon_common()`, `safe_open()`, `walk_next()`, `selinux_restorecon_thread()`, digest helpers, and inode association helpers.

## Control Flow
Common setup maps flags into `struct rest_flags`, lazy-initializes a default selabel handle, resolves paths, opens the root safely with `O_PATH|O_NOFOLLOW`, and either labels one node or recursively walks a directory tree. Recursive walking uses an explicit directory stack, optional worker threads sharing `rest_state`, cycle checks, mount/exclude pruning, sysfs partial-match pruning, digest skip/write decisions, and per-entry `restorecon_sb()` calls.

## State And Persistence Behavior
Persistent effects are `security.selinux` xattr writes and optional `security.sehash` digest xattr writes/removals. Process-global state includes the file-context handle, exclude list, alt root path, xattr report list, skipped/relabeled counters, and file-spec hash. Thread-shared state is protected by mutexes where needed.

## Dependencies And Integration Points
Integrates with selabel file backend, SHA1 digest code, context manipulation, xattr syscalls, `/proc/self/fd` labeling fallback, `statfs` filesystem filtering, syslog, pthread optional support, and restorecon public flags.

## Risks And Test Signals
Risks include TOCTOU around path traversal, shared-state locking in parallel mode, digest skip correctness, custom-label preservation, conflicting hardlink specs, ignored error accounting, alt-root path slicing, and root/global handle ownership. Tests should cover no-change/verbose/syslog modes, recursive and parallel walks, symlinks, hardlinks, excluded mounts, xdev boundaries, customizable contexts, missing files with ignore flag, read-only filesystems, digest hit/miss/write/delete, and abort/count-error semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sestatus.c -->
# sources/security-integrity/selinux/libselinux/src/sestatus.c

## Purpose
Provides fast access to SELinux kernel status through the selinuxfs `status` mmap page, with optional netlink fallback.

## Important APIs, Types, And Functions
`struct selinux_status_t` mirrors the kernel status page. `selinux_status_open()`, `selinux_status_close()`, `selinux_status_updated()`, `selinux_status_getenforce()`, `selinux_status_policyload()`, and `selinux_status_deny_unknown()` expose status reads. Fallback callbacks update local enforcing and policyload counters from netlink events.

## Control Flow
Mapped-page reads use a seqlock pattern: wait for an even sequence, read fields, and retry if the sequence changes. `selinux_status_updated()` triggers AVC callbacks when enforcing or policyload changes since the previous call.

## State And Persistence Behavior
State is process-global: mapped status pointer, last sequence/policyload, fallback counters, and optional fallback netlink thread. It is read-only with respect to kernel state.

## Dependencies And Integration Points
Uses `selinux_mnt`, AVC internal callbacks, netlink open/check/loop helpers, `avc_using_threads`, and memory barriers.

## Risks And Test Signals
Risks include fallback policyload unreliability before first event, thread shutdown, seqlock correctness, and global open/close lifecycle. Tests should cover mmap success, mmap failure with fallback, no fallback, sequence changes, enforcing callbacks, policyload callbacks, and deny_unknown reading.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sestatus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setenforce.c -->
# sources/security-integrity/selinux/libselinux/src/setenforce.c

## Purpose
Sets the kernel SELinux enforcing mode.

## Important APIs, Types, And Functions
`security_setenforce()` writes `0` or `1` as text to `<selinux_mnt>/enforce`.

## Control Flow
The function validates `selinux_mnt`, opens the control file read-write, writes the formatted integer, closes, and returns success on nonnegative write.

## State And Persistence Behavior
Persists immediate kernel enforcing-state change through selinuxfs.

## Dependencies And Integration Points
Used by init policy loading and the `setenforce` utility.

## Risks And Test Signals
Test missing mount, permission denied, invalid values accepted/rejected by kernel, write errors, and caller behavior when SELinux is disabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setenforce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setexecfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/setexecfilecon.c

## Purpose
Computes and sets the process exec context for executing a file, with an RPM script fallback type helper.

## Important APIs, Types, And Functions
`setexecfilecon()` gets the current process context, file context, computes a process transition with `security_compute_create()`, falls back by replacing the current context type with `fallback_type` if no transition occurs, and calls `setexeccon()`. `rpm_execcon()` sets `rpm_script_t` and then `execve()`s.

## Control Flow
If SELinux is disabled it returns success. Errors during computation or setting are tolerated in permissive mode by returning success.

## State And Persistence Behavior
Sets the kernel per-thread exec context through procattr so the next exec uses it. No disk state is changed.

## Dependencies And Integration Points
Uses process/file context getters, context manipulation, class string lookup for `process`, transition computation, procattr setters, and optional RPM integration.

## Risks And Test Signals
Risks include fallback type producing invalid contexts, permissive-mode masking errors, and file context retrieval on symlinks or missing files. Tests should cover disabled/permissive/enforcing modes, default transition and fallback paths, invalid fallback types, and execcon clearing after use by callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setexecfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/setfilecon.c

## Purpose
Sets an SELinux context on a path following normal xattr semantics.

## Important APIs, Types, And Functions
`setfilecon_raw()` writes `security.selinux` using `setxattr()`. `setfilecon()` translates a context to raw form first.

## Control Flow
Like `lsetfilecon_raw()`, it treats `ENOTSUP` as success only if the current raw file context already equals the requested one.

## State And Persistence Behavior
Persists the `security.selinux` xattr on the target path. The translated wrapper allocates and frees the raw context.

## Dependencies And Integration Points
Uses setrans translation, xattr APIs, `getfilecon_raw()`, `freecon()`, and `policy.h`.

## Risks And Test Signals
Test symlink-following expectations, unsupported filesystems, identical/different labels, translation failure, invalid contexts, and permission errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_client.c -->
# sources/security-integrity/selinux/libselinux/src/setrans_client.c

## Purpose
Client-side support for translating raw SELinux contexts to display contexts, display contexts to raw contexts, and raw contexts to color strings via `mcstransd`/setransd.

## Important APIs, Types, And Functions
`selinux_trans_to_raw_context()`, `selinux_raw_to_trans_context()`, and `selinux_raw_context_to_color()` are public entry points. Internals include `setransd_open()`, `send_request()`, `receive_response()`, `raw_to_trans_context()`, `trans_to_raw_context()`, and thread-local one-entry caches.

## Control Flow
Initialization checks for the Unix socket once. If unavailable or disabled at build time, translation degenerates to `strdup()`. Otherwise each cache miss opens a socket, sends a framed request with function ID and NUL-terminated strings, validates a framed response, and caches the result.

## State And Persistence Behavior
State is thread-local cache strings and a pthread destructor key. No persistent storage is changed.

## Dependencies And Integration Points
Uses `SETRANS_UNIX_SOCKET` and protocol constants from `setrans_internal.h`, Unix domain sockets, `readv`/`sendmsg`, optional pthread helpers, and is called by most translated context APIs.

## Risks And Test Signals
Risks include partial `sendmsg()` handling, protocol endian assumptions, socket path limits, stale `has_setrans` after daemon start/stop, cache lifecycle, and fallback masking daemon errors. Tests should cover disabled build, no socket, successful translation, malformed response, oversized response, EINTR, cache hits, and per-thread cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_internal.h -->
# sources/security-integrity/selinux/libselinux/src/setrans_internal.h

## Purpose
Defines the private setrans client/server socket path and protocol constants.

## Important APIs, Types, And Functions
Defines `SETRANS_UNIX_SOCKET`, request IDs `RAW_TO_TRANS_CONTEXT`, `TRANS_TO_RAW_CONTEXT`, `RAW_CONTEXT_TO_COLOR`, and `MAX_DATA_BUF`.

## Control Flow
No executable logic.

## State And Persistence Behavior
No local state; constants describe IPC framing limits and endpoint location.

## Dependencies And Integration Points
Included by `setrans_client.c` and tied to the `mcstransd` protocol.

## Risks And Test Signals
Compatibility with daemon protocol and maximum buffer size are the key concerns. IPC tests should validate all function IDs and boundary response sizes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setup.py -->
# sources/security-integrity/selinux/libselinux/src/setup.py

## Purpose
Python packaging script for the libselinux Python extension.

## Important APIs, Types, And Functions
Calls `distutils.core.setup()` with extension module metadata, building `selinux` from `selinuxswig_python_wrap.c` and linking against `selinux`.

## Control Flow
The script is declarative: when invoked by Python packaging tools, distutils compiles the extension from the specified source and library settings.

## State And Persistence Behavior
Writes build/install artifacts as directed by distutils; no project runtime state is touched.

## Dependencies And Integration Points
Depends on generated SWIG wrapper C source, libselinux headers/libraries, and Python distutils.

## Risks And Test Signals
Risks include deprecated distutils, missing generated wrapper, library path issues, and Python version compatibility. Build/import tests for the extension are the useful signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/seusers.c -->
# sources/security-integrity/selinux/libselinux/src/seusers.c

## Purpose
Maps Linux login users and services to SELinux users and MLS levels using `seusers` and per-login policy files.

## Important APIs, Types, And Functions
`process_seusers()` parses `linuxuser:seuser[:level]` records. `getseuserbyname()` resolves exact, group (`%group`), `__default__`, or username fallback mappings. `getseuser()` first tries `<policyroot>/logins/<username>` service-specific records, then falls back to `getseuserbyname()`.

## Control Flow
`getseuserbyname()` scans all records, preserving the first matching group and default while allowing exact user matches to win. Group membership is checked with `get_default_gid()`, `getgrnam_r()`, and `getgrouplist()`. MLS level parsing is skipped when MLS is disabled.

## State And Persistence Behavior
Global `require_seusers` controls whether no-match fallback to Linux username is allowed. The module reads policy config files and allocates returned strings.

## Dependencies And Integration Points
Uses config path accessors, context/MLS checks, libc passwd/group APIs, and logging callbacks for bad records.

## Risks And Test Signals
Risks include ambiguous precedence, ERANGE buffer growth, missing groups/users, malformed line handling, global `require_seusers`, and service-specific fallback. Tests should cover exact/group/default/no-match, MLS on/off, invalid records, long NSS entries, and `REQUIRESEUSERS` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/seusers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.c -->
# sources/security-integrity/selinux/libselinux/src/sha1.c

## Purpose
Implements SHA-1 hashing for libselinux digest features, especially file-context digest generation.

## Important APIs, Types, And Functions
`Sha1Initialise()`, `Sha1Update()`, and `Sha1Finalise()` operate on `Sha1Context` and produce `SHA1_HASH`. `TransformFunction()` is the internal 80-round compression function.

## Control Flow
Update accumulates bit counts, fills 64-byte blocks, and processes full blocks. Finalise appends SHA-1 padding, appends the big-endian length, and extracts the digest bytes.

## State And Persistence Behavior
State is caller-owned hash context memory. No external state is changed.

## Dependencies And Integration Points
Used by label digest code. Uses `ignore_unsigned_overflow_` because SHA-1 arithmetic intentionally wraps.

## Risks And Test Signals
Risks include integer-size limits (`uint32_t BufferSize`), endian/block handling, and cryptographic obsolescence if used for security instead of change detection. Tests should include standard SHA-1 vectors, incremental updates, empty input, boundary sizes around 64 bytes, and large multi-block inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.h -->
# sources/security-integrity/selinux/libselinux/src/sha1.h

## Purpose
Declares the small SHA-1 API and data structures used internally by libselinux.

## Important APIs, Types, And Functions
Defines `Sha1Context`, `SHA1_HASH_SIZE`, `SHA1_HASH`, and prototypes for `Sha1Initialise()`, `Sha1Update()`, and `Sha1Finalise()`.

## Control Flow
No executable control flow.

## State And Persistence Behavior
All hash state is caller-owned in `Sha1Context`.

## Dependencies And Integration Points
Included by label digest internals and paired with `sha1.c`.

## Risks And Test Signals
Compile checks and known-answer hash tests validate the declaration/implementation contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/stringrep.c -->
# sources/security-integrity/selinux/libselinux/src/stringrep.c

## Purpose
Converts SELinux class and permission names to numeric values and numeric values back to strings by discovering policy data from selinuxfs.

## Important APIs, Types, And Functions
`discover_class()` reads `<selinux_mnt>/class/<name>/index` and permission files. Public helpers include `string_to_security_class()`, `mode_to_security_class()`, `string_to_av_perm()`, `security_class_to_string()`, `security_av_perm_to_string()`, `security_av_string()`, `print_access_vector()`, and `selinux_flush_class_cache()`.

## Control Flow
Class discovery validates class names, allocates a cache node, reads the numeric class index, scans permissions, and inserts the node into a process-global linked-list cache. Permission lookup maps through `mapping.c`.

## State And Persistence Behavior
State is a process-global class cache populated lazily and freed only by `selinux_flush_class_cache()`. It reads selinuxfs and writes no persistent data.

## Dependencies And Integration Points
Used by compute utilities, mapping setup, AVC helpers, and restore/exec transition code. It depends on `selinux_mnt`, class/perms selinuxfs layout, and mapping helpers.

## Risks And Test Signals
Risks include non-thread-safe cache mutation, stale cache after policy reload, sparse permission arrays stopping early in `string_to_av_perm()`, and mode-to-class coverage. Tests should cover cache flush, unknown classes/perms, policy reload behavior, all file modes, and printing known/unknown permission bits.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/stringrep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/validatetrans.c -->
# sources/security-integrity/selinux/libselinux/src/validatetrans.c

## Purpose
Asks the kernel whether a source, target, class, and new context transition is valid under policy constraints.

## Important APIs, Types, And Functions
`security_validatetrans_raw()` writes a space-separated query to `<selinux_mnt>/validatetrans`. `security_validatetrans()` translates all contexts to raw form before calling the raw helper.

## Control Flow
The raw helper allocates one page, formats `scon tcon class newcon`, rejects truncation, writes to the control file, and converts positive byte-count success to `0`.

## State And Persistence Behavior
The kernel validates the transition; no persistent policy or label state is changed.

## Dependencies And Integration Points
Depends on context translation, class unmapping, selinuxfs, and `selinux_page_size`. The utility `validatetrans` wraps this API.

## Risks And Test Signals
Risks include contexts containing spaces, page-size truncation, class mapping errors, and write return semantics. Tests should cover valid/invalid transitions, translated contexts, unset selinuxfs, very long contexts, and invalid classes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/validatetrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/Makefile -->
# sources/security-integrity/selinux/libselinux/utils/Makefile

## Purpose
Builds and installs libselinux command-line utilities.

## Important APIs, Types, And Functions
Defines compiler warning flags, include/link flags, target selection, PCRE-linked utilities, and install/clean rules. `TARGETS` defaults to every `*.c` utility except Android host builds, which only build `sefcontext_compile`.

## Control Flow
Make expands targets from source filenames, appends libselinux and optional PCRE/FTS link libraries, and installs binaries under `$(PREFIX)/sbin`.

## State And Persistence Behavior
Build outputs are utility binaries and object files; install writes to `$(DESTDIR)$(SBINDIR)`.

## Dependencies And Integration Points
Depends on `../src/libselinux`, headers in `../include`, optional libsepol for `sefcontext_compile`, PCRE flags for label utilities, and platform-specific Darwin adjustments.

## Risks And Test Signals
Risks include `-Werror` portability, Android target narrowing, static library linkage for `sefcontext_compile`, and missing PCRE flags. Test signals are full `make all`, Android-host build, Darwin build, install path staging, and clean/distclean.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/avcstat.c -->
# sources/security-integrity/selinux/libselinux/utils/avcstat.c

## Purpose
Displays SELinux AVC cache statistics from selinuxfs, either once or at an interval.

## Important APIs, Types, And Functions
`main()` parses `-c`, `-f`, and optional interval. `set_window_rows()` sizes header repetition from terminal rows. `die()` reports fatal parse/read errors.

## Control Flow
The utility reads a stats file with fixed headers, sums per-CPU rows into totals, prints cumulative or relative values, and loops with `sleep()` plus `lseek()` when an interval is supplied.

## State And Persistence Behavior
Read-only; local `last` stores prior totals for relative output.

## Dependencies And Integration Points
Uses global `selinux_mnt`, `/avc/cache_stats`, terminal `ioctl(TIOCGWINSZ)`, and SIGWINCH.

## Risks And Test Signals
Test header validation, no data, custom file path, relative deltas, cumulative mode, interval zero, SIGWINCH, and counter wrap/large values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/avcstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_av.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_av.c

## Purpose
CLI for computing access-vector decisions between two contexts and a target class.

## Important APIs, Types, And Functions
`main()` validates source/target contexts, resolves class with `string_to_security_class()`, calls `security_compute_av()`, and prints allowed, decided, undecided, auditallow, auditdeny, and dontaudit vectors with `print_access_vector()`.

## Control Flow
Invalid arguments, contexts, class, or compute failures map to distinct exit codes.

## State And Persistence Behavior
Read-only policy query; no state changes.

## Dependencies And Integration Points
Exercises context validation, stringrep, kernel policy computation, and access-vector printing.

## Risks And Test Signals
Tests should cover invalid context/class exits, valid decisions, unknown permissions in print output, and SELinux disabled/missing selinuxfs behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_create.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_create.c

## Purpose
CLI for computing the default create context for a source context, target context, class, and optional object name.

## Important APIs, Types, And Functions
Uses `security_check_context()`, `string_to_security_class()`, and `security_compute_create_name()`.

## Control Flow
Requires three or four operands after the program name, validates inputs, calls compute, prints the returned context, and frees it.

## State And Persistence Behavior
Read-only policy query.

## Dependencies And Integration Points
Integrates with class string resolution and name-based type transition policy.

## Risks And Test Signals
Test named and unnamed creates, invalid contexts/classes, no transition errors, and object names with unusual characters.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_member.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_member.c

## Purpose
CLI for computing a member context for polyinstantiation/member relationships.

## Important APIs, Types, And Functions
Calls `security_compute_member()` after validating two contexts and resolving a target class.

## Control Flow
Argument and validation failures use fixed exit codes, then successful computation prints one context.

## State And Persistence Behavior
Read-only policy query.

## Dependencies And Integration Points
Uses standard libselinux validation and stringrep helpers.

## Risks And Test Signals
Test invalid inputs, valid member rules, policy with no member transition, and class mapping behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_member.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_relabel.c -->
# sources/security-integrity/selinux/libselinux/utils/compute_relabel.c

## Purpose
CLI for computing the context allowed/selected for a relabel operation.

## Important APIs, Types, And Functions
Validates source/target contexts, resolves class, calls `security_compute_relabel()`, prints and frees the result.

## Control Flow
Mirrors the `compute_member` pattern with distinct exit codes for bad inputs or compute failure.

## State And Persistence Behavior
Read-only policy query; no xattrs are changed.

## Dependencies And Integration Points
Useful for testing relabel policy without invoking `restorecon` or `setfilecon`.

## Risks And Test Signals
Test valid relabel rules, invalid contexts, invalid classes, and kernel query errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/compute_relabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getconlist.c -->
# sources/security-integrity/selinux/libselinux/utils/getconlist.c

## Purpose
Prints the ordered list of login contexts available to a user from a current or supplied context.

## Important APIs, Types, And Functions
Parses `-l level`, validates SELinux enabled, obtains current context with `getcon()` when needed, validates supplied context, and calls `get_ordered_context_list()` or `_with_level()`.

## Control Flow
Requires `user [context]`; prints each returned context on success and frees arrays.

## State And Persistence Behavior
Read-only; allocates context list and optional level/current context.

## Dependencies And Integration Points
Uses get-context-list policy logic and SELinux enabled checks.

## Risks And Test Signals
Test disabled SELinux, invalid contexts, explicit versus current context, level override, no contexts, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getconlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c

## Purpose
Prints the default login context for a Linux user, with optional role, level, service, and verbose output.

## Important APIs, Types, And Functions
Uses `getseuser()`, `get_default_context_with_level()`, and `get_default_context_with_rolelevel()`. Options are `-r`, `-l`, `-s`, and `-v`.

## Control Flow
After resolving current/from context and SELinux user/default level, it computes a default context and prints either the context alone or a verbose transition description.

## State And Persistence Behavior
Read-only policy and login mapping access.

## Dependencies And Integration Points
Connects `seusers.c` login mapping to default-context selection APIs.

## Risks And Test Signals
Test service-specific mappings, role/level overrides, invalid from contexts, disabled SELinux, verbose output, and memory cleanup when `level` aliases `dlevel`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getdefaultcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getenforce.c -->
# sources/security-integrity/selinux/libselinux/utils/getenforce.c

## Purpose
Prints SELinux mode as `Enforcing`, `Permissive`, or `Disabled`.

## Important APIs, Types, And Functions
`main()` calls `is_selinux_enabled()` and, when enabled, `security_getenforce()`.

## Control Flow
Failure to query enabled/enforcing state returns `2`; disabled and successful states return `0`.

## State And Persistence Behavior
Read-only selinuxfs access.

## Dependencies And Integration Points
Thin CLI over core mode APIs.

## Risks And Test Signals
Test enabled permissive/enforcing, disabled, and error paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getenforce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getfilecon.c -->
# sources/security-integrity/selinux/libselinux/utils/getfilecon.c

## Purpose
Prints SELinux file contexts for one or more paths.

## Important APIs, Types, And Functions
Loops over operands, calls `getfilecon()`, prints `path<TAB>context`, and frees each context.

## Control Flow
Requires at least one path and exits on the first failure.

## State And Persistence Behavior
Read-only xattr/context access.

## Dependencies And Integration Points
Thin CLI wrapper for translated file-context reads.

## Risks And Test Signals
Test multiple paths, missing files, permission errors, translated contexts, and paths containing tabs/newlines.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getpidcon.c

## Purpose
Prints the current SELinux context for a process ID.

## Important APIs, Types, And Functions
Parses one `pid`, calls `getpidcon()`, prints and frees the returned context.

## Control Flow
Usage, invalid pid text, and API failure return distinct exits.

## State And Persistence Behavior
Read-only procattr access.

## Dependencies And Integration Points
Wraps `procattr.c` PID context support.

## Risks And Test Signals
Test invalid PID strings, pid `0`/negative, nonexistent process, permission denied, and translated contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c -->
# sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c

## Purpose
Prints the previous SELinux context for a process ID.

## Important APIs, Types, And Functions
Parses one PID, calls `getpidprevcon()`, prints and frees the result.

## Control Flow
Same argument and error pattern as `getpidcon`.

## State And Persistence Behavior
Read-only `/proc/<pid>/attr/prev` access.

## Dependencies And Integration Points
Wraps previous-context support in `procattr.c`.

## Risks And Test Signals
Test invalid/nonexistent PIDs, processes with no previous context, permission errors, and translation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpidprevcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpolicyload.c -->
# sources/security-integrity/selinux/libselinux/utils/getpolicyload.c

## Purpose
Prints the kernel policyload counter from the SELinux status page.

## Important APIs, Types, And Functions
Calls `selinux_status_open(0)`, `selinux_status_policyload()`, prints the integer, and closes status.

## Control Flow
Netlink fallback is intentionally disabled because policyload fallback is unreliable until an event arrives.

## State And Persistence Behavior
Read-only mmap/status access with temporary process-global status handle.

## Dependencies And Integration Points
Exercises `sestatus.c` mapped-page path.

## Risks And Test Signals
Test status map available/unavailable, read errors, and cleanup after failed open/read.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getpolicyload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getsebool.c -->
# sources/security-integrity/selinux/libselinux/utils/getsebool.c

## Purpose
Prints active and pending SELinux boolean values.

## Important APIs, Types, And Functions
Supports `-a` for all booleans or explicit names. Uses `security_get_boolean_names()`, `security_get_boolean_active()`, `security_get_boolean_pending()`, and `selinux_boolean_sub()`.

## Control Flow
Checks SELinux enabled, builds the boolean name list, prints `name --> on/off` plus pending state when it differs, and frees names.

## State And Persistence Behavior
Read-only boolean access.

## Dependencies And Integration Points
Thin diagnostic for boolean APIs and boolean alias/substitution handling.

## Risks And Test Signals
Test disabled SELinux, `-a` with no booleans, explicit names, pending different from active, EACCES skip for all-booleans mode, unknown names, and alias allocation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getsebool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getseuser.c -->
# sources/security-integrity/selinux/libselinux/utils/getseuser.c

## Purpose
Diagnostic utility for resolving a Linux user to SELinux user/level and listing ordered contexts from a supplied context.

## Important APIs, Types, And Functions
Calls `getseuserbyname()`, validates `fromcon`, then calls `get_ordered_context_list_with_level()`.

## Control Flow
Requires `linuxuser fromcon`, checks SELinux enabled, prints mapping, then prints numbered contexts or no-match message.

## State And Persistence Behavior
Read-only login mapping and policy access.

## Dependencies And Integration Points
Connects `seusers.c` and default context list logic.

## Risks And Test Signals
Test disabled SELinux, unknown users, invalid from context, no valid contexts, MLS levels, and returned list cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getseuser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/matchpathcon.c -->
# sources/security-integrity/selinux/libselinux/utils/matchpathcon.c

## Purpose
CLI for looking up or verifying default SELinux file contexts for paths.

## Important APIs, Types, And Functions
Options include `-V` verify, `-N` raw/no translation, `-n` no header, `-m` forced mode, `-f` file-context file, `-P` policy root, deprecated `-p` subset, and `-q` quiet verify. Uses `selabel_open()`, `selabel_lookup(_raw)()`, and `selinux_file_context_verify()`.

## Control Flow
For each path it strips a trailing slash, lstat()s unless a mode is forced, then either prints expected context or verifies actual context and reports mismatches.

## State And Persistence Behavior
Read-only; only opens a label handle and reads file xattrs during verify.

## Dependencies And Integration Points
Exercises file label backend, policy-root override, raw/translated lookup, and verification compatibility API.

## Risks And Test Signals
Test all mode letters, missing paths, no-match output, verify quiet behavior, raw versus translated output, policy-root override, deprecated subset option, and multiple path error accumulation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/matchpathcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/policyvers.c -->
# sources/security-integrity/selinux/libselinux/utils/policyvers.c

## Purpose
Prints the kernel policy version.

## Important APIs, Types, And Functions
Calls `security_policyvers()` and prints the integer.

## Control Flow
On API failure, reports strerror and exits `2`; otherwise exits success.

## State And Persistence Behavior
Read-only selinuxfs access.

## Dependencies And Integration Points
Thin wrapper over `src/policyvers.c`.

## Risks And Test Signals
Test missing selinuxfs, malformed policyvers, default fallback for missing file, and valid version output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/policyvers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c -->
# sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c

## Purpose
Compiles text `file_contexts` specifications into the binary mmap-able format consumed by libselinux file labeling.

## Important APIs, Types, And Functions
`process_file()` feeds lines to `process_line()`. `create_sidtab()` deduplicates raw contexts. `write_sidtab()`, `write_literal_spec()`, `write_regex_spec()`, `write_spec_node()`, and `write_binary_file()` serialize the binary format. `main()` handles `-o`, `-p`, `-r`, `-i`, and `-V`.

## Control Flow
The tool optionally loads a binary policy for validation, constructs a dummy file-label handle and saved data tree, parses the text file, sorts specs, creates a SID table, writes to a mode-preserving temporary file with `mkstemp()`, then atomically renames it to the output.

## State And Persistence Behavior
Writes a compiled `.bin` file containing magic/version, regex backend metadata, context table, and spec tree. Temporary files are unlinked on failure.

## Dependencies And Integration Points
Uses libsepol validation, internal label-file structures, sidtab, regex serialization, endian conversion, and file-label parser internals.

## Risks And Test Signals
Risks include binary format compatibility, regex portability, context validation callback behavior, temp-file cleanup, length overflows, and partial writes. Tests should cover default output, `-o`, `-p` valid/invalid policy, `-r`, `-i`, `-V`, malformed specs, long strings, atomic rename, and compiled-file load by `selabel_open()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/sefcontext_compile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_compare.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_compare.c

## Purpose
Compares two SELinux label specification files using a selected backend.

## Important APIs, Types, And Functions
Parses backend and validation options, opens two `selabel_handle`s with `SELABEL_OPT_PATH` and `SELABEL_OPT_VALIDATE`, and calls the backend `selabel_cmp()` operation.

## Control Flow
Backend names map to `SELABEL_CTX_*` constants, defaulting to file. Compare results are printed as equal, subset/superset, incomparable, or error depending on libselinux enum results.

## State And Persistence Behavior
Read-only label spec access.

## Dependencies And Integration Points
Exercises backend comparison callbacks, validation, and label handle lifecycle.

## Risks And Test Signals
Test each backend name, validation on/off, open failures, equal files, subset/superset/incomparable specs, and unknown backend handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_compare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_digest.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_digest.c

## Purpose
Utility for retrieving and optionally checking the digest associated with a selabel handle.

## Important APIs, Types, And Functions
Uses `selabel_open()` with digest options, `selabel_digest()` to obtain digest bytes and specfile list, and `run_check_digest()` to compare against external command output when requested.

## Control Flow
Command-line options select spec file, validation, and digest checking behavior. The digest is printed in hex along with contributing files, or compared to a supplied command/check result.

## State And Persistence Behavior
Read-only; digest bytes and file list are allocated and freed locally.

## Dependencies And Integration Points
Exercises `SELABEL_OPT_DIGEST` and file-label digest generation used by restorecon.

## Risks And Test Signals
Test missing spec file, digest disabled/unavailable, multiple specfiles, command-check mismatch, validation failures, and hex formatting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c

## Purpose
Reports calculated and stored digest values for all file-context specs that partially match directories under a path.

## Important APIs, Types, And Functions
Uses `selabel_get_digests_all_partial_matches()` for each directory found by `fts`, with options for spec file, validation, and recursive traversal.

## Control Flow
The utility opens a file-label handle, traverses the starting path physically, handles directories, prints whether xattr and calculated digests match, and formats digest bytes as hex.

## State And Persistence Behavior
Read-only: it does not set or remove digest xattrs.

## Dependencies And Integration Points
Closely mirrors restorecon digest decision logic and depends on FTS and label digest APIs.

## Risks And Test Signals
Test recursive and single-directory modes, no digest for `<<none>>`, missing xattr, mismatched xattr, allocation failures, FTS errors, and validation/spec-file options.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_get_digests_all_partial_matches.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c

## Purpose
Generic CLI for looking up a label by backend, key, optional type, spec file, validation, and raw/translated mode.

## Important APIs, Types, And Functions
Maps backend names to `SELABEL_CTX_*`, opens `selabel_handle`, calls `selabel_lookup()` or `selabel_lookup_raw()`, and prints the default context.

## Control Flow
Options are parsed with `getopt`; lookup errors distinguish no match, invalid key/type/validation, and other errno cases.

## State And Persistence Behavior
Read-only label spec access.

## Dependencies And Integration Points
Useful for file, media, X, DB, Android property, and Android service label backend diagnostics.

## Risks And Test Signals
Test all backends, missing key, type parsing, raw mode, no-match, validation failure, and custom spec files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c

## Purpose
CLI for finding the best file-context match for a path with optional alias/link paths.

## Important APIs, Types, And Functions
Parses `-p path`, optional `-m mode`, `-f file`, `-v`, and `-r`, builds a NULL-terminated aliases array, and calls `selabel_lookup_best_match()` or raw variant.

## Control Flow
Best-match precedence is handled by libselinux: exact real path, exact alias, then longest fixed prefix. The utility reports specific errors for no match and invalid inputs.

## State And Persistence Behavior
Read-only label lookup; dynamically allocates alias copies.

## Dependencies And Integration Points
Exercises file-label best-match logic used by alias-aware callers.

## Risks And Test Signals
Test zero/multiple aliases, forced modes, raw output, custom spec files, missing path operand, unknown mode letters, and allocation cleanup on partial alias duplication failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_lookup_best_match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c -->
# sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c

## Purpose
CLI for checking whether a path has any possible full or partial file-context match.

## Important APIs, Types, And Functions
Opens a file-label handle and calls `selabel_partial_match(hnd, path)`.

## Control Flow
Requires `-p path`; optional `-f` and `-v` configure the handle. It prints `TRUE` or `FALSE` and returns the boolean value.

## State And Persistence Behavior
Read-only.

## Dependencies And Integration Points
Matches restorecon sysfs pruning and partial-digest behavior.

## Risks And Test Signals
Test partial versus no partial paths, validation/spec-file options, missing path, and return-code expectations where `TRUE` returns nonzero.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selabel_partial_match.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c -->
# sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c

## Purpose
CLI for checking whether a source context has a permission on a target context/class.

## Important APIs, Types, And Functions
Optional `-a auditdata` installs an audit callback that copies the string into the audit message. Then `selinux_check_access()` is called with `scon tcon class perm`.

## Control Flow
Requires four operands after options; returns the libselinux check result and prints perror on failure.

## State And Persistence Behavior
Read-only policy query, but it mutates the process-global SELinux audit callback when `-a` is supplied.

## Dependencies And Integration Points
Exercises high-level access-check API and callback plumbing.

## Risks And Test Signals
Test allowed and denied checks, invalid classes/perms, audit callback content, missing args, and callback side effects in long-lived processes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c -->
# sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c

## Purpose
CLI wrapper around secure TTY context type checking.

## Important APIs, Types, And Functions
Loops over supplied contexts and calls `selinux_check_securetty_context()` for each.

## Control Flow
Every input prints either `securetty` or `not securetty`; the program returns success even for non-secure contexts.

## State And Persistence Behavior
Read-only policy config access.

## Dependencies And Integration Points
Thin diagnostic for `src/selinux_check_securetty_context.c`.

## Risks And Test Signals
Test multiple contexts, invalid contexts, missing securetty file, and caller expectations around always-success exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_securetty_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c -->
# sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c

## Purpose
Provides a shell-friendly test for whether SELinux is enabled.

## Important APIs, Types, And Functions
`main()` returns `!is_selinux_enabled()`.

## Control Flow
Enabled returns exit `0`; disabled returns nonzero. Negative error values become nonzero as well.

## State And Persistence Behavior
Read-only.

## Dependencies And Integration Points
Used by shell scripts and build/runtime checks.

## Risks And Test Signals
Test enabled, disabled, and error states; note that errors are not distinguished from enabled/disabled in output because there is no output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c -->
# sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c

## Purpose
Prints the process context that would result from executing a command from a supplied or current context.

## Important APIs, Types, And Functions
`get_selinux_proc_context()` gets the file context and calls `security_compute_create()` for class `process`. `main()` obtains/validates the source context.

## Control Flow
Requires `command [fromcon]`, computes transition, prints it on success, and reports perror on failure.

## State And Persistence Behavior
Read-only; it does not set exec context or execute the command.

## Dependencies And Integration Points
Diagnostic companion to `setexecfilecon()`.

## Risks And Test Signals
Test current versus supplied context, invalid supplied context, missing command file, no transition, and process class lookup failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxexeccon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setenforce.c -->
# sources/security-integrity/selinux/libselinux/utils/setenforce.c

## Purpose
CLI for changing SELinux enforcing/permissive mode.

## Important APIs, Types, And Functions
Accepts `Enforcing`, `Permissive`, `1`, or `0`; checks `is_selinux_enabled()` and calls `security_setenforce()`.

## Control Flow
Invalid args print usage. Disabled SELinux returns `1`; set failure returns `2`; success returns `0`.

## State And Persistence Behavior
Changes kernel enforcing mode through selinuxfs.

## Dependencies And Integration Points
Thin wrapper over `src/setenforce.c`.

## Risks And Test Signals
Test numeric/text case-insensitive inputs, disabled SELinux, permission denied, invalid values, and mode actually changing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setenforce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setfilecon.c -->
# sources/security-integrity/selinux/libselinux/utils/setfilecon.c

## Purpose
CLI for setting the same SELinux context on one or more paths.

## Important APIs, Types, And Functions
Loops over `path...` and calls `setfilecon(path, context)`.

## Control Flow
Requires `context path...`; exits on first failure.

## State And Persistence Behavior
Writes `security.selinux` xattrs through translated context setter.

## Dependencies And Integration Points
Thin wrapper over `src/setfilecon.c`.

## Risks And Test Signals
Test multiple paths, invalid contexts, permission denied, unsupported filesystems, partial failure behavior, and symlink-following semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setfilecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/togglesebool.c -->
# sources/security-integrity/selinux/libselinux/utils/togglesebool.c

## Purpose
Toggles one or more SELinux booleans and commits the transaction.

## Important APIs, Types, And Functions
Uses `security_get_boolean_active()`, `security_set_boolean()`, `security_commit_booleans()`, and rollback helper that restores processed booleans to active values.

## Control Flow
Each boolean is flipped in pending state. On any set/read error, previously processed booleans are rolled back and the program exits. Successful commit syslogs each changed boolean with username or uid.

## State And Persistence Behavior
Changes pending booleans and commits them to kernel/policy boolean state. Rollback attempts to restore pending values before commit.

## Dependencies And Integration Points
Integrates boolean APIs, syslog, pwd lookup, and user identity.

## Risks And Test Signals
Risks include rollback best-effort semantics, commit failure after pending changes, races with other boolean changes, and logging accuracy. Tests should cover toggling on/off, unknown boolean, mid-list failure rollback, commit failure, disabled SELinux, and syslog identity.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/togglesebool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/validatetrans.c -->
# sources/security-integrity/selinux/libselinux/utils/validatetrans.c

## Purpose
CLI for invoking kernel transition validation.

## Important APIs, Types, And Functions
Validates source, target, and new contexts; resolves class with `string_to_security_class()`; calls `security_validatetrans()`.

## Control Flow
Requires `scontext tcontext tclass newcontext`, prints the return value and current strerror for `errno`, and returns the validation result.

## State And Persistence Behavior
Read-only policy validation query.

## Dependencies And Integration Points
Wrapper for `src/validatetrans.c` and context validation/stringrep APIs.

## Risks And Test Signals
Test valid/invalid transitions, invalid contexts/classes, errno output after success, and shell handling of negative return values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/validatetrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/Makefile -->
# sources/security-integrity/selinux/libsemanage/Makefile

## Purpose
Top-level dispatcher Makefile for libsemanage build, wrapper generation, install, relabel, clean, and tests.

## Important APIs, Types, And Functions
Targets delegate to subdirectories: `src` for `all`, `swigify`, `pywrap`, `rubywrap`, relabel, and wrapper installs; `include`, `man`, and `utils` for install; `tests` for clean/distclean and `test`.

## Control Flow
Each rule is a simple recursive `$(MAKE) -C <dir> <target>` call, preserving the caller's make variables.

## State And Persistence Behavior
Build/install/test state is produced by delegated sub-makes. This file itself creates no artifacts directly.

## Dependencies And Integration Points
Coordinates libsemanage subprojects and provides stable top-level targets for packaging/build systems.

## Risks And Test Signals
Risks include recursive make target drift, missing subdirectories, and install target ordering. Test signals are top-level `make all`, `make test`, wrapper targets, staged install, and clean/distclean delegation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/Makefile -->
