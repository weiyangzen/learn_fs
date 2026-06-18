# Research: subset-b-009813

Grouped source research for the requested Samba `source3/lib` files. Each section is delimited for deterministic splitting into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbldap.c -->
## sources/user-network-fs/samba/source3/lib/smbldap.c

Purpose: LDAP helper layer for Samba passdb/account code. It wraps OpenLDAP/Netscape LDAP APIs with Samba configuration, credential, timeout, retry, talloc, UTF-8, StartTLS, referral, paged-search, and rootDSE feature-detection behavior. The central type is private `struct smbldap_state`, which persists the cached `LDAP *`, URI, bind DN/secret, anonymous flag, optional bind callback, paged-results support, failure count, idle timer, owning PID, and last rebind/use timestamps.

Important APIs include attribute readers (`smbldap_get_single_attribute`, `smbldap_talloc_single_attribute`, `smbldap_talloc_first_attribute`, `smbldap_talloc_smallest_attribute`, `smbldap_talloc_single_blob`, `smbldap_pull_sid`, `smbldap_talloc_dn`), LDAPMod builders (`smbldap_set_mod`, `smbldap_set_mod_blob`, `smbldap_make_mod`, `smbldap_make_mod_blob`), connection lifecycle (`smbldap_init`, `smbldap_set_creds`, `smbldap_free_struct`, `smbldap_get_ldap`), operations (`smbldap_search`, `smbldap_search_paged`, `smbldap_modify`, `smbldap_add`, `smbldap_delete`, `smbldap_extended_operation`, `smbldap_search_suffix`), and feature checks (`smbldap_has_control`, `smbldap_has_extension`, `smbldap_has_naming_context`).

Control flow: callers initialize state, set credentials, then each operation calls `smbldap_open` through `get_cached_ldap_connect`. Opening configures the LDAP handle, upgrades protocol to v3, starts TLS if configured, sets dereference mode, installs referral rebind callbacks, binds either by callback under root privileges or by simple bind, then schedules a tevent idle close. Operations set a local SIGALRM timeout, convert filters/DNs to UTF-8, retry on `LDAP_SERVER_DOWN` by unbinding and reconnecting, and return the final LDAP status after alarm cleanup. Paged search builds RFC 2696 page controls and returns a BER cookie between calls.

State and persistence: state is memory-only and talloc-owned, but secrets are duplicated and explicitly zeroed/freed. A global LDAP-pointer lookup list supports old rebind APIs that do not pass callback data. Connections are cached across operations, closed on idle, fork/PID mismatch, peer death, or failures. Dependencies are LDAP client libraries, Samba loadparm, tevent, talloc, charset converters, SID parsing, root privilege helpers, and debug/logging.

Risks: referral rebind can disclose credentials to referral targets, as the TODO notes. `SIGALRM` is process-global and can interfere with other alarm users. `smbldap_talloc_single_blob` leaks LDAP bervals on the multi-value error path because it returns before `ldap_value_free_len`. `smbldap_talloc_dn` leaks `utf8_dn` on conversion failure. LDAPMod builders panic on allocation/conversion failure. Tests are indirect through LDAP/passdb integration; `test_tldap.c` covers a neighboring LDAP string utility, not this connection layer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbrun.c -->
## sources/user-network-fs/samba/source3/lib/smbrun.c

Purpose: shell-command execution helper for Samba code that needs to run configured commands as the active SMB user. It defines the global `struct current_user current_user` used to pick the child UID/GID, creates optional temporary output capture, drops privileges in the child, and invokes `/bin/sh -c`.

Important functions are `smbrun`, `smbrun_no_sanitize`, `smbrunsecret`, and private `smbrun_internal`/`setup_out_fd`. `smbrun` sanitizes shell expansion by passing the command through `escape_shell_string`; `smbrun_no_sanitize` is reserved for known-safe shell uses. `smbrunsecret` sends a secret to the child over stdin through a pipe.

Control flow: output capture creates an unlinked `tmpdir()/smb.XXXXXX` file with group/other permissions masked. `smbrun_internal` preserves the existing SIGCLD handler, forks, waits in the parent with EINTR handling, rewinds the output fd, and returns child exit status. The child installs normal child handling, dup2s the output fd to stdout when requested, calls `become_user_permanently`, verifies real/effective UID/GID unless in non-root mode, closes descriptors from 3 upward, and executes `/bin/sh`. `smbrunsecret` follows similar parent/child logic but dup2s a pipe to stdin and writes the secret from the parent.

State and persistence: no durable state is written. Output temp files are unlinked immediately and survive only via fd. The code depends on global process identity, signal handlers, `/bin/sh`, Samba privilege helpers, `tmpdir`, and `closefrom`.

Risks: all commands still run through a shell, so caller-provided content must be tightly controlled; the unsanitized entry point is explicitly dangerous outside trusted printing/config contexts. `smbrunsecret` does not sanitize `cmd`, writes the secret once without retrying partial writes, and calls `fsync` on a pipe. Test signals are mostly integration-level: correct UID/GID drop, fd hygiene, output capture, shell quoting, and child exit status behavior should be covered by command-execution and printer-command tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/smbrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/srprs.c -->
## sources/user-network-fs/samba/source3/lib/srprs.c

Purpose: implementation of a small recursive-descent parsing helper library. It advances a `const char **` parse cursor only on success and appends matched text to an optional `cbuf`, which makes it useful for simple line, quoted-string, charset, and hex parsers.

Important functions mirror the header: `srprs_skipws`, `srprs_char`, `srprs_str`, `srprs_charset`, `srprs_charsetinv`, `srprs_quoted_string`, `srprs_hex`, `srprs_nl`, `srprs_eos`, `srprs_eol`, `srprs_line`, and `srprs_quoted`. `srprs_quoted_string` supports continuation across invocations through a `bool *cont`; `srprs_quoted` supports `\"`, `\\`, and two-digit hex escapes.

