# Research: subset-b-007123

Grouped research for GlusterFS NFS server files under `sources/distributed-fs/glusterfs/xlators/nfs/server/src`. Each section is wrapped for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.c

## Purpose

`nfs-inodes.c` wraps generic NFS FOP submission with NFS-specific inode table maintenance. It is the bridge between protocol handlers that issue create/open/link/unlink style operations and Gluster's inode/fd bookkeeping, so successful namespace mutations are reflected in the NFS xlator's inode cache before the original protocol callback is resumed.

## Important APIs, types, and functions

- `nfl_inodes_init()` stores inode, parent, newparent, name, and newname references into `struct nfs_fop_local`.
- `inodes_nfl_to_prog_data` restores the upper-layer callback/local state from the FOP-local wrapper and wipes the wrapper.
- `nfs_inode_create()`, `nfs_inode_mkdir()`, `nfs_inode_mknod()`, and `nfs_inode_symlink()` call the matching `nfs_fop_*` operation and link the returned inode into the parent on success.
- `nfs_inode_unlink()` and `nfs_inode_rmdir()` unlink and forget cached inodes after successful removal.
- `nfs_inode_rename()` updates the inode table using `inode_rename()`.
- `nfs_inode_link()` links an existing inode into a new parent.
- `nfs_inode_open()` and `nfs_inode_opendir()` allocate fds and forward open callbacks; `opendir` binds the fd on success while file opens leave binding to the higher fd-cache layer.

## Control flow

Each public wrapper validates its NFS xlator, target subvolume, loc/user inputs, allocates a `nfs_fop_local` via `nfs_fop_handle_local_init`, stores the protocol callback/local value, and submits the underlying FOP. Completion callbacks first inspect `op_ret`; on success they mutate the inode table with `inode_link()`, `inode_rename()`, `inode_unlink()`, or `inode_forget()`. The wrapper local is then converted back into the protocol callback context and the saved callback is invoked with the original FOP result. Link-like callbacks call `inode_lookup()` then `inode_unref()` on linked inodes to keep lookup counts coherent.

## State and persistence behavior

The file maintains only in-memory inode and fd state. It does not persist metadata itself; backend xlators perform the durable operation. Its state changes are references stored in `nfs_fop_local`, inode table links, lookup counts, and fd refs. Error paths wipe the local wrapper and unref newly created fds to avoid leaks.

## Dependencies and integration points

This file depends on `nfs-fops.h` for asynchronous FOP helpers, `nfs.h` for `nfs_user_t`, Gluster inode/fd APIs, `loc_t`, callback typedefs, and NFS message IDs. It is consumed by NFSv3 operation code that wants one call to perform both the backend FOP and NFS inode-cache repair.

## Risks and edge cases

- A few wipe calls pass `xl` instead of `nfsx`; if the wipe routine assumes the NFS xlator for mempool ownership, that is worth auditing.
- `nfs_inode_link_cbk()` stores `newloc->name` in `nfl->path` while using `nfl->newparent`; the naming works but is easy to misread.
- File `open` intentionally does not bind the fd, so callers must preserve the fd-cache invariant.
- Callback sequencing invokes the upper callback before the final linked-inode lookup/unref pair in create-like operations.

## Test signals

Useful tests cover successful and failed create/mkdir/mknod/symlink, rename across parents, hard link creation, unlink/rmdir cache removal, open/opendir fd lifetime on success and failure, and namespace operation callbacks receiving original FOP return values after cache repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.h

## Purpose

`nfs-inodes.h` declares the inode-aware NFS FOP wrapper API implemented by `nfs-inodes.c`. It gives protocol code a stable interface for issuing namespace and open operations while keeping the NFS inode table synchronized with backend results.

## Important APIs, types, and functions

The header exports wrappers for create, mkdir, open, rename, link, unlink, rmdir, symlink, opendir, mknod, and lookup. All wrappers take the NFS xlator, target subvolume, `nfs_user_t`, loc/name inputs, a Gluster FOP callback typedef, and caller-local data. `nfs_link_inode()` is declared as a direct inode link helper, although this implementation file mainly performs link operations internally through callbacks.

## Control flow

