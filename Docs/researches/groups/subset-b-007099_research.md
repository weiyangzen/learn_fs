# subset-b-007099 research

Grouped research for GlusterFS feature translators: simple-quota, snapview-client, snapview-server, and thin-arbiter build metadata.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.c -->
# sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.c

Purpose: implements the experimental `simple-quota` translator. It sits above one child translator, tracks quota consumption per namespace inode, exposes adjusted `statfs`, rejects space-consuming fops with `EDQUOT`, and persists usage through quota xattrs unless backend quota mode is enabled.

Important APIs/functions: `sync_data_to_disk()` drains `sq_inode_t.pending_update` into `SQUOTA_SIZE_KEY` with `syncop_setxattr`; `sync_data_from_priv()` flushes all namespace contexts on parent-down notification. `sq_set_ns_hardlimit()`, `sq_update_hard_limit()`, `sq_update_namespace()`, `sq_update_total_usage()`, and `sq_update_brick_usage()` create/update inode contexts. `sq_check_usage()` compares `hard_lim` against cached size plus pending deltas. Fops include `sq_lookup`, `sq_statfs`, `sq_setxattr`, `sq_writev`, `sq_create`, `sq_mkdir`, `sq_unlink`, `sq_rename`, `sq_truncate`, `sq_ftruncate`, `sq_fallocate`, `sq_discard`, and pass-through callback pairs. `init`, `reconfigure`, `notify`, `fini`, `fops`, `cbks`, `options`, and `xlator_api` export the translator.

Control flow: lookup requests add `SQUOTA_LIMIT_KEY` and `SQUOTA_SIZE_KEY` probes for first directory validation; the callback only honors quota xattrs when `GF_NAMESPACE_KEY` is present and then stores hard-limit state on the namespace inode. Mutating fops take a namespace inode reference in `frame->local`, wind to the child, then callback updates quota deltas from pre/post block counts or explicit estimates. `writev`, `create`, `mkdir`, and `fallocate` pre-check proposed growth. `unlink` and `rename` request child xdata for link count and block count to subtract overwritten/deleted file size only when link count indicates final removal. `statfs` tags xdata with `simple-quota`, optionally flushes pending updates for quota-helper clients, and rewrites block/free counts to reflect the namespace hard limit.

State/persistence: `sq_private_t` stores global flags and a locked `ns_list` of `sq_inode_t`. Each `sq_inode_t` lives in inode context and stores hard limit, persisted xattr size, pending atomic delta, current total size, and namespace inode pointer. Persistence uses `SQUOTA_SIZE_KEY`; command xattrs include `glusterfs.quota.total-usage`, `glusterfs.quota.total-files`, `glusterfs.quota.reset`, and `glusterfs.quota.disable-check`. Backend quota mode bypasses local xattr persistence. `forget` removes contexts from the private list and frees them; `notify(GF_EVENT_PARENT_DOWN)` flushes pending updates.

Dependencies/integration: depends on GlusterFS xlator, inode/fd context, dict, syncop, atomic, iatt, and namespace inode conventions. It expects server/protocol or lower xlators to provide namespace markers and block/link-count xdata. Options are `pass-through`, `use-backend`, and `cmd-from-all-client`; op version is GD_OP_VERSION_11_0 and category is experimental.

Risks/test signals: quota math is approximate and comments note missing locking around `sq_check_usage`. `create` checks 4096 bytes but only adds 512 bytes, while rmdir/mkdir accounting is disabled in comments. `sync_data_to_disk()` re-adds pending deltas on allocation/dict/setxattr failure, so tests should cover retry and negative-total reset. Permission checks for command xattrs are commented out, guarded mainly by namespace checks and `cmd-from-all-client`. Tests should exercise namespace lookup discovery, statfs aggregation, over-limit write/create/fallocate denial, unlink/rename decrements with xdata, backend mode, reset/allow-fops commands, parent-down flush, and forget cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.h -->
# sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.h

