# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/packer.go

Purpose: builds Nydus artifacts from a source directory and optionally pushes metadata/blob artifacts to a configured backend.

Important APIs/types/functions: `Opt`, `Builder`, `Packer`, `BlobManifest`, `PackRequest`, `PackResult`, `New`, `getBlobsFromBootstrap`, `getChunkDictBlobs`, `getNewBlobsHash`, `dumpBlobBackendConfig`, `tryCompactParent`, `Pack`, `ensureNydusImagePath`, and `initLogger`.

Control flow: `New` initializes logger, artifacts, binary path, builder, and optional pusher. `Pack` optionally compacts a parent bootstrap, reads parent/chunk-dict blobs, runs the builder with rootfs/bootstrap/blob/output paths, finds the first newly generated blob from `output.json`, renames it to digest form when needed, returns local paths or pushes via `Pusher`. Parent compaction dumps secret backend config temporarily and zeroes/removes it afterward.

State and persistence: output directory contains bootstrap, blob, output JSON, temporary backend config, and possible compacted bootstrap. Pusher writes remote backend artifacts.

Dependencies and integration points: nydus-image binary, build package, checker inspector, compactor, backend configs, local filesystem, and logrus.

Risks and test signals: `ensureNydusImagePath` only tries PATH fallback if a non-empty path was supplied. Blob detection chooses first blob not already known. Secret cleanup is best-effort. Push requires backend config.
