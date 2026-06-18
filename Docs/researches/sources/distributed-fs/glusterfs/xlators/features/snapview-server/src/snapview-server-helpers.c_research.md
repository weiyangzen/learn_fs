# sources/distributed-fs/glusterfs/xlators/features/snapview-server/src/snapview-server-helpers.c

Purpose: provides shared inode/fd context management, virtual gfid/iatt helpers, snapshot-list lookup, lazy libgfapi initialization, and snapshot-handle validation for snapview-server.

Important APIs/functions: `svs_inode_ctx_get/set/get_or_new`, `svs_fd_ctx_get/set/get_or_new`, `svs_inode_new`, and `svs_fd_new` allocate and attach `svs_inode_t`/`svs_fd_t`. `svs_uuid_generate()` deterministically generates virtual gfids from snapshot name plus origin gfid. `svs_iatt_fill()` builds synthetic directory attributes; `svs_fill_ino_from_gfid()` maps gfid to inode number. `__svs_get_snap_dirent()`, `svs_get_latest_snap_entry()`, `svs_get_latest_snapshot()`, `svs_initialise_snapshot_volume()`, `svs_inode_ctx_glfs_mapping()`, and `svs_inode_glfs_mapping()` support snapshot instance lookup and validation.

Control flow: fd context creation can open anonymous fds from an inode context using `glfs_h_opendir` or `glfs_h_open`. Snapshot volume initialization is protected by `snaplist_lock`, finds the named `snap_dirent`, creates `glfs_new("/snaps/...")`, chooses the volfile server from process command args or localhost, sets snapshot-specific logging, calls `glfs_init`, and caches `glfs_t` in the dirent. Mapping helpers reject stale `glfs_t` pointers by checking them against the current snap list.

State/persistence: contexts are in memory only. `snap_dirent_t.fs` caches live libgfapi handles. Synthetic gfids are generated from stable names/origin gfids, while synthetic iatt timestamps are fixed at zero. No on-disk data is written by helpers except libgfapi logging configuration.

Dependencies/integration: uses GlusterFS inode/fd context locking, gfapi handle APIs, rpc/protocol headers, `DEFAULT_SVD_LOG_FILE_DIRECTORY`, and private mem types. It relies on `svs_private_t.dirents` being refreshed by management RPC.

Risks/test signals: stale snapshot names reused after deletion are a known risk mitigated by handle validation. Error cleanup closes glfs handles on failures, but ownership is delicate when fd context set fails. Tests should cover repeated snapshot refresh, deletion/recreation with same name, anonymous fd open for NFS paths, deterministic gfid generation, invalid volfile server fallback, glfs_init failure cleanup, and forget/release interaction.
