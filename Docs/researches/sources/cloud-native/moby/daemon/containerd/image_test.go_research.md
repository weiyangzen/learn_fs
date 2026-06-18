<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_test.go

Purpose: shared tests and helpers for image reference resolution and fake services used by containerd image-service tests.

Important APIs and flow: `TestLookup` populates a metadata-backed image store with tagged, tagged+digested, digest-only, ambiguous short-name, and mutation-prone images, then verifies `resolveAllReferences` behavior. It covers default latest normalization, all records by image ID, tag+digest specificity, missing refs, short ID lookup, a repository literally named `sha256`, and retry/failure behavior when image metadata mutates mid-lookup. Helpers create deterministic descriptors/digests, open a test metadata DB, and provide a minimal snapshotter service.

State and persistence: uses temporary bbolt metadata through containerd `metadata.DB`; `mutateOnGetImageStore` intentionally changes image records during `Get` to simulate races.

Dependencies and integration: depends on containerd namespaces/metadata/images, Moby image reference errors, Docker reference helpers, and `gotest.tools`.

Risks and gaps: the tested functions are in nearby image-resolution code not included in this work item, but many listed files depend on correct resolution. It does not cover tag creation/deletion or content state.

Test signals: strong signal for Docker-compatible reference resolution and race detection, especially avoiding confusion between short image IDs and repository names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_test.go -->
