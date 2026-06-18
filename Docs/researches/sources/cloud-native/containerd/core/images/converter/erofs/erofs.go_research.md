# sources/cloud-native/containerd/core/images/converter/erofs/erofs.go

Purpose: EROFS layer conversion support for image converter pipelines, plus manifest platform update for EROFS images.

Important APIs/functions: convert options `WithCompressors`, `WithMkfsOptions`, `WithBlobCompression`; `LayerConvertFunc`; and `UpdateManifestPlatform`.

Control flow and state: `LayerConvertFunc` skips non-layers, existing EROFS media types, and non-distributable layers. It uncompresses compressed layers first, reads source labels, converts uncompressed tar content to a temporary EROFS file using `erofsutils.ConvertTarErofs`, writes the EROFS blob to content store, optionally zstd-compresses the EROFS blob while recording uncompressed digest label, commits with labels, and returns a descriptor with EROFS media type and new size/digest. `UpdateManifestPlatform` ensures manifest platform/config `os.features` includes `erofs`, writes a new config, updates manifest GC label, writes a new manifest, and sets descriptor platform.

Dependencies and integration: core content/images, converter helpers, uncompress converter, internal erofs utilities, compression, labels, errdefs, logging, platforms, UUID generation.

Risks: requires external/system EROFS conversion support through `erofsutils`; temp files must be cleaned. Blob compression option currently recognizes string `"zstd"` only. Labels are taken from original compressed desc info, then applied to converted content. Commit with already-exists is tolerated, but writer state and info lookup must still succeed.

Test signals: no direct tests in this subset. Integration should cover compressed/uncompressed input, zstd blob compression, mkfs option defaults, non-distributable skip, existing EROFS skip, temp cleanup, and platform/config feature update.
