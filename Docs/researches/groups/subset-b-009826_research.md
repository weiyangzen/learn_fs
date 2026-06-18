# subset-b-009826 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.c -->
# sources/user-network-fs/samba/source3/modules/getdate.c

## Purpose
Generated GNU Bison C output for the natural-language date parser defined by `getdate.y`. Samba keeps this generated artifact so consumers can build without regenerating the grammar. Its public result is `get_date(const char *p, const time_t *now)`, which converts absolute or relative date text into a `time_t`.

## APIs, Types, And Control Flow
The file embeds Bison parser tables, `YYSTYPE`, `yyparse(struct parser_control *)`, generated stack growth and error recovery code, plus copied semantic actions from `getdate.y`. Runtime flow is: initialize `parser_control` from `now` or `time(0)`, call `yyparse`, reject duplicate date/time/day/zone components, normalize year/month/day through `mktime`, optionally adjust for explicit time zones, then add relative hours/minutes/seconds with overflow checks. `yylex` recognizes signed and unsigned numbers, words, comments in parentheses, punctuation, meridians, months, weekdays, units, relative words, and zone names.

## State, Dependencies, Integration
All parse state is per-call in `parser_control`; there is no persistent storage. It depends on libc time APIs, optional `tm_gmtoff`, optional `tzname`, and the generated Bison skeleton. It integrates with `vfs_readonly.c`, which uses `get_date()` to parse configured readonly time windows.

## Risks And Test Signals
Risks include divergence from `getdate.y` if regenerated with a different Bison version, ambiguous timezone abbreviations, host-dependent DST handling, integer overflow in numeric lexing before later guards, and localtime/mktime boundary behavior. Useful tests parse absolute dates, ISO dates, `now`, `yesterday`, ordinal weekdays, numeric zones, DST local zone names, invalid duplicate clauses, and `time_t` boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.h -->
# sources/user-network-fs/samba/source3/modules/getdate.h

## Purpose
Small portability header for the `get_date()` natural-language date parser. It exposes the single parser API while handling older C prototype conventions and platform-dependent time includes.

## APIs, Types, And Control Flow
The only exported symbol is `time_t get_date(const char *p, const time_t *now)`, declared through the `PARAMS` macro for compatibility with pre-ANSI builds. Include control flow selects `config.h`, VMS `types.h`, or POSIX `sys/types.h`, `sys/time.h`, and `time.h` based on `TIME_WITH_SYS_TIME` and `HAVE_SYS_TIME_H`.

## State, Dependencies, Integration
The header has no state or persistence. It depends on Samba or autoconf feature macros and the system time type definitions. It is included by the generated parser implementation and by modules that call `get_date()`, notably the readonly VFS module.

## Risks And Test Signals
The main risk is build portability: incorrect config macros can hide `time_t` or duplicate time declarations on unusual platforms. Tests are compile-time signals: consumers should include this header alone and through `getdate.c`, with and without modern prototypes, and verify the exported function signature remains consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.y -->
# sources/user-network-fs/samba/source3/modules/getdate.y

## Purpose
Authoritative Bison grammar and lexer source for Samba's imported GNU `get_date()` parser. It parses human-oriented absolute and relative time expressions into a `time_t`.

## APIs, Types, And Control Flow
The file defines `textint`, lexical `table`, meridian constants, and `struct parser_control`. Grammar rules recognize times (`10pm`, `10:30`, `10:30:05 -0500`), local and named zones, weekdays and ordinal weekdays, slash dates, ISO-style dates, month-name dates, compact numeric dates/times, and relative units with `ago`. After parsing, `get_date()` applies semantic checks, resolves two-digit years, uses `mktime`, handles explicit zones with `tm_gmtoff` or `tm_diff`, applies weekday offsets, and adds relative seconds with overflow detection.

## State, Dependencies, Integration
All parser state is call-local and reentrant through `%pure-parser`; no persistent data is written. Static lookup tables encode supported words, months, weekdays, time units, relative words, common zone abbreviations, and military zones. It depends on libc `localtime`, `gmtime`, `mktime`, ctype/string APIs, optional timezone fields, and Bison generation.

