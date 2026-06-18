# Research: sources/distributed-fs/ipfs-kubo/config/autoconf_client.go

Purpose: Creates and validates the singleton AutoConf client used by configuration expansion.

Important APIs/types/functions: Package globals `clientOnce`, `clientCache`, and `clientErr`; `GetAutoConfClient`, `newAutoConfClient`, `ValidateAutoConfWithRepo`, and `validateAutoConfDisabled`.

Control flow, state, and persistence: `GetAutoConfClient` uses `sync.Once`, so the first config passed determines the process-wide client. `newAutoConfClient` builds a Boxo autoconf client with cache dir `$IPFS_PATH/autoconf`, user agent, cache size, timeout, refresh interval, fallback config, and configured URL. Validation rejects default mainnet AutoConf URL when a private swarm key exists. If AutoConf is disabled, it logs all lingering `"auto"` placeholders and returns a hard error only when Bootstrap is exactly `["auto"]`.

Dependencies and integration points: Depends on Boxo autoconf, Kubo version/user-agent, config path resolution, logging, and startup validation that knows whether a swarm key exists.

Risks and test signals: The singleton can ignore later config changes in the same process, which matters for tests or multi-repo tooling. `validateAutoConfDisabled` only hard-fails one bootstrap-only case; other auto placeholders may be silently skipped at runtime after logging. Tests cover profile/default behavior but not singleton reset or private-network validation.
