# Research: subset-b-009827

Grouped research for Samba `source3/modules` ACL, reparse-point, varlink keybridge, and asynchronous I/O module files. Each section preserves the source path as its title and is wrapped for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c -->
# sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c

## Purpose
This is a cmocka unit-test translation unit for Samba's NFSv4 ACL conversion code. It includes `nfs4_acls.c` directly so static helpers and conversion behavior can be exercised without a loaded VFS module. The tests verify round trips and edge cases between Samba's internal `SMB4ACL_T`/`SMB_ACE4PROP_T` representation and Windows security ACL/DACL structures.

## Important APIs, Types, And Functions
The test-local `struct test_sids` table maps synthetic SIDs and creator SIDs to `struct unixid` values with `ID_TYPE_UID`, `ID_TYPE_GID`, and `ID_TYPE_BOTH`. `group_setup` parses those SIDs and seeds `idmap_cache_set_sid2unixid`; `group_teardown` removes them. Test cases target `smbacl4_nfs42win`, `smbacl4_win2nfs4`, `smb_create_smb4acl`, `smb_add_ace4`, `smb_first_ace4`, `smb_next_ace4`, `smb_get_ace4`, `smb_get_naces`, `smbacl4_get_controlflags`, and security ACL constructors such as `init_sec_ace` and `make_sec_acl`.

## Control Flow
`main` requires an `smb.conf`, initializes a talloc stack frame, loads global configuration with `lp_load_global`, and runs a cmocka group with idmap cache setup/teardown. The tests first prove the cache mappings work, then cover empty ACL conversion, ACE type mapping, inheritance and audit flag mapping, individual permission bits and generic masks, special principals, creator owner/group handling, `map_full_control`, duplicate ACE policies (`e_dontcare`, `e_reject`, `e_ignore`, `e_merge`), `e_special` mode, `ID_TYPE_BOTH` ambiguity, and duplicate removal in NFSv4-to-DACL conversion.

## State And Persistence
The only persistent external state touched is Samba's process-local idmap cache during the test group; setup inserts entries and teardown deletes them. All ACLs, SIDs, and security descriptors are talloc-owned temporary objects. The tests do not write files or durable Samba databases.

## Dependencies And Integration Points
The file depends on `nfs4_acls.c`, `librpc/gen_ndr/idmap.h`, `idmap_cache.h`, cmocka, talloc, Samba SID helpers, security descriptor helpers, and loadparm initialization. It is a direct signal for the NFSv4 ACL behavior used by NFSv4-aware VFS modules such as AIX JFS2 ACL support and by Samba's Windows ACL mapping layer.

## Risks
Because the source includes an implementation `.c` file, changes in `nfs4_acls.c` static names or dependencies can break compilation. The table-driven tests encode exact ordering, flags, and masks, so intentional semantic changes require careful test updates. `ID_TYPE_BOTH` behavior is particularly subtle because owner/group decisions change whether ACEs become user, group, or special owner/group entries.

## Test Signals
Strong signals are the 21 cmocka cases in `main`, especially the full-control, duplicate handling, `e_special`, and `ID_TYPE_BOTH` cases. A passing run with a valid `smb.conf` indicates the ACL mapper preserves expected masks, flags, SID resolution, special principal handling, and duplicate policy behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_nfs4_acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c

## Purpose
This cmocka unit test verifies the operation-name table used by the `vfs_full_audit` module. It is a small compile-and-runtime guard that every VFS operation index has a non-null audit name and that the recorded operation type matches the array index.

## Important APIs, Types, And Functions
The file declares `vfs_full_audit_init` for static builds, includes `vfs_full_audit.c` directly, and checks `vfs_op_names`. `test_full_audit_array` iterates from zero to `SMB_VFS_OP_LAST - 1`, asserting `vfs_op_names[i].name != NULL` and `vfs_op_names[i].type == i`.

## Control Flow
`main` builds a one-test cmocka array, enables subunit output, and runs without custom setup or teardown. The included module provides the audit operation metadata under test.

## State And Persistence
No durable state is touched. The test only reads static data compiled from `vfs_full_audit.c`.

## Dependencies And Integration Points
It depends on Samba includes, `smbd/smbd.h`, cmocka, and the full-audit VFS implementation. It integrates with the build as a regression test for keeping VFS operation enum ordering synchronized with audit metadata.

## Risks
The test only validates table completeness and enum alignment, not audit logging behavior, syslog formatting, configuration parsing, or success/failure filtering. Direct inclusion of the implementation can expose static-build or dependency drift.

## Test Signals
A passing run shows that newly added or reordered `SMB_VFS_OP_*` values have matching `vfs_op_names` entries. Failures usually indicate a missing audit operation name or an enum/table ordering bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_full_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c

## Purpose
This cmocka unit test covers pure mapping helpers in Samba's GPFS VFS module. It validates translation between Samba share-access and DOS attribute bits and the GPFS deny/lease/winattr constants used when integrating with GPFS-specific file APIs.

## Important APIs, Types, And Functions
The test includes `vfs_gpfs.c` directly. `test_share_deny_mapping` checks `vfs_gpfs_share_access_to_deny` for all meaningful combinations of `FILE_SHARE_READ`, `FILE_SHARE_WRITE`, and `FILE_SHARE_DELETE`. When `HAVE_KERNEL_OPLOCKS_LINUX` is defined, `test_gpfs_lease_mapping` checks `lease_type_to_gpfs` for `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`. The DOS attribute tests validate `vfs_gpfs_winattrs_to_dosmode` and `vfs_gpfs_dosmode_to_winattrs`.

## Control Flow
`main` assembles the conditional cmocka test list and runs it with subunit output. Each test is table-like but expressed as direct assertions against expected bit masks.

## State And Persistence
No GPFS filesystem, TDB, xattr, or share state is mutated. The tests exercise in-process mapping functions only.

## Dependencies And Integration Points
Dependencies include cmocka, Samba DOS/share constants, GPFS constants from the included implementation, and optional Linux kernel oplock support. These helpers are integration points between Samba's SMB protocol semantics and GPFS kernel/library semantics for share denies, leases, and Windows attributes.