Purpose: declares private state used by the simple-quota translator.

Important types: `sq_private_t` contains a translator lock, an unused/thread placeholder `quota_set_thread`, the `ns_list` of namespace quota contexts, and booleans controlling distribute/backend behavior, command acceptance, and fop allowance. `sq_inode_t` is stored in inode context; it links into the private list, points to the namespace inode, tracks atomic pending updates, xattr-backed size, hard limit, total size, and backend file-count usage.

Control flow/state: the C implementation allocates `sq_inode_t` on lookup/setxattr/statfs paths, attaches it to an inode, and links it into `sq_private_t.ns_list` for later flush. `pending_update` is the hot update path; `xattr_size` is the last persisted base. `hard_lim` controls enforcement, and `total_size` is used for statfs/check comparisons.

Dependencies/integration: relies on GlusterFS `gf_lock_t`, `list_head`, `inode_t`, and `gf_atomic_t` definitions from included project headers. It is intentionally not a public library header; it is consumed by `simple-quota.c`.

Risks/test signals: ownership of `ns` is subtle because the struct stores raw inode pointers while fops also take refs in `frame->local`. Tests should look for forget/flush races, list integrity, and correct pending_update behavior after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/Makefile.am

Purpose: top-level Automake file for the snapview-client feature translator.

Important declarations: `SUBDIRS = src` delegates all build work to the `src` directory.

Control flow/state: no runtime control flow or persisted state. Build traversal is the only behavior.

Dependencies/integration: integrates the translator into the parent GlusterFS feature-xlator build by recursing into `src`.

Risks/test signals: low risk; build-system tests should confirm `make dist`, recursive build, and clean targets include this subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/Makefile.am

Purpose: builds the `snapview-client.la` xlator module from `snapview-client.c`.

Important declarations: installs the module under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`, uses `-module $(GF_XLATOR_DEFAULT_LDFLAGS)`, links `libglusterfs.la`, and ships private headers `snapview-client.h`, `snapview-client-mem-types.h`, and `snapview-client-messages.h`. Include paths cover libglusterfs and rpc/xdr generated/source directories.

Control flow/state: no runtime behavior; it defines compile/link inputs and warning flags.

Dependencies/integration: depends only on libglusterfs at link time. It does not link libgfapi because the client side routes fops to children rather than reading snapshots directly.

Risks/test signals: build failures would show as missing xlator symbols, missing generated XDR include paths, or mismatched private headers. Validate with configured builds and module install path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-mem-types.h

Purpose: assigns memory accounting IDs for snapview-client allocations.

Important APIs/types: `enum svc_mem_types` starts at `gf_common_mt_end + 1` and defines `gf_svc_mt_svc_private_t`, `gf_svc_mt_svc_fd_t`, and `gf_svc_mt_end`.

Control flow/state: no control flow. The enum is consumed by `GF_CALLOC`, `mem_pool_new`, and `xlator_mem_acct_init` in the implementation.

Dependencies/integration: includes `glusterfs/mem-types.h` and must stay consistent with allocations in `snapview-client.c`.

Risks/test signals: adding allocated structures without adding accounting IDs reduces diagnostic precision. Tests should ensure `mem_acct_init()` succeeds and allocation tags remain below `gf_svc_mt_end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-messages.h

Purpose: centralizes structured message IDs and common message strings for snapview-client logging.

Important APIs/types: `GLFS_MSGID(SNAPVIEW_CLIENT, ...)` reserves IDs for memory failures, inode/fd context failures, dict errors, graph lookup failures, invalid options, special-directory handling, read-only snapshot write attempts, and mem-pool failures. The file also defines string macros such as `SVC_MSG_NORMAL_GRAPH_LOOKUP_FAIL_STR`, `SVC_MSG_INVALID_ENTRY_POINT_STR`, and `SVC_MSG_LINK_SNAPSHOT_ENTRY_STR`.

