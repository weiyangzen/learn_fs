# subset-b-007071 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.h -->
# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.h

## Purpose

`xdr-nfs3.h` is the public XDR contract for GlusterFS's NFSv3 and mount protocol support. It defines the wire-sized scalar aliases, NFSv3 status/procedure enums, request and response structs, mount protocol structs, and encoder/decoder prototypes implemented in `xdr-nfs3.c`. Consumers such as `rpc/xdr/src/msg-nfs3.c`, `xlators/nfs/server/src/nfs3*.c`, ACL code, and mount service code include this header to marshal RPC arguments and replies.

## Important APIs, types, and constants

- Fixed protocol sizes: `NFS3_FHSIZE`, cookie/create/write verifier sizes, and size-estimation macros for readdir/write paths (`NFS3_ENTRY3_FIXED_SIZE`, `NFS3_READDIR_RESOK_SIZE`, `NFS3_WRITE3ARGS_SIZE`).
- Scalar aliases: `uint64`, `int64`, `uint32`, `filename3`, `nfspath3`, `fileid3`, `cookie3`, `uid3`, `gid3`, `size3`, `offset3`, `mode3`, and `count3`.
- Core NFSv3 enums: `nfsstat3`, `ftype3`, `time_how`, `stable_how`, and `createmode3`.
- Attribute and weak-cache-consistency types: `fattr3`, `post_op_attr`, `pre_op_attr`, `wcc_attr`, and `wcc_data`.
- Procedure structs for all NFSv3 calls: `getattr3*`, `setattr3*`, `lookup3*`, `access3*`, `readlink3*`, `read3*`, `write3*`, create/mkdir/symlink/mknod/remove/rmdir/rename/link, `readdir3*`, `readdirp3*`, `fsstat3*`, `fsinfo3*`, `pathconf3*`, and `commit3*`.
- Mount protocol types: `fhandle3`, `mountstat3`, `mountres3`, linked `mountlist`, `groups`, and `exports`.
- Program/procedure numbers: `NFS_PROGRAM`, `NFS_V3`, `NFS3_*`, `MOUNT_PROGRAM`, `MOUNT_V3`, `MOUNT_V1`, and `MOUNT*_PROC_COUNT`.
- XDR prototypes: one `xdr_*` function per scalar, enum, struct, list, and response union, plus optimized helpers `xdr_read3res_nocopy()` and `xdr_free_write3args_nocopy()`.

## Control flow and data model

This header has no executable control flow, but it encodes the discriminated-union model used by the generated/manual XDR routines. Most result structs begin with a status field and contain a union where success arms include full object/parent metadata while failure arms carry weak cache consistency or post-op attributes. Optional protocol fields use `bool_t` discriminants, for example `post_op_attr.attributes_follow`, `pre_op_attr.attributes_follow`, and `post_op_fh3.handle_follows`. Linked-list reply shapes (`entry3`, `entryp3`, `mountbody`, `groupnode`, `exportnode`) are recursive and rely on the matching XDR routines to allocate/free list nodes.

## State and persistence behavior

The types describe RPC wire state only. Persistent storage is outside the header; however, fields such as file handles, cookies, verifiers, weak-cache-consistency attributes, and write commit verifiers carry server state across client requests. The fixed-size constants are important because code in the NFS server sizes buffers and no-copy read/write paths around the NFSv3 wire representation.

## Dependencies and integration points

The header depends on SunRPC-style `XDR`/`bool_t` definitions from `<rpc/rpc.h>` and C integer types from `<sys/types.h>`. `rpc/xdr/src/Makefile.am` builds `xdr-nfs3.c` and `msg-nfs3.c` when GNFS is enabled. `msg-nfs3.c` uses the prototypes to serialize RPC messages and specifically references `xdr_read3res_nocopy()`. The NFS server stack includes this header via `nfs3.h`, `nfs3-fh.c`, `nfs3.c`, ACL code, and mount service sources.

