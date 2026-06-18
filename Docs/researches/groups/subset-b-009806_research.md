# Research Group: subset-b-009806

This grouped report covers the requested Samba source files under `sources/user-network-fs/samba/source3`. Each source file has its own marker-delimited section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb.h -->
# sources/user-network-fs/samba/source3/include/smb.h

## Purpose
`smb.h` is a central Samba source3 include that gathers SMB/CIFS protocol constants, packet offsets, open/share-mode encodings, oplock definitions, core server data structures, and server-wide feature identifiers. It also includes the ACL, quota, readdir-attribute, VFS, SMB macro, and name-service headers that many source3 server paths expect through the broad `includes.h`/`smb.h` dependency chain.

## Important APIs, Types, and Constants
- Network constants: `NMB_PORT`, `DGRAM_PORT`, `NBT_SMB_PORT`, `TCP_SMB_PORT`, and `SMB_PORTS` define NetBIOS and direct TCP SMB listener ports.
- Protocol/open constants: deny modes (`DENY_*`), DOS open modes (`DOS_OPEN_*`), `OPENX_*` disposition flags, `NTCREATEX_*` masks/private flags, pipe flags, IOCTL constants, and usershare error codes.
- Packet layout macros: `smb_com`, `smb_tid`, `smb_uid`, `smb_vwv*`, transaction/NT transaction field offsets, and `smb_base()` encode byte offsets into SMB1 packets after the NBT header. These are used by low-level request decoders and reply builders.
- Oplock definitions: protocol request macros (`CORE_OPLOCK_REQUEST`, `EXTENDED_OPLOCK_REQUEST`), local aliases (`NO_OPLOCK`, `EXCLUSIVE_OPLOCK`, `BATCH_OPLOCK`, `LEVEL_II_OPLOCK`, `LEASE_OPLOCK`), return wire values, and `struct kernel_oplocks_ops`.
- Shared types: `struct notify_change`, `struct sys_notify_context`, `struct current_user`, `userdom_struct`, `struct interface`, EA structures, `enum remote_arch_types`, `enum usershare_err`, `enum file_close_type`, and `struct smb_extended_info`.

## Control Flow and State
This header does not implement executable control flow, but it controls parsing and dispatch by defining field offsets and bit extractions that request handlers use directly. Its oplock macros normalize CORE and extended oplock request bits into the common internal flag set, while the kernel-oplock operations table defines the callback shape used by platform-specific oplock backends.

State exposed here is mostly embedded in other server objects. `struct current_user` binds a connection, SMB2-compatible VUID, Unix token, and NT security token. `struct sys_notify_context` stores a tevent context and backend-private change-notify data. `struct interface` models discovered network interfaces with address, netmask, broadcast, speed, and capability metadata.

## Persistence Behavior
No direct persistence is implemented. The header defines persistent or wire-compatible data shapes indirectly: SMB packet offsets, SID sizing, EA names stored as xattrs (`user.DOSATTRIB`, `user.DosStream.`, `user.SmbReparse`, etc.), usershare status codes, and the 48-byte `smb_extended_info` structure used in object-id information replies.

## Dependencies and Integration Points
`smb.h` depends on generated NDR security/server-id headers, `libcli/smb/smb_common.h`, role constants, quota and VFS headers, SMB ACLs, name service declarations, and macro helpers. Because it pulls in `vfs.h` and `smb_macros.h`, edits can affect most source3 server modules, especially SMB1 transaction handling, file open paths, ACL/quota code, browser announcements, and xattr stream handling.

## Risks
- Packet offset macros are ABI-sensitive; an incorrect offset silently corrupts SMB1 parsing or response generation.
- The open/disposition and oplock bit masks are protocol boundary constants. Changes can break Windows client compatibility or server-side share-mode/oplock semantics.
- The broad include role can amplify compile breakage or dependency cycles.
- Samba-private xattr names must stay synchronized with code that reads or writes those EAs, as noted for POSIX inheritance.

## Test Signals
Relevant signals include SMB1 open/create/trans/NT-trans torture tests, oplock/lease torture coverage, EA/xattr stream tests, usershare parsing tests, and compile coverage for source3 modules that include `smb.h`. Packet-level tests should catch regressions in `smb_vwv*` and transaction offset macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_acls.h -->
# sources/user-network-fs/samba/source3/include/smb_acls.h

## Purpose
`smb_acls.h` defines Samba's portable POSIX ACL abstraction for source3. It maps Samba ACL handles, entries, permission sets, and tags onto generated NDR ACL types and declares the `sys_acl_*` helper API implemented by `lib/sysacls.c`.

## Important APIs, Types, and Functions
- Type aliases: `SMB_ACL_TYPE_T`, `SMB_ACL_PERMSET_T`, `SMB_ACL_PERM_T`, `SMB_ACL_TAG_T`, `SMB_ACL_T`, and `SMB_ACL_ENTRY_T`.
- ACL traversal/query: `sys_acl_get_entry`, `sys_acl_get_tag_type`, `sys_acl_get_permset`, `sys_acl_get_qualifier`, `sys_acl_get_perm`, and `sys_acl_to_text`.
- ACL construction/mutation: `sys_acl_init`, `sys_acl_create_entry`, `sys_acl_set_tag_type`, `sys_acl_set_qualifier`, `sys_acl_set_permset`, `sys_acl_clear_perms`, and `sys_acl_add_perm`.
- File-handle operations: `sys_acl_get_fd`, `sys_acl_set_fd`, and `sys_acl_delete_def_fd`.
- Error classification: `no_acl_syscall_error`.

## Control Flow and State
The header is an interface only. Runtime control flow is the standard Samba ACL path: VFS ACL calls dispatch to system ACL helpers, which create/read/modify `SMB_ACL_T` structures and convert them to or from SMB security descriptors. ACL state lives in the allocated ACL object and on the backing filesystem ACLs associated with `files_struct` handles.

## Persistence Behavior
Persistence is through the host filesystem's ACL mechanism via file-descriptor operations. The header itself does not write, but `sys_acl_set_fd` and `sys_acl_delete_def_fd` are persistence boundary declarations.

## Dependencies and Integration Points
It includes `librpc/gen_ndr/smb_acl.h` and forward-declares VFS and file structures. It is included by `smb.h` and used by VFS operations in `vfs.h`, ACL mapping code, NT security descriptor conversion, and POSIX ACL modules.

## Risks
- The comment about `mode_t` versus PIDL-generated `uint32_t` means type widths must remain compatible with generated IDL.
- Callers must honor talloc ownership of returned ACL/text objects.
- Filesystems without ACL support must be correctly detected through `no_acl_syscall_error` to avoid treating unsupported ACLs as hard failures.