Control flow/state: no runtime state. The message IDs are referenced by `gf_smsg`/`gf_msg` calls in `snapview-client.c`.

Dependencies/integration: includes `glusterfs/glfs-message-id.h`; comments require appending new IDs and never reusing/removing IDs to preserve log compatibility.

Risks/test signals: changing ID order can break log tooling. Spelling errors in strings are non-functional but visible. Tests should include compile coverage and log-message stability checks when adding new diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.c -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.c

Purpose: implements the maintained `snapview-client` translator. It presents a configured snapshot entry directory, routes normal filesystem operations to its first child, routes snapshot/virtual operations to its second child (`snapview-server`), and enforces read-only behavior for snapshot paths.

Important APIs/functions: context helpers `svc_inode_ctx_get/set`, `svc_fd_ctx_get_or_new`, and `svc_local_free` manage inode/fd/frame-local state. `gf_svc_get_entry_point()` copies `private->path` under lock for reconfigure safety. Core fops are `gf_svc_lookup`, `gf_svc_statfs`, `gf_svc_stat`, `gf_svc_fstat`, `gf_svc_opendir`, `gf_svc_getxattr`, `gf_svc_setxattr`, `gf_svc_fsetxattr`, `gf_svc_mkdir`, `gf_svc_mknod`, `gf_svc_open`, `gf_svc_create`, `gf_svc_symlink`, `gf_svc_unlink`, `gf_svc_readv`, `gf_svc_readlink`, `gf_svc_access`, `gf_svc_readdir`, `gf_svc_readdirp`, `gf_svc_rename`, `gf_svc_link`, `gf_svc_removexattr`, `gf_svc_fsync`, and `gf_svc_flush`. Lifecycle exports include `init`, `reconfigure`, `fini`, `notify`, and `mem_acct_init`.

Control flow: lookup first tries to determine inode and parent type from inode context. Root and unknown nameless lookups go to the normal child; named lookups matching the configured entry point go to the snapview child and may add xdata `"entry-point"="true"` when entering from a normal parent. Lookup callback sets inode context as `NORMAL_INODE` or `VIRTUAL_INODE`; if a gfid lookup fails on the normal graph with ENOENT/ESTALE and no context exists, it retries on the snapview graph. Most read/stat fops route by inode context. Mutating fops permit only normal graph targets and unwind virtual/snapshot attempts with `EROFS` or `EINVAL`.

State/persistence: `svc_private_t` stores the snapshot directory name, Samba special directory, a show-entry flag, and a lock. Inode context stores `NORMAL_INODE` or `VIRTUAL_INODE`. `svc_fd_t` stores the last readdir offset and whether a synthetic entry point has been returned for Samba special-directory handling. There is no on-disk state; all routing state is per-process and can be rebuilt through lookup/readdirp.

Dependencies/integration: requires exactly two children, with first child the normal graph and second child the snapview-server graph. It uses GlusterFS stack macros, inode/fd context APIs, dict/xdata, gf_dirent helpers, and structured log IDs. Options are `snapshot-directory` (default `.snaps`, must begin with `.`), `snapdir-entry-path` (not reconfigurable), and `show-snapshot-directory`.

Risks/test signals: inode context loss after graph change/client restart is explicitly handled only in selected lookup paths. Race control around `private->path` depends on always using `gf_svc_get_entry_point()`. Readdirp special-directory code mutates loc/inode/xdata and has ESTALE retry behavior; it needs Samba/NFS coverage. Tests should cover entry-point lookup, normal `.snaps` filtering, virtual read-only enforcement, gfid nameless fallback, statfs path rewrite for virtual entry point, get-real-filename xattr behavior, reconfigure of snapshot-directory, child notification filtering, and fd/inode context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.h

Purpose: declares snapview-client frame-local, private, fd-context, and inode-type data structures plus helper macros.

