# Group Research: group_475_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_61f8a9fdb25b

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vnops.c

## Purpose

`nfs3_vnops.c` is the illumos NFSv3 client vnode operation implementation. It maps VFS/VOP calls onto NFSv3 RPCs, VM/page-cache operations, name cache maintenance, lock-manager integration, ACL/security hooks, and close-to-open consistency behavior.

The exported operation table is `nfs3_vnodeops_template`, with `nfs3_getvnodeops()` returning the installed `struct vnodeops *`. The file is central to the NFSv3 client because it bridges local vnode semantics and remote NFS protocol behavior.

## Main Interfaces

The VOP entry points include:

- File lifecycle and I/O: `nfs3_open`, `nfs3_close`, `nfs3_read`, `nfs3_write`, `nfs3_ioctl`, `nfs3_fsync`
- Attributes and permissions: `nfs3_getattr`, `nfs3_setattr`, `nfs3_access`, `nfs3_setsecattr`, `nfs3_getsecattr`, `nfs3_pathconf`
- Namespace operations: `nfs3_lookup`, `nfs3_create`, `nfs3_remove`, `nfs3_link`, `nfs3_rename`, `nfs3_mkdir`, `nfs3_rmdir`, `nfs3_symlink`, `nfs3_readlink`, `nfs3_readdir`
- VM integration: `nfs3_getpage`, `nfs3_putpage`, `nfs3_pageio`, `nfs3_dispose`, `nfs3_map`, `nfs3_addmap`, `nfs3_delmap`
- Locking and share reservations: `nfs3_frlock`, `nfs3_shrlock`, `nfs3_rwlock`, `nfs3_rwunlock`
- Identity/utility: `nfs3_fid`, `nfs3_seek`, `nfs3_realvp`, `nfs3_inactive`

Important internal helpers include `nfs3read`, `nfs3write`, `nfs3_bio`, `nfs3_rdwrlbn`, `nfs3lookup_dnlc`, `nfs3lookup_otw`, `nfs3create`, `nfs3mknod`, `nfs3rename`, `do_nfs3readdir`, `nfs3readdir`, `nfs3readdirplus`, `nfs3_commit`, `nfs3_putpage_commit`, and commit-page gathering helpers.

## Behavior And Data Flow

Most vnode operations follow this pattern:

1. Validate the caller is in the mount's NFS zone.
2. Acquire rnode locks as needed.
3. Validate or purge local caches.
4. Build NFSv3 RPC argument structs.
5. Call `rfs3call()` with an XDR routine from `nfs3_xdr.c`.
6. Translate NFS status with `geterrno3()`.
7. Update attributes, weak cache consistency data, DNLC, readdir cache, page state, and vnode events.

The file uses `rnode_t` as the per-vnode state carrier. Key fields include cached attributes, size, access cache, readdir cache AVL tree, symlink cache, credential cache, error state, write verifier, dirty/commit flags, mmap count, outstanding async write count, and unlink-open cleanup state.

## Cache And Consistency Model

Open and close paths implement close-to-open consistency unless `MI_NOCTO` disables it. `nfs3_open()` validates caches or forces an over-the-wire `GETATTR` when mmap or cached data might be stale. `nfs3_close()` flushes dirty pages and commits unstable writes unless the mount is `nocto`, in which case it starts async writeback.

Attribute cache handling is pervasive:

- `PURGE_ATTRCACHE` is used after uncertain RPC outcomes, stale file handles, writes, removes, and rename-related uncertainty.
- `nfs3_cache_post_op_attr`, `nfs3_cache_post_op_vattr`, and `nfs3_cache_wcc_data` update attributes from NFS post-op or WCC data.
- `RWRITEATTR` marks that a WRITE changed server state and returned insufficient attributes, forcing later refresh.

The DNLC is used for positive and negative lookup caching. `nfs3lookup_dnlc()` validates directory caches before trusting DNLC entries. `nfs3lookup_otw()` performs actual LOOKUP RPCs and populates nodes/DNLC. Negative lookup caching is controlled by `nfs3_lookup_neg_cache`.

