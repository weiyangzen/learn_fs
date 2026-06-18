# sources/cloud-native/nydus/smoke/tests/blobcache_test.go

Purpose: smoke tests for nydus-image blobcache generation and command-line validation around `--blob-cache-dir`.

Important APIs/types: `BlobCacheTestSuite`, `compareTwoFiles`, `prepareTestEnv`, `TestCommandFlags`, `TestGenerateBlobcache`, and top-level `TestBlobCache`.

Control flow: `prepareTestEnv` creates a lower layer, writes an OCI tar blob into the blob dir named by digest, creates a blobcache output dir, and sets bootstrap path. `TestCommandFlags` runs invalid `nydus-image create` combinations and asserts expected error text. `TestGenerateBlobcache` first creates RAFS metadata and runs nydusd to populate runtime cache, then runs builder with `--blob-cache-dir` and compares generated `.blob.data`/`.blob.meta` against runtime cache files by digest.

State and persistence: uses work dir, blob dir, bootstrap, runtime cache dir, generated blobcache dir, mount dir, and files named from the OCI blob digest. Runtime cache population occurs via reading mounted regular files.

Dependencies and integration: depends on smoke texture/tool helpers, nydus-image builder, nydusd FUSE mount, localfs backend, OpenContainers digest library, and containerd logging for cleanup errors.

Risks: invalid-flag assertions depend on exact CLI error text; FUSE/cache population requires root and correct mount; walking reads use relative paths after deriving mount-relative names, which can be sensitive to current working directory; output file names assume digest hex naming and `.blob.data`/`.blob.meta` suffixes.

Test signals: invalid flag combinations fail with expected messages; builder-generated blobcache data and metadata digests match the runtime cache populated by nydusd.