## Test Signals
Useful tests include POSIX ACL get/set/delete coverage, NT ACL round trips through VFS, behavior on filesystems lacking ACL support, and compile checks for generated ACL type compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_acls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_krb5.h -->
# sources/user-network-fs/samba/source3/include/smb_krb5.h

## Purpose
`smb_krb5.h` is a very small aggregator header for Samba's Kerberos and GSSAPI wrapper interfaces in source3.

## Important APIs, Types, and Functions
The header directly includes:
- `lib/krb5_wrap/krb5_samba.h`
- `lib/krb5_wrap/gss_samba.h`

It declares no local functions, types, constants, or include guard of its own.

## Control Flow and State
There is no local control flow or state. Including this file makes the Kerberos/GSS wrapper APIs visible to code that historically expected `smb_krb5.h`.

## Persistence Behavior
No persistence is performed here. Kerberos credential caches, keytabs, and GSS state are managed by the included wrapper APIs and their implementations.

## Dependencies and Integration Points
This is a compatibility/convenience integration point for authentication and session setup code needing Samba's Kerberos and GSS wrappers. It relies entirely on the wrapped library headers for platform abstraction.

## Risks
- Because it lacks a local guard, repeated inclusion safety depends on the included wrapper headers.
- Any change to this file can have broad build impact in authentication-related source3 code that includes it transitively.

## Test Signals
Compile coverage for Kerberos-enabled and Kerberos-disabled builds is the main signal. Authentication tests using SPNEGO/GSS/Kerberos validate the real downstream behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_ldap.h -->
# sources/user-network-fs/samba/source3/include/smb_ldap.h

## Purpose
`smb_ldap.h` normalizes LDAP and LBER client-library headers and constants across platforms. It provides Samba-local defaults and compatibility aliases for systems with partial or differently named LDAP APIs, and it supplies stub types when LDAP support is not compiled in.

## Important APIs, Types, and Constants
- Conditional platform includes: `lber.h`, `ldap.h`, and optionally `ldap_pvt.h`.
- Compatibility definitions: `LDAP_CONST`, `LDAP_SASL_BIND_IN_PROGRESS`, `LDAPS_PORT`, `LDAP_OPT_SUCCESS`.
- No-LDAP build stubs: `LDAP`, `LDAPMessage`, `LDAPMod`, and `LDAPControl` become `void` aliases; `struct berval` and `struct ldapsam_privates` are forward-declared.
- Timeout and paging constants: `LDAP_DEFAULT_TIMEOUT`, `LDAP_CONNECTION_DEFAULT_TIMEOUT`, `LDAP_PAGE_SIZE`, and `ADS_PAGE_CTL_OID`.
- Password modify extended operation OIDs/tags: `LDAP_EXOP_MODIFY_PASSWD`, `LDAP_TAG_EXOP_MODIFY_PASSWD_ID`, and `LDAP_TAG_EXOP_MODIFY_PASSWD_NEW`.

## Control Flow and State
The file is entirely preprocessor-driven. Control flow is compile-time feature selection based on `HAVE_LBER_H`, `HAVE_LDAP_H`, `HAVE_LDAP`, platform macros, and library-provided OID names. Runtime LDAP connection state is not defined here.

## Persistence Behavior
No persistence is implemented. The constants declared here influence LDAP operations that may modify directory state in other modules.

## Dependencies and Integration Points
It is included by `smbldap.h` and code that talks to OpenLDAP or platform LDAP libraries. It bridges Samba's LDAP abstraction with ADS, ldapsam, passdb, and password-change paths.

## Risks
- Incorrect compatibility aliases can break builds on Solaris, HP-UX, or non-OpenLDAP implementations.
- Stub `void` LDAP types allow non-LDAP builds to parse declarations, but accidental dereference or use outside `#ifdef HAVE_LDAP` would be a compile or runtime design error.
- Timeout/page-size constants affect query responsiveness and memory load when used by LDAP callers.

## Test Signals
LDAP-enabled and LDAP-disabled build matrix coverage is critical. Runtime signals include paged LDAP searches, SASL bind progress handling, LDAPS/TLS startup, and password modify extended operation tests against different LDAP servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_ldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_macros.h -->
# sources/user-network-fs/samba/source3/include/smb_macros.h

## Purpose
`smb_macros.h` collects source3 convenience macros for SMB server checks, packet buffer access, share configuration checks, allocation wrappers, stat validity, domain-controller role checks, Kerberos method checks, and array growth helpers.

## Important APIs, Types, and Macros
- Access checks: `CHECK_READ`, `CHECK_READ_SMB2`, and `CHECK_READ_IOCTL` distinguish path references, real I/O fds, read permission, and SMB2 execute-implies-read semantics.
- Connection/share helpers: `IS_IPC`, `IS_PRINT`, `SNUM`, `CAN_WRITE`, `GUEST_OK`, `MAP_HIDDEN`, `IS_VETO_PATH`, and related macros.
- Stat helpers: `VALID_STAT`, `VALID_STAT_OF_DIR`, and `SET_STAT_INVALID`.
- Packet helpers: `smb_buf`, `smb_buf_const`, `smb_buflen`, `smbreq_bufrem`, `smb_offset`, `smb_len`, `smb_setlen`, and large TCP length aliases.
- Error helpers: `ERROR_NT`, `ERROR_BOTH`, `reply_nterror`, `reply_force_doserror`, and `reply_botherror` preserve call-site file and line.
- Allocation helpers: `SMB_MALLOC*`, `SMB_REALLOC*`, `SMB_CALLOC_ARRAY`, `SMB_XMALLOC*`, `SMB_STRDUP`, and `SMB_STRNDUP`; developer builds can poison direct malloc/realloc/calloc/strdup use.
- Dynamic array helpers: `ADD_TO_ARRAY`, `ADD_TO_MALLOC_ARRAY`, and `ADD_TO_LARGE_ARRAY`.

## Control Flow and State
These macros inline policy checks into SMB request paths. Access macros route behavior based on `files_struct` flags, fd availability, access masks, and SMB request flags. Allocation macros change behavior at compile time when `DEVELOPER`/`PARANOID_MALLOC_CHECKER` is enabled, turning direct allocator use into compile-time errors.

## Persistence Behavior
No persistence is implemented. The macros influence operations that read/write files, allocate state, and generate protocol errors.

## Dependencies and Integration Points
This header assumes many Samba-wide symbols are available: `files_struct`, `connection_struct`, `lp_*` configuration accessors, SMB byte accessors (`CVAL`, `SVAL`, `IVAL`), `fsp_get_io_fd`, `error_packet`, `reply_*`, allocator helpers, role constants, and Kerberos method constants. It is included from `smb.h`, making it widely visible.

