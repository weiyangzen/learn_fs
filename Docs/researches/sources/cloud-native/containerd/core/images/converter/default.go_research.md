# sources/cloud-native/containerd/core/images/converter/default.go

Purpose: default recursive image descriptor converter for layers, manifests, indexes, configs, Docker-to-OCI media types, GC labels, and diff ID rewrites.

Important APIs/types: `ConvertFunc`, `UpdateManifestFunc`, `DefaultIndexConvertFunc`, `ConvertHookFunc`, `ConvertHooks`, `IndexConvertFuncWithHook`, `defaultConverter`, `DualConfig`, `ReadJSON`, `WriteJSON`, `ConvertDockerMediaTypeToOCI`, and `ClearGCLabels`.

Control flow and state: `convert` dispatches by media type, runs optional post-convert hook, converts Docker media types to OCI or strips annotations from Docker descriptors. `convertManifest` reads manifest labels, converts layers concurrently, updates GC labels, records old->new diff IDs, converts config, writes a new manifest when modified, and calls update-manifest callback. `convertIndex` concurrently filters platforms and converts children while updating labels. `convertConfig` rewrites `rootfs.diff_ids` using `diffIDMap` and clears Docker legacy dummy image IDs. JSON writes create new content blobs with preserved labels.

Dependencies and integration: content store, images helpers, platforms, errgroup, log, go-digest, OCI specs.

Risks: layer conversion goroutines update a shared `diffIDMap`; locks protect the map, but config conversion relies on layer conversion finishing first. Platform filtering removes descriptors and GC labels. Annotation stripping for Docker media types can surprise hooks. `ReadJSON` returns the store's label map directly, so mutations affect the map object passed into writes.

Test signals: no direct tests in this subset. Important coverage includes concurrent layer conversion, GC label updates, diffID config rewrite, media type conversion, hook behavior, and platform filtering.
