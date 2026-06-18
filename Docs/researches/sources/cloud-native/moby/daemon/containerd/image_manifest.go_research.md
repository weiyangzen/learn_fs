<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_manifest.go -->
# sources/cloud-native/moby/daemon/containerd/image_manifest.go

Purpose: provides manifest-level helpers around containerd images so Docker can reason about one platform-specific manifest inside an index while preserving the original image/index metadata.

Important APIs and flow: `walkImageManifests` handles locally present manifests; `walkReachableImageManifests` walks known descriptors even when some child content is absent. `ImageManifest` embeds `containerd.Image`, stores `RealTarget`, and overrides `Metadata` to report the original target. `NewImageManifest` rejects non-manifest descriptors and wraps a single manifest with `platforms.All`. Methods classify attestations and pseudo images, cache/read manifest JSON, check content availability, infer platform from descriptor or config, read config subsets, calculate present content size, and calculate unpacked snapshot usage via diff-ID chain ID.

State and persistence: read-only except for cached manifest JSON in the `ImageManifest` instance. It reads content blobs and snapshot usage, and treats missing snapshot usage as zero for images not unpacked locally.

Dependencies and integration: central to list, inspect, push selection, snapshot creation, and attestation handling. It depends on BuildKit attestation annotations, containerd image child walking/checking, OCI identity chain IDs, and snapshot usage helpers.

Risks: `IsPseudoImage` intentionally treats unknown/unknown platform and attestation annotations as pseudo, but manifests with no layers are considered real enough for empty images. `walkReachableImageManifests` suppresses missing child errors to keep partial indexes usable. Snapshot usage depends on config rootfs diff IDs and the configured snapshotter only.

Test signals: indirectly exercised by list, inspect, push, load/save, and provenance tests; those cover partial content, pseudo/attestation classification, and platform selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_manifest.go -->