## Risks and edge cases

- The file handle model permits variable-length `nfs_fh3`, but Gluster's comments and size macros assume returned handles are 64 bytes in some hot paths. A future shorter/longer file handle contract would require auditing buffer sizing and no-copy helpers.
- Recursive list types need correct ownership handling in XDR decode/free paths; leaks or double-frees are likely if callers bypass `xdr_free_exports_list()`, `xdr_free_mountlist()`, or XDR free semantics.
- Status-discriminated unions are valid only when encoders and decoders use the same `status` arm logic. Adding a status/procedure without updating `xdr-nfs3.c` would silently break the wire contract.
- `NFS3ERR_END_OF_LIST = -1` is not a normal RFC NFS status and must not leak to wire consumers that expect unsigned enum values.
- The header aliases integer types by short names (`uint64`, `uint32`) that can collide with other platform headers.

## Test signals

Good coverage comes from RPC encode/decode round trips for every procedure, NFSv3 interoperability tests against standard clients, readdir/readdirplus list/free stress tests, no-copy READ and WRITE memory ownership tests, and mount/export list serialization tests. Integration signals include successful GNFS builds, NFS server functional tests for all `NFS3_*` procedures, and ABI checks that struct/procedure definitions remain synchronized with `xdr-nfs3.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/Makefile.am

## Purpose

This Automake file is the top-level build entry point for GlusterFS translators under `xlators/`. It defines which translator families are always traversed and conditionally includes the legacy GNFS translator directory when `BUILD_GNFS` is enabled.

## Important build variables

- `GNFS_DIR = nfs` is set only inside `if BUILD_GNFS`.
- `DIST_SUBDIRS` lists all distributable translator families, including `nfs` unconditionally so release tarballs contain it.
- `SUBDIRS` lists build traversal order: `cluster`, `storage`, `protocol`, `performance`, `debug`, `features`, `mount`, conditional `${GNFS_DIR}`, `mgmt`, `system`, `playground`, and `meta`.
- `EXTRA_DIST = xlator.sym` distributes the translator symbol file.
- `CLEANFILES` is empty.

## Control flow and integration

Automake evaluates `BUILD_GNFS` at configure time. When disabled, `nfs` remains in the distribution set but is not built. `cluster` is first in `SUBDIRS`, so cluster translators such as AFR are built before later translator families that may depend on shared installed headers or conventions.

## State and persistence behavior

The file only controls generated Makefile state. It does not persist runtime data, but it affects installed translator availability and source distribution completeness.

## Dependencies and integration points

This file depends on the configure-time `BUILD_GNFS` conditional and the existence of child `Makefile.am` files in every listed subdirectory. It integrates with recursive Automake from the repository root and with `xlator.sym` packaging.

## Risks and edge cases

- A directory in `SUBDIRS` without a generated Makefile breaks recursive builds.
- Omitting a directory from `DIST_SUBDIRS` can create incomplete release tarballs even if local builds pass.
- Conditional GNFS inclusion means NFS-related build failures can be hidden in default builds where `BUILD_GNFS` is off.

## Test signals

Run `autoreconf`/configure with GNFS both enabled and disabled, then run `make -C xlators` and `make distcheck` or equivalent distribution checks. Verify that `xlator.sym` is present in source archives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/Makefile.am

## Purpose

This is the cluster-translator recursive Automake file. It builds the three cluster translator families: AFR replication, DHT distribution, and EC erasure coding.

## Important build variables

- `SUBDIRS = afr dht ec` defines traversal order.
- `CLEANFILES` is empty.

## Control flow and integration

Automake enters `afr`, then `dht`, then `ec`. AFR's position first is relevant because it is a core cluster translator and has its own recursive `src` build. This file has no conditionals.

## State and persistence behavior

No runtime state is involved. The file determines which cluster translator modules are built and included in recursive clean/install targets.

## Dependencies and integration points

It depends on valid child Automake files under `afr/`, `dht/`, and `ec/`. The parent `xlators/Makefile.am` reaches this file through its `SUBDIRS` list.

## Risks and edge cases

- Adding a new cluster translator requires updating this file or it will not be built.
- Removing or renaming a child directory without updating `SUBDIRS` breaks recursive Automake.
- Empty `CLEANFILES` means cleanup responsibility sits in child directories.

## Test signals

Recursive `make -C xlators/cluster`, `make install`, and `make distcheck` should traverse all three cluster translators. A packaging check should confirm each translator module is included as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/Makefile.am

## Purpose

This file is the AFR translator directory handoff. It delegates all AFR build work to `src/`, where the `afr.la` translator module and private headers are defined.

## Important build variables

- `SUBDIRS = src` makes `xlators/cluster/afr/src/Makefile.am` authoritative for compilation and installation.
- `CLEANFILES` is empty.

## Control flow and integration

The parent cluster Makefile enters `afr/`, and this file immediately recurses into `src/`. There are no conditionals or distributed extra files here.

## State and persistence behavior

No runtime state is managed. Build state is delegated to the generated Makefile in `src/`.

## Dependencies and integration points

The only dependency is the `src` child directory. The integration point is the recursive Automake traversal from `xlators/cluster/Makefile.am`.

## Risks and edge cases

This file is intentionally minimal. The main risk is accidentally placing build definitions in `afr/` instead of `afr/src/`, which would not affect compilation unless this file is expanded.

## Test signals

`make -C xlators/cluster/afr` should recurse into `src` and produce the same result as building `xlators/cluster/afr/src` through the normal tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/Makefile.am

## Purpose

This Automake file builds and installs the AFR replication translator module. It produces `afr.la` under the cluster translator installation directory and installs a compatibility symlink from `replicate.so` to `afr.so`.

## Important build variables and targets

- `AUTOMAKE_OPTIONS = subdir-objects` allows object paths for sources outside the local directory, notably `$(top_builddir)/xlators/lib/src/libxlator.c`.
- `xlator_LTLIBRARIES = afr.la` declares the translator module.
- `xlatordir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/cluster` sets the install directory.
- `afr_common_source` includes AFR operation families (`afr-dir-read.c`, `afr-dir-write.c`, `afr-inode-read.c`, `afr-inode-write.c`, `afr-open.c`, `afr-transaction.c`, `afr-lk-common.c`, `afr-read-txn.c`) and `libxlator.c`.
- `AFR_SELFHEAL_SOURCES` includes common, data, entry, metadata, daemon, and name self-heal sources.
- `afr_la_SOURCES = $(afr_common_source) $(AFR_SELFHEAL_SOURCES) afr.c`; `afr.c` includes `afr-common.c`, so `afr-common.c` is listed in `noinst_HEADERS` rather than compiled as a separate source.
- `afr_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la`.
- `AM_CPPFLAGS` adds libglusterfs, xlator library, RPC, and generated XDR include directories from both source and build trees.
- `install-data-hook` creates `replicate.so -> afr.so`; `uninstall-local` removes the compatibility symlink.

## Control flow and integration

The generated build compiles AFR's module sources into a libtool module with GlusterFS's default xlator linker flags. The symlink hook preserves the older translator name `replicate.so` for volume graphs or tooling that still refer to "replicate" while the actual module is built as `afr.so`.

## State and persistence behavior

Runtime persistence is not managed here. The file determines installed module artifacts under the versioned GlusterFS translator directory and creates/removes the `replicate.so` symlink during install/uninstall.

## Dependencies and integration points

AFR depends on `libglusterfs.la`, local AFR headers, `xlators/lib/src/libxlator.h`, RPC/XDR headers, and generated XDR build output. It integrates with the broader translator ABI through `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, `GF_CFLAGS`, and the installed module layout consumed by Gluster volume graphs.

