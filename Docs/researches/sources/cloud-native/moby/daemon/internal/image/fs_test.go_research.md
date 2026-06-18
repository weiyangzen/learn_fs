## sources/cloud-native/moby/daemon/internal/image/fs_test.go

Purpose: Tests filesystem-backed image store backend behavior.

Important tests: `TestFSGetInvalidData` corrupts content after `Set` and expects verification failure. `TestFSInvalidSet` creates a directory where a content file should be. `TestFSInvalidRoot` makes conflicting files at root/content/metadata paths. `TestFSMetadataGetSet` covers multiple IDs and keys plus missing content errors. `TestFSInvalidWalker` verifies invalid digest filenames are skipped. `TestFSGetSet` validates known and random sha256 digests. Additional tests cover unset keys, empty data rejection, delete behavior, full walk, and stopping on callback error.

Control flow and state: Tests use `t.TempDir`, direct filesystem mutation, and independent digest calculation for random content.

Dependencies and integration: Exercises `NewFSStoreBackend` and `StoreBackend` methods with `gotest.tools` assertions and OpenContainers digest.

Risks covered: Disk layout conflicts, atomic writes surfacing errors, corruption detection, metadata dependence on existing content, and walker resilience. It does not cover concurrent access or metadata key path traversal.

Persistence: Uses temporary on-disk roots and verifies durable file effects within the test process.
