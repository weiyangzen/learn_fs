# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEmptyDirectory.java

Purpose: Checks that S3A directory status reports definitive `Tristate.TRUE` or `Tristate.FALSE` as children are added or removed.

Important APIs/types/functions: `S3AFileStatus.isEmptyDirectory()`, `S3AFileSystem.innerGetFileStatus()`, `StatusProbeEnum.ALL`, `AuditSpan`, `mkdirs()`, `assertDeleted()`, and `ContractTestUtils.touch()`.

Control flow: one test creates a nested child under a parent, verifies parent is non-empty, deletes the child, and verifies empty. The other creates an empty directory, verifies empty, touches a file beneath it, and verifies non-empty.

State and persistence: remote S3 directory markers and child objects are created/deleted. `innerGetFileStatus(..., true, ALL)` requests definitive emptiness rather than unknown.

Dependencies and integration points: S3A status probing, directory marker handling, list-based emptiness checks, and audit-span wrapping.

Risks: directory marker retention policies and list consistency affect emptiness; using internal APIs means changes to probe semantics can break the test.

Test signals: catches stale or unknown empty-directory state after child creation/deletion.
