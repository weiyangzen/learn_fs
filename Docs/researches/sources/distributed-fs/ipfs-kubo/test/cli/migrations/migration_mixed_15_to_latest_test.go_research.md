# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_mixed_15_to_latest_test.go

Purpose: validates hybrid migration paths between old external migration binaries and newer embedded migrations: v15 to latest and latest back to v15.

Important APIs/functions: `TestMixedMigration15ToLatest`, `TestMixedMigrationLatestTo15Downgrade`, `setupStaticV15Repo`, `runDaemonWithLegacyMigrationMonitoring`, `runDaemonWithMigrationMonitoringCustomEnv`, `buildCustomPath`, `runMigrationWithCustomPath`, `createMockMigrationBinary`, `expectedMigrationSteps`, `verifyMigrationSteps`, `getNestedValue`, and `testRepoReverseHybridMigrationLatestTo15`.

Control flow: tests clone a v15 fixture, compile mock `fs-repo-15-to-16` and reverse binaries into temp PATH directories, then run daemon or repo migration. Daemon monitoring watches hybrid strategy, external phase, embedded phase, and completion messages. Repo tests validate final version/config. Downgrade first migrates to latest, then runs `repo migrate --to=15 --allow-downgrade` using mock external binaries.

State and persistence: mutates copied config/version files, creates mock binaries, writes repo locks in mock migrations, starts/stops daemons, and validates config JSON before/after.

Dependencies/integration: uses `ipfs.RepoVersion`, harness BuildNode, exec, runtime OS extension handling, slices env mutation, and helper fixture cloning.

Risks: generated mock binaries require Go toolchain availability. Output pattern assertions are tightly coupled to migration logging. Test signals are version file, preserved `Identity.PeerID`, `Bootstrap`, `AutoConf` addition/removal, and expected migration step messages.
