# Research: sources/cloud-native/containerd/internal/cri/store/image/image.go

This file implements CRI's image metadata cache. `Image` records image config digest ID, references, chain ID, compressed size, OCI image spec, and pinned state. `Store` holds a reference-to-ID cache, a containerd image getter, content provider, platform matcher, and an internal digest-indexed store.

`Update` locks the outer store, reads the image from containerd unless not found, builds local metadata with `getImage`, and delegates to `update`. `getImage` computes rootfs diff IDs and chain ID, compressed usage, config descriptor digest, config blob, OCI image spec, and pinned label state. `update` handles disappeared refs, unchanged refs with pin state changes, moved refs, and new refs.

The internal `store` protects image map, digest set for truncated lookup, and `pinnedRefs`. `add` merges references and pin state, `isPinned`, `pin`, and `unpin` manage per-reference pinning, `get` supports truncated digest lookup including algorithm-less prefixes, and `delete` removes a reference or the entire image when unreferenced.

State is an in-memory cache derived from containerd image/content stores; no disk persistence here. Dependencies include containerd images/content/usage APIs, digestset, OCI specs, distribution reference sorting, platform matching, CRI pinned-image labels, and set utilities. Risks include cache coherence with containerd events, pin state per ref, ambiguous truncated IDs, platform-limited image metadata, and content read/JSON errors. Tests cover internal add/get/list/delete, reference merging, pinned refs, fake-store update cases, and resolve behavior.
