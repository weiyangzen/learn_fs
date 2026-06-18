# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/atomicfile/atomicfile_test.go

Purpose: verifies the atomic writer's file lifecycle and error handling.

Important APIs and control flow: tests cover `New`, `Close`, `Abort`, forced close/remove errors, `ReadFrom`, Unix permission preservation, repeated abort, and absence of `.tmp-*` files after repeated operations.

State and persistence: creates temp directories and real files, checking target content, target absence after abort, temp-file removal, and file modes. The tests intentionally close/remove files to trigger error paths.

Dependencies and integration: uses `os`, `filepath`, `runtime`, and `stretchr/testify`; validates behavior relied on by migration config backup and rollback.

Risks and test signals: strong coverage for expected temp-file hygiene, but no crash-simulation or fsync durability tests. Multiple aborts are allowed to error, so callers should not require idempotent nil results.
