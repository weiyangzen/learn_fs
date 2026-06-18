# sources/distributed-fs/orangefs/src/common/misc/server-config-mgr.c

Purpose: Maintains a process-local map from `PVFS_fs_id` to loaded `server_configuration_s` objects, with reference counting, cached-config reload support, and global minimum handle-recycle-time tracking.

Important APIs and functions: `PINT_server_config_mgr_initialize`/`finalize` create and destroy the hash table. `PINT_server_config_mgr_add_config` inserts or refcounts configs. `PINT_server_config_mgr_remove_config` decrements refs and frees configs. `PINT_server_config_mgr_reload_cached_config_interface` rebuilds cached handle mappings and recomputes minimum recycle timeout. `__PINT_server_config_mgr_get_config` and `__PINT_server_config_mgr_put_config` expose locked config access. `PINT_server_config_mgr_get_abs_min_handle_recycle_time` returns the cached minimum.

Control flow: Initialization allocates a 17-bucket quickhash table. Add checks for an existing fsid, increments refcount if found, and tells the caller to free the unused config via `free_config_flag`. Reload finalizes/reinitializes cached config state, iterates every stored configuration, expects exactly one filesystem per config, updates the minimum recycle timeout, and loads handle mappings. Get searches by fsid and intentionally leaves `s_server_config_mgr_mutex` locked until put is called.

State and persistence: Static hash table, mutex, per-entry refcounts, and minimum handle recycle timeout are process-local. The manager owns inserted config pointers and frees them with `PINT_config_release` plus `free`.

Dependencies and integration points: Depends on `quickhash`, `qlist`, `gen-locks`, gossip logging, `pint-cached-config`, and server config structures. Client builds use this manager through macros in `server-config-mgr.h`; server builds bypass it and use global server config.

Risks: The get/put lock ownership contract is subtle and can deadlock if callers call back into manager APIs or forget put. `finalize` destroys the static mutex, making reinitialize-after-finalize questionable. Reload uses asserts for expected one-filesystem config and positive timeout, so malformed configs can abort. `SC_MGR_ASSERT_OK` inside put returns from a void function while assuming lock state is valid.

Test signals: Initialize/finalize idempotence, add duplicate fsid and free flag behavior, refcounted remove, get/put lock pairing, concurrent add/remove/get, reload cached mappings across multiple configs, minimum recycle-time recomputation, and error handling for cached-config initialization/load failures.
