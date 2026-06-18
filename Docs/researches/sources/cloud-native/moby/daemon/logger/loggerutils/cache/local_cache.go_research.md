# sources/cloud-native/moby/daemon/logger/loggerutils/cache/local_cache.go

Purpose: wraps a logger with a local cache so writes go both to the primary driver and to a readable local logger.

Important APIs/types/functions: `WithLocalCache`, `loggerWithCache`, `BufSize`, `Log`, `ReadLogs`, `Close`, `ShouldUseCache`, and `dumbCopyMessage`. Constants include `DriverName`, `cachePrefix`, and `cache-disabled`.

Control flow/state/persistence: `WithLocalCache` obtains the `local` driver, initializes it with the same `logger.Info`, and wraps it in `NewRingLogger` when mode is unset or non-blocking, using `max-buffer-size` when configured. `Log` duplicates the original message, sends the duplicate to the primary logger first, and then sends the original to the cache so ownership semantics stay intact. `ReadLogs` delegates to the cache's `LogReader`; `Close` closes primary and cache, logging cache close errors.

Dependencies/integration: depends on core logger factory, `local` driver, container log mode settings, go-units buffer parsing, and ring logger.

Risks: message ownership and double-free to the pool are the main concerns. Cache persistence can diverge from remote delivery if one write succeeds and the other fails. `ShouldUseCache` assumes prior validation for boolean parsing.

Test signals: `log_cache_test.go` validates log forwarding and cache behavior.
