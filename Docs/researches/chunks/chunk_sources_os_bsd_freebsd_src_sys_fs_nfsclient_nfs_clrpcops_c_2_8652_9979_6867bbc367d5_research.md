# Chunk Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c lines 8652-9979

## Scope

This chunk covers the tail of `nfsrpc_createlayout()` plus pNFS layout-result handling, NFSv4.2 server-side copy/clone/seek RPCs, NFSv4 extended attribute RPCs, an `M_EXTPG`-aware mbuf splitter, NFSv4.1 `BIND_CONN_TO_SESSION`, `OPENATTR`, and a locked-vnode statfs refresh helper. The file is part of `sources/os/bsd/freebsd-src`, which is included by `Docs/research_subset_a.md`.

The range starts inside `nfsrpc_createlayout()`. Lines before this chunk build the beginning of the NFSv4 compound create/open request; this chunk begins at the open claim filename and covers reply parsing and cleanup.

## APIs and Entry Points

- `nfsrpc_createlayout(...)`: static pNFS create helper; appends `SAVEFH`, `GETFH`, file `GETATTR`, directory `PUTFH`/`GETATTR`, `RESTOREFH`, and `LAYOUTGET`, then parses open/delegation state, file/directory attrs, open state, and layout data.
- `nfsrpc_getcreatelayout(...)`: create-path pNFS wrapper; chooses flexfile or file layout, sizes layout reply from MDS session cache, and calls `nfsrpc_layoutgetres()`.
- `nfsrpc_layoutgetres(...)`: resolves layoutget results, handles unsupported layout-type fallback/disable, fetches missing device info, and installs layout state.
- `nfsrpc_copy_file_range(...)` / `nfsrpc_copyrpc(...)`: exported wrapper plus NFSv4.2 `COPY` compound marshalling/parsing, stateid handling, retry/recovery, offset advancement, write-verifier, and commit tracking.
- `nfsrpc_clone(...)` / `nfsrpc_clonerpc(...)`: clone/offload wrapper plus NFSv4.2 `CLONE` compound handling.
- `nfsrpc_seek(...)` / `nfsrpc_seekrpc(...)`: NFSv4.2 `SEEK` wrapper and compound worker.
- `nfsrpc_getextattr()`, `nfsrpc_setextattr()`, `nfsrpc_rmextattr()`, `nfsrpc_listextattr()`: NFSv4 named-attribute operations with follow-up `GETATTR`.
- `nfsm_split(...)`: splits ordinary mbuf chains via `m_split()` and manually splits `M_EXTPG` external-page mbufs.
- `nfsrpc_bindconnsess(...)`: reconnect-layer NFSv4.1 `BIND_CONN_TO_SESSION`.
- `nfsrpc_openattr(...)`: sends `OPENATTR`, optionally creating the named-attribute directory.
- `nfscl_statfs(...)`: locked-vnode statfs/fsinfo/lease refresh helper.

## Control Flow

`nfsrpc_createlayout()` completes the create/open compound, sends it, increments the open-owner sequence id, parses returned open stateid and delegation, obtains the created file handle and attributes, reloads parent directory attributes, creates local open state with `nfscl_open()`, then parses `RESTOREFH`/`LAYOUTGET`. A successful create/open can return a layout failure only through `laystat`, not as the function error.

`nfsrpc_getcreatelayout()` calls `nfsrpc_createlayout()` and routes the layout status through `nfsrpc_layoutgetres()`. On successful layout installation it releases the referenced/shared-locked layout with `nfscl_rellayout()`.

`nfsrpc_layoutgetres()` clears `NFSSTA_FLEXFILE` to fall back from flexfile to file layout on `NFSERR_UNKNLAYOUTTYPE`, or disables pNFS entirely for unsupported file layout. On success it walks layout segments and mirrors, binds or fetches device info, and calls `nfscl_layout()`.