## Risks
- Macros evaluate arguments in C preprocessor context; callers must avoid side effects where not safe.
- Access-check macros must stay aligned with Windows SMB2 semantics and low-level VFS pathref restrictions.
- The `SMB_VFS_NEXT_FSTATAT`-style typo risk seen in macro-heavy code applies generally here: incorrect identifiers can compile only in some contexts.
- Allocation wrappers assert on growth failures in `ADD_TO_ARRAY`, which is appropriate for internal invariants but not for recoverable external input paths.

## Test Signals
Signals include developer builds with allocator poisoning, SMB2 read/ioctl access torture tests, stat-cache tests, guest/share configuration tests, and packet encoding/decoding coverage for SMB1 paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smb_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smbldap.h -->
# sources/user-network-fs/samba/source3/include/smbldap.h

## Purpose
`smbldap.h` declares Samba's traditional LDAP helper API, guarded by `HAVE_LDAP`. It wraps LDAP connection setup, bind callbacks, modification-list construction, attribute extraction, searches, TLS startup, and talloc-based cleanup helpers around the platform LDAP library.

## Important APIs, Types, and Functions
- State and callback: opaque `struct smbldap_state` and `smbldap_bind_callback_fn`.
- Connection lifecycle: `smbldap_init`, `smbldap_get_ldap`, `smbldap_setup_full_conn`, `smbldap_start_tls`, and `smbldap_start_tls_start`.
- Paging and binding: `smbldap_get_paged_results`, `smbldap_set_paged_results`, and `smbldap_set_bind_callback`.
- Modification helpers: `smbldap_set_mod`, `smbldap_set_mod_blob`, `smbldap_make_mod`, and `smbldap_make_mod_blob`.
- LDAP operations: `smbldap_search` and `smbldap_modify`.
- Attribute extraction: `smbldap_get_single_attribute`, `smbldap_talloc_single_attribute`, `smbldap_talloc_first_attribute`, `smbldap_talloc_smallest_attribute`, `smbldap_talloc_single_blob`, `smbldap_pull_sid`, and `smbldap_talloc_dn`.
- Cleanup helpers: `smbldap_talloc_autofree_ldapmsg` and `smbldap_talloc_autofree_ldapmod`.

## Control Flow and State
The main state object owns an LDAP connection plus Samba-specific settings such as paged-result preference and optional bind callback. Callers initialize the state, optionally configure callbacks/paging, perform searches/modifies, and rely on talloc cleanup helpers to release LDAP result and mod arrays.

## Persistence Behavior
Search helpers are read-only against directory state, while `smbldap_modify` and password/TLS-related downstream operations can mutate LDAP directory entries. This header itself only declares the persistence boundary.

## Dependencies and Integration Points
It includes `include/smb_ldap.h`, `talloc.h`, and `tevent.h` when LDAP is enabled. It integrates with passdb/ldapsam, account management, SID/GUID conversion, and any source3 code that still uses the synchronous LDAP API rather than `tldap`.

## Risks
- Every declaration is hidden when `HAVE_LDAP` is false; callers must guard use correctly.
- LDAPMod array ownership is subtle and depends on the talloc autofree wrappers.
- Attribute extraction APIs need clear handling of missing, multi-valued, binary, or oversized attributes.
- TLS startup split between `_start` and synchronous variants can be misused if the connection state is assumed secure too early.

## Test Signals
LDAP-enabled build coverage, ldapsam account tests, TLS bind tests, paged-result searches, binary SID/blob extraction tests, and leak checks around LDAPMessage/LDAPMod cleanup provide useful signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smbldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smbprofile.h -->
# sources/user-network-fs/samba/source3/include/smbprofile.h

## Purpose
`smbprofile.h` defines the source3 smbd profiling data model and macros. When `WITH_PROFILE` is enabled, it records counts, timings, byte totals, latency buckets, and per-service statistics into shared/TDB-backed profiling state; when disabled, the public macros collapse to no-ops.

## Important APIs, Types, and Macros
- Statistic catalog: `SMBPROFILE_STATS_ALL_SECTIONS` enumerates global loop, authentication, syscall, ACL, stat-cache, SMB1, Trans2, NT transact, and SMB2 operations.
- Data types: `smbprofile_stats_count`, `smbprofile_stats_time`, `smbprofile_stats_basic`, `smbprofile_stats_bytes`, `smbprofile_stats_iobytes`, their async state types, `profile_stats`, `profile_stats_persvc`, and `smbprofile_global_state`.
- Global state: `profile_p` and `smbprofile_state`.
- Instrumentation macros: `DO_PROFILE_INC`, `START_PROFILE`, `START_PROFILE_BYTES`, `END_PROFILE`, `END_PROFILE_BYTES`, `SMBPROFILE_*_ASYNC_*`, and per-share `_X` variants.
- Runtime functions: `smbprofile_dump_setup`, `smbprofile_dump_schedule_timer`, `smbprofile_dump`, `smbprofile_cleanup`, `smbprofile_stats_accumulate`, `smbprofile_collect_tdb`, `smbprofile_collect`, `set_profile_level`, and `profile_setup`.
- Per-service functions under `WITH_PROFILE`: `smbprofile_persvc_mkref`, `smbprofile_persvc_unref`, `smbprofile_persvc_get`, `smbprofile_persvc_reset`, and collection helpers.

## Control Flow and State
Instrumentation starts by allocating an async state on the stack and recording a monotonic microsecond timestamp when counting/timing is enabled. End macros add elapsed time, idle time, byte totals, failed counts, and latency buckets, then call `smbprofile_dump_schedule`. Dump scheduling avoids repeated timer setup by checking `smbprofile_state.internal.te`. `smbprofile_update_failed_count` treats several protocol statuses as successful for specific SMB2 opcodes, and `smbprofile_update_hist` increments cumulative latency buckets.

## Persistence Behavior
Profiling data is kept in process/global structures and integrated with a TDB-backed dump/collection path via `tdb_wrap`. Per-service records include service number, reference count, active flag, and flexible `dbkey[]`. The header declares cleanup and collection but leaves actual TDB persistence to profile implementation files.

## Dependencies and Integration Points
The file depends on `replace.h`, `tdb.h`, time utilities, SMB2 opcode constants, and NTSTATUS utilities. It is included by `vfs.h`, and its macros are used across smbd syscall wrappers, SMB request handlers, authentication, VFS operations, and profile-control messaging.

## Risks
- Macro instrumentation must pair start/end variables exactly; mismatched names or early returns can lose timings.
- Shared/global counters are performance-sensitive and may be touched in hot paths.
- Disabled-profile no-op macros must preserve compile compatibility and avoid evaluating expensive arguments unexpectedly.
- Latency bucket logic is cumulative; consumers must interpret bucket counts correctly.

