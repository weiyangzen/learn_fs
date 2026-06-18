# sources/cloud-native/moby/integration/container/list_test.go

Purpose: Container list API tests for ordering, annotations, since/before filters, image manifest platform metadata, and health summary versioning.

Important APIs and flow: `TestContainerList` removes existing containers, creates 64 containers, and expects descending creation order. `TestContainerList_Annotations` checks annotations are hidden in API v1.44 and present in v1.46. `TestContainerList_Filter` validates `since` and `before` filters around a middle container. `TestContainerList_ImageManifestPlatform` checks snapshotter-backed manifest platform fields. `pollForHealthStatusSummary` and `TestContainerList_HealthSummary` verify health appears only for API v1.52 and later.

State and dependencies: Creates many containers and one healthchecked container; uses request clients with pinned API versions. Snapshotter and Windows skips avoid unsupported metadata paths.

Risks and signals: It protects API ordering, filter semantics, versioned schema exposure, and list summary health fields. Failures directly affect CLI and API pagination/filter clients.