Control flow is intentionally simple. Matchers snapshot the incoming cursor and, for buffer-writing functions, the `cbuf` position. On failure they leave the cursor unchanged and restore the buffer position. `srprs_str` calculates the remaining null-terminated input length before `memcmp` to avoid reading past the buffer. Newline parsing recognizes CRLF first, then single LF or CR.

State and persistence: no global or durable state exists. All parse state is caller-owned via the input pointer and `cbuf`. Dependencies are `replace.h`, locale character classification, `cbuf`, and assertions.

Risks: all input is assumed null-terminated. `srprs_skipws` passes `char` values to `isspace` without unsigned-char casting, which can be undefined for negative bytes under some locales. `srprs_hex` accepts fewer than the requested number of hex digits as long as `sscanf` parses something, despite the `len` wording. Test signals should focus on cursor rollback, cbuf rollback, CR/LF variants, continuation strings, invalid escapes, and high-bit input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/srprs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/srprs.h -->
## sources/user-network-fs/samba/source3/lib/srprs.h

Purpose: public interface and contract documentation for the simple recursive parser implemented in `srprs.c`. It forward-declares `struct cbuf` and exposes cursor-based matching functions that are composable in larger parsers.

Important APIs are the whitespace, character, string, charset, quoted-string, hex, newline, end-of-string, line, and quoted escaped-string matchers. The documentation states the key semantic guarantee: functions update the parse position and output only if they match, otherwise they leave arguments unchanged, with `cbuf` rollback guaranteed up to the current write position.

Control flow is not in the header, but its comments describe parser composition: callers pass `const char **ptr`, inspect boolean returns, and may use a `cbuf` for accumulated output. The continuation example for `srprs_quoted_string` is especially important because it documents multi-call parsing where an unterminated quote can be accepted temporarily when `cont` is supplied.

State and persistence: the header declares no storage. Parser state is held by caller variables. Dependencies are only C/Samba base types and `struct cbuf` at compile time.

Risks: the API relies on callers understanding pointer ownership and null-terminated input; it has no length-bounded variants. The comments say `srprs_hex` matches a hex string of maximum length, while many callers might expect exactly that length. Test signals for consumers should verify they do not assume destructive parsing on failure and that they handle `NULL` output buffers only for functions whose docs allow it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/srprs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/string_replace.c -->
## sources/user-network-fs/samba/source3/lib/string_replace.c

Purpose: character mapping helper used by VFS filename translation, notably CATIA/macOS private-use mappings. It builds sparse Unicode mapping tables and applies them to UCS-2 converted filenames in either Unix-to-Windows or Windows-to-Unix direction.

Important types and functions: private `struct char_mappings` stores a 255-entry table with two direction slots, indexed by `enum vfs_translate_direction`. `string_replace_init_map` parses mapping strings of the form `0xNN:0xNN`, `string_replace_allocate` converts an input name to UCS-2, applies mapped code points, and converts back. `macos_string_replace_map` provides the standard control/reserved character mapping into U+F001 and nearby private-use values.

Control flow: initialization allocates a `MAP_NUM` array of table pointers. For each mapping string it parses Unix and Windows values with `strtol`, lazily allocates tables for the ranges containing those code points, initializes identity mappings, and then sets both forward and reverse slots. Allocation converts `name_in` with `push_ucs2_talloc`, iterates each UCS-2 code unit, skips unmapped ranges, substitutes mapped entries in the requested direction, then returns a newly allocated Unix string with `pull_ucs2_talloc`.

State and persistence: mapping tables are talloc-owned by the caller’s context; there is no global mutable state except the exported constant string. Dependencies include Samba charset conversion, talloc, VFS direction enums, and debug logging.

Risks: `MAP_SIZE` is `0xFF`, so range math is unusual and should be treated carefully at boundaries. `errno` is not cleared before `strtol`, making invalid mapping detection weak. The `connection_struct *conn` parameter is unused. Tests should cover bidirectional mapping, unmapped identity behavior, malformed map entries, high code points near range boundaries, and conversion failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/string_replace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/string_replace.h -->
## sources/user-network-fs/samba/source3/lib/string_replace.h

Purpose: public declaration for the filename character replacement mapping subsystem. It hides `struct char_mappings` and exposes initialization and application functions to VFS modules and filename translation code.

Important APIs are `string_replace_init_map`, which returns a talloc-owned sparse map array from configuration strings, `string_replace_allocate`, which maps a supplied name into a newly allocated output string, and `macos_string_replace_map`, the built-in mapping list for macOS-problematic characters.

Control flow contract: callers create or receive a mapping table once, then pass it with a direction enum to map names as they cross Unix/Windows boundaries. The output is allocated under the caller-provided `mem_ctx`; the integer return is `0` on success or an `errno` value on conversion/allocation failure.

State and persistence: no header-level storage beyond the extern map constant. Ownership of mapping tables and mapped names is talloc-based. Dependencies include `TALLOC_CTX`, `connection_struct`, and `enum vfs_translate_direction`, so consumers must include Samba connection/VFS context before using the API.

Risks and tests: because the map type is opaque, callers cannot validate internals and must rely on `string_replace_init_map` succeeding. The API allows `cmaps == NULL` for identity conversion in the implementation, so callers should test that no-map behavior still returns a converted copy. Test signals include macOS map round trips and propagation of malformed configuration entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/string_replace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute.c -->
## sources/user-network-fs/samba/source3/lib/substitute.c

Purpose: Samba string substitution engine for `%` variables used in configuration, paths, commands, and service/user contexts. It maintains connection/user identity strings and expands standard, specified, advanced, and full substitution sets into talloc-owned output strings.

