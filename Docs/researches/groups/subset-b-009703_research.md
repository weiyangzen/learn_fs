<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c

## Purpose
Implements the NFSv3 `NFSPROC3_FSSTAT` handler. It translates a client file handle into an FSAL object, asks the FSAL/export for dynamic filesystem statistics, and returns NFSv3 filesystem byte/file counters plus post-operation attributes.

## APIs, Types, and Functions
The exported entry points are `nfs3_fsstat()` and `nfs3_fsstat_free()`. Important types are `fsal_dynamicfsinfo_t`, `fsal_status_t`, `struct fsal_obj_handle`, `FSSTAT3resok`, and `FSSTAT3resfail`. Core helper dependencies are `nfs3_FhandleToCache()`, `fsal_statfs()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, `nfs_RetryableError()`, and object `put_ref`.

## Control Flow, State, and Persistence
The handler initializes failure post-op attributes to not-follow, logs the request, resolves the root file handle, calls `fsal_statfs()`, and maps retryable FSAL errors to `NFS_REQ_DROP` while stable failures become NFSv3 status codes. On success it copies `total_bytes`, `free_bytes`, `avail_bytes`, `total_files`, `free_files`, and `avail_files`, sets `invarsec` to zero to advertise volatile filesystem statistics, and returns `NFS3_OK`. State is request-local except for references acquired from the object cache and export context; no persistent metadata is changed.

## Dependencies and Integration
Integrated through the NFSv3 dispatch table and the shared protocol conversion/cache helpers. It depends on the current `op_ctx` populated by file-handle resolution, FSAL statfs support for the backing export, NFSv3 XDR result structs, logging, and attribute conversion helpers.

## Risks and Test Signals
Risks include stale or missing post-op attributes on error, incorrect retry/drop classification, FSALs returning dynamic counters in units not expected by NFSv3 clients, and `invarsec = 0` forcing clients to treat stats as volatile. Test signals are `FSSTAT` against valid and stale handles, retryable FSAL fault injection, statfs values matching backend capacity, and reference leak checks around object cache lookup failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_fsstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c

## Purpose
Implements NFSv3 `GETATTR`, returning the full NFSv3 attribute set for a file handle by delegating to the FSAL object's `getattrs` operation.

## APIs, Types, and Functions
The file exports `nfs3_getattr()` and `nfs3_getattr_free()`. It works with `nfs_arg_t`, `nfs_res_t`, `struct fsal_attrlist`, and `struct fsal_obj_handle`. Important helpers are `fsal_prepare_attrs(ATTRS_NFS3)`, `nfs3_FhandleToCache()`, `obj->obj_ops->getattrs()`, `fsal_release_attrs()`, `nfs3_Errno_status()`, and `nfs_RetryableError()`.

## Control Flow, State, and Persistence
The handler prepares the response attribute list, resolves the input file handle, calls `getattrs`, maps errors, and sets `NFS3_OK` when attributes are available. Retryable backend failures drop the RPC for client retry; nonretryable failures are encoded in the protocol status. All state is transient: prepared attributes are released and the object reference is returned in all paths.

## Dependencies and Integration
This is a simple bridge between the NFSv3 dispatch layer and the FSAL/mdcache attribute path. It relies on `ATTRS_NFS3` selecting the correct protocol-visible attribute mask and on the XDR layer using the populated `GETATTR3res_u.resok.obj_attributes` directly.

## Risks and Test Signals
Risks include missing `fsal_release_attrs()` for attributes containing ACL or inherited data, stale cache attributes from FSAL implementations, and ambiguity between dropped retryable requests and protocol error returns. Test signals are attribute parity with backend stat data, stale/bad handle behavior, retryable error injection, and leak checks on repeated `GETATTR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_getattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c

## Purpose
Implements NFSv3 `LINK`, creating a hard link to an existing object in a target directory while returning weak cache consistency data for the destination directory and attributes for the linked object.

## APIs, Types, and Functions
The main functions are `nfs3_link()`, `nfs3_link_free()`, and the internal `nfs3_verify_exportid()`. It uses `LINK3args`, `LINK3res`, `fsal_attrlist`, `pre_op_attr`, `nfs3_FhandleToExportId()`, `nfs3_FhandleToCache()`, `fsal_link()`, `nfs_SetPostOpAttr()`, `nfs_SetWccData()`, and `nfs_PreOpAttrFromFsalAttr()`.

## Control Flow, State, and Persistence
Before object lookup, `nfs3_verify_exportid()` rejects malformed handles and cross-export hard links with `NFS3ERR_BADHANDLE` or `NFS3ERR_XDEV`. The handler resolves the destination directory and source object, captures destination pre-change attributes, validates directory type and link name, then calls `fsal_link()` with pre/post directory attribute outputs. Success returns target object post-op attributes and destination WCC; failure maps FSAL status and still attempts to fill target attributes and WCC. Object references and prepared attributes are always released.

## Dependencies and Integration
The handler depends on export IDs encoded in NFSv3 file handles, FSAL hard-link support, object-cache reference handling, and NFSv3 WCC helpers. It integrates with export isolation policy by refusing links across exports before the FSAL call.

## Risks and Test Signals
Risks include export-id parsing mismatches with file-handle formats, link-count or parent WCC races if FSAL pre/post attributes are incomplete, and backends that do not support hard links. Test signals are same-export hard-link creation, cross-export `XDEV`, empty-name `INVAL`, non-directory target parent `NOTDIR`, backend `EOPNOTSUPP` mapping, and reference leak tests on early source-handle failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c

## Purpose
Implements NFSv3 `LOOKUP`, resolving a name within a directory file handle and returning the child file handle plus child and parent post-operation attributes.

## APIs, Types, and Functions
Exports `nfs3_lookup()` and `nfs3_lookup_free()`. It uses `LOOKUP3args`, `LOOKUP3resok`, `LOOKUP3resfail`, `struct fsal_attrlist`, `fsal_lookup()`, `nfs3_FhandleToCache()`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, and `gsh_free()` for the dynamically allocated file-handle buffer.