Copy/clone/seek wrappers all acquire NFSv4 stateids, call the worker RPC, drop returned state locks, sleep/retry on grace/delay/stale/bad-session/old-stateid classes, trigger recovery on stale stateids, check client expiration, and eventually convert persistent failures to `EIO`.

The extattr RPCs all append `GETATTR` for cache refresh. `listextattr` converts server names into FreeBSD extattr list format by prefixing each name with a one-byte length and tracks truncation with `*eofp = false`.

`nfsm_split()` handles external-page mbufs by locating the split page, allocating a new ext-pg mbuf, copying trailing bytes into a fresh wired page for intra-page splits, moving later page references, and fixing lengths/links.

## State and Synchronization

- Mutates open-owner seqid, delegation flags/state, open stateids, attr flags, layout status, and returned file handles.
- Delegation allocation is owned locally until success assigns `*dpp`; error paths free it.
- pNFS capability flags are changed under `NFSLOCKMNT()`.
- Copy write verifier state is updated under `NFSLOCKMNT()`.
- `nfscl_statfs()` updates lease renewal under `NFSLOCKCLSTATE()` and mount fs/stat data under `nm_mtx`.
- Copy/clone/seek state locks from `nfscl_getstateid()` are released with `nfscl_lockderef()` every attempt.

## Dependencies

Depends on FreeBSD NFS client XDR/RPC helpers: `NFSCL_REQSTART`, `nfscl_reqstart`, `NFSM_BUILD`, `NFSM_DISSECT`, `nfsm_strtom`, `nfsm_fhtom`, `nfsm_stateidtom`, `nfsm_uiombuf`, `nfsm_mbufuio`, `nfsm_advance`, `nfsm_loadattr`, `nfsm_getfh`, `nfscl_postop_attr`, `nfsrv_putattrbit`, `nfsrv_getattrbits`, `nfsrv_setuplayoutget`, `nfsrv_parselayoutget`, `nfsrv_dissectace`, `nfscl_request`, and `newnfs_request`.

Also depends on NFS client state helpers (`nfscl_getstateid()`, `nfscl_open()`, `nfscl_openrelease()`, `nfscl_layout()`, `nfscl_adddevinfo()`, `nfsrpc_getdeviceinfo()`, recovery/expiration helpers), vnode/mount/uio/credential infrastructure, mbuf and VM-page APIs, and NFSv4.1/v4.2 protocol constants.

## Risks and Edge Cases

- The range starts mid-function; correctness depends on previous-chunk compound op count and open/create setup.
- Layoutget failure after successful create/open is intentionally non-fatal and only affects layout availability.
- `nfsrpc_getcreatelayout()` returns the create/open error, not the layout status, even though layout fallback/disable may occur.
- `nfsrpc_copyrpc()` requires synchronous copy support and rejects asynchronous behavior with `NFSERR_NOTSUPP`.
- `nfsrpc_clonerpc()` encodes clone-to-EOF as zero length but does not update `*lenp` on success; wrapper offset advancement depends on caller-provided length.
- `nfsrpc_seekrpc()` appears able to overwrite a local `nfsm_loadattr()` error with `nd_repstat`.
- `listextattr` assumes extattr names fit in a single `u_char` length prefix.
- `nfsm_split()` can panic on inconsistent `M_EXTPG` accounting and transfers page physical addresses without clearing moved slots in the original mbuf.
- `nfsrpc_bindconnsess()` only frees reply mbufs on visible paths; request ownership depends on RPC call contract.

## Cross-Chunk References

- Previous chunk contains the beginning of `nfsrpc_createlayout()` and related open-layout logic.
- Earlier layout paths call `nfsrpc_layoutgetres()` for normal layoutget/open layout results.
- Earlier write paths call `nfsm_split()` when splitting transfer mbuf chains.
- Earlier reconnect setup stores `nfsrpc_bindconnsess` as the reconnect callback.
- `nfs_clvnops.c` calls exported RPCs here from VOP copy/clone, seek, extattr, and openattr paths.
- `nfs_var.h` declares the exported copy, clone, seek, extattr, and openattr RPC entry points.