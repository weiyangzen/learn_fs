# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.h

## Purpose

`dht-common.h` is the shared contract for GlusterFS's DHT/distribute translator. It defines the in-memory layout model, per-call local state, inode and fd context, rebalance/migration metadata, disk-usage state, lock wrappers, DHT xattr keys, and the FOP/helper prototypes consumed by the DHT implementation files. The header is the coordination point between lookup/layout code, disk-space placement, linkfile handling, migration checks, read/write forwarding, directory self-heal, and translator lifecycle code.

## Important APIs, Types, and Functions

The central types are `dht_layout_entry_t`, `dht_layout_t`, `dht_inode_ctx_t`, `dht_local_t`, `dht_du_t`, `gf_defrag_info_t`, `dht_conf_t`, `dht_migrate_info_t`, and `dht_fd_ctx_t`. `dht_layout_t` stores hash ranges, commit hashes, generation, spread count, and a refcounted variable-length `list[]`. `dht_inode_ctx_t` persists an inode's cached layout, time cache, lock subvolume, and directory MDS subvolume. `dht_local_t` is the large per-frame scratchpad for locations, xattrs, cached/hashed subvolumes, self-heal, linkfile, rebalance, locks, counters, and retry state.

Important macros include `DHT_STACK_UNWIND`, `DHT_STACK_DESTROY`, `DHT_UPDATE_TIME`, `IS_DHT_MIGRATION_PHASE1`, `IS_DHT_MIGRATION_PHASE2`, `DHT_STRIP_PHASE1_FLAGS`, `check_is_linkfile`, `layout_is_sane`, and the DHT xattr constants such as `GF_XATTR_FIX_LAYOUT_KEY`, `GF_XATTR_FILE_MIGRATE_KEY`, `DHT_FILE_MIGRATE_DOMAIN`, `DHT_LAYOUT_HEAL_DOMAIN`, and `DHT_ENTRY_SYNC_DOMAIN`. The declared APIs span layout allocation/search/merge/extract, hash calculation, linkfile creation, disk-usage refresh, subvolume selection, fd/inode context handling, migration checks, directory self-heal, xattr heal, lock routing, all file/dir FOP entry points, and lifecycle hooks.

## Control Flow and Integration

Most DHT FOPs allocate `dht_local_t` with `dht_local_init`, derive cached or hashed subvolumes from inode layout, wind one or more child FOPs, then unwind through `DHT_STACK_UNWIND`, which also wipes the local state. Layout lookup and self-heal flows use `dht_layout_merge`, `dht_layout_normalize`, and self-heal callbacks. File migration flows use the rebalance fields in `dht_local_t`, `dht_migrate_info_t` in inode ctx slot 1, and `dht_fd_ctx_t` on fd contexts to know whether an fd has been opened on the destination. Directory operations integrate with namespace/layout lock domains and MDS xattrs.

## State and Persistence Behavior

Persistent distributed state is stored mostly as trusted xattrs: directory layout, commit hash, linkto target, migration flags, MDS markers, and debug/status keys. Runtime state is split across translator config (`dht_conf_t`), inode contexts (`dht_inode_ctx_t` plus migration info), fd contexts (`dht_fd_ctx_t`), and call-frame local state. `dht_layout_t` is refcounted unless marked `preset`; `DHT_STACK_UNWIND` and `dht_local_wipe` are therefore part of the memory-safety contract. `vol_commit_hash`, layout `commit_hash`, `gen`, `subvolume_status`, and `subvol_up_time` connect topology changes to lookup/migration behavior.

## Dependencies and Risks

The header depends on GlusterFS frame, inode, fd, dict, syncop, lock, refcount, ACL, XDR, and DHT message/memtype headers. Risks concentrate around aliasing and ownership: `dht_dir_transaction_t` intentionally has a lock wrapper first because cleanup casts into nested variants; layout refs must not be freed for preset layouts; `dht_local_t` stores many owned dicts/locs/refs; and migration phase mode bits must be stripped before returning attrs to upper layers. Tests should exercise layout xattr parsing, refcount lifecycle, DHT unwind cleanup, fd/inode context migration updates, directory MDS routing, and nested DHT migration where `we_are_not_migrating(ret)` passes migration mode bits upward.