Directory read caching is an AVL-backed `rddir_cache` indexed by NFS cookie and request length. `nfs3_readdir()` can use cached results, wait for in-progress fills, trigger asynchronous readahead, and choose READDIRPLUS when previous lookup behavior suggests it will help populate DNLC.

## File I/O And VM Integration

`nfs3_read()` and `nfs3_write()` prefer VM/segmap cached I/O, but bypass VM for `VNOCACHE`, per-rnode direct I/O, mount-level direct I/O, or non-mapped files without cached pages. Direct read uses `nfs3_directio_read()`, decoding directly into the caller's `uio`.

Cached reads call `nfs3_validate_caches()`, map file pages with `vpm_data_copy()` or `segmap_getmapflt()`, and release pages with `SM_DONTNEED` when appropriate.

Cached writes enforce append serialization, file-size limits, async write throttling, and use `writerp()` to dirty page-cache data. `nfs3_write()` forces synchronous writeback for `FSYNC`, `FDSYNC`, `MI_NOAC`, swap vnodes, or out-of-space state.

`nfs3_getpage()` and `nfs3_getapage()` handle page faults and readahead. They use `pvn_getpages`, `pvn_read_kluster`, `pageio_setup`, and `nfs3_bio()` to fetch pages. EOF is represented internally with `NFS_EOF`.

`nfs3_putpage()` and `nfs3_putapage()` handle writeback, clustering, async putpage, and page invalidation. The `RMODINPROGRESS` check prevents data loss when pageout races with a write whose `r_size` update has not completed.

## Stable Writes And COMMIT

The file implements full NFSv3 unstable write handling:

- `nfs3_rdwrlbn()` chooses `UNSTABLE` writes for async writeback when memory pressure allows, marking pages with `C_DELAYCOMMIT`.
- `nfs3write()` sends WRITE RPCs, checks returned counts, tracks server write verifier changes, and purges attributes.
- `nfs3_commit()` sends COMMIT RPCs and compares returned verifier against `rp->r_verf`.
- Verifier mismatches call `nfs3_set_mod()` to mark pages dirty again and return `NFS_VERF_MISMATCH`.
- `nfs3_putpage_commit()` loops: async flush, sync flush, verify write verifier, then commit pages; on verifier mismatch it restarts.
- `nfs3_dispose()` batches commit-needed pages before freeing or destroying them, and can defer commit from pageout/fsflush or cross-zone context through `nfs_async_commit()`.

This write verifier machinery is one of the highest-risk areas in the file because correctness depends on preserving dirty data across server reboots or unstable-write loss.

## Namespace Operations

`nfs3_create()` avoids trusting DNLC for existence decisions and uses guarded CREATE for non-exclusive creates to avoid retransmitted truncation. Exclusive creates generate a verifier and may follow with SETATTR to set final attributes/times.

`nfs3_remove()` implements unlink-open semantics by renaming active files to temporary `.nfs*` names and storing cleanup state in the rnode. `nfs3_inactive()` later removes these temporary names.

`nfs3rename()` handles target activity, mountpoint checks, unlink-open semantics for overwritten active targets, source/target directory lock ordering, DNLC invalidation, readdir cache purging, WCC updates, and vnode event emission. It maps NFS `ENOTEMPTY` to System V style `EEXIST`.

`nfs3_mkdir`, `nfs3_rmdir`, `nfs3_link`, `nfs3_symlink`, and `nfs3mknod` all update directory WCC data, purge readdir caches, adjust DNLC, and compensate for server behavior such as unsupported LINK/SYMLINK or differing group assignment.

## Locking, Mapping, And Zones

Zone checks guard nearly every operation. Synchronous operations return `EIO` or `EPERM` from the wrong zone. `nfs3_inactive()` and some async page cleanup paths can hand work to async workers when called from the wrong zone.

`nfs3_map()` coordinates `r_rwlock`, `r_lkserlock`, and `r_inmap` to prevent races between mmap, direct I/O, and remote locks. `nfs3_delmap()` uses address-space callbacks so NFS writeback/commit can happen after dropping the address-space lock. The callback updates map counts, flushes dirty shared writable mappings, and invalidates direct-I/O pages.

