# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/base.go

Purpose: provides the shared implementation for embedded config-only repo migrations.

Important APIs and control flow: `BaseMigration` stores from/to versions, description, and a `Convert` function. `Versions` formats `"from-to"`, `Reversible` returns true, `Apply` checks the current version, runs `WithBackup` on the repo config, writes the target version, and prints verbose progress. `Revert` checks the target version, restores the backup, and writes the original version.

State and persistence: reads and writes the repo `version` file, rewrites `config`, and leaves `config.<from>-to-<to>.bak` for rollback.

Dependencies and integration: used by embedded migrations 16-to-17 and 17-to-18 and by standalone migration command wrappers.

Risks and test signals: if version write fails after config rewrite, the repo can contain migrated config with old version and a backup; callers get an error but rollback is manual. Test helpers and migration-specific tests exercise apply/revert paths.
