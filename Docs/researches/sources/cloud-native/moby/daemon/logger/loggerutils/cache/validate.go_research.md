# sources/cloud-native/moby/daemon/logger/loggerutils/cache/validate.go

Purpose: validates and merges logging cache-related options.

Important APIs/types/functions: package `init`, `validateLogCacheOpts`, and `MergeDefaultLogConfig`.

Control flow/state/persistence: init adds all local-driver options under a `cache-` prefix plus `cache-disabled` to built-in log opts, then registers an external validator. `validateLogCacheOpts` only validates the `cache-disabled` boolean. `MergeDefaultLogConfig` copies cache-related defaults into destination config when not already set.

Dependencies/integration: uses `logger.RegisterExternalValidator` and common config maps.

Risks: cache opts are not real driver opts, so they must be recognized externally without exposing a fake driver.

Test signals: cache tests and option validation tests cover accepted and rejected keys.