## Risks and edge cases

- `afr-common.c` is included by `afr.c`; adding it to `afr_la_SOURCES` as a normal C source would likely duplicate symbols.
- The symlink hook assumes the installed module name is `afr.so`; libtool naming or install-layout changes could break `replicate.so`.
- Include order includes both source and build XDR directories; stale generated headers in the build tree can mask source-tree changes.
- `libxlator.c` is pulled from `top_builddir`, so out-of-tree builds rely on `subdir-objects` and correct generated paths.

## Test signals

Run recursive `make` for `xlators/cluster/afr/src`, inspect that `afr.la`/`afr.so` is produced, and run `make install DESTDIR=...` to verify `cluster/afr.so` and `cluster/replicate.so` symlink creation. A clean uninstall should remove the symlink. Functional tests should exercise AFR volume loading by both current and compatibility translator names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-common.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-common.c

## Purpose

`afr-common.c` is the central implementation body included by `afr.c` for the AFR/replicate translator. It supplies shared logic for lookup/discover, inode refresh, read-subvolume selection, lock and lease fan-out, lock healing, child notification handling, local/frame cleanup, pending-xattr interpretation, split-brain status, heal-status queries, thin-arbiter coordination, and common quorum/error handling. The file is built into `afr.la` indirectly because `afr.c` includes it.