## Control Flow, State, and Persistence
The handler prepares optional NFSv3 attributes with `ATTR_RDATTR_ERR`, initializes failure directory attributes to absent, resolves the directory handle, and calls `fsal_lookup()`. On lookup failure it maps status and returns directory attributes when possible. On success it builds an NFSv3 file handle for the child, fills child and directory attributes, and returns `NFS3_OK`; if file-handle construction fails, it reports `NFS3ERR_BADHANDLE`. The only persistent effect is cache lookup/reference activity; it does not mutate filesystem state.

## Dependencies and Integration
This is a core NFSv3 namespace operation and depends on the FSAL lookup path, export file-handle encoding, and attribute conversion. It integrates with the XDR free path through `nfs3_lookup_free()`, which releases the allocated handle only on successful lookup.

## Risks and Test Signals
Risks include leaked handle buffers if success status and allocation state diverge, ambiguous behavior for invalid names delegated to FSAL, and parent post-op attributes not representing the lookup instant. Test signals are successful lookup for files/directories/symlinks, nonexistent names, bad parent handles, file-handle encoding failure injection, and memory checks across repeated lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c

## Purpose
Implements NFSv3 `MKDIR`, creating a directory under a parent directory handle and returning the new object's optional file handle, attributes, and parent weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_mkdir()` and `nfs3_mkdir_free()`. It uses `MKDIR3args`, `MKDIR3resok`, `MKDIR3resfail`, `fsal_attrlist`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, `op_ctx->fsal_export->exp_ops.check_quota()`, `fsal_create()`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler prepares attributes for the new directory and parent WCC, resolves the parent handle, validates that the parent is a directory, checks inode quota, validates name and sattr conversion, applies credential squashing, and ensures a mode is present. It calls `fsal_create()` with type `DIRECTORY`, releases requested attributes, builds a post-op file handle, fills new-object attributes and parent WCC, and returns `NFS3_OK`. On failure it maps FSAL status and returns parent WCC if available.

## Dependencies and Integration
Integrated with export quota policy, credential squashing, FSAL create semantics, NFSv3 file-handle encoding, and mdcache reference lifetimes. Parent pre/post attributes are requested from the FSAL create call to satisfy NFSv3 WCC rules.

## Risks and Test Signals
Risks include defaulting missing mode to zero, quota checks happening before full name/attribute validation, inherited ACL or sattr release correctness, and file-handle allocation cleanup. Test signals are normal mkdir, empty name, non-directory parent, quota denial, invalid sattr, handle-encoding failure, parent WCC correctness, and `nfs3_mkdir_free()` freeing only successful returned handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c

## Purpose
Implements NFSv3 `MKNOD`, creating special non-regular filesystem objects such as character devices, block devices, sockets, and FIFOs.