There is no runtime control flow in the header. Its signature pattern shows the intended call chain: NFS protocol handlers resolve a file handle to a `loc_t`, initialize an `nfs_user_t` from the RPC request, then call a wrapper. The wrapper submits a `nfs_fop_*` request and later resumes the protocol-specific callback.

## State and persistence behavior

The header owns no state. It defines ownership expectations through callback signatures: the wrappers may allocate transient FOP-local state and fds, while callers retain responsibility for protocol call state passed as `local`.

## Dependencies and integration points

It includes Gluster dict/iobuf types and `nfs-fops.h`, and relies on `nfs_user_t` from `nfs.h` being visible through included dependencies. It is included by NFSv3 helpers and operation handlers that need inode-maintaining wrappers rather than raw FOP calls.

## Risks and edge cases

Prototype drift is the main risk: callback typedefs must match lower-layer FOP callback shapes exactly. The presence of `nfs_inode_lookup()` in the header without an implementation in this file means its definition is elsewhere or stale, which should be checked during build/link validation.

## Test signals

Compile/link coverage is essential. Runtime signals are the same namespace mutation tests used for `nfs-inodes.c`, plus link-time detection for declared but missing APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-mem-types.h

## Purpose

`nfs-mem-types.h` assigns Gluster memory-accounting type IDs for the NFS translator and its protocol helpers. These IDs let allocations in mount, NFSv3, NLM, auth-cache, inode-context, and helper code be attributed under the NFS component in memory accounting and statedump output.

## Important APIs, types, and functions

The central type is `enum gf_nfs_mem_types_`, starting at `gf_common_mt_end + 1` and ending at `gf_nfs_mt_end`. Important entries include `gf_nfs_mt_nfs_state`, `gf_nfs_mt_nfs3_state`, `gf_nfs_mt_nfs3_fh`, `gf_nfs_mt_nfs_initer_list`, `gf_nfs_mt_xlator_t`, `gf_nfs_mt_inode_ctx`, auth-cache entries, NLM share/client structures, and generic `gf_nfs_mt_char`/`gf_nfs_mt_arr` utility buckets.

## Control flow

The header has no runtime control flow. It is consumed by allocation macros such as `GF_CALLOC`, `GF_MALLOC`, and mempool setup. `nfs.c` initializes accounting with `xlator_mem_acct_init(this, gf_nfs_mt_end)`, so every ID before `gf_nfs_mt_end` must remain valid.

## State and persistence behavior

Memory type IDs are process-local accounting metadata; they are not persisted. They influence diagnostics and leak attribution rather than behavior of the NFS protocol itself.

## Dependencies and integration points

The header depends on `<glusterfs/mem-types.h>` for the common base. It is included by `nfs.c`, `nfs3-helpers.c`, file-handle code, mount/NLM/auth modules, and any NFS allocation site that wants component-specific accounting.

## Risks and edge cases

- IDs must only be appended, not renumbered, if external diagnostics expect stable names.
- A missing or wrong allocation type will not usually break behavior, but it weakens leak and pressure analysis.
- `gf_nfs_mt_end` must remain the final enumerator passed to memory accounting initialization.

## Test signals

Build coverage catches duplicate or missing enum names. Runtime memory-accounting/statedump tests should show NFS allocations under expected buckets when NFS starts, serves requests, and shuts down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-messages.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-messages.h

## Purpose

`nfs-messages.h` defines the stable message ID catalog for the Gluster NFS component. Every `gf_msg()` call in the NFS, mount, NFSv3, NLM, ACL, auth, and helper code uses these IDs for structured logging.

## Important APIs, types, and functions

The `GLFS_MSGID(NFS, ...)` macro expands a long ordered list of `NFS_MSG_*` identifiers. The list covers decode failures, FOP failures, protocol registration, option parsing, subvolume startup, auth/export parsing, file-handle resolution, ACL/NLM events, statd/rpcbind behavior, and inode context errors. `NFS_MSG_UNUSED_*` placeholders preserve numeric stability.

## Control flow

There is no runtime control flow. The important operational rule is in the file comment: append new IDs, never delete or reuse old IDs. That preserves log ABI compatibility across releases and tools.

## State and persistence behavior

Message IDs become part of durable logs and external diagnostics. They do not store process state, but their numeric values are consumed after the process exits by log analysis and support tooling.