`nfs3_frlock()` rejects unsupported OFD/flock modes, validates byte ranges, delegates local-lock mounts to local locking, otherwise serializes with `r_lkserlock`, flushes/invalidate caches before locking or unlocking, and calls `lm4_frlock()`. `nfs3_shrlock()` similarly integrates with local share reservations or remote lock manager share calls.

## Security And ACLs

`nfs3_setattr()` calls `secpolicy_vnode_setattr()` before issuing SETATTR. Mode/owner/group changes purge the NFS access cache and ACL cache. `nfs3_access()` translates VFS access bits to NFSv3 ACCESS bits, handles readonly checks, consults per-rnode access cache, and retries with network-adjusted credentials from `crnetadjust()`.

ACLs are delegated to `acl_setacl3()` and `acl_getacl3()` when mount flag `MI_ACL` is still active; otherwise `nfs3_getsecattr()` falls back to fabricated ACLs through `fs_fab_acl()`.

## Notable Invariants

- NFS RPCs that touch a mount generally require `nfs_zone() == mi_zone`.
- `r_rwlock` serializes high-level vnode operations such as create/remove/rename/readdir and append writes.
- `r_lkserlock` serializes locking with mmap/direct I/O decisions.
- `RCOMMIT` serializes use of the rnode commit page list.
- `r_count`, `r_awcount`, and `r_gcount` throttle or synchronize pageout, writes, and getattr-triggered flushes.
- `rp->r_error` stores async writeback errors until close/fsync-style consumers retrieve them.
- DNLC and readdir caches are purged after namespace mutations or stale/uncertain outcomes.
- `p_fsdata` tracks whether a page needs COMMIT after unstable writes.

## Dependencies

This file depends heavily on:

- NFS client state and RPC helpers from `nfs_clnt.h`, `rnode.h`, and related NFS code.
- XDR routines in `nfs3_xdr.c`, such as `xdr_READ3args`, `xdr_READ3vres`, `xdr_WRITE3args`, `xdr_WRITE3res`, `xdr_READDIR3vres`, and `xdr_COMMIT3res`.
- VM/page-cache APIs: `segmap`, `vpm`, `pvn_*`, `page_*`, `hat_*`, `pageio_setup`.
- DNLC and vnode event APIs.
- Lock-manager functions: `lm4_frlock`, `lm4_shrlock`, `nfs_lockrelease`, `nfs_lockcompletion`.
- ACL helpers: `acl_getacl3`, `acl_setacl3`, `acl_getxattrdir3`.

## Research Notes

This is not just an RPC wrapper. It encodes the client-side semantics that make NFSv3 behave like a local filesystem under VFS: close-to-open cache consistency, unlink-open behavior, memory mapped writeback, unstable write commit, negative lookup caching, READDIRPLUS DNLC population, ACL fallback, lock-cache interaction, and cross-zone cleanup behavior.

Potential audit hotspots are write verifier mismatch handling, `RMODINPROGRESS` writeback races, unlink-open rename cleanup, `nfs3_delmap()` callback flow, direct I/O cache invalidation, and any paths that update `rp->r_error` asynchronously.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_xdr.c

## Purpose

`nfs3_xdr.c` contains the illumos NFSv3 XDR encode/decode routines used by both NFS client and server code. It serializes NFSv3 RPC arguments and results, decodes server responses into kernel-native structures, supports inline fast paths, and integrates with RDMA and mblk-backed XDR streams.

The file is protocol plumbing, but it also enforces important safety and interoperability rules: bounded string decoding, filehandle validation, size/time overflow handling, directory response bounds checks, and direct decode into `vattr_t`, `dirent64_t`, or `uio`.

## Main Interfaces

Important public XDR routines include:

