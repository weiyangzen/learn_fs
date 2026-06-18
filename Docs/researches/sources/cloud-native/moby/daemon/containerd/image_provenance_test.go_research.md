<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_provenance_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_provenance_test.go

Purpose: tests provenance and attestation behavior for image listing and `ImageAttestations`.

Important APIs and flow: helpers `provBlob`, `provJSON`, `buildFullIndex`, and `buildAttestationIndex` synthesize OCI indexes with platform image manifests and BuildKit-style attestation manifests. `TestAttestationDataFor` verifies list manifest summaries expose `AttestationData.For`. `TestImageAttestations` covers statement inclusion, default omission of statement body, order preservation, predicate type filtering, skipping layers without `in-toto.io/predicate-type`, missing statement blob errors, and nil output when no attestations exist.

State and persistence: writes synthetic blobs under temporary `blobs/sha256` directories and registers image records in the fake image service. Some scenarios intentionally omit layer blobs to validate lazy-vs-strict reads.

Dependencies and integration: depends on BuildKit attestation annotations, in-toto predicate annotations, containerd image descriptors, fake service/content store, `ImageAttestations`, and `Images` manifest summaries.

Risks and gaps: focused on synthesized minimal manifests, not registry-pulled referrer graphs. It does not test remote referrer fetching in `image_pull.go`; it validates local content interpretation after content exists.

Test signals: strong coverage for attestation classification and user-facing provenance output, especially the distinction between descriptor-only metadata and full statement body reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_provenance_test.go -->
