## sources/cloud-native/moby/daemon/internal/layer/migration_test.go

Purpose: Tests migration from existing graphdriver layers into the layer store.

Important helpers/tests: `tarFromFilesInGraph` creates graphdriver layers and reads their diffs. `TestLayerMigrationNoTarsplit` creates two graph layers, computes checksum/tar-split metadata for the first, registers it by graph ID, registers the same tar normally and asserts shared references, registers a child normally, computes and registers child by graph ID, asserts shared references, then releases both child references and checks metadata deletion only after the second release.

Control flow and state: Uses vfs graphdriver temp roots and a `.migration-tardata` file to simulate migration metadata generation.

Dependencies and integration: Exercises `ChecksumForGraphID`, `RegisterByGraphID`, regular `Register`, reference counting, and metadata deletion. Skips Windows due to graphdriver differences.

Risks covered: Migration/normal registration deduplication, tar-split metadata import, and release semantics. Gaps include corrupt migration tar data, parent missing errors, and cleanup on commit failure.

Persistence: Uses temporary graphdriver and layerdb data.