## Important APIs, functions, and internal types

Major exported/common functions include:

- Quorum/error helpers: `afr_quorum_errno()`, `afr_fill_success_replies()`, `afr_is_consistent_io_possible()`, `afr_is_symmetric_error()`, `afr_higher_errno()`, `afr_final_errno()`, `afr_handle_replies_quorum()`, and `afr_lookup_has_quorum()`.
- Inode/read-state helpers: `__afr_inode_ctx_get()`, `afr_inode_read_subvol_get()`, `afr_inode_get_readable()`, `afr_read_subvol_get()`, `afr_read_subvol_select_by_policy()`, `afr_inode_need_refresh_set()`, `afr_is_inode_refresh_reqd()`, `afr_set_inode_local()`, and write-subvolume helpers `afr_write_subvol_get/set/reset()`.
- Lookup/discover flow: `afr_lookup()`, `afr_lookup_do()`, `afr_lookup_cbk()`, `afr_lookup_entry_heal()`, `afr_lookup_metadata_heal_check()`, `afr_lookup_done()`, `afr_discover()`, `afr_discover_do()`, `afr_discover_cbk()`, and `afr_discover_done()`.
- Refresh and heal coordination: `afr_inode_refresh()`, `afr_inode_refresh_do()`, lookup/fstat refresh callbacks, `afr_replies_interpret()`, `afr_readables_fill()`, `afr_is_pending_set()`, `afr_get_heal_info()`, `afr_is_split_brain()`, `afr_get_split_brain_status()`, and `afr_heal_splitbrain_file()`.
- Locking APIs: `afr_inodelk()`, `afr_finodelk()`, `afr_entrylk()`, `afr_fentrylk()`, `afr_lk()`, serialized/parallel lock callbacks, `afr_lk_transaction()` for mandatory lock healing, lease functions, and lock-heal queue helpers.
- FOP support: `afr_flush()`, `afr_fsyncdir()`, `afr_statfs()`, `afr_ipc()`, `afr_release()`, `afr_forget()`, `afr_priv_dump()`, `afr_local_init()`, `afr_transaction_local_init()`, `afr_local_cleanup()`, and matrix allocation helpers.
- Notification and thin-arbiter support: `afr_notify()`, `__afr_handle_child_up_event()`, `__afr_handle_child_down_event()`, HALO latency selection, upcall handling, `afr_ta_post_op_lock()`, `afr_ta_post_op_unlock()`, `afr_ta_frame_create()`, `afr_ta_has_quorum()`, and `afr_ta_dict_contains_pending_xattr()`.