Important state includes static `local_machine`, `remote_machine`, `remote_proto`, `sub_peeraddr`, `sub_peername`, `sub_sockaddr`, and global `userdom_struct current_user_info`. Important APIs include setters/getters for remote protocol, machine names, socket IDs, and current user info, plus `standard_sub_basic`, `talloc_sub_basic`, `talloc_sub_specified`, `talloc_sub_advanced`, and `talloc_sub_full`.

Control flow: machine-name setters trim, filter through `SAFE_NETBIOS_CHARS`, lower-case, and optionally lock the value permanently. `sub_set_socket_ids` normalizes IPv4-mapped peer addresses and stores peer name/socket address. `talloc_sub_basic` loops over `%` markers, replacing `%U`, `%G`, `%D`, `%I/%J`, `%i/%j`, `%L`, `%N`, `%M`, `%R`, `%T/%t`, `%a`, `%d`, `%h`, `%m`, `%v`, `%w`, `%V`, and `%$(ENV)` with runtime values. `talloc_sub_specified` first substitutes explicitly supplied user/group/domain fields, then invokes basic substitution. `talloc_sub_advanced` handles service/path/home/group/user-specific tokens, and `talloc_sub_full` chains advanced then basic.

State and persistence: state is process-global and memory-only; `sub_peername` is talloc-owned off NULL and replaced when socket IDs change. Dependencies are loadparm, passwd/group lookups, hostname/version/time helpers, secrets/auth includes, CTDB VNN, and generic string replacement in `substitute_generic.c`.

Risks: process-global substitution state can be stale or cross-context-sensitive in long-lived daemons. Environment expansion logs unset variables and can expose deployment-specific values into configured strings. Several replacements depend on NSS/group lookups and may block. `standard_sub_basic` uses `strncpy` into caller storage and depends on caller-supplied length. Test signals should cover each substitution token, permanent-name behavior, IPv6 path-safe conversion, NULL source handling, and talloc ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute.h -->
## sources/user-network-fs/samba/source3/lib/substitute.h

Purpose: public interface for Samba substitution state and expansion functions. It declares setters/getters for process connection identity and the talloc-returning expansion functions used by configuration and service code.

Important APIs: `set_remote_proto`, `set_local_machine_name`, `get_local_machine_name`, `set_remote_machine_name`, `get_remote_machine_name`, `sub_set_socket_ids`, `set_current_user_info`, `get_current_username`, `get_current_user_info_domain`, `standard_sub_basic`, `talloc_sub_basic`, `talloc_sub_specified`, `talloc_sub_advanced`, and `talloc_sub_full`.

Control flow contract: callers first seed runtime context such as machine names, socket addresses, and user info, then call a substitution helper matching their context. `standard_sub_basic` mutates a caller buffer, while all `talloc_sub_*` APIs return allocated strings and must be freed through talloc context lifetime.

State and persistence: the state lives in the implementation as process globals; the header does not expose storage. Dependencies are Samba base types, `TALLOC_CTX`, and UID/GID types.

Risks and test signals: header users must choose the right expansion layer because basic, specified, advanced, and full token sets differ. Callers must not assume thread isolation. Tests should verify API-level ownership, permanent machine-name semantics, and that buffer-based `standard_sub_basic` truncation is acceptable for callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute_generic.c -->
## sources/user-network-fs/samba/source3/lib/substitute_generic.c

Purpose: generic allocated-string substitution helpers used by `substitute.c` and other Samba utilities. It adapts lower-level `realloc_string_sub_raw` to the historic Samba calling convention that mutates/reallocates a talloc-allocated string.

Important APIs are `realloc_string_sub2` and `realloc_string_sub`. `realloc_string_sub2` accepts options for unsafe-character replacement and trailing-dollar handling; `realloc_string_sub` is the common safe wrapper that removes unsafe shell/path characters and disallows trailing dollar behavior.

Control flow: the function validates non-null/non-empty input, optionally selects `STRING_SUB_UNSAFE_CHARACTERS` and `_` as replacement policy, then calls `realloc_string_sub_raw` with `replace_once=false`. On failure it logs an out-of-memory error and returns `NULL` without touching the caller’s existing pointer, matching the documented odd convention that the string is usually allocated on `talloc_tos`.

State and persistence: no global state. Returned strings remain talloc-owned according to the lower-level realloc helper. Dependencies are `includes.h`, Samba string wrappers, debug logging, and raw substitution logic elsewhere in the tree.

Risks: returning `NULL` for both invalid arguments and allocation failure makes diagnosis caller-dependent. Because the old pointer may still be valid on failure, callers must not overwrite their only reference before checking. Tests should cover repeated replacements, unsafe character filtering, trailing-dollar cases, empty pattern rejection, and preserving the original string on allocation failure paths where injectable alloc failure is available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/substitute_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysacls.c -->
## sources/user-network-fs/samba/source3/lib/sysacls.c

Purpose: Samba system ACL abstraction. It provides a normalized `sys_acl_*` interface over Samba’s internal `struct smb_acl_t` and dispatches fd ACL operations to the platform’s default VFS ACL backend when compiled.

Important APIs include ACL entry iteration and inspection (`sys_acl_get_entry`, `sys_acl_get_tag_type`, `sys_acl_get_permset`, `sys_acl_get_qualifier`, `sys_acl_get_perm`), construction/mutation (`sys_acl_init`, `sys_acl_create_entry`, `sys_acl_set_tag_type`, `sys_acl_set_qualifier`, `sys_acl_clear_perms`, `sys_acl_add_perm`, `sys_acl_set_permset`), rendering (`sys_acl_to_text`), fd operations (`sys_acl_get_fd`, `sys_acl_set_fd`, `sys_acl_delete_def_fd`), and `no_acl_syscall_error`.

