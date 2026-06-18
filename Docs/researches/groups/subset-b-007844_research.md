# Research: subset-b-007844

Grouped research for OrangeFS `src/common/misc` utility, path, debug, hint, and server-configuration manager files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-util.c -->
## sources/distributed-fs/orangefs/src/common/misc/pint-util.c

Purpose: Implements internal OrangeFS utility primitives used across client/server code: wall/user/system timing, message-tag allocation, deep copy/free of `PVFS_object_attr`, object-type names, time helpers, BMI address/layout request encoding, alias guessing, and Windows `statfs` shims.

Important APIs and functions: `PINT_time_mark`/`PINT_time_diff` capture elapsed wall and CPU time. `PINT_util_get_next_tag` returns nonzero protocol message tags under `current_tag_lock`. `PINT_copy_object_attr` and `PINT_free_object_attr` own deep-copy and teardown for nested object attributes including distributions, datafile arrays, mirror arrays, symlink targets, directory hints, distributed-directory bitmaps/handles, and capabilities. `encode/decode_PVFS_BMI_addr_t` and `encode/decode_PVFS_sys_layout` bridge BMI addresses/layout lists into the request protocol. Time helpers expose seconds, milliseconds, microseconds, timestamp formatting, version packing, and absolute timespec construction.

Control flow: Attribute copy walks the source mask and allocates only masked dynamic fields, freeing destination-owned fields first when the destination already carries compatible mask bits. Encoding converts BMI handles through reverse lookup strings and bounds layout encodings against `PVFS_REQ_LIMIT_LAYOUT`. Windows `PINT_statfs_lookup` canonicalizes a path, extracts the root/UNC share, then fills a POSIX-like `struct statfs` from `GetDiskFreeSpace`.

State and persistence: Process-local state is limited to the static message tag counter/mutex. Attribute routines transfer heap ownership but do not persist. Time and encoding helpers are stateless. Windows filesystem statistics are read live from the OS.

Dependencies and integration points: Includes `pvfs2-internal.h`, generated request-protocol encoders, `gen-locks`, BMI, gossip logging, security capability helpers, distribution utilities, distributed-directory helpers, and byte-swap code. The functions are used by request construction, metadata caches, setattr/getattr paths, and platform abstraction code.

Risks: `PINT_copy_object_attr` can leak partially allocated fields on mid-copy failure unless callers free the destination. Some nested copies assume valid source pointers when length fields are positive. Windows `PINT_time_mark` appears to assign user time from the system `FILETIME` value rather than the user value. `decode_PVFS_sys_layout` asserts allocation success instead of returning an error. `PINT_util_get_timeval_diff` returns microseconds in `int`, so long intervals can overflow.

Test signals: Exercise deep-copy/free round trips for every attr mask combination, including partial allocation failures. Test tag wraparound around `PINT_MSG_TAG_INVALID`, BMI address encode/decode with unknown addresses, layout size-limit failure, Windows `statfs` for drive and UNC paths, and timing helpers for monotonic positive deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-util.h -->
## sources/distributed-fs/orangefs/src/common/misc/pint-util.h

Purpose: Declares common internal utility contracts and portability macros for OrangeFS code that needs attribute conversion, timing, filesystem statistics, UID/GID access, digests, and alias generation.

Important APIs and types: `PINT_CONVERT_ATTR` maps `PVFS_sys_attr` common fields into `PVFS_object_attr` masks. `PINT_time_marker` holds wall, user, and system `timeval` samples. Prototypes cover tag allocation, object-attribute copy/free, time helpers, UID/GID wrappers, `PINT_util_bytes2str`, digest lifecycle/SHA1/MD5 helpers, and `PINT_util_guess_alias`. The header also abstracts `statfs`/`fstatfs` as `PINT_statfs_*` macros or Windows declarations.

Control flow: Header-only control flow is macro expansion. `PINT_CONVERT_ATTR` resets the destination mask, copies only source-mask-selected fields, preserves explicit atime/mtime set bits, and ORs caller-provided extra mask bits. Platform `statfs` macros choose Linux `sys/vfs.h`, BSD-style `sys/mount.h`, or the Windows shim implemented in `pint-util.c`.

State and persistence: No state is defined here. State belongs to implementations or callers. Macro use mutates caller-provided structures directly.