## Dependencies and integration points

The header depends on `<glusterfs/glfs-message-id.h>`. It is included across NFS server source files, including `nfs.c`, `nfs-inodes.c`, `nfs3-fh.c`, and `nfs3-helpers.c`. It also holds IDs used by adjacent NLM/mount/auth modules, so changes affect more than the ten files in this group.

## Risks and edge cases

- Removing or reordering IDs can corrupt the meaning of old and new logs.
- A generic ID such as `NFS_MSG_STAT_ERROR` is reused by many protocol result logs; excessive consolidation can make automated diagnosis less precise.
- New code should use the closest existing ID only when the semantic match is real.

## Test signals

Compile coverage verifies symbol availability. Logging tests and support tooling should confirm that expected NFS error paths emit the right component and message ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.c

## Purpose

`nfs.c` is the main Gluster NFS translator implementation. It initializes process-wide NFS state, configures the RPC service, registers MOUNT/NFSv3/NLM/ACL protocol programs, initializes per-subvolume inode tables, handles reconfiguration, and exposes xlator callbacks, dump operations, and volume options.

## Important APIs, types, and functions

- `nfs_init_state()` parses options and allocates `struct nfs_state`, the FOP-local mempool, gid cache, RPC service, auth/rmtab/statd settings, portmap registration policy, event-thread count, DRC prerequisites, and generation state.
- `nfs_add_all_initiators()`, `nfs_init_versions()`, `nfs_init_version()`, and `nfs_deinit_version()` manage protocol initializer records and RPC program registration.
- `nfs_init_subvolumes()` and `nfs_startup_subvolume()` create inode tables and perform root lookups before marking child xlators started.
- `nfs_user_create()`, `nfs_request_user_init()`, and `nfs_request_primary_user_init()` translate RPC credentials into `nfs_user_t`.
- `nfs_reconfigure_state()` and `reconfigure()` update live options and delegate to NFSv3, mount, RPC, and DRC reconfigure code.
- `init()`, `notify()`, and `fini()` are the xlator lifecycle entry points.
- `nfs_priv_to_dict()`, `nfs_priv()`, and `nfs_itable_dump()` support statedump/CLI inspection.
- `options[]` and `xlator_api` publish the translator's configuration and API.

## Control flow

`init()` calls `nfs_init_state()`, adds protocol initializers, initializes child inode tables, initializes mount and NLM state, registers protocol programs, initializes DRC, and reports service start. Child-up notifications call `nfs_startup_subvolume()`, which fills a root loc, issues a root lookup as root, and marks the subvolume started in a lock-protected `initedxl` array when the callback succeeds. Descendent up/down notifications increment `generation`, which is used by inode/share context consumers to detect topology changes.

Reconfigure first rejects options that require restart (`nfs.port`, transport type, mem-factor, and some unset transitions), then updates rmtab path, server aux-gids and gid-cache TTL, rdirplus, dynamic-volumes, ino32, NLM/ACL registration, event threads, NFSv3 state, mount state, RPC service options, portmap registration, outstanding RPC limits, and DRC configuration.

## State and persistence behavior

`struct nfs_state` is the central in-memory state. It tracks protocol versions, RPC service, mount/NFSv3/NLM state pointers, subvolume list, started-subvolume array, memfactor, auth settings, gid cache, statd paths, rmtab path, generation, and event-thread settings. Persistent side effects are indirect: rmtab is stored under `GLUSTERD_DEFAULT_WORKDIR/nfs/rmtab` by default unless disabled with `/-`; logs and portmap/rpcbind registrations outlive individual calls; backend filesystems hold actual export data.

## Dependencies and integration points

This file integrates Gluster xlator APIs, RPC service/DRC code, `mount3`, `nfs3`, `nlm4`, `acl3`, `nfs-fops`, gid cache, event pool, option parsing, memory accounting, and statedump. Its volume options are consumed by glusterd/CLI and downstream state initialization. NFSv3 helpers use `gf_nfs_this_private`/`gf_nfs_enable_ino32()` from `nfs.h`, so this file's private state must be initialized before protocol traffic.

## Risks and edge cases