Important APIs/types: `svc_local_t` stores copied loc, chosen subvolume, fd, cookie, xdata, and revalidation flag. `SVC_STACK_UNWIND` unwinds and frees local state. `SVC_ENTRY_POINT_SET` ensures xdata exists and marks entry-point lookup for snapview-server. `SVC_GET_SUBVOL_FROM_CTX` fetches inode type and maps it to a child. `svc_private_t` stores entry-point configuration and lock. `svc_fd_t` stores readdir offset/special-dir flags. `inode_type_t` declares `NORMAL_INODE` and `VIRTUAL_INODE`. `gf_svc_special_dir_revalidate_lookup()` is exposed for callback reuse.

Control flow/state: macros are central to error paths and memory cleanup. The local struct is allocated from `this->local_pool`, while fd/private structs use memory accounting types.

Dependencies/integration: includes GlusterFS base, logging, dict, defaults, and the local mem/message headers. It assumes the translator has exactly two children and that inode contexts contain values from `inode_type_t`.

Risks/test signals: macro gotos require callers to have matching local variable names and labels. Tests should cover error unwinds to ensure `svc_local_free()` releases loc/fd/xdata exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-client/src/snapview-client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/Makefile.am

Purpose: top-level Automake file for the snapview-server feature translator.

Important declarations: `SUBDIRS = src` recurses into the implementation directory.

Control flow/state: no runtime behavior or persistence.

Dependencies/integration: connects snapview-server to the parent feature-xlator build.

Risks/test signals: low risk; recursive build and distribution checks should ensure `src` is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/Makefile.am

Purpose: builds the `snapview-server.la` xlator module when `WITH_SERVER` is enabled.

Important declarations: sources are `snapview-server.c`, `snapview-server-mgmt.c`, and `snapview-server-helpers.c`. The module links `libglusterfs.la`, `libgfapi.la`, readline libs, `libgfxdr.la`, and `libgfrpc.la`. Include paths cover libglusterfs, api, rpc-lib, rpc/xdr source and build directories. `DATADIR` is defined from `$(localstatedir)` for snapshot log paths.

Control flow/state: build-only file; the conditional protects server-only builds.

Dependencies/integration: integration point for libgfapi and management RPC dependencies used by the implementation.

Risks/test signals: missing `WITH_SERVER`, XDR, gfapi, or rpc libs will break module build. Tests should cover server-enabled and server-disabled configure paths and installed xlator location.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-helpers.c

Purpose: provides shared inode/fd context management, virtual gfid/iatt helpers, snapshot-list lookup, lazy libgfapi initialization, and snapshot-handle validation for snapview-server.

Important APIs/functions: `svs_inode_ctx_get/set/get_or_new`, `svs_fd_ctx_get/set/get_or_new`, `svs_inode_new`, and `svs_fd_new` allocate and attach `svs_inode_t`/`svs_fd_t`. `svs_uuid_generate()` deterministically generates virtual gfids from snapshot name plus origin gfid. `svs_iatt_fill()` builds synthetic directory attributes; `svs_fill_ino_from_gfid()` maps gfid to inode number. `__svs_get_snap_dirent()`, `svs_get_latest_snap_entry()`, `svs_get_latest_snapshot()`, `svs_initialise_snapshot_volume()`, `svs_inode_ctx_glfs_mapping()`, and `svs_inode_glfs_mapping()` support snapshot instance lookup and validation.

Control flow: fd context creation can open anonymous fds from an inode context using `glfs_h_opendir` or `glfs_h_open`. Snapshot volume initialization is protected by `snaplist_lock`, finds the named `snap_dirent`, creates `glfs_new("/snaps/...")`, chooses the volfile server from process command args or localhost, sets snapshot-specific logging, calls `glfs_init`, and caches `glfs_t` in the dirent. Mapping helpers reject stale `glfs_t` pointers by checking them against the current snap list.

