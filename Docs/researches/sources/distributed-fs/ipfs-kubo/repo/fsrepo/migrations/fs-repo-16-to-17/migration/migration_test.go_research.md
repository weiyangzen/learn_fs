# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/migration/migration_test.go

Purpose: validates 16-to-17 config conversion and reversible migration behavior.

Important APIs and control flow: helpers run conversion on JSON, assert nested map/slice values, and build minimal configs. `TestMigration` creates a temp repo, writes version 16 and config, applies migration, checks version 17 and config changes, then reverts to version 16. Additional tests cover bootstrap processing, missing sections, preservation of custom DNS/bootstrap values, delegated router rewriting, delegated publisher defaults, and existing AutoConf preservation.

State and persistence: temp repo tests write real `config`, `version`, and backup files; conversion-only tests use buffers.

Dependencies and integration: exercises `common.BaseMigration`, config constants, and helpers from the migration package.

Risks and test signals: strong coverage for expected migration semantics. It does not cover corrupt JSON beyond conversion error path, backup write failure, or lock behavior.