- Basic types: `xdr_string3`, `xdr_nfs_fh3`, `xdr_nfs_fh3_server`, `xdr_diropargs3`, `xdr_post_op_attr`, `xdr_post_op_fh3`
- Attribute operations: `xdr_GETATTR3res`, `xdr_GETATTR3vres`, `xdr_SETATTR3args`, `xdr_SETATTR3res`
- Lookup/access/readlink: `xdr_LOOKUP3res`, `xdr_LOOKUP3vres`, `xdr_ACCESS3args`, `xdr_ACCESS3res`, `xdr_READLINK3args`, `xdr_READLINK3res`
- Data I/O: `xdr_READ3args`, `xdr_READ3res`, `xdr_READ3vres`, `xdr_READ3uiores`, `xdr_WRITE3args`, `xdr_WRITE3res`
- Namespace operations: `xdr_CREATE3args`, `xdr_CREATE3res`, `xdr_MKDIR3args`, `xdr_MKDIR3res`, `xdr_SYMLINK3args`, `xdr_SYMLINK3res`, `xdr_MKNOD3args`, `xdr_MKNOD3res`, `xdr_REMOVE3res`, `xdr_RMDIR3res`, `xdr_RENAME3args`, `xdr_RENAME3res`, `xdr_LINK3args`, `xdr_LINK3res`
- Directory operations: `xdr_READDIR3args`, `xdr_READDIR3res`, `xdr_READDIR3vres`, `xdr_READDIRPLUS3args`, `xdr_READDIRPLUS3res`, `xdr_READDIRPLUS3vres`
- Filesystem metadata: `xdr_FSSTAT3res`, `xdr_FSINFO3res`, `xdr_PATHCONF3res`
- Commit: `xdr_COMMIT3args`, `xdr_COMMIT3res`

Several helpers are private: `xdr_decode_nfs_fh3`, `xdr_encode_nfs_fh3`, `xdr_fattr3`, `xdr_fattr3_to_vattr`, `xdr_post_op_vattr`, `xdr_wcc_data`, `xdr_sattr3`, `xdr_putdirlist`, and `xdr_putdirpluslist`.

## Filehandle Encoding

The file has two NFSv3 filehandle paths:

- `xdr_nfs_fh3()` is the generic counted opaque filehandle routine.
- `xdr_nfs_fh3_server()` uses illumos-specific internal filehandle knowledge for server-side encode/decode unless `FH_WEBNFS` requires generic encoding.

`xdr_inline_decode_nfs_fh3()` validates total size and component sizes before reconstructing the internal `nfs_fh3`. It handles native-order internal fields, unaligned length fields, historical `NFS_FHMAXDATA` padding behavior, and final XDR alignment. Malformed filehandles are decoded far enough to preserve stream position but leave a zero length so the NFS layer can reject them.

`xdr_inline_encode_nfs_fh3()` computes on-the-wire length, rounds to an XDR word boundary, zeroes padding, and writes the internal handle layout into the XDR stream.

## String And Attribute Handling

`xdr_string3()` treats protocol strings as counted strings but returns C strings to callers. On decode it rejects embedded NULs by comparing `strlen()` to the counted length. Names that exceed the local max are skipped with `XDR_SKIPBYTES` and represented by the sentinel `nfs3nametoolong`.

`xdr_fattr3()` is the raw NFSv3 attribute serializer. `xdr_fattr3_to_vattr()` is the client-oriented fast decoder that writes directly into `vattr_t`. It converts NFS file types to vnode types, maps nobody uid/gid values, validates file sizes with `NFS3_SIZE_OK`, handles optional pre-epoch time behavior, checks time overflow, computes `va_nblocks`, and fills device numbers for character/block special files.

`xdr_post_op_vattr()` decodes optional post-op attributes into `vattr_t` and drops invalid attributes by clearing the `attributes` boolean. `xdr_post_op_attr()` is the raw `fattr3` variant. `xdr_wcc_data()` handles weak cache consistency pre/post attributes and validates pre-op times on 32-bit builds.

## RPC Result Patterns

Most operation result encoders/decoders follow the NFSv3 discriminated-union pattern:

1. Decode or encode `status`.
2. If status is not `NFS3_OK`, serialize failure attributes or WCC data.
3. If status is OK, serialize operation-specific payload and post-op/WCC data.

This appears in SETATTR, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, WRITE, COMMIT, FSSTAT, FSINFO, and PATHCONF.

The client vnode code in `nfs3_vnops.c` relies on these routines to leave caches in a useful state even after errors, because failure arms frequently carry post-op attrs or WCC data.

## READ/WRITE And RDMA Support