## Risks And Test Signals
The grammar intentionally has 13 shift/reduce conflicts, so rule changes can alter accepted parses. Ambiguous abbreviations and locale/DST behavior are host-sensitive. The word buffer truncates after 20 characters for lookup, and signed numeric accumulation can overflow before final checks. Test signals should cover every grammar family, duplicate component rejection, comments, plural units, military zones, local DST abbreviations, `ago` inversion, and regeneration equivalence against `getdate.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/getdate.y -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/hash_inode.c -->
# sources/user-network-fs/samba/source3/modules/hash_inode.c

## Purpose
Provides a deterministic synthetic inode generator for named streams and xattr-backed stream views. It hashes the underlying device, inode, and stream name into an `SMB_INO_T`.

## APIs, Types, And Control Flow
The exported API is `SMB_INO_T hash_inode(const SMB_STRUCT_STAT *sbuf, const char *sname)`. It uppercases the stream name with `talloc_strdup_upper`, enters GnuTLS FIPS lax mode, initializes a SHA1 hash, feeds `st_ex_dev`, `st_ex_ino`, and the uppercase name bytes, finalizes into a digest, and copies the leading bytes into the result. On any GnuTLS error it returns zero after cleanup.

## State, Dependencies, Integration
No persistent state is kept. It depends on Samba stat wrappers, talloc, GnuTLS hashing, and Samba's FIPS helper macros. Callers in `vfs_fruit.c` and `vfs_streams_xattr.c` use it to expose stable inode values for alternate data streams.

## Risks And Test Signals
Risks include SHA1 collision possibility, result truncation to `SMB_INO_T`, endian/width differences across platforms, return value zero on hashing failure, and `SMB_ASSERT` abort if name allocation fails. Tests should assert case-insensitive stream-name hashing, different stream names/devices/inodes producing different values, deterministic output within one build, and graceful behavior when GnuTLS initialization fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/hash_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/hash_inode.h -->
# sources/user-network-fs/samba/source3/modules/hash_inode.h

## Purpose
Declares the synthetic inode hash helper used by stream-capable VFS modules.

## APIs, Types, And Control Flow
Exports `SMB_INO_T hash_inode(const SMB_STRUCT_STAT *sbuf, const char *sname)`. The function takes an existing Samba stat buffer and stream/xattr name, and returns an inode-sized deterministic hash. There is no inline logic.

## State, Dependencies, Integration
The header has no state. It relies on prior inclusion of Samba type definitions for `SMB_INO_T` and `SMB_STRUCT_STAT`, commonly supplied by `includes.h`. It is included by `vfs_fruit.c`, `vfs_streams_xattr.c`, and the implementation file.

## Risks And Test Signals
The main risk is type-context fragility if included without Samba base headers. Compile tests should include it from modules that use stream inode synthesis and validate ABI consistency with `hash_inode.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/hash_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/lib_vxfs.c -->
# sources/user-network-fs/samba/source3/modules/lib_vxfs.c

## Purpose
Runtime wrapper around Veritas VxFS xattr and writeable-xattr helpers from `/usr/lib64/vxfsmisc.so`. It lets Samba VFS code call VxFS-specific APIs when the library is present while returning standard errno-style failures when unavailable.

## APIs, Types, And Control Flow
The file defines function pointers for `vxfs_nxattr_set`, `vxfs_nxattr_get`, `vxfs_nxattr_remove`, `vxfs_nxattr_list`, `vxfs_wattr_set`, and `vxfs_wattr_check`. Public wrappers are fd and path variants for set/get/remove/list xattrs plus set/check writeable xattr state. Path variants open files or directories, call the fd wrapper, and close the descriptor. `vxfs_init()` lazily `dlopen`s the library and resolves all symbols with `dlsym`.

## State, Dependencies, Integration
State is process-local static function pointers and a static library handle. The persistent state affected is filesystem xattr data and VxFS writeable-xattr metadata. It depends on `dlopen`, POSIX `open/close`, `vfs_vxfs.h`, and the external Veritas library. Integration is through VxFS-specific VFS modules.

## Risks And Test Signals
Missing symbols are treated as nonfatal at init and later return `ENOSYS`, which is useful but can delay diagnostics. Path wrappers open non-directories with `O_WRONLY` for mutating operations and `O_RDONLY` for reads, so permission behavior differs from fd callers. Test signals include absent library, partially missing symbols, EFBIG to ERANGE mapping, directory path operations, close-after-error behavior, and errno preservation for returned VxFS error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/lib_vxfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4_acls.c -->
# sources/user-network-fs/samba/source3/modules/nfs4_acls.c

