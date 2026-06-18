<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go

Purpose: tests chunked cache construction, serialization, parsing, and TOC unmarshalling.

Important APIs/types/functions: fixture `jsonTOC`, `TestPrepareMetadata`, `TestPrepareMetadataFlat`, `bigDataToBuffer`, `findTag`, `TestWriteCache`, `TestReadCache`, `FuzzReadCache`, `TestUnmarshalToc`, and `TestMakeBinaryDigest`.

Control flow: tests parse fixture TOC, validate prepared entry counts and flattened path shape, write cache data into a buffer-backed fake store, find digest/hardlink/chunk tags and decode locations, read the binary cache back and deep-compare, fuzz the cache parser and lookup path, verify TOC rejects trailing extra JSON, and assert digest string-to-binary conversion.

State/persistence: buffer-backed fake big-data only; no real store writes.

Dependencies/integration: exercises `prepareCacheFile`, `writeCache`, `readCacheFileFromMemory`, `findBinaryTag`, `calculateHardLinkFingerprint`, `parseFileLocation`, `unmarshalToc`, and graphdriver output formats.

Risks/test signal: protects cache binary compatibility and malformed input resilience. Fuzzing is especially relevant because cache blobs can be loaded from persistent layer metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go -->