Important state types are declared in `afr.h`: `afr_private_t` holds child arrays, quorum/arbiter/thin-arbiter state, pending xattr keys, event generation, heal queues, saved lock queues, latency/HALO state, and translator options; `afr_local_t` holds per-FOP snapshots, reply arrays, transaction state, lock state, and xdata; `afr_inode_ctx_t` caches read/write subvolume bitmaps, split-brain choice, lock queues, open-fd counts, refresh flags, and unstable-write state; `afr_fd_ctx_t` tracks per-child fd open state and lock-heal metadata.

## Control flow

Frame setup begins with `AFR_FRAME_INIT`, which calls `afr_local_init()` to snapshot `priv->child_up`, initialize reply arrays, set `call_count`, capture `event_generation`, and allocate per-FOP readable/open state. Most multi-child FOPs wind to each up child and use `afr_frame_return()` as a locked fan-in counter.

Lookup has two paths. Nameless lookups go through `afr_discover()`. Named lookups reject private root entries, prepare xattr requests for pending/lock/link-count information, wind lookup to all up children, and collect replies in `afr_lookup_cbk()`. Once all replies arrive, AFR may launch name self-heal or metadata self-heal, interprets pending xattrs into readable data/metadata bitmaps, checks GFID/type mismatch, applies quorum rules, avoids arbiter read selection, and unwinds the chosen child reply. Fresh lookup is forced with `ESTALE` when lower layers report `gfid-changed`.

Inode refresh is a lookup/fstat pass over all usable child subvolumes. It requests AFR pending xattrs, dirty xattrs, link count, and inodelk counts. `afr_readables_fill()` marks accused children from pending vectors, excludes arbiter from read candidates, optionally accuses smaller files when no data transaction appears active, and updates inode read bitmaps. If refresh detects healable divergence and self-heal is enabled, it schedules `afr_throttled_selfheal()`.

Read-subvolume selection first uses cached inode bitmaps. It prefers configured `read_child`, then policies based on GFID hash, GFID+PID hash, least pending reads, least latency, or latency multiplied by pending reads, and finally the first readable child. When data and metadata readable sets intersect, AFR prefers the intersection to avoid mixing content from one child with metadata from another.

Lock operations use two strategies. Inode/entry locks first try parallel nonblocking acquisition; on contention they release partial locks and retry serialized to avoid two clients each holding partial locks. `afr_lk()` for POSIX byte-range locks walks children serially, tracks `locked_nodes`, honors quorum, and unlocks on failure. Mandatory lock mode uses `afr_lk_transaction()` with a domain lock (`AFR_LK_HEAL_DOM`) and saved lock records so locks can be healed when a child returns.

Notification flow aggregates child up/down/connecting/ping/upcall events. `afr_notify()` updates `child_up`, `last_event`, `event_generation`, quorum transitions, and HALO latency decisions under `priv->lock`; it only propagates selected events upward to avoid exposing every child transition. Child-up schedules pending lock heal and self-heal; child-down marks saved locks for healing or invalidates fds if quorum was lost.

Thin-arbiter flow uses a special child index and lock domains `AFR_TA_DOM_NOTIFY` and `AFR_TA_DOM_MODIFY`. Clients hold notify-domain locks as a notification mechanism; self-heal daemon contention can trigger clients to release after in-memory/on-wire transactions finish. Thin-arbiter quorum allows two data bricks, or one data brick plus the thin arbiter.

## State and persistence behavior

Persistent correctness state is primarily stored in per-child AFR pending xattrs (`priv->pending_key[]`) and dirty xattrs (`AFR_DIRTY`). `afr_mark_pending_changelog()` constructs data/metadata/entry changelog matrices for on-disk pending state. `afr_replies_interpret()` reads those xattrs back and caches readable sets in `afr_inode_ctx_t`.

