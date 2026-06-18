# sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.h

Purpose: `nfsfh.h` defines the on-wire and internal NFSD filehandle layouts plus helper functions for composing, comparing, hashing, and releasing filehandle-backed state. The source was read as a complete 339-line file.

Important APIs/types/functions: core types are `struct knfsd_fh`, `typedef struct svc_fh`, `enum nfsd_fsid`, and `enum fsid_source`. Important helpers/macros include `fh_version`, `fh_auth_type`, `fh_fsid_type`, `fh_fileid_type`, `fh_fsid`, `mk_fsid`, `key_len`, `fh_copy`, `fh_copy_shallow`, `fh_init`, `fh_match`, `fh_fsid_match`, `fh_want_write`, `fh_drop_write`, `knfsd_fh_hash`, and `fh_clear_pre_post_attrs`. It declares `fh_verify`, `fh_verify_local`, `fh_getattr`, `fh_compose`, `fh_update`, `fh_put`, `nfsd4_change_attribute`, and pre/post attribute fillers.

Control flow: inline flow is mostly data preparation and cleanup. `mk_fsid` writes the fsid portion for a selected encoding scheme, `key_len` returns the corresponding byte length, `fh_init` zeroes a handle and sets max size, `fh_want_write`/`fh_drop_write` acquire and release mount write access, and match/hash helpers support comparisons and diagnostics. The declared C file functions perform actual decode/encode and validation.

State and persistence: `knfsd_fh` stores opaque bytes sent to clients; `svc_fh` wraps that with transient server-side dentry/export refs, write protection state, WCC flags, readdir-cookie sizing, and saved pre/post attributes. The filehandle byte format is a compatibility contract with clients and exportfs, while `svc_fh` state is per-request or per-compound and must be released.

Dependencies and integration points: crc32, SunRPC service types, inode versioning, exportfs fid types, NFSv4 constants, and export metadata. This is the shared filehandle contract for XDR decoders, NFS procedure implementations, export cache lookup, VFS operations, stats, and trace formatting.

Risks: the layout uses host-byte-order words for opaque values, sometimes storing network-order pieces with sparse casts. Alignment-sensitive writes in `mk_fsid` for 64-bit inode/UUID formats require care. Any new fsid type must update `key_len`, composition, decoding, and compatibility expectations. `fh_copy` warns when copying an initialized handle with a dentry because ownership would be duplicated incorrectly.

Test signals: handle encode/decode across all fsid types, NFSv2/3/4 max-size behavior, mount write reference balancing, hash compatibility with packet analyzers, match/fsid-match comparisons, WCC flag propagation, and build coverage across filesystems with and without UUIDs or stable device IDs.
