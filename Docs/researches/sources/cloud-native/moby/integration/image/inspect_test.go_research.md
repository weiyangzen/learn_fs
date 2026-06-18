# sources/cloud-native/moby/integration/image/inspect_test.go

Purpose: integration tests for image inspect response shape, descriptor fields, repo digest uniqueness, missing blob resilience, and platform-specific inspect.

Important APIs and helpers: `TestImageInspectEmptyTagsAndDigests`, `TestImageInspectUniqueRepoDigests`, `TestImageInspectDescriptor`, `TestImageInspectWithoutSomeBlobs`, and `TestImageInspectWithPlatform`.

Control flow: dangling image inspect verifies `RepoTags` and `RepoDigests` are empty arrays in typed and raw JSON. Repo digest test tags busybox multiple times and ensures repo digests are not duplicated. Descriptor test checks descriptor presence only in snapshotter mode. The missing-blob regression is currently skipped. Platform inspect loads a synthetic multi-platform image with a legacy manifest and tests default, explicit native, explicit non-native, graphdriver error, and manifest inclusion behavior.

State and persistence: tests load special OCI images, create tags, and inspect daemon image metadata. Platform tests validate descriptor platform metadata and manifest list exposure in snapshotter mode.

Dependencies and integration: depends on specialimage builders, internal image load helper, raw response capture, image inspect options, snapshotter vs graphdriver behavior, and OCI platform structs.

Risks: some behavior is mode-specific and skipped or branched. The skipped missing-blob test documents a known desired regression test but currently provides no active signal.

Test signals: strong response compatibility signal for empty arrays vs nulls, descriptor fields, manifest inclusion, and platform-specific inspect semantics.