## Risks
The test encodes the GPFS limitation that Samba cannot express "deny delete only" and therefore maps `FILE_SHARE_READ|FILE_SHARE_WRITE` to zero deny bits. It does not cover real GPFS ioctl behavior, error paths, fileset handling, or lease lifecycle.

## Test Signals
Passing tests indicate GPFS bit translations remain stable. Failures are high-signal for accidental constant changes, wrong bitwise inversion of share modes, or DOS attribute translation regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_gpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c -->
# sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c

## Purpose
This cmocka test verifies conversion from Samba's abstract POSIX ACL representation to a native POSIX `acl_t` in the `vfs_posixacl` module. It focuses on a simple ACL containing owner, group, and other entries.

## Important APIs, Types, And Functions
The file includes `vfs_posixacl.c` directly. `smb_acl_add_entry` constructs Samba ACL entries using `sys_acl_create_entry`, `sys_acl_set_tag_type`, optional `sys_acl_set_qualifier`, `sys_acl_get_permset`, `sys_acl_add_perm`, and `sys_acl_set_permset`. `acl_check_entry` inspects native entries with `acl_get_permset`, `acl_get_tag_type`, optional `acl_get_qualifier`, and `acl_get_perm` or `acl_get_perm_np`. `test_smb_acl_to_posix_simple_acl` calls `smb_acl_to_posix`.

## Control Flow
`main` requires an `smb.conf`, initializes talloc/loadparm state, and runs the single cmocka case. The case builds an SMB ACL with `SMB_ACL_USER_OBJ`, `SMB_ACL_GROUP_OBJ`, and `SMB_ACL_OTHER`, converts it, then iterates native ACL entries in order and checks tag and read/write/execute permissions.

## State And Persistence
All ACL structures are memory-local; the native ACL object is freed with `acl_free`, and the talloc frame is released. No filesystem ACLs are read or written.

## Dependencies And Integration Points
The test depends on POSIX ACL library functions, Samba's `sys_acl_*` compatibility layer, talloc, loadparm, and cmocka. It directly validates the utility path used when Samba converts internal ACL objects before calling platform ACL setters.

## Risks
Coverage is narrow: it does not test named users/groups, masks, default ACLs, deny-like cases, invalid ACLs, or filesystem set/get integration. Ordering expectations can be platform-sensitive if `smb_acl_to_posix` changes construction order.