Control flow: callers build an ACL with `sys_acl_init`, append entries, set tag/qualifier/permission fields, and pass it to VFS-backed setters. Iteration uses `acl_d->next`, reset by `SMB_ACL_FIRST_ENTRY`, then advanced by `SMB_ACL_NEXT_ENTRY`. fd operations compile-time dispatch to POSIX, AIX, Solaris/UnixWare, HPUX, or no-ACL stubs returning `ENOTSUP`/`ENOSYS`.

State and persistence: ACL structures are talloc-owned and memory-only until passed to backend setters, which persist ACLs on filesystem objects. Dependencies are platform ACL modules, passwd/group name lookups, talloc, VFS handle/files structures, and Samba debug classes.

Risks: `SMB_ACL_ENTRY_T` pointers become unstable after operations that may reorder/reallocate ACL entries, as the file comment warns. `sys_acl_get_tag_type` and similar accessors do little NULL validation. Rendering uses passwd/group lookups and can return numeric group IDs when lookup fails. Tests should exercise backend dispatch, no-ACL errno recognition, ACL text output, invalid tags/perms, iteration order, and descriptor invalidation assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysacls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas.c

Purpose: high-level quota dispatcher. It maps a Samba path/device to a mount path, block device, and filesystem type, optionally delegates to configured quota commands, and otherwise calls filesystem-specific quota backends or default VFS quota wrappers.

Important helpers are `sys_dev_to_bdev`, multiple `sys_path_to_bdev` variants, `command_get_quota`, `command_set_quota`, and exported `sys_get_quota`/`sys_set_quota`. The `sys_quota_backends` table registers JFS2, XFS/GFS/GFS2, and NFS backends when compiled.

Control flow: `sys_get_quota` and `sys_set_quota` first try `lp_get_quota_command`/`lp_set_quota_command` via `file_lines_ploadv`, using argv-style execution and parsing/formatting `SMB_DISK_QUOTA` fields. If no command is configured (`ENOSYS`), they resolve mount metadata. Linux-like systems prefer `/proc/self/mountinfo`; fallback walks `realpath` components to the mount root and scans `setmntent`. Then they match `fs` against specialized backends, else call `sys_get_vfs_quota`/`sys_set_vfs_quota`.

State and persistence: no durable state except external quota changes. `sys_dev_to_bdev` caches inability to open `/proc/self/mountinfo` in a static boolean. Dependencies include loadparm substitution, mount tables, stat wrappers, quota backend symbols, talloc, command execution helpers, and `SMB_DISK_QUOTA`.

Risks: command output parsing expects seven fields even though it initializes and scans an eighth `bsize` field, so bsize override handling is suspect. Mountinfo parsing is Linux-specific and assumes field positions. Fallback realpath/stat mount discovery can race with remounts. Tests should cover command delegation, malformed command output, mountinfo parsing, filesystem backend selection, NFS unsupported set, and cleanup of talloc-owned mount strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_4A.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_4A.c

Purpose: quota backend for systems with the 4-argument `quotactl(int cmd, char *special, qid_t id, caddr_t addr)` style, historically HPUX/IRIX-like platforms.

Important APIs are `sys_get_vfs_quota` and `sys_set_vfs_quota`, compiled only under `HAVE_SYS_QUOTAS` and `HAVE_QUOTACTL_4A`. Compatibility macros normalize quota command names, group quota support, quota block size, and alternate `dqblk` field names.

Control flow: get switches on Samba quota type. User/group quota reads call `quotactl(QCMD(Q_GETQUOTA,...), bdev, id, &D)` and tolerate `EDQUOT`; filesystem quota types query the current UID/GID and set `QUOTAS_DENY_DISK` when the query succeeds. Results are copied from `struct dqblk` into `SMB_DISK_QUOTA` with `QUOTABLOCK_SIZE`. Set translates Samba limits into native block units, calls `Q_SETQLIM` for user/group IDs, and for filesystem quota enable/disable only verifies whether the current enforcement flags already match because real toggling is documented as unreliable.

State and persistence: quota changes persist through the OS quota subsystem. No local state is stored. Dependencies are platform quota headers and Samba quota types.

Risks: group quota paths only exist under `HAVE_GROUP_QUOTA`, so unsupported group requests fall through to `ENOSYS`. Filesystem quota toggling is not implemented, only compared. Block-size conversion can truncate. The file compiles a dummy symbol when unsupported. Tests are platform/build-matrix tests that mock or exercise 4A `quotactl`, block conversion, EDQUOT handling, and unsupported quota types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_4A.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_4B.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_4B.c

Purpose: quota backend for BSD-derived `quotactl(const char *path, int cmd, int id, char *addr)` systems, with Darwin-specific privilege workaround support.

Important functions are private translators `xlate_qblk_to_smb`, `xlate_smb_to_qblk`, syscall wrapper `sys_quotactl_4B`, and exported `sys_get_vfs_quota`/`sys_set_vfs_quota`. It maps native `struct dqblk` fields to `SMB_DISK_QUOTA` and sets `QUOTAS_ENABLED | QUOTAS_DENY_DISK` on successful reads.

Control flow: `sys_get_vfs_quota` selects user, current-user filesystem, group, or current-group filesystem quota by choosing USRQUOTA/GRPQUOTA and supplied or effective IDs. `sys_quotactl_4B` logs the operation, optionally becomes root for Darwin HFS, calls `quotactl`, suppresses noisy logs for common unsupported/unconfigured quota errors, and restores privileges. Set converts limits and calls `Q_SETQUOTA` for the requested ID/type.

State and persistence: native quota state is persisted by the filesystem. There is no local state. Dependencies include BSD quota headers, optional UFS/JFS headers, Samba privilege helpers, and quota structs.

Risks: filesystem quota types are treated as quota records for the current effective UID/GID rather than quota-enforcement toggles, unlike XFS. Debug detection of get/set via bit tests on `cmd` is approximate. The Darwin root workaround increases privilege-sensitive surface. Tests should cover translation with byte-vs-block native fields, Darwin root enter/leave, ENOTSUP/EINVAL handling, and all four Samba quota types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_4B.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_jfs2.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_jfs2.c

