# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.c` is a handwritten rpcgen-style XDR implementation for NFSv3, mount, export, and related structures. It serializes/deserializes primitive aliases, file handles, attributes, weak-cache-consistency data, all core NFSv3 procedure arguments/results, mount responses/lists, exports, and cleanup helpers. The source was read as a complete 1907-line file for this report.

## Important APIs, Types, and Functions

Primitive wrappers include `xdr_uint64`, `xdr_int64`, `xdr_uint32`, `xdr_int32`, `xdr_filename3`, `xdr_nfspath3`, `xdr_fileid3`, `xdr_cookie3`, verifier helpers, UID/GID/size/offset/mode/count helpers, `xdr_nfsstat3`, and `xdr_ftype3`. Structural helpers include `xdr_specdata3`, `xdr_nfs_fh3`, `xdr_nfstime3`, `xdr_fattr3`, `xdr_post_op_attr`, `xdr_pre_op_attr`, `xdr_wcc_data`, `xdr_post_op_fh3`, `xdr_sattr3`, `xdr_diropargs3`, and `xdr_sattrguard3`.

Procedure coverage includes getattr, setattr, lookup, access, readlink, read, write, create, mkdir, symlink, mknod, remove, rmdir, rename, link, readdir, readdirp, fsstat, fsinfo, pathconf, and commit. Mount/export support includes `xdr_fhandle3`, `xdr_dirpath`, `xdr_name`, `xdr_mountstat3`, `xdr_mountres3`, `xdr_mountbody`, `xdr_mountlist`, `xdr_groups`, `xdr_exports`, and `xdr_exportnode`. Cleanup helpers are `xdr_free_exports_list`, `xdr_free_mountlist`, and `xdr_free_write3args_nocopy`.

## Control Flow

Each XDR function returns `FALSE` on the first failed field operation and `TRUE` after all fields are processed. Union-like results first serialize/deserialize status or discriminator fields, then switch on success/failure cases to choose the correct arm. Optional attributes and handles use boolean discriminators. Linked lists use recursive `xdr_pointer` for NFS directory, mount, group, and export lists. `xdr_pathconf3resok` has optimized inline encode/decode branches using `XDR_INLINE` for four booleans, with a field-by-field fallback. `xdr_write3args` intentionally decodes only the payload length and leaves remaining payload extraction to higher-level nocopy code.

## State and Persistence Behavior

No global state is owned. Decode operations can allocate strings, opaque byte arrays, file handles, and list nodes through XDR routines. Cleanup helpers free recursive or iterative mount/export list allocations and the nocopy write file-handle buffer. Encoded/decoded values persist in caller-owned structures and RPC buffers.

## Dependencies and Integration Points

It depends on `xdr-nfs3.h`, Gluster memory helpers, and `xdr-common.h`. `msg-nfs3.c` wraps these functions for iovec-based RPC handlers, and the GNFS server relies on the exact NFSv3 wire format implemented here.

## Risks and Edge Cases

This is wire-format code, so any field order or discriminator mistake breaks NFS interoperability. Several list encoders are recursive and can consume stack on deeply nested lists. Nocopy write handling is subtle because `data.data_len` is filled but `data.data_val` is not populated by `xdr_write3args`; callers must use the remaining payload iovec. Memory ownership follows SunRPC allocation conventions mixed with Gluster `GF_FREE`/`FREE`, so cleanup must match allocation source. The inline fast path in `xdr_pathconf3resok` must behave identically to fallback paths for encode/decode/free operations.

## Test Signals

NFSv3 protocol round-trip tests for every procedure, byte-level comparison with known-good rpcgen encodings, mount/export list tests, large readdir/readdirp responses, nocopy write payload tests, pathconf inline/fallback coverage, decode failure and cleanup leak tests, and interoperability tests with standard NFSv3 clients are important.