State/persistence: contexts are in memory only. `snap_dirent_t.fs` caches live libgfapi handles. Synthetic gfids are generated from stable names/origin gfids, while synthetic iatt timestamps are fixed at zero. No on-disk data is written by helpers except libgfapi logging configuration.

Dependencies/integration: uses GlusterFS inode/fd context locking, gfapi handle APIs, rpc/protocol headers, `DEFAULT_SVD_LOG_FILE_DIRECTORY`, and private mem types. It relies on `svs_private_t.dirents` being refreshed by management RPC.

Risks/test signals: stale snapshot names reused after deletion are a known risk mitigated by handle validation. Error cleanup closes glfs handles on failures, but ownership is delicate when fd context set fails. Tests should cover repeated snapshot refresh, deletion/recreation with same name, anonymous fd open for NFS paths, deterministic gfid generation, invalid volfile server fallback, glfs_init failure cleanup, and forget/release interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mem-types.h

Purpose: defines memory accounting IDs for snapview-server allocations.

Important APIs/types: `enum snapview_mem_types` starts at `gf_common_mt_end + 1` and defines tags for private state, inode contexts, dirent arrays, fd contexts, and `gf_svs_mt_end`.

Control flow/state: no executable behavior; allocation tags are consumed by `GF_CALLOC` and initialized through `xlator_mem_acct_init(this, gf_svs_mt_end)`.

Dependencies/integration: includes `glusterfs/mem-types.h` and must match allocations in server, helper, and management code.

Risks/test signals: adding new persistent allocations without a tag weakens leak accounting. Compile and memory-accounting init tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-messages.h

Purpose: declares structured log message IDs for snapview-server.

Important APIs/types: `GLFS_MSGID(SNAPVIEW_SERVER, ...)` covers memory/accounting failures, null/stale gfids, snapshot-list refresh, glfs context/handle failures, inode/fd context errors, xattr/listxattr failures, release/open/read/stat/access/readlink failures, credential-setting failures, RPC setup/submission/XDR failures, dict errors, and glfs initialization/logging/volfile-server failures.

Control flow/state: no runtime state. IDs are consumed throughout `snapview-server.c`, `snapview-server-helpers.c`, and `snapview-server-mgmt.c`.

Dependencies/integration: includes `glusterfs/glfs-message-id.h`. The comment requires appending IDs only and preserving old IDs for log compatibility.

Risks/test signals: message ID reordering can break operational tooling. Compile coverage and log assertion tests should catch missing IDs after adding diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mgmt.c -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mgmt.c

Purpose: manages snapview-server communication with Gluster management to discover and refresh the snapshot list.

Important APIs/functions: `svs_mgmt_init()` creates an RPC client to glusterd using command-line volfile server/address-family settings, registers notify and callback programs, and starts the client. `svs_rpc_notify()` triggers snapshot refresh on RPC connect. `mgmt_cbk_snap()` handles management callbacks indicating snapshot-list changes. `svs_mgmt_submit_request()` serializes XDR requests into iobuf/iobref and submits RPC. `svs_get_snapshot_list()` requests snapshot name/uuid/volume data. `mgmt_get_snapinfo_cbk()` decodes the response dict and swaps `priv->dirents`.

Control flow: init builds transport options, starts RPC, and registers `GF_CBK_GET_SNAPS`. A refresh creates a frame, serializes a dict containing `volname`, and sends `GF_HNDSK_GET_SNAPSHOT_INFO`. The callback unserializes `snap-count`, `snap-volname.N`, `snap-id.N`, and `snapname.N`, allocates a new dirent array, carries forward matching cached `glfs_t` handles from the old array, swaps under `snaplist_lock`, then finalizes stale old handles.

State/persistence: authoritative snapshot state in this translator is `svs_private_t.dirents` plus `num_snaps`. The state is in-memory and refreshed from glusterd; libgfapi handles are preserved for unchanged snapshots and finalized for removed snapshots.