## Purpose
Core NFSv4 ACL conversion library. It converts between Samba's internal `SMB4ACL_T` list representation and Windows security descriptors, and supplies stat wrappers that retry with `CAP_DAC_OVERRIDE` for NFSv4 ACL protected paths.

## APIs, Types, And Control Flow
Private structs `SMB4ACE_T` and `SMB4ACL_T` store ACE properties, control flags, count, and a linked list. Exported helpers create ACLs, append and iterate ACEs, get/set control flags, identify inherited ACEs, read VFS parameters, wrap stat/fstat/lstat/fstatat, get NT ACLs from an SMB4 ACL, and set NT ACLs through a native setter callback. Read conversion maps NFSv4 special IDs (`OWNER@`, `GROUP@`, `EVERYONE@`) and uid/gid ACEs to SIDs, maps flags, optionally expands owner/group inheriting ACEs to creator-owner/group, suppresses inappropriate inheritance on files, and builds a security descriptor. Write conversion optionally changes owner/group, maps Windows ACEs to NFSv4 ACEs, resolves SIDs to Unix ids, handles duplicate ACE policy (`merge`, `ignore`, `reject`, `dontcare`), substitutes owner/group with special IDs in simple or special mode, copies descriptor control flags, and invokes the caller's native ACL writer as root when ownership changes require it.

## State, Dependencies, Integration
The ACL object is talloc-owned transient state. Persistent effects happen through the native `set_nfs4_native` callback and optional `chown_if_needed`. Dependencies include Samba id mapping, SID utilities, security descriptor builders, VFS stat calls, loadparm, and privilege elevation helpers. It is integrated by NFSv4 ACL VFS modules such as GPFS, ZFS, AIX ACL, and `vfs_nfs4acl_xattr`.

## Risks And Test Signals
Critical risks are authorization semantics drift when mapping inheritance, silent ACE drops when SIDs cannot map to Unix IDs, duplicate merge policy changing masks, root elevation around native set, owner/group substitution with `ID_TYPE_BOTH`, and deprecated modes still supported. Tests should cover round-trips between NFSv4 and NT ACLs, owner/group chown plus ACL write failure, file versus directory inheritance flags, duplicate ACE policies, unmappable SIDs, `SECINFO_*` combinations, `SEC_DESC_*` control flags, and EACCES stat fallback with and without capability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4_acls.h -->
# sources/user-network-fs/samba/source3/modules/nfs4_acls.h

## Purpose
Public contract for Samba's NFSv4 ACL abstraction and NT ACL conversion helpers.

## APIs, Types, And Control Flow
The header defines `SMB_NFS4_ACEWHOID_T`, `SMB_ACE4PROP_T`, special identity constants, ACE type constants, NFSv4 flag and mask constants, opaque `SMB4ACL_T` and `SMB4ACE_T`, mode and duplicate policy enums, and `struct smbacl4_vfs_params`. It declares stat wrappers, ACL list construction and iteration helpers, control flag accessors, `nfs_ace_is_inherit`, NT ACL get/set conversion functions, and the native set callback type.

## State, Dependencies, Integration
No state is stored in the header. It requires Samba VFS, file, security descriptor, and talloc types from including contexts. It is the shared interface for native NFSv4 ACL modules and xattr-backed NFSv4 ACL encoders.

## Risks And Test Signals
The constants are semantic ABI: changing bit values breaks on-disk, wire, and conversion behavior. The opaque ACL list requires callers to use helper APIs rather than struct access. Compile tests should cover every module that includes it, and behavior tests should exercise each declared conversion entry point with both special and numeric identities.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4_acls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr.h -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr.h

## Purpose
Shared configuration header for the `nfs4acl_xattr` VFS module and its encoding-specific converters.

## APIs, Types, And Control Flow
Defines `NFS4ACL_XDR_MAX_ACES` as 8192, `enum nfs4acl_encoding` with NDR, XDR, and NFS encodings, and `struct nfs4acl_config`. The config records NFS protocol version, encoding, xattr name, generic NFSv4 ACL parameters, default ACL style, whether NFS identities are numeric, and whether mode validation is enabled.

## State, Dependencies, Integration
The header declares configuration shape only. Runtime instances are attached to VFS handles by `vfs_nfs4acl_xattr.c` and consumed by `nfs4acl_xattr_ndr.c`, `nfs4acl_xattr_xdr.c`, and `nfs4acl_xattr_nfs.c`.

