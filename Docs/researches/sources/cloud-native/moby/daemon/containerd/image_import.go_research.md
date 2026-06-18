<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import.go -->
# sources/cloud-native/moby/daemon/containerd/image_import.go

Purpose: implements `ImageService.ImportImage`, the containerd-backed equivalent of importing a tar layer into a Docker image. It turns one layer archive plus Dockerfile-style config changes into content blobs, an OCI image config, an OCI manifest, a containerd image record, and an unpacked snapshot.

Important APIs and flow: `ImportImage` creates a containerd lease, defaults the requested platform, applies `dockerfile.BuildFromConfig`, stores the layer with `saveArchive`, labels the compressed blob with `containerd.io/uncompressed`, writes config and manifest JSON via `storeJson`, creates or replaces the image tag (or a synthetic dangling name), and calls `unpackImage`. `saveArchive` accepts gzip/zstd as-is and recompresses uncompressed, xz, and bzip2 inputs to gzip. `writeCompressedBlob` and `compressAndWriteBlob` use pipes and digest tee readers to compute compressed and uncompressed digests while streaming. `detectCompression`, `fillUncompressedLabel`, and `writeBlobAndReturnDigest` are small support points.

State and persistence: persistent writes go to the containerd content store and image metadata store under a lease. The manifest records GC labels for config and layer content, and the compressed layer content info is updated with the uncompressed diff ID label. A successful unpack persists snapshotter state and logs an image import event.

Dependencies and integration: depends on containerd content/images, Moby dockerfile config mutation, Docker image spec conversion in `imagespec.go`, dangling image helpers, and the snapshotter unpack path. Errors are mapped through Moby `errdefs` so daemon APIs receive Docker-compatible classifications.

Risks: the concurrent pipe/digest paths must close readers/writers correctly or can deadlock on copy errors. Zstd and gzip are trusted as precompressed input, while xz/bzip2 are decompressed and recompressed, so digest and media type behavior differs by input. Import creates the image record before unpack failure is returned, leaving content/tag state after an unpack error. Empty archives intentionally become empty uncompressed streams, which is compatibility-sensitive.

Test signals: direct coverage is light; `image_import_test.go` validates config conversion used by import, while broader load/list/inspect tests exercise content/config interpretation after images are materialized.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import.go -->
