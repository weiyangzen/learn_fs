# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c lines 10242-10676

## Scope

This report covers `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c` lines 10242-10676 for subset A (`Docs/research_subset_a.md`). The chunk contains NFS referral support built on Solaris/illumos reparse points, compatibility handling for clients that cannot consume NFSv4 referrals, and the HA-NFSv4 resource-group failover reconciliation helper. Adjacent context shows the referral disable tunable `rfs4_no_referrals` immediately before the chunk and server-start failover callers earlier in the same file.

## Public And Internal APIs Covered

- `vn_find_nfs_record(vnode_t *vp, nvlist_t **nvlp, char **svcp, char **datap)` parses vnode reparse data into an `nvlist_t`, finds the first nvpair whose name begins with `NFS` case-insensitively, returns the service type and string data, and transfers ownership of the nvlist to the caller on success.
- `vn_is_nfs_reparse(vnode_t *vp, cred_t *cr)` is the boolean gate used by server paths to decide whether a vnode is an NFS referral point. It honors `rfs4_no_referrals`, verifies `vn_is_reparse()`, then probes for an NFS reparse record.
- `nfs4_create_components(char *path, component4 *comp4)` splits a path on `/`, NUL, or newline and optionally converts components to NFSv4 UTF-8. Comments require it to stay in sync with user-level `ref_subr.c`.
- `make_pathname4(char *path, pathname4 *pathname)` counts components, allocates a `component4` array, fills a `pathname4`, and returns the component count.
- `fetch_referral(vnode_t *vp, cred_t *cr)` resolves an NFS reparse point into an allocated `fs_locations4` by upcalling `reparse_kderef()`, decoding XDR `fattr4_fs_locations`, and setting `fs_root` from `vp->v_path`.
- `build_symlink(vnode_t *vp, cred_t *cr, size_t *strsz)` converts the first referral location and first server into a legacy `/net/<server>/<rootpath...>` symlink target.
- `client_is_downrev(struct svc_req *req)` maps an RPC caller address to `rfs4_clntip_t` and returns `ri_no_referrals`.
- `hanfsv4_failover(nfs4_srv_t *nsrv4)` reconciles current DSS paths with new `nfsd` resource-group paths, removes paths no longer served, creates a server instance for added paths, reads stable state, and resets grace periods.

## Control Flow And Behavior

- Referral detection checks `rfs4_no_referrals`, `vn_is_reparse()`, then `vn_find_nfs_record()`. Successful `vn_find_nfs_record()` callers own the returned nvlist and must call `reparse_free(nvl)`.
- Path conversion is two-pass: count non-empty components, allocate `component4[]`, then populate it. Empty components from repeated/leading slashes are skipped; newline terminates parsing.
- `fetch_referral()` uses a fixed 1024-byte stack buffer for `reparse_kderef()`, then decodes the daemon response with `xdr_fattr4_fs_locations`.
- `build_symlink()` only consumes `locations_val[0]` and `server_val[0]`, appends convertible rootpath components, frees the decoded referral, and returns the allocated symlink buffer.
- `client_is_downrev()` does not create missing client-IP records; absent state means “not downrev.”
- `hanfsv4_failover()` first removes missing paths from circular `nsrv4->dss_pathlist`, skipping `NFS4_DSS_VAR_DIR`. It then builds an `added_paths` array from unmatched `rfs4_dss_newpaths`, creates a new server instance if needed, reads DSS state, and restarts active grace periods.

## State And Data Structures

- Reparse state is an `nvlist_t`; returned `stype` and `sdata` point into that nvlist lifetime.
- Referral payloads use `fs_locations4`, `fs_location4`, `pathname4`, `component4`, and UTF-8 protocol wrappers. Nested memory is released by `rfs4_free_fs_locations4()`.
- Symlink compatibility uses transient `utf8_to_str()` buffers and a returned `kmem_zalloc()` string. `strsz` is the allocation size.
- HA state is held in `nfs4_srv_t::dss_pathlist`, circular `rfs4_dss_path_t` nodes, and each `rfs4_servinst_t::dss_paths`.
- New HA input comes from global `rfs4_dss_newpaths` / `rfs4_dss_numnewpaths`, assumed sorted and duplicate-free by `nfsd`.

## Dependencies

- VFS/reparse: `vn_is_reparse()`, `reparse_init()`, `reparse_vnode_parse()`, `reparse_free()`, nvlist/nvpair APIs, and `reparse_kderef()`.
- XDR/protocol: `xdrmem_create()`, `xdr_fattr4_fs_locations()`, `XDR_DESTROY()`, `str_to_utf8()`, `utf8_to_str()`.
- RPC/client state: `svc_getrpccaller()`, `rfs4_find_clntip()`, `rfs4_dbe_rele()`.
- HA-NFSv4: `NFS4_DSS_VAR_DIR`, `rfs4_servinst_create()`, `rfs4_dss_readstate()`, `rfs4_grace_reset_all()`, `insque()`/`remque()`.
- Cross-file consumers include NFSv2/v3 lookup/readlink paths, NFSv4 compound/readdir paths, and NFSv4 `fs_locations` attribute generation.

## Risks And Invariants

- `fetch_referral()` appears to leak the allocated `fs_locations4` wrapper if XDR decoding fails after `kmem_alloc()`.
- `fetch_referral()` frees the reparse nvlist before its DTrace probe references `stype` and `sdata`; those pointers are nvlist-owned.
- The 1024-byte referral buffer may fail for large referral payloads.
- `nfs4_create_components()` copies into `char buf[MAXNAMELEN]` without checking `slen < MAXNAMELEN`.
- `build_symlink()` assumes at least one location and one server in decoded data.
- `build_symlink()` sizes the destination from UTF-8 recorded lengths but concatenates converted strings, making length semantics important.
- `hanfsv4_failover()` assumes `dss_pathlist` is non-NULL and circular because `NFS4_DSS_VAR_DIR` is always present.
- Removal mutates the circular list while walking it; correctness depends on the default path never being removed and list invariants staying intact.
- Addition detection uses prefix comparison, unlike exact comparison for removals.
- The failover algorithm is documented as roughly `2 * O(n**2)` and has no visible local locking; it relies on higher-level server-start/reconfiguration serialization.

## Cross-Chunk References

- Earlier same-file `rfs4_do_server_start()` calls `hanfsv4_failover()` on warm clustered start; cold start reads `rfs4_dss_newpaths` directly.
- Earlier same-file helpers define `rfs4_grace_reset_all()`, `rfs4_dss_newpath()`, and `rfs4_servinst_create()`.
- Earlier NFSv4 compound paths use `vn_is_nfs_reparse()`, `client_is_downrev()`, and `build_symlink()` to choose moved/referral versus symlink compatibility behavior.
- `nfs4_srv_attr.c` calls `fetch_referral()` for `FATTR4_FS_LOCATIONS` and defines `rfs4_free_fs_locations4()`.
- `nfs4_srv_readdir.c` uses referral helpers while walking directories and encoding `fs_locations`.
- NFSv2/v3 server files also call `vn_is_nfs_reparse()` and `build_symlink()`, so these helpers serve legacy protocol compatibility as well as NFSv4.