## Risks And Test Signals
The encoding enum drives persistent xattr interpretation, so mismatched config can make stored ACLs unreadable or incorrectly mapped. Test signals include initialization with each encoding, max ACE enforcement, version 4.0 versus 4.1 control flag behavior, numeric versus name ID modes, and custom xattr names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.c -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.c

## Purpose
Converts between Samba `SMB4ACL_T` objects and Samba NDR-encoded `struct nfs4acl` blobs stored in extended attributes.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_ndr_blob_to_smb4()` and `nfs4acl_smb4acl_to_ndr_blob()`. Blob-to-ACL pulls an NDR `nfs4acl`, creates an SMB4 ACL, maps versioned ACL flags to security descriptor control flags, then copies ACE type, flags, mask, numeric id, and special strings for owner/group/everyone into `SMB_ACE4PROP_T`. ACL-to-blob allocates a generated `struct nfs4acl`, copies SMB4 ACEs into it, maps control flags for versions above 4.0, emits special `e_who` strings or empty strings for numeric ids, optionally rejects ACLs with no special IDs under `nfs4acl_xattr:denymissingspecial`, and NDR-pushes the result.

## State, Dependencies, Integration
No durable state is held by the converter. It reads `struct nfs4acl_config` from the VFS handle and persists only the returned `DATA_BLOB` through its caller. Dependencies include generated NDR code, `nfs4_acls.h`, loadparm for `denymissingspecial`, and talloc.

## Risks And Test Signals
Unsupported special IDs are skipped without compacting the precomputed ACE count, which is worth regression coverage. Numeric identities carry an empty `e_who`, so readers depend on `e_id` and flags. Tests should cover NDR parse failures, all special identities, version 4.0 flag suppression, `denymissingspecial`, empty ACLs, malformed blobs, and round-trip stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.h -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.h

## Purpose
Declares NDR xattr conversion functions for NFSv4 ACL storage.

## APIs, Types, And Control Flow
Exports `nfs4acl_ndr_blob_to_smb4()` to parse a `DATA_BLOB` into an `SMB4ACL_T`, and `nfs4acl_smb4acl_to_ndr_blob()` to serialize an `SMB4ACL_T` into a blob. Both require a VFS handle for configuration and a talloc context for returned allocations.

## State, Dependencies, Integration
The header stores no state. It forward-declares `SMB4ACL_T` and relies on Samba VFS, NTSTATUS, talloc, and DATA_BLOB definitions supplied by including modules. It is consumed by `vfs_nfs4acl_xattr.c`.

## Risks And Test Signals
The declarations are the handoff between generic xattr VFS logic and NDR persistence. Compile and link tests should ensure the NDR converter is available whenever the NDR encoding is selectable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_ndr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.c -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.c

## Purpose
Converts between `SMB4ACL_T` and kernel/NFS-style XDR ACL blobs stored under `system.nfs4_acl`. Unlike the internal XDR numeric format, this format stores NFSv4 who fields as UTF-8 strings such as `OWNER@`, numeric text, or user/group names.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_smb4acl_to_nfs_blob()` and `nfs4acl_nfs_blob_to_smb4()`. The file supports NFSv4.0 and NFSv4.1 structures. Serialization maps SMB4 special IDs to NFS strings, maps uid/gid either to numeric strings when `nfs4_id_numeric` is set or to names via `getpwuid`/`getgrgid`, computes XDR blob sizes including aligned identifier lengths with overflow checks, and calls `xdr_nfsacl40` or `xdr_nfsacl41`. Deserialization XDR-decodes the configured version, maps special strings through a lookup table, maps group or user names/numbers with `nametogid`/`nametouid`, maps 4.1 flags to security descriptor control flags, and appends valid ACEs to a new SMB4 ACL.

## State, Dependencies, Integration
The converter has transient talloc/XDR state only. Persistent behavior is the encoded xattr blob returned to the caller. It depends on `<rpc/xdr.h>`, generated `nfs41acl.h`, passwd/group lookups, Samba id helpers, and `nfs4acl_xattr_util`. If RPC XDR headers are absent, both public functions return `NT_STATUS_NOT_SUPPORTED`.

## Risks And Test Signals
The biggest risk is silent ACE loss: unknown users, groups, unsupported special IDs, or unqualified nonnumeric names are skipped. Name service changes can make persisted name ACLs non-reproducible, so numeric mode should be tested separately. Additional tests should cover 4.0 versus 4.1 flags, overflow size guards, max ACE count, malformed XDR, special identities beyond owner/group/everyone, group flag preservation, and no-XDR build behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.h -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.h

