# sources/distributed-fs/ceph-client/fs/smb/client/dfs_cache.h

Purpose: declares the CIFS DFS referral cache API and target-list iterator model shared by mount, reconnect, remount, and refresh code.

Important APIs and types: declares global `dfscache_wq`, global atomic `dfs_cache_ttl`, `dfscache_proc_ops`, `struct dfs_cache_tgt_list`, and `struct dfs_cache_tgt_iterator`. Public functions include `dfs_cache_init`, `dfs_cache_destroy`, `dfs_cache_find`, `dfs_cache_noreq_find`, `dfs_cache_noreq_update_tgthint`, `dfs_cache_get_tgt_referral`, `dfs_cache_get_tgt_share`, `dfs_cache_canonical_path`, `dfs_cache_remount_fs`, and `dfs_cache_refresh`. Inline helpers include `DFS_CACHE_TGT_LIST_INIT`, `DFS_CACHE_TGT_LIST`, `dfs_cache_get_next_tgt`, `dfs_cache_get_tgt_iterator`, `dfs_cache_free_tgts`, `dfs_cache_get_tgt_name`, `dfs_cache_get_nr_tgts`, and `dfs_cache_get_ttl`.

Control flow: callers typically declare a stack `DFS_CACHE_TGT_LIST`, call `dfs_cache_find` or `dfs_cache_noreq_find`, iterate targets with `dfs_cache_get_tgt_iterator` and `dfs_cache_get_next_tgt`, and release copied target nodes with `dfs_cache_free_tgts`. Refresh work is queued on `dfscache_wq` and calls `dfs_cache_refresh`.

State and persistence behavior: target lists returned to callers are copied lists owned by the caller; freeing removes every iterator node and its duplicated name and resets `tl_numtgts`. The real persistent cache state lives in `dfs_cache.c`. The exported TTL controls refresh scheduling and is read atomically.

Dependencies and integration points: includes Linux NLS/list/uuid helpers and CIFS global structures. It is included by `dfs.h`, `dfs.c`, `connect.c`, and cache refresh/remount paths.

Risks: callers must initialize lists before use and free them on every path. `dfs_cache_get_next_tgt` assumes the iterator belongs to the given list. `dfs_cache_get_tgt_name` returns borrowed iterator storage. The header exposes globals, so module init/exit ordering must ensure `dfscache_wq` and `dfs_cache_ttl` are valid before scheduling or reading.

Test signals: compile coverage with DFS enabled, target-list iteration over empty/single/multiple targets, freeing partially populated lists after allocation failure, TTL reads after init, and all users freeing copied target lists after reconnect or mount attempts.