Dependencies and integration points: Pulls in `pvfs2-internal.h`, `pvfs2-types.h`, and `pvfs2-attr.h`; many client/server modules include this to avoid platform-specific filesystem-stat and attr-mask conditionals.

Risks: `PINT_CONVERT_ATTR` is a multi-statement macro that evaluates `dest` and `src` repeatedly and should only be used with stable lvalues. The digest functions are declared here but implemented elsewhere, so link coverage is needed. The header emits compile-time errors on platforms lacking supported `statfs` headers unless the Windows path is selected.

Test signals: Compile on all supported platform macro combinations, verify attr-mask conversions for every common field and explicit time-set bit, and ensure Windows callers see the same `PINT_statfs_*` accessor contract as POSIX callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pint-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-debug.c -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-debug.c

Purpose: Converts human-readable debug keyword strings into gossip debug masks and exposes keyword iteration for tools and configuration parsing.

Important APIs and functions: `PVFS_debug_eventlog_to_mask` maps general debug keywords through `s_keyword_mask_map`; `PVFS_kmod_eventlog_to_mask` maps kernel-module keywords through `s_kmod_keyword_mask_map`; `PVFS_debug_get_next_debug_keyword` returns the keyword at a numeric position or `NULL` when exhausted. Local `debug_to_mask` implements token parsing and ordered mask mutation.

Control flow: `debug_to_mask` duplicates the input string, tokenizes on comma and space, treats a leading `-` as a mask-clear operation, searches the selected keyword table, and applies each recognized token in order. Unknown tokens are ignored. A `NULL` input returns zero.

State and persistence: Stateless apart from heap allocation of the temporary token buffer. It reads static keyword tables provided by `pvfs2-debug.h`; no persistent configuration is written.

Dependencies and integration points: Used by OrangeFS command-line tools, system initialization, and logging setup paths that accept event-log strings. Depends on `pvfs2-debug.h` for generated/static maps and on standard C allocation/string routines.

Risks: `strdup` failure is not checked before `strtok`, which can crash on allocation failure. The `negate` flag is not reset per token, so once a `-keyword` is seen, later tokens in the same string are also treated as negated. Unknown keywords silently do nothing, making typo detection difficult.

Test signals: Parse empty, `NULL`, single, multiple comma/space-separated, unknown, and ordered positive/negative keyword strings. Include a regression test showing whether negation should apply only to one token. Iterate `PVFS_debug_get_next_debug_keyword` from `-1`, valid positions, and one past the end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-hint.c -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-hint.c

Purpose: Serializes, deserializes, frees, and augments OrangeFS operation hints, including optional hints supplied through the `PVFS2_HINTS` environment variable.

Important APIs and functions: `PINT_hint_calc_size` computes transfer size for server-transferable hints. `PINT_hint_encode` writes type/string pairs plus a sentinel. `PINT_hint_decode` rebuilds a `PVFS_hint` linked list from encoded bytes. `PVFS_free_hint` releases linked-list nodes. `PINT_hint_add_environment_hints` parses `PVFS2_HINTS` entries such as `REQUEST_ID:value+CREATE_SET_DATAFILE_NODES:value`.

Control flow: Encode/decode honor `hint_types[type].transfer_to_server` and terminate streams with `NUMBER_HINT_TYPES`. Decode repeatedly reads a type, stops at the sentinel, decodes the string, and calls `PVFS_add_hint`. Environment parsing copies the env string, splits on `+`, splits name/value on `:`, maps names with `PVFS_hint_get_type`, and only adds a hint if that type is not already present.

State and persistence: Hints are heap-backed linked lists owned by callers. Environment hints are transient process input; no file or registry persistence occurs. When `NO_PVFS_HINT_SUPPORT` is defined, most functions become no-op or return empty output.

Dependencies and integration points: Relies on request-protocol encode/decode helpers, `pvfs2-hint.h` definitions, `hint_types`, `PVFS_add_hint`, `PVFS_get_hint`, and gossip logging. Integrated with client request paths that forward selected hints to servers.

Risks: `PINT_hint_decode` asserts `act_hint_type < NUMBER_HINT_TYPES`; malformed network data can abort debug builds or proceed badly in release builds. Encode checks `act->length + 8` but size calculation uses `roundup8`, so boundary behavior needs validation. `PINT_hint_add_environment_hints` does not check `malloc` before `strncpy`, returns success after some malformed entries, and uses legacy `index`.

