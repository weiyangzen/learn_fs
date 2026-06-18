<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_attestations.go -->
# sources/cloud-native/moby/daemon/images/image_attestations.go

Purpose: declares that image attestations are unsupported for the legacy image store.

Important APIs and control flow: `ImageAttestations` ignores its arguments and returns an `errdefs.NotImplemented` error explaining that the legacy image store does not support attestations.

State and persistence: no state is read or written.

Dependencies and integration: satisfies the daemon `ImageService` interface and lets API handlers return a typed not-implemented response when running without the containerd image store.

Risks: callers must not assume attestation support is universal across image-store backends. Feature detection should account for this backend-specific error.

Test signals: no direct tests in this subset; API behavior is expected to be checked in image-store mode integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_attestations.go -->
