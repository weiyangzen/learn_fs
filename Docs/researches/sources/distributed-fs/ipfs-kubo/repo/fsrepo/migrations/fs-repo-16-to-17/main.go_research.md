# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-16-to-17/main.go

Purpose: standalone command wrapper for the embedded 16-to-17 repo migration.

Important APIs and control flow: parses `-path`, `-verbose`, and `-revert`; requires `-path`; builds `common.Options`; calls `mg16.Migration.Apply` or `Revert`; prints errors to stderr and exits with status 1 on failure.

State and persistence: mutates the repo at `-path` through the migration implementation, including config backup, config rewrite, and version update.

Dependencies and integration: wraps `repo/fsrepo/migrations/fs-repo-16-to-17/migration` and common migration options. Intended for manual migration scenarios even though the migration is embedded in Kubo.

Risks and test signals: no direct test file for the CLI wrapper; migration behavior is tested in the migration package. The wrapper does not acquire a repo lock itself, so lock safety depends on the migration being run through embedded runner or external operator discipline.