## Test Signals
Builds with and without `WITH_PROFILE`, smbd profile level changes, `smbstatus`/profile collection behavior, SMB2 failed-count exceptions, per-share profile reference/unref tests, and leak/race checks around scheduled dumps are strong signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/smbprofile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/srvstr.h -->
# sources/user-network-fs/samba/source3/include/srvstr.h

## Purpose
`srvstr.h` is a tiny server string helper compatibility header. It maps `srvstr_pull_talloc` to the generic `pull_string_talloc` implementation.

## Important APIs, Types, and Macros
- `srvstr_pull_talloc(ctx, base_ptr, smb_flags2, dest, src, src_len, flags)` expands directly to `pull_string_talloc` with the same arguments.

## Control Flow and State
There is no local control flow or state. The macro preserves a historical server-specific name while deferring all behavior to the generic string conversion routine.

## Persistence Behavior
No persistence is involved.

## Dependencies and Integration Points
Callers must already have `pull_string_talloc` declared and must provide SMB flags and base pointer context appropriate for string decoding. It integrates with SMB request parsing where wire strings are converted into talloc-owned C strings.

## Risks
- As a macro alias, argument side effects are passed through to `pull_string_talloc`.
- Behavior depends entirely on the generic string routine and its interpretation of SMB flags, Unicode state, and buffer bounds.

## Test Signals
SMB1 path/name parsing tests, Unicode/OEM conversion tests, malformed string buffer tests, and compile coverage of legacy callers using `srvstr_pull_talloc`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/srvstr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/stamp-h.in -->
# sources/user-network-fs/samba/source3/include/stamp-h.in

## Purpose
`stamp-h.in` is an Autoconf-era stamp file containing a single timestamp line: `Sun Jul 18 20:32:29 UTC 1999`. Such files are normally used by configure/build systems to track generated header freshness.

## Important APIs, Types, and Functions
There are no C APIs, types, or functions. The only content is the timestamp.

## Control Flow and State
No executable control flow exists. Build tooling may treat the file timestamp/content as part of dependency tracking.

## Persistence Behavior
The file itself is persisted build metadata in the source tree. It does not persist runtime state.

## Dependencies and Integration Points
Integration is with configure/make dependency logic around generated configuration headers. It is not included by C code.

## Risks
- Editing or regenerating this file can create noisy build-system diffs.
- Removing it may break legacy make rules that expect a stamp input.

## Test Signals
Build-system tests or a clean configure/build are the relevant validation. Runtime Samba tests do not exercise this file directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/stamp-h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/sysquotas.h -->
# sources/user-network-fs/samba/source3/include/sysquotas.h

## Purpose
`sysquotas.h` defines source3 disk-quota constants, platform quota block-size selection, and the `SMB_DISK_QUOTA` structure used by VFS quota operations.

## Important APIs, Types, and Macros
- Platform includes under `HAVE_SYS_QUOTAS`: `mntent.h` when mount-entry helpers are available, or `devnm.h` on systems with `devnm`.
- Limit markers: `SMB_QUOTAS_NO_LIMIT` and `SMB_QUOTAS_NO_SPACE`.
- Initializer macros: `SMB_QUOTAS_SET_NO_LIMIT(dp)` and `SMB_QUOTAS_SET_NO_SPACE(dp)`.
- Main type: `SMB_DISK_QUOTA` holds quota type, block size, hard/soft block limits, current blocks, inode limits/current inodes, and flags.
- `QUOTABLOCK_SIZE` selection handles AIX, Linux, Darwin, BSD, and a fallback.

## Control Flow and State
The header's logic is compile-time platform selection. Runtime quota state is represented in `SMB_DISK_QUOTA` and filled by system/VFS quota functions.

## Persistence Behavior
No direct persistence. The VFS/system quota implementations that use `SMB_DISK_QUOTA` read or modify filesystem quota state.

## Dependencies and Integration Points
It depends on `enum SMB_QUOTA_TYPE` from surrounding includes and is included by `smb.h` and `vfs.h`. `SMB_DISK_QUOTA` is the argument type for `get_quota`/`set_quota` VFS function pointers and call wrappers.

## Risks
- Block-size mismatches can misreport or incorrectly set quota limits.
- The no-limit/no-space sentinel values are small integers in `uint64_t`; callers must not confuse them with real limits without context.
- Platform guards must match configure feature detection.

## Test Signals
Quota get/set tests on supported filesystems, build coverage on quota-enabled and quota-disabled platforms, unit checks for block-size conversion, and VFS quota module tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/sysquotas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/tldap.h -->
# sources/user-network-fs/samba/source3/include/tldap.h

## Purpose
`tldap.h` declares Samba's tevent/talloc-based asynchronous LDAP client interface. It provides typed LDAP result codes, request/response functions for LDAP protocol operations, message inspection helpers, controls, modifications, debug logging, and constants for LDAP application tags, modification operations, scopes, and paged-results control.

## Important APIs, Types, and Functions
- Opaque state: `struct tldap_context` and `struct tldap_message`.
- Data shapes: `tldap_control`, `tldap_attribute`, and `tldap_mod`.
- Result code abstraction: `TLDAPRC`, `TLDAP_RC`, `TLDAP_RC_V`, `TLDAP_RC_EQUAL`, `TLDAP_RC_IS_SUCCESS`, and many `TLDAP_*` code constants.
- Context/transport: `tldap_context_create_from_plain_stream`, `tldap_context_create`, `tldap_get_plain_tstream`, TLS/gensec stream setters/getters, channel bindings, connection status, and attribute get/set.
- LDAP operations: async send/recv and sync wrappers for SASL bind, simple bind, search, search-all, add, modify, delete, and extended operations.
- Message inspection: `tldap_msg_id`, `tldap_msg_type`, `tldap_msg_rc`, matched DN, diagnostic message, referral, server controls, last message, and `tldap_rc2string`.
- Debug integration: `tldap_set_debug`.

## Control Flow and State
The API follows the Samba async pattern: callers create a `tevent_req` with `*_send`, run it on a `tevent_context`, and complete it with the paired `*_recv`, or call synchronous wrappers that perform the same operation internally. `tevent_req_ldap_error` and `tevent_req_is_ldap_error` encode LDAP result codes into tevent request failure state. The context can wrap a raw fd or tstream and can be upgraded with TLS or GENSEC streams.

## Persistence Behavior
The header itself does not persist data. LDAP add/modify/delete/extended operations can change directory state through their implementations. Context attributes can hold process-local metadata but are not persisted.

## Dependencies and Integration Points
It includes `replace.h`, `talloc.h`, `tevent.h`, and `DATA_BLOB`. It integrates with async Samba authentication/directory code, tstream TLS/GENSEC layers, and higher-level helpers in `tldap_util.h`.

