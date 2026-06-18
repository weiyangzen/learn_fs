# sources/distributed-fs/ceph-client/fs/nfsd/nfs3proc.c

## Purpose
`nfs3proc.c` implements NFSD's NFSv3 procedure layer. It maps decoded RPC arguments to NFSD VFS/filehandle/filecache helpers, applies NFSv3-specific semantics and status mappings, and registers the NFSv3 procedure table.

## Important APIs, types, and functions
Procedure handlers cover all NFSv3 calls: NULL, GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT. Important helpers include `nfsd3_map_status()`, `nfsd3_create_file()`, and `nfsd3_init_dirlist_pages()`. The registration objects are `nfsd_procedures3` and `const struct svc_version nfsd_version3`.

## Control flow
Each handler copies or initializes response filehandles, calls the relevant NFSD helper, maps internal status through `nfsd3_map_status()`, and returns RPC-level success so the protocol status is encoded in the reply. READ clamps count to service payload and reply buffer limits and clamps offsets to `OFFSET_MAX`. WRITE validates offset plus length before calling `nfsd_write()`. CREATE implements unchecked, guarded, and exclusive verifier semantics, including Solaris/XFS high-bit masking on verifier timestamps and post-create setattr handling. READDIR/READDIRPLUS allocate reply pages, run `nfsd_readdir()` with NFSv3 entry encoders, backpatch cookies, and recycle unused pages. COMMIT obtains a GC-managed writable `nfsd_file` before calling `nfsd_commit()`.

## State and persistence
The procedure layer is mostly stateless. Persistent effects are delegated to VFS operations for writes, creates, removes, renames, links, setattr, symlink, mknod, and commits. Runtime response state includes filehandles, weak-cache-consistency attrs, page buffers, readdir cookies, and write verifiers. Per-CPU procedure counters are maintained by the RPC service layer.

## Dependencies and integration points
It depends on `xdr3.h` decode/encode functions, `vfs.c` NFSD operation helpers, filecache acquisition for COMMIT, export flags such as `NFSEXP_NOREADDIRPLUS`, filesystem magic constants for FSINFO/PATHCONF behavior, tracepoints, and duplicate reply cache policy via `pc_cachetype`. Non-idempotent operations are marked `RC_REPLBUFF`.

## Risks and test signals
Risks include incorrect internal-to-v3 status mapping, offset/count overflow, response page accounting in READDIR, exclusive create verifier compatibility, stale filehandle release, weak-cache-consistency attr correctness, READDIRPLUS filehandle composition across mountpoints/export roots, and duplicate reply cache classification. Test signals include full NFSv3 connectathon/pynfs coverage, large read/write boundary tests, exclusive create replay, non-idempotent duplicate RPC replay, READDIRPLUS with `nordirplus`, FSINFO/PATHCONF on ext2/msdos/other filesystems, COMMIT after unstable writes, and symlink target page-boundary cases.