In-memory persistence includes inode ctxs attached to Gluster inode objects, fd ctxs attached to fds, `priv->event_generation`, child health arrays, saved lock queues, lock-heal queues, split-brain choice timers, and thin-arbiter lock offsets. `afr_forget()` destroys inode ctx state, including split-brain choice timers. `afr_release()` destroys fd ctx state and removes saved lock records. `afr_priv_destroy()` frees translator private arrays and lock resources.

Split-brain choice is temporarily persisted in inode ctx as `spb_choice` with a timer controlled by `priv->spb_choice_timeout`; expiry invalidates the inode and clears the choice. HALO latency state persists in `priv->child_latency` and `priv->halo_child_up` while the translator is alive.

## Dependencies and integration points

The file depends on `afr.h`, AFR operation headers, self-heal headers, transaction helpers, lock helpers, libglusterfs dictionaries/lists/statedump/events/upcall APIs, syncop/synctask APIs, Gluster call-frame/stack macros, inode/fd ctx APIs, and child translator FOP tables. It calls functions defined in sibling files such as `afr_has_quorum()` and thin-arbiter loc helpers from `afr-transaction.c`, `afr_locked_nodes_count()` from `afr-lk-common.c`, self-heal routines from `afr-self-heal-*`, read helpers from `afr-inode-read.c`, and quota handling from inode-read code.

Build integration is unusual: `xlators/cluster/afr/src/Makefile.am` lists `afr-common.c` as `noinst_HEADERS`, and `afr.c` includes it directly. This gives the file access to static/private AFR symbols in one translation unit but means duplicate compilation would create symbol conflicts.

Runtime integration points include child storage/protocol translators via `STACK_WIND`, parent translators via `AFR_STACK_UNWIND` and `default_notify`, self-heal daemon synctasks, md-cache invalidation via upcalls, statedump via `afr_priv_dump()`, and NFS/client behavior through read-child and consistency options.

## Risks and edge cases

- Many code paths depend on correctly paired dict refs/unrefs, inode/fd refs, and `AFR_STACK_DESTROY`; leaks or use-after-free bugs are plausible around async self-heal, timers, and error exits.
- `event_generation` is central to consistency checks. Missing an increment or comparing stale local snapshots can either reject valid I/O with `ENOTCONN` or allow stale reads.
- Readable bitmaps are packed into 16-bit fields for child counts <= 16; larger replica counts are explicitly unsupported in those helpers.
- Lock healing supports only replica-3 non-arbiter volumes in `afr_lk_transaction()`. Other layouts return `ENOTSUP`.
- Partial lock recovery is complex: parallel lock contention, serialized retry, quorum failure, and unlock failure logging must preserve POSIX expectations and avoid leaving locks behind.
- Lookup GFID mismatch handling intentionally tolerates some in-flight transactions but fails with `EIO` when mismatch cannot be explained. This path is sensitive to pending xattr accuracy.
- Arbiter and thin-arbiter children must not be selected for normal reads; several paths explicitly filter them, and regressions can return invalid size/content.
- HALO can mark high-latency children down or swap children to satisfy min/max replica constraints; bad latency inputs can change availability decisions.
- Some helpers use `alloca0(priv->child_count)` heavily; unexpected large child counts could create stack pressure.
- Error priority (`ENODATA > ENOENT > ESTALE > ENOSPC > other`) affects user-visible behavior and repair decisions.

## Test signals

High-value tests include AFR lookup under GFID mismatch, pending entry heal, in-flight create/unlink/rename, data and metadata split-brain, root private-directory filtering, arbiter read exclusion, read policy selection, refresh after child up/down, md-cache invalidation when pending xattrs appear, quorum loss/recovery, HALO latency threshold behavior, mandatory lock healing across child down/up, partial lock cleanup after `EAGAIN`/`EINTR`, POSIX `lk` quorum failure, lease unlock cleanup, thin-arbiter notify/modify lock contention, split-brain choice timeout, fd-bad behavior after lost lock quorum, and cleanup paths under allocation failures. Build tests must also confirm `afr-common.c` remains included only through `afr.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-common.c -->