## Purpose
Declares the NFS/kernel xattr encoding adapter for NFSv4 ACLs.

## APIs, Types, And Control Flow
Defines the persistent xattr name `NFS4ACL_NFS_XATTR_NAME` as `system.nfs4_acl`. Exports `nfs4acl_nfs_blob_to_smb4()` and `nfs4acl_smb4acl_to_nfs_blob()` for parsing and serializing ACL blobs. There is no inline control flow.

## State, Dependencies, Integration
The header is stateless and forward-declares `SMB4ACL_T`. It is included by the converter implementation and by `vfs_nfs4acl_xattr.c` when NFS encoding is configured.

## Risks And Test Signals
The xattr name is part of the storage contract. Tests should verify the VFS module selects this name by default for NFS encoding and rejects or reports unsupported conversion on platforms without RPC XDR support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.c -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.c

## Purpose
Small utility implementation for translating NFSv4 ACL flag bits and Samba security descriptor control flags.

## APIs, Types, And Control Flow
When `HAVE_RPC_XDR_H` is defined, exports `smb4acl_to_nfs4acl_flags(uint16_t)` and `nfs4acl_to_smb4acl_flags(unsigned)`. The first maps `SEC_DESC_DACL_AUTO_INHERITED`, `SEC_DESC_DACL_PROTECTED`, and `SEC_DESC_DACL_DEFAULTED` to `ACL4_AUTO_INHERIT`, `ACL4_PROTECTED`, and `ACL4_DEFAULTED`. The second maps those bits back and always starts the Samba control flags with `SEC_DESC_SELF_RELATIVE`.

## State, Dependencies, Integration
There is no state or persistence. Dependencies are Samba security descriptor constants and `nfs41acl.h` constants behind RPC XDR availability. The helpers are used by NFS and XDR xattr converters to avoid duplicating flag mapping.

## Risks And Test Signals
If compiled without RPC XDR support the header still declares functions, but this C file does not define them; consumers must also be guarded by the same build feature. Tests should compile both feature paths and validate exact bit mapping, including preservation of unrelated bits by omission.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.h -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.h

## Purpose
Declares shared NFSv4 ACL control-flag conversion helpers for xattr encoders.

## APIs, Types, And Control Flow
Exports `unsigned smb4acl_to_nfs4acl_flags(uint16_t smb4acl_flags)` and `uint16_t nfs4acl_to_smb4acl_flags(unsigned nfsacl41_flags)`. The functions convert between security descriptor DACL control bits and NFSv4.1 ACL flag bits.

## State, Dependencies, Integration
The header has no state. It relies on including contexts for integer typedefs and is used by XDR/NFS converters that need 4.1 control flag handling.

## Risks And Test Signals
The implementation is feature-gated by RPC XDR support, so declarations must only be linked from compatible build paths. Compile tests should cover `HAVE_RPC_XDR_H` on and off.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.c -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.c

## Purpose
Converts between `SMB4ACL_T` and a numeric NFSv4.1 XDR ACL representation stored in `security.nfs4acl_xdr`.

## APIs, Types, And Control Flow
Public functions are `nfs4acl_smb4acl_to_xdr_blob()` and `nfs4acl_xdr_blob_to_smb4()`. Serialization allocates a compact `nfsacl41i` with inline ACE array, maps control flags for versions above 4.0, converts special owner/group/everyone to `ACEI4_SPECIAL_WHO` numeric constants, copies uid/gid values for ordinary ACEs, computes fixed-size XDR blob length with max ACE and overflow checks, and encodes via `xdr_nfsacl41i`. Deserialization estimates ACE count from blob length, allocates an internal ACL, XDR-decodes, clears flags for version 4.0, maps special ids back to SMB4 special identities, copies uid/gid based on group flags, and appends ACEs to an SMB4 ACL.

## State, Dependencies, Integration
State is transient. Persistent data is the returned blob that callers put into xattrs. It depends on RPC XDR headers, `nfs41acl.h`, `nfs4acl_xattr_util`, and VFS handle configuration. Without RPC XDR headers, public functions return `NT_STATUS_NOT_SUPPORTED`.

