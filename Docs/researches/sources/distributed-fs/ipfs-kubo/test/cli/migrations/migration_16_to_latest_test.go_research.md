# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_16_to_latest_test.go

Purpose: reference migration suite for upgrading a real v16 repo fixture to latest, covering daemon `--migrate`, `repo migrate`, reverse migration, corrupted config handling, missing/default field behavior, temp-file cleanup, and backup files.

Important APIs/types/functions: `TestMigration16ToLatest`, `MigrationTestHelper` and assertion methods, `setupStaticV16Repo`, `cloneStaticRepoFixture`, `runDaemonMigrationWithMonitoring`, `runDaemonWithExpectedMigrations`, `runDaemonWithMultipleMigrationMonitoring`, `assertNoTempFiles`, `backupPath`, and cleanup/backup test helpers.

Control flow: each test clones `testdata/v16-repo`, runs daemon or repo migration, monitors stdout for migration messages and “Daemon is ready,” then shuts down. JSON helpers inspect nested config paths including map-key syntax. Failure tests corrupt config and verify atomic non-overwrite. Backup tests check `.bak` files and manual restore.

State and persistence: heavily mutates copied repo config/version files, creates backups, may create temp files, and starts daemons. Source fixture is copied, not modified.

Dependencies/integration: requires built `ipfs` in PATH, uses current `ipfs.RepoVersion`, harness node runner, JSON maps, exec pipes, and testify.

Risks: assumes latest includes 16-to-17 and 17-to-18 migrations; backup assertions mention v18 explicitly. Daemon output patterns are brittle. Test signals are version file, config JSON fields such as `AutoConf` and `auto`, output patterns, backup/temp file presence, and stderr emptiness.
