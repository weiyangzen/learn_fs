# sources/distributed-fs/ceph-client/fs/nfsd/nfsxdr.c

Purpose: `nfsxdr.c` implements NFSv2 XDR encode/decode helpers for filehandles, attributes, procedure arguments, procedure results, directory entries, and result release. It is the wire-format partner of `nfsproc.c`. The source was read as a complete 663-line file.

Important APIs/types/functions: decoders include `nfssvc_decode_fhandleargs`, `nfssvc_decode_sattrargs`, `nfssvc_decode_diropargs`, `nfssvc_decode_readargs`, `nfssvc_decode_writeargs`, `nfssvc_decode_createargs`, `nfssvc_decode_renameargs`, `nfssvc_decode_linkargs`, `nfssvc_decode_symlinkargs`, and `nfssvc_decode_readdirargs`. Encoders include `svcxdr_encode_stat`, `svcxdr_decode_fhandle`, `svcxdr_encode_fattr`, `nfssvc_encode_statres`, `nfssvc_encode_attrstatres`, `nfssvc_encode_diropres`, `nfssvc_encode_readlinkres`, `nfssvc_encode_readres`, `nfssvc_encode_readdirres`, `nfssvc_encode_statfsres`, `nfssvc_encode_nfscookie`, and `nfssvc_encode_entry`. Release helpers are `nfssvc_release_attrstat`, `nfssvc_release_diropres`, and `nfssvc_release_readres`.

Control flow: decoders consume an `xdr_stream`, initialize `svc_fh` objects, validate names and payload lengths, convert NFSv2 `sattr` sentinels into Linux `iattr` flags, and build subsegments for opaque write payloads. Encoders reserve stream space, write status first, and conditionally append attributes, filehandles, opaque pages, readdir terminators, statfs data, and read/readlink payload metadata. Readdir uses a page-backed XDR buffer; each new entry patches the previous entry's cookie, then writes presence, fileid, clipped name, and placeholder cookie.

State and persistence: no persistent state. Per-request state includes decoded pointers into the RPC buffer, `svc_fh` ownership, response pages, `cookie_offset`, and result lengths. Release callbacks drop filehandle refs after the response has been encoded.

Dependencies and integration points: shared VFS attribute data, `xdr.h` argument/result structs, auth namespace mapping via `nfsd_user_namespace`, filehandle helpers, lease mtime adjustment, export fsid-source selection, and SunRPC XDR/page-payload helpers. `nfsproc.c` binds these helpers into the NFSv2 procedure table.

Risks: name decoding rejects empty names, slash, and embedded NUL. NFSv2 fixed-size filehandles are copied as exactly `NFS_FHSIZE`. `sattr` has legacy Sun compatibility for `0xffff` mode and `useconds=1000000` touch semantics. Attribute encoding truncates symlink size at `NFS_MAXPATHLEN` and maps fsid depending on export configuration. Readdir must correctly roll back partial entries on `toosmall`.

Test signals: XDR round trips for every NFSv2 procedure, malformed short buffers, invalid names, large write/read payload bounds, UID/GID namespace munging, sattr sentinel handling, symlink size clipping, statfs field encoding, readdir cookie patching and rollback, and filehandle release callbacks after encode.