Dependencies/integration: depends on Gluster RPC client, handshake/callback programs, XDR types `gf_getsnap_name_uuid_req/rsp`, dict serialization, iobuf pools, and `SVS_STACK_DESTROY`. It uses `ctx->mgmt` for submission in `svs_mgmt_submit_request`.

Risks/test signals: refresh failure can leave old state intact or fail init depending on call site. The stale-handle transfer depends on matching both snapshot name and uuid. Tests should cover empty list, added/removed snapshots, renamed/recreated snapshots with same name different uuid, RPC connect refresh, malformed dict keys, XDR decode failure, frame cleanup on submit failure, and glfs_fini for stale cached handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.c -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.c

Purpose: implements the maintained `snapview-server` translator. It serves the virtual snapshot namespace for snapview-client, lists snapshots as directories, maps virtual inodes to libgfapi snapshot handles, and services read-only fops against snapshot volumes.

Important APIs/functions: lookup helpers `svs_lookup_entry_point`, `svs_lookup_gfid`, `svs_lookup_snapshot`, `svs_lookup_entry`, `svs_revalidate`, and `svs_get_handle` build or refresh inode contexts. Fops include `svs_lookup`, `svs_opendir`, `svs_getxattr`, `svs_fgetxattr`, `svs_readdirp`, `svs_readdir`, `svs_stat`, `svs_fstat`, `svs_statfs`, `svs_open`, `svs_readv`, `svs_readlink`, `svs_access`, and `svs_flush`. Callback/lifecycle functions include `svs_release`, `svs_releasedir`, `svs_forget`, `notify`, `mem_acct_init`, `init`, and `fini`.

Control flow: every user-visible fop validates inputs and often calls `gf_setcredentials()` so libgfapi access happens under the caller's uid/gid/groups. Lookup identifies entry-point xdata from snapview-client, synthesizes an entry-point inode when entering `.snaps`, opens a named snapshot volume when the parent is an entry point, and resolves deeper entries with `glfs_h_lookupat`. Revalidation returns cached synthetic attrs if the handle is still valid; otherwise it redoes handle lookup using parent context. Directory reads on the entry-point inode synthesize one dirent per snapshot from `priv->dirents`; reads below a snapshot call `glfs_readdir_r` or `glfs_readdirplus_r`. File/stat/xattr/readlink/read/access operations use cached `glfs_t` and `glfs_object_t`/`glfs_fd_t`, with fallback handle acquisition when readdirp created partial inode contexts.

State/persistence: `svs_private_t` stores `volname`, management RPC client, snapshot dirents, count, and `snaplist_lock`. `svs_inode_t` stores type (`ENTRY_POINT`, `SNAPSHOT`, or `VIRTUAL`), `glfs_t`, object handle, parent gfid, snapname, and cached iatt. `svs_fd_t` stores the libgfapi fd. State is volatile and rebuilt from lookups plus management refresh. `forget` frees snapname and closes object handles when their snapshot handle remains valid; release/releasedir close glfs fds.

Dependencies/integration: integrates with snapview-client through `"entry-point"` xdata and virtual inode gfids. It depends on libgfapi handle APIs, Gluster inode/fd contexts, RPC management refresh from `snapview-server-mgmt.c`, helper functions from `snapview-server-helpers.c`, iobuf/iobref for reads, ACL/access credential propagation, and volume option `volname`.

Risks/test signals: many paths assume inode contexts exist; NFS/readdirp partial contexts are handled by `svs_get_handle` but remain sensitive to parent context availability. Snapshot delete/recreate invalidates `glfs_t` and object pointers; validation tries to avoid use-after-free. `svs_readv` uses `ENOENT` as an EOF signal in `op_errno`, which higher layers must expect. Tests should cover entry-point lookup/listing, snapshot-name lookup, nested lookup, nameless gfid lookup to latest snapshot, snapshot deletion/recreation, NFS readdirp then direct fop, xattr list/get behavior and skip-cache marker, credential propagation, access semantics on entry point, read EOF signaling, release/forget cleanup, and management init failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.h -->
# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.h

