<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go

Purpose: Linux chunked-layer lookaside cache for finding file payloads, hardlink-compatible files, and chunks in previously stored layers.

Important APIs/types/functions: constants `cacheKey`, `cacheVersion`, bloom settings; types `cacheFile`, `layer`, `layersCache`, `setBigData`; cache lifecycle `getLayersCache`, `load`, `release`; cache IO `loadLayerBigData`, `loadLayerCache`, `createCacheFileFromTOC`, `writeCache`, `readCacheFileFromMemory`; lookup helpers `makeBinaryDigest`, `calculateHardLinkFingerprint`, `generateFileLocation`, `parseFileLocation`, `appendTag`, `findBinaryTag`, `findDigestInternal`, `findFileInOtherLayers`, `findChunkInOtherLayers`, `unmarshalToc`.

Control flow: a process-global cache is ref-counted per `storage.Store`. Loading scans store layers, reuses existing loaded layers unless marked for mmap reload, attempts to mmap existing cache big-data, and creates missing writable caches from TOC big-data. `writeCache` parses TOC metadata, flattens if requested, emits tags for file digest, hardlink fingerprint, and chunk digest, stores variable location data and filenames, builds a bloom filter, writes a versioned binary blob through `SetLayerBigData`, and returns an in-memory `cacheFile`. Lookup converts digest strings to binary, bloom-filters by layer, binary-searches sorted tags, parses location/name, and returns target path plus offset.

State/persistence: persists binary cache blobs as layer big data under `chunked-manifest-cache`; may mmap those blobs and registers finalizers to `Munmap`. Uses mutexes/ref counts for process-local cache lifecycle.

Dependencies/integration: integrates with `containers/storage` layer store, graphdriver output formats, chunked minimal TOC metadata, `jsoniter`, OCI digests, mmap/madvise, and deduplication logic elsewhere in chunked package.

Risks: binary format parsing must be defensive against corrupt or malicious big data; max tag/bloom lengths reduce DoS risk. Global cache assumes one store identity. Finalizer-based mmap cleanup is best-effort, so explicit `release` matters. Hardlink fingerprint must include all metadata relevant to safe hardlink reuse. `unmarshalToc` rejects trailing non-whitespace to keep digests meaningful.

Test signals: `cache_linux_test.go` covers TOC parsing, flat/dir preparation, cache write/read round-trip, tag lookups for file/chunk/hardlink fingerprints, binary digest parsing, and fuzzes cache reading.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go -->