## APIs, Types, and Functions
The exported functions are `nfs3_mknod()` and `nfs3_mknod_free()`. It consumes `MKNOD3args`, maps NFSv3 node types to `object_file_type_t`, converts attributes through `nfs3_Sattr_To_FSALattr()`, sets `ATTR_RAWDEV` for device numbers, checks inode quota, uses `fsal_create()`, builds NFSv3 file handles with `nfs3_FSALToFhandle()`, and returns WCC via `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves and validates the parent directory, validates the object name, decodes the requested node type and type-specific attributes, rejects unsupported/bad types, checks quota, applies `squash_setattr()`, supplies a default mode if missing, and creates the object. Success returns a new post-op handle, attributes, and parent WCC. Failure maps FSAL status and returns parent WCC when possible. Persistent filesystem state changes only through `fsal_create()`.

## Dependencies and Integration
Depends on FSAL support for special-file creation and export file-handle generation. It integrates with export quota policy and NFSv3 WCC requirements similarly to `MKDIR`/`SYMLINK`, but with type-specific raw-device handling.

## Risks and Test Signals
Risks include rejecting or mishandling unimplemented NFSv3 type variants, raw device major/minor conversion errors, backend-specific permission constraints for device nodes, and leaked handles on partial success. Test signals are FIFO/socket/char/block creation, invalid type handling, quota denial, non-directory parent, default mode behavior, handle freeing on success, and WCC before/after changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c

## Purpose
Implements NFSv3 `PATHCONF`, returning path configuration limits and booleans for the export containing the requested object.

## APIs, Types, and Functions
Exports `nfs3_pathconf()` and `nfs3_pathconf_free()`. It uses `PATHCONF3resok`, `struct fsal_export`, `op_ctx->fsal_export`, `nfs3_FhandleToCache()`, `nfs_SetPostOpAttr()`, and export attributes such as `maxread`, `maxwrite`, and hard-coded POSIX/NFS path configuration fields.

## Control Flow, State, and Persistence
The handler initializes failure object attributes to absent, resolves the object handle, then fills pathconf fields. It reports `linkmax` as `LINK_MAX`, `name_max` from `exp_hdl->exp_ops.fs_maxnamelen()`, `no_trunc = TRUE`, `chown_restricted = TRUE`, `case_insensitive = FALSE`, and `case_preserving = TRUE`. It includes post-op attributes and returns `NFS3_OK`. No persistent state changes occur.

## Dependencies and Integration
This operation depends on the active FSAL export selected during file-handle resolution and its `fs_maxnamelen` operation. It is integrated into the NFSv3 protocol surface as an export-level capability query rather than an object mutator.

## Risks and Test Signals
Risks include hard-coded case-sensitivity and chown semantics being wrong for unusual FSALs, name length changing by path or backend, and failure attributes being absent after handle errors. Test signals are PATHCONF on supported exports, backend-specific max name length checks, bad handle behavior, and clients relying on case or truncation fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_pathconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c

## Purpose
Implements NFSv3 `READ`, including synchronous and resumable asynchronous FSAL reads, export read limits, EOF compatibility handling, response data lifetime, and server I/O statistics.

## APIs, Types, and Functions
Key functions are `nfs3_read()`, `nfs3_complete_read()`, `nfs3_read_cb()`, `nfs3_read_resume()`, `nfs_read_ok()`, `read3_io_data_release()`, and `nfs3_read_free()`. It uses `struct nfs3_read_data`, `struct fsal_io_arg`, `fsal_read2()`, `obj->obj_ops->read2()`, `svc_resume()`, `resume_op_context()`, `server_stats_io_done()`, `gsh_calloc()`, and `nfs_SetPostOpAttr()`.

## Control Flow, State, and Persistence
The handler resolves the file handle, captures pre-op attributes, checks read access, rejects directories and non-regular/non-symlink reads, enforces `MaxRead` and `MaxOffsetRead`, handles zero-length reads locally, allocates an async data wrapper, and starts `fsal_read2()`. If the FSAL completes inline, `nfs3_complete_read()` sets `count`, `data`, `eof`, and attributes; if the FSAL returns async or resumable state, the request is suspended and later resumed via `rq_resume_cb`. For non-compliant EOF FSALs, completion may fetch file size to correct EOF at exact end. Persistent filesystem state is unchanged, but request state and object references persist while suspended.

## Dependencies and Integration
Depends on export options, FSAL read2 async contract, RPC suspend/resume infrastructure, op-context save/restore, XDR release callbacks for read buffers, and server statistics accounting. The file integrates tightly with `sal_functions.h` and object reference management.

## Risks and Test Signals
Risks include object or `read_data` lifetime bugs across async resume, incorrect EOF for FSALs without compliant EOF behavior, max-offset overflow checks, read buffer release ownership, and double statistics accounting on suspended paths. Test signals are zero-byte reads, reads past EOF, max read and max offset rejection, directory read `ISDIR`, async FSAL completion/resume, retryable errors, data buffer release, and stats counters for success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c

## Purpose
Implements NFSv3 `READDIR`, producing an encoded directory entry stream with cookie verifier handling, synthetic `.` and `..` entries, FSAL directory iteration, and bounded XDR response construction.

## APIs, Types, and Functions
The important functions are `nfs3_readdir()`, `nfs3_readdir_callback()`, `nfs_readdir_dot_entry()`, and `nfs3_readdir_free()`. It uses `struct nfs3_readdir_cb_data`, `fsal_readdir()`, `fsal_lookupp()`, `xdr_encode_entry3()`, `xdrmem_create()`, `nfs_SetPostOpAttr()`, `op_ctx_export_has_option(EXPORT_OPTION_USE_COOKIE_VERIFIER)`, and `gsh_calloc()/gsh_free()`.

## Control Flow, State, and Persistence
The handler validates the directory handle, obtains directory attributes, optionally builds a cookie verifier from the directory change attribute, and validates client verifiers for nonzero cookies. It converts NFS cookies 1 and 2 into synthetic `.` and `..` responses and uses FSAL cookie 0 for real iteration when needed. The callback encodes each entry into an XDR memory buffer, checks client count and server memory limits, rewinds the XDR stream if an entry does not fit, and marks EOF only when FSAL reports end-of-directory. No filesystem state changes occur; encoded response memory is request-owned.

## Dependencies and Integration
Depends on FSAL directory enumeration semantics, NFSv3 cookie verifier export option, XDR helpers, and directory attribute `change` support. It integrates with client pagination through cookies and with the XDR response path through an `xdr_uio` buffer.

## Risks and Test Signals
Risks include cookie verifier mismatch with FSAL change support, off-by-one handling around synthetic cookies, XDR rewind correctness when entries do not fit, count limits producing `TOOSMALL` or partial replies, and memory lifetime for encoded buffers. Test signals are first-page `.`/`..`, continuation cookies, bad cookie verifier, tiny count, directory mutation between calls, no-more-entries EOF, and XDR encode failure injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c

## Purpose
Implements NFSv3 `READDIRPLUS`, extending `READDIR` by encoding attributes and file handles for each returned entry while respecting both `dircount` and `maxcount`.

## APIs, Types, and Functions
Exports `nfs3_readdirplus()`, `nfs3_readdirplus_callback()`, and `nfs3_readdirplus_free()`. It uses `struct nfs3_readdirplus_cb_data`, `fsal_readdir()`, `fsal_lookupp()`, `nfs3_FSALToFhandle()`, `xdr_encode_entryplus3()`, `xdrmem_create()`, `nfs_SetPostOpAttr()`, `EXPORT_OPTION_NO_READDIR_PLUS`, `EXPORT_OPTION_USE_COOKIE_VERIFIER`, and attribute masks `ATTRS_NFS3 | ATTR_RDATTR_ERR`.

## Control Flow, State, and Persistence
The handler rejects exports configured with no READDIRPLUS, calculates response overhead, caps memory by export `MaxRead`, validates directory type and attributes, builds/checks cookie verifier, emits synthetic `.` and `..` entries with handles/attributes, and then calls `fsal_readdir()` with a callback. The callback builds `entryplus3`, encodes the name, cookie, attributes, and post-op file handle, tracks RFC `dircount` contribution, rewinds the XDR stream if the next entry cannot fit, and frees any temporary handle allocation. Success attaches encoded data as an `xdr_uio` response and returns directory attributes and EOF state.

## Dependencies and Integration
Depends on FSAL support for per-entry object handles and attributes, NFS file-handle encoding, export limits/options, and special XDR entryplus encoders. It is a high-cost integration point between namespace traversal, attribute lookup, and handle serialization.

## Risks and Test Signals
Risks include overlarge responses from handle/attribute expansion, handle allocation leaks inside the callback, cookie verifier dependence on directory change, optional disabling via export config, and mismatches between `dircount` and `maxcount`. Test signals are normal pagination, tiny `dircount` or `maxcount`, `NO_READDIR_PLUS` exports, synthetic dot entries, handle-encoding failure, mutation causing bad cookie, and memory/XDR leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readdirplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c

## Purpose
Implements NFSv3 `READLINK`, returning the contents of a symbolic link and post-operation attributes for the link object.

## APIs, Types, and Functions
Exports `nfs3_readlink()` and `nfs3_readlink_free()`. It uses `READLINK3resok`, `READLINK3resfail`, `struct fsal_obj_handle`, `nfs3_FhandleToCache()`, `fsal_readlink()`, `nfs_SetPostOpAttr()`, `nfs3_Errno_status()`, and `gsh_free()` for the returned path buffer.

## Control Flow, State, and Persistence
The handler resolves the file handle, initializes failure attributes as absent, verifies the object is a symbolic link through FSAL behavior, calls `fsal_readlink()`, maps errors with retry/drop handling, and on success returns a dynamically allocated path string plus link attributes. It releases the object reference and frees the path only in `nfs3_readlink_free()` when status is `NFS3_OK`.

## Dependencies and Integration
Depends on FSAL symlink content retrieval and NFSv3 XDR ownership of the returned string. It integrates with attribute reporting and common retryable error policy.

## Risks and Test Signals
Risks include path buffer ownership mismatches, backend readlink size limits, non-symlink error mapping, and absent attributes on failure. Test signals are valid symlink reads, non-symlink handles, broken/stale handles, retryable backend errors, long symlink targets, and memory leak checks for successful response cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c

## Purpose
Implements NFSv3 `REMOVE`, deleting a non-directory name from a parent directory and returning parent weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_remove()` and `nfs3_remove_free()`. It uses `REMOVE3args`, `REMOVE3resok`, `REMOVE3resfail`, `fsal_lookup()`, `fsal_remove()`, `nfs3_FhandleToCache()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, `nfs_PreOpAttrFromFsalAttr()`, and FSAL attribute lists for parent pre/post state.

## Control Flow, State, and Persistence
The handler resolves the parent directory, captures pre-op attributes, validates directory type and non-empty name, optionally looks up the child to reject directories with `NFS3ERR_ISDIR`, then calls `fsal_remove()`. Success returns WCC from FSAL-provided parent pre/post attributes; failure maps FSAL status and returns failure WCC. The persistent effect is deletion through the FSAL when the remove succeeds.

## Dependencies and Integration
Integrated with FSAL namespace mutation, mdcache object references, and NFSv3 WCC. It relies on a pre-delete child lookup for protocol-specific directory rejection but still delegates final remove races to FSAL.

## Risks and Test Signals
Risks include lookup/remove races where a child changes type between validation and deletion, incomplete WCC if FSAL lacks pre/post attributes, and retryable error handling after partial backend mutation. Test signals are file removal, directory removal rejection, nonexistent name, empty name, non-directory parent, concurrent rename/remove races, and WCC validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c

## Purpose
Implements NFSv3 `RENAME`, moving or replacing an entry between two parent directories while enforcing export boundaries and returning WCC for both source and destination directories.

## APIs, Types, and Functions
Exports `nfs3_rename()` and `nfs3_rename_free()`. It uses `RENAME3args`, `RENAME3resok`, `RENAME3resfail`, `nfs3_FhandleToExportId()`, `nfs3_FhandleToCache()`, `fsal_rename()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, `nfs_PreOpAttrFromFsalAttr()`, and FSAL pre/post attribute lists for both directories.

