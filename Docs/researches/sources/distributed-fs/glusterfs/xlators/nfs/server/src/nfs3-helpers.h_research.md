# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.h

## Purpose

`nfs3-helpers.h` declares the NFSv3 helper API used by request handlers and related modules. It is the public surface for file-handle extraction, errno/status conversion, XDR decode preparation, response construction, directory-result cleanup, logging, file-handle resolution, cookie verification, access-bit mapping, auth checks, and device-ID mapping.

## Important APIs, types, and functions

The declarations are grouped around the NFSv3 procedure set: LOOKUP, GETATTR, FSINFO, ACCESS, READDIR, READDIRPLUS, FSSTAT, CREATE, SETATTR, MKDIR, SYMLINK, READLINK, MKNOD, REMOVE, RMDIR, LINK, RENAME, WRITE, COMMIT, READ, and PATHCONF. It also declares `GF_NFS3_FD_CACHED`, status string helpers, `nfs3_cached_inode_opened()`, logging helpers, `nfs3_fh_resolve_*()` functions, `nfs3_fh_resolve_and_resume()`, `nfs3_verify_dircookie()`, `nfs3_is_parentdir_entry()`, `nfs3_request_to_accessbits()`, `nfs3_fh_auth_nfsop()`, and `nfs3_map_deviceid_to_statdev()`.

## Control flow

The header's comments document a key decode-control pattern: `nfs3_prep_*args()` pre-populates XDR argument members with caller-owned stack/storage pointers so SunRPC decode avoids tiny heap allocations. Request handlers then decode into those prepared structs, extract handles/names, resolve file handles, perform FOPs, and use `nfs3_fill_*res()` plus `nfs3svc_submit_reply()` to respond.

## State and persistence behavior

No state is stored in the header. The API operates on caller-owned request/call state, `struct nfs3_state`, `struct nfs3_fh`, `struct iatt`, `gf_dirent_t`, and XDR result structs. Ownership is important for READDIR/READDIRPLUS result chains, which require explicit free helpers.

## Dependencies and integration points

The header includes `nfs3.h`, `nfs3-fh.h`, NFSv3 message/XDR headers, and `sys/statvfs.h`. It is included by NFSv3 operation code and utility modules that need consistent marshalling and resolution behavior.

## Risks and edge cases

- The API surface is broad; response helper signatures must match XDR union layouts exactly.
- Prep helpers rely on caller-provided buffers remaining live through decode.
- Cleanup helpers must be called for allocated directory result chains to avoid leaks.
- Resolution helpers are asynchronous via `nfs3_resume_fn_t`, so call-state lifetime must outlive callbacks.

## Test signals

Compile tests catch signature drift. Runtime tests should exercise each prep/fill pair through an encoded/decoded RPC, verify READDIRPLUS cleanup, and validate that resolution callbacks resume exactly once on success and failure.