Test signals: Round-trip multiple transferable and non-transferable hints, maximum-size hint buffers, malformed type/sentinel streams, duplicate environment hints, unknown env names, missing colon, and `NO_PVFS_HINT_SUPPORT` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-hint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-internal.h -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-internal.h

Purpose: Central internal compatibility header for non-kernel OrangeFS code, defining initialization attributes, malloc redirection policy, portable printf/scanf helpers, and canonical internal key strings used by metadata and xattr paths.

Important APIs and definitions: Defines `GCC_CONSTRUCTOR`, `GCC_DESTRUCTOR`, `GCC_UNUSED`, `PVFS_INIT`, initialization/cleanup priority constants, `llu`/`lld` cast macros, `SCANF_lld`, metadata key strings like `ROOT_HANDLE_KEYSTR`, `DIRECTORY_ENTRY_KEYSTR`, `METAFILE_DIST_KEYSTR`, distributed-directory keys, `SPECIAL_PREFIX` and `user.pvfs2.*` xattr names, plus `IO_MAX_REGIONS`.

Control flow: Header logic is compile-time conditional. Non-kernel builds include `pvfs2-config.h` and `pint-malloc.h`, optionally disable malloc redefinition, and force `PVFS_INIT(f)` to call `f()` at entry points. Integer-format macros branch on `BITS_PER_LONG` or configured `SIZEOF_LONG_INT`.

State and persistence: No runtime state is owned here, but key-string constants define persistent storage names for server metadata and optional user xattrs. Changing these constants would affect on-disk or keyval compatibility.

Dependencies and integration points: Included widely throughout OrangeFS internals. It bridges generated configure values, Linux kernel type definitions, malloc wrappers, metadata servers, clients, xattr tools, and request code needing stable key names.

Risks: Forced `PVFS_INIT(f)` means entry points may repeatedly call initialization checks; behavior depends on idempotent init functions. Format macros intentionally cast on some architectures, which can hide incorrect format strings on 64-bit builds. Key lengths include NUL bytes and must stay synchronized with string literals.

Test signals: Compile with GCC pre-4.4, modern GCC, non-GCC, kernel, 32-bit, and 64-bit configurations. Add static assertions or tests for every key length and verify xattr/keyval lookup compatibility with stored metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-types-debug.h -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-types-debug.h

Purpose: Provides inline debugging helpers for printing OrangeFS object attribute types and attrmask contents through the gossip logging subsystem.

Important APIs and functions: `PINT_attr_dump_object_type` logs the decoded `PVFS_object_type` when `PVFS_ATTR_COMMON_TYPE` is set. `PINT_attrmask_print` logs each recognized `PVFS_ATTR_*` bit in a `uint32_t` object-attribute mask.

Control flow: Both functions are `static inline` and execute only logging calls. The object-type helper switches over known values from `PVFS_TYPE_NONE` through `PVFS_TYPE_INTERNAL`; the attrmask helper checks each supported bit independently so composite masks print one line per bit.

State and persistence: Stateless. Output goes to gossip debug sinks selected elsewhere; no data is persisted by this header.

Dependencies and integration points: Includes `gossip.h` and `pvfs2-types.h`. Used by getattr/setattr and utility code when diagnosing mask conversion or server-returned attributes.

Risks: Unknown object types are silently ignored. Labels contain minor spelling/name drift for symlink and distributed-directory mask strings, which can affect log-based diagnostics. As inline header code, any change recompiles many dependent modules.

Test signals: Log masks with no bits, every individual bit, all bits, unknown future bits, and every object type including invalid values. Verify expected strings under enabled and disabled gossip masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-types-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-util.c -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-util.c

Purpose: Implements the POSIX OrangeFS public utility layer for mount-table parsing, default initialization, path-to-filesystem resolution, mount-entry lifecycle, credential generation/refresh, system-attribute copy/free, attrmask conversion, size formatting, and POSIX mode translation.

