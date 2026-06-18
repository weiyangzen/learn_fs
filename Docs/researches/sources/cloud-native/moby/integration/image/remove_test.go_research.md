# sources/cloud-native/moby/integration/image/remove_test.go

Purpose: integration tests for image removal semantics: orphaning parent images, digest removal, platform-specific removal, and conflict/not-found errors.

Important APIs and helpers: `TestRemoveImageOrphaning`, `TestRemoveByDigest`, `TestRemoveWithPlatform`, `checkPlatformDeleted`, and `TestAPIImagesDelete`.

Control flow: orphaning test commits two images under the same reference and removes the tag, expecting the first committed image to remain and the second to disappear. Digest test removes a tag by repo digest without deleting busybox. Platform test loads a multi-platform image, removes selected platform manifests with `ImageRemoveOptions.Platforms`, verifies deleted descriptors, then removes the rest. API delete test builds an image, tags it twice, expects conflict when deleting by ID without force, expects not-found for missing tag, and removes a single tag.

State and persistence: validates image reference graph mutation, manifest/index content deletion, platform descriptor retention, tag untagging, and conflict handling when multiple tags point to an image.

Dependencies and integration: depends on specialimage multi-platform builder, build helper/fakecontext, snapshotter mode for platform deletion and repo digest behavior, string ID truncation, and Moby image remove API.

Risks: platform deletion behavior is snapshotter-only and includes a TODO about reporting platform-specific manifests when deleting the rest. Graphdriver vs snapshotter differences require skips.

Test signals: protects removal correctness for references, digests, platforms, conflict errors, and orphaned image retention.
