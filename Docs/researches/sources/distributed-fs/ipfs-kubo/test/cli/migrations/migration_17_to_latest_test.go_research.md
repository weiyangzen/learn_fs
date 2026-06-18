# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_17_to_latest_test.go

Purpose: focused 17-to-latest migration tests for consolidating legacy `Provider`/`Reprovider` config into the new `Provide` section.

Important APIs/functions: `TestMigration17ToLatest`, migration case functions, setup helpers `setupV17RepoWithProviderConfig`, `setupV17RepoWithFlatStrategy`, `setupV17RepoWithConfig`, empty/partial/invalid strategy setup helpers, `runDaemonMigrationFromV17`, and `MigrationTestHelper.RequireProviderMigration`.

Control flow: because no v17 fixture exists, setup clones v16, runs `repo migrate --to=17`, injects Provider/Reprovider JSON, then tests daemon `--migrate` or `repo migrate`. Assertions verify migrated fields (`Provide.Enabled`, `Provide.DHT.MaxWorkers`, `Provide.Strategy`, `Provide.DHT.Interval`), old-section removal, flat-to-all conversion, empty-section omission, partial migrations, and invalid strategy preservation followed by daemon startup failure.

State and persistence: mutates copied repo config/version and starts daemons for daemon migration cases. Invalid strategy test intentionally leaves invalid migrated config and runs daemon with timeout.

Dependencies/integration: depends on helper code from `migration_16_to_latest_test.go`, current `ipfs.RepoVersion`, JSON map edits, and Kubo provide-strategy validation.

Risks: cross-file helper dependency means this test file is not standalone. Numeric JSON values compare as `float64`. Output strings and invalid-strategy error text are implementation-coupled. Test signals are config fields, absent sections, migration output, version file, and daemon error text.
