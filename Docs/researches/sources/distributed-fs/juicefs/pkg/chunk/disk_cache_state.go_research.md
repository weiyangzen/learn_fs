## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state.go

Purpose: implements a small disk-cache health state machine used by `cacheStore` to degrade or disable a cache directory after IO errors or timeouts.

Important APIs/types/functions: globals configure thresholds such as IO errors to unstable, successes to normal, max duration to down, unstable concurrency limit, tick durations, and probe settings. States implement `dcState`: `normalDC`, `unstableDC`, `downDC`, and `unchangedDC`. `normalDC` counts IO errors and transitions to unstable after the threshold. `unstableDC` counts successes/errors, probes the cache by writing/reading/removing probe pages, limits concurrent operations, returns to normal when enough successes and low error percentage occur, or transitions down after max duration. `downDC` rejects operations with `errCacheDown`. `cacheStore.event` coordinates transitions and stops prior state goroutines. `getEnvs` overrides thresholds from environment variables.

State and persistence: state is in memory per `cacheStore`; probes create and remove files under a `probe` cache path. Environment variables tune process-wide globals.

Dependencies and integration points: `cacheStore.checkErr` calls `beforeCacheOp`, `checkCacheOp`, `afterCacheOp`, `onIOErr`, and `onIOSucc`. `disk_cache.go` removes unavailable stores from `cacheManager`.

Risks and test signals: concurrency limit uses atomic counters and must balance before/after calls. Probe loops can add load to unstable devices. Global env overrides affect all stores in process. Tests exercise state transitions and environment-dependent behavior.