- Partial failure cleanup is incomplete in several init branches: some allocated state is not fully deinitialized before returning failure.
- `nfs_startup_subvolume()` passes `nfsx->private` as the lookup cookie, but the callback treats `cookie` as an `xlator_t *` for logging while marking `this->private`; this looks suspicious and deserves targeted review.
- Live toggling of NLM/ACL registers or unregisters RPC programs and portmap entries; failures are logged but not deeply reconciled.
- `nfs.mem-factor` option validation in `options[]` allows up to 1024, wider than constants in `nfs.h`; code defaults to 15 but does not clamp the parsed value here.
- `fini()` unregisters protocols and frees `instance_name` but leaves several allocated substructures to version-specific cleanup or process teardown.

## Test signals

High-value tests include translator init with no children, normal multi-subvolume startup, root lookup failure, port override/portmap disabled, NLM disabled by option or invalid statd path, ACL/NLM live reconfigure, rmtab path disable/rewrite, dynamic-volumes and ino32 toggles, gid-cache reconfigure, event-thread reconfigure, and statedump of mount clients, DRC, NLM, and inode table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.h

## Purpose

`nfs.h` is the shared contract for the Gluster NFS translator. It defines global constants, the protocol initializer callback type, central `struct nfs_state`, per-inode NFS context, user credential representation, and public helpers used by NFS protocol modules.

## Important APIs, types, and functions

- `GF_NFS`, memory/concurrency defaults, inode LRU multiplier, event-thread bounds, dynamic-volume constants, export-auth defaults, and auth cache defaults define core sizing and behavior.
- `nfs_version_initer_t` and `struct nfs_initer_list` describe protocol registration entries.
- `struct nfs_state` stores versions, gid cache, locks, RPC service, mount/NFSv3/NLM states, FOP mempool, subvolume/startup state, rmtab/statd paths, runtime options, auth settings, generation, and event-thread count.
- `struct nfs_inode_ctx` stores per-inode share state and generation.
- `nfs_user_t` stores uid, primary plus auxiliary gids, lock owner, and peer identifier.
- Public helpers initialize users, check subvolume startup, fix groups, and start the RPC poller.

## Control flow

The header defines macro-level access patterns rather than executing control flow. `gf_nfs_this_private` assumes `THIS` is the NFS xlator and exposes the private state; `gf_nfs_enable_ino32()` is used by NFSv3 attribute conversion to decide whether to hash GFIDs into 32-bit inode numbers.

## State and persistence behavior

`struct nfs_state` is process-local and authoritative for live NFS behavior. It includes references to persistent-path settings (`rmtab`, statd pid file), but actual persistence is performed by mount/statd/RPC code. `generation` lets dependent inode contexts detect topology changes; `gid_cache` caches server-side auxiliary group lookups.

## Dependencies and integration points

The header includes RPC service types, Gluster dict/gidcache/lkowner types, and is included by most NFS server modules. It is the shared ABI between `nfs.c`, NFSv3 code, mount, NLM, ACL, FOP wrappers, and helpers.

## Risks and edge cases

- Macros tied to global `THIS` are convenient but fragile in async callbacks if `THIS` is not the expected xlator.
- `NFS_NGROUPS` is fixed to protocol limits plus one primary gid, so callers must reject longer aux lists.
- `struct nfs_state` has many ownership-bearing pointers; lifecycle cleanup is spread across modules.

## Test signals

Build coverage detects ABI drift. Runtime tests should verify uid/gid extraction, auxiliary group truncation/rejection, `enable_ino32` behavior, generation changes on graph notifications, and correct defaults for auth/cache/event-thread options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.c

## Purpose

`nfs3-fh.c` constructs, validates, logs, and formats Gluster NFSv3 file handles. File handles encode a Gluster identity marker, export identity, object GFID, and mount identity into the fixed-size NFSv3 handle layout.

## Important APIs, types, and functions

