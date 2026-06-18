# sources/cloud-native/soci-snapshotter/integration/index_test.go

Purpose: validates `soci index` CLI info/list/remove behavior and rebuild interactions, including shared-layer zTOC retention.

Important APIs and flow: helpers `prepareSociIndices`, `prepareCustomSociIndices`, and `getZtocDigestsForImage` build indexes for multiple images/platforms and parse zTOC listings. `TestSociIndexInfo` accepts index digests and rejects zTOC digests. `TestSociIndexList` checks full, quiet, ref-filtered, and platform-filtered listing output. `TestSociIndexRemove` verifies removal by digest, removal by ref, removal of orphaned zTOCs from the containerd content store while retaining shared zTOCs, removing all listed indexes, and invalid digest errors. `TestSociIndexRemoveAndRebuildWithSharedLayers` ensures removing one shared-layer image and rebuilding the DB does not lose the other image's zTOCs.

State and persistence: creates and removes SOCI index/zTOC content in local content stores, triggers containerd GC, and rebuilds the artifact database.

Dependencies and integration: uses SOCI CLI, containerd GC config, platform parsing, content-store type options, and shared test helpers for image/index validation.

Risks and test signals: high signal for CLI metadata consistency and reference counting. It relies on chosen images actually sharing layers for some tests and uses sleeps for GC/rebuild timing.
