# sources/cloud-native/soci-snapshotter/integration/create_test.go

Purpose: validates `soci create` index generation, input parameter validation shared with convert, sparse index behavior, content-store selection, prefetch artifacts, and garbage-collection labels.

Important APIs and flow: `TestCreateWithForceRecreateZtocs` checks existing zTOCs are skipped unless `--force` is used. `TestCreateConvertParameterValidation` verifies negative and overflowing min-layer/span-size arguments fail for both create and convert. `TestSociCreateEmptyIndex` expects no index when every layer is smaller than min layer size. `TestSociCreateSparseIndex` builds indexes at different min layer sizes and validates included layer sets against image manifest sizes. `TestSociCreate` covers images, platforms, and SOCI/containerd content stores. `TestSociCreateWithPrefetchArtifacts` creates prefetch artifacts for absolute/relative paths and verifies runtime loading. GC tests verify SOCI artifacts survive unrelated GC but are removed when their image GC label is gone.

State and persistence: writes zTOC/index blobs to selected content stores, creates registry artifacts, exercises containerd GC, and reads content-store blob files.

Dependencies and integration: uses SOCI CLI, containerd content store, local registry, OCI manifest decoding, snapshotter config generation, prefetch log monitoring, and helper validation of SOCI index structure.

Risks and test signals: strong coverage for index selection and artifact lifetime. Tests can be brittle around external image layer sizes, GC timing, and log messages used for prefetch confirmation.
