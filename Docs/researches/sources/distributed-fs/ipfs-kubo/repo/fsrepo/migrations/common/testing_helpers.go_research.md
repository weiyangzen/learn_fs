# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/testing_helpers.go

Purpose: centralizes test scaffolding for embedded config migrations.

Important APIs and control flow: `RunMigrationTest` marshals a config map, invokes a `BaseMigration.Convert`, decodes output, and checks `ConfigAssertion` entries. `AssertConfigField` handles nil-missing assertions, string slices, string maps, and scalar values. `GenerateTestConfig`, `CreateTestRepo`, `AssertMigrationSuccess`, `AssertMigrationReversible`, and `compareConfigs` cover end-to-end apply/revert flows.

State and persistence: creates temp repos with `version` and `config`, writes backup files for revert tests, then reads migrated/reverted JSON.

Dependencies and integration: used by migration-specific tests, especially 17-to-18.

Risks and test signals: helper expectations mirror JSON decoder types, for example numbers become `float64`. It only supports `BaseMigration` conversions for direct conversion tests and compares maps recursively for revert fidelity.
