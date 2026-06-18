<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go

Purpose: migrates build history blobs and leases from the main containerd namespace to the isolated history namespace used by Queue v2.

Important APIs and types: `Queue.migrateV2`, `blobRefs`, and `migrateBlobV2`.

Control flow: `migrateV2` scans Bolt records, lists old per-record lease resources, migrates content resources recursively, creates matching leases in the history namespace, attaches migrated resources, deletes old leases, and records version `2`. `blobRefs` reads content labels and optionally inspects OCI manifests to avoid treating skipped layers as references. `migrateBlobV2` copies content by digest to the history store with reconstructed GC labels and recursively migrates referenced blobs, tolerating missing source blobs by returning false.

State and persistence: mutates Bolt `_version`, old/new lease managers, and old/new content stores. Temporary migration leases guard content during copy.

Dependencies and integration: called from `NewQueue` when the stored version is absent or not greater than one.

Risks and test signals: migration deliberately allows missing blobs in some paths, which can later cause record deletion as orphaned. Recursive copy ignores errors for nested refs in one place. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/migrate.go -->
