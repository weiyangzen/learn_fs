## sources/cloud-native/moby/daemon/internal/image/tarexport/save.go

Purpose: Implements Docker image archive save/export, including Docker `manifest.json`, legacy `repositories`, and OCI layout/index/blob content.

Important APIs/types: `imageDescriptor` records refs, layer DiffIDs, image config, and retained top layer. `saveSession` tracks output dir, selected images, saved layer descriptors, and saved legacy configs. Key methods are `Save`, `parseNames`, `takeLayerReference`, `releaseLayerReferences`, `save`, `writeTar`, `saveImage`, `saveConfigAndLayer`, and `saveConfig`.

Control flow: `Save` resolves requested names/IDs into image descriptors and retains top layers, deferring release. `parseNames` handles digest references, canonical sha256-looking names, bare repository names with all tags, tagged refs, duplicate tags, and invalid refs. `takeLayerReference` loads image config, checks host OS and optional platform, and retains the rootfs top layer. `save` creates a temp dir, loops images, calls `saveImage`, builds Docker manifest entries and OCI manifest/index descriptors, writes legacy repositories when tags exist, writes `manifest.json`, `oci-layout`, `index.json`, fixes timestamps, and tars the directory with `CopyCtx`. `saveImage` walks RootFS layers, creates legacy V1 IDs/configs for compatibility, writes actual image config as an OCI blob, and records layer order. `saveConfigAndLayer` writes legacy config if needed, gets layer tar stream, tees through a digest calculator, writes the layer blob, records descriptor metadata, and warns if the layer DiffID does not match tar digest.

State and persistence: Temporary export tree is written to disk and streamed to caller. The function retains/releases layer references but does not mutate image store except for event logging. Cached `savedLayers` prevents duplicate layer writes.

Dependencies and integration: Integrates image store, layer store, refstore, OCI specs, Docker distribution descriptors, archive/compression, sequential file IO, tracing, events, and context-aware copy.

Risks: Empty image export is not implemented. Partial writes in temp dir are cleaned, but caller output stream may receive partial tar data on late errors. The untagged OCI index branch checks global manifest descriptor length, so multiple untagged images after tagged images need careful review. Descriptor reuse for foreign layers depends on layer implementing `distribution.Describable`.

Tests: No direct tests in this subset; lower-level layer/image tests cover some dependencies.
