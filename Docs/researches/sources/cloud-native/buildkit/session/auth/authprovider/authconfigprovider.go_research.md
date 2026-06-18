<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go

Purpose: adapts Docker CLI config files into an `AuthConfigProvider` with simple per-host caching.

Important APIs, types, and functions: `LoadAuthConfig(config)` returns `acp.load`. `authConfigProvider` holds the Docker config, cache map, and mutex. `load(ctx, host, scopes, cacheExpireCheck)` returns a cached auth config unless expired, maps Docker Hub registry host to Docker's config-file key, loads credentials, and stores a timestamped cache entry. `authConfigCacheEntry` stores creation time and auth pointer.

Control flow and state: mutable cache is protected by a mutex. `scopes` are accepted for provider interface compatibility but not used by this config-file implementation.

Dependencies and integration: uses Docker CLI `configfile.ConfigFile` and `types.AuthConfig`. Used by `NewDockerAuthProvider` in client sessions.

Risks and test signals: cache key is only host, so scope-specific providers would need a different implementation. Docker Hub key translation is critical. Existing test `TestFetchTokenCaching` covers cache reuse and expiration through token fetch behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfigprovider.go -->