Purpose: AIX JFS2 quota backend. It exists because JFS2 uses different quota commands from the generic 4B backend and requires root even for some documented read cases.

Important APIs are `sys_get_jfs2_quota` and `sys_set_jfs2_quota`, plus private `sys_quotactl_JFS2`. Compilation is guarded by `HAVE_JFS_QUOTA_H` and `Q_J2GETQUOTA`.

Control flow: `sys_get_jfs2_quota` selects user/group or current effective user/group based on `enum SMB_QUOTA_TYPE`, calls `sys_quotactl_JFS2` with `Q_J2GETQUOTA`, and copies `quota64_t` fields into `SMB_DISK_QUOTA` using `QUOTABLOCK_SIZE` and `QUOTAS_ENABLED | QUOTAS_DENY_DISK`. `sys_quotactl_JFS2` always becomes root around `quotactl`, logs unsupported/unconfigured errors selectively, and returns the native result. Setting quota is intentionally unsupported and returns `ENOSYS` because JFS2 limit classes do not map cleanly to Samba’s model.

State and persistence: read-only from Samba’s perspective; setting is not persisted because it is refused. Dependencies are AIX JFS quota headers, Samba privilege helpers, and quota types.

Risks: unconditional root elevation around reads must be audited for balanced `unbecome_root` under all paths; this file does restore after the call. Lack of set support means administrator UI paths must handle `ENOSYS`. Tests should cover all get quota types on AIX/JFS2, unsupported type behavior, and set returning `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_jfs2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_linux.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_linux.c

Purpose: Linux default quota backend using Linux `quotactl` and `struct dqblk` semantics. It is compiled for `HAVE_SYS_QUOTAS` plus `HAVE_QUOTACTL_LINUX`.

Important APIs are `sys_get_vfs_quota` and `sys_set_vfs_quota`. They translate between Linux quota fields and Samba `SMB_DISK_QUOTA`, including block size normalization and inode limits.

Control flow: get validates pointers, zeroes output, switches on quota type, calls `quotactl(Q_GETQUOTA)` for supplied UID/GID or effective UID/GID, and for filesystem quota types treats successful current-user/current-group reads as evidence for `QUOTAS_DENY_DISK`. It stores `curblocks` as `dqb_curspace / QUOTABLOCK_SIZE`. Set fills `dqb_bsoftlimit`, `dqb_bhardlimit`, inode limits, and `dqb_valid = QIF_LIMITS` for user/group writes. For filesystem quota types it does not toggle enforcement; it compares current query success with requested `QUOTAS_DENY_DISK` and succeeds only if already matching, else returns `EPERM`.

State and persistence: quota records are persisted by the Linux kernel/filesystem. No local state. Dependencies are `<sys/quota.h>`, Samba quota types, debug logging, and platform macros.

Risks: quota enforcement toggling is deliberately not implemented for fs quota types. `curspace / bsize` truncates partial blocks. Pointer validation panics instead of returning errors. Tests should cover user/group get/set, filesystem type comparison behavior, block-size conversions, `QIF_LIMITS`, and unsupported type `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_nfs.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_nfs.c

Purpose: NFS quota backend using the remote rquota RPC protocol. It supports reading user quotas from an NFS server and explicitly does not support setting quotas.

Important functions are XDR helpers `my_xdr_getquota_args`/`my_xdr_getquota_rslt`, exported `sys_get_nfs_quota`, and `sys_set_nfs_quota`. It consumes an NFS device string of the form `host:/export/path` and returns `SMB_DISK_QUOTA`.

Control flow: get validates inputs and only accepts `SMB_USER_QUOTA_TYPE`. It splits `bdev` at `:`, uses the host to create a UDP RPC client for `RQUOTAPROG/RQUOTAVERS`, authenticates with `authunix_create_default`, calls `RQUOTAPROC_GETQUOTA` with a two-second timeout, decodes rquota status and fields, maps status 1 to quota values, status 2 to no-limit quota, and status 3 to `EPERM`. `ECONNREFUSED` from the RPC call is treated as success/no quotas. Cleanup destroys auth/client handles and frees the host buffer.

State and persistence: read-only; no local persistent state. Dependencies are SunRPC headers/libraries, `rpcsvc/rquota.h`, Samba quota structs, and memory/debug helpers.

Risks: only UDP rquota v1 is used, with a fixed short timeout. Only user quotas are supported; group/fs quota types return `ENOSYS`, and set always returns `ENOSYS`. Device-string parsing is fragile for unusual NFS mount source syntax. Tests should cover status-code mapping, connection refused behavior, malformed `host:path`, unsupported quota types, and cleanup on RPC/auth failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_xfs.c -->
## sources/user-network-fs/samba/source3/lib/sysquotas_xfs.c

Purpose: XFS/GFS/GFS2 quota backend using XFS quota-manager commands and `fs_disk_quota`/`fs_quota_stat`. It supports user/group quota records and enforcement/accounting state for filesystem quota types.

Important APIs are `sys_get_xfs_quota` and `sys_set_xfs_quota`. Compatibility macros normalize XFS command names on IRIX-like systems, and `BBSIZE` defines the native block unit.

Control flow: get switches by quota type. User/group record reads call `Q_XGETQUOTA`; `ENOENT` is normalized to success with zero quota because XFS reports missing quota records that way. Filesystem quota reads call `Q_XGETQSTAT` and inspect `XFS_QUOTA_UDQ_*` or `XFS_QUOTA_GDQ_*` flags to set `QUOTAS_DENY_DISK` or `QUOTAS_ENABLED`. Set converts block limits to basic blocks, sets `FS_DQ_LIMIT_MASK`, and uses `Q_XSETQLIM` for user/group. For filesystem quota types it queries status, turns enforcement/accounting on or off using `Q_XQUOTAON`/`Q_XQUOTAOFF` according to requested flags, and returns failure if neither enabled nor deny-disk is requested.

