# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/fs-repo-17-to-18/main.go

Purpose: standalone command wrapper for the 17-to-18 repo migration.

Important APIs and control flow: parses `-path`, `-verbose`, and `-revert`; errors when `-path` is missing; calls `mg17.Migration.Apply` or `Revert`; exits non-zero on failure.

State and persistence: delegates all persistent config/version mutation to the migration implementation.

Dependencies and integration: wraps `repo/fsrepo/migrations/fs-repo-17-to-18/migration` and common migration options for manual execution.

Risks and test signals: wrapper has no direct tests. As with the 16-to-17 wrapper, standalone execution does not itself lock the repo; the embedded runner handles locking when used in-process.
