# sources/cloud-native/containerd/core/images/archive/importer.go

Purpose: Docker and OCI image archive importer that ingests tar entries into a content store and returns an OCI index descriptor.

Important APIs/functions: `WithImportCompression`, `ImportIndex`, `onUntarJSON`, `onUntarBlob`, `resolveLayers`, `compressBlob`, `writeManifest`, and `detectLayerMediaType`.

Control flow and state: `ImportIndex` scans tar entries, tracks symlinks, ingests regular files as blobs, parses `oci-layout` and Docker `manifest.json`, then either returns the OCI `index.json` descriptor or constructs a new OCI index from Docker manifests. Docker import resolves configs/layers, optionally maps symlinked layers, normalizes repo tags into annotations, writes schema2 manifests and final index into the content store.

Dependencies and integration: tar/json, content store ingestion/reading/walking, archive compression, image platform/media helpers, labels, errdefs, platforms.

Risks: JSON parsing is capped at 20 MiB. All regular files outside recognized JSON are ingested as blobs, so malformed archive layouts can consume content store space before failing. `resolveLayers` reuses existing compressed blobs by `LabelUncompressed` and can compress uncompressed layers, making media type/digest changes. Windows platform OSVersion is filled from host defaults when missing.

Test signals: no direct tests in this subset. Important coverage includes OCI layout import, Docker v1.1/v1.2 import, symlink layers, compression option, missing files, empty layer media detection, and normalized annotations.
