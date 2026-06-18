# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/migrations.go

Purpose: orchestrates repo migrations across legacy external migration binaries and modern embedded migrations.

Important APIs and control flow: `RunMigration` validates repo/version, finds step names, downloads missing binaries, then runs each with `-path` and optional `-revert`. `ReadMigrationConfig` reads only the config `Migration` section and fills defaults. `GetMigrationFetcher` turns download sources into HTTP fetchers or a `MultiFetcher`, rejecting legacy IPFS downloads. `findMigrations` computes ordered step names and looks for binaries in `PATH`. `RunHybridMigrations` chooses pure embedded, pure external, hybrid, or reverse hybrid paths around embedded min version 16.

State and persistence: reads repo version/config, downloads binaries to temp dirs, executes external processes that mutate repos, and calls embedded migrations that lock and rewrite config/version.

Dependencies and integration: used by repo open/migration commands; depends on config, fetchers, external executable lookup, and embedded runners.

Risks and test signals: external binaries execute with inherited stdio and trust boundary depends on fetched/verifiable artifacts. Hybrid path fallback can perform network downloads for old repos. Tests cover path finding, fetch, downgrade denial, migration config defaults/errors, and fetcher source parsing.
