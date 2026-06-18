# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/optimizer.go

Purpose: optimizes an existing Nydus image by creating and pushing a new prefetch blob, bootstrap layer, config, and manifest.

Important APIs/types/functions: `Opt`, `BuildInfo`, `File`, `hosts`, `remoter`, `makeDesc`, `packToTar`, `getOriginalBlobLayers`, `fetchBlobs`, `Optimize`, `pushBlob`, `pushNewBootstrap`, `pushConfig`, and `pushNewImage`.

Control flow: `Optimize` parses the source Nydus image for the host arch, prepares work dirs, optionally fetches localfs blobs, pulls and unpacks the source bootstrap, invokes `Build`, then pushes a new image. Push flow uploads the prefetch blob, packs optimized bootstrap plus prefetch file into a tar and gzip layer, computes compressed digest and uncompressed diffID, rewrites config RootFS diff IDs, then writes and pushes a manifest containing original Nydus blobs plus the new prefetch blob and bootstrap.

State and persistence: uses temporary build directories, blob directories, generated bootstrap/tar/tar.gz/output JSON files, and remote registry uploads. Source parser and remoter hold registry state.

Dependencies and integration points: provider remote, parser, converter provider for localfs blob preparation, nydus-image optimize, containerd local readers/content readers, OCI descriptors, gzip/tar, and committer ref validation.

Risks and test signals: annotation map from old bootstrap is reused and mutated, which can alias source manifest state. Missing bootstrap/prefetch files fail late. Push retry is inconsistent across blob/config/bootstrap/manifest.
