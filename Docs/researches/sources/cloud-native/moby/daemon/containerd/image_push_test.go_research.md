<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_push_test.go

Purpose: validates platform and availability decision logic for push descriptor selection.

Important APIs and flow: `TestImagePushIndex` defines `pushTestCase` rows with index platforms, locally available platforms, optional requested platform, optional daemon platform override, and a checker. Each case creates a multi-platform image, deletes content for unavailable platforms with `deletePlatform`, then calls `getPushDescriptor`. Checkers assert whole-index selection, single-manifest selection, not-found, or conflict.

State and persistence: uses a temporary blob store and fake image service. `deletePlatform` walks matching platform manifests and deletes all present content descriptors to simulate a shallow/partial local index.

Dependencies and integration: uses `specialimage.MultiPlatform`, platform matchers, `walkImageManifests`, `ImageManifest.ImagePlatform`, `walkPresentChildren`, and containerd content deletion.

Risks and gaps: it tests selection only, not registry push, fake mountable blob behavior, progress, auth, distribution source labeling, or fallback aux output. Some comments identify open semantic questions around ARM fallback.

Test signals: strong regression coverage for host-preferred fallback and strict requested-platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_push_test.go -->
