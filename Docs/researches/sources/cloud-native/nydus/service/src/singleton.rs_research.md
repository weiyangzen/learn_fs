# sources/cloud-native/nydus/service/src/singleton.rs

Purpose: implements a singleton-style `ServiceController` daemon that hosts fscache/blob-cache services without creating a FUSE mount itself. It is the daemon path for fscache service mode and online upgrade of cachefiles state.

Important APIs/types: `ServiceController`, `initialize_fscache_service`, `create_daemon`, `start_services`, `stop_services`, `initialize_blob_cache`, `get_fscache_file`, and `delete_blob`. It implements both `NydusDaemon` and `DaemonStateMachineSubscriber`.

Control flow: `create_daemon` builds channels and optional `UpgradeManager`, initializes blob-cache config from a JSON `blobs` list, starts the common daemon FSM thread, checks for crash/failover unless upgrading, initializes fscache when requested, saves its fd/path/thread count into upgrade state, then emits `Mount` and `Start`. `start_services` spawns one fscache run-loop worker per configured thread; each wakes the global controller when exiting. `stop_services` calls `FsCacheHandler::stop`.

State and persistence: stores build/id/state/supervisor, blob cache manager, optional upgrade manager, fscache enabled flag, and optional `Arc<FsCacheHandler>`. Upgrade persistence includes fscache fd, path, thread count, and blob entries. `delete_blob` delegates to `FsCacheHandler::cull_cache` only when fscache is enabled and initialized.

Dependencies and integration: integrates daemon FSM, `BlobCacheMgr`, Linux `FsCacheHandler`, `UpgradeManager`, `mio::Waker`, `/dev/cachefiles`, and API socket crash detection. It is exported as `create_daemon` by `lib.rs`.

Risks: crash detection treats an unavailable `/dev/cachefiles` as either failover or "another daemon is running" depending on residual API socket connectivity. Spawned fscache worker handles are not joined in `wait`; stopping relies on the handler barrier. Blob-cache config parsing silently ignores JSON without `blobs` or invalid shape unless `add_blob_list` fails.

Test signals: Linux tests cover invalid fscache paths, optional root/kernel/device-gated fscache initialization, blob config loading, daemon properties/state, disabled and uninitialized `delete_blob`, missing fscache fd, no-op wait/umount, and optional managers.
