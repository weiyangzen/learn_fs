# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/embedded.go

Purpose: registers and runs migrations embedded in the Kubo binary, currently 16-to-17 and 17-to-18.

Important APIs and control flow: `embeddedMigrations` is registered into `migrationsByName` as `fs-repo-<versions>`. `RunEmbeddedMigration` looks up a name, checks reversibility, builds options, and applies or reverts. `RunEmbeddedMigrations` validates the repo path, acquires `repo.lock` once, reads current version, enforces downgrade rules, finds step names with `findMigrations`, and runs available embedded steps in sequence.

State and persistence: locks the repo, reads/writes the repo version, and lets individual migrations atomically rewrite config and backups.

Dependencies and integration: used by `RunHybridMigrations` and by `fsrepo.Open` migration guidance. Depends on `go-fs-lock` and embedded migration packages.

Risks and test signals: if a version range includes both embedded and missing steps, the current logic runs embedded ones and only errors when zero embedded migrations exist; it does not require every step be embedded. Tests verify registration and missing migration error.