- `nfs3_fh_validate()` checks the `:OGL` identifier bytes.
- `nfs3_fh_init()` initializes the identifier and copies an `iatt` GFID into the handle.
- `nfs3_fh_build_indexed_root_fh()` builds a root handle whose export ID is the child xlator index.
- `nfs3_fh_build_uuid_root_fh()` builds a root handle using volume UUID and mount UUID for dynamic volumes.
- `nfs3_fh_is_root_fh()` compares the handle GFID with Gluster's root GFID.
- `nfs3_fh_build_child_fh()`, `nfs3_fh_build_parent_fh()`, and `nfs3_build_fh()` derive handles from parent/child state or an inode.
- `nfs3_fh_to_str()` and `nfs3_log_fh()` support diagnostics.
- `nfs3_fh_compute_size()` returns the static XDR size used by response helpers.

## Control flow

Handle builders initialize an empty struct, install the magic identifier, copy the object GFID, then copy either export index/UUID and mount ID from the parent or caller-provided arguments. Validation is intentionally shallow: it rejects non-Gluster handles by magic bytes, while volume mapping and stale detection happen later in NFSv3 resolve logic.

## State and persistence behavior

File handles are persistent client-visible tokens. The code itself stores no global state, but the bytes it emits can be cached by NFS clients across requests. The export ID scheme changes depending on `nfs.dynamic-volumes`: index-based handles are tied to child order, UUID-based handles are stable across dynamic volume changes.

## Dependencies and integration points

The file depends on `xdr-nfs3.h`, `nfs3-fh.h`, Gluster UUID/iatt utilities, and `nfs_xlator_to_xlid()` from NFS common code. Its output is consumed by NFSv3 replies, mount replies, readdirplus entries, and handle-resolution helpers.

## Risks and edge cases

- `nfs3_fh_hash_entry()` is declared in the header but not implemented here, suggesting stale API or another implementation to verify.
- `nfs3_fh_build_parent_fh()` copies export ID but not mount ID, unlike child handle construction.
- `nfs3_fh_validate()` only checks magic bytes; callers must still validate export and GFID.
- The packed struct must remain exactly `NFS3_FHSIZE`; size changes can break XDR decoding.

## Test signals

Tests should validate fixed handle size, magic validation, root GFID detection, indexed and UUID root handle encoding, child/parent export propagation, string formatting, and compatibility of handles across mount, lookup, and readdirplus flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.h

## Purpose

`nfs3-fh.h` defines the wire-compatible Gluster NFSv3 file-handle structure and builder/validator API. It fixes the handle layout used by mount, lookup, readdirplus, and all NFSv3 operations that identify files by opaque NFS handles.

## Important APIs, types, and functions

`struct nfs3_fh` is a packed 64-byte handle containing four identifier bytes, `exportid`, object `gfid`, `mountid`, and padding. Macros define the magic bytes, static size, static initializer, and index extraction from `exportid[15]`. Prototypes cover compute size, hash entry, validation, indexed/UUID root builders, root detection, child/parent handle derivation, logging, formatting, and inode-based handle construction.

## Control flow

The header has no runtime control flow. It encodes the expected handle lifecycle: create a root handle for an export, derive child handles from attributes returned by lookup/create/readdirplus, validate handles on incoming requests, then map export ID plus GFID back to a subvolume and inode.

## State and persistence behavior

The struct layout is a persistent client-facing ABI. NFS clients treat it as opaque but may cache it for long periods, so identifier, export ID, GFID, and mount ID semantics must remain stable. Dynamic-volume mode relies on UUID export IDs; non-DVM mode relies on subvolume index in the final export ID byte.

## Dependencies and integration points

The header includes NFSv3 XDR definitions, Gluster `iatt`, UUID compatibility, and xlator list types. It is included by `nfs3.h`, mount code, helper code, and file-handle implementation.

## Risks and edge cases

- Any change to `struct nfs3_fh` must preserve `NFS3_FHSIZE`.
- The index macro reads only `exportid[15]`, limiting non-DVM indexed exports to one byte of identity.
- Declared functions must stay synchronized with implementations; currently `nfs3_fh_hash_entry()` needs link verification.

## Test signals

Static assertions or tests should confirm size and field offsets. Runtime tests should cover stale/invalid handles, root handles under both export schemes, and readdirplus handle decode by a client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-fh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.c

## Purpose

`nfs3-helpers.c` is the NFSv3 protocol utility layer. It converts Gluster/POSIX metadata and errors into NFSv3 XDR structures, prepares decode buffers to avoid SunRPC heap churn, builds READDIR/READDIRPLUS lists, maps logging severity, resolves file handles to `loc_t`, and checks export authorization for NFS operations.