## Risks
- `TLDAPRC` may be an immediate structure on some compilers; callers must use comparison/access macros rather than assuming it is a raw integer.
- Async send/recv pairs require correct talloc ownership and request lifecycle handling.
- TLS/GENSEC stream replacement affects channel bindings and connection security; callers must not use stale plain streams after upgrade.
- Search APIs have size/time/deref controls that can affect directory load and memory usage.

## Test Signals
Async LDAP operation tests, sync wrapper tests, SASL bind continuation handling, TLS/GENSEC upgrade tests, paged search coverage through utilities, and error propagation checks through `tevent_req_is_ldap_error`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/tldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/tldap_util.h -->
# sources/user-network-fs/samba/source3/include/tldap_util.h

## Purpose
`tldap_util.h` declares convenience helpers layered on top of `tldap.h` for attribute extraction, typed conversion, modification-list construction, formatted searches, RootDSE fetching, control handling, and paged searches.

## Important APIs, Types, and Functions
- Attribute/value extraction: `tldap_entry_values`, `tldap_get_single_valueblob`, `tldap_talloc_single_attribute`, `tldap_pull_binsid`, `tldap_pull_guid`, `tldap_pull_uint64`, and `tldap_pull_uint32`.
- Modification builders: `tldap_add_mod_blobs`, `tldap_add_mod_str`, `tldap_make_mod_blob`, and `tldap_make_mod_fmt`.
- Error/search helpers: `tldap_errstr`, `tldap_search_va`, and `tldap_search_fmt`.
- RootDSE: `tldap_fetch_rootdse_send`, `tldap_fetch_rootdse_recv`, `tldap_fetch_rootdse`, and `tldap_rootdse`.
- Controls: `tldap_entry_has_attrvalue`, `tldap_supports_control`, `tldap_add_control`, and `tldap_msg_findcontrol`.
- Paged search: `tldap_search_paged_send` and `tldap_search_paged_recv`.

## Control Flow and State
The helpers either synchronously inspect a `tldap_message`, append to talloc-owned arrays, or wrap async LDAP operations. Paged searches build on repeated search requests and controls, returning messages through the request/recv pattern. RootDSE fetch caches or exposes RootDSE information through the LDAP context.

## Persistence Behavior
Read helpers do not persist state. Modification builders produce request data consumed by LDAP modify/add calls, which may persist directory changes. RootDSE state may be cached in the `tldap_context` implementation.

## Dependencies and Integration Points
It includes `includes.h`, so it expects the broader Samba source3 context. It integrates with `tldap.h`, SID/GUID parsing, directory capability discovery, and code that needs formatted filters or paged results.

## Risks
- Formatted search helpers must escape LDAP filter input correctly in their implementations; the declaration marks printf attributes for compiler checking.
- Attribute conversion helpers need robust handling of missing, duplicated, malformed, and endian-sensitive values.
- Paged-search control handling must avoid infinite loops and must handle servers that omit or reject the control.

## Test Signals
Tests should cover attribute extraction edge cases, SID/GUID/integer parsing, formatted filter generation, RootDSE control discovery, paged search continuation/end behavior, and memory ownership of generated mod arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/tldap_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/trans2.h -->
# sources/user-network-fs/samba/source3/include/trans2.h

## Purpose
`trans2.h` defines SMB1 Transaction2, NT passthrough, FSCC file-information, filesystem-information, directory-search, and related info-level constants and legacy structure offsets. It is a protocol layout header for SMB1 query/set path/file/fs info and findfirst/findnext handlers.

## Important APIs, Types, and Constants
- Legacy DOS find/status offsets: `l1_*`, `l2_*`, `l260_achName`, FS allocation/volume offsets, and `DIRLEN_GUESS`.
- SMB info levels: `SMB_INFO_STANDARD`, `SMB_INFO_QUERY_EA_SIZE`, `SMB_QUERY_FS_*`, `SMB_QUERY_FILE_*`, `SMB_FIND_*`, and `SMB_SET_FILE_*`.
- Device and characteristic constants: `DEVICETYPE_*`, `TYPE_*`, `FILE_DEVICE_*`, and `FILE_*` characteristics.
- Sector-size info constants: `SSINFO_FLAGS_*` and `SSINFO_OFFSET_UNKNOWN`.
- FSCC classes: `FSCC_FILE_*` and `FSCC_FS_*`, including Samba's POSIX info placeholder class `100`.
- NT passthrough mapping: `NT_PASSTHROUGH_OFFSET`, `SMB_FILE_*`, `SMB_FS_*`, and internal SMB2 special levels.
- Find flags: `FLAG_TRANS2_FIND_CLOSE`, `FLAG_TRANS2_FIND_CLOSE_IF_END`, `FLAG_TRANS2_FIND_REQUIRE_RESUME`, `FLAG_TRANS2_FIND_CONTINUE`, and `FLAG_TRANS2_FIND_BACKUP_INTENT`.

## Control Flow and State
This header has no functions, but it drives transaction dispatch and marshalling. Request handlers compare incoming info levels against these constants, choose parser/encoder paths, and write legacy response buffers using the offset macros.

## Persistence Behavior
No direct persistence. Some info levels declared here trigger file metadata mutation in setfile/setpathinfo handlers, including allocation size, EOF, disposition/delete-on-close, basic timestamps, and filesystem metadata where supported.

## Dependencies and Integration Points
It integrates with SMB1 `TRANS2_*` handlers, SMB2 getinfo/setinfo compatibility mapping, FSCC marshalling, directory enumeration, stream info, quota/object-id handling, and Mac CIFS extension handling.

## Risks
- Constants are wire protocol values; changing them breaks client compatibility.
- Legacy offset macros must match packed wire structures, independent of compiler struct packing.
- NT passthrough offset mapping must stay aligned with FSCC class values and Samba internal special levels.
- Unsupported or undefined info levels must be rejected predictably to avoid malformed response buffers.

## Test Signals
SMB1 trans2 torture tests, query/set path/file/fs info tests, directory enumeration info-level coverage, Mac extension tests if enabled, SMB2 getinfo/setinfo mapping tests, and fuzzing malformed trans2 buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/trans2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/transfer_file.h -->
# sources/user-network-fs/samba/source3/include/transfer_file.h

## Purpose
`transfer_file.h` declares utility functions for copying bytes from one file-like object to another, either through caller-provided pread/pwrite callbacks or plain file descriptors.

## Important APIs, Types, and Functions
- `transfer_file_internal(void *in_file, void *out_file, size_t n, ssize_t (*pread_fn)(...), ssize_t (*pwrite_fn)(...))`: generic transfer loop over abstract file handles.
- `transfer_file(int infd, int outfd, off_t n)`: descriptor-based wrapper that transfers up to `n` bytes.

