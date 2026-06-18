# Research: sources/cloud-native/containerd/internal/cri/store/image/fake_image.go

This test helper constructs an image `Store` preloaded with synthetic image metadata. `NewFakeStore` creates a normal `Store` with nil containerd image getter and content provider, using the default platform matcher. For each supplied `Image`, it fills `refCache` for every reference and inserts the image into the internal store with `store.add`.

The helper returns an error if any image cannot be added, wrapping the failed image. It intentionally does not support `Update`, because the underlying containerd getter/provider are nil; tests use it for local resolve/get/list/update-cache behavior where image data is already known.

State is in-memory only: reference cache, digest set, image map, and pinned reference map are initialized exactly like the production store. Dependencies are the image store implementation and containerd platform default. Risks are test-only fidelity gaps around content reads, image usage calculation, platform-specific manifest selection, and containerd image labels. It is used by `image_test.go` to validate update and reference behavior without a live containerd content store.