`xdr_READ3args()` supports ordinary XDR plus RDMA write chunks. It can register a reply write chunk backed by either a `uio` or an address buffer. On RDMA decode it records the write list and connection.

`xdr_READ3res()` supports server-side encoding with inline data, mblk data, or RDMA_WRITE transfer through `xdrrdma_send_read_data()`.

`xdr_READ3vres()` is the normal client decode path into an address buffer and validates RDMA write-list byte counts. `xdr_READ3uiores()` is direct-I/O oriented: it skips attributes, decodes into a `uio`, supports `xdrmblk_ops`, RDMA write-list completion, inline XDR buffers, and fallback temporary allocation.

`xdr_WRITE3args()` supports ordinary bytes, mblk decode, and RDMA read-from-client via `xdrrdma_getrdmablk()` and `xdrrdma_read_from_client()`. Its FREE path releases RDMA clists. `xdr_WRITE3res()` decodes WCC data, count, stable commit mode, and write verifier, treating the verifier as an XDR hyper for efficiency.

## Directory Handling

`xdr_READDIR3res()` and `xdr_putdirlist()` encode server directory listings while respecting the requested byte count. Entry sizing includes list booleans, fileid, name length, padded name bytes, cookie, final false marker, and EOF marker.

`xdr_READDIR3vres()` decodes client directory responses directly into a caller-provided `dirent64_t` buffer. It checks each record length, stops cleanly if the output buffer would overflow, updates `loff` from the decoded cookie, and returns the number of bytes filled.

`xdr_READDIRPLUS3vres()` extends this by also decoding each entry's post-op attributes and optional filehandle. When both are valid and the name is not `"."`, it creates or finds an NFS node with `makenfs3node_va()` and updates the DNLC. This makes XDR decode an active participant in client name-cache population.

## Safety Properties

Notable defensive behavior:

- String lengths are bounded and oversized strings are skipped rather than over-read.
- Optional booleans are validated as true/false in multiple places.
- Filehandle size and internal component sizes are validated.
- Attribute sizes and times can invalidate attributes without breaking full response decode.
- Directory decode stops before overflowing caller buffers.
- READ RDMA paths verify transferred lengths match protocol counts.
- WRITE RDMA clists are released in the FREE path.
- Server-side READDIR encoding respects response count limits.

## Dependencies

This file depends on:

- RPC/XDR core APIs and inline XDR macros.
- RDMA XDR support: `xdrrdma_ops`, `xdrrdmablk_ops`, RDMA chunk controls, clists.
- mblk XDR support: `xdrmblk_ops`.
- NFS vnode/rnode helpers, especially `makenfs3node_va()` and DNLC update for READDIRPLUS.
- NFS constants and conversion helpers such as `nf3_to_vt`, `NFS3_SIZE_OK`, `NFS3_TIME_OVERFLOW`, `nfs3tsize()`, and `nfs_allow_preepoch_time`.

## Research Notes

This file is a critical trust boundary. It converts untrusted network byte streams into kernel structures. The code is optimized for the common inline XDR path but contains fallback paths for stream types and allocation failures. The most important audit areas are filehandle validation, directory buffer accounting, RDMA count validation, `xdr_string3()` sentinel handling, and any path where invalid attributes must be ignored without desynchronizing the XDR stream.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs3_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acache.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acache.c

## Purpose

`nfs4_acache.c` implements the NFSv4 client access cache. It stores ACCESS results per `(rnode4_t, credential)` so repeated access checks can avoid unnecessary NFSv4 server calls when cached attributes are still valid.

This is a small, focused file. It owns the NFSv4 access-cache hash table, allocation cache, lookup/update logic, per-rnode purge, and module init/fini routines.

## Main Interfaces

Public functions:

- `nfs4_access_check(rnode4_t *rp, uint32_t acc, cred_t *cr)`
- `nfs4_access_cache(rnode4_t *rp, uint32_t acc, uint32_t resacc, cred_t *cr)`
- `nfs4_access_purge_rp(rnode4_t *rp)`
- `nfs4_acache_init(void)`
- `nfs4_acache_fini(void)`

Private helper:

- `acache4hash(rnode4_t *rp, cred_t *cred)`

