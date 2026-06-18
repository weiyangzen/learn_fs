<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go

Purpose: Linux helpers for reading, validating, and decoding estargz and zstd:chunked manifests and tar-split metadata.

Important APIs/types/functions: `maxTocSize`, `typesToTar`, `typeToTarType`, `readEstargzChunkedManifest`, `openTmpFile`, `openTmpFileNoTmpFile`, `readZstdChunkedManifest`, `ensureTOCMatchesTarSplit`, `tarSizeFromTarSplit`, `ensureTimePointersMatch`, `ensureFileMetadataAttributesMatch`, `validateBlob`, `decodeAndValidateBlob`, and `decodeAndValidateBlobToStream`.

Control flow: estargz reading fetches the footer, parses TOC offset, bounds TOC size, fetches/gunzips the embedded tar TOC, and verifies its digest. zstd:chunked reading parses annotations for manifest/tar-split offsets and lengths, bounds sizes, fetches chunks, validates compressed checksums, optionally zstd-decodes, unmarshals TOC, authenticates tar-split only when the TOC carries a digest, writes tar-split to an unlinked temp file, and validates TOC and tar-split metadata match exactly. Helpers compute tar size from tar-split segments/files and compare metadata excluding data-location fields.

State/persistence: creates unlinked temporary files for tar-split data with `O_TMPFILE` or create+unlink fallback. Reads seekable remote blob ranges and annotation metadata.

Dependencies/integration: integrates with chunked layer download/convert logic, `minimal.TOC`, `getBlobAt`, `ensureAllBlobsDone`, `pgzip`, `zstd`, `tar-split`, OCI digests, and fallback error types.

Risks: size caps and digest validation are critical DoS/integrity controls. Tar-split without authenticated digest must be ignored. Metadata comparison must stay in sync with `minimal.FileMetadata`. Temporary file fallback assumes unlink succeeds and `/proc/self/fd` semantics in tests.

Test signals: `compression_linux_test.go` covers tar-split size calculation and unlinked temp-file creation; broader zstdchunked tests outside this subset cover manifest generation/parsing and tar type mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go -->
