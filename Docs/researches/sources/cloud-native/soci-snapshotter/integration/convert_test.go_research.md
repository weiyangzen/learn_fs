# sources/cloud-native/soci-snapshotter/integration/convert_test.go

Purpose: validates online `soci convert` behavior for OCI image indexes/manifests, SOCI v2 artifact annotations, idempotency, platform matrices, pushability, and invalid converted images.

Important APIs and flow: `TestConvertWithForceRecreateZtocs` checks zTOC reuse versus `--force`. `validateConversion` asserts converted digests differ, separates image manifests from SOCI v2 descriptors, verifies SOCI index annotations point to image manifests, verifies platform and annotation consistency in both index and manifest, and checks containerd GC content labels for config/layers. `TestConvert` covers all-platform, single-platform, idempotent, single-manifest, and convert-in-place workflows across common images. `TestConvertAndPush` combines pull/convert/push platform options and validates expected "not found" failures. `TestInvalidConversion` deletes required manifest or SOCI index content before push and expects registry push failure.

State and persistence: mutates containerd image/content store, creates converted image references, deletes content for negative tests, and pushes to a local registry.

Dependencies and integration: uses `soci convert`, `nerdctl pull/push/login`, `ctr content`, OCI JSON decoding, platform helpers, registry helper shells, and SOCI annotation constants.

Risks and test signals: strong end-to-end signal for v2 conversion metadata and content-label retention. Tests are sensitive to image availability, platform naming, registry behavior, and containerd label output formatting.