## Control Flow, State, and Persistence
The handler rejects malformed or cross-export source/destination handles, resolves both parent directories, captures pre-op attributes, validates directory types and non-empty source/destination names, and invokes `fsal_rename()` with source and destination parent pre/post attributes. Success returns WCC for both directories; failure maps the FSAL status and still attempts to return WCC. Persistent state changes are entirely in the FSAL rename.

## Dependencies and Integration
Depends on export ID encoding in NFSv3 handles, FSAL atomic rename semantics, object reference management, and WCC helpers. It integrates with client-cache correctness by reporting both old and new directory changes.

## Risks and Test Signals
Risks include cross-export enforcement differing from backend mount boundaries, rename races with directory replacement rules, partial or non-atomic backend rename behavior, and WCC accuracy when source and destination directories are the same object. Test signals are same-directory rename, cross-directory rename, cross-export `XDEV`, empty names, non-directory parents, replacement cases, and same-parent WCC consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c

## Purpose
Implements NFSv3 `RMDIR`, removing a directory entry after verifying the parent is a directory and the named child is itself a directory.

## APIs, Types, and Functions
Exports `nfs3_rmdir()` and `nfs3_rmdir_free()`. It uses `RMDIR3args`, `RMDIR3resok`, `RMDIR3resfail`, `nfs3_FhandleToCache()`, `fsal_lookup()`, `fsal_remove()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, and parent pre/post `fsal_attrlist` values.

## Control Flow, State, and Persistence
The handler resolves the parent, captures pre-op attributes, validates parent type and non-empty name, looks up the child to ensure it is a directory, and calls `fsal_remove()` to remove it. Success returns parent WCC and `NFS3_OK`; failure maps FSAL status and returns failure WCC if possible. The only persistent mutation is the FSAL remove.

## Dependencies and Integration
Integrated with FSAL lookup/remove, object cache references, and NFSv3 WCC. It mirrors `REMOVE` with inverted type validation and relies on backend semantics for non-empty directory errors.

## Risks and Test Signals
Risks include child type races between lookup and remove, backend error mapping for non-empty directories, incomplete WCC, and retry/drop behavior after ambiguous backend failures. Test signals are empty directory removal, non-empty directory error, file removal rejected as `NOTDIR`, empty name, non-directory parent, and concurrent mutation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_rmdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c

## Purpose
Implements NFSv3 `SETATTR`, applying client-provided size/mode/owner/time updates with optional guarded ctime checking and returning object weak cache consistency data.

## APIs, Types, and Functions
Exports `nfs3_setattr()` and `nfs3_setattr_free()`. It uses `SETATTR3args`, `sattr3`, `guard3`, `fsal_attrlist`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, `fsal_setattr()`, `state_deleg_conflict()`, `nfs_SetPreOpAttr()`, `nfs_SetWccData()`, and `sal_functions.h`.

## Control Flow, State, and Persistence
The handler resolves the object, captures pre-op attributes, optionally compares the guard ctime with current attributes and returns `NFS3ERR_NOT_SYNC` on mismatch, converts NFSv3 attributes to FSAL attributes, applies credential squashing when owner/group are set, checks for delegation conflict before mutating, and calls `fsal_setattr()`. Success and stable failures both return WCC based on pre and current post attributes; retryable errors are dropped. Persistent metadata changes occur through FSAL setattr, including possible truncation.

## Dependencies and Integration
Depends on attribute conversion policy, delegation conflict detection, export/user credential squashing, FSAL setattr semantics, and NFSv3 WCC. It integrates with state management by refusing changes while conflicting delegations exist.

## Risks and Test Signals
Risks include guard timestamp precision mismatches, owner/group squashing surprises, delegation conflict returning `JUKEBOX`, truncation/state interactions, and failure WCC accuracy. Test signals are guarded and unguarded mode/size/time changes, stale guard rejection, delegation conflict, invalid sattr conversion, retryable FSAL failures, and WCC before/after verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_setattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c

## Purpose
Implements NFSv3 `SYMLINK`, creating a symbolic link with client-supplied target data and returning optional handle, attributes, and parent WCC.

## APIs, Types, and Functions
Exports `nfs3_symlink()` and `nfs3_symlink_free()`. It uses `SYMLINK3args`, `SYMLINK3resok`, `SYMLINK3resfail`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, export inode quota checking, `fsal_create()` with type `SYMBOLIC_LINK`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves the parent, captures pre-op attributes, validates parent directory type, checks inode quota, validates link name and non-empty target, converts and squashes attributes, ensures a mode is present, and calls `fsal_create()` with the link target string. Success returns a post-op handle, object attributes, and parent WCC; failure maps FSAL status and returns parent WCC where available. Persistent state is the newly created symlink.

## Dependencies and Integration
Depends on FSAL symlink creation support, quota policy, credential squashing, file-handle encoding, and XDR cleanup of dynamically allocated handles. It follows the same create/WCC pattern as `MKDIR` and `MKNOD`.

## Risks and Test Signals
Risks include validating target content too strictly or too loosely relative to NFSv3 expectations, default mode behavior, quota ordering, handle leaks, and backend symlink length limits. Test signals are normal symlink creation, empty name or target, non-directory parent, quota denial, handle-encoding failure, long target handling, and WCC/attribute correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c

## Purpose
Implements NFSv3 `WRITE`, including export limits, stable/unstable write policy, quota checks, asynchronous FSAL write completion, WCC generation, write verifiers, and server I/O accounting.

## APIs, Types, and Functions
Key functions are `nfs3_write()`, `nfs3_complete_write()`, `nfs3_write_cb()`, `nfs3_write_resume()`, and `nfs3_write_free()`. It uses `struct nfs3_write_data`, `struct fsal_io_arg`, `obj->obj_ops->write2()`, `svc_resume()`, `resume_op_context()`, `server_stats_io_done()`, `NFS3_write_verifier`, `op_ctx->export_perms.options & EXPORT_OPTION_COMMIT`, `MaxWrite`, `MaxOffsetWrite`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves the object, captures pre-op attributes, checks write access, rejects directories/non-regular objects, checks inode quota, validates count and max-offset limits, handles zero-length writes locally, allocates an async write wrapper, sets `fsal_stable` based on client stable mode or forced export commit, and calls `write2()`. Completion maps FSAL status, returns count, committed mode, verifier, and WCC, releases the object, frees wrapper state, and records I/O stats. Suspended FSAL operations persist request state until callback/resume.

## Dependencies and Integration
Depends on FSAL async write2 contract, export commit and write size configuration, quota checks, RPC suspend/resume, op-context restore, and global NFSv3 write verifier state. It is a major integration point for writeback semantics and statistics.

## Risks and Test Signals
Risks include stable write mode mismatches, quota type using inode quota for data writes, max-offset overflow, WCC after partial writes, async lifetime/double-free bugs, and stats accounting differences between inline and suspended writes. Test signals are unstable/data-sync/file-sync writes, forced commit exports, zero-byte writes, `FBIG` limits, async callback/resume, partial writes, verifier consistency across reboot policy, and WCC validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c

## Purpose
Implements the NFSv4 `COMPOUND` procedure dispatcher and lifecycle manager. It validates minor versions and compound shape, dispatches per-op handlers, accounts response sizes/statistics/QoS, handles async resume, maintains NFSv4.1 session replay caching, and frees/copies compound results.

## APIs, Types, and Functions
Major entry points are `nfs4_Compound()`, `process_one_op()`, `complete_op()`, `complete_nfs4_compound()`, `nfs4_compound_resume()`, `nfs4_Compound_FreeOne()`, `release_nfs4_res_compound()`, `nfs4_Compound_Free()`, `compound_data_Free()`, `nfs4_Compound_CopyResOne()`, `xdr_COMPOUND4res_extended()`, and optional `nfs4_qos_compound_cb()`. The central table is `optabv4[]`, mapping opcodes to names, handlers, resume callbacks, free callbacks, response sizes, and required export permission flags.

## Control Flow, State, and Persistence
`nfs4_Compound()` allocates `COMPOUND4res_extended` and `compound_data_t`, validates minor version enablement and RDMA support, copies/validates the tag, extracts client credentials, allocates the response op array, enforces v4.1 first-op/session rules, installs `rq_resume_cb`, and iterates operations. `process_one_op()` enforces position rules for `SEQUENCE`, `BIND_CONN_TO_SESSION`, and `DESTROY_SESSION`, export permission flags, per-session max operations, response room limits, QoS suspension, and handler dispatch. `complete_op()` reads the first status field from the result union, updates response size and per-op stats, and stops the compound on error. Completion caches full or uncached v4.1 slot replies, updates leases, and releases preserved client IDs. `compound_data_Free()` releases current/saved objects, session slots, exports, pNFS DS refs, and file-handle buffers. Persistent state includes slot replay cache entries, lease renewal side effects, and session slot last-request metadata.

## Dependencies and Integration
This file integrates nearly every NFSv4 subsystem: FSAL handles, SAL state/session/clientid management, exports, pNFS, QoS, server stats, LTTng tracing, XDR, and all individual `nfs4_op_*` implementations. It is the authoritative opcode dispatch and cleanup contract for dynamic result memory.

## Risks and Test Signals
Risks include stale `optabv4` metadata, shallow replay-cache copies of results with dynamic memory, response-size underestimation, async resume touching already-resumed requests, slot lock/refcount leaks, incorrect v4.1 compound-shape errors, and missing deep-copy/free support for newer operations. Test signals are pynfs compound/session suites, replay cache tests, async READ/WRITE/LAYOUT operations, response size limit tests, invalid opcode/minor-version/RDMA cases, sanitizer leak checks, and slot cache reference-count tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c

## Purpose
Provides helper routines for constructing and freeing NFSv4 callback `CB_COMPOUND` requests sent from the server to clients.

## APIs, Types, and Functions
Exports `cb_compound_init_v4()`, `cb_compound_add_op()`, and `cb_compound_free()`. It uses `nfs4_compound_t`, `nfs_cb_argop4`, `alloc_cb_argop()`, `alloc_cb_resop()`, `free_cb_argop()`, `free_cb_resop()`, and a default tag table containing `"Ganesha CB Compound"`.

## Control Flow, State, and Persistence
Initialization zeroes the compound container, sets minor version and callback identifier, allocates argument and response arrays sized for the planned operation count, and either attaches a caller-provided tag or the static default tag. `cb_compound_add_op()` appends by shallow-copying one callback argument op and increments both argument and response lengths. `cb_compound_free()` releases the allocated op arrays. There is no persistent state beyond the caller-owned callback compound object.

## Dependencies and Integration
Integrated with the NFSv4 callback RPC stack, delegation recall, layout recall, and session backchannel code that needs to compose callback operations. It depends on callback XDR allocation helpers and assumes callers manage any pointed-to data inside shallow-copied ops.

## Risks and Test Signals
Risks include caller-provided tag lifetime, shallow-copy ownership of callback operation payloads, no capacity check in `cb_compound_add_op()`, and mismatched argument/response array lengths if callers over-add. Test signals are callback creation for CB_NULL/CB_RECALL-style operations, bounds tests around planned op count, custom tag lifetime checks, and leak checks after callback failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_cb_Compound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c

## Purpose
Implements NFSv4 `OP_ACCESS`, reporting which requested access bits are supported and currently permitted for the compound current file handle.

## APIs, Types, and Functions
Exports `nfs4_op_access()` and `nfs4_op_access_Free()`. It uses `ACCESS4args`, `ACCESS4res`, `compound_data_t`, `nfs4_sanity_check_FH()`, `nfs_access_op()`, `nfs4_Errno_status()`, and LTTng tracepoints. For minor version 4.2 and newer it permits xattr access bits `ACCESS4_XAREAD`, `ACCESS4_XAWRITE`, and `ACCESS4_XALIST`.

## Control Flow, State, and Persistence
The handler initializes supported/access output to zero, validates the current file handle with no specific file type, rejects unknown access bits above the allowed mask, and calls `nfs_access_op()` to perform the FSAL access check. FSAL success and access denial both return `NFS4_OK` because denial is represented by clearing bits; other FSAL errors map to protocol status. It does not alter filesystem or compound state.

## Dependencies and Integration
Depends on `compound_data_t->current_obj` being set by a prior PUTFH/lookup operation and on shared access conversion code. The compound dispatcher applies export metadata-read permission before this handler runs.

## Risks and Test Signals
Risks include bad max-access masks by minor version, confusion between protocol success and denied bits, and FSAL access implementations returning hard errors for ordinary denials. Test signals are access probes across file types, denied permissions returning `NFS4_OK` with cleared bits, xattr bits only for v4.2+, empty current FH errors, and tracepoint/status parity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c

## Purpose
Implements NFSv4.2 `OP_ALLOCATE` and `OP_DEALLOCATE`, changing file space allocation through the FSAL `fallocate` operation with NFSv4 stateid and permission checks.

## APIs, Types, and Functions
Exports `nfs4_op_allocate()` and `nfs4_op_deallocate()` with shared helper `allocate_deallocate()`. It uses `ALLOCATE4args`, `DEALLOCATE4args`, `stateid4`, `nfs4_sanity_check_FH()`, `nfs4_Check_Stateid()`, `nfs4_State_Get_Pointer()`, `state_deleg_conflict()`, `obj->obj_ops->test_access()`, `obj->obj_ops->fallocate()`, export `MaxOffsetWrite`, and `check_quota(FSAL_QUOTA_BLOCKS)`.

## Control Flow, State, and Persistence
The shared helper requires a regular-file current FH, checks block quota, validates the stateid, converts lock stateids to their open state, accepts write delegations for ordering, rejects invalid state types and opens without write access, checks anonymous stateids for delegation conflicts, verifies write access, enforces max write offset, treats zero length as no-op success, and calls `fallocate(obj, state, offset, size, allocate)`. It releases state references before returning. Persistent file allocation state changes only through FSAL `fallocate`.

## Dependencies and Integration
Depends on NFSv4 state management, delegation conflict rules, export write limits, quota implementation, and FSAL support for allocation/deallocation. The compound dispatcher gates these v4.2 operations and export write permission.

## Risks and Test Signals
Risks include offset+length overflow, stateid handling differences between special, lock, share, and delegation states, delegation conflict delays, backend fallocate support gaps, and quota accounting for deallocate. Test signals are valid allocate/deallocate with write opens, read-only open `OPENMODE`, anonymous stateid with delegation conflict, max-offset `FBIG`, zero-length no-op, quota denial, unsupported FSAL mapping, and state reference leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_allocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c

## Purpose
Implements NFSv4.1 `OP_BIND_CONN_TO_SESSION`, associating the current transport connection with an existing session forechannel and optionally establishing backchannel use.

## APIs, Types, and Functions
Important functions are `nfs4_op_bind_conn()`, `bind_conn_to_session_backchannel()`, and `nfs4_op_nfs4_op_bind_conn_Free()`. It uses `BIND_CONN_TO_SESSION4args/res`, `nfs41_Session_Get_Pointer()`, `reserve_lease_or_expire()`, `check_session_conn()`, `nfs_rpc_create_chan_v41()`, `display_session_id()`, `display_xprt_sockaddr()`, `inc_client_id_ref()`, and `dec_session_ref()`.

## Control Flow, State, and Persistence
The handler rejects minor version 0, looks up the session, reserves the client lease, stores the session and preserved clientid in compound data, adds the current transport to the session connection list, echoes the session ID, and maps the client-requested channel direction. Backchannel requests call `bind_conn_to_session_backchannel()`, which supports only `SP4_NONE` and creates the RPC callback channel. Optional backchannel failure for `FORE_OR_BOTH` degrades to forechannel-only; mandatory failures return errors. Success updates `op_ctx->clientid` and returns selected server channel direction. Persistent state includes session connection membership and possible backchannel resources.

## Dependencies and Integration
Depends on session/clientid tables, lease management, transport state, callback RPC channel creation, and compound cleanup to release preserved references. `nfs4_Compound.c` also enforces that this op is single/first-position as required.

## Risks and Test Signals
Risks include leaked session/clientid refs on mid-handler errors, duplicate or stale connection records, unsupported state protection modes, backchannel setup failures, and RDMA mode echo semantics. Test signals are bind forechannel-only, mandatory and optional backchannel binds, bad session, expired lease, v4.0 invalid use, compound position errors, duplicate connection handling, and connection teardown cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_bind_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c

## Purpose
Implements NFSv4 `OP_CLOSE`, retiring an open stateid, cleaning related lock states, handling NFSv4.0 seqid replay behavior, and returning a final/invalid stateid.

## APIs, Types, and Functions
Exports `nfs4_op_close()`, `cleanup_layouts()`, `nfs4_op_close_Free()`, and `nfs4_op_close_CopyRes()`. It uses `CLOSE4args/res`, `nfs4_sanity_check_FH()`, `nfs4_check_stateid_acquire_state_lock()`, `Check_nfs4_seqid_locked()`, `state_unlock_all_locked()`, `state_del_locked()`, `update_stateid_locked()`, `Copy_nfs4_state_req()`, `nfs4_return_one_state()`, and state/object owner reference helpers.

## Control Flow, State, and Persistence
The handler validates a regular-file current FH, checks and locks the open state, treats certain v4.0 races as replayed close success, validates v4.0 owner seqid, deletes all associated lock states, returns an incremented stateid for v4.0 or an all-zero/`UINT32_MAX` invalid stateid for v4.1+, deletes the open state, invalidates `current_stateid`, and for v4.1+ calls `cleanup_layouts()` to return pNFS layouts marked return-on-close when this was the last open. It releases state locks, object refs, owner refs, and state refs on exit.

## Dependencies and Integration
Deeply integrated with SAL state management, open-owner replay cache, pNFS layout state, FSAL extended close effects via state deletion, and compound current-object state. The dispatcher uses the free/copy hooks for replay cache support.

## Risks and Test Signals
Risks include state lock/ref leaks, close replay ambiguity, deleting locks while iterating, layout return-on-close races, invalid stateid semantics across minor versions, and stale state objects after concurrent closes. Test signals are v4.0 seqid replay and misorder tests, v4.1 close invalid stateid, lock cleanup, last-close layout return, concurrent close/open tests, and sanitizer checks around state reference paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c

## Purpose
Implements NFSv4 `OP_COMMIT`, flushing unstable writes for a byte range and returning the export write verifier. It also supports pNFS data-server commit handles.

## APIs, Types, and Functions
Exports `nfs4_op_commit()` and `nfs4_op_commit_Free()`, with internal `op_dscommit()`. It uses `COMMIT4args/res`, `nfs4_Is_Fh_DSHandle()`, `nfs4_sanity_check_FH(REGULAR_FILE, true)`, `fsal_commit()`, `op_ctx->fsal_export->exp_ops.get_write_verifier()`, `op_ctx->ctx_pnfs_ds->s_ops.dsh_commit()`, and `nfs4_Errno_status()`.

## Control Flow, State, and Persistence
The handler initializes status, logs offset/count, dispatches directly to `op_dscommit()` for data-server file handles, otherwise validates the current FH as a regular file, calls `fsal_commit()` for the requested byte range, and fills the NFSv4 verifier from the active export. The data-server branch bypasses mdcache and calls the pNFS DS commit operation with `current_ds`. The operation persists data by forcing backend writeback/commit; no protocol state is otherwise changed.

## Dependencies and Integration
Depends on FSAL commit semantics, pNFS data-server context, export write verifier generation, and current FH/object setup. The compound table requires metadata write access before dispatch.

## Risks and Test Signals
Risks include verifier mismatch between MDS and DS paths, missing regular-file validation for DS handles, backend partial commit behavior, and stale `current_ds` context. Test signals are COMMIT after unstable writes, zero-count commit, commit past EOF, FSAL commit failure mapping, pNFS DS commit, verifier stability across normal operation, and verifier change after server restart policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c

## Purpose
Implements NFSv4 `OP_CREATE` for non-regular objects: directories, symlinks, sockets, FIFOs, character devices, and block devices. Regular file creation is intentionally left to `OPEN`.

## APIs, Types, and Functions
Exports `nfs4_op_create()` and `nfs4_op_create_Free()`. It uses `CREATE4args/res`, `nfs4_sanity_check_FH(DIRECTORY)`, `check_quota(FSAL_QUOTA_INODES)`, `nfs4_Fattr_Supported()`, `nfs4_Fattr_Check_Access()`, `nfs4_utf8string_scan()`, `nfs4_Fattr_To_FSAL_attr()`, `fsal_create()`, `nfs4_FSALToFhandle()`, `set_current_entry()`, `fsal_get_changeid4()`, and parent change attributes.

## Control Flow, State, and Persistence
The handler validates the current FH and export quota, checks that requested create attributes are supported and writable, validates the object name, converts fattrs to FSAL attrs, maps `createtype4` to FSAL object type and raw-device/link data, supplies default modes if absent, and calls `fsal_create()`. Success builds a new current FH for the created object, invalidates the current stateid, reports the requested attrset mask, computes change info from FSAL pre/post parent change attributes or fallback change IDs, stores the new object as the compound current entry, and returns `NFS4_OK`. Persistent state is the new namespace object.

## Dependencies and Integration
Depends on FSAL create support, NFSv4 attribute conversion, export quota, UTF-8/path component validation, current FH mutation, and compound current-entry reference management. It integrates with subsequent compound ops by replacing the current FH with the created object.

## Risks and Test Signals
Risks include default mode choices, symlink target validation differences, attrset reporting all requested bits after create, change-info atomic flag accuracy, raw device number handling, and current FH update after partial failures. Test signals are create directory/symlink/FIFO/socket/char/block, regular-file rejection, invalid UTF-8 names, unsupported attrs, quota denial, change info before/after/atomic behavior, and follow-up GETFH/GETATTR in the same compound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create_session.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create_session.c

## Purpose
Implements NFSv4.1 `OP_CREATE_SESSION`, confirming or updating a clientid, creating a session with fore/back channel attributes, adding the current connection, optionally creating a callback backchannel, and caching the create-session reply for replay.

## APIs, Types, and Functions
Key functions are `nfs4_op_create_session()`, `populate_callback_params_in_session()`, `schedule_initial_cb_null()`, `initial_cb_null_call()`, and `nfs4_op_create_session_Free()`. It uses `CREATE_SESSION4args/res`, `nfs_client_id_get_unconfirmed()`, `nfs_client_id_get_confirmed()`, `nfs_compare_clientcred()`, `nfs41_session_pool`, `nfs41_Build_sessionid()`, `nfs41_Session_Set/Del()`, `check_session_conn()`, `nfs_client_id_confirm()`, `nfs_client_id_expire()`, `nfs_rpc_create_chan_v41()`, callback security parameter copying, and client/session refcount helpers.

## Control Flow, State, and Persistence
The handler rejects v4.0, locates the clientid in unconfirmed or confirmed tables, locks the client record, handles create-session sequence replay/misorder, verifies principals, validates flags and channel attributes, allocates and initializes `nfs41_session_t`, creates slot arrays and locks, links the session to the clientid, inserts it into the session table, adds the current transport connection, resolves confirmed/unconfirmed clientid transitions, expires old confirmed records when needed, increments the create-session sequence, renews the lease, copies callback security parameters, optionally creates a backchannel and schedules an asynchronous CB_NULL probe, and caches the response in `cid_create_session_slot`. Persistent state includes confirmed clientid updates, active session table entries, connection lists, callback security data, leases, and replay slot response.

## Dependencies and Integration
Depends on the client manager, session table, general fridge thread pool, callback RPC stack, credential comparison, transport connection tracking, and NFSv4.1 compound rules. It is one of the main transitions from `EXCHANGE_ID` client identity into stateful session operation.

## Risks and Test Signals
Risks include refcount leaks in many error paths, callback credential deep-copy ownership, duplicate sessions on replay/misorder races, session table insertion cleanup, old confirmed-client expiration side effects, backchannel creation not affecting success, and locking around client record updates. Test signals are CSESS pynfs cases, sequence replay and misorder, unconfirmed-to-confirmed promotion, confirmed update, principal mismatch, too-small channel attributes, connection add failure, backchannel requested/unavailable, CB_NULL probe behavior, and leak/thread sanitizer runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c

## Purpose
Provides the NFSv4 `OP_DELEGPURGE` handler, currently implemented as unsupported.

## APIs, Types, and Functions
Exports `nfs4_op_delegpurge()` and `nfs4_op_delegpurge_Free()`. It touches `DELEGPURGE4args` only as an unused placeholder, fills `DELEGPURGE4res`, sets `resp->resop = NFS4_OP_DELEGPURGE`, and returns `NFS4ERR_NOTSUPP`.

## Control Flow, State, and Persistence
The handler does no validation of clientid or delegation state because the operation is not supported. It deterministically returns `NFS_REQ_ERROR` with protocol status `NFS4ERR_NOTSUPP`. No persistent state changes occur.

## Dependencies and Integration
The operation is still present in `optabv4[]`, so compounds containing it dispatch here and stop at this error. The free callback is a no-op because no dynamic response data is allocated.

## Risks and Test Signals
Risks are mostly protocol-coverage gaps: clients expecting delegation purge semantics will fail, and future implementation must revisit clientid validation and delegation cleanup. Test signals are compounds containing `DELEGPURGE` returning `NFS4ERR_NOTSUPP`, no result memory leaks, and dispatcher behavior stopping the compound after the error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegpurge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c

## Purpose
Implements NFSv4 `OP_DELEGRETURN`, returning a file delegation stateid to the server and deleting the corresponding delegation state on success.

## APIs, Types, and Functions
Exports `nfs4_op_delegreturn()` and `nfs4_op_delegreturn_Free()`. It uses `DELEGRETURN4args/res`, `nfs4_sanity_check_FH(REGULAR_FILE)`, `nfs4_Check_Stateid()`, `get_state_owner_ref()`, `deleg_heuristics_recall()`, `reset_cbgetattr_stats()`, `release_lease_lock()`, `nfs4_Errno_state()`, `state_del_locked()`, `STATELOCK_lock/unlock()`, and state refcount helpers.

## Control Flow, State, and Persistence
The handler validates the current FH as a regular file, converting `ISDIR` to `INVAL`, checks the delegation stateid, obtains the owner reference, locks the object state, updates delegation recall heuristics and CB_GETATTR stats, releases the owner ref, calls `release_lease_lock()` to return the delegation through SAL/FSAL, maps the state status, and deletes the delegation state if release succeeds. It unlocks the object and drops the state reference on exit. Persistent state changes include delegation removal, heuristics updates, and callback stat reset.

## Dependencies and Integration
Depends on NFSv4 stateid validation, delegation/lease SAL paths, object state locking, and FSAL lease release behavior. The compound dispatcher requires metadata-read export permission before calling it.

## Risks and Test Signals
Risks include stale owner/state handling, lock ordering around object state, deleting state after partial release failures, and protocol status differences for non-regular file handles. Test signals are successful delegation return, stale/bad stateid, directory handle returning `INVAL`, concurrent recall/return races, lease-release failure mapping, and state table cleanup verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_delegreturn.c -->
