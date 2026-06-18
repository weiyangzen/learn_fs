<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/image.go -->
# sources/cloud-native/containerd/client/image.go

Purpose: high-level image object implementation with metadata access, rootfs/config resolution, size/usage calculation, unpacking, and platform-aware behavior.

Important APIs/types/functions: `Image` interface, usage options, `NewImage`, `NewImageWithPlatform`, concrete `image`, `RootFS`, `Size`, `Usage`, `Config`, `IsUnpacked`, `Spec`, `UnpackConfig`, unpack options, `Unpack`, `getManifest`, `getLayers`, `checkSnapshotterSupport`, `ContentStore`, and `Platform`.

Control flow: `RootFS` caches diff IDs under a mutex. `Usage` maps client options into usage package options. `Spec` reads and unmarshals image config JSON. `Unpack` leases content, applies unpack options, resolves manifest/layers, resolves snapshotter, optionally checks snapshotter platform support, applies each layer through rootfs/diff services, writes uncompressed digest labels for newly unpacked layers, then labels the config blob with a snapshot GC reference.

State/persistence: caches `diffIDs` in memory. Unpack creates snapshotter state, updates content labels for uncompressed digests and snapshot GC references, and uses leases for mutation lifetime.

Dependencies/integration: content, diff, images/usage, snapshots, keyed mutex type, labels, rootfs, errdefs, platforms, OCI descriptors/specs, digest/identity, semaphores.

Risks: `UnpackConfig` has duplication suppressor and limiter fields but this `Unpack` implementation does not use them directly, so callers expecting local throttling may need higher-level paths. `getLayers` fails if image layer count differs from diff IDs after filtering non-layer artifact descriptors. Platform support check only runs for OSFeatures or explicit option. Cached diffIDs may become stale if image metadata changes behind the object.

Test signals: RootFS caching, usage option mapping, config/spec errors, unpack layer application and label updates, mismatched layer/diffID errors, IsUnpacked not-found behavior, platform support checks, and lease cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/image.go -->