## Control Flow and State
The implementation is expected to repeatedly read from the input and write to the output until the requested byte count, EOF, or error. The internal function's callbacks allow VFS-like or test-specific file abstractions.

## Persistence Behavior
The output file descriptor/object is modified with copied bytes. No long-term state is kept by the helper itself.

## Dependencies and Integration Points
It integrates with source3 file-copy paths, potential VFS copy fallbacks, and tests that need to inject read/write functions. It uses POSIX-like `ssize_t` and `off_t` semantics.

## Risks
- Partial reads/writes, short writes, EINTR/EAGAIN, and large `off_t` values must be handled in the implementation.
- The generic callback interface cannot enforce whether input/output offsets are advanced by callback behavior or by the helper.
- Descriptor wrapper must not assume sparse/offloaded copy semantics.

## Test Signals
Tests should cover zero-length transfer, EOF before requested count, partial read/write callbacks, write errors, large transfers, and descriptor-to-descriptor copies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/transfer_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_event.h -->
# sources/user-network-fs/samba/source3/include/util_event.h

## Purpose
`util_event.h` declares a source3 tevent helper for recurring idle callbacks.

## Important APIs, Types, and Functions
- Opaque `struct idle_event`.
- `event_add_idle(struct tevent_context *event_ctx, TALLOC_CTX *mem_ctx, struct timeval interval, const char *name, bool (*handler)(const struct timeval *now, void *private_data), void *private_data)`.

## Control Flow and State
The helper registers an idle event in a tevent loop. The handler receives the current time and private data and returns a boolean that likely controls whether the idle event remains scheduled. Event state is owned by the returned `idle_event` and its talloc context.

## Persistence Behavior
No persistent storage. The helper maintains in-memory event-loop state until freed or cancelled.

## Dependencies and Integration Points
It includes `replace.h` and `tevent.h` and is implemented in `lib/util_event.c`. It integrates with long-running source3 daemons that need periodic idle work without blocking request handling.

## Risks
- Handler runtime must be short; blocking idle handlers can delay the event loop.
- Ownership of `private_data` and the returned event must be clear to avoid use-after-free.
- Time interval handling must be robust against clock changes if wall-clock time is used downstream.

## Test Signals
tevent loop tests for repeated execution, handler false/cleanup behavior, talloc ownership cleanup, and daemon idle-maintenance tests are relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_sd.h -->
# sources/user-network-fs/samba/source3/include/util_sd.h

## Purpose
`util_sd.h` declares command/client-facing helpers for converting, parsing, and printing Windows security descriptor components.

## Important APIs, Types, and Functions
- SID conversion: `SidToString` and `StringToSid`.
- ACE formatting/parsing: `print_ace` and `parse_ace`.
- Security descriptor printing: `sec_desc_print`.

## Control Flow and State
The functions operate on `cli_state`, `dom_sid`, `security_ace`, and `security_descriptor` inputs. Conversion and parsing routines transform between textual forms and binary security structures, while print helpers write to a `FILE *`.

## Persistence Behavior
No direct persistence. Printed descriptors can be consumed by tools or logs; parsed ACEs/descriptors may later be applied to filesystem or registry security state by callers.

## Dependencies and Integration Points
It is used by Samba client/admin utilities and ACL tooling that need human-readable SIDs, ACEs, and descriptors. It depends on security NDR types and client connection state for name resolution when `numeric` is false.

## Risks
- Name lookup through `cli_state` can fail or be ambiguous; numeric mode must remain reliable.
- ACE parser strictness affects CLI interoperability and error reporting.
- Printing/parsing must preserve security-relevant fields such as flags, masks, trustee SID, and ACE type.

## Test Signals
Round-trip tests for ACE and SID strings, numeric versus resolved-name printing, malformed ACE parse failures, and descriptor output comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_sd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_tdb.h -->
# sources/user-network-fs/samba/source3/include/util_tdb.h

## Purpose
`util_tdb.h` declares source3 utility helpers around Samba's TDB database library, including deprecated packing helpers, logging-aware open, error mapping, data comparison/debug formatting, and timeout-based chain locks.

## Important APIs, Types, and Functions
- Deprecated marshalling: `tdb_unpack`, `tdb_pack`.
- Open/error helpers: `tdb_open_log` and `map_nt_error_from_tdb`.
- Data helpers: `tdb_data_cmp`, `tdb_data_string`, and `tdb_data_dbg`.
- Lock helpers: `tdb_chainlock_with_timeout`, `tdb_lock_bystring_with_timeout`, and `tdb_read_lock_bystring_with_timeout`.

## Control Flow and State
Callers open TDBs through `tdb_open_log`, manipulate `TDB_DATA`, and use timeout lock helpers around critical sections. The header explicitly recommends IDL/NDR instead of the legacy format-string pack/unpack helpers for complex data.

## Persistence Behavior
TDB databases persist Samba runtime state such as locks, shares, profiles, and caches depending on the caller. This header declares utility operations over those persistent databases but does not define a schema.

## Dependencies and Integration Points
It includes `tdb.h`, `talloc.h`, NTSTATUS mapping, and the common `lib/util/util_tdb.h`. It is used by source3 code that stores state in TDB and needs source3-specific logging/error behavior.

## Risks
- Deprecated pack/unpack use can create fragile binary schemas.
- Timeout lock helpers must avoid deadlocks and must report lock failure clearly.
- Debug string helpers must avoid logging untrusted binary data unsafely or leaking sensitive content.

## Test Signals
TDB open/error mapping tests, lock timeout behavior, data comparison/formatting checks, and migration tests away from pack/unpack formats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/util_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/vfs.h -->
# sources/user-network-fs/samba/source3/include/vfs.h

## Purpose
`vfs.h` is the central source3 VFS ABI and file-server state header. It defines the VFS interface version, core file/connection/request/path structures, operation function-pointer table, module handle state, VFS extension helpers, public `smb_vfs_call_*` wrappers, registration APIs, and not-implemented fallback declarations.