## Test Signals
The strongest signal is successful conversion and native inspection of the three base ACL entries. Failing assertions point to tag mapping, qualifier handling, or permission-bit conversion bugs in `vfs_posixacl.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/test_vfs_posixacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.c -->
# sources/user-network-fs/samba/source3/modules/util_reparse.c

## Purpose
This utility implements SMB FSCTL reparse-point get, tag, set, and delete operations for Samba file handles. It bridges Windows reparse buffer semantics with Samba xattrs, DOS attributes, Unix special files, and symlink reparse helpers.

## Important APIs, Types, And Functions
Exported functions are `fsctl_get_reparse_point`, `fsctl_get_reparse_tag`, `fsctl_set_reparse_point`, and `fsctl_del_reparse_point`. Internal helpers include `fsctl_get_reparse_point_reg` for stored `SAMBA_XATTR_REPARSE_ATTRIB` xattrs, `fsctl_get_reparse_point_int` for marshalling `struct reparse_data_buffer`, special-file helpers for FIFO/socket/block/char devices using `IO_REPARSE_TAG_NFS`, and `fsctl_get_reparse_point_lnk` for symlink reparse data via `parent_pathref` and `read_symlink_reparse`.

## Control Flow
Get starts by requiring `FILE_ATTRIBUTE_REPARSE_POINT` from `fdos_mode`, then dispatches on `st_ex_mode & S_IFMT`. Regular files read the reparse xattr; special Unix objects synthesize NFS reparse buffers; symlinks read link-specific reparse metadata. The result is validated with `reparse_buffer_check` before returning tag, bytes, and length. Set validates that the handle is a writable regular file, checks incoming reparse data, rejects tag replacement with a different existing tag, writes the xattr, and updates DOS attributes. Delete requires a writable handle, validates the existing tag and an empty-data delete buffer, removes the xattr, and clears the DOS reparse bit.

## State And Persistence
Regular-file reparse data is persisted in `SAMBA_XATTR_REPARSE_ATTRIB`. DOS attributes are updated through `SMB_VFS_FSET_DOS_ATTRIBUTES` and mirrored into `fsp->fsp_name->st.cached_dos_attributes`. Special-file get paths synthesize data from stat information and do not persist new state.

## Dependencies And Integration Points
The file depends on `libcli/smb/reparse.h`, `source3/smbd/proto.h`, VFS xattr and DOS attribute operations, stat data in `files_struct`, Unix major/minor helpers, symlink reparse helpers, talloc, and NTSTATUS/errno mapping. It is called by SMB FSCTL handling when clients query or manipulate reparse points.

## Risks
Set/delete access checks depend on `SEC_FILE_WRITE_DATA | SEC_FILE_WRITE_ATTRIBUTE` and `twrp`, so incorrect handle state can expose or reject operations. Tag mismatch handling must preserve Windows semantics. `fsctl_get_reparse_point_reg` bounds allocation to 64 KiB plus header and returns `BUFFER_TOO_SMALL` on `ERANGE`; callers must retry correctly. DOS attribute and xattr updates are not rolled back as a transaction if one succeeds and the other fails.

## Test Signals
Useful tests include regular-file set/get/delete, tag mismatch rejection, too-small output buffers, readonly handle denial, invalid reparse buffers, special FIFO/socket/device synthesis, symlink reparse reads, and DOS attribute cache updates after set/delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.h -->
# sources/user-network-fs/samba/source3/modules/util_reparse.h

## Purpose
This header declares the reparse-point FSCTL helper API implemented by `util_reparse.c`. It exposes a small boundary used by SMB server code and VFS modules without leaking implementation details about xattrs or special-file synthesis.

## Important APIs, Types, And Functions
The declared APIs are `fsctl_get_reparse_point`, `fsctl_get_reparse_tag`, `fsctl_set_reparse_point`, and `fsctl_del_reparse_point`. All operate on `struct files_struct *fsp`; get returns a tag, talloc-owned output bytes, and output length; set/delete consume raw reparse buffer bytes and lengths.

## Control Flow
The header itself has no runtime flow. It establishes the contract that callers pass a memory context for returned or temporary allocations and receive `NTSTATUS` results.

## State And Persistence
No state is stored in the header. The declared functions persist or remove reparse data through the implementation's xattr and DOS attribute paths.

## Dependencies And Integration Points
It relies on Samba core types such as `NTSTATUS`, `TALLOC_CTX`, and `files_struct` being visible to includers. It integrates the FSCTL dispatch layer with the reparse utility implementation.

## Risks
Callers must respect ownership of returned `uint8_t *` buffers and must pass correctly sized Windows reparse buffers to set/delete. The header does not document those ownership and validation constraints beyond the function signatures.

## Test Signals
Compile coverage through any user of the FSCTL helpers confirms declaration compatibility. Behavioral signals come from `util_reparse.c` tests or SMB FSCTL integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/util_reparse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.c -->
# sources/user-network-fs/samba/source3/modules/varlink_keybridge.c

## Purpose
This file implements a small client for Samba's container keybridge varlink protocol. It fetches configuration data, especially key material for encrypted CephFS shares, from a local varlink service so Samba does not need to know the service's remote-secret backend.

## Important APIs, Types, And Functions
The exported API is `varlink_keybridge_entry_get`. Internal helpers include `vlkb_kind_string`, `vlkb_error`, the varlink method callback `vlkb_get`, `vlkb_wait_for_response`, and `vlkb_entry_get`. The protocol uses method `org.samba.containers.keybridge.Get` and fields `name`, `scope`, `kind`, `entry`, `data`, with kind strings `B64` and `VALUE`.

## Control Flow
`varlink_keybridge_entry_get` delegates to `vlkb_entry_get`. That function builds a varlink object with requested name/scope/kind, opens a connection to `kbc->path`, allocates a talloc result, calls the `Get` method, then waits up to five seconds with `select` before processing events. The callback handles either a varlink error object or a successful `entry` object, extracts `kind` and `data`, fills `struct varlink_keybridge_result`, and closes the connection.

## State And Persistence
No durable state is stored. The only state is the transient varlink connection, request object, and talloc-owned result. Returned secret/config data is kept in `result->data` under the caller's memory context.

## Dependencies And Integration Points
The implementation depends on libvarlink, Samba debug/talloc infrastructure, and the public declarations in `varlink_keybridge.h`. It integrates share setup or filesystem-module code with a local secret provider over a Unix-socket-style varlink path.

## Risks
The five-second blocking `select` timeout is simple but can stall setup paths. On early setup failures before result allocation, `*resp` may remain untouched while the function returns false. Unknown kind strings default to `VALUE` behavior except explicit `B64`. Error responses include serialized JSON in the returned data string, which is useful diagnostically but may expose service-provided details in logs or callers.

## Test Signals
Useful tests include successful VALUE and B64 responses, server-side varlink errors, missing or malformed `entry`, `kind`, or `data` fields, connection failure, timeout, and talloc allocation failure handling. Integration tests need a local keybridge varlink service or mock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.h -->
# sources/user-network-fs/samba/source3/modules/varlink_keybridge.h

## Purpose
This header defines the public interface for the varlink keybridge client. It describes how Samba requests scoped configuration or key entries and how returned data is represented.

## Important APIs, Types, And Functions
`enum varlink_keybridge_kind` distinguishes default, base64 binary, and UTF-8/plain value data. `enum varlink_keybridge_status` distinguishes connection/protocol failure, successful result, and server-returned error. `struct varlink_keybridge_config` carries socket path, scope, entry name, and desired kind. `struct varlink_keybridge_result` carries status, actual kind, and result or error data. `varlink_keybridge_entry_get` performs the request and allocates a result from the supplied memory context.

## Control Flow
The header has no runtime flow, but its contract is request/response oriented: callers populate config, pass an output pointer, and inspect both the boolean return value and result status when populated.

## State And Persistence
The header stores no state. It documents talloc ownership of returned result data and leaves persistence to the external keybridge service.

## Dependencies And Integration Points
It requires Samba core types such as `TALLOC_CTX` and is included by consumers that need local secret/config lookup. Its comments explicitly connect the API to encrypted CephFS share setup and local varlink-mediated secret retrieval.

## Risks
The boolean return and `status` enum are distinct; callers must not assume a populated result on all false returns. The `char *` fields are mutable pointers, so callers should preserve storage for config values through the call.

## Test Signals
Compile-time coverage should confirm enum and struct use across consumers. Runtime validation belongs to `varlink_keybridge.c` tests with successful, error, and failed connection paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/varlink_keybridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_common.c

## Purpose
This file provides common logic for VFS modules that persist Windows NT security descriptors outside the native filesystem ACL path, primarily `acl_xattr` and `acl_tdb`. It serializes/deserializes NT ACL blobs, validates them against underlying filesystem ACL hashes, merges incoming partial security descriptor updates, and supplies shared delete/chmod behavior.

## Important APIs, Types, And Functions
Public functions are `init_acl_common_config`, `fget_nt_acl_common`, `fset_nt_acl_common`, `rmdir_acl_common`, `unlink_acl_common`, and `fchmod_acl_module_common`. Internal functions include `parse_acl_blob`, `create_acl_blob`, `create_sys_acl_blob`, `hash_blob_sha256`, `hash_sd_sha256`, `validate_nt_acl_blob`, `add_directory_inheritable_components`, `set_underlying_acl`, `store_v3_blob`, and `acl_common_remove_object`.

## Control Flow
`init_acl_common_config` reads module parameters `ignore system acls` and `default acl style` into handle data. Get flow fetches a backend blob, parses xattr NTACL versions 1-4, validates version 3/4 hashes unless system ACLs are ignored, falls back to the lower VFS NT ACL when needed, synthesizes default ACLs when ignoring system ACLs, adds inheritable directory components if the filesystem ACL lacks them, strips protected-DACL bits, and filters owner/group/DACL/SACL according to `security_info`. Set flow first fetches the current full descriptor, overlays incoming owner/group/DACL/SACL portions, rejects macOS MS-NFS chmod descriptors, marks the fsp extension as `setting_nt_acl`, optionally sets only ownership in the lower layer when system ACLs are ignored, otherwise sets the lower ACL, hashes the resulting lower NT ACL and optional sys-ACL blob, then stores a version 3 or 4 serialized descriptor via the backend callback.

## State And Persistence
Per-share config is stored on the VFS handle. A transient `acl_common_fsp_ext` flag prevents lower-layer POSIX ACL changes made during NT ACL setting from deleting the stored NT ACL. Durable persistence is delegated to backend callbacks; this file defines the NDR blob shape and SHA-256 hash validation. Delete helpers may temporarily become root to remove files opened with delete-on-close and `DELETE_ACCESS`.

## Dependencies And Integration Points
The file depends on Samba security descriptor/NDR code, `librpc/gen_ndr/ndr_xattr.h`, passdb SID lookup, gnutls SHA-256 hashing, VFS lower-layer ACL calls, xattr/sys-ACL blob hooks, talloc, loadparm, and SMB file-open tracking. It is the integration spine for `vfs_acl_tdb.c` and `vfs_acl_xattr.c`.

## Risks
Hash validation must stay compatible with older xattr versions while detecting underlying ACL drift. Version 3 validation only hashes the lower NT descriptor, while version 4 also hashes the system ACL blob when available. The root override path for owner changes and delete-on-close must preserve Windows semantics without granting arbitrary chown/delete. `ignore system acls` changes create masks and makes stored descriptors authoritative, so configuration mistakes can hide filesystem ACL changes.

## Test Signals
Important tests cover xattr/TDB get/set with versions 1-4, hash match/mismatch fallback, system ACL blob unavailable, `ignore system acls`, directory inheritable ACE synthesis, MS-NFS chmod ignore, owner take-over with `SEC_STD_WRITE_OWNER`, delete-on-close root override, and POSIX-open-only chmod pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.h -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_common.h

## Purpose
This header declares the shared contract used by Windows-ACL persistence modules such as `acl_xattr` and `acl_tdb`. It exposes common configuration, fsp extension state, and helper functions for get/set/delete/chmod behavior.

## Important APIs, Types, And Functions
`struct acl_common_config` holds `ignore_system_acls`, `default_acl_style`, and an optional `security_acl_xattr_name`. `struct acl_common_fsp_ext` carries the `setting_nt_acl` guard. Function declarations include `init_acl_common_config`, `rmdir_acl_common`, `unlink_acl_common`, `fchmod_acl_module_common`, `chmod_acl_acl_module_common`, `get_nt_acl_common_at`, `fget_nt_acl_common`, and `fset_nt_acl_common`. The get/set common functions are callback-driven so each backend supplies blob fetch/store functions.

## Control Flow
The header has no execution flow. Its function-pointer signatures define how backend modules hand storage operations to the common ACL engine while the common engine handles security descriptor merging and validation.

## State And Persistence
The structs define per-handle configuration and per-open-file transient state. Durable persistence is not specified here; it is supplied by backend modules through callbacks.

## Dependencies And Integration Points
The header includes `smbd/proto.h` and relies on Samba VFS, `files_struct`, `smb_filename`, `DATA_BLOB`, `security_descriptor`, and `NTSTATUS` types. It is included by ACL storage modules and any code sharing the common delete/chmod logic.

## Risks
The header declares `chmod_acl_acl_module_common` and `get_nt_acl_common_at`, but this source batch did not include implementations for them; consumers must only use APIs available in the linked build. Backend callbacks must obey ownership expectations for returned `DATA_BLOB` buffers.

## Test Signals
Compile/link tests of `acl_xattr` and `acl_tdb` validate this contract. Runtime signals come from backend get/set tests that exercise the callback signatures and `acl_common_fsp_ext` guard.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c

## Purpose
This VFS module stores Windows NT ACL blobs in Samba's state TDB `file_ntacls.tdb`, keyed by filesystem file id. It is one backend for `vfs_acl_common.c`, useful when NT ACLs should be preserved without relying on per-file xattrs.

## Important APIs, Types, And Functions
The module registers as `acl_tdb`. Key functions are `acl_tdb_init`, `disconnect_acl_tdb`, `acl_tdb_delete`, backend callbacks `fget_acl_blob` and `store_acl_blob_fsp`, `unlinkat_acl_tdb`, `connect_acl_tdb`, `sys_acl_set_fd_tdb`, `acl_tdb_fget_nt_acl`, and `acl_tdb_fset_nt_acl`. It uses static `ref_count` and `struct db_context *acl_db`.

## Control Flow
Connect calls the next VFS connect, opens the state database as root if needed, initializes common config, and forces share parameters such as `inherit acls`, `dos filemode`, and `force unknown acl user`. If `ignore system acls` is set, it also relaxes create/directory masks, disables DOS attribute mapping, and enables stored DOS attributes. Get/set delegate to `fget_nt_acl_common` and `fset_nt_acl_common` using TDB fetch/store callbacks. Unlink/rmdir go through common delete behavior, then delete the TDB record for non-stream objects. Direct lower POSIX ACL sets delete the stored NT ACL unless they are part of a guarded NT ACL set.

## State And Persistence
NT ACL blobs are persisted in `state_path("file_ntacls.tdb")`. Records use the backwards-compatible 16-byte dev/inode file id from `push_file_id_16`, which means data follows inode identity rather than path. The database is process-global with reference counting and closes when the last share disconnects.

## Dependencies And Integration Points
Dependencies include dbwrap/TDB, Samba state paths, VFS file-id helpers, common ACL helpers, auth/loadparm, and lower VFS ACL/unlink calls. It integrates with Samba's module stack through `vfs_fn_pointers` for connect, disconnect, unlinkat, fchmod, NT ACL get/set, and sys ACL set.

## Risks
Keying by dev/inode is compatible but can leave stale records after inode reuse if delete cleanup is missed. Named streams intentionally do not carry separate stored ACLs. Database open failures disable the module connect. Refcounting is static process state and must remain balanced across failed connect/disconnect paths.

## Test Signals
Tests should cover database creation, fetch/store by file id, delete-on-unlink/rmdir, named stream no-op cleanup, common ACL hash behavior through this backend, direct POSIX ACL set invalidating stored ACLs, and disconnect closing the TDB at refcount zero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c -->
# sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c

## Purpose
This VFS module stores Windows NT ACL blobs in file extended attributes. It is the xattr backend for `vfs_acl_common.c` and also hides or remaps a configured security ACL xattr name from normal client xattr operations.

## Important APIs, Types, And Functions
The module registers as `acl_xattr`. Backend helpers are `getxattr_do`, `fget_acl_blob`, `store_acl_blob_fsp`, and `sys_acl_set_fd_xattr`. VFS entry points include `connect_acl_xattr`, `acl_xattr_unlinkat`, `acl_xattr_fget_nt_acl`, `acl_xattr_fset_nt_acl`, async `acl_xattr_getxattrat_send/recv`, and fget/flist/fremove/fset xattr wrappers that protect or remap configured ACL xattr names.

## Control Flow
Connect initializes common config, forces Windows ACL-friendly share parameters, optionally adjusts masks and DOS attribute settings for `ignore system acls`, and reads `acl_xattr:security_acl_name`. ACL get reads `XATTR_NTACL_NAME` as root with a retry loop for `ERANGE` up to 65536 bytes, then delegates validation to common code. ACL set delegates descriptor merging and storage to common code, and storage writes the xattr as root. POSIX ACL changes remove the NTACL xattr unless guarded by an in-progress NT ACL set. Client xattr operations deny direct access to the configured hidden security xattr and optionally translate public `XATTR_NTACL_NAME` to the configured private name.

## State And Persistence
NT ACLs are persisted per file in `XATTR_NTACL_NAME` or a configured security ACL xattr name. Per-handle config stores xattr-name policy. There is no module-global database state.

## Dependencies And Integration Points
Dependencies include Samba VFS xattr operations, common ACL helpers, tevent async wrappers, loadparm, auth/root privilege helpers, and NTSTATUS/Unix error mapping. The module is stackable and forwards unlink/chmod and xattr operations to the next VFS layer after applying ACL-specific policy.

## Risks
The xattr get loop must avoid unbounded allocation and currently caps at 64 KiB. Hidden xattr remapping is easy to misconfigure; direct access to the real security xattr is denied to prevent clients from bypassing ACL semantics. Set xattr and DOS/common ACL changes are not a single filesystem transaction. Filesystems without xattr support will return mapped Unix errors.

## Test Signals
Key tests include ACL get/set round trips, `ERANGE` resize, missing xattr fallback to filesystem ACLs, configured `security_acl_name` remapping, denial of direct private xattr access, list filtering, POSIX ACL set invalidating stored NTACLs, and async getxattrat behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_acl_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_afsacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_afsacl.c

## Purpose
This VFS module converts between AFS ACL strings and Windows NT security descriptors. It lets Samba expose and set AFS directory ACLs through Windows ACL interfaces while preserving unmapped AFS principals where possible.

## Important APIs, Types, And Functions
Core types are `struct afs_ace`, `struct afs_acl`, and `struct afs_iob`. Helpers cover ACL allocation/freeing, parsing/unparsing AFS ACL text, ACE merge/clone, AFS-to-NT and NT-to-AFS rights conversion, file/dir ACL splitting and merging, SID/name mapping, AFS pioctl get/set, and unknown ACE preservation. VFS entry points are `afsacl_connect`, `afsacl_fget_nt_acl`, `afsacl_fset_nt_acl`, and `afsacl_sys_acl_blob_get_fd`.

## Control Flow
Connect calls the next VFS module and reads the `afsacl:space` replacement character. Get reads the AFS ACL with `afs_syscall(AFSCALL_PIOCTL, VIOCGETAL)`, parses positive/negative ACE lines, maps known AFS system names and PTS names to SIDs, converts rights into Windows ACE masks, and builds a security descriptor with owner/group from stat data. Set identifies the directory whose AFS ACL should be modified, reads the old ACL, splits it into directory and file rights, converts the incoming DACL into a new AFS dir or file ACL depending on object type and `afsacl:fileacls`, merges dir/file ACLs back together, preserves unknown old ACEs, unparses the ACL string, and writes it with `VIOCSETAL`.

## State And Persistence
AFS ACLs are durable state in the AFS filesystem and are accessed through pioctl syscalls. Module-global `space_replacement` and `sidpts` affect name parsing/mapping. Temporary ACL structures are talloc-managed within helper-owned contexts.

## Dependencies And Integration Points
The module depends on AFS headers/syscalls, Samba security/SID/passdb/name lookup, stat/VFS operations, loadparm, and the SMB VFS NT ACL hooks. It maps AFS special names such as `system:administrators`, `system:anyuser`, `system:authuser`, and `system:backup` to built-in or well-known SIDs.

## Risks
AFS ACLs have a different model from Windows ACLs; deny ACEs, inheritance, and file ACL behavior are approximated. `unparse_afs_acl` has a TODO about string length checks but uses bounded `strlcat` against `MAXSIZE`. Unknown principal preservation is best-effort. The `sidpts` mode changes whether PTS users/groups are represented as SIDs. `afsacl_sys_acl_blob_get_fd` returns `ENOSYS`, limiting hash validation integrations.

## Test Signals
Useful tests require an AFS environment: parse/unparse round trips, known system-name mapping, SID PTS mode, file versus directory ACL conversion, `afsacl:fileacls` modes `yes/no/ignore`, unknown ACE preservation, `VIOCGETAL`/`VIOCSETAL` failure handling, and Windows ACL get/set through SMB clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_afsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c

## Purpose
This VFS module simulates asynchronous pread, pwrite, and fsync by dispatching blocking I/O to forked helper children. It avoids in-process blocking while keeping per-request completion integrated with Samba's tevent async VFS interface.

## Important APIs, Types, And Functions
Important structures are `aio_fork_config`, `mmap_area`, `rw_cmd`, `rw_ret`, `aio_child`, and `aio_child_list`. Helpers include shared mmap setup/destruction, file-descriptor passing with `read_fd`/`write_fd`, child cleanup, child creation, idle-child selection, and the child loop. VFS async entry points are `aio_fork_pread_send/recv`, `aio_fork_pwrite_send/recv`, and `aio_fork_fsync_send/recv`, registered by `vfs_aio_fork_init`.

## Control Flow
Connect allocates per-handle config and reads `vfs_aio_fork:erratic_testing_mode`. On async I/O, the module obtains an idle child or forks a new one with a 128 KiB shared mmap area and a socketpair. The parent sends a command and file descriptor to the child. Reads write into shared memory and copy back on completion; writes copy user data into shared memory before dispatch. The parent waits asynchronously for an `rw_ret` packet with result, errno, and duration. Idle children are cleaned after two 30-second cleanup passes without activity.

## State And Persistence
Per-share state includes the child list and cleanup timer. Each child owns a process, socket fd, and shared mmap region. No durable state is persisted; the module only performs underlying file I/O. Child process lifetime is managed by talloc destructors and timed cleanup.

## Dependencies And Integration Points
The module depends on Unix fd passing via `sendmsg`/`recvmsg`, `mmap`, `fork`, Samba tevent, async socket helpers, sys read/write wrappers, profiling timestamps, and VFS async hooks. It closes inherited pathref fds in children to avoid holding system-level share modes.

## Risks
Requests larger than 128 KiB fail with `EINVAL`. Child death or malformed packets surface as async errors and may destroy the child. File descriptor passing support is required at compile time. Shared-memory copying means callers must respect async buffer lifetimes. Forked children inherit process state, so careful fd cleanup is needed to avoid share-mode side effects.

## Test Signals
Tests should exercise async read/write/fsync success, append write path, oversized request rejection, child reuse and cleanup, child failure recovery, errno propagation, duration reporting, and optional erratic delay mode. Integration tests should verify no share-mode leakage from inherited fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c

## Purpose
This VFS module provides thread-pool-backed asynchronous open support for selected create-exclusive opens. It is intentionally narrow: only `O_CREAT|O_EXCL` opens are offloaded, reducing latency for potentially slow creates while avoiding broader path-resolution races.

## Important APIs, Types, And Functions
When `HAVE_OPENAT` and `HAVE_LINUX_THREAD_CREDENTIALS` are available, the core type is `struct aio_open_private_data`, tracked in static `open_pd_list`. Helpers include `find_open_private_data_by_mid`, `aio_open_handle_completion`, `aio_open_worker`, `aio_open_do`, `opd_free`, `create_private_open_data`, `opd_inflight_destructor`, `open_async`, and `find_completed_open`. The registered VFS hook is `aio_pthread_openat_fn`.

## Control Flow
`aio_pthread_openat_fn` first rejects unsupported resolve flags, named streams, missing threadpool, SMB multichannel, pathref opens, non-create opens, non-exclusive creates, and `RESOLVE_NO_XDEV` cases needing retry through other open paths. If async open is disabled or ineligible, it calls `SMB_VFS_NEXT_OPENAT`. For eligible first-pass opens, it snapshots connection, names, credentials, dir fd, flags, mode, MID, and initial allocation size, then queues `aio_open_worker` on Samba's pthreadpool and returns `EINPROGRESS`. Completion clears the in-flight destructor, reschedules the deferred SMB open by MID, and stores the returned fd/errno. A later reentrant open for the same MID returns the completed fd.

## State And Persistence
Outstanding opens are stored in process memory in `open_pd_list` and allocated under the connection so teardown can mark abandoned work. No durable state is written. Worker threads set Linux thread credentials before `openat`; optional `fallocate` sets initial allocation size as an optimization.

## Dependencies And Integration Points
Dependencies include Samba pthreadpool/tevent integration, Linux thread credentials, `openat`, deferred SMB open scheduling, SMB MID tracking, `files_struct`/`smb_filename` copying, and loadparm option `aio_pthread:aio open`. It is registered as `aio_pthread`.

## Risks
The module is disabled for multichannel because MID-to-connection assumptions are not yet compatible. If a supposedly completed open is still in progress on reentry, the module panics, treating it as an open timeout. Connection teardown while a worker is in flight relies on a destructor that prevents freeing and later schedules an error response. Thread creation `EAGAIN` falls back to synchronous processing under restored user credentials.

## Test Signals
Useful tests include eligible `O_CREAT|O_EXCL` async opens, ineligible fallback paths, threadpool unavailable, connection teardown during in-flight open, worker credential failure, `EAGAIN` fallback, initial allocation-size optimization, and `RESOLVE_NO_XDEV` retry behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_pthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c

## Purpose
This stackable VFS module rate-limits asynchronous read and write operations with token buckets. It can enforce per-share IOPS and bandwidth ceilings, inject tevent delays before dispatching async I/O, and persist token state across reconnects/restarts in a local TDB.

## Important APIs, Types, And Functions
Important types are `struct ratelimit_tdb_record`, `struct ratelimiter`, `struct vfs_aio_ratelimit_config`, and `struct vfs_aio_ratelimit_state`. Key helpers include TDB version/init/load/save functions, `ratelimiter_init`, `ratelimiter_refill`, `ratelimiter_pre_io`, `ratelimiter_post_io`, config parsing helpers, connect/disconnect, and async pread/pwrite send/waited/done/recv functions.

## Control Flow
Connect opens `aio_ratelimit.tdb` if possible, then creates per-handle read/write ratelimiters from `aio_ratelimit:*` parameters. Before each async pread or pwrite, `ratelimiter_pre_io` refills tokens based on monotonic time, consumes one IOP token and requested byte tokens, computes the maximum deficit-derived delay, updates counters, and periodically saves state. If no delay is required, the request is passed immediately to the next VFS async operation. Otherwise a `tevent_wakeup_send` delay is scheduled, and the next VFS operation starts after the wakeup. Completion calls `ratelimiter_post_io` to credit unused byte tokens when short I/O occurs.

## State And Persistence
Per-connection ratelimiters hold token counters, capacities, totals, timestamps, burst multiplier, and share number. Process-global `ratelimit_tdb` is refcounted and stores records under `share/<servicename>/<read|write>` with schema version `RATELIMIT_TDB_VERSION`. TDB failure is non-fatal; limiting continues without persistence.

## Dependencies And Integration Points
The module depends on Samba tevent, VFS async pread/pwrite hooks, tdb, state paths, loadparm parsing including size strings, monotonic time helpers, and root privilege helpers for TDB open. It registers as `aio_ratelimit` and is meant to stack above an async I/O provider.

## Risks
Token fields are floats, so long-running precision and serialization stability matter. The TDB key is per share/service and operation, not per client, so limits are shared across connections to a share. Maximum injected delay is capped at 100 seconds. Refcount decrement assumes a successful init path; careful connect/disconnect pairing is needed. Delays are applied before the lower async I/O starts, so they rate-limit response flow but do not cancel queued requests.

## Test Signals
Tests should cover disabled limits, IOPS-only, bandwidth-only, combined limits, burst multiplier behavior, short I/O token refund, TDB version mismatch, persistence across reconnect, invalid bandwidth config strings, delay cap, read and write independent buckets, and stacking with an async backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_ratelimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl.c

## Purpose
This VFS module exposes classic AIX ACLs through Samba's POSIX ACL abstraction. It implements file-descriptor get/set hooks using AIX `fstatacl`, `fchacl`, and `chacl`, with conversion delegated to `vfs_aixacl_util.c`.

## Important APIs, Types, And Functions
The exported VFS helpers are `aixacl_sys_acl_get_fd`, `aixacl_sys_acl_set_fd`, and `aixacl_sys_acl_delete_def_fd`. The module registers `sys_acl_get_fd_fn`, `sys_acl_blob_get_fd_fn`, `sys_acl_set_fd_fn`, and `sys_acl_delete_def_fd_fn` under module name `aixacl`.

## Control Flow
Get rejects default ACL requests because classic AIX has no default ACL. It allocates an initial `BUFSIZ` `struct acl`, calls `fstatacl`, reallocates to `file_acl->acl_len + sizeof(struct acl)` on `ENOSPC`, then converts the AIX ACL to `SMB_ACL_T`. Set converts `SMB_ACL_T` to AIX ACL. For pathref fsp objects it calls path-based `chacl`; otherwise it calls `fchacl` on the I/O fd. Delete-default returns success so upper layers can proceed.

## State And Persistence
The module persists ACL changes directly to the AIX filesystem via `chacl`/`fchacl`. It has no module-private durable state.

## Dependencies And Integration Points
Dependencies include AIX ACL system calls and structures, Samba VFS/fsp helpers, `posix_sys_acl_blob_get_fd`, and conversion helpers from `vfs_aixacl_util.h`. It is a platform-specific adapter in Samba's VFS ACL stack.

## Risks
Default ACLs are unsupported but reported as successful for delete-default. The get path must correctly size variable-length AIX ACL structures after `ENOSPC`. The pathref set path is no longer handle-based and uses the base path, so path stability and symlink semantics depend on surrounding Samba pathref guarantees.

## Test Signals
Platform tests on AIX should cover access ACL get/set, `ENOSPC` resize, pathref and fd set paths, default ACL request rejection, delete-default success, and round-trip conversion through `aixacl_to_smbacl` and `aixacl_smb_to_aixacl`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.h -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl.h

## Purpose
This header declares the classic AIX ACL VFS helper functions implemented by `vfs_aixacl.c`. It allows related AIX ACL code to call or register the shared fd-based ACL operations.

## Important APIs, Types, And Functions
Declared functions are `aixacl_sys_acl_get_fd`, `aixacl_sys_acl_set_fd`, and `aixacl_sys_acl_delete_def_fd`. They use Samba `vfs_handle_struct`, `files_struct`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `TALLOC_CTX`.

## Control Flow
The header has no runtime control flow. It defines the signatures for get, set, and delete-default operations.

## State And Persistence
No state is defined here. Implementations persist ACL changes through AIX filesystem calls.

## Dependencies And Integration Points
It depends on Samba VFS and ACL types being visible to includers. It is part of the AIX-specific ACL integration boundary.

## Risks
The header intentionally exposes platform-specific functions; callers must compile only in builds with the corresponding AIX ACL support.

## Test Signals
Compile/link coverage in AIX builds validates the declarations. Runtime signals are supplied by `vfs_aixacl.c` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c

## Purpose
This VFS module supports AIX JFS2 ACLs, including NFSv4 ACLs and AIXC POSIX-like ACLs. It converts JFS2 NFSv4 ACL data to Samba's NFSv4 ACL abstraction for NT ACL operations and falls back to POSIX ACL paths where NFSv4 ACLs are unavailable.

## Important APIs, Types, And Functions
The file defines `AIXJFS2_ACL_T` as a union over `nfs4_acl_int_t` and `aixc_acl_t`. Important helpers are `aixacl2_getlen`, `aixjfs2_getacl_alloc`, `aixjfs2_get_nfs4_acl`, `aixjfs2_fget_nt_acl`, `aixjfs2_sys_acl_blob_get_fd`, `aixjfs2_get_posix_acl`, `aixjfs2_sys_acl_get_fd`, `aixjfs2_query_acl_support`, `aixjfs2_process_smbacl`, `aixjfs2_set_nt_acl_common`, `aixjfs2_fset_nt_acl`, `aixjfs2_sys_acl_set_fd`, and `aixjfs2_sys_acl_delete_def_fd`.

## Control Flow
ACL allocation starts with `aclx_get`, optionally querying type info with `GET_ACLINFO_ONLY`, then reallocates based on ACL length on `ENOSPC`. Get NT ACL attempts an NFSv4 JFS2 ACL read, converts each `nfs4_ace_int_t` into `SMB_ACE4PROP_T`, and calls `smb_fget_nt_acl_nfs4`; `ENOSYS` triggers fallback to `posix_fget_nt_acl`. Set NT ACL first queries whether `ACL_NFS4` is supported; if so, `smb_set_nt_acl_nfs4` calls back into `aixjfs2_process_smbacl`, which linearizes Samba NFSv4 ACEs into JFS2 `nfs4_acl_int_t` and writes them with `aclx_put`. Without NFSv4 support, it falls back to `set_nt_acl`. POSIX ACL get/set paths use AIXC ACL type and conversion helpers.

## State And Persistence
ACLs are persisted directly in the AIX JFS2 filesystem using `aclx_get`, `aclx_put`, and `aclx_fput`. The module has no private persistent database. Temporary ACL allocations are talloc-based.

## Dependencies And Integration Points
Dependencies include AIX JFS2 ACL APIs and types, Samba NFSv4 ACL conversion (`nfs4_acls.h`), POSIX ACL fallback helpers, AIX classic conversion helpers, and VFS stat wrappers `nfs4_acl_stat/fstat/lstat/fstatat`. It registers as `aixacl2`.

## Risks
The code stores numeric `who.id` values and does not serialize textual NFSv4 principals. `sys_acl_blob_get_fd` cannot linearize NFSv4 ACLs and returns `ENOSYS`, limiting common hash validation. Query failures are mapped from errno, while lack of NFSv4 support assumes POSIX fallback. Entry length alignment and ACL length calculations must match AIX kernel structure expectations.

## Test Signals
AIX JFS2 tests should cover NFSv4 ACL get/set, AIXC ACL get/set, fallback from `ENOSYS` to POSIX ACLs, `aclx_gettypes` support detection, pathref versus fd set paths, ACE count/entry length alignment, and NT ACL conversion through Samba's NFSv4 ACL helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c

## Purpose
This utility converts between AIX classic ACL structures and Samba's `SMB_ACL_T` representation. It is shared by the classic AIX ACL module and the JFS2/AIXC fallback paths.

## Important APIs, Types, And Functions
Exported functions are `aixacl_to_smbacl` and `aixacl_smb_to_aixacl`. Internal helper `aixacl_smb_to_aixperm` maps `SMB_ACL_READ`, `SMB_ACL_WRITE`, and `SMB_ACL_EXECUTE` to AIX `R_ACC`, `W_ACC`, and `X_ACC`.

## Control Flow
`aixacl_to_smbacl` initializes a Samba ACL, walks extended AIX ACL entries when `S_IXACL` is enabled, skips entries with unsupported multi-id forms, maps `ACEID_USER` and `ACEID_GROUP` to named user/group ACL entries, converts `ACC_PERMIT`/`ACC_SPECIFY` directly, approximates `ACC_DENY` by inverting low permission bits, then appends synthetic owner, group-object, and other entries from `u_access`, `g_access`, and `o_access`. `aixacl_smb_to_aixacl` allocates a variable-length AIX ACL, fills base owner/group/other permissions from object entries, skips masks, and appends named user/group `ACC_SPECIFY` entries with one `ace_id`.

## State And Persistence
The utility has no durable state. It allocates returned AIX ACLs with `SMB_MALLOC` for callers to free and returned Samba ACL entries under the provided talloc context.

## Dependencies And Integration Points
Dependencies include AIX `struct acl`, `struct acl_entry`, `struct ace_id` layout macros, Samba ACL compatibility types, talloc, and Samba allocation/debug helpers. It is used by `vfs_aixacl.c` and `vfs_aixacl2.c`.

## Risks
DENY ACLs are lossy because Samba's POSIX ACL abstraction cannot represent deny entries; the code inverts permissions to approximate a permit mask. Multi-identifier AIX entries are skipped. There is a suspicious check after `talloc_realloc` in the extended-entry loop that tests `result == NULL` rather than `result->acl == NULL`, which could miss allocation failure. Buffer growth for AIX ACL construction must keep `acl_len` and allocation size synchronized.

## Test Signals
Tests should round-trip base owner/group/other entries, named user/group entries, deny approximation, disabled `S_IXACL`, mask skipping, dynamic ACL buffer growth, unsupported multi-id entries, and allocation-failure paths where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h -->
# sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h

## Purpose
This header declares the AIX classic ACL conversion helpers shared by AIX-specific VFS modules.

## Important APIs, Types, And Functions
It declares `aixacl_to_smbacl(struct acl *file_acl, TALLOC_CTX *mem_ctx)` and `aixacl_smb_to_aixacl(SMB_ACL_TYPE_T acltype, SMB_ACL_T theacl)`.

## Control Flow
The header has no runtime flow. It establishes the conversion API between platform ACL structures and Samba ACL structures.

## State And Persistence
No state is stored in the header. Implementations allocate converted ACLs and callers persist them through AIX ACL system calls.

## Dependencies And Integration Points
It depends on AIX `struct acl` and Samba ACL/talloc types being visible. It is included by `vfs_aixacl.c` and `vfs_aixacl2.c`.

## Risks
The header lacks include guards in the displayed source, so repeated inclusion depends on compiler tolerance and surrounding includes. It should only be used in AIX ACL builds where `struct acl` is defined.

## Test Signals
Compile/link tests in AIX builds confirm declaration compatibility. Behavioral testing belongs to `vfs_aixacl_util.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aixacl_util.h -->