Important APIs and functions: `PVFS_util_gen_mntent`, `PVFS_util_parse_pvfstab`, `PVFS_util_add_dynamic_mntent`, `PVFS_util_remove_internal_mntent`, `PVFS_util_get_mntent_copy`, `PVFS_util_resolve`, `PVFS_util_resolve_absolute`, `PVFS_util_init_defaults`, `PINT_release_pvfstab`, `PVFS_util_gen_credential`, `PVFS_util_refresh_credential`, `PVFS_util_copy_sys_attr`, `PVFS_util_free_mntent`, `PVFS_util_copy_mntent`, `PVFS_util_sys_to_object_attr_mask`, `PVFS_util_object_to_sys_attr_mask`, `PVFS_util_make_size_human_readable`, and `PVFS_util_translate_mode` form the main surface.

Control flow: Tab parsing checks `PVFS2EP`, an explicit tabfile, `PVFS2TAB_FILE`, `/etc/fstab`, `/etc/pvfs2tab`, local `pvfs2tab`, then `/etc/mtab`; it caches parsed tabs in `s_stat_tab_array`. Mount entries split comma-separated config servers, validate common fs names, parse `flowproto`, `encoding`, `num_dfiles`, and `bmi_opts`, then remain locked behind `s_stat_tab_mutex`. Resolution uses `PVFS_path` state, direct prefix removal, then `PINT_realpath` fallback for symlinks/nonexistent basename creation cases. Security builds fork/exec `pvfs2-gencred`; non-security builds synthesize unsigned credentials from uid/gid/group list data.

State and persistence: Static mount-table arrays, dynamic mount entries, cached umask, and the tab mutex are process-local. External inputs are environment variables, tab files, passwd/group databases, current cwd, and `pvfs2-gencred`. No durable writes happen here, but dynamic mount tables persist for process lifetime.

Dependencies and integration points: Integrates with `PVFS_sys_initialize`, `PVFS_sys_fs_add`, `PVFS_sys_finalize`, path helpers, realpath, gossip, security credential helpers, request-protocol credential decode/copy, fstab/mntent platform APIs, and generated config macros.

Risks: `PVFS2EP` parsing increments `pvfs_fs_name` into an allocated string, complicating freeing. Some allocation checks are wrong or incomplete, for example checking `dest_mntent` after allocating `dest_mntent->pvfs_config_servers`. Several error paths may leave partially cached state. `PVFS_util_resolve` frees `Ppath` directly in one path instead of `PVFS_free_path`. Environment/tab parsing uses substring option detection, fixed-size tab arrays, and global mutable state.

Test signals: Parse all tabfile sources and options, malformed server strings, multiple config servers with mismatched fs names, dynamic add/remove/copy cycles, default fsid lookup, path resolution for existing paths, symlinks, relative paths, and creation of nonexistent basenames. Test credential generation in security and non-security builds, group-list fallback, attrmask conversions, sys-attr copy/free, umask caching, and human-readable sizes on 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-win-util.c -->
## sources/distributed-fs/orangefs/src/common/misc/pvfs2-win-util.c

Purpose: Windows-specific counterpart to `pvfs2-util.c`, implementing OrangeFS utility behavior with CRT/Win32-compatible path, mount-tab, umask, attrmask, size, and mode helpers while leaving credential code disabled.

Important APIs and functions: Provides `PVFS_util_gen_mntent`, `PVFS_util_parse_pvfstab`, `PVFS_util_add_dynamic_mntent`, `PVFS_util_remove_internal_mntent`, `PVFS_util_get_mntent_copy`, `PVFS_util_resolve`, `PVFS_util_resolve_absolute`, `PVFS_util_init_defaults`, `PINT_release_pvfstab`, `PVFS_util_copy_sys_attr`, `PVFS_util_free_mntent`, `PVFS_util_copy_mntent`, `PVFS_util_sys_to_object_attr_mask`, `PVFS_util_object_to_sys_attr_mask`, `PVFS_util_make_size_human_readable`, `PVFS_util_translate_mode`, and local `basename`/`dirname` replacements. Most credential helpers are inside `#if 0` and are not compiled.

Control flow: Windows tab parsing accepts `PVFS2EP` or a single explicit/`PVFS2TAB_FILE` tabfile rather than searching Unix defaults. It uses a simplified local `struct fstab` parser based on space-separated fields, validates `pvfs2` entries, splits comma-separated server addresses, and parses `flowproto`, `encoding`, and `num_dfiles`. Resolution directly checks internal mount arrays with `PINT_remove_dir_prefix`; canonicalization fallback is disabled by `#if 0`.

