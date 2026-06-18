# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/common/migration.go

Purpose: defines the embedded migration interface and shared options.

Important APIs and control flow: `Options` carries `Path` and `Verbose`. `Migration` requires `Versions`, `Apply`, `Revert`, and `Reversible`, giving the embedded runner a uniform way to execute or roll back migration steps.

State and persistence: no direct persistence; implementations use the options path to mutate repo files.

Dependencies and integration: implemented by `BaseMigration` and consumed by `embedded.go` registration and execution.

Risks and test signals: the interface assumes migrations can be expressed as apply/revert operations and relies on implementations to enforce version checks, locking, and backup behavior. Embedded migration tests assert registered migrations implement this contract.