## Important APIs, Types, and Constants
- ABI constant: `SMB_VFS_INTERFACE_VERSION 53`, with an extensive version history documenting every VFS ABI change.
- Core state: `files_struct`, `connection_struct`, `smb_request`, `smb_filename`, `stream_struct`, `smb_file_time`, `vfs_aio_state`, `vfs_open_how`, `vfs_rename_how`, `fsp_lease`, and `vuid_cache`.
- Function table: `struct vfs_fn_pointers` covers disk, quota, DFS, directory, open/create/close, sync/async read/write/fsync, stat, metadata mutation, locking, share modes, leases, symlink/link/mknod, realpath, file IDs, copy offload, compression, snapshots, streams, case lookup, byte-range locking, name translation, fsctl, DOS attributes, NT ACLs, POSIX ACLs, xattrs, AIO, durable handles, and readdir attributes.
- Module handle: `vfs_handle_struct` links modules in a stack and stores module-private data and cleanup callback.
- Extension/data helpers: `VFS_ADD_FSP_EXTENSION`, `VFS_FETCH_FSP_EXTENSION`, `VFS_MEMCTX_FSP_EXTENSION`, `VFS_REMOVE_FSP_EXTENSION`, and `SMB_VFS_HANDLE_*`.
- Public wrappers: `smb_vfs_call_*` declarations correspond to VFS macro calls and function pointers.
- Registration/assertion: `smb_register_vfs`, `smb_vfs_assert_all_fns`, `smb_vfs_assert_allowed`, and VFS deny push/pop.
- Fallbacks: `vfs_not_implemented_*` declarations for unimplemented module operations.

## Control Flow and State
The VFS call path is stacked. High-level code uses `SMB_VFS_*` macros from `vfs_macros.h`, which call `smb_vfs_call_*` with `conn->vfs_handles` or `handle->next`. The wrappers dispatch through `vfs_fn_pointers`, allowing modules to intercept operations and then delegate to the next module. `files_struct` carries per-open state, including access masks, fd handles, oplocks/leases, delete-on-close, byte-range lock cache, pathref/FSA flags, stream relationships, async requests, and SMB1 lock-blocking state. `connection_struct` carries per-tree/share state, VFS stack, session info, share capabilities, hide/veto lists, encryption state, and current directory handle.

The pathref/FSA commentary is critical: `is_pathref` marks low-level handles that may be O_PATH or root-opened fallback references and are restricted to descriptor/path operations, while `is_fsa` marks handles processed through Samba's NTFS-semantic file system abstraction. Callers must use `fsp_get_pathref_fd` for metadata/path operations and `fsp_get_io_fd` for true I/O.

## Persistence Behavior
The header defines persistence boundaries for filesystem mutation and durable state: create/open, write, rename, unlink, timestamps, allocation, quota, xattrs, DOS attributes, NT/POSIX ACLs, durable handle cookies, snapshots, compression, and DFS paths. It does not implement persistence itself; VFS modules and wrappers do.

## Dependencies and Integration Points
`vfs.h` includes `smbprofile.h` and then `vfs_macros.h`, and depends on many Samba types: security descriptors, SMB leases/create blobs, talloc, tevent, quota types, stat types, DFS referrals, byte-range locks, TDB-backed open state, and readdir attributes. It is used by smbd request handlers, VFS modules, ACL/quota/EA/stream code, durable-handle code, and file-serving subsystems.

## Risks
- This is an ABI header. Adding/removing/reordering `vfs_fn_pointers` requires bumping the interface version and updating audit/full-audit modules and default wrappers.
- Pathref misuse is security-sensitive: calling I/O or mutating operations on root-opened/O_PATH handles can bypass intended permission semantics or fail unpredictably.
- Module stack delegation must use `NEXT` calls correctly to avoid recursion, bypassing lower modules, or skipping default behavior.
- `files_struct` and `connection_struct` fields are central concurrent server state; incorrect lifetime or talloc ownership can create stale handles, bad leases, lock leaks, or delete-on-close bugs.
- Async VFS operations require exact send/recv pairing and correct `vfs_aio_state` propagation.

## Test Signals
VFS module ABI build tests, full-audit operation coverage, SMB create/open/read/write/rename/unlink/lock/oplock/durable-handle torture tests, pathref-specific permission tests, xattr/ACL/quota tests, async I/O tests, snapshot/compression/offload tests, and module-stack delegation tests are all relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/vfs_macros.h -->
# sources/user-network-fs/samba/source3/include/vfs_macros.h

## Purpose
`vfs_macros.h` provides the canonical `SMB_VFS_*` and `SMB_VFS_NEXT_*` invocation macros for source3 VFS operations. It hides direct access to `conn->vfs_handles`, `handle->next`, and `smb_vfs_call_*` wrapper details from callers and VFS modules.

## Important APIs, Types, and Macros
- Disk/quota/DFS: `SMB_VFS_CONNECT`, `DISCONNECT`, `DISK_FREE`, `GET_QUOTA`, `SET_QUOTA`, shadow copy, `FSTATVFS`, capabilities, and DFS referral/path calls.
- Directory: `FDOPENDIR`, `READDIR`, `REWINDDIR`, `MKDIRAT`, and `CLOSEDIR`.
- File operations: `OPENAT`, `CREATE_FILE`, `CLOSE`, sync/async `PREAD`/`PWRITE`, `LSEEK`, `SENDFILE`, `RECVFILE`, `RENAMEAT`, `RENAME_STREAM`, async `FSYNC`, stat variants, allocation, unlink, chmod/chown, timestamps, truncate/fallocate, locks, fcntl, leases, symlink/readlink/link/mknod, realpath, chflags, file IDs, streams, case lookup, byte-range locking, name translation, parent path, fsctl, DOS attributes, copy offload, compression, snapshots.
- Security/metadata: NT ACL, POSIX ACL fd/blob operations, xattr get/list/remove/set, AIO force, durable handle cookie/disconnect/reconnect, and readdir attributes.

## Control Flow and State
Each top-level macro starts dispatch at the connection's VFS stack, generally `conn->vfs_handles` or `fsp->conn->vfs_handles`. Each `NEXT` macro dispatches at `handle->next` for modules that intercept and delegate. This establishes the control-flow contract for stacked VFS modules.

## Persistence Behavior
The macros do not persist state, but many wrapped operations are persistence boundaries: file create/write/delete/rename, metadata mutation, ACL/xattr/quota changes, durable cookies, snapshots, and compression.

## Dependencies and Integration Points
The macros depend on `smb_vfs_call_*` declarations from `vfs.h` and on valid `connection_struct`, `files_struct`, and `vfs_handle_struct` relationships. They are included by `vfs.h`, so VFS callers and modules can use them uniformly.

## Risks
- Macro argument mistakes can dispatch through the wrong stack node or evaluate unexpected expressions.
- Module authors must call the `NEXT` variant when delegating; calling the top-level variant from inside a module can restart the stack and recurse.
- Some macros are long and easy to desynchronize from function signatures when `vfs_fn_pointers` changes.
- Because many macros derive connection from `fsp`, invalid or partially initialized `files_struct` values can crash before reaching wrapper validation.

## Test Signals
Build failures catch signature drift. Runtime signals include VFS module stacking tests, full-audit logging for each operation, durable/snapshot/xattr/ACL/quota module tests, and recursion/delegation tests for custom VFS modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/include/vfs_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/intl/linux-msg.sed -->
# sources/user-network-fs/samba/source3/intl/linux-msg.sed