## Risks And Test Signals
ACE count inference from blob size assumes the fixed internal layout and should be tested with truncated and padded blobs. Unsupported special IDs are skipped during conversion, and `smb_add_ace4()` return is not checked in deserialization. Tests should cover max ACE count, malformed XDR, version 4.0 flag clearing, special and numeric identities, group flag preservation, no-XDR builds, and round-trip byte stability for representative ACLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.h -->
# sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.h

## Purpose
Declares the numeric XDR xattr adapter for NFSv4 ACL storage.

## APIs, Types, And Control Flow
Defines `NFS4ACL_XDR_XATTR_NAME` as `security.nfs4acl_xdr`. Exports `nfs4acl_xdr_blob_to_smb4()` and `nfs4acl_smb4acl_to_xdr_blob()` for converting between xattr blobs and `SMB4ACL_T`.

## State, Dependencies, Integration
The header has no state and forward-declares no local data beyond the xattr name. It is included by `vfs_nfs4acl_xattr.c` and the XDR converter implementation.

## Risks And Test Signals
The xattr name and function signatures are persistent integration contracts. Tests should ensure configured XDR encoding uses this name and that unsupported-platform return paths are handled by the caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/nfs4acl_xattr_xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/non_posix_acls.c -->
# sources/user-network-fs/samba/source3/modules/non_posix_acls.c

## Purpose
Builds a stable serialized hash wrapper for non-POSIX ACL blobs by combining the ACL blob with current file owner, group, and mode metadata.

## APIs, Types, And Control Flow
The exported helper `non_posix_sys_acl_blob_get_fd_helper()` takes an existing ACL `DATA_BLOB`, obtains file stat data from `fsp->fsp_name->st` or `smb_vfs_call_fstat`, fills `xattr_sys_acl_hash_wrapper` with ACL blob, uid, gid, and mode, and NDR-pushes that wrapper into the output blob. On stat failure it returns `-1`; on NDR failure it sets `errno = EINVAL`.

## State, Dependencies, Integration
The helper uses only stack/talloc-frame state. It persists nothing directly; callers use the output blob as an ACL identity/hash source. Dependencies are generated `ndr_xattr.h`, Samba VFS fstat, DATA_BLOB, and talloc. It integrates with VFS modules that expose ACL blobs but do not use POSIX ACL syscalls.

## Risks And Test Signals
Risk centers on metadata coupling: owner/group/mode changes alter the wrapper even when the ACL blob is unchanged. Tests should cover valid cached stat, fstat fallback, fstat failure, NDR serialization failure, and ensuring uid/gid/mode changes produce distinct output blobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/non_posix_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/non_posix_acls.h -->
# sources/user-network-fs/samba/source3/modules/non_posix_acls.h

## Purpose
Declares the non-POSIX ACL blob wrapper helper.

## APIs, Types, And Control Flow
Exports `non_posix_sys_acl_blob_get_fd_helper(vfs_handle_struct *handle, files_struct *fsp, DATA_BLOB acl_as_blob, TALLOC_CTX *mem_ctx, DATA_BLOB *blob)`. The function serializes the supplied ACL blob together with file metadata into an output blob.

## State, Dependencies, Integration
The header has no state. It relies on Samba VFS, file, talloc, and DATA_BLOB definitions from the including module. It is the interface used by non-POSIX ACL VFS code to provide ACL blob identity data.

## Risks And Test Signals
The signature passes the input blob by value and output by pointer, so callers must preserve input lifetime through serialization and manage output talloc ownership. Compile tests should include it from relevant VFS modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/non_posix_acls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/offload_token.c -->
# sources/user-network-fs/samba/source3/modules/offload_token.c

## Purpose
Implements in-process ODX/copy-offload token storage and validation. It lets VFS modules create opaque resume/copy tokens, map them back to open `files_struct` handles, and enforce SMB access rules before server-side copy operations.

## APIs, Types, And Control Flow
`vfs_offload_token_ctx_init()` lazily creates a `vfs_offload_ctx` with an in-memory rbt dbwrap database. `vfs_offload_token_create_blob()` creates 20-byte or 24-byte tokens containing persistent id, volatile id, and fsctl code at fixed offsets. `vfs_offload_token_db_store_fsp()` stores a token-to-fsp pointer under db lock and attaches a `fsp_token_link` destructor to delete the record when the file handle is freed. `vfs_offload_token_db_fetch_fsp()` parses the record back to a typed `files_struct *`. `vfs_offload_token_check_handles()` enforces same session, valid and non-closing handles, non-directory and non-IPC/PRINT shares, writable destination, and readable source.

