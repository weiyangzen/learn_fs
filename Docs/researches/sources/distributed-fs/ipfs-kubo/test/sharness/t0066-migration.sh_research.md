## sources/distributed-fs/ipfs-kubo/test/sharness/t0066-migration.sh

Purpose: tests repo migration prompting, explicit migration flags, `ipfs repo migrate`, and failure behavior when migration is blocked by a repo lock.

Important APIs and helpers: defines `gen_mock_migrations` to synthesize `fs-repo-<n>-to-<n+1>` executables, `check_migration_output` to assert ordered migration messages, and uses `IPFS_REPO_VER`, `$IPFS_PATH/version`, `ipfs daemon --migrate=false/true`, `ipfs repo migrate`, and daemon launch/kill helpers.

Control flow and state: creates mock migration binaries on `PATH`, downgrades the repo version file, checks that `--migrate=false` fails with a requires-migration diagnostic, checks `--migrate=true` runs migrations and starts far enough to shut down, checks interactive daemon startup can auto-migrate, runs `ipfs repo migrate` directly, verifies no-op behavior when already current, then holds a daemon lock and confirms `repo migrate` fails with `repo.lock`.

Dependencies and integration points: covers fs-repo versioning, external migration binary discovery, daemon startup migration gating, direct migration command behavior, repo lock enforcement, and migration output compatibility including hybrid migration messages.

Risks and test signals: protects against accidental automatic upgrades when disabled, bad migration ordering, poor user diagnostics, and unsafe migration under lock. Signals are expected exit codes, version-file transitions, and exact migration or lock text.
