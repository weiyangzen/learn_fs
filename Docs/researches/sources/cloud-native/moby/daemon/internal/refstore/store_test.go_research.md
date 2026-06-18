<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store_test.go -->
# sources/cloud-native/moby/daemon/internal/refstore/store_test.go

Purpose: verifies JSON reference store persistence, lookup, mutation, sorting, and error classification.

Important APIs and types: `TestLoad`, `TestSave`, `TestAddDeleteGet`, `TestInvalidTags`, shared `saveLoadTestCases`, and expected marshaled JSON.

Control flow: load test writes fixture JSON and verifies every reference resolves. Save test adds tags/digests and compares exact output JSON. Add/delete/get test exercises name-only tags, multiple refs per digest, duplicate adds, digest conflict behavior, force tag overwrite, reverse lookups, repository lookups, not-found paths, and deletion. Invalid-tag test rejects `sha256` repo ambiguity and adding digest refs as tags.

State and persistence: uses temporary JSON files and real `NewReferenceStore` persistence.

Dependencies and integration: uses distribution/reference, OCI digest, containerd errdefs, and gotest assertions.

Risks: exact JSON comparison depends on deterministic map marshaling for string keys. Tests do not cover corrupted JSON reload or concurrent access.

Test signals: strong coverage of core store contract and on-disk compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store_test.go -->
