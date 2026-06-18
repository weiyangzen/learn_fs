# Research: sources/cloud-native/containerd/internal/cri/store/image/image_test.go

This test file validates both the internal image store and the outer reference cache behavior. `TestInternalStore` adds several digest-named images, retrieves them by truncated full digest and truncated algorithm-less digest, verifies ambiguous prefixes fail, lists images, merges a new reference into an existing image, ignores duplicate references, deletes references one at a time, and removes the image when no references remain.

`TestInternalStorePinnedImage` verifies pin tracking is per reference while the image-level `Pinned` flag remains true if any reference is pinned. It covers adding pinned refs, pinning an existing unpinned ref, unpinning one ref while another remains pinned, unpinning the last ref, and deleting a pinned ref.

`TestImageStore` uses `NewFakeStore` and direct `update` calls to cover outer cache scenarios: disappearing nonexistent refs, adding a new ref to an existing image, adding a new image, moving an existing ref to a new image ID, and removing an existing ref. It also verifies `Resolve` for present refs and not-found for removed refs. Gaps include live containerd image/content access, platform manifest selection, size calculation, OCI config unmarshalling errors, and event-driven cache refresh.
