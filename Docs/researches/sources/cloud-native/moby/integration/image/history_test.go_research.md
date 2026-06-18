# sources/cloud-native/moby/integration/image/history_test.go

Purpose: integration tests for image history API, including BuildKit cross-platform image history.

Important APIs and helpers: `TestAPIImagesHistory`, `TestAPIImageHistoryCrossPlatform`, and `pullImageForPlatform`. They use internal build helpers, fake build contexts, `ImageBuild`, `ImageHistory`, `ImagePull`, and platform options.

Control flow: the basic test builds a small Dockerfile and asserts the built image ID appears in history. The cross-platform regression test selects a non-native architecture, pulls a base image for that platform, builds with BuildKit for that platform, extracts the image ID, then checks history by ID, by explicit platform, and by tag. It also asserts expected item count and non-negative layer sizes.

State and persistence: build outputs are persisted as images in the daemon store and removed during cleanup. Cross-platform state includes pulled platform-specific base image content and manifest metadata.

Dependencies and integration: depends on BuildKit builder, registry access for alpine, platform selection, fakecontext, image history API, and daemon architecture metadata.

Risks: cross-platform test is skipped on Windows but still depends on external pull availability and BuildKit behavior. The expected history length can change if builder output changes.

Test signals: protects `docker history`/image history for native and non-native platform images, especially avoiding missing snapshot errors.
