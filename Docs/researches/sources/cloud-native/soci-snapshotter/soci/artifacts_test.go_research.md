# sources/cloud-native/soci-snapshotter/soci/artifacts_test.go

Purpose: this file tests the BoltDB artifact metadata helpers used by SOCI index and zTOC management.

Important APIs and helpers: `newTestableDb` creates a temporary bbolt DB with the `soci_artifacts` bucket and returns an `ArtifactsDb` wrapper. `resetArtifactDBInit` resets package-level `once` and `db` to make singleton initialization testable. Tests use realistic sha256 digest strings and `ArtifactEntry` structs.

Control flow: `TestGetIndexArtifactEntries` writes multiple index and layer entries and verifies filtering by `OriginalDigest` returns only index entries for the requested digest. `TestArtifactDbPath` checks default and custom root path behavior. `TestArtifactDB_DoesNotExist` forces singleton initialization failure and confirms `NewDB` reports unavailable DB. `TestArtifactEntry_ReadWrite_Using_ArtifactsDb` writes through the public API and reads back through `GetArtifactEntry`. `TestArtifactEntry_ReadWrite_AtomicDbOperations` exercises lower-level transaction helpers directly.

State and persistence behavior tested: tests create real temporary bbolt files, initialize the root bucket, and verify varint-encoded fields and string fields round-trip through bucket storage. They also demonstrate the global singleton must be reset to isolate tests.

Dependencies and integration points: tests use bbolt directly and validate helpers consumed by `soci_index.go` and `artifacts.go`.

Risks and gaps: no tests cover `SyncWithLocalStore`, `RemoveOldArtifacts`, `addNewArtifacts`, prefetch entries, `CreatedAt` binary encoding with non-zero times, image-digest reverse lookup, or removal by index digest. Ordering in `getIndexArtifactEntries` depends on Bolt bucket iteration order; current fixture order matches lexicographic digest order.

Test signal quality: good for core read/write and filtering helpers, limited for content-store synchronization and cleanup behavior.
