# sources/cloud-native/moby/integration/image/list_test.go

Purpose: integration tests for image list filtering, size calculations, and manifest metadata exposure.

Important APIs and helpers: `TestImagesFilterMultiReference`, `TestImagesFilterUntil`, `TestImagesFilterBeforeSince`, `TestAPIImagesFilters`, `TestAPIImagesListSizeShared`, and `TestAPIImagesListManifests`.

Control flow: filter tests create tags or committed images and verify reference glob/canonical filters, since/before/until behavior, and multi-reference output trimming. Size-shared test loads two images sharing a top layer and requests shared-size calculation. Manifest test loads a multi-platform image in a sub-daemon, creates a container for one platform, checks old API behavior, then requests manifests on API 1.47 and verifies kind, availability, platform coverage, and container association.

State and persistence: creates image tags, committed images with distinct timestamps, synthetic multi-layer/multi-platform images, and a container tied to one manifest. Filter tests depend on persisted image creation timestamps and references.

Dependencies and integration: depends on client filters, fake commits, specialimage loading, daemon harness, API version negotiation, OCI platforms, and image summary response shape.

Risks: timestamp precision is truncated to seconds in the API, so order-independent assertions are needed. Manifest tests require snapshotter mode and non-Windows sub-daemons.

Test signals: broad signal for image list filter correctness, shared-size computation by ChainID, and manifest-list API behavior.
