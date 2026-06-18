## sources/cloud-native/stargz-snapshotter/fs/config/config.go

Purpose: defines configuration and snapshot label keys for the stargz snapshotter filesystem, including cache modes, resolve TTLs, prefetch/background fetch behavior, verification policy, metrics, blob fetching, directory cache, and FUSE options.

Important APIs/types/functions: label constants are `TargetSkipVerifyLabel` and `TargetPrefetchSizeLabel`. `Config` aggregates high-level filesystem settings and embeds `BlobConfig`, `DirectoryCacheConfig`, and `FuseConfig`. `BlobConfig` controls remote blob validity, chunk size, prefetch chunking, retry counts, wait bounds, and single-range mode. `DirectoryCacheConfig` controls LRU sizes, sync adds, direct mode, and fadvise. `FuseConfig` controls attr/entry timeouts, passthrough mode, merge buffer size, and merge worker count.

Control flow: this file is declarative; consumers such as `fs.NewFilesystem`, `layer.NewResolver`, and `remote.NewResolver` interpret zero values as defaults and booleans as feature toggles.

State and persistence: fields are tagged for TOML and JSON serialization, making them persisted through config files or API structs outside this file. No runtime state is stored here.

Dependencies and integration points: imported by `fs/fs.go`, `fs/layer/layer.go`, remote blob resolution, and snapshot label handling. The labels control mount-time prefetch override and optional verification skip when policy permits.

Risks: typo in `BlobConfig.FetchTimeoutSec` JSON tag (`fetching_tieout_sec`) may affect JSON config compatibility. Some comments say seconds for millisecond fields (`MinWaitMSec`, `MaxWaitMSec`). Zero-value defaults are implemented elsewhere, so adding new fields requires coordinated defaulting in consumers.

Test signals: no direct tests in this subset. Behavior is indirectly covered where filesystem/layer code reads config values for default concurrency, timeouts, cache types, prefetch, passthrough, and verification.
