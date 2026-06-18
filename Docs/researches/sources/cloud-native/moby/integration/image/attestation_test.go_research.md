# sources/cloud-native/moby/integration/image/attestation_test.go

Purpose: integration tests for `GET /images/{name}/attestations` against the containerd image store, plus helpers that build a synthetic OCI layout with in-toto attestation manifests.

Important APIs and helpers: `TestImageAttestations`, `statementLayer`, `buildAttestationImage`, `writeBlob`, `writeJSON`, and `mustMarshal`. The test uses `apiClient.ImageAttestations`, `ImageAttestationsWithStatement`, `ImageAttestationsWithPredicateTypes`, and `ImageAttestationsWithPlatform`.

Control flow: the test loads an OCI image containing a normal platform image manifest and an attestation manifest with SLSA provenance and SPDX SBOM statement layers. Subtests verify default omission of statement bodies, opt-in body return, predicate-type filtering, explicit platform matching, wrong-platform not found, multi-platform query rejection through raw HTTP, unknown-image not found, and empty filter semantics.

State and persistence: image content is written into a temporary OCI layout, loaded into the daemon's image store, and removed at cleanup. Attestation metadata is represented by OCI descriptors and Docker attestation annotations pointing at the image manifest digest.

Dependencies and integration: depends on containerd snapshotter image store, BuildKit attestation annotations, OCI image-spec types, distribution reference parsing, digest calculations, raw request helpers, and the Moby image API client.

Risks: skipped outside snapshotter mode. The handcrafted OCI layout must stay aligned with daemon attestation discovery rules. Raw HTTP query construction is sensitive to API version and error text.

Test signals: strong endpoint coverage for attestation listing, statement retrieval, filtering, platform validation, and error classification.
