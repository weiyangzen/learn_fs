# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_concurrent_test.go

Purpose: verifies concurrent daemon migrations are prevented by repo locking.

Important APIs/functions: `TestConcurrentMigrations`, `testConcurrentDaemonMigrations`, and constant `daemonStartupWait`.

Control flow: the test clones a static v16 repo through shared migration helpers, starts the first `ipfs daemon --migrate` under a timeout context, waits two seconds for it to acquire the repo lock, then starts a second daemon migration against the same repo. The second command must fail and mention “lock.” Cleanup shuts down the first daemon and waits for process exit.

State and persistence: the first daemon may migrate and hold repo state/lock. The test asserts no `.tmp-*` migration files remain after the lock failure.

Dependencies/integration: depends on `setupStaticV16Repo`, `setupDaemonCmd`, and `assertNoTempFiles` from the migration helper suite, plus real OS file locking behavior.

Risks: fixed startup sleep can be too short or unnecessarily slow depending on machine load. If the first daemon exits before the second starts, the assertion loses meaning. Test signals are second command error, output containing “lock,” and no temp migration files.