## Data Structures

The global cache state is:

- `acache4`: array of hash buckets
- `nacache`: optional sizing override
- `acache4size` and `acache4mask`: power-of-two hash sizing and mask
- `acache4_cache`: `kmem_cache` for `acache4_t`
- `acache4_hashlen`: target average chain length
- `ACACHE4_SHIFT_BITS`: shifts rnode pointer bits before hashing, to avoid allocation-alignment noise

Each cache entry records:

- `known`: access bits for which the cache has an answer
- `allowed`: access bits allowed by the server
- `rnode`: owning NFSv4 rnode
- `cred`: held credential
- hash queue links
- per-rnode list link

The same entry is linked both into a global hash bucket and into `rp->r_acache`, enabling efficient lookup by hash and efficient purge by rnode.

## Lookup Behavior

`nfs4_access_check()` first refuses to use the cache if the vnode attribute cache is invalid or if a purge is pending/completing:

- `ATTRCACHE4_VALID(vp)` must be true.
- `nfs4_waitfor_purge_complete(vp)` must not require waiting/fail use.

If an access cache exists for the rnode, the function locks the relevant hash bucket as reader, searches for an entry whose credential compares equal with `crcmp()` and whose `rnode` matches, then returns:

- `NFS4_ACCESS_ALLOWED` when all requested bits are known and allowed.
- `NFS4_ACCESS_DENIED` when all requested bits are known but not all allowed.
- `NFS4_ACCESS_UNKNOWN` when no entry exists or requested bits are not fully known.

Debug counters track hits and misses.

## Update Behavior

`nfs4_access_cache()` records a server ACCESS answer. It preallocates a new cache entry with `KM_NOSLEEP` before taking the bucket writer lock. This avoids sleeping while holding the hash lock.

If an entry already exists for the same rnode and credential, it merges the new knowledge:

- `known |= acc`
- clears the newly checked bits from `allowed`
- applies `resacc` for the checked bits

If no entry exists and allocation succeeded, it inserts the entry into the hash bucket and links it into `rp->r_acache` under `r_statelock`. The credential is held with `crhold()` and later released during purge.

If allocation fails, the function silently skips caching; correctness falls back to future server ACCESS calls.

## Purge Behavior

`nfs4_access_purge_rp()` removes all access-cache entries for one rnode. It first detaches the per-rnode list under `r_statelock`, then iterates that detached list. For each entry, it takes the entry's hash bucket writer lock, unlinks the hash queue links, releases the credential, and frees the entry from `acache4_cache`.

This two-index design avoids a full global hash scan during rnode invalidation.

## Initialization And Finalization

`nfs4_acache_init()` sizes the hash table from `nacache` if set, otherwise from external `rtable4size`. It initializes each bucket as a circular doubly linked list with an `rwlock`, then creates the `nfs4_access_cache` kmem cache.

`nfs4_acache_fini()` destroys the kmem cache, destroys each bucket lock, and frees the hash table.

## Concurrency And Invariants

- Hash buckets use reader/writer locks.
- The per-rnode `r_acache` pointer is protected by `rp->r_statelock`.
- Entries are linked in both hash and rnode lists.
- Cached answers are only trusted while attribute cache state is valid.
- Credentials are reference-counted for the lifetime of cache entries.
- The code assumes cache finalization occurs after entries have been purged; `nfs4_acache_fini()` destroys the object cache directly.

## Dependencies

This file depends on:

- NFSv4 rnode/vnode conversion via `RTOV4()`.
- Attribute-cache validity macros and purge synchronization.
- Credential comparison and reference management: `crcmp`, `crhold`, `crfree`, `crgetuid`.
- illumos kernel allocation and synchronization primitives: `kmem_alloc`, `kmem_cache_*`, `rw_enter`, `rw_exit`, `mutex_enter`.

## Research Notes

The important behavior is the coupling between access-cache validity and attribute-cache validity. Access results are permission snapshots and are only safe while file attributes and purge state are current. Audit focus should be on purge ordering, dual-list unlink correctness, hash sizing, and callers ensuring `nfs4_access_purge_rp()` runs on permission-changing attribute updates.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acache.c -->