Purpose: declares snapview-server public/private structures, constants, macros, and cross-file helper prototypes.

Important APIs/types: constants bound cached gfapi objects (`SNAP_VIEW_MAX_GLFS_T`, fd and object limits) and set the default log directory. Macros include `SVS_STACK_DESTROY`, `SVS_CHECK_VALID_SNAPSHOT_HANDLE`, `SVS_GET_INODE_CTX_INFO`, and `SVS_STRDUP`. Types include `inode_type_t` for entry-point/snapshot/virtual inodes, `svs_inode_t` for gfapi object mapping plus synthetic metadata, `svs_fd_t`, `snap_dirent_t`, and `svs_private_t`. Prototypes expose inode/fd context helpers, gfid/iatt helpers, snapshot initialization/list helpers, management init/submit, and `svs_get_handle`.

Control flow/state: the macros encode important runtime policy. `SVS_CHECK_VALID_SNAPSHOT_HANDLE` scans the current snapshot list under lock before a cached `glfs_t` is trusted. `SVS_GET_INODE_CTX_INFO` recovers missing/invalid fs/object handles via `svs_get_handle`.

Dependencies/integration: includes Gluster dict/defaults/mem/call-stub/iatt/logging/ACL/syncop/list/timer, libgfapi internals, RPC client/protocol headers, and server message IDs. It is shared by `snapview-server.c`, helpers, and management.

Risks/test signals: macros mutate caller variables and branch to caller labels, so call-site variable naming is part of the contract. `SVS_CHECK_VALID_SNAPSHOT_HANDLE` compares pointer identity; tests should cover stale handles after snapshot refresh and paths where handle recovery is attempted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/Makefile.am

Purpose: top-level Automake file for the thin-arbiter feature translator.

Important declarations: recurses into `src` and defines an empty `CLEANFILES`.

Control flow/state: build traversal only; no runtime behavior.

Dependencies/integration: integrates thin-arbiter into the feature xlator build tree.

Risks/test signals: low risk. Build/distribution tests should confirm the `src` subdir is included and clean targets remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/Makefile.am

Purpose: builds the `thin-arbiter.la` translator module.

Important declarations: enables `subdir-objects`, installs into the GlusterFS feature xlator directory, compiles `thin-arbiter.c` plus shared `xlators/lib/src/libxlator.c`, links `libglusterfs.la`, and declares noinst headers including thin-arbiter headers and `libxlator.h`. Include paths cover libglusterfs, xlators/lib, rpc-lib, and rpc/xdr source/build dirs.

Control flow/state: no runtime behavior; build configuration only.

Dependencies/integration: links the shared libxlator implementation directly and depends on RPC/libglusterfs headers used by thin-arbiter code outside this subset.

Risks/test signals: path drift in `top_builddir` references can break out-of-tree builds. Validate with Automake build, module install path, and clean/dist targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-mem-types.h

Purpose: defines memory accounting IDs for thin-arbiter allocations.

Important APIs/types: `gf_ta_mem_types_t` starts at `gf_common_mt_end + 1` and defines `gf_ta_mt_local_t`, `gf_ta_mt_char`, and `gf_ta_mt_end`.

Control flow/state: no executable behavior. The enum is expected to be passed to thin-arbiter memory accounting initialization and allocation calls.

Dependencies/integration: includes `glusterfs/mem-types.h` and is included by thin-arbiter implementation/header files.

Risks/test signals: allocation tags must stay synchronized with implementation use. Tests should cover mem accounting initialization and compile checks when adding new thin-arbiter allocation classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/thin-arbiter/src/thin-arbiter-mem-types.h -->