State and persistence: all state is kernel/filesystem quota state. No local storage. Dependencies include XFS quota headers, Linux/IRIX quota macros, Samba quota types, and privilege inherited from caller.

Risks: quota-on/off sequencing can partially succeed if one call succeeds and a later call fails. Return values for intermediate status queries are not always checked. Group quota support is forced by macro in this file. Tests should cover `ENOENT` normalization, fs state flag mapping, q_on/q_off transitions, block conversion, and invalid `qflags`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/sysquotas_xfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/system.c -->
## sources/user-network-fs/samba/source3/lib/system.c

Purpose: central portability wrapper layer for common OS calls in Samba. It normalizes EINTR behavior, stat metadata conversion, allocation/fallocate/mknod availability, capabilities, random number wrappers, supplementary groups, device number extraction, realpath, and `/proc/self/fd` helpers.

Important APIs include `sys_send`, `sys_recvfrom`, `sys_fcntl_ptr/long/int`, `init_stat_ex_from_stat`, `sys_stat`, `sys_fstat`, `sys_lstat`, `sys_fstatat`, `sys_posix_fallocate`, `sys_fallocate`, `sys_fdopendir`, `sys_mknod`, `sys_mknodat`, `sys_getwd`, `set_dmapi_capability`, `set_dac_override_capability`, `sys_random`, `sys_srandom`, `setgroups_max`, `getgroups_max`, `sys_getgroups`, `sys_setgroups`, `unix_dev_major`, `unix_dev_minor`, `sys_realpath`, `sys_have_proc_fds`, and `sys_proc_fd_path`.

Control flow: stat wrappers call native stat variants, force directory size to zero, and convert to `struct stat_ex`, calculating birth time from native birthtime when available or the minimum non-zero c/m/a time. Timestamp update helpers preserve or recalculate calculated birthtime. Allocation wrappers return `ENOSYS` when unavailable. Capability helpers try POSIX capabilities and fall back to `become_root`/`unbecome_root` for DAC override. Group wrappers handle broken int-based getgroups and BSD effective-gid requirements.

State and persistence: static state includes capability availability, `/proc/self/fd` detection, and process start via related time functions elsewhere. Most operations reflect OS state but do not persist data except syscalls such as mknod/fallocate and credential/capability changes. Dependencies are extensive: system headers, Samba setid, time utilities, debug, capability library, and platform macros.

Risks: wrappers can hide platform-specific semantics, especially calculated birthtime, group truncation on BSD, and capability fallback to root. `sys_send` retries EAGAIN/EWOULDBLOCK in a tight loop, which can spin on nonblocking sockets. Tests should cover stat_ex conversion, fake directory create times, group set/get variants, capability fallback, proc-fd detection, and ENOSYS behavior under feature-matrix builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/system_smbd.c -->
## sources/user-network-fs/samba/source3/lib/system_smbd.c

Purpose: smbd-linked system wrapper focused on Unix group membership lookup for a user without letting winbind remote membership expansion leak into local Unix group enumeration.

Important functions are private `getgrouplist_getgrset`, `getgrouplist_internals`, `sys_getgrouplist`, and public `getgroups_unix_user`. The implementation selects native `getgrouplist` when available, AIX `getgrset` when available, or a root-only `initgroups` fallback.

Control flow: `sys_getgrouplist` temporarily disables winbind environment lookups, performs the platform-specific group-list call, then re-enables winbind only if it was not already disabled. The fallback saves current supplementary groups, calls `initgroups`, sets effective/real gid to the primary gid to normalize returned groups, reads the group list, restores IDs, and restores original groups with `sys_setgroups`, panicking if restoration fails. `getgroups_unix_user` first tries a bounded stack array, reallocates if the platform reports more groups, and then builds a unique talloc-owned group array with the primary gid first.

State and persistence: it temporarily mutates process group credentials and winbind environment state, but intends to restore them before returning. Output groups are talloc-owned. Dependencies are smbd privilege helpers, winbind client toggles, passwd/group APIs, and `sys_setgroups`.

Risks: the fallback is privilege-sensitive and process-global; failure to restore groups is fatal. Disabling winbind can affect concurrent code in the same process. Stack VLA size depends on `getgroups_max` capped to 128. Tests should cover native and fallback paths, duplicate primary gid handling, insufficient buffer retry, winbind on/off restoration, and failure injection for group restoration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/system_smbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tallocmsg.c -->
## sources/user-network-fs/samba/source3/lib/tallocmsg.c

Purpose: messaging hook that lets another process request a talloc memory report from a Samba process via `MSG_REQ_POOL_USAGE`.

Important functions are private `pool_usage_filter` and public `register_msg_pool_usage`. The filter expects exactly one passed file descriptor and writes `talloc_full_report_printf(NULL, f)` to it.

Control flow: `register_msg_pool_usage` starts a persistent `messaging_filtered_read_send` request on the message context’s tevent loop using `pool_usage_filter`. The filter ignores other message types, validates fd count, wraps the fd with `fdopen_keepfd`, writes the talloc report, closes the stdio stream, and returns false so the filtered read remains active rather than completing.

State and persistence: no durable state. The persistent tevent request is owned by the supplied `mem_ctx`; reports are emitted to caller-supplied fd. Dependencies are Samba messaging, tevent, talloc reporting, debug, and `fdopen_keepfd`.

Risks: a requester with messaging access can trigger potentially large memory reports and learn allocation layout. The code expects exactly one fd; missing fd just logs and ignores. Closing the `FILE *` around `fdopen_keepfd` should not close the original fd, matching helper semantics. Tests should cover registration failure, message type filtering, bad fd counts, repeated requests, and report output to an fd.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tallocmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tallocmsg.h -->
## sources/user-network-fs/samba/source3/lib/tallocmsg.h

