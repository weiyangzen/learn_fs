## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/standalone.go

Purpose: OCI-layout load/save helpers for standalone conversion without containerd.

Important APIs/types/functions: `StandaloneImageInfo`, `LoadImage`, `SaveImageToTar`, `SaveImageToDir`, `resolveLayoutRoot`, and `blobPath`.

Control flow: load copies a directory or extracts a tar into a temp layout, reads `index.json`, resolves a root descriptor, and opens ORAS/local content stores. Save-to-tar exports a manifest through containerd archive. Save-to-dir copies layout and writes a clean `index.json` containing only the converted descriptor. Root resolution handles single manifests, nested indexes, and filtered platform lists with missing blobs.

State and persistence: reads/writes OCI layout directories, blobs, `index.json`, and tar output.

Dependencies and integration: containerd archive/content, ORAS OCI store, OCI specs, digest utilities.

Risks and test signals: `SaveImageToDir` removes output path before copying. `os.CopyFS` behavior depends on destination cleanliness. No direct tests here.