## Important APIs, types, and functions

- Error/attribute conversion: `nfs3_errno_to_nfsstat3()`, `nfs3_cbk_errno_status()`, `nfs3_stat_to_fattr3()`, `nfs3_stat_to_post_op_attr()`, `nfs3_stat_to_pre_op_attr()`, and `nfs3_stat_to_wcc_data()`.
- Inode/device mapping: `nfs3_iatt_gfid_to_ino()` honors `nfs.enable-ino32`; `nfs3_map_deviceid_to_statdev()` sets `ia_dev`.
- XDR argument preparation: many `nfs3_prep_*args()` functions pre-seed handle/name pointers before decode.
- Reply filling: `nfs3_fill_*res()` functions populate lookup/getattr/fsinfo/access/readdir/fsstat/create/setattr/mkdir/symlink/readlink/mknod/remove/rmdir/link/rename/read/write/commit/pathconf responses.
- Directory helpers: `nfs3_fill_entry3()`, `nfs3_fill_entryp3()`, `nfs3_free_readdir3res()`, `nfs3_free_readdirp3res()`, and cookie verification.
- Logging: per-operation loglevel functions, `nfs3_loglevel()`, and `nfs3_log_*_call/res()` helpers.
- Resolution/auth: `nfs3_fh_resolve_and_resume()`, root/inode/entry hard-resolution callbacks, and `nfs3_fh_auth_nfsop()`.

## Control flow

Protocol handlers typically prepare argument structs, decode RPC XDR, validate/map a file handle, initialize call state, and call `nfs3_fh_resolve_and_resume()`. Resolution starts with root lookup if needed, then either resolves an inode by GFID or an entry by parent GFID plus basename. It first tries inode-table state and falls back to hard lookup using `nfs_gfid_loc_fill()` or `nfs_entry_loc_fill()`. Completion callbacks update `resolve_ret`, copy stats, link inodes into the table, fix generation context, and resume the original operation callback.

Reply helpers are mostly straight-line: zero the result, set status, return early on failure, map device IDs into stats, convert attrs/WCC data, attach file handles, and set NFS constants such as FSINFO sizes or PATHCONF limits. READDIR builders walk Gluster `gf_dirent_t` lists until the requested count/maxcount is reached and allocate NFS entry chains that must later be freed.

## State and persistence behavior

The file maintains transient per-request state through `nfs3_call_state_t`; persistent protocol identity remains in file handles and inode-table entries. It mutates inode-table state during hard resolution and readdirplus handle generation. It uses root-looked-up flags in `nfs3_state` to avoid repeated root lookups. It does not write durable storage.

## Dependencies and integration points

Dependencies include NFSv3 XDR types, `nfs3.h`, file-handle code, `nfs-fops`, inode wrappers, generic loc helpers, mount auth, Gluster iatt/list/memory/logging utilities, and RPC request/transport APIs. It is called heavily by `nfs3.c` operation handlers and feeds all NFSv3 wire responses.

## Risks and edge cases

- `nfs3_extract_nfs3_fh()` copies `data_len` bytes into a fixed struct without an explicit size check in this helper; callers must validate decoded handle size.
- READDIR sizing is approximate and allocates one object per entry; partial allocation failure returns a shorter list without an explicit error status.
- `nfs3_fh_to_post_op_fh3()` allocates a copied handle and depends on the matching free helper for READDIRPLUS.
- Cookie verification intentionally does not enforce `cookieverf == fd_t address` because of VMware client behavior, weakening stale-cookie detection.
- Resolution has multiple async branches where a failure becomes `EFAULT` if helper return values are unexpected.
- The per-operation loglevel tables are large and duplicated; future status additions can drift across operations.

## Test signals

Tests should cover errno-to-NFS status mapping, zero-filled stat suppression, ino32 hashing, all major reply fillers, WCC data, create/setattr mode translation, READDIR/READDIRPLUS list construction and cleanup, root `.`/`..` inode funging, cookie verification, invalid/stale handle paths, hard GFID and entry resolution, root lookup caching, export auth failures returning access/rofs semantics, and loglevel selection for expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3-helpers.h -->