Purpose: public declaration for registering the talloc pool usage messaging handler.

Important API: `register_msg_pool_usage(TALLOC_CTX *mem_ctx, struct messaging_context *msg_ctx)`. It forward-declares `struct messaging_context` and includes `replace.h`/`talloc.h` for base types.

Control flow contract: callers with a messaging context call the function during process initialization. The implementation installs a long-lived filtered read request that listens for `MSG_REQ_POOL_USAGE` and writes reports to a received fd.

State and persistence: the header exposes no state. Lifetime is controlled by the passed talloc context in the implementation. Integration points are Samba messaging setup and diagnostic tooling that sends the request message.

Risks and tests: callers must ensure the `mem_ctx` outlives the desired diagnostic registration. The API has no return value, so registration failure is only logged. Test signals should validate that services register it at startup where expected and that failure to register does not break service operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tallocmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tdb_validate.c -->
## sources/user-network-fs/samba/source3/lib/tdb_validate.c

Purpose: validation and backup/repair helper for Samba TDB databases. It verifies TDB structural integrity and caller-specific records, creates rotating backups for valid databases, and attempts restore from backup when corruption is detected.

Important functions are `tdb_validate`, `tdb_validate_open`, `tdb_validate_and_backup`, and private helpers `tdb_validate_child`, `tdb_copy`, `tdb_backup`, `tdb_backup_with_rotate`, and `rename_file_with_suffix`. The status struct tracks `tdb_error`, `bad_freelist`, `bad_entry`, `unknown_key`, and `success`.

Control flow: `tdb_validate` forks a child so validation crashes/panics do not kill the parent. The child runs `tdb_check`, validates freelist, traverses records with the caller callback, and exits with status. The parent waits and maps exit/signal/stop to a nonzero result. Backup opens and locks the source TDB, copies all records into `dst.tmp`, verifies traversal count, fsyncs, and atomically renames. `tdb_validate_and_backup` backs up valid DBs to `.bak` with `.old` rotation; for invalid DBs it checks `.bak`, moves corrupt originals to `.corrupt`, and restores the backup, with ENOSPC fallback options.

State and persistence: it mutates filesystem state by creating `.bak`, `.old`, `.tmp`, and `.corrupt` files and renaming/restoring databases. Dependencies are TDB APIs, Samba `util_tdb`, fork/wait, stat/rename/unlink/fsync, talloc, and debug.

Risks: forked validation inherits process state; open locks and callbacks must be fork-safe. Backup success is ignored after a valid validation, intentionally returning success even if backup creation fails. ENOSPC fallback may rename the source as last resort during restore. Tests should cover child signal handling, corrupt freelist/record callback statuses, backup rotation, ENOSPC retry paths, and restore from valid/invalid backups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tdb_validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tdb_validate.h -->
## sources/user-network-fs/samba/source3/lib/tdb_validate.h

Purpose: public interface for TDB validation and backup handling. It defines the validation status structure, callback type, and three validation entry points.

Important API/type details: `struct tdb_validation_status` is passed to validation callbacks through the generic private state pointer and lets callbacks mark bad entries or unknown keys while setting `success=false`. `tdb_validate_data_func` matches `tdb_traverse`-style callbacks. `tdb_validate` operates on an open TDB, `tdb_validate_open` opens by path, and `tdb_validate_and_backup` validates plus backup/restore side effects.

Control flow contract: callbacks should inspect each `TDB_DATA` key/value, update the provided status, and return traversal-compatible status. A zero return from validation APIs means good or restored; nonzero means validation/repair failed.

State and persistence: the header itself has no state. `tdb_validate_and_backup` is documented to write `.bak`, `.bak.old`, and `.corrupt` files as needed, so callers must pass paths where those sidecar files are acceptable.

Risks and tests: consumers must understand that backup creation failure after successful validation is not surfaced as failure by the implementation. Callback misuse can produce false success. Tests should include callback status flag behavior and path permissions for sidecar backup files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tdb_validate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/test_adouble.c -->
## sources/user-network-fs/samba/source3/lib/test_adouble.c

Purpose: cmocka regression tests for AppleDouble parsing safety in `adouble.c`, included directly into the test translation unit to access implementation internals.

Important fixtures are byte arrays `ad_basic`, `ad_finderinfo1/2/3`, `ad_name`, and `ad_date1/2`, plus helper `parse_adouble`. Test cases exercise valid FinderInfo/resource fork layouts, empty entries, and dangerous offset/length combinations for FinderInfo, name, and date entries.

Control flow: group setup creates a talloc stackframe and teardown frees it. `parse_adouble` allocates an `adouble`, copies the fixture into `ad->ad_data`, and calls `ad_unpack(ad, 2, filesize)`. Individual tests assert whether parsing succeeds and whether `ad_get_entry` returns non-null/null for expected entries. `main` optionally accepts a cmocka filter, emits subunit output, and runs the test group.

State and persistence: no persistence. State is per-test talloc memory and static fixture data. Dependencies are `adouble.c`, cmocka, talloc, and AppleDouble constants such as `ADEID_FINDERI` and `ADEID_FILEDATESI`.

Risks: direct inclusion of `adouble.c` can hide linkage issues and couples the test to implementation details. The test names contain `abouble` typos but are harmless. The key signal is bounds-check coverage for offset+length validation and empty entry handling, guarding against out-of-bounds reads from malformed AppleDouble metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/test_adouble.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/test_tldap.c -->
## sources/user-network-fs/samba/source3/lib/test_tldap.c

Purpose: cmocka test suite for LDAP DN/filter unescape behavior in `tldap.c`, included directly into the test translation unit.

