# sources/cloud-native/moby/integration/image/pull_test.go

Purpose: integration tests for image pull platform validation, digest/repository verification, nonexistent image errors, and preserving old images as dangling after pull.

Important APIs and helpers: `TestImagePullPlatformInvalid`, `createTestImage`, `TestImagePullStoredDigestForOtherRepo`, `TestImagePullNonExisting`, and `TestImagePullKeepOldAsDangling`.

Control flow: invalid platform pull expects invalid-argument. `createTestImage` writes a minimal Docker schema2 manifest, config, and layer into a content store. Digest/repo test pushes that image to a local registry, pulls it once to cache content, then tries pulling the same digest under a different repository and expects not found. Nonexistent test table-drives references with implicit library/latest variants and checks error text/classification. Dangling test tags busybox as alpine, removes busybox tag, pulls alpine, and verifies the previous ID is still inspectable.

State and persistence: uses daemon image cache/content store, local registry state, manifest cache, tag references, and dangling image records.

Dependencies and integration: depends on containerd content store/client, local registry test harness, platform validation, Docker Hub-like error messages, and daemon image pull implementation.

Risks: registry/network behavior can affect tests. Nonexistent pull tests rely on external registry response conventions. Digest/repo test is skipped for remote and Windows.

Test signals: verifies security-relevant remote digest validation, platform error classification, user-facing missing-image errors, and old-image retention on pull replacement.
