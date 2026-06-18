# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/migration/migration.go

Purpose: migrates deprecated `Provider` and `Reprovider` config sections into the unified `Provide` section for repo version 18.

Important APIs and control flow: exported `Migration` is a `common.BaseMigration`. `convert` decodes config, maps `Provider.Enabled` to `Provide.Enabled`, `Provider.WorkerCount` to `Provide.DHT.MaxWorkers`, `Reprovider.Strategy` to `Provide.Strategy` with `"flat"` converted to `"all"`, and `Reprovider.Interval` to `Provide.DHT.Interval`. It deletes old sections and logs guidance for non-default values and high worker counts.

State and persistence: modifies config JSON and updates version through `BaseMigration`.

Dependencies and integration: uses migration common helpers and is registered as an embedded migration.

Risks and test signals: logs include Unicode warning symbols in source output, which may be undesirable in strict ASCII terminals. Existing `Provide` content is overwritten if migrated fields exist. Non-string strategy becomes `"all"`. Tests cover missing/empty sections, preservation of unrelated sections, flat conversion, reversibility, and framework integration.