## Purpose
`linux-msg.sed` converts Uniforum `.po` translation files into Linux `.msg` message catalog format. It was originally from GNU gettext tooling and assigns monotonically increasing numeric message IDs while emitting translations and original-message comments.

## Important Rules and Behavior
- On the first input line, inserts `$set 1 # Automatically created by po2msg.sed`, initializes hold space, and starts the numeric counter at `0`.
- For each `msgid`, strips the opening `msgid "`, increments the decimal counter in hold space using sed substitutions, and prints a comment line of the form `$ #<id> Original Message:(...)`.
- For each `msgstr`, rewrites the translated string to `# <translation>`, folds continuation lines, inserts trailing backslashes for multi-line translations, and prints catalog text.
- All other lines are deleted with final `d`.

## Control Flow and State
The sed script uses pattern space and hold space as state. Hold space carries the current message ID counter. Labels `:d`, `:b`, and `:a` implement decimal incrementing and multi-line `msgstr` processing. `N`, `P`, `D`, `G`, `x`, and branch-on-substitution commands form the control flow.

## Persistence Behavior
No runtime persistence. It writes generated `.msg` output to stdout for build/install tooling.

## Dependencies and Integration Points
It integrates with Samba's internationalization build process and must be used with the same `.po` ordering as `po-to-tbl` so generated catalog IDs match `cat-id-tbl.c`.

## Risks
- The script assumes simple `.po` syntax and has comments noting that old multi-line `msgid` handling does not work with newer formats.
- Message ordering must remain stable between this conversion and table generation.
- Shell/sed portability matters because the script may run during builds on different Unix variants.

## Test Signals
Builds that regenerate message catalogs, comparison of generated `.msg` IDs against `cat-id-tbl.c`, and sample `.po` files with single-line and multi-line `msgstr` entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/intl/linux-msg.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/addrchange.c -->
# sources/user-network-fs/samba/source3/lib/addrchange.c

## Purpose
`addrchange.c` implements an asynchronous network-address change watcher for Samba. On Linux with rtnetlink support, it listens for IPv4/IPv6 address add/delete notifications and exposes them through a tevent request API. On non-rtnetlink builds, it returns unsupported/not-implemented stubs.

## Important APIs, Types, and Functions
- `struct addrchange_context`: owns a `tdgram_context` wrapping a netlink route socket.
- `addrchange_context_create`: allocates context, opens `AF_NETLINK`/`NETLINK_ROUTE`, sets close-on-exec, makes it nonblocking, binds to `RTMGRP_IPV6_IFADDR | RTMGRP_IPV4_IFADDR`, and wraps the socket with `tdgram_bsd_existing_socket`.
- `struct addrchange_state`: per-request state containing event context, context pointer, received buffer/from address, change type, parsed sockaddr, and interface index.
- `addrchange_send`: creates a tevent request and starts `tdgram_recvfrom_send`.
- `addrchange_done`: receives datagrams, validates netlink sender and message length/type, extracts `RTM_NEWADDR`/`RTM_DELADDR`, parses `ifaddrmsg` and `IFA_LOCAL`/`IFA_ADDRESS` attributes into IPv4/IPv6 `sockaddr_storage`, retries ignored messages, and completes the request.
- `addrchange_recv`: returns `ADDRCHANGE_ADD`/`ADDRCHANGE_DEL`, address, and optional ifindex.

## Control Flow and State
The Linux control flow is asynchronous. `addrchange_send` arms one receive operation. `addrchange_done` either completes the request with a parsed address change, maps errors to NTSTATUS, or loops by freeing stale receive buffers and starting another receive for irrelevant datagrams. It rejects messages not from kernel netlink pid 0, undersized messages, malformed lengths, and unexpected message types. The context is long-lived; each request handles one valid address-change event.

## Persistence Behavior
No persistent storage is used. State is in-memory talloc/tevent request state and the kernel netlink socket. The observed address changes are kernel network-interface state, not Samba-owned persistence.

## Dependencies and Integration Points
Linux path depends on `linux/netlink.h`, `linux/rtnetlink.h`, `tsocket/tdgram`, `tevent`, talloc, nonblocking socket helpers, and NTSTATUS/unix error mapping. Call sites include smbd server address-change handling, winbindd address-change handling, and `torture/test_addrchange.c`.

## Risks
- The current length calculation for netlink attributes is security-sensitive; malformed kernel or injected messages must not overrun parsing.
- The watcher is Linux-specific; non-Linux builds get no working events.
- Ignored messages trigger recursive re-arming from callback context; sustained irrelevant traffic could keep the request active indefinitely.
- It trusts kernel-origin netlink messages only after checking `nl_pid == 0`, which is an important spoofing guard.

## Test Signals
`run_addrchange` in source3 torture directly exercises the API. Additional signals include smbd/winbindd reacting to address add/delete events, Linux-only build coverage with `HAVE_LINUX_RTNETLINK_H`, non-Linux stub build coverage, malformed netlink message tests, and leak checks for repeated retry paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/addrchange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/addrchange.h -->
# sources/user-network-fs/samba/source3/lib/addrchange.h

## Purpose
`addrchange.h` declares the public async API for Samba components that need notification when local network interface addresses are added or removed.

## Important APIs, Types, and Functions
- Opaque `struct addrchange_context`.
- `addrchange_context_create(TALLOC_CTX *mem_ctx, struct addrchange_context **pctx)`.
- `addrchange_send(TALLOC_CTX *mem_ctx, struct tevent_context *ev, struct addrchange_context *ctx)`.
- `enum addrchange_type` with `ADDRCHANGE_ADD` and `ADDRCHANGE_DEL`.
- `addrchange_recv(struct tevent_req *req, enum addrchange_type *type, struct sockaddr_storage *addr, uint32_t *if_index)`.

## Control Flow and State
The API uses Samba's standard tevent send/recv pattern. A daemon creates one context, starts a request with `addrchange_send`, receives one address-change event with `addrchange_recv`, then starts another request if it wants continuous monitoring. The context abstracts platform-specific watcher state.

## Persistence Behavior
No persistence. The API reports kernel/network state changes to in-memory daemon logic.

## Dependencies and Integration Points
It includes replacement/system network headers, talloc, tevent, and NTSTATUS. It is included by `addrchange.c`, smbd, winbindd, and torture tests.

## Risks
- Callers must handle `NT_STATUS_NOT_SUPPORTED` or NULL send requests on platforms without support.
- Continuous monitoring requires re-arming after every successful event.
- The output address and optional interface index are only valid after successful recv.

## Test Signals
Compile coverage in daemons, torture `run_addrchange`, platform stub tests, and daemon integration tests that verify listeners are re-armed after events.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/addrchange.h -->