Important tests are `test_tldap_unescape_ldapv3` and `test_tldap_unescape_ldapv2`. Both verify that escaped representations of `(&(objectclass=group)(cn=Samba*))` are decoded in place by `tldap_unescape_inplace`, one using LDAPv3 hex escapes and one using LDAPv2 backslash-literal escaping.

Control flow: each test initializes a mutable `char dn[]`, sets `dnlen = sizeof(dn)`, calls the unescape function, asserts success, and compares the resulting string with the expected unescaped value. `main` registers both tests, selects subunit output, and runs without setup/teardown.

State and persistence: no durable state. The mutation is in-place on stack arrays. Dependencies are cmocka and direct inclusion of `source3/lib/tldap.c`.

Risks: direct implementation inclusion can duplicate compile context and miss integration-link issues. The tests cover successful decode paths only; malformed hex, truncated backslash escapes, embedded NUL, and length-shrinking behavior would be useful additions. These tests are still important signals for LDAP escaping compatibility across LDAPv2 and LDAPv3 forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/test_tldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tevent_barrier.c -->
## sources/user-network-fs/samba/source3/lib/tevent_barrier.c

Purpose: asynchronous barrier primitive for tevent. It releases a group of wait requests only after a configured number of waiters have arrived, then optionally invokes a trigger callback.

Important types are private `struct tevent_barrier_waiter`, `struct tevent_barrier`, and `struct tevent_barrier_wait_state`. Public APIs are `tevent_barrier_init`, `tevent_barrier_wait_send`, and `tevent_barrier_wait_recv`.

Control flow: initialization allocates a barrier with a fixed waiter array and per-slot immediate events. Each `tevent_barrier_wait_send` creates a request, stores its barrier/index state, records the event context and request in the next waiter slot, and installs a destructor so cancelled requests remove themselves. If the count reaches array length, it schedules an immediate trigger that calls `tevent_barrier_release`. Release schedules completion immediates for all current waiters, clears their destructors and slots, resets count to zero, and calls `trigger_cb`. Destroying the barrier releases any waiters.

State and persistence: state is talloc-owned in the barrier object and wait requests; no persistence. Dependencies are talloc, tevent, and Samba `tevent_unix` simple receive helpers.

Risks: cancellation destructor swaps only the request pointer from the last slot and does not copy the corresponding event context, which could leave a mismatched waiter slot in some cancellation orders. There is no bounds check before indexing `waiters[b->count]`, so callers must not submit more simultaneous waiters than configured. Tests should cover exact-count release, cancellation before release, barrier destruction with waiters, callback invocation count, and reuse after release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tevent_barrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tevent_barrier.h -->
## sources/user-network-fs/samba/source3/lib/tevent_barrier.h

Purpose: public interface for the tevent barrier primitive implemented in `tevent_barrier.c`.

Important APIs: opaque `struct tevent_barrier`, `tevent_barrier_init(TALLOC_CTX *, unsigned count, trigger_cb, private_data)`, `tevent_barrier_wait_send`, and `tevent_barrier_wait_recv`. The send/recv shape follows Samba tevent request conventions.

Control flow contract: callers allocate a barrier with a nonzero waiter count, issue wait requests on event contexts, and complete each request through the normal tevent callback/recv path once the barrier trips. The optional trigger callback runs when the barrier releases a full group or when destruction releases pending waiters.

State and persistence: all state is in the opaque talloc object and request objects. The header depends on `talloc.h` and `tevent.h` only.

Risks and tests: the header does not state whether the barrier is reusable, but the implementation resets count after release, so users may rely on that behavior. It also does not document cancellation limits or max simultaneous waiters. API tests should verify send/recv error semantics, zero-count initialization returning NULL, and lifetime interactions between barrier and wait requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tevent_barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/time.c -->
## sources/user-network-fs/samba/source3/lib/time.c

Purpose: Samba source3 time conversion and formatting utilities. It bridges Unix `time_t`/`timespec`, DOS date formats, NT time values, server timezone offset, and process uptime/start time.

Important APIs include `convert_time_t_to_uint32_t`, `convert_uint32_t_to_time_t`, `nt_time_is_zero`, `generalized_to_unix_time`, `get_server_zone_offset`, `set_server_zone_offset`, `srv_put_dos_date`, `srv_put_dos_date2_ts`, `srv_put_dos_date3`, `round_timespec`, `put_long_date_timespec`, `put_long_date_full_timespec`, `pull_long_date_full_timespec`, `put_long_date`, `dos_filetime_timespec`, `make_unix_date*`, `srv_make_unix_date*`, `interpret_long_date`, `TimeInit`, `get_process_uptime`, `get_startup_time`, `nt_time_to_unix_abs`, `unix_to_nt_time_abs`, `time_to_asc`, `display_time`, and `nt_time_is_set`.

Control flow: server date helpers use a process-global `server_zone_offset` initialized by `TimeInit` or `set_server_zone_offset`. Long-date writers round according to requested timestamp resolution before converting to NT time. DOS-date readers delegate to pull helpers with explicit or server zone offset. Absolute NT conversions handle zero, -1, infinity, and 64-bit time bounds specially. Uptime subtracts a saved `start_time_hires` from current time.

State and persistence: static `server_zone_offset` and `start_time_hires` are process-global memory state. No durable state. Dependencies are Samba byte-order macros, DOS/NT time conversion helpers, timeval/timespec utilities, and debug logging.

Risks: `generalized_to_unix_time` ignores timezone suffixes despite parsing generalized time, which can surprise LDAP/ASN.1 consumers. `display_time` uses float arithmetic for 64-bit NT durations and allocates on `talloc_tos`. `TimeInit` only captures startup time once, before daemon fork by design. Tests should cover special time sentinels, 32/64-bit `time_t`, timezone offset initialization, rounding modes, DOS date variants, and generalized-time timezone cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/time.c -->
