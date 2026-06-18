# sources/distributed-fs/ceph-client/fs/nfs/nfs2xdr.c

## Purpose
`nfs2xdr.c` implements XDR encoding and decoding for NFSv2 RPC arguments and results. It defines the RPC procedure table `nfs_procedures[]` and `nfs_version2`, which the NFSv2 module registers through `nfs2super.c`.

## Important APIs, Types, And Functions
The file provides low-level codecs for fixed NFSv2 filehandles, attributes, times, filenames, paths, read/write data, directory entries, and statfs results. It translates uid/gid values through the RPC client's user namespace. Publicly consumed symbols are `nfs2_decode_dirent()` and `nfs_version2`; `nfs_procedures[]` is declared in `internal.h`.

Encoders include `nfs2_xdr_enc_fhandle()`, `nfs2_xdr_enc_sattrargs()`, `nfs2_xdr_enc_diropargs()`, `nfs2_xdr_enc_readlinkargs()`, `nfs2_xdr_enc_readargs()`, `nfs2_xdr_enc_writeargs()`, create/remove/rename/link/symlink encoders, and `nfs2_xdr_enc_readdirargs()`. Decoders include status, attrstat, diropres, readlink, read, write, readdir, and statfs result handlers.

## Control Flow And Integration Points
Each RPC operation in `nfs_procedures[]` maps an NFSv2 procedure number to an encoder, decoder, argument size, reply size, timer class, and stat index. Read and readlink replies prepare page-backed receive buffers and use `xdr_read_pages()`. Write and symlink paths mark XDR buffers as write-backed. Directory replies are stored raw in the page cache; `nfs2_decode_dirent()` later decodes entries during readdir iteration.

## State And Persistence Behavior
The file keeps static procedure metadata and per-procedure counters in `nfs_version2_counts`. Runtime decoded state is written into caller-provided `nfs_fattr`, `nfs_fh`, `nfs_pgio_res`, `nfs_entry`, or statfs structures. NFSv2 read replies have no EOF flag, so `decode_nfsdata()` clears `result->eof`.

## Dependencies
Dependencies include SunRPC XDR streams, NFSv2 protocol constants, NFS common errno/status translation, page-cache reply buffers, user namespace uid/gid conversion, tracepoints, and common NFS attribute helpers from `internal.h`.

## Risks And Edge Cases
NFSv2 has 32-bit offsets, sizes, cookies, and fixed 32-byte filehandles. The decoder clamps cheating read servers that claim more data than received. Path and filename length checks must be exact; malformed replies return `-EIO` or `-ENAMETOOLONG`. FIFO special handling maps the historical NFSv2 FIFO device convention to `S_IFIFO`. Invalid uid/gid mappings reject attributes with `-EINVAL`.

## Test Signals
Test NFSv2 getattr/setattr/lookup/read/write/create/remove/rename/readdir/statfs, long names and paths, FIFO nodes, user namespace id mapping, short or malformed read replies, directory cookie iteration, and protocol table counters.
