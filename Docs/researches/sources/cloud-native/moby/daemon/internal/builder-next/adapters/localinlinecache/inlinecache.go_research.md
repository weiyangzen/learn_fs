<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go

Purpose: lets BuildKit import inline cache metadata from locally stored legacy images before falling back to registry cache import.

Important APIs and control flow: `ResolveCacheImporterFunc` wraps the registry importer and first calls `tryImportLocal` for `attrs["ref"]`. `tryImportLocal` resolves a local reference through the refstore and image store and returns raw image JSON. `localImporter.Resolve` parses inline cache into BuildKit cache manager storage. `importInlineCache` decodes image config, parses `moby.buildkit.cache.v0`, builds descriptors for each diff ID with created/description annotations from non-empty history entries, and calls `v1.ParseConfig`. `parseCreatedLayerInfo` aligns history metadata to non-empty rootfs layers.

State and persistence: reads local image/ref store data only. It constructs in-memory cache manager data for BuildKit; registry fallback may read remote state.

Dependencies and integration: integrates BuildKit remote cache APIs, registry cache importers, session manager, containerd content interfaces, and Moby image/ref stores.

Risks: `parseCreatedLayerInfo` assumes history non-empty entries align with rootfs diff IDs; malformed configs could produce length mismatches later in `importInlineCache`. The local descriptor provider cannot read layer blobs, so it is only suitable for metadata reconstruction.

Test signals: no direct tests here; inline-cache build tests should cover local-vs-registry import behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/adapters/localinlinecache/inlinecache.go -->