State and persistence: `s_stat_tab_array`, `s_stat_tab_count`, `s_stat_tab_mutex`, dynamic mount entries, and cached `_umask` are process-local. Inputs come from `PVFS2EP`, `PVFS2TAB_FILE`, and the specified tabfile. No registry or file writes are performed by this file.

Dependencies and integration points: Includes Windows CRT headers (`io.h`, `_umask`, `_snprintf`) and the same OrangeFS sysint, attr, debug, string, lock, realpath, and security headers as the POSIX version. Integrates with `PVFS_sys_initialize`, `PVFS_sys_fs_add`, and `PVFS_sys_finalize`.

Risks: Several error exits return while holding `s_stat_tab_mutex` in dynamic add/remove paths. The simplified fstab parser uses non-reentrant `strtok` despite a comment claiming thread safety, though the parser is usually under a mutex. Credential functions are disabled, so Windows callers must obtain credentials elsewhere. `memset(cred, 0, sizeof(cred))` in disabled code would be pointer-sized if re-enabled. Option support lacks `bmi_opts` parity with POSIX.

Test signals: Windows tabfile parsing for valid/malformed entries, duplicate dynamic fsids, lock-release behavior on allocation failures, path resolution with drive/relative/slash forms, local basename/dirname edge cases, attrmask parity with POSIX, size formatting via `_snprintf`, and compile checks proving disabled credential code stays excluded or is fixed before enabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/pvfs2-win-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/realpath.c -->
## sources/distributed-fs/orangefs/src/common/misc/realpath.c

Purpose: Provides `PINT_realpath`, a bundled path canonicalizer that removes `.`/`..`, follows symlinks, and works around libc realpath behavior while preserving OrangeFS mount-point interactions.

Important APIs and functions: `PINT_realpath(const char *path, char *resolved_path, int maxreslth)` is the exported function. POSIX builds manually canonicalize path components and symlinks. Windows builds delegate to `_fullpath`.

Control flow: POSIX relative paths start with `getcwd`; absolute paths start at `/`. The loop consumes slash-separated components, ignores repeated slash and `.`, backs up on `..`, copies normal components with length checks, then calls `readlink` or `SYS_readlinkat`. Before reading links, non-user-interface builds call `PVFS_util_resolve_absolute` to detect PVFS mount points and choose the readlink method. Symlink targets are spliced back into the remaining path, with absolute links restarting from the root.

State and persistence: Stateless except for temporary heap buffer `buf` used while expanding symlink targets. It reads filesystem and symlink state but does not write.

Dependencies and integration points: Depends on POSIX `getcwd`, `readlink`, `readlinkat`, `errno`, `PVFS_util_resolve_absolute`, `pvfs2-util.h`, and PVFS error codes. Used by `PVFS_util_resolve` to canonicalize paths during mount resolution and object-creation fallback.

Risks: `readlinks` increments for every path component rather than only successful symlinks, so deep non-symlink paths can hit `PVFS_ELOOP`. Many filesystem errors collapse to `-PVFS_EINVAL`, losing diagnostic precision. The PVFS mount check has side effects through `PVFS_path` resolution state. Windows behavior is only CRT absolute-path expansion and does not resolve symlinks.

Test signals: Relative/absolute paths, repeated slashes, `.`/`..`, trailing slash, nonexistent basename via caller fallback, symlink chains and loops, paths with more than 32 components, PVFS mount-boundary paths, long paths near `PATH_MAX`, and Windows `_fullpath` failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/realpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/realpath.h -->
## sources/distributed-fs/orangefs/src/common/misc/realpath.h

Purpose: Declares the OrangeFS internal `PINT_realpath` canonicalization routine implemented in `realpath.c`.

Important APIs and types: `int PINT_realpath(const char *path, char *resolved_path, int m);` takes an input path, caller-provided output buffer, and maximum output length, returning `0` or a negative PVFS error.

Control flow: No runtime logic. The header exposes a libc-like realpath contract to path-resolution code while allowing the implementation to differ between POSIX and Windows builds.

State and persistence: None. Callers own all buffers.

