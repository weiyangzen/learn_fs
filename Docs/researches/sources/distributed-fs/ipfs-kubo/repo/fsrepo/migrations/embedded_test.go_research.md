# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded_test.go

Purpose: smoke-tests embedded migration registration and error behavior.

Important APIs and control flow: `TestHasEmbeddedMigration` checks `fs-repo-16-to-17` exists and an unknown migration does not. `TestEmbeddedMigrations` verifies the embedded list is non-empty and every migration has a non-empty version string. `TestRunEmbeddedMigration` confirms a missing migration name returns an error.

State and persistence: does not create or mutate real repos; the missing-migration test passes `/tmp` but exits before path use.

Dependencies and integration: validates the map built by `embedded.go` and migration interface implementation.

Risks and test signals: coverage is shallow; it does not run successful embedded migrations, lock contention, downgrade paths, or incomplete-step ranges.
