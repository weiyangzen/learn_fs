# Research: sources/distributed-fs/ipfs-kubo/config/migration.go

Purpose: Retains deprecated configuration for legacy external repo migrations.

Important APIs/types/functions: `DefaultMigrationKeep`, `DefaultMigrationDownloadSources`, and `Migration` fields `DownloadSources` and `Keep`.

Control flow, state, and persistence: No functions. The comments state these settings apply only to repo versions below 16; modern repos use embedded migrations and ignore them.

Dependencies and integration points: Top-level `Config` includes `Migration`; migration code outside this subset reads it for old repositories.

Risks and test signals: Operators may assume these settings affect modern migrations when they do not. `migration_test.go` checks decoding preserves legacy config values.