Dependencies and integration points: Included by `pvfs2-util.c`, `pvfs2-win-util.c`, and the implementation file. The declaration intentionally avoids pulling in large dependency headers, but callers must know PVFS error-code semantics.

Risks: The third parameter is named only `m`, which obscures expected units and relation to `resolved_path` length. There is no include guard, so repeated inclusion relies on identical declaration tolerance. No nullability or buffer-size annotations are present.

Test signals: Compile repeated includes, verify declaration matches implementation on POSIX and Windows, and exercise caller behavior for `NULL` pointers and undersized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/realpath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.c -->
## sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.c

Purpose: Maintains a process-local map from `PVFS_fs_id` to loaded `server_configuration_s` objects, with reference counting, cached-config reload support, and global minimum handle-recycle-time tracking.

Important APIs and functions: `PINT_server_config_mgr_initialize`/`finalize` create and destroy the hash table. `PINT_server_config_mgr_add_config` inserts or refcounts configs. `PINT_server_config_mgr_remove_config` decrements refs and frees configs. `PINT_server_config_mgr_reload_cached_config_interface` rebuilds cached handle mappings and recomputes minimum recycle timeout. `__PINT_server_config_mgr_get_config` and `__PINT_server_config_mgr_put_config` expose locked config access. `PINT_server_config_mgr_get_abs_min_handle_recycle_time` returns the cached minimum.

Control flow: Initialization allocates a 17-bucket quickhash table. Add checks for an existing fsid, increments refcount if found, and tells the caller to free the unused config via `free_config_flag`. Reload finalizes/reinitializes cached config state, iterates every stored configuration, expects exactly one filesystem per config, updates the minimum recycle timeout, and loads handle mappings. Get searches by fsid and intentionally leaves `s_server_config_mgr_mutex` locked until put is called.

State and persistence: Static hash table, mutex, per-entry refcounts, and minimum handle recycle timeout are process-local. The manager owns inserted config pointers and frees them with `PINT_config_release` plus `free`.

Dependencies and integration points: Depends on `quickhash`, `qlist`, `gen-locks`, gossip logging, `pint-cached-config`, and server config structures. Client builds use this manager through macros in `server-config-mgr.h`; server builds bypass it and use global server config.

Risks: The get/put lock ownership contract is subtle and can deadlock if callers call back into manager APIs or forget put. `finalize` destroys the static mutex, making reinitialize-after-finalize questionable. Reload uses asserts for expected one-filesystem config and positive timeout, so malformed configs can abort. `SC_MGR_ASSERT_OK` inside put returns from a void function while assuming lock state is valid.

Test signals: Initialize/finalize idempotence, add duplicate fsid and free flag behavior, refcounted remove, get/put lock pairing, concurrent add/remove/get, reload cached mappings across multiple configs, minimum recycle-time recomputation, and error handling for cached-config initialization/load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.h -->
## sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.h

Purpose: Declares the server-configuration manager API and maps config access differently for client and server builds.

Important APIs and definitions: Declares manager lifecycle, reload, add/remove, locked get/put, and minimum handle-recycle-time query functions. For `__PVFS2_CLIENT__`, `PINT_server_config_mgr_get_config` and `put_config` map to the manager implementations. For `__PVFS2_SERVER__`, get maps to `PINT_get_server_config()`, put is an inline no-op, and `PINT_server_config_mgr_set_config` maps to `PINT_set_server_config`.

Control flow: Header control flow is preprocessor selection by build role. Client code gets mutex-protected fsid lookup; server code bypasses fsid lookup and uses the process server config.

State and persistence: No state is stored here. It defines ownership and synchronization contracts for implementation-held or server-global config state.

Dependencies and integration points: Includes `pvfs2-internal.h` and `server-config.h`; server builds include `config-utils.h`. This header is the abstraction boundary for modules that need configuration without hard-coding client vs server storage.

Risks: If neither `__PVFS2_CLIENT__` nor `__PVFS2_SERVER__` is defined, callers see only the underscored functions and may miss the generic macros. The server put inline ignores its parameter and returns from a void function expression, which is harmless but stylistically odd. Client callers must understand that get may hold a mutex until put.

Test signals: Compile in client, server, and neutral build configurations; verify macro expansion in callers; test client get/put pairing and server get/set behavior; ensure modules do not mix underscored and macro APIs inconsistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.h -->