## State, Dependencies, Integration
State is per-context in-memory dbwrap data, lifetime-bound to the Samba client or module context. No token database survives process lifetime. Dependencies include dbwrap rbt, talloc destructors, SMB2 file handle structures, access-check helpers, and FSCTL constants. Integrated by `vfs_default.c`, `vfs_btrfs.c`, and `vfs_fruit.c`.

## Risks And Test Signals
Tokens contain handle IDs but the authoritative lookup is an in-memory pointer, so process restart or handle destruction invalidates them. Pointer serialization requires record size validation and talloc type checking. Tests should cover duplicate token store for same and different fsp, destructor cleanup, unknown tokens, malformed db values, each access-denied branch, FSCTL length selection, and copychunk-specific destination read checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/offload_token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/offload_token.h -->
# sources/user-network-fs/samba/source3/modules/offload_token.h

## Purpose
Public interface for Samba VFS offload token creation, lookup, and handle validation.

## APIs, Types, And Control Flow
Forward-declares `vfs_offload_ctx` and `req_resume_key_rsp`, defines token offsets for persistent id, volatile id, and fsctl, and declares context initialization, database store/fetch, token blob creation, and handle checking functions.

## State, Dependencies, Integration
The header has no state. It exposes fixed offsets that are shared with the implementation and VFS callers that may inspect token layout. Included by default, btrfs, and fruit VFS modules for ODX/copychunk support.

## Risks And Test Signals
The offset constants are ABI-like within Samba. Compile tests should ensure all callers agree on token size and offsets, and behavior tests should validate unsupported FSCTL handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/offload_token.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/posixacl_xattr.c -->
# sources/user-network-fs/samba/source3/modules/posixacl_xattr.c

## Purpose
Implements POSIX ACL get/set/delete helpers that store Linux POSIX ACL xattr binary format directly, used by backends that expose ACLs through xattrs instead of native sys_acl calls.

## APIs, Types, And Control Flow
Public functions are `posixacl_xattr_acl_get_fd()`, `posixacl_xattr_acl_set_fd()`, and `posixacl_xattr_acl_delete_def_fd()`. The parser validates a 4-byte version, requires 8-byte entries, maps Linux ACL tags and permissions to Samba `smb_acl_entry`, and fills uid/gid for named users/groups. Serialization maps Samba ACL entries back to little-endian tag/perm/id entries, writes version `0x0002`, and qsorts entries by tag then id. Get selects `system.posix_acl_access` or `system.posix_acl_default`, retries after ERANGE by querying actual size, parses the blob, and falls back to a three-entry mode-derived ACL on empty/missing xattr. Set serializes to alloca memory and writes via `SMB_VFS_FSETXATTR`; delete removes the default ACL xattr.

## State, Dependencies, Integration
No in-memory state persists between calls. Persistent state is the xattr content. Dependencies include Samba sys_acl structures, endian helpers, VFS fgetxattr/fsetxattr/fremovexattr, and POSIX ACL constants. It is integrated by GlusterFS and Ceph VFS modules.

## Risks And Test Signals
Risks include stack allocation sized by ACL entry count, strict version/size rejection, mode fallback masking missing default ACL semantics, and ordering changes from qsort. Tests should cover all ACL tags, invalid tags, malformed sizes, unknown version, ERANGE retry, ENOATTR fallback, access versus default names, large ACL counts, and byte-for-byte serialization ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/posixacl_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/posixacl_xattr.h -->
# sources/user-network-fs/samba/source3/modules/posixacl_xattr.h

## Purpose
Declares POSIX ACL over xattr helper APIs.

## APIs, Types, And Control Flow
Exports `posixacl_xattr_acl_get_fd()`, `posixacl_xattr_acl_set_fd()`, and `posixacl_xattr_acl_delete_def_fd()`. These mirror Samba sys_acl VFS hooks for reading, writing, and deleting default ACLs on an open file.

## State, Dependencies, Integration
The header has no state. It relies on Samba VFS, file, ACL, and talloc types from including code. GlusterFS and Ceph VFS modules use it to route sys_acl hooks through xattr persistence.

## Risks And Test Signals
Callers must pass a valid ACL type and open file structure; invalid types map to `EINVAL` in the implementation. Compile tests should confirm hook signatures remain compatible with `struct vfs_fn_pointers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/posixacl_xattr.h -->
