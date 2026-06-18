# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration.go

Purpose: implements repo config migration from version 16 to 17, introducing AutoConf and replacing old defaults with the `"auto"` placeholder.

Important APIs and control flow: exported `Migration` is a `common.BaseMigration`. `convert` decodes JSON, calls `enableAutoConf`, `migrateBootstrap`, `migrateDNSResolvers`, `migrateDelegatedRouters`, and `migrateDelegatedPublishers`, then writes JSON. Default bootstrap peers are removed and replaced with `"auto"` while custom peers are preserved. DNS resolver defaults are converted to `"auto"` and `"."` is ensured. Empty delegated routers/publishers become `"auto"`.

State and persistence: operates on config JSON and, through `BaseMigration`, leaves a backup and updates repo version.

Dependencies and integration: depends on Kubo config constants and migration common helpers. Registered as an embedded migration.

Risks and test signals: invalid or non-slice bootstrap data is replaced by `"auto"`, which repairs but can discard malformed custom data. Default matching is exact string matching. Tests cover end-to-end apply/revert and many bootstrap/DNS/routing/IPNS/autoconf cases.
