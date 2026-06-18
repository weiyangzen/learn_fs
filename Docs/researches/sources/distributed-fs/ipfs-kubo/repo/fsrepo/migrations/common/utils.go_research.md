# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/utils.go

Purpose: provides version-file and JSON backup/rewrite helpers shared by embedded migrations.

Important APIs and control flow: `CheckVersion` reads and trims `version`, `WriteVersion` writes a version string, `Must` panics on supposedly unrecoverable transactional errors, `WithBackup` reads config into memory, atomically writes a backup, atomically rewrites config through a converter, and removes backup on conversion setup failure. `RevertBackup` renames backup over config. `ReadConfig` and `WriteConfig` decode and pretty-print JSON.

State and persistence: mutates repo `config`, backup config files, and `version`. Reads config fully before renaming to avoid Windows open-file rename issues.

Dependencies and integration: depends on the local `atomicfile` package and is called by `BaseMigration`.

Risks and test signals: `Must(out.Close())` can panic instead of returning an error if final rename fails. No fsync durability. Backup remains after successful migration for revert.
