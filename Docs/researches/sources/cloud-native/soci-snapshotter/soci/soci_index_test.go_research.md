# sources/cloud-native/soci-snapshotter/soci/soci_index_test.go

Purpose: this file tests important SOCI index builder helper contracts without requiring a real containerd content store.

Important tests: `TestGetExistingZtocForLayer` verifies artifacts DB lookup respects original layer digest, span size, and force-recreate. `TestSkipBuildingZtoc` verifies min-layer-size behavior. `TestBuildSociIndexNotLayer` distinguishes non-layer media from supported layer media types. `TestBuildSociIndexWithLimits` checks layer size thresholds. `TestDisableXattrs` validates the xattr optimization rejects xattrs and opaque directory whiteouts. `TestNewIndex`, `TestDecodeIndex`, and `TestMarshalIndex` validate index construction and OCI-manifest serialization for v1/v2. Prefetch tests cover empty path behavior, storing artifacts, descriptor annotations, and span normalization.

Control flow and state: tests use `newFakeContentStore`, `NewOrasMemoryStore`, and temporary artifact DBs. They call some private builder helpers directly, giving targeted coverage of edge conditions.

Dependencies and integration points: tests depend on fake content-store implementations from `util_test.go`, ORAS memory store, OCI descriptors, zTOC metadata structs, and cmp diffing.

Risks and gaps: the tests do not exercise full `Build` over real tar/gzip layer content, concurrent layer builds, actual zTOC correctness, `writeSociIndex` GC label error aggregation, `GetImageManifestDescriptor`, or the prefetch path search against real zTOC file metadata. Some layer media tests only assert not `errNotLayerType`; they may still fail later for fake content/compression reasons. The prefetch layer builder test expects zero descriptors because no zTOCs/layers are supplied, so it does not validate path matching.

Test signal quality: broad helper coverage with low setup cost, but end-to-end build and concurrency behavior need integration or race tests.
