## sources/cloud-native/buildkit/snapshot/imagerefchecker/checker.go

Purpose: provides a cache external-reference checker that reports whether a sequence of layer digests is referenced by any image in a containerd image store.

Important APIs/types/functions: `Opt` carries image and content stores. `New` returns a factory for `cache.ExternalRefChecker`. `Checker.Exists(key, blobs)` initializes once, caches answers by caller key, and checks if `layerKey(blobs)` was registered. `init` lists images and dispatches handlers over their targets. `layersHandler` reads manifests/indexes and passes manifest layers to `registerLayers`.

Control flow: first `Exists` call loads all image layer stacks. Manifest descriptors register their layer digest sequence; index descriptors return child manifests for traversal; blob read errors are ignored for missing content paths.

State and persistence: in-memory `images` set and result cache. No writes.

Dependencies and integration points: integrates containerd `images.Dispatch`, content reads, OCI descriptors, and BuildKit cache external reference checks used to avoid garbage collecting image-backed snapshots.

Risks and test signals: `layerKey` concatenates digest strings without delimiters, which is probably safe with digest syntax but not formally length-delimited. `init` silently returns on list/dispatch errors, yielding false negatives. No direct tests in this subset.
